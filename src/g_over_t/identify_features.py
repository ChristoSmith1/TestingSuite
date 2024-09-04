"""
Identify features: On/off moon pairs and elevation columns
"""

from collections.abc import Sequence
import sys

from matplotlib import pyplot as plt
import pandas as pd

sys.path.insert(0, "./src")

from g_over_t.test_info import TestInfo, march_info, april_info, ElapsedInterval
from g_over_t.util.plots import grid_subplots, plot_all_test_info, HighlightInterval


def find_on_off(
    test_info: TestInfo,
    threshold_value: float = 0.05,
    off_moon_time_addition: float = 15,
):
    """Find on/off cluster pairs and inject that info into `test_info`."""
    plot_all_test_info(test_info)
    plt.show()
    pass


def _plot_elapsed_elevation(
    test_info: TestInfo, highlights: Sequence[ElapsedInterval] | None = None
):
    highlights = list(highlights or [])
    fig, [ax1, ax2] = grid_subplots(2)

    data = test_info.data
    colors = ["#ff0000", "#00ff00", "#0000ff"]
    if highlights:
        highlight_data_list: list[pd.DataFrame] = []

        for column in highlights:
            highlight_data = data[
                (data["elapsed"] >= column.start) & (data["elapsed"] <= column.end)
            ]
            if not highlight_data.empty:
                highlight_data_list.append(highlight_data)

    for ax in [ax1, ax2]:
        ax.plot(
            data["elapsed"],
            data["elevation"],
            color="#888888",
            linewidth=0.5,
        )
        for highlight_index, highlight_data in enumerate(highlight_data_list):
        # if highlight_data_combined is not None:
            ax.plot(
                highlight_data["elapsed"],
                highlight_data["elevation"],
                color=colors[highlight_index % len(colors)],
                linewidth=2.0,
                label=f"col[{highlight_index}]"
            )
        ax.legend()
        ax.set_xlabel("elapsed")
        ax.set_ylabel("elevation")
    ax1.set_title("START")
    ax1.set_title("END")
    plt.show(block=False)
    print("AFTER SHOW")
    input("Waiting")


def find_elevation_column_manually(test_info: TestInfo):
    highlights = [
        ElapsedInterval(500, 1000),
        ElapsedInterval(2000, 3000),
    ]
    _plot_elapsed_elevation(
        test_info,
        highlights=highlights,
    )
    pass


if __name__ == "__main__":
    find_elevation_column_manually(march_info)
