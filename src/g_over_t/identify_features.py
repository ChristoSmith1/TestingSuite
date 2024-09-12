"""
Identify features: On/off moon pairs and elevation columns
"""

from collections.abc import Sequence
import itertools
import random
import sys
from typing import Iterable

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "./src")

from g_over_t.test_info import TestInfo, march_info, april_info, sept_info, sept_info2, ElapsedInterval
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


def _find_clusters(
    data: pd.DataFrame,
    index_delta: int = 1,
) -> list[ElapsedInterval]:
    indexes: list[int] = list(data.index)
    chunks = []
    chunk_start_index: int | None = None
    previous_index: int | None = None
    for index in indexes:
        if chunk_start_index is None:
            chunk_start_index = index
        if previous_index is None:
            previous_index = index
        if index > previous_index + index_delta:
            chunk_start_elapsed = data.loc[chunk_start_index]["elapsed"]
            chunk_end_elapsed = data.loc[previous_index]["elapsed"]
            chunks.append(ElapsedInterval(chunk_start_elapsed, chunk_end_elapsed))
            previous_index = None
            chunk_start_index = None
            continue
        else:
            previous_index = index
    chunk_start_elapsed = data.loc[chunk_start_index]["elapsed"]
    chunk_end_elapsed = data.loc[previous_index]["elapsed"]
    chunks.append(ElapsedInterval(chunk_start_elapsed, chunk_end_elapsed)) 
    return chunks


def is_elevation_column(
    data: pd.DataFrame,
    interval: ElapsedInterval,
    *,
    start_max_elevation: float = 10.0,
    end_min_elevation: float = 85.0,
    max_width_deg = 0.1,
    min_height_deg = 75.0,
    min_data_points = 100,
) -> bool:
    column_data = data[
        (data["elapsed"] >= interval.start)
        & (data["elapsed"] <= interval.end)
    ]
    if column_data.empty:
        return False
    
    if len(column_data) < min_data_points:
        return False
    
    azimuths = np.array(column_data["azimuth"])
    elevations = np.array(column_data["elevation"])

    if elevations[0] > start_max_elevation:
        return False
    if elevations[-1] < end_min_elevation:
        return False

    if max(azimuths) - min(azimuths) > max_width_deg:
        return False
    if max(elevations) - min(elevations) < min_height_deg:
        return False
    return True


random.seed(40351)

def _random_color():
    return "#" + "".join(random.choices("89abcdef", k=6))


random_colors = [_random_color() for _ in range(20)]

# TODO: Make this binary search
def _extend_column(
    data: pd.DataFrame,
    interval: ElapsedInterval,
) -> ElapsedInterval:
    print(f"Extending {interval} . . . ")
    earlier_elapsed = data[data["elapsed"] < interval.start]["elapsed"]
    for earlier in reversed(earlier_elapsed):
        candidate = ElapsedInterval(
            start=earlier,
            end=interval.end,
            column=interval.column,
        )
        # print(f"Checking {candidate}")
        if is_elevation_column(data=data, interval=candidate):
            interval = candidate
        else:
            break

    later_elapsed = data[data["elapsed"] > interval.end]["elapsed"]
    for later in later_elapsed:
        candidate = ElapsedInterval(
            start=interval.start,
            end=later,
            column=interval.column,
        )
        # print(f"Checking {candidate}")
        if is_elevation_column(data=data, interval=candidate):
            interval = candidate
        else:
            break

    return interval
    pass

def find_elevation_columns(test_info: TestInfo):
    data = test_info.data.copy()

    print(data)
    print(f"{len(data) = }")
    print(f"{type(data) = }")

    # azimuth = np.array(data["azimuth"])
    # elevation = np.array(data["elevation"])

    low_elevation = data[data["elevation"] < 10]
    high_elevation = data[data["elevation"] > 85]
    high_elevation.to_csv("./high.csv")
    print(f"{len(low_elevation) = }")
    print(f"{len(high_elevation) = }")
    high_clusters = _find_clusters(high_elevation)
    low_clusters = _find_clusters(low_elevation)
    print(f"{low_clusters = }")
    print(f"{high_clusters = }")

    low_cluster_ends = [x.end for x in low_clusters]
    high_cluster_starts = [x.start for x in high_clusters]


    identified_columns: list[ElapsedInterval] = []
    for low_end, high_end in itertools.product(low_cluster_ends, high_cluster_starts):
        # if high_end <= low_end:
        #     continue
        candidate_interval = ElapsedInterval(low_end, high_end)
        # print(f"{candidate_interval=}")
        if is_elevation_column(data, candidate_interval):
            print(f"IDENTIFIED ELEVATION COLUMN: {candidate_interval}")
            identified_columns.append(candidate_interval)
    
    # Identify and deal with overlapping columns
    filtered_columns: list[ElapsedInterval] = []
    while identified_columns:
        column = identified_columns.pop()

        overlapping_columns = [
            other
            for other
            in identified_columns
            if column.overlaps(other)
        ]
        print(f"DEBUG: checking {column}, which overlaps with {overlapping_columns}")

        for overlapping_column in overlapping_columns:
            identified_columns.remove(overlapping_column)
            column = column.union(overlapping_column)


        filtered_columns.append(column)
        # break
        

    identified_columns = filtered_columns

    identified_columns = [
        _extend_column(data=data, interval=column)
        for column
        in identified_columns
    ]

    highlights = []
    for index, col in enumerate(identified_columns):
        highlights.append(HighlightInterval(
            start = col.start,
            end=col.end,
            color = random_colors[index % len(random_colors)],
            label=f"col[{index}]",
            column_name="elapsed",
        ))

    

    # highlights.extend([
    #     HighlightInterval(
    #         column_name="elapsed",
    #         start=cluster.start,
    #         end=cluster.end,
    #         color="#ff0000",
    #         label="high"
    #     )
    #     for cluster
    #     in high_clusters
    # ])

    # highlights.extend([
    #     HighlightInterval(
    #         column_name="elapsed",
    #         start=cluster.start,
    #         end=cluster.end,
    #         color="#00ff00",
    #         label="low"
    #     )
    #     for cluster
    #     in low_clusters
    # ])

    plot_all_test_info(
        test_info,
        highlights=highlights,
        # show=True,
    )
    # plot_all_test_info(
    #     test_info=test_info,
    #     show=True,
    # )

    # plt.plot(azimuth, elevation)
    # plt.show()


if __name__ == "__main__":
    import time
    start = time.monotonic()
    find_elevation_columns(sept_info2)
    end = time.monotonic()
    print(f"Took {end - start} seconds.")
    # find_elevation_columns(sept_info)
    # find_elevation_columns(march_info)
    # find_elevation_columns(april_info)
