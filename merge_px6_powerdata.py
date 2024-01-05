from datetime import datetime
from datetime import timedelta
from datetime import time

PX6_FILE_PATH = "mockpx6.txt"
POWER_METER_CSV_PATH = "MSU_PowerMeter_GoverT_09202023_2300UTC_1.txt"

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

with open(PX6_FILE_PATH, "r", encoding="utf8") as pointing_file:
    pointing_file_lines = pointing_file.readlines()

    #print(pointing_file_lines)
    for line in pointing_file_lines:
        # stripped_line = line.strip()
        # print(stripped_line)
        data = parse_px6_line(line)