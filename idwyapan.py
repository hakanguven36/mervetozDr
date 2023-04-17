import math
import numpy
import pandas as pd

def IDWyap(df, komsudf, pisim, komsusayisi, power):
    dr = df.copy()
    for index, row in dr.iterrows():
        if numpy.isnan(row[pisim]):
            istno = row["istno"]
            date = row["date"]
            komsurow = komsudf.loc[komsudf["istno"] == istno].squeeze()
            # bu rowdaki istno için komsuları aldım
            # her bir komsunun aynı date'teki değerlerini ve mesafelerini çekelim. Bunları Array'lere atalım
            valArr = []
            mesArr = []
            for i in range(komsusayisi):
                k_istno = komsurow["k"+str(i)]
                deger = dr.loc[(dr["istno"] == k_istno) & (dr["date"] == date)][pisim].squeeze()
                if numpy.isnan(deger):
                    continue
                valArr.append(deger)
                k_mesafe = komsurow["m" + str(i)]
                mesArr.append(k_mesafe)
            # IDW_Func uygulayalım ve boş yere ekleyelim
            dr.loc[index,pisim] = IDW_Func(valArr, mesArr, power)
        print("işlem yapıldı", str(index))
    return dr

def IDW_Func(valArr, mesArr, power):
    pay = 0
    payda = 0
    for i in range(len(valArr)):
        pay += valArr[i]/ math.pow(mesArr[i], power)
        payda += 1/math.pow(mesArr[i], power)
    return pay/payda


