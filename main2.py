# BÖLÜM-2 Boşluk Doldurma

import os
import pickle as pcl
import pandas as pd
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
df_maxsic = df[["istno", "date", "maxsic"]]
df_minsic = df[["istno", "date", "minsic"]]
df_nem = df[["istno", "date", "nem"]]
df_ruzgar = df[["istno", "date", "ruzgar"]]

print("gunes", df_gunes["gunes"].count())
print("maxsic", df_maxsic["maxsic"].count())
print("gunes", df_minsic["minsic"].count())
print("gunes", df_nem["nem"].count())
print("gunes", df_ruzgar["ruzgar"].count())


temp = df_gunes.groupby(["istno"])["gunes"].count().sort_values(ascending=False)
# Burada görüleceği üzere güneş değerleri kötü.. 1000 den az değeri olan istasyonları direk eleyip diğerlerini kullanalım.
df_gunes_count = df_gunes.groupby(["istno"])["gunes"].count()
df_gunes_sec = df_gunes_count.loc[df_gunes_count>1000]



