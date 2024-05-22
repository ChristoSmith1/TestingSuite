
"""
Script written to analyze and manipulate combined data only 05-22-2024

"""
import datetime
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D

import g_over_t

from scipy.interpolate import BSpline
from scipy.interpolate import make_interp_spline

import pandas as pd

FILTERED_COMBINED_DATA_PATH = R"april21govert\combined_filtered_XBand_April.csv"

filtered_data = pd.read_csv(FILTERED_COMBINED_DATA_PATH)

timemin = min(filtered_data["timestamp_posix"])
filtered_data["elapsed"] = filtered_data["timestamp_posix"] - timemin

print(filtered_data)
print(filtered_data.dtypes)

fig,ax = plt.subplots()
ax: plt.Axes
ax.plot(filtered_data["timestamp_posix"],filtered_data["power"])
plt.show()

def y_factor_criteria(
    data: pd.DataFrame,
    threshold_value: float = 0.05
):
    max_power = max(data["power"])
    min_power = min(data["power"])
    power_threshold_min = max_power - threshold_value
    power_threshold_max = min_power + threshold_value
    y_factor_max = data.loc[data["power"]>=power_threshold_min]
    y_factor_min = data.loc[data["power"]<=power_threshold_max]
    fig,[ax0, ax1] = plt.subplots(2)
    ax0: plt.Axes
    ax1: plt.Axes
    ax0.scatter(y_factor_max["elapsed"],y_factor_max["power"])
    ax0.plot(y_factor_max["elapsed"],y_factor_max["power"])
    ax1.scatter(y_factor_min["elapsed"],y_factor_min["power"])
    ax1.plot(y_factor_min["elapsed"],y_factor_min["power"])

    min_elapsed = min(data["elapsed"])
    max_elapsed = max(data["elapsed"])
    ax0.set_xlim(min_elapsed,max_elapsed)
    ax1.set_xlim(min_elapsed,max_elapsed)

    plt.show()

y_factor_criteria(data=filtered_data, threshold_value=.03)
