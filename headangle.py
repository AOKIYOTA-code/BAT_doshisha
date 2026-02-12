import math
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


path = r"C:\Users\yota-\Desktop\Head_Pulse_kiku"
Env = "Env2"
Bat = "2871" 
no = "no1"
other = ""

bat_df = pd.read_csv(path + rf"\mc_interpld\{Env}\{Bat}_{no}{other}.csv")
bat_x = bat_df["X1"]
bat_y = bat_df["Y1"]
bat_z = bat_df["Z1"]

# パルスタイミングを読み込み
#timing_df = pd.read_csv(rf'C:\Users\yota-\Desktop\Head_Pulse\timing\ユビ\{Bat}_{no}_{other}_timing.csv')
timing_df = pd.read_csv(path + rf"\timing\{Env}\{Bat}_{no}{other}_timing.csv")
pulsetiming = timing_df["Call_Time"]

# パルスタイミングに該当するデータを抽出
bat_pulse = bat_df[bat_df['Time'].isin(pulsetiming)].reset_index(drop=True)

# 角度計算関数
def calculate_angle(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    angle_rad = math.atan2(dy, dx)  # ラジアンで角度計算
    return math.degrees(angle_rad)  # 度に変換

# パルス放射時の頭部方向角度を計算し、bat_pulse に追加
bat_pulse['Angle'] = bat_pulse.apply(lambda row: calculate_angle(row['X1'], row['Z1'], row['X2'], row['Z2']), axis=1)
# 出力ディレクトリの作成（存在しない場合）
output_dir = path + rf'\head_angle\{Env}'
os.makedirs(output_dir, exist_ok=True)


# DataFrame に結果を追加
#df_bat['Direction'] = directions
bat_df['Angle'] = bat_df.apply(lambda row: calculate_angle(row['X1'], row['Z1'], row['X2'], row['Z2']), axis=1)

# 結果の確認
print(bat_df[['Time', 'X1', 'Z1','Angle']])
# パルス放射時のデータのみ保存
pulse_output_path = path + rf'\head_angle\{Env}\{Bat}_{no}{other}.csv'
bat_pulse.to_csv(pulse_output_path, index=False)
print("パルス放射時のデータを出力しました:", pulse_output_path)

# プロット
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(bat_df['X1'], bat_df['Z1'], label="Trajectory", color="gray")

# 軌跡を描画（X1 vs Z1）
plt.plot(bat_df['X1'], bat_df['Z1'], color='gray', linestyle='-', linewidth=1, label='Trajectory')
# パルス放射点ごとの矢印描画
for i in range(len(bat_pulse)):
    x = bat_pulse.loc[i, 'X1']
    y = bat_pulse.loc[i, 'Z1']
    angle = bat_pulse.loc[i, 'Angle']

    length = 0.5  # 矢印の長さ
    dx = length * math.cos(math.radians(angle))
    dy = length * math.sin(math.radians(angle))

    arrow = FancyArrowPatch((x, y), (x + dx, y + dy),
                            arrowstyle='-|>',
                            mutation_scale=15,
                            color='blue')
    ax.add_patch(arrow)

# 軸範囲を指定（任意に調整）
ax.set_xlim(0, 4.5)
ax.set_ylim(0, 7.5)

ax.set_xlabel("X1")
ax.set_ylabel("Z1")
ax.set_title("Trajectory with Head Direction Arrows (every 100 rows)")
ax.grid(True)
plt.legend()
plt.tight_layout()
plt.show()