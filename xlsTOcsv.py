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
