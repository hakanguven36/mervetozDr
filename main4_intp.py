import datetime
import os
import pickle as pcl
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import scipy.interpolate as interpolate

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file = open(os.path.join(datasetpath, "df_tamamlandi.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
del(file)

# Rüzgar ve nem tahminlerini atalım.
df.drop(columns=["U_z_tahmin", "RH_mean_tahmin"], inplace=True)

df_ruzgar_dolu = df.loc[df["U_z"].isnull() == False]
df_ruzgar_dolu.reset_index(drop=True, inplace=True)

df_ruzgar_dolu = pd.DataFrame(df_ruzgar_dolu)

# Her istasyonun 10 diğer istasyon ile ilişkisinden bir çıkarıma gidelim.
istasyonlar = pd.DataFrame(df.groupby("istno").first().index)
for r, row in istasyonlar.iterrows():
    r_istno = row["istno"]
    ruzgar_array1 = pd.DataFrame(df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == r_istno, ["istno", "date", "U_z"]])
    score_biriktir = []
    for k, k_row in istasyonlar.iterrows():
        k_istno = row["istno"]
        ruzgar_array2 = pd.DataFrame(df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == k_istno, ["istno", "date", "U_z"]])
        birlesim = ruzgar_array1.merge(ruzgar_array2, on=["istno", "date"], how="inner")
        score = r2_score(ruzgar_array1, ruzgar_array2)
        score_biriktir.append(score)


