
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

# fig,ax = plt.subplots()
# ax: plt.Axes
# ax.plot(filtered_data["timestamp_posix"],filtered_data["power"])
# plt.show()

def find_clusters(
    on_moon_power: pd.DataFrame
        
):
    elapsed_times = list(on_moon_power["elapsed"])
    cluster = []
    while elapsed_times:
        first_item = elapsed_times.pop(0)
        if not cluster:
            cluster.append(first_item)
        # if #elapsed times are in close proximity
        #     #pass it to a "cluster"
        # else # look at next time
        #     #repeat process
        pass

def y_factor_criteria(
    data: pd.DataFrame,
    threshold_value: float = 0.05
):
    max_power = max(data["power"])

    power_threshold_min = max_power - threshold_value
    
    on_moon_power: pd.DataFrame = data.loc[data["power"]>=power_threshold_min]


    
    fig,[ax0, ax1] = plt.subplots(2)
    ax0: plt.Axes
    ax1: plt.Axes
    ax0.scatter(on_moon_power["elapsed"],on_moon_power["power"])
    ax0.plot(on_moon_power["elapsed"],on_moon_power["power"])

    min_elapsed = min(data["elapsed"])
    max_elapsed = max(data["elapsed"])
    ax0.set_xlim(min_elapsed,max_elapsed)


    plt.show()

y_factor_criteria(data=filtered_data, threshold_value=.03)
