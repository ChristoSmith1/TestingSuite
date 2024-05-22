import math
from typing import Any, Generator
import matplotlib as mpl
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms


file_path = R"april21govert/combined_filtered_01.csv"

PI_OVER_2 = math.pi / 2

LINE_OFFSET_MULTIPLIER = .01

data = pd.read_csv(file_path)
min_timestamp = min(data["timestamp_posix"])
data["elapsed"] = data["timestamp_posix"] - min_timestamp

print(data)



def angle_close_to(
    angle_radians: float,
    target_radians: float,
    angle_delta_radians: float = math.radians(1.0),
    reverse_ok: bool = True
) -> bool:
    angle_radians = angle_radians % (2*math.pi)
    target_radians = target_radians % (2*math.pi)
    if (
        target_radians - angle_delta_radians <= angle_radians
        and target_radians + angle_delta_radians >= angle_radians
    ):
        return True
    elif reverse_ok:
        target_radians = (target_radians + math.pi) % (2*math.pi)
        return (
            target_radians - angle_delta_radians <= angle_radians
            and target_radians + angle_delta_radians >= angle_radians
        )   
    else:
        return False

def find_elevation_columns(data: pd.DataFrame):
    data = data.reset_index()
    azimuths = np.array(data["azimuth"])
    elevations = np.array(data["elevation"])

    def elevation_column_search(
        start_index: int,
        end_index: int,
        *,
        angle_delta_radians: float = math.radians(1.0)
    ) -> Generator[tuple[int, int], None, None]: # -> Generator[Any, None, None]:
        # print(f"{start_index}, {end_index}")
        if start_index >= end_index - 1 :
            # print(f"  TERMINAL {start_index=} {end_index=}")
            # return
            # yield
            pass
        else:
            y = elevations[end_index] - elevations[start_index]
            x = azimuths[end_index] - azimuths[start_index]
            
            # NOTE: atan2 requires the y value FIRST, and does not support keyword arguments
            angle_radians = math.atan2(y, x)

            # CRITERION: Line defined by START and END points must be within 1 deg of vertical (i.e., theta=pi/2)
            if angle_close_to(
                angle_radians,
                PI_OVER_2,
                angle_delta_radians=angle_delta_radians
            ):
                # print(f"  +++++ ({start_index},{end_index}) good angle {math.degrees(angle_radians)} deg")
                result = (start_index, end_index)
                yield result
            else:
                # print(f"  ({start_index},{end_index}) bad angle {math.degrees(angle_radians)} deg")
                midpoint_index = (start_index + end_index) // 2
                # print(f"FIRST RECURSIVE CALL START")
                yield from elevation_column_search(start_index, midpoint_index)
                # print(f"FIRST RECURSIVE CALL END / SECOND RECURSIVE CALL START")
                yield from elevation_column_search(midpoint_index, end_index)
                # print(f"SECOND RECURSIVE CALL END")

    candidates = elevation_column_search(0, len(elevations) - 1)
    
    def validate(start_index: int, end_index: int):
        # CRITERION: Must be at least 10 points
        if end_index - start_index - 1 < 10:
            return None
        
        start_az = azimuths[start_index]
        end_az = azimuths[end_index]
        start_el = elevations[start_index]
        end_el = elevations[end_index]
        start_point = np.asarray((start_az, start_el))
        end_point = np.asarray((end_az, end_el))

        # CRITERION: highest elevation must be at least 60 deg
        if max(start_el, end_el) < 60:
            return None
        
        # CRITERION: lowest elevation must be at most 30 deg
        if min(start_el, end_el) > 30:
            return None
        
        # CRITERION: All (az, el) points must be within 1% of the line from START to END
        line_length = math.dist((start_az, start_el), (end_az, end_el))
        def distance_to_line(az: float, el: float) -> float:
            # See https://stackoverflow.com/a/52756183/11700208
            # This could possibly be optimized
            vector = np.asarray((az, el))
            
            return float(np.cross(end_point-start_point,vector-start_point)/np.linalg.norm(end_point-start_point))

        print(f"DEBUG: {line_length=}")
        for index in range(start_index, end_index + 1):
            distance = distance_to_line(azimuths[index], elevations[index])
            # print(f"{distance = }")
            if distance > LINE_OFFSET_MULTIPLIER * line_length:
                return None

        # return (start_index, end_index)
        return (
            data.iloc[start_index],
            data.iloc[end_index],
        )
        pass

    for start_index, end_index in candidates:
        response = validate(start_index, end_index)
        if response:
            yield response


elevation_columns = list(find_elevation_columns(data))

print(elevation_columns)

# print(list(i))



# PLOTS

fig, axes = plt.subplots(1,1, constrained_layout=True)
ax2: plt.Axes = axes
# ax0: plt.Axes = axes[0]
# ax1: plt.Axes = axes[1]
# ax2: plt.Axes = axes[2]

tups = [
    # (ax0, "elapsed", "azimuth"),
    # (ax1, "elapsed", "elevation"),
    (ax2, "azimuth", "elevation"),
]

for ax, x_key, y_key in tups:
    ax: plt.Axes
    ax.plot(data[x_key], data[y_key])
    ax.set_xlabel(x_key)
    ax.set_ylabel(y_key)
    ax.scatter([list(data[x_key])[0]], [list(data[y_key])[0]], color="#00ff00")
    ax.scatter([list(data[x_key])[-1]], [list(data[y_key])[-1]], color="#008888")

for column_start_series, column_end_series in elevation_columns:
    start_el = column_start_series["elevation"]
    end_el = column_end_series["elevation"]
    start_az = column_start_series["azimuth"]
    end_az = column_end_series["azimuth"]
    line_length = math.dist((start_az, start_el), (end_az, end_el))
    width = line_length * LINE_OFFSET_MULTIPLIER

    midpoint_az = (start_az + end_az) / 2
    midpoint_el = (start_el + end_el) / 2

    rect = Rectangle(
        xy=(midpoint_az - width / 2, midpoint_el - line_length / 2),
        height=line_length,
        width=width,
        color="#ff000044",
        # rotation_point="center",
    )
    rotation_angle = math.atan2((end_el-start_el), (end_az-start_az))
    # transform = matplotlib.transforms.Affine2D().rotate_deg_around(midpoint_az, midpoint_el, 0.0) + ax2.transData
    transform = matplotlib.transforms.Affine2D().rotate_around(midpoint_az, midpoint_el, rotation_angle + PI_OVER_2) + ax2.transData
    rect.set_transform(transform)
    ax2.add_patch(rect)
    # ax2.plot([start_az, end_az], [start_el, end_el], color="#ff0000", linewidth=3)
    pass

plt.show()