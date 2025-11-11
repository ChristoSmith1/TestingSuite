import datetime
import math
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

import matplotlib.pyplot as plt

###EXAMPLE TO SHOW HOW TO GENERICALLY PLOT STUFF FOR SYNTAX PURPOSES###
# data = {'A': np.random.rand(10), 'B': np.random.rand(10)}
# df = pd.DataFrame(data)
# ax = df.plot(kind='line')
# ax.set_ylim([-3, 3]) # Set y-axis limits using Matplotlib
# plt.show()


pcovernodata = pd.read_csv(R"C:/Users/chris/OneDrive/Desktop/ANOMALY TRACK DATA OCTOBER 2025/DOY 100-304 parsed DTT logs/dcc.car.2025-288.csv")
df=pcovernodata
ax=df.plot(kind="line")
plt.show()