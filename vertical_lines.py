import enum
import itertools
import math
from pathlib import Path
from collections import Counter

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


# path = Path(R"april21govert/combined_filtered_XBand_April.csv").expanduser().resolve()
path = Path(R"april21govert/combined_filtered_SBand_March.csv").expanduser().resolve()

data = pd.read_csv(path)
min_timestamp = min(data["timestamp_posix"])
data["elapsed"] = data["timestamp_posix"] - min_timestamp

print(data)
print(data.dtypes)

azimuths = data["azimuth"].to_numpy()
elevations = data["elevation"].to_numpy()



def is_vertical(x0: float, y0: float, x1: float, y1: float, tolerance_deg: float = 1.0) -> bool:
    degrees = math.degrees(math.atan2((y1 - y0), (x1 - x0)))
    degrees %= 180.0
    return (90.0 - tolerance_deg <= degrees <= 90.0 + tolerance_deg)


class Status(enum.Enum):
    UNKNOWN = enum.auto()
    ON_LINE = enum.auto()
    NOT_ON_LINE = enum.auto()

index_statuses = [
    Status.UNKNOWN
    for index
    in range(len(azimuths))
]

# FIND A VERTICAL SEGMENT, IF ONE EXISTS
# NOT GUARANTEED TO BE LONGEST
def find_a_vertical_segment(left_index: int, right_index: int) -> tuple[int, int] | None:
    print(f"Checking {left_index=} to {right_index=}")
    # 0 length line, by definition not vertical
    if left_index == right_index:
        return
    
    if is_vertical(
        x0 = azimuths[left_index],
        x1 = azimuths[right_index],
        y0 = elevations[left_index],
        y1 = elevations[right_index],
    ):
        for index in range(left_index, right_index+1):
            index_statuses[index] = Status.ON_LINE
        return (left_index, right_index)
    elif right_index - left_index < 2:
        return
    
    midpoint_index = (left_index + right_index) // 2
    print(f"  Checking LOWER")
    lower_segment = find_a_vertical_segment(left_index, midpoint_index)
    if lower_segment:
        return lower_segment
    print(f"  Checking UPPER")
    upper_segment = find_a_vertical_segment(midpoint_index, right_index)
    if upper_segment:
        return upper_segment
    
def find_an_unknown_run() -> tuple[int, int]:
    start_index = index_statuses.index(Status.UNKNOWN)
    index = start_index
    while index < len(index_statuses) and index_statuses[index] == Status.UNKNOWN:
        index += 1
    print(f"ABout to return {(start_index, index - 1) !r}")
    return (start_index, index - 1)

def find_all_vertical_segments():
    found_segments = []
    undetermined_index_count = sum((
        1
        for index
        in range(len(azimuths))
        if index_statuses[index] == Status.UNKNOWN
    ))
    while undetermined_index_count:
        left_index, right_index = find_an_unknown_run()
        print(f"{left_index=} {right_index=} {Counter(index_statuses)}")
        segment = find_a_vertical_segment(left_index, right_index)
        if segment:
            found_segments.append(segment)
            for index in range(left_index, right_index+1):
                index_statuses[index] = Status.NOT_ON_LINE
        else:
            for index in range(left_index, right_index+1):
                index_statuses[index] = Status.NOT_ON_LINE
        undetermined_index_count = sum((1 for index in range(len(azimuths)) if index_statuses[index] == Status.UNKNOWN))
    return found_segments


vertical_indexes = find_a_vertical_segment(left_index=0, right_index=len(azimuths)-1)
for index in range(vertical_indexes[0], vertical_indexes[0] + 1):
    index_statuses[index] = Status.ON_LINE

print(vertical_indexes)
counter = Counter(index_statuses)
print(counter)

fig, ax = plt.subplots()
ax: plt.Axes
ax.plot(azimuths, elevations)
ax.plot(
    [azimuths[vertical_indexes[0]], azimuths[vertical_indexes[1]]],
    [elevations[vertical_indexes[0]], elevations[vertical_indexes[1]]],
)
plt.show()

segments = find_all_vertical_segments()
print(segments)