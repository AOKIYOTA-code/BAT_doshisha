import pandas as pd
import glob, os

target_env_list = glob.glob("./calcdata_pd_yubi/*")
for idx, target_env in enumerate(target_env_list):
    # print(f"target_env:{os.path.split(target_env)[-1]}")
    target_bat_list = glob.glob(f"{target_env}/*")
    env_name = os.path.split(target_env)[-1]
    for target_bat in target_bat_list:
        # print(f"target_bat:{os.path.split(target_bat)[-1]}")
        target_data_list = glob.glob(f"{target_bat}/combine/*.csv")
        bat_name = os.path.split(target_bat)[-1]
        for target_data in target_data_list:
            fname = os.path.split(target_data)[1].split(".csv")[0]
            df = pd.read_csv(target_data)


            #2次元 
            #df.iloc[df["pulse"] == 0, 12:-1] = 2
            #3次元
            df.iloc[df["pulse"] == 0, 16:-1] = 2
            # df.mask(df.iloc[:, 11:-1] == 0, 2)

            # print(df.iloc[:, 6:])

            # flagフォルダーが存在しない場合は作成
            flag_dir = './calcdata_pd_yubi/{}/{}/flag/'.format(env_name, bat_name)
            os.makedirs(flag_dir, exist_ok=True)
            
            df.to_csv('./calcdata_pd_yubi/{}/{}/flag/{}.csv'.format(env_name, bat_name, fname), index=None)
            print("finish {}".format(fname))