import math
import os
import pickle
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

noktalar = pd.read_csv("noktalar.csv", sep=";", decimal=".", encoding="utf8")

islemsayar = 0
def mesafe(gelen):
    global islemsayar
    islemsayar += 1
    print(islemsayar)

    x = gelen.lat
    y = gelen.lon
    t = pd.DataFrame(columns=["istno", "mesafe"])
    for i in range(len(noktalar)):
        mesafe = math.sqrt(math.pow(noktalar.loc[i,"lat"] - x, 2) + math.pow(noktalar.loc[i,"lon"] - y, 2))
        t = t.append(dict({"myNo": gelen.istno,"istno":noktalar.loc[i,"istno"], "mesafe":mesafe }), ignore_index=True)
    t = t.sort_values(by=["mesafe"])
    t.reset_index(inplace=True, drop=True)

    return t.loc[1,"myNo"].astype(str) + ";" +\
    t.loc[1,"istno"].astype(str) + ";" + t.loc[1,"mesafe"].astype(str)+ ";" +\
    t.loc[2,"istno"].astype(str) + ";" + t.loc[2,"mesafe"].astype(str) + ";" +\
    t.loc[3, "istno"].astype(str) + ";" + t.loc[3, "mesafe"].astype(str) + ";" +\
    t.loc[4, "istno"].astype(str) + ";" + t.loc[4, "mesafe"].astype(str)+ ";" +\
    t.loc[5, "istno"].astype(str) + ";" + t.loc[5, "mesafe"].astype(str)


tamam = noktalar.apply(mesafe, axis=1)
tamam.to_csv("mesafeler.csv", decimal=".", sep="\t")

deneme = mesafe(noktalar.iloc[0])


deneme = pd.DataFrame({"ID":[1,2,3,4,5], "numbers":[7,12,5,1,99]})
denemesort = deneme.sort_values(by="numbers")
deneme.reset_index()