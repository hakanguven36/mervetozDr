# BÖLÜM-2 Boşluk Doldurma
import datetime
import os
import pickle as pcl
import pandas as pd
from komsular import KomsulariYaz
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

# Verilerin bulunduğu klasör
datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file_df = open(os.path.join(datasetpath, "file_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file_df))
file_df.close()
file_ist = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
istdf = pd.DataFrame(pcl.load(file_ist))
file_ist.close()
del(file_df, file_ist)
print("Dosyalar başarıyla içeri aktarıldı.")

# sütun isimlerini basitleştirelim
df.rename(columns={"Istasyon_No": "istno", "GUNESLENME_SURESI_saat": "gunes", "MAKSIMUM_SICAKLIK_°C":"maxsic", "MINIMUM_SICAKLIK_°C":"minsic", "ORTALAMA_NEM_%": "nem", "GUNLUK_ORTALAMA_HIZI_m_sn":"ruzgar"}, inplace=True)


# gunes, maxsic, minsic, nem ayrı ayrı dataframelere ayıralım. örn |istno|date|gunes|  şeklinde.
# sonra herbir tabloda kendi içinde eleme yapalım. gunes için 1000 satirdan az ise atalım.
# kalanlar ile komşuları tesbit edelim.
# eksik verileri komşulardan idw ile dolduralım.

df_gunes = df[["istno", "date", "gunes"]]
#df_maxsic = df[["istno", "date", "maxsic"]]
#df_minsic = df[["istno", "date", "minsic"]]
#df_nem = df[["istno", "date", "nem"]]
#df_ruzgar = df[["istno", "date", "ruzgar"]]
"""
print("gunes", df_gunes["gunes"].count())
print("maxsic", df_maxsic["maxsic"].count())
print("minsic", df_minsic["minsic"].count())
print("nem", df_nem["nem"].count())
print("ruzgar", df_ruzgar["ruzgar"].count())
"""

df_gunes_ordered = df_gunes.groupby(["istno"])["gunes"].count().sort_values(ascending=False)
# Burada görüleceği üzere güneş değerleri kötü..
# 1000 den az değeri olan istasyonları direk eleyip diğerlerini kullanalım.
"""
df_gunes_chosen = df_gunes_ordered.loc[df_gunes_ordered.values>1000]
print(df_gunes_chosen.count()) # = 59 istasyon
print(df_gunes_chosen.sum())  # = 380.090 adet değer var.
daysXist = (datetime.datetime(2022,12,31) - datetime.datetime(1992,1,1)).days * df_gunes_chosen.count()   # = 667.998 olması gereken değer
print("oran(%):", (380090/667998)*100)  # seçilmiş istasyonların %57'si dolu imiş.
"""

# %57 doluluk idw için yetersiz olacağı düşünüldü.
# 6000 den fazla veri olan istasyonları seçelim
df_gunes_chosen6000 = df_gunes_ordered.loc[df_gunes_ordered.values>6000]
print(df_gunes_chosen6000.count()) #   33 istasyon
print(df_gunes_chosen6000.sum()) # 298.967 adet değer var
daysXist = (datetime.datetime(2022,12,31) - datetime.datetime(1992,1,1)).days * df_gunes_chosen6000.count()   # = 373.626 olması gereken değer
print("oran(%)", (298967/373626)*100 ) # % 80 doluluk oranı bulundu. bu idw için yeterli görüldü.


# Bu seçilmiş istasyonlar dışında kalanları df_gunes tablosundan atalım.
df_gunes_temiz = df_gunes.loc[df_gunes["istno"].apply(lambda x: x in df_gunes_chosen6000.index)]
# indexler bozuldu, resetleyelim.
df_gunes_temiz.reset_index(inplace=True, drop=True)

# Komşuları (ve mesafeleri) belirleyip df_gunes_komsu tablosuna yazalım.
df_gunes_komsu = istdf.loc[istdf["istno"].apply(lambda x: x in df_gunes_chosen6000.index)][["istno", "coordx", "coordy"]]
df_gunes_komsu.reset_index(inplace=True, drop=True)
deneme = KomsulariYaz(df_gunes_komsu, 6)


pd.DataFrame(df_gunes_komsu).to_csv("secilmisgunes.csv", sep=";", decimal=".")

deneme = pd.DataFrame(df_gunes_temiz).merge(df_gunes_komsu, on="istno", how="left")
deneme.to_csv("secilmis33nokta92to2022.csv", sep=";", decimal=".")

