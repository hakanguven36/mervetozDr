import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

"""Bu fonksiyonda istenen DF içinde 'istno', 'coordx', 'coordy' olmalı"""
"""Talep edilen komşu sayısınca k1,m1,k2,m2... şeklinde komşuyu ve mesafeyi ayrı bir tabloya ekleyip döndürür."""
"""mesafe fonksiyonuna bağımlıdır."""

def komsulari_yaz(gelendf, komsu_sayisi):
    islemno = 0
    dr = pd.DataFrame(gelendf.copy())
    for index, row in dr.iterrows():
        komsulartemp = mesafe(row, dr, komsu_sayisi)
        komsulartemp.reset_index(inplace=True, drop=True)
        for i , r in komsulartemp.iterrows():
            dr.loc[index,"k"+str(i)] = r["istno"]
            dr.loc[index,"m"+str(i)] = r["mesafe"] * 111    # lat-long * 111 = KM
        print("islemno", islemno)
        islemno += 1
    return dr

def mesafe(gelen, noktalar, komsu_sayisi):
    x = gelen.coordx
    y = gelen.coordy
    t = pd.DataFrame(columns=["istno", "mesafe"])
    for i in range(len(noktalar)):
        mesafe = ((noktalar.loc[i,"coordx"] - x) ** 2 + (noktalar.loc[i,"coordy"] - y) ** 2) ** 0.5
        t = t.append(dict({"istno":noktalar.loc[i,"istno"], "mesafe":mesafe }), ignore_index=True)
    t = t.sort_values(by=["mesafe"])
    t.reset_index(inplace=True, drop=True)
    return t.iloc[1:komsu_sayisi+1]


