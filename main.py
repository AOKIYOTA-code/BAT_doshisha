import glob
import os
import numpy as np
import pandas as pd
import argparse


# from natsort import natsorted

from calculation import (
    vel,
    horizon_angle,
    vertical_angle,
    rotation,
    cross_point
)

#from cut_down import cut_for_episode, dwnsmp


def calc_cross_points(target_data, pos_x, pos_z, env_name):
    X = target_data["X1"][:-1]
    Y = target_data["Y1"][:-1]
    Z = target_data["Z1"][:-1]

    cross_list = cross_point(X, Z, pos_x, pos_z, env_name)

    return cross_list


def calc_rotation_point(target_data):
    X = target_data["X1"]
    Y = target_data["Y1"]
    Z = target_data["Z1"]

    rot_all_x, rot_all_z = rotation(X, Z)

    return rot_all_x, rot_all_z


def calc_angles(target_data):
    X = target_data["X1"]
    Y = target_data["Y1"]
    Z = target_data["Z1"]

    theta = horizon_angle(X, Z)
    alpha = vertical_angle(X, Y, Z)

    return theta, alpha


def calc_velocities(target_data):
    Vx = vel(target_data["X1"], target_data["dt"])
    Vy = vel(target_data["Y1"], target_data["dt"])
    Vz = vel(target_data["Z1"], target_data["dt"])

    return Vx, Vy, Vz


def read_data(target_data):
    Time = target_data["Time (Seconds)"]
    dt = Time[1] - Time[0]
    target_data = {
        "Time": target_data["Time (Seconds)"],
        "dt": dt,
        "X1": target_data["X1"],
        "Y1": target_data["Y1"],
        "Z1": target_data["Z1"]
    }

    return target_data


def calc_states(indf, env_name):
    # read data
    print("read data.................")
    target_data = read_data(indf)
    # calc velocity
    print("calc velocity.............")
    Vx, Vy, Vz = calc_velocities(target_data)
    # calc angle
    print("calc angle................")
    theta, alpha = calc_angles(target_data)
    # calc rotation point
    print("calc rotation point.......")
    pos_x, pos_z = calc_rotation_point(target_data)
    # calc cross point
    print("calc cross points.........")
    cross_distance = calc_cross_points(target_data, pos_x, pos_z, env_name)
    
    # 進行方向角度を度数法で計算（t+1の進行方向をtに出力）
    X = target_data["X1"]
    Z = target_data["Z1"]
    heading_angles = []
    
    # データが3点以上ある場合のみ計算
    if len(X) >= 3:
        for i in range(len(X)-2):
            # t+1の進行方向（t+1→t+2のベクトル）を計算
            heading_angle = np.degrees(np.arctan2(Z[i+2]-Z[i+1], X[i+2]-X[i+1]))
            heading_angles.append(heading_angle)
        # 最後から2番目の点は最後の点との差分で計算
        heading_angle = np.degrees(np.arctan2(Z[len(X)-1]-Z[len(X)-2], X[len(X)-1]-X[len(X)-2]))
        heading_angles.append(heading_angle)
        # 最後の点は前の点との差分で計算
        heading_angle = np.degrees(np.arctan2(Z[len(X)-1]-Z[len(X)-2], X[len(X)-1]-X[len(X)-2]))
        heading_angles.append(heading_angle)
    elif len(X) == 2:
        # データが2点の場合は両方とも同じ進行方向
        heading_angle = np.degrees(np.arctan2(Z[1]-Z[0], X[1]-X[0]))
        heading_angles = [heading_angle, heading_angle]
    else:
        # データが1点以下の場合は0を追加
        heading_angles = [0.0] * len(X)

    return Vx, Vy, Vz, theta, alpha, cross_distance, target_data["dt"], target_data, heading_angles


def calc_actions(indf):
    target_data = read_data(indf)
    actions = []
    for x, y, z in zip(
        target_data["X1"][1:], target_data["Y1"][1:], target_data["Z1"][1:]
    ):
        actions.append([x, y, z])
    return actions


def calc_rewards(indf):
    target_data = read_data(indf)
    rewards = [0]
    theta, _ = calc_angles(target_data)
    for i in range(len(theta) - 1):
        rewards.append(theta[i + 1] - theta[i])
    return rewards

def batname_list(target_data,length):
    bat_id=0
    ##yubi
    if target_data=="BatA":
        bat_id:int=100
    elif target_data=="BatB":
        bat_id:int=101
    elif target_data=="BatC":
        bat_id:int=102
    elif target_data=="BatD":
        bat_id:int=103
    elif target_data=="BatE":
        bat_id:int=104
    ##kiku
    #elif target_data=="BatA":
    #    bat_id:int=200
    #elif target_data=="BatB":
    #    bat_id:int=201
    #elif target_data=="BatC":
    #    bat_id:int=202
    #elif target_data=="BatD":
    #    bat_id:int=203
    #elif target_data=="BatE":
    #    bat_id:int=204
    #elif target_data=="kiku":
    #    bat_id:int=205


    batname=[bat_id for _ in range(length)]

    return batname

def Env(env_name,length):
    # if env_name=="Env3":
    #     env=4
    # elif env_name=="Env4":
    #     env=5
    # elif env_name=="Env5":
    #     env=6
    # elif env_name=="Env6":
    #     env=7
    # elif env_name=="Env7":
    #     env=3
    # else:
    env=env_name.split("v")[1]#Env1のvで切って["En","1"]にする
    env_list=[env for _ in range(length)]

    return env_list



def preprocess_bat(input_data):
    states, actions, rewards, lengths, conditions, vel_abss = [], [], [], [], [], []
    yubi_ID = [100, 101, 102, 103, 104]
    #kiku_ID = [200, 201, 202, 203, 204]
    target_env_list = glob.glob(
        f"{input_data}/*"
    )  # target_data == "OneDrive - 同志社大学\源田会\data\藤井先生\ユビ\2023"　想定
    for idx, target_env in enumerate(target_env_list):
        print(f"target_env:{os.path.split(target_env)[-1]}")
        target_bat_list = glob.glob(f"{target_env}/*")
        env_name = os.path.split(target_env)[-1]
        # testのため一旦障害物なしで
        # env_name = "Test"
        for target_bat, target_bat_ID in zip(target_bat_list, yubi_ID):
            print(f"target_bat:{os.path.split(target_bat)[-1]}")
            target_data_list = glob.glob(f"{target_bat}/*.csv")
            bat_name = os.path.split(target_bat)[-1]
            for target_data in target_data_list:
                fname = os.path.split(target_data)[1].split(".csv")[0]
                indf = pd.read_csv(target_data)
                # import pdb; pdb.set_trace()
                Vx, Vy, Vz, theta, alpha, cross_distance, dt, rawdata, heading_angles = calc_states(
                    indf, env_name
                )
                states.append(cross_distance)
                action = calc_actions(indf)
                reward = calc_rewards(indf)
                length = len(reward)
                actions.append(action)
                rewards.append(reward)
                lengths.append(length)
                conditions.append(idx)
                vel_abss.append(
                    np.sqrt(np.array(Vx) ** 2 + np.array(Vy) ** 2 + np.array(Vz) ** 2)
                )
                print('finish calculation........')

                df = pd.DataFrame()
                df["Time (Seconds)"] = rawdata["Time"][2:].tolist()
                df["X"] = rawdata["X1"][2:].tolist()
                df["Y"] = rawdata["Y1"][2:].tolist()
                df["Z"] = rawdata["Z1"][2:].tolist()
                print('finish position...........')
                df["Vx"] = Vx[1:len(rawdata["Time"][2:]) + 1]
                df["Vy"] = Vy[1:len(rawdata["Time"][2:]) + 1]
                df["Vz"] = Vz[1:len(rawdata["Time"][2:]) + 1]
                print('finish velocity...........')
                df["theta"] = theta[:len(df.index)]
                df["alpha"] = alpha[:len(df.index)]
                #df["Env"] = [env_name.replace("Env", "") for i in range(len(df["X"]))]
                #df["Bat"] = [target_bat_ID for i in range(len(df["X"]))]
                print('finish angle..............')
                # import pdb; pdb.set_trace()
                length=len(rawdata["Time"][:-2])
                #df["pulse_flag"] = [1 for _ in range(length)]
                df["Env"] = Env(env_name,length)
                df["bat"] = batname_list(bat_name,length)
                # 進行方向角度を度数法で追加
                df["heading_angle"] = heading_angles[:len(df.index)]
                print('finish pulseflag,Env,bat...')
                # bat列の直後にheading_angle列を移動
                cols = list(df.columns)
                if "bat" in cols and "heading_angle" in cols:
                    bat_idx = cols.index("bat")
                    heading_angle_col = df.pop("heading_angle")
                    # bat列の直後にheading_angleを挿入（列数を超えないようにチェック）
                    insert_idx = min(bat_idx + 1, len(df.columns))
                    df.insert(insert_idx, "heading_angle", heading_angle_col)
                cross_distance = np.array(cross_distance).T
                cross_distance = cross_distance.tolist()
                for i in range(251):
                    df = df.iloc[:len(cross_distance[:][i][:-1])]
                    df["distance obs {}".format(i + 1)] = cross_distance[:][i][1:]
                df.to_csv("./calcdata_yubi/{}/{}/path/{}.csv".format(env_name, bat_name, fname), index=None)
                print(f"finish {fname} ..........")

    # states_arr = np.array(states)
    # import matplotlib.pyplot as plt
    # plt.plot(states_arr[0][0])
    # plt.savefig("tmp.png")
    # dt = 0.01
    # cut_samples_len = episode_sec // dt
    # states = cut_for_episode(states, cut_samples_len)
    # actions = cut_for_episode(actions, cut_samples_len)
    # rewards = cut_for_episode(rewards, cut_samples_len)
    # vel_abss = cut_for_episode(vel_abss, cut_samples_len)

    return states, actions, rewards, lengths, conditions, vel_abss


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path", type=str, default="../AniMARL_data/", help="data path"
    )
    args = parser.parse_args()
    input_data_path = args.data_path  # not fix yet, data is .csv.

    (
        states,
        actions,
        rewards,
        lengths,
        conditions,
        vel_abss,
    ) = preprocess_bat(input_data_path)

    # import pdb; pdb.set_trace()

    # df = pd.DataFrame()

    # for i in range(len(states)):
    #     df["distance obs {}".format(i + 1)] = states[i]

    # os.mkdir("./calc/")

    # df.to_csv("./calcdata/yubi/{}.csv".format(path))