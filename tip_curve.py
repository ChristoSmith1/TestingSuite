"""
This is the Tip Curve Function
It's inputs are dataFrames from power collection and the calculated averaged Y-factor
It outputs a graph of the tip curve showing t_sys at elevations
"""

import matplotlib.pyplot as plt
from test_info import march_info, april_info, sept_info, sept_info2, TestInfo
from util.plots import (
    plot_all_test_info,
    HighlightInterval,
    save_figure,
    plot_one,
    plot_all,
)
import numpy as np
import numpy.typing as npt



def tip_curve(info: TestInfo)-> tuple[npt.NDArray[float], npt.NDArray[float]]: # type: ignore
    data = info.elevation_column_data_list[0]
    data = data.sort_values("elevation")
    y_factor = info.y_factor()
    elevation = np.array(data["elevation"])
    print(f"{y_factor=}")
    t_op = abs(180 - ((10 ** (y_factor / 10)) * 2.75)) / ((10 ** (y_factor / 10)) - 1)
    # Top=abs((135-(10**(Yfactor/10))*10)/(10**(Yfactor/10)-1)) <- 135 moon contribution at S-Band, 180 at X-band

    # I need to get just the elevation column from sept_info which right now gets everything.
    # T_op = (135-((10**(Y-factor/10))*10))/((10**(Y-factor/10))-1) <- correct math!
    t_el = t_op*10**((np.array(data["power"]) - info.average_off_moon())/10) 
    plt.plot(elevation,t_el)
    # smoothed = np.convolve(t_el, np.ones(1000) /1000, mode="valid")
    # plt.plot(elevation[ : 14000], smoothed[ : 14000])
    from scipy.ndimage import uniform_filter1d
    N = 350
    y = uniform_filter1d(t_el, size = N)
    plt.ylabel("Temperature (K)")
    plt.xlabel("Elevation")
    plt.title(info.description)
    plt.plot(elevation, y)
    print(t_op)
    plt.show()
    return elevation, t_el

if __name__ == "__main__":
    info = march_info
    elevation_columns = info.analysis_results.elevation_columns
    highlights = []
    for elevation_column in elevation_columns:
        pass
        highlight = HighlightInterval(
            elevation_column, label="elevation column", color="#000fff", linewidth=4
        )
        highlights.append(highlight)

    # fig,axes = plot_all_test_info(info,highlights=highlights,interval=info.analysis_results.elevation_column_interval())
    # save_figure(fig=fig,test_info=info,relative_path="./christo.png")

    fig, axes = plot_one(
        info.data,
        # highlights=highlights,
        # interval=info.analysis_results.elevation_columns[3],
        x_column_name="elapsed",
        y_column_name="power",
    )
    # x = np.array(
    #     info.analysis_results.elevation_columns[3].subset_data_frame(info.data)["power"]
    # )
    data = info.elevation_column_data_list[0]
    y = np.array(data["power"])
    x = np.array(data["elapsed"])
    axes.plot(x, y, color = "red")
    # save_figure(fig=fig, test_info=info, relative_path="elevationcolumntest.png")
    # axes.set_xlabel("elapsed time")
    # axes.set_ylabel("power (in dB)")
    # axes.set_title("power over time for April X-band test")
    plt.show()
    # exit()

    # import YFactor and use info to generate average Y-factor from multiple on/off measurements
    tip_curve(sept_info)
