import os
import pickle as pcl
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

datasetpath = "D:/Business/Merve/kullanımda/"
if os.path.exists(datasetpath) == False:
    datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/"
    if os.path.exists(datasetpath) == False:
        print("dataset_path yerine uygun dosya yolunu yazınız.")
        quit()

file = open(os.path.join(datasetpath, "gsi_df.pcl"), "rb")
df = pd.DataFrame(pcl.load(file))
file.close()
file = open(os.path.join(datasetpath, "ist_df.pcl"), "rb")
ist_df = pd.DataFrame(pcl.load(file))
file.close()
del file

istasyonlar = df.groupby("istno").first().index
ist_df = ist_df.loc[ist_df["istno"].isin(istasyonlar)]
ist_df.reset_index(drop=True, inplace=True)

iller = [['17110','Çanakkale'],
['17112','Çanakkale'],
['17114','Balıkesir'],
['17145','Balıkesir'],
['17150','Balıkesir'],
['17175','Balıkesir'],
['17180','İzmir'],
['17184','Manisa'],
['17186','Manisa'],
['17220','İzmir'],
['17221','İzmir'],
['17232','Aydın'],
['17234','Aydın'],
['17290','Muğla'],
['17292','Muğla'],
['17294','Muğla'],
['17296','Muğla'],
['17297','Muğla'],
['17298','Muğla'],
['17375','Antalya'],
['17380','Antalya'],
['17674','Balıkesir'],
['17700','Balıkesir'],
['17742','İzmir'],
['17746','Manisa'],
['17789','İzmir'],
['17850','Aydın'],
['17854','İzmir'],
['17886','Muğla'],
['17892','Burdur'],
['17924','Muğla'],
['17926','Antalya'],
['17970','Antalya']]
iller = pd.DataFrame(iller, columns=["istno", "ilname"])
iller = iller.astype({"istno": "int64"})
df = df.merge(iller, on="istno")
df["year"] = df.date.dt.year
df["month"] = df.date.dt.month




### İstasyonlara göre gruplanmış
df_indisler_yillik_ort = df[["istno", "date","ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"  ]]
df_indisler_istort = df_indisler_yillik_ort.groupby("istno")["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].mean()
df_indisler_istort.reset_index(inplace=True, drop=True)
df_temp1 = ist_df
df_temp1[["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"]] =df_indisler_istort[["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"]]
df_temp1.to_csv("indisler istasyonlara göre.csv", sep=";", decimal=".", encoding="utf8")

### Yıllara göre gruplanmış
df_yillara_gore_grup = df[["istno", "date","ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"]]
df_yillara_gore_grup = df_yillara_gore_grup.groupby(df_yillara_gore_grup.date.dt.year)["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].mean()
df_yillara_gore_grup.to_csv("indisler yıllara göre.csv", sep=";", decimal=".", encoding="utf8")

### Pivot Table
for p in ["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"]:
    pivot = pd.pivot_table(df, columns=["ilname"], index=["year"], values=[p])
    pivot.to_csv("pivot" + p + ".csv", sep=";", decimal=".", encoding="utf8")

### İllere göre gruplanmış
df_indisler_illere_gore = df[["istno", "ilname", "date", "ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"]]
df_indisler_illere_gore = df_indisler_illere_gore.groupby("ilname")["ilname", "ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].mean()
df_indisler_illere_gore.to_csv("indisler illere göre.csv", sep=";", decimal=".", encoding="utf8")

### Grafikler için excel'e veri sağlıyorum
temp = df.groupby(["ilname", 'month'])["ilname", "month", "ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].mean()
temp.to_csv(os.path.join(datasetpath, "iller aylar.xlsx"), sep=";", decimal=".", encoding="utf8")

temp = df.groupby(["ilname", 'month'])["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].sum()
temp.to_csv(os.path.join(datasetpath, "iller aylar sum.csv"), sep=";", decimal=".", encoding="utf8")

temp = df.groupby(["ilname", 'month'])["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].sum().cumsum()
temp.to_csv(os.path.join(datasetpath, "iller aylar cumsum.csv"), sep=";", decimal=".", encoding="utf8")

temp = df.groupby(["ilname", 'year'])["ETo_FAO_mm", "i_Tmin", "i_rad", "i_etp", "i_foto", "GSI"].mean()
temp.to_csv(os.path.join(datasetpath, "iller yıllar mean.csv"), sep=";", decimal=".", encoding="utf8")




