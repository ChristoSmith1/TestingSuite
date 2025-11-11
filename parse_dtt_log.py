import datetime
import math
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
from g_over_t import _parse_time

# def convert_day_of_year_to_datetime(year, day_of_year):
#     """
#     Converts a given year and day of the year into a datetime object.

#     Args:
#         year (int): The year (e.g., 2025).
#         day_of_year (int): The day of the year (1-365 or 1-366 for leap years).

#     Returns:
#         datetime: A datetime object representing the specified date.
#     """
#     # Create a string in the format 'YYYY-DDD' where DDD is the day of the year
#     date_string = f"{year}-{day_of_year:03d}" 
#     # Use strptime to parse the string with the format code '%Y%j'
#     # %Y for year, %j for day of the year (001-366)
#     date_object = datetime.strptime(date_string, "%Y-%j")
#     return date_object



def read_dtt_log(path: Path):
    data=pd.read_csv(
        path,
        # parse_dates=["Time tag"],
        sep = "\t",
        skip_blank_lines=True,
        skipfooter=1,
        engine="python",
    )

    # Remove first line if it's a leftover from previous log, because the
    # timestamp will be parsed for the wrong DOY otherwise
    if data["Time tag"][0].startswith("23:59"):
        data = data.iloc[1:]

    times = data["Time tag"].to_numpy()

    year_and_doy = path.name.split(".")[-1]
    year, doy = year_and_doy.split("-")
    year = int(year)
    doy = int(doy)
    timestamps = []
    for time in times:
        utc_timestamp_date = _parse_time(2025, 288, f"{time}.000")
        # print(f"{utc_timestamp_date=!s}  {time=}")
        timestamps.append(utc_timestamp_date)

    data["timestamp"] = timestamps

    # print(f"{times=} {type(times)=}")
    # edited_dtt_frame=data[['Time tag','Estimate of Pc/No      dB-Hz']]
    data=data[['timestamp','Estimate of Pc/No      dB-Hz']]
    # print(edited_dtt_frame)

    # Rename column
    data['power'] = data['Estimate of Pc/No      dB-Hz']
    
    # Subset data to columns we care about
    data=data[['timestamp','power']]

    # Return
    return data

if __name__ == "__main__":
        #improts a whole DOY DTT log, which is a log of 37 variables tracked every second of a 24 hour day, as per UTC time
    #we want time or "timestamp" and ESTIMATE of Pc/No which changes as opposed to "predicted" which does not
    path = Path('C:/Users/chris/OneDrive/Desktop/ANOMALY TRACK DATA OCTOBER 2025/DOY 288-304 DTT LOGS/dtt_data/dcc.car.2025-288')
    # data = read_dtt_log(path)
    # print(data)

    paths = sorted(path.parent.glob("*"))
    failures = []
    for index, path in enumerate(paths, start=1):
        print(f"Parsing #{index} of {len(paths)}: {path}")
        try:
            data = read_dtt_log(path)

            output_path = Path("C:/Users/chris/OneDrive/Desktop/ANOMALY TRACK DATA OCTOBER 2025/DOY 288-304 parsed DTT logs") / f"{path.name}.csv"
            output_path.parent.mkdir(parents=True, exist_ok=True,)
            data.to_csv(output_path, index=False)
            print(f"Wrote output to {output_path}")
        except Exception as exc:
            print(f"FAILED on {path}")
            import traceback
            traceback.print_exc()
            failures.append(path)

    print(f"Failed on {len(failures)} paths:")
    for p in failures:
        print(f"  {p}")
# print (convert_day_of_year_to_datetime(2025, 288))
# edited_dtt_frame.to_csv
#append DOY date in the "correct format ex: 2024-03-26 02:00:55.596320"
#print to a csv, the "parsed_dtt_log_[DOY]"
#this CSV is to be stitched together with a HWCTRL log