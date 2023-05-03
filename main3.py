import datetime
import os
import pickle as pcl

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file = open(os.path.join(datasetpath, "file_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.readable()
file.close()
file = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
ist_df = pd.DataFrame(pcl.load(file))
file.close()
del(file)
print("Dosyalar başarıyla içeri aktarıldı.")

# Mevcut dosyalarda:
# df => 216 adet istasyonun (1,1,1992 - 31,12,2022) tarih aralığındaki "her bir gün" için bazı meteoroloji parametreleri
# ist_df => 216 adet istasyonun ad, lat-lon, yükseklik verileri bulunmaktadır.
# Yer kaplamaması için iki ayrı dosyada tutulmaktadır.

# ETo paketine uygun şekilde isimlendirme yapıyoruz
df.rename(columns={"Istasyon_No":               "istno",
                   "GUNESLENME_SURESI_saat":    "n_sun",
                   "MAKSIMUM_SICAKLIK_°C":      "T_max",
                   "MINIMUM_SICAKLIK_°C":       "T_min",
                   "ORTALAMA_NEM_%":            "RH_mean",
                   "GUNLUK_ORTALAMA_HIZI_m_sn": "U_z"
                   }, inplace=True)

ist_df.rename(columns={"coordx": "lat",
                       "coordy": "lon",
                       "height": "z_msl"
                       }, inplace=True)

# En eksik veriler "günlük güneşlenme süresi" sütununda olduğundan
# ve bu değişkenin en önemli değişken olmasindan dolayı
# istasyon seçimini/elemesini bu değişkenin bulunuş durumuna göre yapıyoruz

# Önce güneş verilerinin bulunuş sayısına göre istasyonları gruplayalım,
# ve en büyükten itibaren sıralayalım.
df_gunes_ordered = df.groupby(["istno"])["n_sun"].count().sort_values(ascending=False)

# 31 yılda 6000 günden fazla verisi olan istasyonlarda güneşlenme doluluk oranı %80 bulunmuştur.
# Bu nedenle bu istasyonlar seçilmiştir. (33 adet)
df_gunes_chosen6000 = df_gunes_ordered.loc[df_gunes_ordered.values > 6000]

# Diğer istasyonları atıp yalnızca 33 istasyon verilerini tutuyoruz.
df = df.loc[df["istno"].apply(lambda x: x in df_gunes_chosen6000.index)]
df.reset_index(inplace=True, drop=True)

# Seçilen istasyonların lat-lon ve yükseklik değerlerini "komsular" tablosuna alalım.
komsular = ist_df.loc[ist_df["istno"].apply(lambda x: x in df_gunes_chosen6000.index)][["istno", "lat", "lon", "z_msl"]]
komsular.reset_index(inplace=True, drop=True)

# Bu fonksiyon bir istasyonun diğer istasyonlarla olan mesafesini koordinat verilerine dayalı olarak hesaplamakta,
# yakından uzağa sıralamakta,
# istenen komşu sayısı kadar sütun dönmektedir.
def mesafe(row, tablo, komsu_sayisi):
    k = tablo["istno"]
    m = ((tablo["lat"] - row["lat"].squeeze()) ** 2 + (tablo["lon"] - row["lon"].squeeze()) ** 2) ** 0.5
    km = pd.DataFrame({"k": k, "m": m}).sort_values(by="m")
    km = km.convert_dtypes()
    km = km.iloc[1:komsu_sayisi+1]
    km.reset_index(drop=True, inplace=True)
    return km.unstack()

# 33 adet istasyon için en yakın 10 adet komşu numaralarını ve mesafelerini bulalım
kom_mes = komsular.apply(lambda x: mesafe(x, komsular, 10), axis=1)

# istasyon numarasını index olarak kullanalım
kom_mes["istno"] = komsular["istno"]
kom_mes.set_index("istno", drop=True, inplace=True)

# Eksik verileri doldurmak için IDW formülünü kullanacağız
# Öncelikle parametrelerimizi yazıyoruz.
# komşu sayısı 10 ve power 2 alınarak yapılan denemelerde güneşlenme süresi bakımından,
# % 70-80 aralığında korelasyon bulunmuştur.


# Bu fonksiyon tablodaki herbir satır için (373659 adet) tek tek IDW hesaplaması yapıyor.
# Bulunan değerlerin parametre ismine "_tahmin" şeklinde ayrı sütunda kaydediyor.
# Böylece hali hazırda dolu değerler ile tahmin edilen değerlerin korelasyonları kontrol edilebilir.
# Bu işlem 10-15 dk kadar sürebilir. (apply fonksiyonu'da aynı şekilde uzun sürdüğünden iterrow kullanıldı)
"""
komsu_sayisi = 10
power = 2

def IDW_yap(paramname):
    global df   # üzerine yazılacak
    global islem_no
    islem_no = 0
    tamamlanma_yuzdesi = 0
    old_tamamlanma_yuzdesi = -1
    print(paramname, "için başlandı.")

    for r, row in df.iterrows():
        islem_no += 1
        tamamlanma_yuzdesi = int((islem_no/toplam_islem)*100)
        if tamamlanma_yuzdesi != old_tamamlanma_yuzdesi:
          print(paramname, "Tamamlanma(%): ", tamamlanma_yuzdesi)
          old_tamamlanma_yuzdesi = tamamlanma_yuzdesi

        row_istno = row["istno"]
        row_date = row["date"]
        pay = 0
        payda = 0

        for i in range(komsu_sayisi):
            # her komşunun istasyon numarası ve mesafesi alınıyor
            k_istno = kom_mes.loc[kom_mes.index == row_istno, "k"][i].squeeze()
            k_mes = kom_mes.loc[kom_mes.index == row_istno, "m"][i].squeeze()

            # Bu komşunun aynı tarihteki seçilen parametre için değerini çekiyoruz
            k_val = df.loc[(df["istno"] == k_istno) & (df["date"] == row_date)][paramname]

            # Değer boş dönerse bunu atlayıp bir sonraki komşuya geçiyoruz
            if k_val.empty:
                continue

            k_val = k_val.squeeze()

            # IDW formülündeki pay ve payda
            pay += k_val / (k_mes ** power)
            payda += 1 / (k_mes ** power)

        # paydanın 0 dönmesi durumunda program 0'a bölünemez hatası verecektir.
        # Bu değeri -999 olarak dolduruyoruz. Bunları daha sonra eleyebiliriz.
        if payda == 0:
            df.loc[r, paramname + "_tahmin"] = -999
        df.loc[r, paramname + "_tahmin"] = pay / payda


# Her parametre için IDW_yap fonksiyonunu çalıştırıyoruz.
parametreler = df.columns[2:]
for parametre in parametreler:
    IDW_yap(parametre)
"""





def idw_yapici(row, df, kom_mes, komsu_sayisi, power, paramname):
    global islem_no
    global tamamlanma_yuzdesi
    global old_tamamlanma_yuzdesi

    islem_no += 1
    tamamlanma_yuzdesi = int((islem_no / toplam_islem) * 100)
    if tamamlanma_yuzdesi != old_tamamlanma_yuzdesi:
        print(paramname, "Tamamlanma(%): ", tamamlanma_yuzdesi)
        old_tamamlanma_yuzdesi = tamamlanma_yuzdesi

    row_istno = row["istno"]
    row_date = row["date"]
    pay = 0
    payda = 0


    for i in range(komsu_sayisi):
        # her komşunun istasyon numarası ve mesafesi alınıyor
        k_istno = kom_mes.loc[kom_mes.index == row_istno, "k"][i].squeeze()
        k_mes = kom_mes.loc[kom_mes.index == row_istno, "m"][i].squeeze()
        k_val = df.loc[(df["istno"] == k_istno) & (df["date"] == row_date)][paramname]

        # Değer boş dönerse bunu atlayıp bir sonraki komşuya geçiyoruz
        if k_val.empty:
            continue
        k_val = k_val.squeeze()
        if np.isnan(k_val) or k_val is None:
            continue

        # IDW formülündeki pay ve payda
        pay += k_val / (k_mes ** power)
        payda += 1 / (k_mes ** power)

        # paydanın 0 dönmesi durumunda program 0'a bölünemez hatası verecektir.
        # Bu değeri -999 olarak dolduruyoruz. Bunları daha sonra eleyebiliriz.
        if payda == 0:
            return np.nan
        return pay / payda


komsu_sayisi = 10
power = 2

islem_no = 0
toplam_islem = len(df.index)
tamamlanma_yuzdesi = 0
old_tamamlanma_yuzdesi = -1
parametreler = df.columns[2:]

# 5 adet parametre için doldurmaları başlatalım. 1 saat kadar sürecek!!!
for parametre in parametreler:
    df[parametre + "_tahmin"] = df.apply(lambda row: idw_yapici(row, df, kom_mes, komsu_sayisi, power, parametre), axis=1)

# burada tahmin sütunlarının 100% dolduğu onaylanır.
(df.count() / len(df.index)) * 100

# Bu tabloyu kaydedelim.
file = open(os.path.join(datasetpath, "df_tamamlandi.pcl"), "wb")
pcl.dump(df, file)
file.close()

# Son olarak korelasyonlara bakalım
df = pd.DataFrame(df)

for parametre in parametreler:
    indexler = df.loc[df[parametre].notnull()].index
    score = r2_score(df.loc[indexler, parametre].to_list(), df.loc[indexler, parametre+"_tahmin"].to_list())
    print(parametre, "\t", score)

df.count() / len(df.index) * 100

"""
Sonuç
n_sun 	 0.6170665295205193
T_max 	 0.9437998740219037
T_min 	 0.8861197060054262
U_z 	 0.09668875858132941
RH_mean	 0.4665202129758401
güneş verisinde yeterli korelasyon yok. IDW superparametrelerini değiştirerek 70 üzerine çıkaralım.
rüzgar ve nem için IDW kullanılamaz. 216 istasyon ile Korelasyon tablosu oluşturup oradan devam edelim.
Yine de rüzgar ve nemdeki boşluk oranı % 2-3 civarında. Yani çok hayati bir etkisi yok.
"""











