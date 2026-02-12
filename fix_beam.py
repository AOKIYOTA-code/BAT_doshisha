import pandas as pd

tetr = "train"

path = r"./teshima/path/flag/yubi_tim_raw.csv"

indf = pd.read_csv(path, header = None)

#時間情報あり
indf.iloc[:, 10:29] = 2
indf.iloc[:, 242:] = 2

#進行方向
#indf.iloc[:, 9:28] = 2
#indf.iloc[:, 241:] = 2

#時間情報なし
#indf.iloc[:, 8:70] = 2
#indf.iloc[:, 196:] = 2


outdf = indf.to_csv(path, index=False, header = False)