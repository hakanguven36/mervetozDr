import numpy
import pandas as pd
import pickle as pcl
# python 3.9.13
# pd.__version__ #1.5.3
# pickle.format_version 4.0

# verileri çek
file = open('son.pcl', 'rb')
dfmulti = pd.DataFrame(pcl.load(file))

# multiindex => normal index
df = dfmulti.reset_index()

# dolu hücre sayıları
print(df.count())

# df[Istasyon_No] obj to int64
df["Istasyon_No"] = pd.to_numeric(df["Istasyon_No"])
print(df.dtypes)

# Seçilmiş istasyonları çek
dfsecilmisler = pd.read_csv("secilmisler.csv", sep="\t")

# kırmızıları at
dfsecilmislertemiz = pd.DataFrame(dfsecilmisler.loc[dfsecilmisler["durum"] != 0])

# dfsecilmislertemiz[istno] obj to int64
dfsecilmislertemiz["istno"] = pd.to_numeric(dfsecilmislertemiz["istno"])
print(dfsecilmislertemiz.dtypes)

# ana datasetten kırmızıları at
dftemiz = df.merge(dfsecilmislertemiz, how="right", on="Istasyon_No")

df.loc[df["Istasyon_No"] == 17926]
dftemiz.loc[dftemiz["date"].isnull()]




