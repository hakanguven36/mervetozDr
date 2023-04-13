import os
import pandas as pd

def excelToCSVConverter(pathname):
    excelDosyaFileNameList = os.listdir(pathname)
    print("başladım")
    i = 1
    for filename in excelDosyaFileNameList:
        thafilename = os.path.splitext(filename)[1].lower()
        print(thafilename)
        if thafilename != ".xlsx":
            print(filename, "atlanıyor.")
            continue
        fullname = os.path.join(pathname, filename)
        csvname = os.path.join(pathname, os.path.splitext(filename)[0] + ".csv")
        dffromexcel = pd.read_excel(fullname, decimal=",")
        dffromexcel.to_csv(csvname, decimal=",", sep=";")
        print(filename, "tamamlandı")
        i += 1
    print("bitirdim")

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



def istasyonisimlerFromCSVs(pathname):
    dfs = []
    allfiles = os.listdir(pathname)
    for fn in allfiles:
        if os.path.splitext(fn)[1] == ".csv":
            tempdf = pd.read_csv(os.path.join(pathname, fn), sep=";", decimal=".")
            tempdf.drop(tempdf.tail(1).index, inplace=True)
            dfs.append(tempdf)

    tamam = pd.concat(dfs, join="inner", ignore_index=True)
    grp = tamam.groupby("Istasyon_No").first()["Istasyon_Adi"]
    grp = pd.DataFrame(grp)
    grp["istno"] = grp.index
    return grp






