import datetime
import os
import pickle as pcl
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import scipy.interpolate as interpolate

"""
Burada rüzgar değerlerinin yüksek korelasyon gösteren istasyonlar arasında linear interpolasyon ile tamamlanması hedeflenmişti.
Ancak son satırda oluşturulan korelasyon tablosu incelendiğinde istasyonlar arasında hiçbir ilişki olmadığı saptandı.
ETo kütüphanesinin linear interpolasyon kullanarak boş değerleri doldurması mümkün. 
O yüzden rüzgar için boş kısımlar boş bırakılacak.
"""

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

corr = []
for i,row in istasyonlar.iterrows():
    sol_istno = row["istno"]
    sol_gunes = df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == sol_istno]
    r2_score_arr = []
    for t in range(len(istasyonlar.index)):
        k_istno = istasyonlar.loc[t,"istno"]
        sag_gunes = df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == k_istno]
        birlesik_gunes = sol_gunes.merge(sag_gunes, on="date", how="inner")
        r2_score_arr.append(r2_score(birlesik_gunes["U_z_x"].to_list(), birlesik_gunes["U_z_y"].to_list()))
    r2_score_arr.sort(reverse=True)
    corr.append(r2_score_arr)
corr = pd.DataFrame(corr)
corr["istno"] = istasyonlar["istno"]
corr.set_index("istno", inplace=True, drop=True)

corr.to_csv(os.path.join(datasetpath, "ruzgar istasyonlar arasi korelasyon.csv"), sep=";", decimal=".")
