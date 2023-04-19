import pandas as pd
# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)

"""Bu fonksiyonda istenen DF içinde 'istno', 'coordx', 'coordy' olmalı"""
"""Talep edilen komşu sayısınca k1,m1,k2,m2... şeklinde komşuyu ve mesafeyi ayrı bir tabloya ekleyip döndürür."""
"""mesafe fonksiyonuna bağımlıdır."""
"""
def KomsulariYaz(gelendf, komsusayisi):
    islemno = 0

    dr = pd.DataFrame(gelendf.copy())
    for index, row in dr.iterrows():
        komsulartemp = mesafe(row, dr, komsusayisi)
        komsulartemp.reset_index(inplace=True, drop=True)
        for i , r in komsulartemp.iterrows():
            dr.loc[index,"k"+str(i)] = r["istno"]
            dr.loc[index,"m"+str(i)] = r["mesafe"] * 111 # lat-long * 111 = KM
        print("islemno", islemno)
        islemno += 1
    return dr

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
"""

def komsulari_yaz(gelendf, komsusayisi):
    dr = pd.DataFrame(gelendf.copy())
    komsu_cols = [f'k{i}' for i in range(komsusayisi)]
    mesafe_cols = [f'm{i}' for i in range(komsusayisi)]
    dr[komsu_cols] = pd.DataFrame(dr.apply(lambda x: mesafe(x, dr, komsusayisi), axis=1).tolist(), index=dr.index)
    dr[mesafe_cols] = dr[komsu_cols].apply(lambda x: x['mesafe']*111)
    return dr[komsu_cols+mesafe_cols]

def mesafe(gelen, noktalar, komsusayisi):
    x = gelen.coordx
    y = gelen.coordy
    mesafeler = ((noktalar.coordx - x) ** 2 + (noktalar.coordy - y) ** 2) ** 0.5
    t = pd.DataFrame({'istno': noktalar.istno, 'mesafe': mesafeler})
    t = t.sort_values(by='mesafe')
    return t.iloc[1:komsusayisi+1]
