
import pandas as pd

df = pd.read_csv("./teshima/path/flag/yubi_tim_raw.csv",header = None)
df_digits = df.iloc[:, 10:].round(3)

DF = pd.concat([df.iloc[:, :10], df_digits], axis=1)


DF.to_csv("./teshima/path/flag/yubi_tim_raw_.csv", header = None, index=None)

# df = pd.DataFrame([[555.1111111, 555.2222222, 100.530555, 50.99922, 0.333333],
#                    [555.1111111, 555.2222222, 100.530555, 50.99922, 0.333333]])
# df_digits = df.iloc[:, 2:].round(3)
# DF = pd.concat([df.iloc[:, :2], df_digits], axis=1)
# # DF.to_csv("temp.csv")
# print(DF)
