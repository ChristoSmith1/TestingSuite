import csv
from datetime import UTC, datetime, timedelta, time, timezone
import functools
import math
from pathlib import Path
import re
from typing import Any, Literal, Protocol, Sequence
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline, PchipInterpolator


def hello_world(message: str):
    print (f"Hello {message}")

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

def _parse_time(year: int, days: int, time: str,) -> datetime:
    """convert time and date to datetime object"""
    jan_1 = datetime(year,1,1)
    delta_after_jan1 = timedelta(days-1)
    date_in_px6 = jan_1 + delta_after_jan1
    # print(f"{jan_1} {delta_after_jan1} {date_in_px6}")

    # CHANGED 2024-08-09:
    # UTC time zone added. (Previously, `datetime` object was naive)
    utc_time = datetime.strptime(time, "%H:%M:%S.%f").replace(
        year=date_in_px6.year,
        month=date_in_px6.month,
        day=date_in_px6.day,
        # tzinfo=timezone.utc,
    )
    return utc_time 
    pass

def _parse_px6_line(line: str) -> dict:
    """parse a line of position data from px6 file"""
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
        date_object = _parse_time(year,doy,time_in_utc)
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
        
def read_power_file(path: str) -> list [dict[str, datetime | float]]:
    """read a power meter file. Expected datetime UTC and power in dB.
    the function returns a list of dictionaries of strings
    """
    return_value = []
    with open(path,"r",encoding='utf8') as csv_file:
        csv_reader = csv.DictReader(csv_file,fieldnames=["timestamp","power"])
        for row_dict in csv_reader:
            timestamp_str = row_dict["timestamp"]
            timestamp_dt = datetime.fromisoformat(timestamp_str)
            timestamp_dt = timestamp_dt.replace(tzinfo=timezone.utc)
            power_float = float(row_dict["power"])
            row_dict["power"] = power_float
            row_dict["timestamp"] = timestamp_dt
            return_value.append(row_dict)
            # print(f"{timestamp_str=!r}   {type(timestamp_str)=}")
            # print(f"{timestamp_dt=!r}   {type(timestamp_dt)=}")
            # print()
        return return_value
        
def read_px6_file(path: str) -> list[dict[str, datetime | float]]:
    """read a px6 file 
    """
    return_value = []
    with open(path, "r", encoding="utf8") as pointing_file:
        pointing_file_lines = pointing_file.readlines()

        #print(pointing_file_lines)
        for line in pointing_file_lines:
            stripped_line = line.strip()
            # print(stripped_line)
            data = _parse_px6_line(line)
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
    """
    return [
        item[key]
        for item
        in data
    ]

# This class is only to make type hinting work better.
# This entire thing can be deleted with no change in
# functionality.
class _FloatInterpolator(Protocol):
    def __call__(self, x: float) -> float:
        """Interpolate the given value of `x`"""
        ...


class LinearSpline(_FloatInterpolator):
    """Class to mimic (some) behavior of `scipy.interpolate.CubicSpline` et al
    for linear interpolation"""
    def __init__(
        self,
        x: Sequence[float],
        y: Sequence[float],
        extrapolate: bool = False,
    ) -> None:
        self.x = list(x)
        self.y = list(y)
        self.min_x = min(self.x)
        self.max_x = max(self.x)
        self.extrapolate = extrapolate

    @functools.lru_cache(maxsize=None)  # noqa: B019
    def __call__(self, x: float) -> float:
        if (
            (x < self.min_x or x > self.max_x)
            and not self.extrapolate
        ):
            return float("nan")
        return np.interp(
            x,
            self.x,
            self.y,
        )


class Interpolator:
    def __init__(
        self,
        data: list[dict[str, float]],
        x_key: str,
        *,
        method: Literal["linear", "cubic", "pchip"] = "linear",
        extrapolate: bool = False,
    ) -> None:
        self.x_key = x_key
        self.data = data
        self.extrapolate = extrapolate
        self.y_keys = {
            key
            for key
            in data[0]
            if (
                key != self.x_key
                and isinstance(data[0][key], (int, float))
            )
        }
        # if len(self.y_keys) == 1:
        #     self.y_key = next(iter(self.y_keys))
        # else:
        #     self.y_key = None
        
        self.method = method
        self.xs = [item[x_key] for item in data]
        if isinstance(self.xs[0], datetime):
            self.xs: list[datetime]
            self.xs = [item[x_key] for item in data]
            pass

        self._interpolators: dict[str, _FloatInterpolator] = {}
        if self.method == "linear":
            self._create_linear_interpolators()
        elif self.method == "cubic":
            self._create_cubic_interpolators()
        elif self.method == "pchip":
            self._create_pchip_interpolators()
        else:
            raise ValueError(f"Invalid interpolation type {self.method!r}.")
    
    def __call__(self, x: float, key: str) -> float:
        return self._interpolators[key](x)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} object, method={self.method!r}, x_key={self.x_key!r}, domain=[{min(self.xs):0.4f},{max(self.xs):0.4f}]>"

    def _create_linear_interpolators(self) -> None:
        for y_key in self.y_keys:
            ys = [item[y_key] for item in self.data]
            self._interpolators[y_key] = LinearSpline(
                x=self.xs,
                y=ys,
                extrapolate=self.extrapolate,
            )

    def _create_cubic_interpolators(self) -> None:
        for y_key in self.y_keys:
            ys = [item[y_key] for item in self.data]
            self._interpolators[y_key] = CubicSpline(
                x=self.xs,
                y=ys,
                extrapolate=self.extrapolate,
            )

    def _create_pchip_interpolators(self) -> None:
        for y_key in self.y_keys:
            ys = [item[y_key] for item in self.data]
            self._interpolators[y_key] = PchipInterpolator(
                x=self.xs,
                y=ys,
                extrapolate=self.extrapolate,
            )

def combine_power_position(
    power_data: list[dict[str, Any]],
    position_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """combine power and position with linearily interpolated values of az and el
    limiting factor is timestamp from power data 

    These are the keys: 
            'timestamp_posix'
            'timestamp'
            'power'
            'azimuth'
            'elevation'

    Args:
        power_data (list[dict[str, Any]]): _description_
        position_data (list[dict[str, Any]]): _description_

    Returns:
        list[dict[str, Any]]: _description_
    """
    # add timestamp_float key to all data
    for row in power_data:
        timestamp_dt: datetime = row['timestamp']
        timestamp_float = timestamp_dt.timestamp()
        row['timestamp_float'] = timestamp_float
    for row in position_data:
        timestamp_dt: datetime = row['timestamp']
        timestamp_float = timestamp_dt.timestamp()
        row['timestamp_float'] = timestamp_float

    interpolator = Interpolator(position_data,"timestamp_float")
    # print(interpolator)
    
    # creating a L.D.S. with time, power, az, el
    return_value=[]
    for power_data_row in power_data:
        timestamp_float = power_data_row['timestamp_float']
        timestamp_dt = power_data_row['timestamp']
        power = power_data_row['power']
        azimuth = interpolator(timestamp_float,'azimuth')
        elevation = interpolator(timestamp_float,'elevation')
        # print(f"{timestamp_float=} {timestamp_dt=} {power=}  {azimuth=}  {elevation=}")
        output_row_dict = {
            'timestamp_posix': timestamp_float,
            'timestamp': timestamp_dt,
            'power': power,
            'azimuth': azimuth,
            'elevation': elevation,

        }
        return_value.append(output_row_dict)
    return return_value

_hwctrl_regex_pattern = re.compile(
    r"^(?P<year>\d+)\s+"
    + r"(?P<day>\d+)\s+"
    + r"(?P<time>\d+:\d+:\d+),\s*"
    + r"(?P<actual_azimuth>\d+\.?\d*),\s*"
    + r"(?P<actual_elevation>\d+\.?\d*),"
    + r"(?P<commanded_azimuth>\d+\.?\d*),\s*"
    + r"(?P<commanded_elevation>\d+\.?\d*),"
    + r".*$",
    flags=re.MULTILINE,
)

# print(f"Regex pattern string is:\n{regex_pattern.pattern!r}")
# print(f"\nRegex pattern is:\n{regex_pattern}")

def parse_hwctrl_log_text(text: str) -> list[dict[str, datetime | float]]:
    """extract hwctrl log data from raw text
    These are the exact keys:
            "timestamp"
            "actual_azimuth"
            "actual_elevation"
            "commanded_azimuth"
            "commanded_elevation"
            "azimuth"
            "elevation"
    Args:
        text (str): _description_

    Returns:
        list[dict[str, datetime | float]]: _description_
    """
    rv = []
    for match in _hwctrl_regex_pattern.finditer(text):
        # print (match)
        groupdict = match.groupdict()
        
        date_dt = datetime(
            year=int(groupdict["year"]),
            month=1,
            day=1,
        ) + timedelta(
            days = int(groupdict["day"]) - 1,
        )
        time_hwctrl = time.fromisoformat(groupdict["time"])
        timestamp = datetime.combine(date_dt.date(), time_hwctrl, tzinfo=UTC)
        
        # NOTE: Changed the keys on 2024-08-09:
        # "actual_azimuth" -> "azimuth"
        # "actual_elevation" -> "elevation"
        rv.append({
            "timestamp": timestamp,
            "azimuth": float(groupdict["actual_azimuth"]),
            "elevation": float(groupdict["actual_elevation"]),
            "commanded_azimuth": float(groupdict["commanded_azimuth"]),
            "commanded_elevation": float(groupdict["commanded_elevation"]),
        })
    return rv

def parse_hwctrl_log_file(path: Path | str) -> list[dict[str, datetime | float]]:
    """reads hwctrl log file

    Args:
        path (Path | str): _description_

    Returns:
        list[dict[str, datetime | float]]: _description_
    """
    path = Path(path).expanduser().resolve()
    text = path.read_text(encoding="utf8")
    return parse_hwctrl_log_text(text)

def _convert_timestamp_to_float(data: list[dict[str, datetime | float]]) -> None:
    """Convert the entries' `"timestamp"` values from `datetime.datetime` objects to `float` objects"""
    for item in data:
        timestamp_dt: datetime = item["timestamp"]
        timestamp_float: float = float(timestamp_dt.timestamp())
        item["timestamp_float"] = timestamp_float
        item["timestamp_dt"] = timestamp_dt
        del item["timestamp"]

def _convert_timestamp(
    timestamp: datetime,
    coerce_naive_to_utc: bool = True,
    sep: str = "T",
) -> str:
    if coerce_naive_to_utc and timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.isoformat(sep=sep,timespec="microseconds")

def write_csv(
    data: list[dict[str, datetime | float]],
    path: Path | str,
    fieldnames: Sequence[str] | None = None,
):
    """Writes csv from the LDS of data passed to it to the given path, with header
    Args:
        data (list[dict[str, datetime  |  float]]): _description_
        path (Path | str): _description_
        fieldnames (Sequence[str] | None, optional): _description_. Defaults to None.
    """
    if fieldnames is None:
        fieldnames = tuple(data[0])
    path = Path(path).expanduser().resolve()
    with open(path, "w", encoding="utf8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect="unix")
        writer.writeheader()
        for row in data:
            # Have to manually convert datetime. Yuck
            for key in row:
                value = row[key]
                if isinstance(value, datetime):
                    row[key] = _convert_timestamp(value)
            writer.writerow(row)

def convert_to_dataframe(data: list[dict[str, Any]])->pd.DataFrame:
    first_row = data[0]
    column_names=list(first_row.keys())
    data_dict={}
    for column_name in column_names:
        column_data=get_column(data, column_name)
        data_dict[column_name] = column_data
    return_value=pd.DataFrame(data_dict)
    return return_value

def add_elapsed_time_column(data: pd.DataFrame) ->pd.DataFrame:
    time_start = min(data["timestamp_posix"])
    time_elapsed = data["timestamp_posix"] - time_start
    data["elapsed"]=time_elapsed
    return data




if __name__ == "__main__":
    pass
    # print ("mayo")
    # convert_to_dataframe()
