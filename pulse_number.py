import pandas as pd

Env = "Env2"
Bat = "607"
no = "no1"
other = "_2"
# データを読み込み（エンコーディングは適宜変更してください）
file_path = rf'C:\Users\yota-\Desktop\Head_Pulse_yubi\xls\{Env}\{Env}_{Bat}_{no}{other}.csv'
data = pd.read_csv(file_path, encoding='shift_jis')

# 'peak_power' や 'peak_freq' に番号を振り直す
# 対象となる列名を取得し、新しい名前を付ける
time_columns = [col for col in data.columns if 'time' in col]
peak_power_columns = [col for col in data.columns if 'peak_power' in col]
peak_freq_columns = [col for col in data.columns if 'peak_freq' in col]


# 新しい列名を生成し、辞書形式でマッピング
new_column_names = {}
for i, col in enumerate(time_columns, start=1):  # 'Time.' についても1から連番を振る
    new_column_names[col] = f'time{i}'
for i, col in enumerate(peak_power_columns, start=1):
    new_column_names[col] = f'peak_power{i}'
for i, col in enumerate(peak_freq_columns, start=1):
    new_column_names[col] = f'peak_freq{i}'

# 列名を置き換え
data.rename(columns=new_column_names, inplace=True)

# 結果を表示
#print(new_column_names)

# 必要であれば保存
data.to_csv(rf'C:\Users\yota-\Desktop\Head_Pulse_yubi\xls\{Env}\{Env}_{Bat}_{no}{other}.csv', index=False, encoding='shift_jis')