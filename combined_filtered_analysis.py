
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
    off_moon_time_addition: float = 15,
):
    max_power = max(data["power"])

    power_threshold_min = max_power - threshold_value
    
    on_moon_power: pd.DataFrame = data.loc[data["power"]>=power_threshold_min]
    clusters = find_clusters(on_moon_power)
    on_moon_cluster_powers: list[pd.DataFrame] = []
    off_moon_cluster_powers: list[pd.DataFrame] = []
    for cluster in clusters:
        on_moon_start_time = cluster[0]
        on_moon_stop_time = cluster[-1]
        timeframe = on_moon_stop_time - on_moon_start_time
        off_moon_start_time = on_moon_stop_time + off_moon_time_addition
        off_moon_stop_time = off_moon_start_time + timeframe
        on_moon_cluster_power = data.loc[data["elapsed"]>=on_moon_start_time]
        on_moon_cluster_power = on_moon_cluster_power.loc[on_moon_cluster_power["elapsed"]<=on_moon_stop_time]
        average_on_moon_power = on_moon_cluster_power["power"].mean()
        print(f"the on moon average per cluster",average_on_moon_power)
        off_moon_cluster_power = data.loc[data["elapsed"]>=off_moon_start_time]
        off_moon_cluster_power = off_moon_cluster_power.loc[off_moon_cluster_power["elapsed"]<=off_moon_stop_time]
        average_off_moon_power = off_moon_cluster_power["power"].mean()
        print(f"the off moon average per cluster",average_off_moon_power)
        on_moon_cluster_powers.append(on_moon_cluster_power)
        off_moon_cluster_powers.append(off_moon_cluster_power)
       
    # print(on_moon_cluster_powers)
    # print(off_moon_cluster_powers)
    # on_moon_cluster_power_0 = on_moon_cluster_powers[0]
    # average_on_moon_power_0 = on_moon_cluster_power_0["power"].mean()
    # off_moon_cluster_power_0 = off_moon_cluster_powers[0]
    # average_off_moon_power_0 = off_moon_cluster_power_0["power"].mean()
    # print( f"{average_on_moon_power_0=}")
    # print( f"{average_off_moon_power_0=}")
    # comparison_0 = average_on_moon_power_0 - average_off_moon_power_0
    # print( f"{comparison_0=}")
    y_factors: list[float] = []
    y_factors_len: list[float] = []
    for index in range(len(on_moon_cluster_powers)):
        y_factor = on_moon_cluster_powers[index]["power"].mean() - off_moon_cluster_powers[index]["power"].mean()
        print( f"{index=} {y_factor=}")
        y_factors.append(y_factor)
        y_factors_len.append(index)
    



    fig,[ax_on_moon, ax_off_moon, ax_y_factor] = plt.subplots(3)
    ax_on_moon: plt.Axes
    ax_off_moon: plt.Axes
    ax_y_factor: plt.Axes
    #ax0.scatter(data["elapsed"],data["power"],color="#d9d1d0")
    ax_on_moon.plot(data["elapsed"],data["power"],color="#d9d1d0")
    
    # ax1.scatter(data["elapsed"],data["power"],color="#d9d1d0")
    ax_off_moon.plot(data["elapsed"],data["power"],color="#d9d1d0")
    
    ax_y_factor.scatter(y_factors_len,y_factors)
    ax_y_factor.plot(y_factors_len,y_factors)
    colors: list[str] = [
        "#d42c19",
        "#1529c2",
    ]

    for index in range (len(on_moon_cluster_powers)):
        color_index = index % len(colors)
        # ax_on_moon.scatter(on_moon_cluster_powers[index]["elapsed"],on_moon_cluster_powers[index]["power"],color=colors[color_index])
        ax_on_moon.plot(on_moon_cluster_powers[index]["elapsed"],on_moon_cluster_powers[index]["power"],color=colors[color_index],linewidth=4)
        # ax_off_moon.scatter(off_moon_cluster_powers[index]["elapsed"],off_moon_cluster_powers[index]["power"],color=colors[color_index])
        ax_off_moon.plot(off_moon_cluster_powers[index]["elapsed"],off_moon_cluster_powers[index]["power"],color=colors[color_index],linewidth=4)


    min_elapsed = min(on_moon_cluster_powers[0]["elapsed"]) - 50
    max_elapsed = max(off_moon_cluster_powers[-1]["elapsed"]) + 50
    ax_on_moon.set_xlim(min_elapsed,max_elapsed)
    ax_off_moon.set_xlim(min_elapsed,max_elapsed)



    plt.show()

y_factor_criteria(data=filtered_data, threshold_value=.03)
