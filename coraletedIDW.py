import datetime
import os
import pickle as pcl
from sklearn.metrics import r2_score
import numpy as np
import pandas
import pandas as pd

#datasetpath = "C:/Users/ozitron/Desktop/kullanımda/" # Evde
datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/" # İşte

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
    return km.unstack()

kom_mes = komsular.apply(lambda x: mesafe(x, komsular, 10), axis=1)
kom_mes["istno"] = komsular["istno"]
kom_mes.set_index("istno", drop=True, inplace=True)
#kom_mes.iloc[0,1]
#kom_mes.loc[kom_mes.index == 17114, "k"][0].squeeze()

# Bu komşuluk ilişkilerinin korelasyonununu bulalım. bu korelasyonu ek ağırlık olarak kullanacağız
komsu_sayisi = 10

corr = []
for i,row in komsular.iterrows():
    sol_istno = row["istno"]
    sol_gunes = df_dolu.loc[df_dolu["istno"] == sol_istno]
    print(sol_istno, "----------------------")
    r2_score_arr = []
    for t in range(komsu_sayisi):
        k_istno = kom_mes.iloc[i,t]
        sag_gunes = df_dolu.loc[df_dolu["istno"] == k_istno]
        birlesik_gunes = sol_gunes.merge(sag_gunes, on="date", how="inner")
        r2_score_arr.append(r2_score(birlesik_gunes["gunes_x"].to_list(), birlesik_gunes["gunes_y"].to_list()))
     corr.append(r2_score_arr)
corr = pd.DataFrame(corr)
corr["istno"] = komsular["istno"]
corr.set_index("istno", inplace=True, drop=True)

# Korelasyonları -1 - 1 arasından 0-1 arasına getirelim
corr = (corr +1) / 2

del(birlesik_gunes, df_gunes_chosen6000, df_gunes_ordered, i, k_istno, r2_score_arr, row, sag_gunes, sol_gunes, sol_istno, t)
# ---------------------------
orj_komsu_sayisi = 10
power = 1
pay = 0
payda = 0

df_sample = df_dolu.sample(1000)
df_sample["tahmin"] = -1.0
line = 0
for r, row in df_sample.iterrows():
    print(line)
    line += 1

    row_istno = row["istno"]
    row_date = row["date"]
    pay = 0
    payda = 0
    meancr = corr.iloc[corr.index == row_istno].sum().mean()
    for i in range(komsu_sayisi):
        k_istno = kom_mes.loc[kom_mes.index == row_istno, "k"][i].squeeze()
        k_mes = kom_mes.loc[kom_mes.index == row_istno, "m"][i].squeeze()
        if k_mes == 0:
            continue
        k_val = df_dolu.loc[(df_dolu["istno"] == k_istno) & (df_dolu["date"] == row_date)]["gunes"]
        if k_val.empty:
            continue
        k_val = k_val.squeeze()
        ## Burada corr devreye giriyor.
        # cr = corr.iloc[corr.index == row_istno, i].squeeze()
        # k_val = (k_val * cr) / meancr
        ##
        pay += k_val / (k_mes ** power)
        payda += (1 / (k_mes ** power))
    if payda == 0:
        continue
    df_sample.loc[r, "tahmin"] = pay / payda

r2score = r2_score(df_sample["gunes"], df_sample["tahmin"])
print("r2score:", r2score)



### Yalnızca Corelasyon haritası
df_sample = df_dolu.sample(1000)
df_sample["tahmin"] = -1.0
df_sample.reset_index(drop=True, inplace=True)
line = 0
for r, row in df_sample.iterrows():
    line += 1
    row_istno = row["istno"]
    row_date = row["date"]
    k_val_total = 0
    meancr = corr.iloc[corr.index == row_istno].sum().mean()
    totalcr = 0
    dolu_hucre = 0
    for i in range(komsu_sayisi):
        k_istno = kom_mes.loc[kom_mes.index == row_istno, "k"][i].squeeze()
        k_val = df_dolu.loc[(df_dolu["istno"] == k_istno) & (df_dolu["date"] == row_date)]["gunes"]
        if k_val.empty:
            continue

        k_val = k_val.squeeze()
        dolu_hucre += 1
        ## Burada corr devreye giriyor.
        cr = corr.iloc[corr.index == row_istno, i].squeeze()
        k_val = (k_val * cr) ** 2
        k_val_total += k_val
        totalcr += cr
    df_sample.loc[r, "tahmin"] = (k_val_total / totalcr) * 0.5
    print("line:",line,"  dolu:", dolu_hucre)

r2score = r2_score(df_sample["gunes"], df_sample["tahmin"])
print("r2score:", r2score)






