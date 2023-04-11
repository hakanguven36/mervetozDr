import datetime
import os
import pickle

import pandas as pd

"""
hamdosyalar = os.listdir("rawrar")
for hamdosya in hamdosyalar:
    kokname, extname = os.path.splitext(hamdosya)
    if extname == ".xlsx":
        temp = pd.read_excel(os.path.join("rawrar", hamdosya), decimal=".")
        temp.to_csv(os.path.join("csvfiles", kokname + ".csv"), decimal=".", sep=";", encoding="utf8")
        print(kokname)
"""

csvgunes = []
csvruzgar = []
csvminsic = []
csvmaxsic = []
csvnem = []
csvfilenames = os.listdir("csvfiles")

for fn in csvfilenames:
    temp = pd.read_csv(os.path.join("csvfiles", fn), decimal=".", sep=";")
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

dfgunes = pd.concat(csvgunes)
dfmaxsic = pd.concat(csvmaxsic)
dfminsic = pd.concat(csvminsic)
dfruzgar = pd.concat(csvruzgar)
dfnem = pd.concat(csvnem)

dfgunes["date"] = pd.to_datetime(dict(year = dfgunes["YIL"], month = dfgunes["AY"], day = dfgunes["GUN"]))
dfmaxsic["date"] = pd.to_datetime(dict(year = dfmaxsic["YIL"], month = dfmaxsic["AY"], day = dfmaxsic["GUN"]))
dfminsic["date"] = pd.to_datetime(dict(year = dfminsic["YIL"], month = dfminsic["AY"], day = dfminsic["GUN"]))
dfruzgar["date"] = pd.to_datetime(dict(year = dfruzgar["YIL"], month = dfruzgar["AY"], day = dfruzgar["GUN"]))
dfnem["date"] = pd.to_datetime(dict(year = dfnem["YIL"], month = dfnem["AY"], day = dfnem["GUN"]))

dfgunes.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
dfmaxsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
dfminsic.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
dfruzgar.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)
dfnem.drop(columns=["Unnamed: 0", "YIL", "AY", "GUN", "Istasyon_Adi"], inplace=True)

tamam = dfgunes.merge(dfmaxsic, how="outer", on=["Istasyon_No", "date"])
tamam = tamam.merge(dfminsic, how="outer", on=["Istasyon_No", "date"])
tamam = tamam.merge(dfruzgar, how="outer", on=["Istasyon_No", "date"])
tamam = tamam.merge(dfnem, how="outer", on=["Istasyon_No", "date"])

len(tamam["Istasyon_No"].unique())

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
istsay 140 (Güneş)
istsay 201 (MaxSıc)
istsay 190 (MinSıc)
istsay 188 (Rüzgar)
istsay 204 (Nem)
"""