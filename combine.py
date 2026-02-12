import pandas as pd
import glob
import os
from natsort import natsorted

data_list = []

path = './20251110/analyse2/'
files = natsorted(glob.glob(path + '/*.csv'))
for file in files:
    data_list.append(pd.read_csv(file))
    print(file)

df = pd.concat(data_list, axis=0)
df.to_csv(f'{path}/dataset_pd_yubi.csv', index=None)