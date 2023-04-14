import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize = (8,7))
ax.scatter(df_gunes_komsu.coordy, df_gunes_komsu.coordx, zorder=1, alpha=0.2, c="b", s=10)
plt.show()

