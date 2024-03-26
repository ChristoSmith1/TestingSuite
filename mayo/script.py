import datetime
import os

import g_over_t

print(f"{os.getcwd() = }")
print(f"{g_over_t = }")

power_data = g_over_t.read_power_file("./mayo/2024-03-26/inputs/power.csv")
pointing_data = g_over_t.parse_hwctrl_log_file("./mayo/2024-03-26/inputs/hwctrl.log")
pointing_data_actual = [
    {
        "timestamp": row["timestamp"],
        "azimuth": row["actual_azimuth"],
        "elevation": row["actual_elevation"],
    }
    for row
    in pointing_data
]
pointing_data_commanded = [
    {
        "timestamp": row["timestamp"],
        "azimuth": row["commanded_azimuth"],
        "elevation": row["commanded_elevation"],
    }
    for row
    in pointing_data
]
pass
combined_actual = g_over_t.combine_power_position(power_data=power_data, position_data=pointing_data_actual)
combined_commanded = g_over_t.combine_power_position(power_data=power_data, position_data=pointing_data_commanded)
g_over_t.write_csv(data=combined_actual, path="./mayo/2024-03-26/outputs/combined_actual.csv")
g_over_t.write_csv(data=combined_commanded, path="./mayo/2024-03-26/outputs/combined_commanded.csv")
g_over_t.write_csv(data=power_data, path="./mayo/2024-03-26/outputs/power_data.csv")
g_over_t.write_csv(data=pointing_data_actual, path="./mayo/2024-03-26/outputs/pointing_data_actual.csv")
g_over_t.write_csv(data=pointing_data_commanded, path="./mayo/2024-03-26/outputs/pointing_data_commanded.csv")
g_over_t.write_csv(data=pointing_data, path="./mayo/2024-03-26/outputs/pointing_data.csv")

import matplotlib.pyplot as plt


timestamps_float = g_over_t.get_column(combined_actual, "timestamp_posix")
timestamps_float_zeroed = [
    x - timestamps_float[0]
    for x
    in timestamps_float
]
timestamps_dt = g_over_t.get_column(combined_actual, "timestamp")
powers = g_over_t.get_column(combined_actual, "power")
azimuths_actual = g_over_t.get_column(combined_actual, "azimuth")
elevations_actual = g_over_t.get_column(combined_actual, "elevation")
azimuths_commanded = g_over_t.get_column(combined_commanded, "azimuth")
elevations_commanded = g_over_t.get_column(combined_commanded, "elevation")


# https://stackoverflow.com/a/45925049/11700208
# fig, ax = plt.subplots(layout="constrained")
fig, ax1 = plt.subplots()
# ax: plt.Axes
# ax1: plt.Axes = ax.twinx()
ax1: plt.Axes
ax2: plt.Axes = ax1.twinx()
plots: list[plt.Line2D] = []
plots.append(ax1.plot(timestamps_float_zeroed, powers, label="Power", color="black"))

# ax2 = ax1.twinx()
# ax2: plt.Axes
# ax.plot(timestamps_dt, powers)

# ax.plot(timestamps_float_zeroed, azimuths_actual, label="azimuth (actual)")
# ax.plot(timestamps_float_zeroed, elevations_actual, label="elevation (actual)")
# ax.plot(timestamps_float_zeroed, azimuths_commanded, label="azimuth (commanded)")
# ax.plot(timestamps_float_zeroed, elevations_commanded, label="elevation (commanded)")
ax1.set_xlabel(f"seconds since {timestamps_dt[0]}")
ax1.set_ylabel(f"Power (dBm)")

plots.append(ax2.plot(timestamps_float_zeroed, azimuths_actual, label="azimuth", color="red"))
plots.append(ax2.plot(timestamps_float_zeroed, elevations_actual, label="elevation", color="green"))
ax2.set_ylabel(f"Az/El degrees")
# ax.plot(azimuths_actual, elevations_actual, label="actual")
# ax.plot(azimuths_commanded, elevations_commanded, label="commanded")
# ax.set_xlabel("Azimuth")
# ax.set_ylabel("Elevation")

# ax.spines[['right', 'top']].set_visible(False)
# ax.set_yticklabels([])

ax1.legend(handles = plots[0] + plots[1] + plots[2])
plt.show()
