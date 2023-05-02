import datetime
import os
import pickle as pcl
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/" # Evde

file_df = open(os.path.join(datasetpath, "file_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file_df))
file_df.close()
file_ist = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
istdf = pd.DataFrame(pcl.load(file_ist))
file_ist.close()
del(file_df, file_ist)
print("Dosyalar başarıyla içeri aktarıldı.")

df.rename(columns={"Istasyon_No": "istno", "GUNESLENME_SURESI_saat": "gunes", "MAKSIMUM_SICAKLIK_°C":"maxsic", "MINIMUM_SICAKLIK_°C":"minsic", "ORTALAMA_NEM_%": "nem", "GUNLUK_ORTALAMA_HIZI_m_sn":"ruzgar"}, inplace=True)
df = df[["istno", "date", "gunes"]]

df_gunes_ordered = df.groupby(["istno"])["gunes"].count().sort_values(ascending=False)
df_gunes_chosen6000 = df_gunes_ordered.loc[df_gunes_ordered.values>6000]

df = df.loc[df["istno"].apply(lambda x: x in df_gunes_chosen6000.index)]
df.reset_index(inplace=True, drop=True)

df = pd.DataFrame(df)

komsular = istdf.loc[istdf["istno"].apply(lambda x: x in df_gunes_chosen6000.index)][["istno", "coordx", "coordy"]]
komsular.reset_index(inplace=True, drop=True)

boslar = pd.DataFrame(df.loc[np.isnan(df["gunes"])])
dolular = pd.DataFrame(df.loc[np.isnan(df["gunes"]) == False])

def mesafe(row, tablo, komsu_sayisi):
    k = tablo["istno"]
    m = ((tablo["coordx"] - row["coordx"].squeeze()) ** 2 + (tablo["coordy"] - row["coordy"].squeeze()) ** 2) ** 0.5
    km = pd.DataFrame({"k": k, "m": m}).sort_values(by="m")
    km = km.convert_dtypes()
    km = km.iloc[1:komsu_sayisi+1]
    km.reset_index(drop=True, inplace=True)
    return km.unstack().to_list()

komsular["km"] = komsular.apply(lambda x: mesafe(x, komsular, 10), axis=1)
komsular= pd.DataFrame(komsular)


# Doğruluk testi
komsular.set_index("istno", inplace=True)
komsular.drop(columns=["coordx", 'coordy'], inplace=True)

orj_komsu_sayisi = 10
komsu_sayisi = 5
power = 1
pay = 0
payda = 0
line = 0

def idw_yap(row):
    global line

    r_istno = row["istno"]
    r_date = row["date"]
    km = komsular.loc[komsular.index == r_istno, "km"].squeeze()

    print("lin----------------------------", line)
    line += 1

    pay = 0
    payda = 0
    for i in range(komsu_sayisi):
        k_istno = km[i]
        k_mes = km[i + orj_komsu_sayisi]
        if k_mes == 0:
            continue

        k_val = df.loc[(df["istno"] == k_istno) & (df["date"] == r_date)]["gunes"].squeeze()
        if type(k_val) != np.float_:
            continue
        if np.isnan(k_val):
            continue

        pay += k_val / (k_mes ** power)
        payda += 1 / (k_mes ** power)
    if payda == 0:
        return -1.0
    return pay / payda



# 3 komşu ile deneyip r2 scoruna bakalım
# power = 3 ile deneyip r2 scoruna bakalım
sample = dolular.sample(n=5000)
sample.reset_index(inplace=True, drop=True)

sample["tahminx"] = sample.apply(idw_yap, axis=1)

r2score = r2_score(sample["gunes"], sample["tahminx"])
# k=5 p=2       score = 0.716163
# k=10 p=2      score = 0.745457
# k=10 p=3      score = 0.728464
# k=10 p=1.5    score = 0.749967
# k=10 p=1      score = 0.750000
# k=8 p=1       score = 0.750048
# k=3 p=1       score = 0.622882
# k=5 p=1       score = 0.724000
# k=10 p=0.8    score = 0.748687












"""
def idw_yap(row):
    global line

    r_istno = row["istno"]
    r_date = row["date"]
    km = komsular.loc[komsular.index == r_istno, "km"].squeeze()

    print("lin----------------------------", line)
    line += 1

    pay = 0
    payda = 0
    for i in range(komsu_sayisi):
        k_istno = km[i]
        k_mes = km[i + komsu_sayisi]
        k_val = df.loc[(df["istno"] == k_istno) & (df["date"] == r_date)]["gunes"].squeeze()
        if type(k_val) != np.float_:
            continue
        pay += k_val / (k_mes ** power)
        payda += 1 / (k_mes ** power)
    return pay / payda
"""

