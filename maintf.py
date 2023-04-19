import os.path
import pickle as pcl
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import seaborn as sns


datasetpath = "C:/Users/oguzfehmi.sen.TARIM/Desktop/veriler/" # İşte

filename = open(os.path.join(datasetpath, "dfgunes.pcl"), "rb")
df = pd.DataFrame(pcl.load(filename))
filename.close()
file_ist = open(os.path.join(datasetpath, "file_ist.pcl"), "rb")
istdf = pd.DataFrame(pcl.load(file_ist))
file_ist.close()
del(filename, file_ist)
print("Dosyalar başarıyla içeri aktarıldı.")

df = df.merge(istdf[["istno", "coordx","coordy"]], how="left", on='istno')
df.drop(columns=["date", "istno"], inplace=True)
dfdolu = df.loc[df["gunes"].notnull()]
dftahminlenecek = df.loc[df["gunes"].isnull()]


