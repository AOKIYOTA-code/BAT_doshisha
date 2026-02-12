import glob
import os
import numpy as np
import pandas as pd
import argparse

# from natsort import natsorted

from calculation_pd import (
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
        "Z1": target_data["Z1"],
        "X2": target_data["X2"],
        "Y2": target_data["Y2"],
        "Z2": target_data["Z2"],
        "Pxy": target_data["Pxy"],  # Pxy列を追加
        "Pxz": target_data["Pxz"],  # Pxz列を追加
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
    pulse_directions = target_data["Pxy"]
    pos_x, pos_z = rotation(indf["X1"], indf["Z1"], pulse_directions)
    # calc cross point
    print("calc cross points.........")
    cross_distance = calc_cross_points(target_data, pos_x, pos_z, env_name)

    return Vx, Vy, Vz, theta, alpha, cross_distance, target_data["dt"], target_data


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
                Vx, Vy, Vz, theta, alpha, cross_distance, dt, rawdata = calc_states(
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
                df["X1"] = rawdata["X1"][2:].tolist()
                df["Y1"] = rawdata["Y1"][2:].tolist()
                df["Z1"] = rawdata["Z1"][2:].tolist()
                df["X2"] = rawdata["X2"][2:].tolist()
                df["Y2"] = rawdata["Y2"][2:].tolist()
                df["Z2"] = rawdata["Z2"][2:].tolist()
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
                print('finish pulseflag,Env,bat...')
                cross_distance = np.array(cross_distance).T
                cross_distance = cross_distance.tolist()
                df["Pxy"] = rawdata["Pxy"][2:].tolist() # Time (Seconds)と同じ範囲でAngleを揃える
                df["Pxz"] = rawdata["Pxz"][2:].tolist() # Time (Seconds)と同じ範囲でAngleを揃える

                if all(pd.isna(val) for val in rawdata["Pxy"]): # Angle列が全てNaNか確認
                    for i in range(251):
                        df["distance obs {}".format(i + 1)] = [2] * len(df) # 全て2で埋める
                else:
                    new_columns = {}
                    for i in range(251):
                        distance_values = cross_distance[i][2:]
                        time_length = len(df["Time (Seconds)"])
                    
                        if len(distance_values) > time_length:
                            new_columns["distance obs {}".format(i + 1)] = distance_values[:time_length]
                        elif len(distance_values) < time_length:
                            padding = [2] * (time_length - len(distance_values))
                            new_columns["distance obs {}".format(i + 1)] = distance_values + padding
                        else:
                            new_columns["distance obs {}".format(i + 1)] = distance_values
                    
                    df = pd.concat([df, pd.DataFrame(new_columns)], axis=1)


                df = df.copy()
                df.to_csv("./calcdata_pd_yubi/{}/{}/path/{}.csv".format(env_name, bat_name, fname), index=None)
                print(f"finish {fname} ..........")
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
