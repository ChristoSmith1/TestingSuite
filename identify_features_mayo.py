"""
Identify features: On/off moon pairs and elevation columns
"""

import itertools
import random

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from combined_filtered_analysis import find_clusters
from util import simple_log
from util.plots import plot_all_test_info, HighlightInterval, save_figure
from test_info import OnOffMoonPair, TestInfo, all_tests, march_info, april_info, sept_info, sept_info2, ColumnInclusiveInterval


random.seed(40351)



# def find_on_off(
#     test_info: TestInfo,
#     threshold_value: float = 0.05,
#     off_moon_time_addition: float = 15,
# ):
#     """Find on/off cluster pairs and inject that info into `test_info`."""
#     plot_all_test_info(test_info)
#     plt.show()
#     pass


# def _plot_elapsed_elevation(
#     test_info: TestInfo, highlights: Sequence[ColumnInclusiveInterval] | None = None
# ):
#     highlights = list(highlights or [])
#     fig, [ax1, ax2] = grid_subplots(2)

#     data = test_info.data
#     colors = ["#ff0000", "#00ff00", "#0000ff"]
#     if highlights:
#         highlight_data_list: list[pd.DataFrame] = []

#         for column in highlights:
#             highlight_data = data[
#                 (data["elapsed"] >= column.start) & (data["elapsed"] <= column.end)
#             ]
#             if not highlight_data.empty:
#                 highlight_data_list.append(highlight_data)

#     for ax in [ax1, ax2]:
#         ax.plot(
#             data["elapsed"],
#             data["elevation"],
#             color="#888888",
#             linewidth=0.5,
#         )
#         for highlight_index, highlight_data in enumerate(highlight_data_list):
#         # if highlight_data_combined is not None:
#             ax.plot(
#                 highlight_data["elapsed"],
#                 highlight_data["elevation"],
#                 color=colors[highlight_index % len(colors)],
#                 linewidth=2.0,
#                 label=f"col[{highlight_index}]"
#             )
#         ax.legend()
#         ax.set_xlabel("elapsed")
#         ax.set_ylabel("elevation")
#     ax1.set_title("START")
#     ax1.set_title("END")
#     plt.show(block=False)
#     print("AFTER SHOW")
#     input("Waiting")


# def find_elevation_column_manually(test_info: TestInfo):
#     highlights = [
#         ColumnInclusiveInterval(500, 1000),
#         ColumnInclusiveInterval(2000, 3000),
#     ]
#     _plot_elapsed_elevation(
#         test_info,
#         highlights=highlights,
#     )
#     pass


def _find_clusters(
    data: pd.DataFrame,
    index_delta: int = 1,
) -> list[ColumnInclusiveInterval]:
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
            chunks.append(ColumnInclusiveInterval(chunk_start_elapsed, chunk_end_elapsed))
            previous_index = None
            chunk_start_index = None
            continue
        else:
            previous_index = index
    chunk_start_elapsed = data.loc[chunk_start_index]["elapsed"]
    chunk_end_elapsed = data.loc[previous_index]["elapsed"]
    chunks.append(ColumnInclusiveInterval(chunk_start_elapsed, chunk_end_elapsed)) 
    return chunks


def is_elevation_column(
    data: pd.DataFrame,
    interval: ColumnInclusiveInterval,
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


def _random_color():
    return "#" + "".join(random.choices("89abcdef", k=6))


random_colors = [_random_color() for _ in range(20)]

# TODO: Make this binary search
def _extend_column(
    data: pd.DataFrame,
    interval: ColumnInclusiveInterval,
) -> ColumnInclusiveInterval:
    print(f"Extending {interval} . . . ")
    earlier_elapsed = data[data["elapsed"] < interval.start]["elapsed"]
    for earlier in reversed(earlier_elapsed):
        candidate = ColumnInclusiveInterval(
            start=earlier,
            end=interval.end,
            name=interval.name,
        )
        # print(f"Checking {candidate}")
        if is_elevation_column(data=data, interval=candidate):
            interval = candidate
        else:
            break

    later_elapsed = data[data["elapsed"] > interval.end]["elapsed"]
    for later in later_elapsed:
        candidate = ColumnInclusiveInterval(
            start=interval.start,
            end=later,
            name=interval.name,
        )
        # print(f"Checking {candidate}")
        if is_elevation_column(data=data, interval=candidate):
            interval = candidate
        else:
            break

    return interval
    pass

def find_elevation_columns(
    test_info: TestInfo,
    *,
    save: bool = False,
) -> list[ColumnInclusiveInterval]:
    data = test_info.data.copy()

    print(data)
    print(f"{len(data) = }")
    print(f"{type(data) = }")

    # azimuth = np.array(data["azimuth"])
    # elevation = np.array(data["elevation"])

    low_elevation = data[data["elevation"] < 10]
    high_elevation = data[data["elevation"] > 85]
    print(f"{len(low_elevation) = }")
    print(f"{len(high_elevation) = }")
    high_clusters = _find_clusters(high_elevation)
    low_clusters = _find_clusters(low_elevation)
    print(f"{low_clusters = }")
    print(f"{high_clusters = }")

    low_cluster_ends = [x.end for x in low_clusters]
    high_cluster_starts = [x.start for x in high_clusters]


    identified_columns: list[ColumnInclusiveInterval] = []
    for low_end, high_end in itertools.product(low_cluster_ends, high_cluster_starts):
        # if high_end <= low_end:
        #     continue
        candidate_interval = ColumnInclusiveInterval(low_end, high_end)
        # print(f"{candidate_interval=}")
        if is_elevation_column(data, candidate_interval):
            print(f"IDENTIFIED ELEVATION COLUMN: {candidate_interval}")
            identified_columns.append(candidate_interval)
    
    # Identify and deal with overlapping columns
    filtered_columns: list[ColumnInclusiveInterval] = []
    while identified_columns:
        column = identified_columns.pop()

        overlapping_columns = [
            other
            for other
            in identified_columns
            if column.overlaps(other)
        ]
        simple_log.debug(f"checking {column}, which overlaps with {overlapping_columns}")

        for overlapping_column in overlapping_columns:
            identified_columns.remove(overlapping_column)
            column = column.strict_union(overlapping_column)


        filtered_columns.append(column)
        # break
        

    identified_columns = filtered_columns

    identified_columns = [
        _extend_column(data=data, interval=column)
        for column
        in identified_columns
    ]

    identified_columns.sort()

    highlights = []
    for index, col in enumerate(identified_columns):
        highlights.append(
            HighlightInterval(
                interval=col,
                # start = col.start,
                # end=col.end,
                color = random_colors[index % len(random_colors)],
                label=f"col[{index}]",
            )
        )

    

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

    fig, ax = plot_all_test_info(
        test_info,
        highlights=highlights,
        # show=True,
    )
    save_figure(
        fig=fig,
        test_info=test_info,
        relative_path=f"./columns.png"
    )
    # plot_all_test_info(
    #     test_info=test_info,
    #     show=True,
    # )

    # plt.plot(azimuth, elevation)
    # plt.show()

    test_info.analysis_results.elevation_columns = identified_columns
    if save:
        simple_log.info(f"Saving identified columns to {test_info.parameters_relative_path}")
        test_info.write_parameters()

    return identified_columns


def find_on_off_moon_pairs(
    test_info: TestInfo,
    *,
    threshold_value: float = 0.05,
    off_moon_time_addition: float = 15,
    save: bool = False,
) -> list[OnOffMoonPair]:
    # pairs = [
    #     OnOffMoonPair(
    #         on = ColumnInclusiveInterval(100, 200),
    #         off = ColumnInclusiveInterval(300, 400),
    #     ),
    #     OnOffMoonPair(
    #         on = ColumnInclusiveInterval(1100, 1200),
    #         off = ColumnInclusiveInterval(1300, 1400),
    #     )
    # ]
    pairs: list[OnOffMoonPair] = []


    data = test_info.data

    # Logic below copied from `combined_filtered_analysis.y_factor_criteria`
    max_power = max(data["power"])

    power_threshold_min = max_power - threshold_value
    
    on_moon_power: pd.DataFrame = data.loc[data["power"]>=power_threshold_min]
    clusters = find_clusters(on_moon_power)
    # on_moon_cluster_powers: list[pd.DataFrame] = []
    # off_moon_cluster_powers: list[pd.DataFrame] = []
    for cluster in clusters:
        on_moon_start_time = cluster[0]
        on_moon_stop_time = cluster[-1]

        on_moon = ColumnInclusiveInterval(start=on_moon_start_time, end=on_moon_stop_time)

        timeframe = on_moon_stop_time - on_moon_start_time
        off_moon_start_time = on_moon_stop_time + off_moon_time_addition
        off_moon_stop_time = off_moon_start_time + timeframe

        off_moon = ColumnInclusiveInterval(start=off_moon_start_time, end=off_moon_stop_time)

        pairs.append(OnOffMoonPair(on=on_moon, off=off_moon))
        # on_moon_cluster_power = data.loc[data["elapsed"]>=on_moon_start_time]
        # on_moon_cluster_power = on_moon_cluster_power.loc[on_moon_cluster_power["elapsed"]<=on_moon_stop_time]
        # average_on_moon_power = on_moon_cluster_power["power"].mean()
        # print(f"the on moon average per cluster",average_on_moon_power)
        # off_moon_cluster_power = data.loc[data["elapsed"]>=off_moon_start_time]
        # off_moon_cluster_power = off_moon_cluster_power.loc[off_moon_cluster_power["elapsed"]<=off_moon_stop_time]
        # average_off_moon_power = off_moon_cluster_power["power"].mean()
        # print(f"the off moon average per cluster",average_off_moon_power)
        # on_moon_cluster_powers.append(on_moon_cluster_power)
        # off_moon_cluster_powers.append(off_moon_cluster_power)




    # pairs = []
    pairs.sort()

    highlights = []

    for index, pair in enumerate(pairs):
        # label = f"on_off_{index}"
        highlight_on = HighlightInterval(
            interval=pair.on,
            color = random_colors[index % len(random_colors)],
            label=f"on[{index}]",
        )
        highlight_off = HighlightInterval(
            interval=pair.off,
            color = random_colors[index % len(random_colors)],
            label=f"off[{index}]",
        )
        highlights.append(highlight_on)
        highlights.append(highlight_off)

    fig, ax = plot_all_test_info(test_info=test_info, highlights=highlights)
    save_figure(
        fig=fig,
        test_info=test_info,
        relative_path=f"./pairs.png"
    )

    test_info.analysis_results.on_off_moon_pairs = pairs

    if save:
        simple_log.info(f"Saving pairs to {test_info.parameters_relative_path}")
        test_info.write_parameters()

    return pairs


if __name__ == "__main__":
    simple_log.set_level("DEBUG")
    import time
    test_infos = list(all_tests())

    for test_info in test_infos:
        _ = test_info.data

    for test_info in test_infos:
        start = time.monotonic()
        find_on_off_moon_pairs(
            test_info,
            save=True,
        )
        find_elevation_columns(
            test_info,
            save=True,
        )
        end = time.monotonic()
        print(f"Took {end - start} seconds.")
        # find_elevation_columns(sept_info)
        # find_elevation_columns(march_info)
        # find_elevation_columns(april_info)
        print(sept_info2.analysis_results.elevation_columns)