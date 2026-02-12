import numpy as np
import pandas as pd
import math
import os

def main():
    """
    データ処理のメイン関数
    """
    # ベースパス (このスクリプトがあるディレクトリ)
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        base_path = os.getcwd()

    # 各ディレクトリのパス
    rawdata_yubi_path = os.path.join(base_path, 'rawdata_yubi')
    timing_base_path = os.path.join(base_path, 'timing')

    if not os.path.exists(rawdata_yubi_path):
        print(f"エラー: rawdata_yubi ディレクトリが見つかりません。パス: {rawdata_yubi_path}")
        return

    # rawdata_yubiディレクトリを走査
    for env_dir in os.listdir(rawdata_yubi_path):
        env_path = os.path.join(rawdata_yubi_path, env_dir)
        if not os.path.isdir(env_path):
            continue

        # マイク位置情報の読み込み
        mic_pos_path = os.path.join(env_path, 'mic_position.csv')
        if not os.path.exists(mic_pos_path):
            print(f"警告: mic_position.csv が見つかりません。スキップ: {env_path}")
            continue
        mic_df = pd.read_csv(mic_pos_path)
        mic_positions_list = list(zip(mic_df["X"], mic_df["Y"], mic_df["Z"]))
        ref_mic_position = (mic_df["X"][24], mic_df["Y"][24], mic_df["Z"][24]) # 基準マイク(25番目)

        # BatA, BatB... ディレクトリを走査
        for bat_dir in os.listdir(env_path):
            bat_path = os.path.join(env_path, bat_dir)
            if not os.path.isdir(bat_path):
                continue
            
            # pathサブディレクトリ内のCSVファイルを処理
            path_dir = os.path.join(bat_path, "path")
            if not os.path.isdir(path_dir):
                continue
            
            # pathディレクトリ内のEnv〇_Bat〇_no〇_〇ディレクトリを走査
            for subdir in os.listdir(path_dir):
                subdir_path = os.path.join(path_dir, subdir)
                if not os.path.isdir(subdir_path):
                    continue
                
                # サブディレクトリ内のCSVファイルを処理
                for filename in os.listdir(subdir_path):
                    if not filename.endswith('.csv'):
                        continue

                    file_key = filename.replace('.csv', '')
                    # --- ファイル読み込み ---
                    # 1. パルスタイミング
                    # サブディレクトリ名からパルスタイミングファイル名を生成
                    pulse_timing_filename = f"{subdir}.csv"
                    pulse_timing_path = os.path.join(timing_base_path, env_dir, bat_dir, pulse_timing_filename)
                    if not os.path.exists(pulse_timing_path):
                        print(f"警告: パルスタイミングファイルが見つかりません。スキップ: {pulse_timing_path}")
                        continue
                    pulsetiming_df = pd.read_csv(pulse_timing_path)
                    if "Pulsetiming" not in pulsetiming_df.columns:
                        print(f"警告: 'Pulsetiming'列がありません。スキップ: {pulse_timing_path}")
                        continue
                    pulsetiming = pulsetiming_df["Pulsetiming"]

                    # 2. コウモリの位置座標
                    bat_df_path = os.path.join(subdir_path, filename)
                    bat_df = pd.read_csv(bat_df_path)
                    if "Time (Seconds)" not in bat_df.columns:
                        print(f"警告: 'Time (Seconds)'列がありません。スキップ: {bat_df_path}")
                        continue
                    
                    # --- データ前処理 ---
                    # pulsetimingを基準にbat_dfをマージする (how='left')
                    pulsetiming_df_to_merge = pd.DataFrame({"Time (Seconds)": pulsetiming})
                    bat_pulse = pd.merge(pulsetiming_df_to_merge, bat_df.drop_duplicates(subset=["Time (Seconds)"]), on="Time (Seconds)", how="left")

                    # マージできなかった行（位置情報がなかったパルス）をチェック
                    if bat_pulse['X1'].isnull().any():
                        missing_count = bat_pulse['X1'].isnull().sum()
                        #print(f"情報: {filename}で{len(pulsetiming)}パルス中{missing_count}個の位置データが見つかりませんでした。見つかったデータのみ処理を続行します。")
                        bat_pulse.dropna(inplace=True) # 位置データが見つからなかったパルスは除外

                    if bat_pulse.empty:
                        print(f"情報: {filename} で一致するパルスタイミングがありませんでした。")
                        continue

                    # --- 計算実行 ---
                    call_times = []
                    all_arrival_times = []
                    for i in range(len(bat_pulse)):
                        bat_pos = (bat_pulse["X1"].iloc[i], bat_pulse["Y1"].iloc[i], bat_pulse["Z1"].iloc[i])
                        mic_time = bat_pulse["Time (Seconds)"].iloc[i]
                        
                        call_time = calculate_bat_call_time(bat_pos, ref_mic_position, mic_time)
                        arrival_times = calculate_arrival_times(bat_pos, mic_positions_list, call_time)
                        
                        call_times.append(call_time)
                        all_arrival_times.append(arrival_times)

                    # --- 結果の保存 ---
                    output_dir = os.path.join(rawdata_yubi_path, env_dir, bat_dir, "pulse")
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"{file_key}.csv")
                    
                    result_df = create_result_dataframe(call_times, all_arrival_times, mic_df)
                    result_df.to_csv(output_path, index=False)
                    print(f"処理完了: {output_path}")

    print("\nすべてのファイルの処理が完了しました。")

def calculate_bat_call_time(bat_position, mic_position, mic_time, sound_speed=343):
    """コウモリの発声時刻を計算する"""
    distance = math.sqrt(
        (bat_position[0] - mic_position[0]) ** 2 +
        (bat_position[1] - mic_position[1]) ** 2 +
        (bat_position[2] - mic_position[2]) ** 2
    )
    travel_time = distance / sound_speed
    return mic_time - travel_time

def calculate_arrival_times(bat_position, mic_positions, call_time, sound_speed=343):
    """各マイクへの音の到達時刻を計算する"""
    arrival_times = []
    for mic_pos in mic_positions:
        distance = math.sqrt(
            (bat_position[0] - mic_pos[0]) ** 2 +
            (bat_position[1] - mic_pos[1]) ** 2 +
            (bat_position[2] - mic_pos[2]) ** 2
        )
        travel_time = distance / sound_speed
        arrival_times.append(call_time + travel_time)
    return arrival_times

def create_result_dataframe(call_times, all_arrival_times, mic_df):
    """計算結果をDataFrameにまとめる"""
    call_times_rounded = [round(ct, 2) for ct in call_times]
    
    # Call_Time列のみのDataFrameを作成
    result_df = pd.DataFrame({"Call_Time": call_times_rounded})
    
    return result_df

if __name__ == '__main__':
    main()