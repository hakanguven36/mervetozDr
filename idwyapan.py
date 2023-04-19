# import math
# import pandas as pd
import numpy as np

"""
def idw_yap(df, komsudf, pisim, komsusayisi, power):
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

import numpy as np
"""

def idw_yap(df, komsudf, pisim, komsusayisi, power):
    dr = df.copy()
    # komsurow dataframe'ini bir kez oluşturup kullanmak, döngü dışında tanımlanabilir
    komsurow_df = komsudf.set_index('istno')

    # apply fonksiyonu kullanarak döngüyü kaldırma
    def idw_func_apply(row):
        if not np.isnan(row[pisim]):
            return row[pisim]
        istno = row["istno"]
        date = row["date"]
        komsurow = komsurow_df.loc[istno].squeeze()

        # valArr ve mesArr yerine Pandas'ın query özelliği ile direkt seçim yapılabilir
        valArr = dr.query("istno in @komsurow[['k0', 'k1', 'k2', 'k3', 'k4']] and date == @date")[pisim]
        mesArr = komsurow[['m0', 'm1', 'm2', 'm3', 'm4']].values

        return IDW_Func(valArr, mesArr, power)

    dr[pisim] = dr.apply(idw_func_apply, axis=1)
    return dr

def IDW_Func(valArr, mesArr, power):
    n = len(valArr)
    pay = np.zeros(n)
    payda = np.zeros(n)
    for i in range(n):
        pay[i] = valArr[i] / np.power(mesArr[i], power)
        payda[i] = 1 / np.power(mesArr[i], power)
    return np.sum(pay) / np.sum(payda)