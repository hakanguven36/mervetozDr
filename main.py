# BÖLÜM 1: Excel ve txt dosyalarından tüm verileri birleştirme
# Tüm rar dosyalarını tek bir klasöre açınız. duplicate olmamasına özen gösteriniz.
# bu klasörde xlsx ve txt uzantılı dosyalar var. klasör ismini aşağıdaki datasetpath değişkenine yazınız.

import datetime
import os
import numpy
import pandas as pd
import pickle as pcl
from xlsTOcsv import excelToCSVConverter, infoTXT_Birlestirici, infoTXT_GetCoords, istasyonisimlerFromCSVs
from paketalan import CSVtoDataFrame
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

# Verilerin bulunduğu klasör
datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

# tüm excel verileri csv'ye dönüştürülüyor
excelToCSVConverter(datasetpath)

# tüm csv'leri tek bir tabloda birleştiriyoruz
dfcsv = CSVtoDataFrame(datasetpath)

# bazı değerler 32 ye kadar tekrarlanıyor.. Unique yapalım
dfunique = dfcsv.groupby(["Istasyon_No", "date"]).first()

# bazı istasyonlarda bazı tarihler dolu bazılar boş.. bu sorun yaratıyor.
# her bir istasyon ve her bir tarihler aralığını kapsayan full bir tablo yapıp üzerine csv'lerden gelen verileri merge ediyoruz.
# Böylece tarih atlanmamış oluyor.
mindate = datetime.datetime(1992, 1, 1)
maxdate = datetime.datetime(2022, 12, 31)

istasyonlar = dfcsv["Istasyon_No"].unique()
print(len(istasyonlar), "adet istasyon var")
df = pd.DataFrame()
for istasyon in istasyonlar:
    df = df.append(pd.DataFrame({"Istasyon_No": istasyon, "date": pd.date_range(start=mindate, end=maxdate, freq="D")}))
print("geniş tablo yapıldı. csv değerleri derç ediliyor.")
df = df.merge(dfunique, how="left", on=["Istasyon_No", "date"])
print("geniş tablonun dtype'ları: ")
print(df.dtypes)

# istasyon no object görünüyor. int64 yapalım.
df = df.astype({"Istasyon_No": "int64"})

# ram temizliği
del(dfcsv, dfunique, istasyon, mindate, maxdate, istasyonlar)

# txt koordinat verileri tek bir txt dosyasında birleştiriliyor.
infoTXT_Birlestirici(datasetpath)
# koordinat bilgilerini tabloya alıyoruz.
dfcoords = infoTXT_GetCoords(os.path.join(datasetpath, "tamamı.txt"))
# unique hale getirelim
dfcoords.drop_duplicates(inplace=True)


print(len(istasyonlar))
#=> 216
print(len(dfcoords))
#=> 219
# csv dosyalarında olmayan 219-216 = 3 istasyon txt dosyalarında var
# tespit edildi: 3671, 4919, 6989 no'lu istasyonlar csv'lerde yok, ancak txt'lerde var.

# istasyon isimleri txt'lerde düzgün değil. csv'lerden alalım. istisimDF + dfcoords => istasyonDF yapalım.
istisimDF = istasyonisimlerFromCSVs(datasetpath)
istisimDF = istisimDF.astype({"istno": "int64"})
istasyonDF = istisimDF.merge(dfcoords, how="left", on="istno")

# ram temizliği
del(istisimDF, dfcoords)

# df ve istasyonDF tablolarını pcl formatında kaydedip DONDURALIM.
file_df = open(os.path.join(datasetpath, "file_df.pcl"), "wb")
pcl.dump(df, file_df)
file_df.close()
file_ist = open(os.path.join(datasetpath, "file_ist.pcl"), "wb")
pcl.dump(istasyonDF, file_ist)
file_ist.close()
del(file_df, file_ist)
print("Dosyalar Kaydedildi.")

####### BÖLÜM SONU ############
