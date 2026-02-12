import math
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

# ベースパス
try:
    base_path = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_path = os.getcwd()

rawdata_yubi_path = os.path.join(base_path, 'rawdata_yubi')
head_angle_base = os.path.join(base_path, 'head_angle')
timing_base_path = os.path.join(base_path, 'timing')

# 角度計算関数
def calculate_angle(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    angle_rad = math.atan2(dy, dx)
    return math.degrees(angle_rad)

for env_dir in os.listdir(rawdata_yubi_path):
    env_path = os.path.join(rawdata_yubi_path, env_dir)
    if not os.path.isdir(env_path):
        continue
    for bat_dir in os.listdir(env_path):
        bat_path = os.path.join(env_path, bat_dir)
        if not os.path.isdir(bat_path):
            continue
        path_dir = os.path.join(bat_path, 'path')
        if not os.path.isdir(path_dir):
            continue
        # pathディレクトリ内のサブディレクトリを検索
        for subdir in os.listdir(path_dir):
            subdir_path = os.path.join(path_dir, subdir)
            if not os.path.isdir(subdir_path):
                continue
            for filename in os.listdir(subdir_path):
                if not filename.endswith('.csv'):
                    continue
                file_key = filename.replace('.csv', '')
                bat_df_path = os.path.join(subdir_path, filename)
                bat_df = pd.read_csv(bat_df_path)
                if not all(col in bat_df.columns for col in ['X1', 'Y1', 'Z1', 'X2', 'Y2', 'Z2', 'Time (Seconds)']):
                    print(f"スキップ: 必要な列がありません {bat_df_path}")
                    continue

                # XY方向の角度計算（X1,Z1からX2,Z2）
                bat_df['Pxy'] = bat_df.apply(
                    lambda row: calculate_angle(row['X1'], row['Z1'], row['X2'], row['Z2'])
                    if pd.notna(row['X2']) and pd.notna(row['Z2']) else np.nan,
                    axis=1
                )

                # XZ方向の角度計算（X1,Y1からX2,Y2）
                bat_df['Pxz'] = bat_df.apply(
                    lambda row: calculate_angle(row['X1'], row['Y1'], row['X2'], row['Y2'])
                    if pd.notna(row['X2']) and pd.notna(row['Y2']) else np.nan,
                    axis=1
                )

                # 出力ディレクトリ作成
                output_dir = os.path.join(rawdata_yubi_path, env_dir, bat_dir)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f'{file_key}.csv')
                bat_df.to_csv(output_path, index=False)
                print(f"全時系列データの頭部方向（Pxy, Pxz）を出力しました: {output_path}")