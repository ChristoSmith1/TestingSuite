from datetime import datetime
from datetime import timedelta
from datetime import time
import csv
from typing import Any

#"r", encoding="utf8") as csv_file:

PX6_FILE_PATH = "merge_test\GTprocedure_3.txt"
POWER_METER_CSV_PATH_1 = "merge_test\MSU_PowerMeter_GoverT_06022024_XXXXUTC_1.csv"
POWER_METER_CSV_PATH_2 = "merge_test\MSU_PowerMeter_GoverT_06022024_XXXXUTC_2.csv"
POWER_METER_CSV_PATH_3 = "merge_test\MSU_PowerMeter_GoverT_06022024_XXXXUTC_3.csv"


def parse_time(year: int, days: int, time: str,) -> datetime:
    """convert time and date to datetime object"""
    jan_1 = datetime(year,1,1)
    delta_after_jan1 = timedelta(days-1)
    date_in_px6 = jan_1 + delta_after_jan1
    # print(f"{jan_1} {delta_after_jan1} {date_in_px6}")

    utc_time = datetime.strptime(time, "%H:%M:%S.%f").replace(year=date_in_px6.year, month=date_in_px6.month, day=date_in_px6.day)
    return utc_time 
    pass

def parse_px6_line(line: str) -> dict:
    """parse a line"""
    # print(line)
    try:
        stripped_line = line.strip()
        # print(f"stripped_line: {stripped_line} {type(stripped_line)}")
        tokens = stripped_line.split()
        # print(f"tokens: {tokens} {type(tokens)}")
        year = int(tokens[0])
        doy = int(tokens[1])
        time_in_utc = tokens[2]
        azimuth = float(tokens[3])
        elevation = float(tokens[4])
        # print(f"{year = }  {doy = }   {time_in_utc = }   {azimuth = }   {elevation = }")
        date_object = parse_time(year,doy,time_in_utc)
        # print(date_object)
        return_value = {
            "timestamp": date_object,
            "azimuth": azimuth,
            "elevation": elevation,
        }
        return return_value
    except Exception as exc:
        return_value = {

        }
        # print(f"EXCEPTION: {type(exc)} {exc}")
        return return_value
        
def read_power_file(path: str) -> list [dict]:
    """read a power meter file
    """
    return_value = []
    with open(path,"r",encoding='utf8') as csv_file:
        csv_reader = csv.DictReader(csv_file,fieldnames=["timestamp","power"])
        for row_dict in csv_reader:
            timestamp_str = row_dict["timestamp"]
            timestamp_dt = datetime.fromisoformat(timestamp_str)
            power_float = float(row_dict["power"])
            row_dict["power"] = power_float
            row_dict["timestamp"] = timestamp_dt
            return_value.append(row_dict)
            # print(f"{timestamp_str=!r}   {type(timestamp_str)=}")
            # print(f"{timestamp_dt=!r}   {type(timestamp_dt)=}")
            # print()
        return return_value
        
def read_px6_file(path: str) -> list[dict]:
    """read a px6 file
    """
    return_value = []
    with open(path, "r", encoding="utf8") as pointing_file:
        pointing_file_lines = pointing_file.readlines()

        #print(pointing_file_lines)
        for line in pointing_file_lines:
            stripped_line = line.strip()
            # print(stripped_line)
            data = parse_px6_line(line)
            if not data: 
                continue
            # print (data)
            return_value.append(data)
            # print (return_value)
        return return_value


def get_column(data: list[dict[str, Any]], key: str) -> list[Any]:
    """Get the data for a given key from a list of dicts, where each
    dict contains that key

    ```
    px6_data = read_px6_file(PX6_FILE_PATH)
    azimuth_data_list = get_column(px6_data, "azimuth")
    ```

    Args:
        data (list[dict[str, Any]]): _description_
        key (str): _description_

    Returns:
        list[Any]: _description_
    """
    return [
        item[key]
        for item
        in data
    ]

#print(PX6_FILE_PATH)
pointing_data_1 = read_px6_file(PX6_FILE_PATH)
#print(power_data_timestamps)
pointingaz = get_column(pointing_data_1,"azimuth")
pointingel = get_column(pointing_data_1,"elevation")
pointtime = get_column(pointing_data_1,"timestamp")


power_data_1 = read_power_file(POWER_METER_CSV_PATH_1)
power_data_2 = read_power_file(POWER_METER_CSV_PATH_2)
power_data_3 = read_power_file(POWER_METER_CSV_PATH_3)

# You can combine lists of things like this:
#combined_power_data = power_data_1 + power_data_2 + power_data_3
combined_power_data = power_data_3

power_data_timestamps = get_column(combined_power_data, "timestamp")
power_data_power = get_column(combined_power_data, "power")

import matplotlib.pyplot as plt
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
fig.suptitle('Power vs. Time and Azimuth vs. Elevation')

ax1.plot(power_data_timestamps,power_data_power)
ax1.set_title('power vs. time')
ax1.set_ylabel('power in dB')
ax1.set_xlabel('Day + Time in UTC')

ax2.plot(pointtime,pointingaz, 'tab:green')
ax2.set_title('time vs. az')
ax2.set_xlabel("time")
ax2.set_ylabel("azimuth")

ax3.plot(pointtime,pointingel)
ax3.set_title('time vs. el')
ax3.set_xlabel("time")
ax3.set_ylabel("elevation")

ax4.plot(pointingaz,pointingaz, 'tab:red')
ax4.set_title('az vs. el')
ax4.set_xlabel("azimuth")
ax4.set_ylabel("elevation")

fig.tight_layout()

plt.show()