
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

def find_clusters(
    on_moon_power: pd.DataFrame,
    cluster_time_threshold = 2,    
) -> list[list[float]]:
    """creates clusters of times that are close to each other

    Args:
        on_moon_power (pd.DataFrame): _description_
        cluster_time_threshold (int, optional): _description_. Defaults to 2.

    Returns:
        list[list[float]]: _description_
    """
    clusters = []
    elapsed_times = list(on_moon_power["elapsed"])
    cluster = []
    while elapsed_times:
        first_item = elapsed_times.pop(0)
        if not cluster:
            cluster.append(first_item)
        else:
            smallest_cluster_value = cluster[0]
            largest_cluster_value = cluster[-1]
            if (
                first_item >= smallest_cluster_value - cluster_time_threshold
                and first_item <= largest_cluster_value + cluster_time_threshold
            ):
                cluster.append(first_item)
            else:
                print("found a cluster")
                print(cluster[0])
                print(cluster[-1])
                clusters.append(cluster)
                cluster = []
                cluster.append(first_item)
                
            pass

    if cluster:
        print("found a cluster")
        print(cluster[0])
        print(cluster[-1])
        clusters.append(cluster)

    return clusters


def y_factor_criteria(
    data: pd.DataFrame,
    threshold_value: float = 0.05,
    off_moon_time_additon = 2
):
    max_power = max(data["power"])

    power_threshold_min = max_power - threshold_value
    
    on_moon_power: pd.DataFrame = data.loc[data["power"]>=power_threshold_min]
    clusters = find_clusters(on_moon_power)
    for cluster in clusters:
        on_moon_start_time = cluster[0]
        on_moon_stop_time = cluster[-1]
        timeframe = on_moon_stop_time - on_moon_start_time
        off_moon_start_time = on_moon_stop_time + off_moon_time_additon
        off_moon_stop_time = off_moon_start_time + timeframe
        on_moon_cluster_power = data.loc[data["elapsed"]>=on_moon_start_time]
        on_moon_cluster_power = on_moon_cluster_power.loc[on_moon_cluster_power["elapsed"]<=on_moon_stop_time]
        average_on_moon_power = on_moon_cluster_power["power"].mean()
        print(f"the on moon average per cluster",average_on_moon_power)
        off_moon_cluster_power = data.loc[data["elapsed"]>=off_moon_start_time]
        off_moon_cluster_power = off_moon_cluster_power.loc[off_moon_cluster_power["elapsed"]<=off_moon_stop_time]
        average_off_moon_power = off_moon_cluster_power["power"].mean()
        print(f"the off moon average per cluster",average_off_moon_power)

        pass

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
