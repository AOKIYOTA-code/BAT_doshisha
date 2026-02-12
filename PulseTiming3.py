import numpy as np
import pandas as pd
import math
path = r"C:\Users\yota-\Desktop\Head_Pulse_yubi"
Env = "Env2"
Bat = "607" 
no = "no1"
other = "_2"

#基準のマイクのパルスタイミング
pulsetiming_df = pd.read_csv(path + rf"\timing\{Env}\{Bat}_{no}{other}.csv")
pulsetiming = pulsetiming_df["Pulsetiming"]
mic_pos = pd.read_csv(path +rf"\mc_raw\{Env}\mic_position.csv")
mic4_x = mic_pos["X"][24]
mic4_y = mic_pos["Y"][24]
mic4_z = mic_pos["Z"][24]

#マイク座標
mic_df = pd.read_csv(path +rf"\mc_raw\{Env}\mic_position.csv")
mic_x = mic_df["X"]
mic_y = mic_df["Y"]
mic_z = mic_df["Z"]

#コウモリの位置座標
bat_df = pd.read_csv(path +rf"\mc_interpld\{Env}\{Bat}_{no}{other}.csv")
bat_x = bat_df["X1"]
bat_y = bat_df["Y1"]
bat_z = bat_df["Z1"]
# `bat_df` の `Time (Seconds)` 列と `pulsetiming_times` が一致する行を抽出
#bat_pulse = pd.read_csv(r'C:\Users\yota-\Desktop\20240730\mc\batpulse_positions_4.csv')
bat_pulse = bat_df[bat_df['Time'].isin(pulsetiming)]
#print(bat_pulse)
bat_pulse_x = bat_pulse['X1']
bat_pulse_y = bat_pulse['Y1']
bat_pulse_z = bat_pulse['Z1']
# コウモリと基準マイクの距離を算出して実際にコウモリが鳴いた時間を出す
def calculate_bat_call_time(bat_position, mic_position, mic_time, sound_speed=343):
    bat_pulse_x, bat_pulse_y, bat_pulse_z = bat_position
    mic4_x, mic4_y, mic4_z = mic_position
    # Calculate the distance between the bat and the microphone
    distance = math.sqrt(
        (bat_pulse_x - mic4_x) ** 2 +
        (bat_pulse_y - mic4_y) ** 2 +
        (bat_pulse_z - mic4_z) ** 2
    )
    
    # Calculate the time it took for the sound to travel this distance
    travel_time = distance / sound_speed
    
    # Calculate the actual time the bat made the call
    call_time = mic_time - travel_time
    return call_time
call_times = []

# 各マイクへ音が到達する時間を計算
def calculate_arrival_times(bat_position, mic_positions, call_time, sound_speed=343):
    arrival_times = []
    
    for mic_position in mic_positions:
        mic_x, mic_y, mic_z = mic_position
        bat_pulse_x, bat_pulse_y, bat_pulse_z = bat_position
        # Calculate the distance between the bat and the microphone
        distance = math.sqrt(
            (bat_pulse_x - mic_x) ** 2 +
            (bat_pulse_y - mic_y) ** 2 +
            (bat_pulse_z - mic_z) ** 2
        )
        
        # Calculate the time it took for the sound to travel this distance
        travel_time = distance / sound_speed
        
        # Calculate the arrival time at this microphone
        arrival_time = call_time + travel_time
        
        arrival_times.append(arrival_time)
    #print(arrival_time)
    return arrival_times


for i in range(len(bat_pulse)):
    bat_position = ((bat_pulse["X1"].iloc[i], bat_pulse["Y1"].iloc[i], bat_pulse["Z1"].iloc[i]))
    mic_position = (mic_df["X"][24], mic_df["Y"][24], mic_df["Z"][24])
    mic_time = pulsetiming[i]
    
    call_time = calculate_bat_call_time(bat_position, mic_position, mic_time)
    call_times.append(call_time)
    #print(call_time)

all_arrival_times = []

for i, call_time in enumerate(call_times):
    bat_position = ((bat_pulse["X1"].iloc[i], bat_pulse["Y1"].iloc[i], bat_pulse["Z1"].iloc[i]))
    mic_positions = list(zip(mic_df["X"], mic_df["Y"], mic_df["Z"]))
    
    arrival_times = calculate_arrival_times(bat_position, mic_positions, call_time)
    all_arrival_times.append(arrival_times)

# 各到着時間を小数点以下3桁に丸める
call_times = [round(call_time, 3) for call_time in call_times]
all_arrival_times = [[round(arrival_time, 3) for arrival_time in arrival_times] for arrival_times in all_arrival_times]
# データフレームに変換
columns = ["Call_Time"] + [f"ch{i+1}" for i in range(len(mic_df))]
data = [ [call_times[i]] + all_arrival_times[i] for i in range(len(call_times)) ]
result_df = pd.DataFrame(data, columns=columns)

# CSVファイルに出力
result_df.to_csv(path + rf"\timing\{Env}\{Bat}_{no}{other}_timing.csv", index=False)