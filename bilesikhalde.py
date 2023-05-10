
####### 1. BÖLÜM ############
# 1. bölümde tüm Excel dosyalarını csv'dosyasına çeviriyoruz ve tek bir DataFrame içinde birlertiriyoruz.
import datetime
import os
import pickle as pcl
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

# Tüm rar dosyalarını tek bir klasöre açınız. duplicate olmamasına özen gösteriyoruz.
# Bu klasörde xlsx ve txt uzantılı dosyalar var. Klasör yolunu aşağıdaki datasetpath değişkenine yazınız.
datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"
    if os.path.exists(datasetpath) == False:
        print("dataset_path yerine uygun dosya yolunu yazınız.")
        quit()

# Tüm excel dosyaları csv'ye dönüştürülüyor
def excelToCSVConverter(pathname):
    if os.path.exists(pathname) == False:
        print("pathname hatalıydı. Program durduruluyor")
        quit()
    excel_file_name_list = os.listdir(pathname)
    print("Dönüştürme başladı.")
    i = 1
    for filename in excel_file_name_list:
        extention = os.path.splitext(filename)[1].lower()
        print(extention)
        if extention != ".xlsx":
            print(filename, "atlanıyor.")
            continue
        excel_fullname = os.path.join(pathname, filename)
        csv_fullname = os.path.join(pathname, os.path.splitext(filename)[0] + ".csv")
        df_from_excel = pd.read_excel(excel_fullname)
        df_from_excel.to_csv(csv_fullname, decimal=".", sep=";", encoding="utf8")
        print(i, "dosya tamamlandı. => ", filename)
        i += 1
    print("Tüm dosyalar dönüştürüldü.")
excelToCSVConverter(datasetpath)

# Tüm csv'leri tek bir DataFrame içinde birleştiriyoruz
def CSVtoDataFrame(pathname):
    csvgunes = []
    csvruzgar = []
    csvminsic = []
    csvmaxsic = []
    csvnem = []
    i = 0
    filenames = os.listdir(pathname)
    for filename in filenames:
        extention = os.path.splitext(filename)[1]
        if extention == ".csv":
            print(filename, "başladı", "sıra:", i)
            i += 1
            temp_df = pd.read_csv(os.path.join(pathname, filename), decimal=",", sep=";")
            temp_df.drop(temp_df.tail(1).index, inplace=True)
            if "Güneş" in filename:
                csvgunes.append(temp_df)
            if "Maksimum" in filename:
                csvmaxsic.append(temp_df)
            if "Minimum" in filename:
                csvminsic.append(temp_df)
            if "Nispi" in filename:
                csvnem.append(temp_df)
            if "Rüzgar" in filename:
                csvruzgar.append(temp_df)
    print("Append işlemi tamamlandı.")

    dfgunes = pd.concat(csvgunes)
    dfmaxsic = pd.concat(csvmaxsic)
    dfminsic = pd.concat(csvminsic)
    dfruzgar = pd.concat(csvruzgar)
    dfnem = pd.concat(csvnem)
    print("Concat işlemi tamamlandı.")

    dfgunes["date"] = pd.to_datetime(dict(year=dfgunes["YIL"], month=dfgunes["AY"], day=dfgunes["GUN"]))
    dfmaxsic["date"] = pd.to_datetime(dict(year=dfmaxsic["YIL"], month=dfmaxsic["AY"], day=dfmaxsic["GUN"]))
    dfminsic["date"] = pd.to_datetime(dict(year=dfminsic["YIL"], month=dfminsic["AY"], day=dfminsic["GUN"]))
    dfruzgar["date"] = pd.to_datetime(dict(year=dfruzgar["YIL"], month=dfruzgar["AY"], day=dfruzgar["GUN"]))
    dfnem["date"] = pd.to_datetime(dict(year=dfnem["YIL"], month=dfnem["AY"], day=dfnem["GUN"]))
    print("(date) isimli sütun eklendi.")

    dfgunes.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfmaxsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfminsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfruzgar.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfnem.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    print("yıl, ay, gün, Istasyon_Adı, gereksiz sütunlar kaldırıldı.")

    df = dfgunes.merge(dfmaxsic, how="outer", on=["Istasyon_No", "date"])
    df = df.merge(dfminsic, how="outer", on=["Istasyon_No", "date"])
    df = df.merge(dfruzgar, how="outer", on=["Istasyon_No", "date"])
    df = df.merge(dfnem, how="outer", on=["Istasyon_No", "date"])
    print("merge işlemi tamamlandı.")

    print(len(df["Istasyon_No"].unique()), "adet istasyon birleştirildi.")
    return df
df = CSVtoDataFrame(datasetpath)

# Bazı değerler (aynı tarih ve aynı istasyon no ile) tekrarlar (duplicate) mevcut.
# Bunları tek satır haline getirelim.
df = df.groupby(["Istasyon_No", "date"]).first()

# Bazı istasyonlarda bazı tarihlerde boşluklar var.. bu sorun yaratıyor.
# her bir istasyon için istenen tarihler arasındaki her bir günü kapsayan full bir tablo yapalım
min_date = datetime.datetime(1992, 1, 1)
max_date = datetime.datetime(2022, 12, 31)

istasyonlar = df["Istasyon_No"].unique()
print(len(istasyonlar), "adet istasyon var")    # 216
df_genis = pd.DataFrame()
for istasyon in istasyonlar:
    df_genis = df_genis.append(pd.DataFrame({"Istasyon_No": istasyon, "date": pd.date_range(start=min_date, end=max_date, freq="D")}))
print("Geniş tablo yapıldı. csv değerleri bunun üzerine derç ediliyor.")
df = df_genis.merge(df, how="left", on=["Istasyon_No", "date"])

# Istasyon_No object görünüyor. int64 yapalım.
df = df.astype({"Istasyon_No": "int64"})

# txt dosyalarında koordinat verileri ve istasyon isimleri var. Bunları tek bir txt dosyasında birleştirelim.
def infoTXT_Birlestirici(pathname):
    son = open((os.path.join(pathname, "tamamı.txt")), "wb")
    for filename in os.listdir(pathname):
        if os.path.splitext(filename)[1].lower() != ".txt":
            continue
        temp = open(os.path.join(pathname, filename), "rb")
        lines = temp.readlines()
        lines.pop(0)
        son.writelines(lines)
    son.close()
infoTXT_Birlestirici(datasetpath)

# Koordinat bilgilerini DataFrame içine alıyoruz.
def infoTXT_GetCoords(txtfilepath):
    df = pd.DataFrame(columns=["istno", "coordx", "coordy", "height"])
    temp = open(txtfilepath, "rb")
    lines = temp.readlines()
    for line in lines:
        if len(line) > 5:
            splt = line.split(sep=b"|")
            istno = int(splt[0])
            coordx = float(splt[4])
            coordy = float(splt[5])
            height = int(splt[6])
            df = df.append({"istno": istno, "coordx":coordx, "coordy":coordy, "height":height}, ignore_index=True)
            df = df.astype(dtype={"istno": "int64", "coordx": "float64", "coordy": "float64", "height": "int64" })
    return df
ist_df = infoTXT_GetCoords(os.path.join(datasetpath, "tamamı.txt"))
# unique hale getirelim
ist_df.drop_duplicates(inplace=True)

print(len(istasyonlar))     #=> 216
print(len(ist_df))          #=> 219
# csv dosyalarında olmayan 219-216 = 3 istasyon txt dosyalarında var
# tespit edildi: 3671, 4919, 6989 no'lu istasyonlar csv'lerde yok, ancak txt'lerde var.

# istasyon isimleri txt'lerde düzgün değil. csv'lerden alalım. istisimDF + dfcoords => istasyonDF yapalım.
def istasyon_isimler_from_CSVs(pathname):
    dfs = []
    allfiles = os.listdir(pathname)
    for fn in allfiles:
        if os.path.splitext(fn)[1] == ".csv":
            temp_df = pd.read_csv(os.path.join(pathname, fn), sep=";", decimal=".")
            temp_df.drop(temp_df.tail(1).index, inplace=True)
            dfs.append(temp_df)

    complate_df = pd.concat(dfs, join="inner", ignore_index=True)
    df_grp_by_istno = complate_df.groupby("Istasyon_No").first()["Istasyon_Adi"]
    df_grp_by_istno["istno"] = df_grp_by_istno.index
    df_grp_by_istno = df_grp_by_istno.astype({"istno": "int64"})
    return df_grp_by_istno
ist_isim_df = istasyon_isimler_from_CSVs(datasetpath)
ist_df = ist_isim_df.merge(ist_df, how="left", on="istno")

file = open(os.path.join(datasetpath, "file_df.pcl"), "wb")
pcl.dump(df, file)
file.close()
file = open(os.path.join(datasetpath, "file_ist.pcl"), "wb")
pcl.dump(ist_df, file)
file.close()
del file
print("Dosyalar Kaydedildi.")

####### 1. BÖLÜM SONU ############


####### 2. BÖLÜM ############
# 2. bölümde veriler inceleniyor.
import datetime
import os
import pickle as pcl
from sklearn.metrics import r2_score
import numpy as np
import pandas as pd
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"
    if os.path.exists(datasetpath) == False:
        print("dataset_path yerine uygun dosya yolunu yazınız.")
        quit()

file = open(os.path.join(datasetpath, "file_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.readable()
file.close()
file = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
ist_df = pd.DataFrame(pcl.load(file))
file.close()
del file, datasetpath
print("Dosyalar başarıyla içeri aktarıldı.")

# sütun isimlerini basitleştirelim
df.rename(columns={"Istasyon_No": "istno",
                   "GUNESLENME_SURESI_saat": "gunes",
                   "MAKSIMUM_SICAKLIK_°C": "maxsic",
                   "MINIMUM_SICAKLIK_°C": "minsic",
                   "ORTALAMA_NEM_%": "nem",
                   "GUNLUK_ORTALAMA_HIZI_m_sn": "ruzgar"}, inplace=True)
ist_df.rename(columns={"coordx": "lat",
                       "coordy": "lon",
                       "height": "z_msl"
                       }, inplace=True)

# Veriler inceleniyor.
toplam_gun_sayisi = (datetime.datetime(2022, 12, 31) - datetime.datetime(1992, 1, 1)).days
toplam_istasyon_sayisi = len(ist_df.index)
beklenen_veri_sayisi = toplam_istasyon_sayisi * toplam_gun_sayisi
print("Günlük Güneşlenme saat(%)", df["gunes"].count() / beklenen_veri_sayisi * 100)
print("Günlük Maksimum Sıcaklık(%)", df["maxsic"].count() / beklenen_veri_sayisi * 100)
print("Günlük Minimum Sıcaklık(%)", df["minsic"].count() / beklenen_veri_sayisi * 100)
print("Günlük Ortalama Nem(%)", df["nem"].count() / beklenen_veri_sayisi * 100)
print("Günlük Ortalama Rüzgar(%)", df["ruzgar"].count() / beklenen_veri_sayisi * 100)
# Burada görüleceği üzere güneş değerleri kötü..
del beklenen_veri_sayisi, toplam_gun_sayisi, toplam_istasyon_sayisi

# Güneş verilerini alalım
df_gunes = df[["istno", "date", "gunes"]]

# Güneşlenme verileri bakımından istasyonları gruplayıp sıralayalım.
df_gunes_ordered = df_gunes.groupby(["istno"])["gunes"].count().sort_values(ascending=False)
print(df_gunes_ordered.head())

# Güneş verisi 1000 den az olan istasyonları direk eleyip diğerlerini kullanalım. İPTAL
"""
df_gunes_chosen = df_gunes_ordered.loc[df_gunes_ordered.values>1000]
print(df_gunes_chosen.count()) # = 59 istasyon
print(df_gunes_chosen.sum())  # = 380.090 adet değer var.
daysXist = (datetime.datetime(2022,12,31) - datetime.datetime(1992,1,1)).days * df_gunes_chosen.count()   # = 667.998 olması gereken değer
print("oran(%):", (380090/667998)*100)  # seçilmiş istasyonların %57'si dolu imiş.
"""
# 59 istasyon alındı. Doluluk oranı %57 idi. Bu yeterli görülmedi!
# Güneş için 6000 den fazla veri olan istasyonları seçelim
df_gunes_secilen = df_gunes_ordered.loc[df_gunes_ordered.values > 6000]
gunes_secilen_ist_sayisi = df_gunes_secilen.count()
print("istasyon sayısı:", gunes_secilen_ist_sayisi)     # 33 istasyon
toplam_gun_sayisi = (datetime.datetime(2022, 12, 31) - datetime.datetime(1992, 1, 1)).days
print("toplam_gun_sayisi:", toplam_gun_sayisi)
beklenen_veri_sayisi = gunes_secilen_ist_sayisi * toplam_gun_sayisi
print("beklenen_veri_sayisi:", beklenen_veri_sayisi)
gunes_secilen_deger_sayisi = df_gunes_secilen.sum()
print("değer sayısı:", gunes_secilen_deger_sayisi)      # 298.967 adet değer var
print("doluluk oranı (%):", (gunes_secilen_deger_sayisi / beklenen_veri_sayisi) * 100)  # %80 doluluk oranı bulundu. bu idw için yeterli görüldü!
del beklenen_veri_sayisi, gunes_secilen_deger_sayisi, gunes_secilen_ist_sayisi, toplam_gun_sayisi, df_gunes_ordered

# Yalnızca bu seçilmiş istasyonları içeren verileri alalım.
df = df.loc[df["istno"].apply(lambda x: x in df_gunes_secilen)]
df.reset_index(inplace=True, drop=True)


# Seçilen istasyonların lat-lon ve yükseklik değerlerini "komsular" tablosuna alalım.
secilen_istasyonlar = df.groupby(["istno"]).first().index
komsular = ist_df.loc[ist_df.apply(lambda row: row["istno"] in secilen_istasyonlar, axis=1)]
komsular = komsular[["istno", "lat", "lon"]]
komsular.reset_index(inplace=True, drop=True)
print(komsular.head())

# 33 adet istasyon için en yakın komşuların istasyon numaralarını ve mesafelerini bulalım (pisagor ile)
# Bu komşuları mesafe yakından uzağa olacak şekilde sıralayım en yakın 10 komşu ile DataFrame yapalım.
def mesafe(row, tablo, komsu_sayisi):
    k = tablo["istno"]
    m = ((tablo["lat"] - row["lat"].squeeze()) ** 2 + (tablo["lon"] - row["lon"].squeeze()) ** 2) ** 0.5
    km = pd.DataFrame({"k": k, "m": m}).sort_values(by="m")
    km = km.convert_dtypes()
    km = km.iloc[1:komsu_sayisi+1]
    km.reset_index(drop=True, inplace=True)
    return km.unstack()
kom_mes = komsular.apply(lambda x: mesafe(x, komsular, 10), axis=1)
kom_mes["istno"] = komsular["istno"]
kom_mes.set_index("istno", drop=True, inplace=True)
print(kom_mes.head())
del secilen_istasyonlar, df_gunes, df_gunes_secilen

# IDW ile eksik verileri tamamlamaya hazırız!
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
        # komşunun o tarihteki değeri alınıyor
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

        # paydanın 0 dönmesi hata verir. -np.nan olarak dolduruyoruz. Bunları daha sonra eleyebiliriz.
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

# 5 parametre için değerin dolu yada boş olup olmadığına bakmaksızın...
# idw ile doldurmaları başlatalım. Buradan dönen değerleri 'parametre'_tahmin ekiyle sütun olarak ekleyelim.
# NOT: 1 saat kadar sürmüştür!!!
for parametre in parametreler:
    # ## df[parametre + "_tahmin"] = df.apply(lambda row: idw_yapici(row, df, kom_mes, komsu_sayisi, power, parametre), axis=1)
    print(parametre)

# burada eklenen tahmin sütunlarının 100% dolduğu onaylanır.
(df.count() / len(df.index)) * 100

# Güneş tahminlerini doğruluyoruz.
df_gunes_dolu = df.loc[df["gunes"].notnull]
r2_score(df_gunes_dolu["gunes"], df_gunes_dolu["gunes_tahmin"])
# NOT: güneşlenme için farklı komşu sayıları ve farklı power değerleri ile yapılan denemelerde
# gerçek değer ile tahmin değeri arasında r2_score fonksiyonu ile yapılan karşılaştırmalarda şu sonuçlar bulundu:
# k=5 p=2       score = 0.716163
# k=10 p=2      score = 0.745457
# k=10 p=3      score = 0.728464
# k=10 p=1.5    score = 0.749967
# k=10 p=1      score = 0.750000
# k=8 p=1       score = 0.750048
# k=3 p=1       score = 0.622882
# k=5 p=1       score = 0.724000
# k=10 p=0.8    score = 0.748687

# Tüm parametreler için r2 hesaplayalım
for parametre in parametreler:
    dolu_indexler = df.loc[df[parametre].notnull()].index
    score = r2_score(df.loc[dolu_indexler, parametre].to_list(), df.loc[dolu_indexler, parametre+"_tahmin"].to_list())
    print(parametre, "\t", score)
"""
Sonuç
gunes 	 0.7170665295205193
maxsic 	 0.9437998740219037
minsic 	 0.8861197060054262
ruzgar 	 0.0966887585813294
nem 	 0.4665202129758401
"""
# Burada rüzgar (U_z) ve nem (RH_mean) değerleri idw ile tahmin edildiğinde düşük r2 verdiği için farklı bir yöntem denendi.
# Buna göre rüzgar ve nem verilerinde yüksek korelasyon gösteren komşu istasyonlar ile 33 * 33 lük bir tablo yapılacak..
# en yüksek korelasyon gösteren 4-5 komşu ile linear interpolasyon ile değerler doldurulacaktı.
# Ancak rüzgar bakımından korelasyonlar aşırı düşük bulunduğundan bu işlemden vazgeçildi.
# İstasyon çiftleri arazındaki bazı korelasyon değerleri şöyledir:
# 0.59, 0.40, 0.45, 0.55, 0.24, 0.61, -0.95, 0.52, 0.37, 0.04, 0.47, 0.13, -1.10, 0.45, 0.19
# Ayrıca ordinary krigging de araştırıldı. Ancak yine doğru bir tamamlama yapılamadı.
# Zaten seçilen 33 istasyonda güneş dışındaki verilerde önemli bir eksiklik olmadığı şu şekilde görülebilir:
print(df.count() / len(df.index) * 100)
# ETo kütüphanesi değerleri bu şekilde de kabul edebiliyor. Ve dahi istenirse linear intepolasyon uygulayabiliyor.

# ETo kütüphanesinin istediği başlıkları ekleyelim.
df.rename(columns={"gunes":  "n_sun",
                   "maxsic": "T_max",
                   "minsic": "T_min",
                   "ruzgar": "U_z",
                   "nem":    "RH_mean"
                   }, inplace=True)

# Bu idw tahminlerini içeren tabloyu kaydedelim.
file = open(os.path.join(datasetpath, "df_tamamlandi.pcl"), "wb")
pcl.dump(df, file)
file.close()
####### 2. BÖLÜM SONU ############


####### 3. BÖLÜM ############
# 3. bölümde ETo hesaplanıyor.
import os
import pickle as pcl
import numpy as np
import pandas as pd
from eto import ETo
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file = open(os.path.join(datasetpath, "df_tamamlandi.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
file = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
ist_df = pd.DataFrame(pcl.load(file))
file.close()
del file

ist_df.rename(columns={"coordx": "lat",
                       "coordy": "lon",
                       "height": "z_msl"
                       }, inplace=True)

# IDW tahmini kabul edilenleri alıyoruz
df["n_sun"] = df["n_sun_tahmin"]
df["T_max"] = df["T_max_tahmin"]
df["T_min"] = df["T_min_tahmin"]

# diğer tahminleri atıyoruz.
df.drop(["n_sun_tahmin", "T_max_tahmin", "T_min_tahmin", "U_z_tahmin","RH_mean_tahmin"], axis=1, inplace=True)
print(df.count() / len(df.index) * 100)
df.set_index("date", inplace=True, drop=True)

istasyonlar = df.groupby("istno").first().index
ist_df.rename(columns={"coordx": "lat",
                       "coordy": "lon",
                       "height": "z_msl"
                       }, inplace=True)

param_estimation_df_arr = []
fao_df_arr = []
for istasyon in istasyonlar:
    df_x = df.loc[df["istno"] == istasyon]
    df_x.drop(columns=["istno"], inplace=True)

    istasyon_info = ist_df.loc[ist_df["istno"] == istasyon]
    z_msl = istasyon_info.z_msl.squeeze()
    lat = istasyon_info.lat.squeeze()
    lon = istasyon_info.lon.squeeze()
    # TZ_lon = 173
    freq = 'D'
    et1 = ETo()
    et1.param_est(df_x, freq, z_msl, lat, lon)
    temp_est_df = et1.ts_param
    temp_est_df["istno"] = istasyon
    param_estimation_df_arr.append(temp_est_df)
    fao_df_arr.append(et1.eto_fao())

# ETo kütüphanesi verisi bulunmayan bazı parametreleri hesapladı
param_est_df = pd.concat(param_estimation_df_arr)
param_est_df["date"] = param_est_df.index
param_est_df.reset_index(inplace=True, drop=True)
# ETo kütüphünesi fao yöntemine göre ET0 değerlerini hesapladı
fao_df = pd.DataFrame(pd.concat(fao_df_arr))
fao_df["date"] = fao_df.index
fao_df.reset_index(inplace=True, drop=True)


# iki tabloyu birleştirip csv olarak dışarı verelim
fao_df.drop("date", inplace=True, axis=1)
sonuc_df = param_est_df.merge(fao_df, left_index=True, right_index=True)
sonuc_df.to_csv(os.path.join(datasetpath, "sonuc_df.csv"), decimal=".", sep=";")

# sütun yerleşimi düzenleme
temp = sonuc_df[["istno", "date"]]
sonuc_df.drop(["istno", "date"], inplace=True, axis=1)
sonuc_df = temp.merge(sonuc_df, left_index=True,right_index=True)


# ayrıca pcl ile kaydedelim
file = open(os.path.join(datasetpath, "sonuc_df.pcl"), "wb")
pcl.dump(sonuc_df, file)
file.close()
####### 3. BÖLÜM SONU ############


####### 4. BÖLÜM ############
# 4. GSI hesaplanıyor.
import os
import pickle as pcl
import numpy as np
import pandas as pd
import datetime
from eto import ETo
import matplotlib.pyplot as plt
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

datasetpath = "C:/Users/ozitron/Desktop/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"

file = open(os.path.join(datasetpath, "sonuc_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
del file

# zeytin parametreleri
Tm_min = 0.0
Tm_max = 7.0
rad_min = 5.0
rad_max = 12.0
etp_min = 2.0
etp_max = 5.0
fot_min = 10.0
fot_max = 11.0

def doy(date):
    return date.timetuple().tm_yday

# phi olarak latude yazılır.
def photoperiod(phi, doy, verbose=False):
    phi = np.radians(phi)  # Convert to radians
    light_intensity = 2.206 * 10 ** -3

    C = np.sin(np.radians(23.44))  # sin of the obliquity of 23.44 degrees.
    B = -4.76 - 1.03 * np.log(
        light_intensity)  # Eq. [5]. Angle of the sun below the horizon. Civil twilight is -4.76 degrees.

    # Calculations
    alpha = np.radians(90 + B)  # Eq. [6]. Value at sunrise and sunset.
    M = 0.9856 * doy - 3.251  # Eq. [4].
    lmd = M + 1.916 * np.sin(np.radians(M)) + 0.020 * np.sin(np.radians(2 * M)) + 282.565  # Eq. [3]. Lambda
    delta = np.arcsin(C * np.sin(np.radians(lmd)))  # Eq. [2].

    # Defining sec(x) = 1/cos(x)
    P = 2 / 15 * np.degrees(
        np.arccos(np.cos(alpha) * (1 / np.cos(phi)) * (1 / np.cos(delta)) - np.tan(phi) * np.tan(delta)))  # Eq. [1].
    return P



df["i_Tmin"] = (df["T_min"] - Tm_min) / (Tm_max - Tm_min)
df["i_rad"] = (df["R_s"] - rad_min) / (rad_max - rad_min)
df["i_etp"] = (df["ETo_FAO_mm"] - etp_min) / (etp_max - etp_min)
df["doy"] = df.apply(lambda x : doy(x["date"]), axis=1)
lat_df = ist_df[["istno", "lat"]]
df = df.merge(lat_df, how="outer", on="istno")
df["fotoperiod"] = photoperiod(df["lat"], df["doy"])
df["i_foto"] = (df["fotoperiod"] - fot_min) / (fot_max - fot_min)

df["i_Tmin"].clip(lower=0.0, upper=1.0, inplace=True)
df["i_rad"].clip(lower=0.0, upper=1.0, inplace=True)
df["i_etp"].clip(lower=0.0, upper=1.0, inplace=True)
df["i_foto"].clip(lower=0.0, upper=1.0, inplace=True)

df["GSI"] = df["i_Tmin"] * df["i_rad"] * df["i_etp"] * df["i_foto"]


df17 = pd.DataFrame(df.loc[df["istno"] == 17110])
df17.set_index("date", inplace=True, drop=True)
aylikort = df17.groupby(df17.date.dt.month)['GSI'].mean()

aylikort = pd.DataFrame(aylikort)
plt.plot(aylikort)
plt.fill_between(aylikort.index, aylikort["GSI"])
plt.show()







file = open(os.path.join(datasetpath, "gsi_df.pcl"), "wb")
pcl.dump(df, file)
file.close()