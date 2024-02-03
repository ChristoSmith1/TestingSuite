from datetime import datetime
from datetime import timedelta
from datetime import time
import csv

PX6_FILE_PATH = "merge_test/mockpx6.txt"
POWER_METER_CSV_PATH = "merge_test/RealPower.csv"

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
        pass

def read_power_file(path: str) -> list [dict]:
    """read a power meter file
    """
    return_value = []
    with open(POWER_METER_CSV_PATH) as csv_file:
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
    with open(PX6_FILE_PATH, "r", encoding="utf8") as pointing_file:
        pointing_file_lines = pointing_file.readlines()

        #print(pointing_file_lines)
        for line in pointing_file_lines:
            # stripped_line = line.strip()
            # print(stripped_line)
            data = parse_px6_line(line)
            if not data: 
                continue
            # print (data)
            return_value.append(data)
            # print (return_value)
        return return_value

print(PX6_FILE_PATH)
data = read_px6_file(PX6_FILE_PATH)
print(data)
print("reading power data")
power_data = read_power_file(POWER_METER_CSV_PATH)
print(power_data)