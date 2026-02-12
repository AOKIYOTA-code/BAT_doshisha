import numpy as np
import pandas as pd
import math
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

path = r"C:\Users\yota-\Desktop\Head_Pulse_yubi"
Env = "Env3"
Bat = "658" 
no = "no1"
other = "_1_2"
# CSVファイルからマイクの位置座標を読み込む
mic_df = pd.read_csv(path + rf"\mc_raw\{Env}\mic_position.csv")
mic_positions = mic_df[['X', 'Y', 'Z']].values

bat_df = pd.read_csv(path + rf"\mc_interpld\{Env}\{Bat}_{no}{other}.csv")
bat_x = bat_df["X1"]
bat_y = bat_df["Y1"]
bat_z = bat_df["Z1"]

#基準のマイクのパルスタイミング
pulsetiming_df = pd.read_csv(path + rf"\timing\{Env}\{Bat}_{no}{other}.csv")
pulsetiming = pulsetiming_df["Pulsetiming"]
mic_pos = pd.read_csv(path + rf"\mc_raw\{Env}\mic_position.csv")
mic4_x = mic_pos["X"][24]
mic4_y = mic_pos["Y"][24]
mic4_z = mic_pos["Z"][24]

#マイク座標
mic_df = pd.read_csv(path + rf"\mc_raw\{Env}\mic_position.csv")
mic_x = mic_df["X"]
mic_y = mic_df["Y"]
mic_z = mic_df["Z"]


#スペクトル強度と周波数の結果
peakpower_df = pd.read_csv(path + rf"\xls\{Env}\{Env}_{Bat}_{no}{other}.csv", encoding='shift_jis')
# "peak_power" で始まるカラムだけを抽出
peak_power = peakpower_df.filter(like="peak_power")
peak_power = peak_power.apply(pd.to_numeric, errors='coerce')
# 結果を確認
#print(peak_power)

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
result_df.to_csv(path + r"\pulsetiming.csv", index=False)
print("output : pulsetiming.csv")

#################################################################################################

#Calltimeの位置座標
timing = result_df["Call_Time"]
pulse_path = bat_df[bat_df["Time"].isin(timing)]
bat_positions = pulse_path[['X1', 'Y1', 'Z1']].values
# 距離の計算前に mic_positions を NumPy 配列に変換
mic_positions = np.array(mic_positions)

# 各マイクまでの距離を計算する関数
def calculate_distances(mic_positions, bat_positions):
    distances = np.zeros((bat_positions.shape[0], mic_positions.shape[0]))
    for i, bat_pos in enumerate(bat_positions):
        for j, mic_pos in enumerate(mic_positions):
            distances[i, j] = np.linalg.norm(bat_pos - mic_pos)
    return distances

# 距離の計算
distances = calculate_distances(mic_positions, bat_positions)

# 結果をDataFrameに変換
distances_df = pd.DataFrame(distances, columns=[f'Mic_{i+1}' for i in range(mic_positions.shape[0])])

distances_df.to_csv(path + r"\distance.csv", index=False)
print(bat_df["Time"])
print("output : distance.csv")

##########################################################################################################

spr_loss = 20*np.log10(distances_df/0.1)    #拡散減衰
ato_atte = 2*(distances_df-0.1)     #吸収減衰
Loss_1 = spr_loss + ato_atte        #減衰
Loss = Loss_1.transpose()
#print(Loss)
# peaklevelとpeak周波数を入力
# 基準値を設定
reference_value = 9728.66642 # 使用している基準値
# dB値を計算して新しいデータフレームに追加
dB_columns = peak_power.apply(lambda col: 20 * np.log10(col / reference_value))
#print(Loss)

#print(dB_Loss)
# dB_columns と Loss が同じ形状であることを確認
# インデックス名と列名をリセット
# 列名を整数インデックスに変更
dB_columns_reset = dB_columns.copy()
dB_columns_reset.columns = range(dB_columns.shape[1])
Loss_reset = Loss.reset_index(drop=True)
#print(dB_columns_reset)
# 要素ごとの加算
combined = dB_columns_reset + Loss_reset
# 25行目を削除する (インデックスは0から始まるので、25行目はインデックス24)
combined = combined.drop(index=24)

# 結果を CSV に保存
combined.to_csv(path + rf"\dB_Loss\{Env}\{Bat}_{no}{other}_dB.csv", index=False)
print("output : dB_Loss.csv")

################################################################################################
# パルスタイミング
result_df = result_df.round(3)
timing = result_df["Call_Time"]
pulse_path = bat_df[bat_df["Time"].isin(timing)]

# batの座標
x1 = pulse_path["X1"].values
x2 = pulse_path["X2"].values
y1 = pulse_path["Z1"].values
y2 = pulse_path["Z2"].values

# 体軸を決定する関数 (ベクトル)
def calculate_body_vector(x1, y1, x2, y2):
    dx = x1 - x2  # 尾から頭へのx方向の変位
    dy = y1 - y2  # 尾から頭へのy方向の変位
    return np.array([dx, dy])

# 尾からマイクまでのベクトルを計算する関数
def calculate_mic_vector(tail_position, mic_position):
    mx = mic_position[0] - tail_position[0]  # 尾からマイクへのx方向の変位
    my = mic_position[2] - tail_position[1]  # 尾からマイクへのy方向の変位
    return np.array([mx, my])

# 2つのベクトル間の相対角度を計算する関数 (体軸を0°とする)
def calculate_relative_angle(body_vector, mic_vector):
    # 体軸ベクトルとマイクベクトルのなす角度を計算
    angle_rad = math.atan2(mic_vector[1], mic_vector[0]) - math.atan2(body_vector[1], body_vector[0])
    angle_deg = math.degrees(angle_rad)
    

    # 角度を -180° から 180° の範囲に調整
    if angle_deg > 180:
        angle_deg -= 360
    elif angle_deg < -180:
        angle_deg += 360

    return angle_deg

# 尾と頭のベクトルと、全てのマイクベクトルとの角度を計算する関数
def calculate_all_mic_angles(tail_position, head_position, mic_positions):
    # コウモリの尾から頭への体軸ベクトルを計算
    body_vector = calculate_body_vector(head_position[0], head_position[1], tail_position[0], tail_position[1])

    angles = []
    # 各マイクに対して角度を計算
    for mic_position in mic_positions[:24]:
        mic_vector = calculate_mic_vector(tail_position, mic_position)  # 尾からマイクへのベクトル
        angle = calculate_relative_angle(body_vector, mic_vector)  # 体軸との相対角度を計算
        angles.append(angle)

    return angles


# コウモリの座標 (ここでは各タイミングのX1, Z1が頭、X2, Z2が尾と仮定)
bat_head_position = (pulse_path["X1"].values, pulse_path["Z1"].values)
bat_tail_position = (pulse_path["X2"].values, pulse_path["Z2"].values)

# すべての時間ステップについて計算
all_angles = []
for i in range(len(pulse_path)):
    # それぞれの時間ステップでのコウモリの頭と尾の座標を取り出す
    bat_head_position_i = (pulse_path["X1"].iloc[i], pulse_path["Z1"].iloc[i])
    bat_tail_position_i = (pulse_path["X2"].iloc[i], pulse_path["Z2"].iloc[i])

    # 各マイクに対しての角度を計算
    angles = calculate_all_mic_angles(bat_tail_position_i, bat_head_position_i, mic_positions)
    all_angles.append(angles)

# 結果をデータフレームに変換して保存
angles_df = pd.DataFrame(all_angles, columns=[f'Mic_{i+1}' for i in range(24)])
angles_df = angles_df.T
angles_df.reset_index(drop=True, inplace=True)
angles_df.to_csv(path + rf"\mic_angle\{Env}\{Bat}_{no}{other}_angle.csv", index=False)
print("output: mic_angles.csv")
#print(angles_df)
#print(combined)
##################################################################################################
# モデル関数の定義
def gauss_func(x,a,mu,sigma):
    """ガウシアン（正規分布）"""
    return a*np.exp(-(x-mu)**2/(2*sigma**2))

# フィッティングを行うための関数
def fit(func, x, param_init):
    """
    func:データxに近似したい任意の関数
    x:データ
    param_init:パラメータの初期値
    popｔ:最適化されたパラメータ
    pocv:パラメータの共分散
    """
    X = x[0]
    Y = x[1]
    try:
        popt, pocv = curve_fit(func, X, Y, p0=param_init, maxfev=100000)
        perr = np.sqrt(np.diag(pocv))  # 対角成分が各パラメータの標準誤差に相当
        y = func(sample_x, *popt)  # X に最適化されたパラメータで関数を適用
        success = True
    except RuntimeError:
        print("Optimal parameters not found: Number of calls to function has reached maxfev.")
        popt, perr, y = None, None, None  # エラーが出た場合のデフォルト値
        y = func(sample_x, *param_init)  # 初期パラメータでのフィッティング値を計算

    return y, popt, perr

# パラメータの初期値の設定
param_init = [90, 0, 10]     # y軸の最大,平均,標準偏差
# グラフ描画用のサンプルデータ
sample_x = np.arange(-150, 150, 0.01)
# データフレームの列数に基づいて繰り返しフィッティングを行う
num_cols = angles_df.shape[1]  # 列数を取得
# サンプルデータの用意
# 1列目と2列目のデータに対してフィッティングを行い、結果を出力する
for col in range(num_cols):  
    # データの抽出
    angles_col = angles_df.iloc[:, col].values
    combined_col = combined.iloc[:, col].values

    # -100から100の範囲でデータをフィルタリング
    mask = (angles_col >= -80) & (angles_col <= 80)
    angles_col_filtered = angles_col[mask]
    combined_col_filtered = combined_col[mask]

    # 長さが一致するか確認
    if len(angles_col_filtered) != len(combined_col_filtered):
        print(f"Length mismatch for column {col}: angles_col ({len(angles_col_filtered)}) vs combined_col ({len(combined_col_filtered)})")
        continue

    # フィルタリング後のデータが少なすぎないか確認
    if len(angles_col_filtered) < 10:
        print(f"Not enough data points after filtering for column {col+1}")
        continue

    # パラメータの初期値をデータに基づいて設定
    param_init = [max(combined_col_filtered), np.mean(angles_col_filtered), np.std(angles_col_filtered)]

    data_gauss_func = np.array([
        angles_col_filtered,  # angles_dfのcol列目
        combined_col_filtered  # combinedのcol列目
    ])
    #print(combined_col_filtered)

    # フィッティングの実行
    result = fit(gauss_func, data_gauss_func, param_init)
    y_fit = result[0]  # フィッティングしたy値
    popt = result[1]  # 最適化されたパラメータ
    perr = result[2]  # パラメータの標準誤差
    X = data_gauss_func[0]
    Y = data_gauss_func[1]
    Y_fit = gauss_func(X,*result[1])
    # poptがNoneでないことを確認してからフィッティング結果を計算
    if popt is not None:
        R2 = 1 - (np.sum((Y - Y_fit) ** 2)/np.sum((Y - np.mean(Y)) ** 2))
        print(f"Column {col+1}: R² = {R2}, Parameters = {popt}, Errors = {perr}")
    else:
        print(f"Column {col+1}: Fitting failed, using initial parameters.")
    


    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    ax.scatter(data_gauss_func[0], data_gauss_func[1],label='Data')
    ax.plot(sample_x, result[0],label='Fit',color='red')
    ax.legend()
    plt.xlabel('angle')
    plt.ylabel('dB')
    plt.title('Gaussian Fit')

    # フィッティングパラメータと標準誤差の出力
    print("Fitted parameters:", result[1])
    print("Parameter standard errors:", result[2])
    print("R²:", R2)

    # ピークのX座標を出力
    peak_x = result[1][1]
    print("Peak X coordinate:", peak_x)
    print("Column:",[col+1])

    # ピークのY座標（dB値）を出力
    peak_y = result[1][0]
    print("Peak Y (dB value):", peak_y)

    # -6dB下の点の座標を計算
    if popt is not None:
        peak_dB = popt[0]  # 最大dB値
        target_dB = peak_dB - 6  # -6dB下の値
        
        # ガウス関数の逆関数を使用して座標を計算
        sigma = popt[2]
        mu = popt[1]
        x1 = mu + sigma * np.sqrt(-2 * np.log(target_dB / peak_dB))
        x2 = mu - sigma * np.sqrt(-2 * np.log(target_dB / peak_dB))
        
        print(f"-6dB points: x1 = {x1:.2f}, x2 = {x2:.2f}")
        
        # ピークからの距離を計算
        distance1 = abs(x1 - mu)
        distance2 = abs(x2 - mu)
        print(f"Distance from peak to -6dB points: {distance1:.2f}° and {distance2:.2f}°")
        print(f"Total beam width at -6dB: {distance1 + distance2:.2f}°")

    plt.show()
