import datetime
import os
import pickle as pcl
import numpy as np
import pandas as pd
from eto import ETo

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file = open(os.path.join(datasetpath, "df_tamamlandi.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
file = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
ist_df = pd.DataFrame(pcl.load(file))
file.close()
del(file)

df["n_sun"] = df["n_sun_tahmin"]
df["T_max"] = df["T_max_tahmin"]
df["T_min"] = df["T_min_tahmin"]
df.drop(["n_sun_tahmin", "T_max_tahmin", "T_min_tahmin", "U_z_tahmin","RH_mean_tahmin"], axis=1, inplace=True)
ist_df.rename(columns={"coordx": "lat",
                       "coordy": "lon",
                       "height": "z_msl"
                       }, inplace=True)

ist17886 = df.loc[df["istno"] == 17886]
ist17886 = pd.DataFrame(ist17886)
ist17886.drop(columns=["istno"], inplace=True)
ist17886.set_index("date", inplace=True, drop=True)



row = ist_df.loc[ist_df["istno"] == 17886]


et1 = ETo()
z_msl = row.z_msl.squeeze()
lat = row.lat.squeeze()
lon = row.lon.squeeze()
# TZ_lon = 173
freq = 'D'

et1.param_est(ist17886, freq, z_msl, lat, lon)
mydataframe = et1.ts_param

eto1 = et1.eto_fao()

eto1.head()