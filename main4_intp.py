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

file = open(os.path.join(datasetpath, "file_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
del(file)

df.rename(columns={"Istasyon_No":               "istno",
                   "GUNESLENME_SURESI_saat":    "n_sun",
                   "MAKSIMUM_SICAKLIK_°C":      "T_max",
                   "MINIMUM_SICAKLIK_°C":       "T_min",
                   "ORTALAMA_NEM_%":            "RH_mean",
                   "GUNLUK_ORTALAMA_HIZI_m_sn": "U_z"
                   }, inplace=True)

# Rüzgar ve nem tahminlerini atalım.
df.drop(columns=["U_z_tahmin", "RH_mean_tahmin"], inplace=True)

df_ruzgar_dolu = df.loc[df["RH_mean"].isnull() == False]
df_ruzgar_dolu.reset_index(drop=True, inplace=True)

df_ruzgar_dolu = pd.DataFrame(df_ruzgar_dolu)

# Her istasyonun 10 diğer istasyon ile ilişkisinden bir çıkarıma gidelim.
istasyonlar = pd.DataFrame(df_ruzgar_dolu.groupby("istno").first().index)

corr = []
for i,row in istasyonlar.iterrows():
    sol_istno = row["istno"]
    sol_gunes = df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == sol_istno]
    r2_score_arr = []
    for t in range(len(istasyonlar.index)):
        k_istno = istasyonlar.loc[t,"istno"]
        sag_gunes = df_ruzgar_dolu.loc[df_ruzgar_dolu["istno"] == k_istno]
        birlesik_gunes = sol_gunes.merge(sag_gunes, on="date", how="inner")
        if len(birlesik_gunes.index) < 1000:
            continue
        r2 = r2_score(birlesik_gunes["RH_mean_x"].to_list(), birlesik_gunes["RH_mean_y"].to_list())
        if r2 < 0.7:
            continue
        r2_score_arr.append(r2)
    r2_score_arr.sort(reverse=True)
    corr.append(r2_score_arr)
    print(i)

corr = pd.DataFrame(corr)
corr["istno"] = istasyonlar["istno"]
corr.set_index("istno", inplace=True, drop=True)
corr = corr.iloc[:, 0:4]
corr = corr.loc[corr[3].isnull() == False]



corr.to_csv(os.path.join(datasetpath, "ruzgar istasyonlar arasi korelasyon.csv"), sep=";", decimal=".")
