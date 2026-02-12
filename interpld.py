import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# データの読み込み
path = r"C:\Users\yota-\Desktop\Head_Pulse_yubi"
Env = "Env2"
Bat = "607" 
no = "no1"
other = "_2"
data = pd.read_csv(path + rf"\mc_raw\{Env}\{Bat}_{no}{other}.csv")

# 時系列データ
time = data['Time (Seconds)']
x1 = data['X1']
y1 = data['Y1']
z1 = data['Z1']
x2 = data['X2']
y2 = data['Y2']
z2 = data['Z2']

# 元のデータのサンプリングレート
original_sampling_rate = 100  # Hz
original_time_step = 1 / original_sampling_rate

# 新しいサンプリングレート
new_sampling_rate = 1000  # Hz
new_time_step = 1 / new_sampling_rate

# 新しい時系列データ
new_time = np.arange(time.iloc[0], time.iloc[-1], new_time_step)
#new_time = np.linspace(time.iloc[0], time.iloc[-1], int((time.iloc[-1] - time.iloc[0]) * new_sampling_rate))
new_time = new_time[new_time <= time.iloc[-1]]
# 補間関数の作成
x1_interp = interp1d(time, x1, kind='linear')
y1_interp = interp1d(time, y1, kind='linear')
z1_interp = interp1d(time, z1, kind='linear')
x2_interp = interp1d(time, x2, kind='linear')
y2_interp = interp1d(time, y2, kind='linear')
z2_interp = interp1d(time, z2, kind='linear')

# 新しいサンプリングレートに基づいたデータの生成
new_x1 = x1_interp(new_time)
new_y1 = y1_interp(new_time)
new_z1 = z1_interp(new_time)
new_x2 = x2_interp(new_time)
new_y2 = y2_interp(new_time)
new_z2 = z2_interp(new_time)

# 補間されたデータをデータフレームに変換
interpolated_data = pd.DataFrame({
    'Time': new_time,
    'X1': new_x1,
    'Y1': new_y1,
    'Z1': new_z1,
    'X2': new_x2,
    'Y2': new_y2,
    'Z2': new_z2
})

# CSVファイルに出力
interpolated_data.to_csv(path + rf"\mc_interpld\{Env}\{Bat}_{no}{other}.csv", index=False)

# 結果をプロット
plt.figure(figsize=(12, 12))

plt.subplot(6, 1, 1)
plt.plot(time, x1, 'o', label='Original X1')
plt.plot(new_time, new_x1, '-', label='Interpolated X1')
plt.title('X1 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('X1')
plt.legend()

plt.subplot(6, 1, 2)
plt.plot(time, y1, 'o', label='Original Y1')
plt.plot(new_time, new_y1, '-', label='Interpolated Y1')
plt.title('Y1 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('Y1')
plt.legend()

plt.subplot(6, 1, 3)
plt.plot(time, z1, 'o', label='Original Z1')
plt.plot(new_time, new_z1, '-', label='Interpolated Z1')
plt.title('Z1 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('Z1')
plt.legend()

plt.subplot(6, 1, 4)
plt.plot(time, x2, 'o', label='Original X2')
plt.plot(new_time, new_x2, '-', label='Interpolated X2')
plt.title('X2 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('X2')
plt.legend()

plt.subplot(6, 1, 5)
plt.plot(time, y2, 'o', label='Original Y2')
plt.plot(new_time, new_y2, '-', label='Interpolated Y2')
plt.title('Y2 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('Y2')
plt.legend()

plt.subplot(6, 1, 6)
plt.plot(time, z2, 'o', label='Original Z2')
plt.plot(new_time, new_z2, '-', label='Interpolated Z2')
plt.title('Z2 Coordinate')
plt.xlabel('Time (s)')
plt.ylabel('Z2')
plt.legend()

plt.tight_layout()
plt.show()

