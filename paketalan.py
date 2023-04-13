import datetime
import os
import pickle
import pandas as pd


def CSVtoDataFrame(pathname):
    csvgunes = []
    csvruzgar = []
    csvminsic = []
    csvmaxsic = []
    csvnem = []
    i = 0
    filenames = os.listdir(pathname)
    for fn in filenames:
        if os.path.splitext(fn)[1] == ".csv":
            print(fn, "başladı", "sıra:", i)
            i += 1
            temp = pd.read_csv(os.path.join(pathname, fn), decimal=",", sep=";")
            temp.drop(temp.tail(1).index, inplace=True)
            if "Güneş" in fn:
                csvgunes.append(temp)
            if "Maksimum" in fn:
                csvmaxsic.append(temp)
            if "Minimum" in fn:
                csvminsic.append(temp)
            if "Nispi" in fn:
                csvnem.append(temp)
            if "Rüzgar" in fn:
                csvruzgar.append(temp)
    print("append tamam")

    dfgunes = pd.concat(csvgunes)
    dfmaxsic = pd.concat(csvmaxsic)
    dfminsic = pd.concat(csvminsic)
    dfruzgar = pd.concat(csvruzgar)
    dfnem = pd.concat(csvnem)
    print("concat tamam")


    dfgunes["date"] = pd.to_datetime(dict(year=dfgunes["YIL"], month=dfgunes["AY"], day=dfgunes["GUN"]))
    print("date sütunu güneş tamam")
    dfmaxsic["date"] = pd.to_datetime(dict(year=dfmaxsic["YIL"], month=dfmaxsic["AY"], day=dfmaxsic["GUN"]))
    print("date sütunu maxsic tamam")
    dfminsic["date"] = pd.to_datetime(dict(year=dfminsic["YIL"], month=dfminsic["AY"], day=dfminsic["GUN"]))
    print("date sütunu minsic tamam")
    dfruzgar["date"] = pd.to_datetime(dict(year=dfruzgar["YIL"], month=dfruzgar["AY"], day=dfruzgar["GUN"]))
    print("date sütunu ruzgar tamam")
    dfnem["date"] = pd.to_datetime(dict(year=dfnem["YIL"], month=dfnem["AY"], day=dfnem["GUN"]))
    print("date sütunu nem tamam")

    dfgunes.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfmaxsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfminsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfruzgar.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    dfnem.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
    print("drop yıl ay gün tamam")

    tamam = dfgunes.merge(dfmaxsic, how="outer", on=["Istasyon_No", "date"])
    tamam = tamam.merge(dfminsic, how="outer", on=["Istasyon_No", "date"])
    tamam = tamam.merge(dfruzgar, how="outer", on=["Istasyon_No", "date"])
    tamam = tamam.merge(dfnem, how="outer", on=["Istasyon_No", "date"])
    print("merge tamam")

    print(len(tamam["Istasyon_No"].unique()), "adet istasyon birleştirildi.")
    return tamam


"""
kaydet = [dfgunes, dfmaxsic, dfminsic, dfruzgar, dfnem]
file = open('kaydet.pcl', 'wb')
pickle.dump(kaydet, file)
file.close()
# pd.__version__ #1.5.3
# python 3.9.13
# pickle.format_version 4.0
file = open('kaydet.pcl', 'rb')
banana = pickle.load(file)
"""