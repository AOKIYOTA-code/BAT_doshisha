import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = r"C:\Users\yota-\Desktop\Head_Pulse_yubi"
# Env = "Env1"
# Bat = "2899" 
# no = "no2"
# other = "_1"

Env = "Env3"
Bat = "607" 
no = "no1"
other = "_1_2"

# CSVファイルの読み込み
file_path = path + rf"\mc_interpld\{Env}\{Bat}_{no}{other}.csv" # CSVファイルのパスを指定
chain_position = pd.read_csv(path + rf"\mc_raw\{Env}\chain_position.csv",encoding='shift_jis')
#pulsetiming = pd.read_csv(rf'C:\Users\yota-\Desktop\Head_Pulse\timing\キク\{Bat}_{no}_{other}_timing.csv',encoding='shift_jis')
pulsetiming = pd.read_csv(path + rf"\timing\{Env}\{Bat}_{no}{other}_timing.csv")
data_subset = pd.read_csv(file_path)
start = 0
end = 14.45
# "Time" 列の値が 18 ~ 28 の間にある行を抽出
data_subset = data_subset[(data_subset['Time'] >= start) & (data_subset['Time'] <= end)]

# 抽出結果の確認
#print(data_subset)
# x座標とy座標の抽出
x = data_subset['X1']  # x座標の列名を指定
y = data_subset['Z1']  # y座標の列名を指定
time = data_subset['Time']

x_chain = chain_position['X']
y_chain = chain_position['Z']

# パルスタイミングデータの秒数をリストに変換
pulse_times = pulsetiming['Call_Time'].tolist()

# パルスタイミングに対応する飛行軌跡の位置を取得
pulse_positions = data_subset[data_subset['Time'].isin(pulse_times)]
#print(pulse_positions)
x_pulse = pulse_positions['X1']
y_pulse = pulse_positions['Z1']
#print(x_pulse)

# y座標を反転
#y = -y
#y_chain = -y_chain
#y_pulse = -y_pulse

# 角度データの読み込み
angle_path = pd.read_csv(path + rf"\head_angle\{Env}\{Bat}_{no}{other}.csv",encoding='shift_jis')
angle_path = angle_path[(angle_path['Time'] >= start) & (angle_path['Time'] <= end)]

head_time = angle_path[angle_path["Time"].isin(pulse_times)]
angles_head = head_time["頭部方向"]
angles_pulse = head_time["放射方向"]
#angles_direction = head_time["進行方向"]
#print(head_time)
# プロット
plt.figure(figsize=(4.5, 7.5))
plt.plot(x, y, marker='', linestyle='-', color='gray', markersize=5, zorder=1)
plt.scatter(x_chain, y_chain, marker='o', linestyle='', color='orange')
plt.scatter(x_pulse, y_pulse, marker='o', linestyle='', color='k', label='Pulse Timing', s=10, zorder=2)

# `Direction`に基づく矢印を追加
#for i, angle in enumerate(angles_direction):
    #radian = np.deg2rad(angle)
    #arrow_length = 0.3
    #dx = arrow_length * np.cos(radian)
    #dy = arrow_length * np.sin(radian)
    #plt.arrow(x_pulse.iloc[i], y_pulse.iloc[i], dx, dy, linestyle = "-", head_width=0.1, head_length=0.1, fc='g', ec='g', label='Direction' if i == 0 else "")
    #plt.arrow(x_pulse.iloc[i], y_pulse.iloc[i], dx, dy, color = 'k', linestyle = "-", label='Direction' if i == 0 else "")

# 各パルスタイミングで`Angle_Head`に基づく線分を追加
for i,angle in enumerate(angles_head):
    radian = np.deg2rad(angle)
    arrow_length = 0.5
    dx = arrow_length * np.cos(radian)
    dy = arrow_length * np.sin(radian)
    plt.plot([x_pulse.iloc[i], x_pulse.iloc[i] + dx], 
             [y_pulse.iloc[i], y_pulse.iloc[i] + dy], 
             color='r', alpha=0.8, label='Head Angle' if i == 0 else "")

# `Angle_Pulse`に基づく線分を追加
for i, angle in enumerate(angles_pulse):
    radian = np.deg2rad(angle)
    arrow_length = 0.5
    dx = arrow_length * np.cos(radian)
    dy = arrow_length * np.sin(radian)
    plt.plot([x_pulse.iloc[i], x_pulse.iloc[i] + dx], 
             [y_pulse.iloc[i], y_pulse.iloc[i] + dy], 
             color='b', alpha=0.8, label='Pulse Angle' if i == 0 else "")



plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.xlim([0, 4.5])
plt.ylim([0, 7.5])

plt.tick_params(direction='in')
plt.grid(False)
#plt.legend()
plt.show()
