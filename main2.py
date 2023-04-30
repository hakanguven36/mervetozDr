# BÖLÜM-2 Boşluk Doldurma
# import numpy
import datetime
import os
import pickle as pcl
import pandas as pd
from komsular import komsulari_yaz
from idwyapan import idw_yap
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

# Verilerin bulunduğu klasör
datasetpath = "C:/Users/ozitron/Desktop/kullanımda/" # Evde
#datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/" # İşte


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
# şimdilik siliyorum df'yi
del(df)
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
print("istasyon sayısı:", df_gunes_chosen6000.count()) #   33 istasyon
print("değer sayısı:", df_gunes_chosen6000.sum()) # 298.967 adet değer var
daysXist = (datetime.datetime(2022,12,31) - datetime.datetime(1992,1,1)).days * df_gunes_chosen6000.count()   # = 373.626 olması gereken değer
print("oran(%)", (298967/373626)*100 ) # % 80 doluluk oranı bulundu. bu idw için yeterli görüldü.


# Yalnızca bu seçilmiş istasyonları içeren verileri temiz tablosuna alalım.
df_gunes_temiz = df_gunes.loc[df_gunes["istno"].apply(lambda x: x in df_gunes_chosen6000.index)]
# indexler bozuldu, resetleyelim.
df_gunes_temiz.reset_index(inplace=True, drop=True)

# Komşuları (ve mesafeleri) belirleyip df_gunes_komsu tablosuna yazalım.
df_gunes_komsu = istdf.loc[istdf["istno"].apply(lambda x: x in df_gunes_chosen6000.index)][["istno", "coordx", "coordy"]]
df_gunes_komsu.reset_index(inplace=True, drop=True)
df_gunes_komsu = komsulari_yaz(df_gunes_komsu, 5)
# komsuların istno'larını integer yapalım
df_gunes_komsu = df_gunes_komsu.astype({"k0": "int64", "k1": "int64", "k2": "int64", "k3": "int64", "k4": "int64"})

# Belirlenen komşulardan df_gunes tablosundaki boş değerler için idw hesaplayıp değeri yerine yazalım.
deneme1 = idw_yap(df_gunes_temiz, df_gunes_komsu, "gunes", 5, 2)
deneme2 = pd.DataFrame(deneme1).sort_values(by=["date", "istno"])
deneme2.reset_index(inplace=True, drop=True)
deneme2.to_csv("dolduruldu.csv", sep=";", decimal=".")

df_gunes_temiz_sort = df_gunes_temiz.sort_values(by=["date", "istno"])
df_gunes_temiz_sort.reset_index(inplace=True, drop=True)
df_gunes_temiz_sort.to_csv("doldurulmadi.csv", sep=";", decimal=".")

filename = open(os.path.join(datasetpath, "dfgunes.pcl"), "wb")
pcl.dump(df_gunes_temiz, filename)
filename.close()

filename = open(os.path.join(datasetpath, "dfgunes.pcl"), "rb")
mesela = pcl.load(filename)

