import datetime
import os
import pickle as pcl
from sklearn.metrics import r2_score
import numpy as np
import pandas
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

df_bos = pd.DataFrame(df.loc[np.isnan(df["gunes"])])
df_dolu = pd.DataFrame(df.loc[np.isnan(df["gunes"]) == False])

def mesafe(row, tablo, komsu_sayisi):
    k = tablo["istno"]
    m = ((tablo["coordx"] - row["coordx"].squeeze()) ** 2 + (tablo["coordy"] - row["coordy"].squeeze()) ** 2) ** 0.5
    km = pd.DataFrame({"k": k, "m": m}).sort_values(by="m")
    km = km.convert_dtypes()
    km = km.iloc[1:komsu_sayisi+1]
    km.reset_index(drop=True, inplace=True)
    return km.unstack().to_list()

komsular["km"] = komsular.apply(lambda x: mesafe(x, komsular, 10), axis=1)
komsular = pd.DataFrame(komsular)
# Bu komşuluk ilişkilerinin korelasyonununu bulalım. bu korelasyonu ek ağırlık olarak kullanacağız
komsu_sayisi = 10

corr = []
for satir, row in komsular.iterrows():
    sol_istno = row["istno"]
    print(sol_istno, "----------------------")
    r2_score_arr = []
    for i in range(komsu_sayisi):
        k_istno = row["km"][i]
        sol_gunes = df_dolu.loc[df_dolu["istno"] == sol_istno]
        sag_gunes = df_dolu.loc[df_dolu["istno"] == k_istno]
        birlesik_gunes = sol_gunes.merge(sag_gunes, on="date", how="inner")
        r2_score_arr.append(r2_score(birlesik_gunes["gunes_x"], birlesik_gunes["gunes_y"]))
     corr.append(r2_score_arr)
komsular["corr"] = corr






sol_istno = 17110
for i in range(komsu_sayisi):
    k_istno = komsular.head(1)["km"].squeeze()[9]
    print(k_istno)
