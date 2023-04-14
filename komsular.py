import math
import os
import pickle
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def KomsulariYaz(df):
    df = pd.DataFrame(df)
    for istno in df["istno"]:
        print(istno)

