"""
Written 2024-03-28 to analyze data collected on 2024-03-26
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

# INPUT DATA PATHS
# Paths to data from 2024-04-21 test
POWER_METER_DATA_PATH = R"april21govert\MSU_PowerMeter_GoverT_04212024_0230UTC_1.csv"
PX6_DATA_PATH = R"april21govert\GTprocedure20240421.txt"
HWCTRL_LOG_DATA_PATH = R"april21govert\GTAUTO.176.D113T00-27-51"

# OUTPUT DATA PATHS
COMBINED_DATA_PATH = R"april21govert\combined_01.csv"
FILTERED_COMBINED_DATA_PATH = R"april21govert\combined_filtered_01.csv"

if __name__ == "__main__":
    print(f"START OF SCRIPT {__file__}")
    start_time = datetime.datetime.now()
    print(f"Script {__file__} started at {start_time}")

    # Read the data
    print(f"***** Reading in data *****")
    power_meter_data = g_over_t.read_power_file(POWER_METER_DATA_PATH)
    px6_data = g_over_t.read_px6_file(PX6_DATA_PATH)
    hwctrl_data = g_over_t.parse_hwctrl_log_file(HWCTRL_LOG_DATA_PATH)


    # This function should be moved into `g_over_t`.
    def print_raw_data_info(data: list[dict[str, Any]], detail: bool = False) -> None:
        """Print out some summary information about data that is represented
        as a list of dicts for each row's data.

        There is no return value. The data is printed to the screen.

        If `detail` is `True`, print detailed information about each key.
        """
        print(f"There are {len(data):,} data points.")
        if not data:
            print(f"  [No data points to analyze.]")
            return
        print(f"  keys: {list(data[0])}")
        if not detail:
            return
        for key, value in data[0].items():
            print(f"  KEY: {key}")
            column_data = g_over_t.get_column(data=data, key=key)
            print(f"    key type:   {type(key)!r}")
            print(f"    value type: {type(value)!r}")
            print(f"    first: {column_data[0]}")
            print(f"    last:  {column_data[-1]}")
            try:
                column_min = min(column_data)
                column_max = max(column_data)
                print(f"    min: {column_min}")
                print(f"    max: {column_max}")
                print(f"    (max - min): {column_max - column_min}")
                print(f"    (last - first): {column_data[-1] - column_data[0]}")
            except:
                print(f"    Unable to do calculations on this column.")
                pass


    print(f"***** RAW DATA SUMMARY STATS *****")
    print(f"`power_meter_data`  from {POWER_METER_DATA_PATH}")
    print_raw_data_info(power_meter_data)
    print()
    print(f"`px6_data`  from {PX6_DATA_PATH}")
    print_raw_data_info(px6_data)
    print()
    print(f"`hwctrl_data`  from {HWCTRL_LOG_DATA_PATH}")
    print_raw_data_info(hwctrl_data)
    print()

    # A PROBLEM:
    # 
    # Note that the keys printed out above for `px6_data` and `hwctrl_data` are not the same:
    # 
    # 
    # `px6_data`  from ./GTpoint03252024.txt
    #   keys: ['timestamp', 'azimuth', 'elevation']
    # 
    # `hwctrl_data`  from ./newEvent.176.D086T01-59-45
    #   keys: ['timestamp', 'actual_azimuth', 'actual_elevation', 'commanded_azimuth', 'commanded_elevation']
    #
    #
    # This will cause problems if we use `hwctrl_data` for the pointing data, since our
    # `g_over_t.combine_power_position()` function expects keys of "azimuth" and "elevation".
    # 
    # SOLUTION FOR THIS DATA SET: We go through each row dictionary in `hwctrl_data` list and add a new entry to the
    # dictionary for key "azimuth" and key "elevation"
    # 
    # SOLUTION IN THE FUTURE: Fix the `g_over_t.parse_hwctrl_log_file()` function to output the correct keys.
    for row_dictionary in hwctrl_data:
        # Get the actual azimuth value
        actual_azimuth = row_dictionary["actual_azimuth"]

        # Save that azimuth value back to the dictionary with the key "azimuth"
        row_dictionary["azimuth"] = actual_azimuth

        # Get the actual elevation value
        actual_elevation = row_dictionary["actual_elevation"]

        # Save that elevation value back to the dictionary with the key "elevation"
        row_dictionary["elevation"] = actual_elevation

    print(f"**** AFTER ADDING 'azimuth' AND 'elevation' KEYS *****")
    print(f"`hwctrl_data`  after modification")
    print_raw_data_info(hwctrl_data)
    print()


    # A MUCH MORE SUBTLE PROBLEM
    # 
    # Some of our timestamps don't know that they are UTC times.
    # 
    # So when we convert those to POSIX time (which is the number of seconds elapsed
    # since 1970-01-01 00:00:00 UTC), the ones that don't know they are UTC times get
    # treated as local time times, and the values are off by 3600 * 4 = 14400 seconds.
    def print_timezone(data: list[dict[str, Any]]) -> None:
        """Print the timezone info of the "timestamp" value of the first row's
        row dictionary"""
        try:
            first_row_data = data[0]
            timestamp: datetime.datetime = first_row_data["timestamp"]
            timezone = timestamp.tzinfo
            print(f"timezone={timezone!r}  [{type(timezone)!r}]")
        except:
            print(f"Unable to find a `datetime.datetime` object")


    print(f'***** Time zone attribute of "timestamp" values [before fix] *****')
    print("`hwctrl_data`:      ", end="")
    print_timezone(hwctrl_data)
    print("`px6_data`:         ", end="")
    print_timezone(px6_data)
    print("`power_meter_data`: ", end="")
    print_timezone(power_meter_data)
    print()

    # SOLUTION FOR THIS DATASET: Convert all the `datetime.datetime` objects to have their timezone
    # set to UTC
    # 
    # SOLUTION FOR THE FUTURE: Fix the `g_over_t.read_px6_file()` and `g_over_t.read_power_file()`
    # functions to set the timestamps to be UTC.
    def fix_timestamps(data: list[dict[str, Any]]) -> None:
        """_summary_

        Args:
            data (list[dict[str, Any]]): _description_
        """

        # Iterate over the rows
        for row_dictionary in data:

            # Iterate over the key, value pairs of the row dictionary
            for key, value in row_dictionary.items():
                
                # Check that this value is a `datetime.datetime` object.
                if isinstance(value, datetime.datetime):
                    old_timestamp = value

                    # Check if there is no time zone is set
                    if old_timestamp.tzinfo is None:
                        # Make a copy of the `datetime.datetime` with the same numeric values,
                        # But interpreted as a UTC time.
                        new_timestamp = old_timestamp.replace(tzinfo=datetime.UTC)

                        # Replace the existing value in the row dictionary with this new thing
                        row_dictionary[key] = new_timestamp

    print(f"***** Fixing timestamps *****")
    fix_timestamps(hwctrl_data)
    fix_timestamps(px6_data)
    fix_timestamps(power_meter_data)
    print(f'***** Time zone attribute of "timestamp" values [AFTER FIX] *****')
    print("`hwctrl_data`:      ", end="")
    print_timezone(hwctrl_data)
    print("`px6_data`:         ", end="")
    print_timezone(px6_data)
    print("`power_meter_data`: ", end="")
    print_timezone(power_meter_data)
    print()

    # After applying those fixes, we can properly combine our data!
    print(f"***** Combining data (might take awhile) *****")
    print(f"Started at {datetime.datetime.now():%X}")
    combined_data = g_over_t.combine_power_position(power_data=power_meter_data, position_data=hwctrl_data)
    print(f"Finished at {datetime.datetime.now():%X}")
    print()
    print(f"***** SUMMARY OF `combined_data` *****")
    print_raw_data_info(combined_data)
    print()

    print(f"***** DETAILS OF `combined_data` *****")
    print_raw_data_info(combined_data, detail=True)
    print()



    # FILTER OUT THE NANS
    # This should also go in `g_over_t`
    def filter_out_nan(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create a copy of the data, but any row that has any NaN value (for any key) will be thrown out"""
        data_copy = data.copy()

        # A little trick! I use this trick all the time, but I think I'm the only one.
        # 
        # We're going to be deleting rows from the list. If we start at the beginning of the list and delete
        # an item, it will mess up the indexes later in iteration. (If we delete index=5, then what used to be
        # in index=6 is now in index=5, and if I then move on to the next index (6), I'll never inspect the old
        # index=6, which is the new index=5, and move on to the new index=6, which was the old index=7.)
        # 
        # Instead of dealing with all that, we go backwards: Start at the biggest index, then count down to 0
        # Then we just delete the relevant ones as we find them and everything is fine.
        # 
        # (This is also guaranteed to be faster because of computer science reasons. Deleting an item from a list takes
        # an amount of time proportional to how many items exist between the index you're deleting and the end of
        # the list.)
        reversed_indexes = list(reversed(range(len(data))))
        for index in reversed_indexes:
            row = data_copy[index]
            found_any_nan = False
            for value in row.values():
                try:
                    if math.isnan(value):
                        found_any_nan = True
                        break
                        # print(f"Found a nan at index={index}")
                except TypeError:
                    pass
            if found_any_nan:
                # data_copy.pop(index)
                del data_copy[index]
        return data_copy


    valid_combined_data = filter_out_nan(combined_data)

    print(f"***** SUMMARY OF `filtered_combined_data` *****")
    print_raw_data_info(valid_combined_data)
    print()

    print(f"***** DETAILS OF `filtered_combined_data` *****")
    print_raw_data_info(valid_combined_data, detail=True)
    print()


    # This function should go into `g_over_t` and be used by all the
    # g_over_t.
    def create_parent_folder(path: str | Path) -> Path:
        """Create the folder represented by a path.
        
        Returns the fully qualified `Path` of the passed file path."""
        # Make the path be a `pathlib.Path` object, which is easier to work with
        path = Path(path)

        # Convert paths like "~/whatever/" to "/home/username/whatever/"
        # This is mostly only important on Linux
        path = path.expanduser()

        # Convert relative path like "./subfolder/" to "c:/dev/project/subfolder/"
        # (Assuming that your current directory is "c:/dev/project")
        path = path.resolve()

        # The folder will be the parent of the given path
        folder = path.parent

        # Make the directory.
        # The arguments mean "Make the folder, even if the folder's parent path doesn't already exist"
        # and "If the folder already exists, don't raise an exception."
        if not folder.exists():
            print(f"Creating folder {folder}")
            folder.mkdir(parents=True, exist_ok=True)
        
        # Return back the path object, which will be fully qualified and absolute now.
        return path


    combined_data_file_path = create_parent_folder(COMBINED_DATA_PATH)
    #print(f"***** Writing `combined_data` to {combined_data_file_path} *****")
    g_over_t.write_csv(
        data = combined_data,
        path = combined_data_file_path,
    )

    filtered_combined_data_file_path = create_parent_folder(FILTERED_COMBINED_DATA_PATH)
    #print(f"***** Writing `filtered_combined_data` to {filtered_combined_data_file_path} *****")
    g_over_t.write_csv(
        data = valid_combined_data,
        path = filtered_combined_data_file_path,
    )

    #  ╭───────────────────────────╮
    #  │                           │
    #  │     DO ANALYSIS HERE!     │
    #  │                           │
    #  ╰───────────────────────────╯
    # 
    # At this point in the code, you have these two objects to work with:
    # 
    # `combined_data` is a list of 29,167 row dictionaries.
    # 
    # Each row dictionary has these keys and values:
    # 
    #   key               --> value type [description]
    #   -----------------     ------------------------------------------------------------------------------------
    #   "timestamp_posix" --> float [Number of seconds since Unix epoch]
    #   "timestamp"       --> datetime.datetime [The time as a Python object in UTC time zone.]
    #   "power"           --> float [Measured power in dBm (I think?)]
    #   "azimuth"         --> float [ACTUAL azimuth, in degrees, linearly interpolated from the HWCTRL log data]
    #   "elevation"       --> float [ACTUAL elevation, in degrees, linearly interpolated from the HWCTRL log data]
    # 
    # `filtered_combined_data` is the same thing, but it has 27,718 data points. Every data point that has
    # ANY value that is a NAN has been removed.
    power_data_list = g_over_t.get_column(valid_combined_data, "power")
    elevation_data_list = g_over_t.get_column(valid_combined_data, "elevation")
    azimuth_data_list = g_over_t.get_column(valid_combined_data, "azimuth")
    time_data_list = g_over_t.get_column(valid_combined_data, "timestamp_posix")

    # plt.plot (time_data_list,power_data_list)
    # plt.plot (elevation_data_list, time_data_list)
    # plt.show()

    # fig, axs = plt.subplots(3)
    # fig.suptitle('Vertically stacked subplots')
    # axs[0].plot(time_data_list, power_data_list)
    # axs[1].plot(time_data_list, elevation_data_list)
    # axs[2].plot(time_data_list, azimuth_data_list)
    # plt.show()
##### ACTUAL VS COMMANDED POINTING #####
    
##### ATTEMPTING TO FIGURE OUT FILTERING OF ELEVATION COLUMNS #####

    elevation_column_1_points = [
        point
        for point
        in valid_combined_data
        if point["azimuth"] <=(120)
    ]
    elevation_column_2_points = [
        point
        for point
        in elevation_column_1_points
        if point["timestamp_posix"] >=(1713747477.119895)
    ]
    elevation_column_3_points = [
        point
        for point
        in elevation_column_2_points
        if point["timestamp_posix"] <=(1713749583.801868)
    ]
    for point in elevation_column_3_points:
        elcolel = g_over_t.get_column(elevation_column_3_points,"elevation")
        elcolpower = g_over_t.get_column(elevation_column_3_points,"power")
    Yfactor=4.45
    print(f"Y-factor ={Yfactor}")
    T_op = (180-((10**(Yfactor/10))*10))/((10**(Yfactor/10))-1)
    # T_el = (T_op*10**((elcolpower-60.22))/10)
    print(f"Tempetrature (Op), T_op = {T_op}")

#     # #####Y-FACTOR DEFINITION####
#    Yfactor=(max(power_data_list)-min(power_data_list))
#     # need Y-factor to be just from the on/off moon portion of the test
#     # having it use the generic minimum creates an inaccurate reading
#     #T(el) = T_op*10**(measured power at elevation - cold sky temperature from moon reading)
#     #plotting T(el) we must first caluclate it for Az=200,Az=225

# #T_op = (135-((10**(Y-factor/10))*10))/((10**(Y-factor/10))-1) <- correct math!
# #T_el = T_op*10**((measured_power_at_any_elevation - off_moon_measurement)/10) <- theoretical math
# #off_moon_measurement hardcoded in as -40.52 until I figure out how to identify it. <- future problem
# #then I need to plot Y=T_el, X=elevation <-next to last step
# #overlay a line over that plot to show the T_el average <-last step

    delta_cold_sky_off_moon = [-60.22]*len(elcolpower) #designed to make a list that is the length of all elevations, but -40.52dB see line 374
    #print(delta_cold_sky_off_moon)
    my_array = np. array(delta_cold_sky_off_moon)
    #print(my_array)
    my_array2 = np. array(elcolpower)
    #print(my_array2-my_array)
    my_array3 = (my_array2-my_array)/10
    Tel = T_op*(10**my_array3)

    # ######PLOTS FOR DATA VISUALIZATION#####
    ### tip curve ###
    plt.plot(elcolel,Tel)
    plt.plot(np.unique(elcolel), np.poly1d(np.polyfit(elcolel, Tel, 4))(np.unique(elcolel)))
    plt.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    plt.title('SNT vs. elevation at 119 degrees Azimuth')
    plt.ylabel('SNT (in K)')
    plt.xlabel('Elevation in Degrees')
    plt.show()

#     # ######DOME PLOT FOR TRACK#####
#     # # min = min(power_data_list)
#     # # print (min)
#     # def minmap(power_data_list) -> list[float]:
#     #     minimum=min(power_data_list)
#     #     scaled_values =[]
#     #     for i in power_data_list:
#     #         new_value = i - minimum
#     #     scaled_values.append(new_value)
#     #     return scaled_values

#     # minmapvalues=minmap(power_data_list)

#     # azimuth_rad = np.radians(azimuth_data_list)
#     # elevation_rad = np.radians(elevation_data_list)

#     # # Create a 3D plot
#     # fig = plt.figure(figsize=(8, 8))
#     # ax = fig.add_subplot(111, projection='3d')

#     # # Plot points on the dome
#     # ax.scatter(np.cos(azimuth_rad) * np.sin(elevation_rad),
#     #         np.sin(azimuth_rad) * np.sin(elevation_rad),
#     #         np.cos(elevation_rad),marker=".",
#     #         c=power_data_list, cmap='YlOrRd')  # Colormap from green to red, eventually

#     # # Set labels and title
#     # ax.set_xlabel('Az angle')
#     # ax.set_ylabel('Az angle')
#     # ax.set_zlabel('Elevation angle')
#     # ax.set_title(f"Az. and El. Points Heat Mapped to Power Data in dBm, Yfactor ={Yfactor}")

#     # # Set limits and aspect ratio
#     # ax.set_xlim(-1, 1)
#     # ax.set_ylim(-1, 1)
#     # ax.set_zlim(-1, 1)
#     # ax.set_aspect('equal')

#     # # Remove axis ticks and grid
#     # ax.set_xticks([])
#     # ax.set_yticks([])
#     # ax.set_zticks([])
#     # ax.grid(True)

#     # # Colorbar
#     # sm = plt.cm.ScalarMappable(cmap='YlOrRd')
#     # sm.set_array([])
#     # fig.colorbar(sm, label='Power Meter Values (in dB)', ax=ax)
#     # # Show the plot
#     # plt.show()

    # Wrapping up
    print(f"***** Analysis complete *****")
    finish_time = datetime.datetime.now()
    elapsed_time = finish_time - start_time
    print(f"Script finished at {finish_time:%X}")
    print(
        f"Total run time: {elapsed_time}"
        + f" = {elapsed_time.total_seconds():,} seconds"
        + f" = {elapsed_time.total_seconds() / 60:,} minutes"
        + f" = {elapsed_time.total_seconds() / 3600:,} hours"
    )
    print(f"END OF SCRIPT {__file__}")