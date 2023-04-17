import math
import os
import pickle
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def KomsulariYaz(gelendf, komsusayisi):
    islemno = 0

    dr = gelendf.copy()
    for index, row in dr.iterrows():
        komsulartemp = mesafe(row, dr, komsusayisi)
        komsulartemp.reset_index(inplace=True, drop=True)
        for i , r in komsulartemp.iterrows():
            dr.loc[index,"k"+str(i+1)] = r["istno"]
            dr.loc[index,"m"+str(i+1)] = r["mesafe"]
        print("islemno", islemno)
        islemno += 1
    return dr


 # ddd = mesafe( df_gunes_komsu.iloc[0] ,df_gunes_komsu, 5)

def mesafe(gelen, noktalar, komsusayisi):
    x = gelen.coordx
    y = gelen.coordy
    t = pd.DataFrame(columns=["istno", "mesafe"])
    for i in range(len(noktalar)):
        mesafe = math.sqrt(math.pow(noktalar.loc[i,"coordx"] - x, 2) + math.pow(noktalar.loc[i,"coordy"] - y, 2))
        t = t.append(dict({"istno":noktalar.loc[i,"istno"], "mesafe":mesafe }), ignore_index=True)
    t = t.sort_values(by=["mesafe"])
    t.reset_index(inplace=True, drop=True)

    return t.iloc[1:komsusayisi+1]


# deneme = KomsulariYaz(df_gunes_komsu, 7)