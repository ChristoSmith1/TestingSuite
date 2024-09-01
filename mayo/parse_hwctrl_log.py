import datetime
from pathlib import Path
import re

sample = """
2,1,0,0,2,0,0,
# Antenna Controller (0): Antenna Control Unit (Actual Az, El, Commanded Az, El, Autotrack Status)
# Signal Strength (0): Antenna Control Unit Selected Rcvr
# Offline
# Pointing angles extracted from C:\FTP\GTprocedure.txt
# the scheduled pass parameters are
# On Off Moon,-1,0,176,37,18:32:00,18:35:00,00:00:00,18:46:00,0.000000,0.000000,0.000000,0.000000,1,0,unknown,unknown,SINGLE,FILE,C:\FTP\GTprocedure.txt,0,,-1,0.000000,0
2024 037 18:32:00, 139.978, 90.001,139.978, 90.001,0,  0.0,
# 037 18:32:00 - Sending configuration 176 to instruments
2024 037 18:32:01, 139.978, 90.001,139.978, 90.001,0,  0.0,
# 037 18:32:01 - Antenna Control Unit: Moving Antenna to IP (Az: 228.108 El:   3.553)
2024 037 18:32:02, 139.978, 90.001,139.978, 90.001,0,  0.0,
2024 037 18:32:03, 139.978, 90.001,139.978, 90.001,0,  0.0,
2024 037 18:32:04, 139.978, 89.915,139.978, 85.000,0,  0.0,
2024 037 18:32:05, 139.978, 89.761,139.978, 85.000,0,  0.0,
"""

regex_pattern = re.compile(
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

def parse_hwctrl_log_text(text: str) -> list[dict[str, datetime.datetime | float]]:
    rv = []
    for match in regex_pattern.finditer(text):
        # print (match)
        groupdict = match.groupdict()
        
        date_dt = datetime.datetime(
            year=int(groupdict["year"]),
            month=1,
            day=1,
        ) + datetime.timedelta(
            days = int(groupdict["day"]) - 1,
        )
        time = datetime.time.fromisoformat(groupdict["time"])
        timestamp = datetime.datetime.combine(date_dt.date(), time, tzinfo=datetime.UTC)
        rv.append({
            "timestamp": timestamp,
            "actual_azimuth": float(groupdict["actual_azimuth"]),
            "actual_elevation": float(groupdict["actual_elevation"]),
            "commanded_azimuth": float(groupdict["commanded_azimuth"]),
            "commanded_elevation": float(groupdict["commanded_elevation"]),
        })
    return rv

def parse_hwctrl_log_file(path: Path | str) -> list[dict[str, datetime.datetime | float]]:
    path = Path(path).expanduser().resolve()
    text = path.read_text(encoding="utf8")
    return parse_hwctrl_log_text(text)


if __name__ == "__main__":
    try:
        from rich.pretty import pprint as _rich_pprint
        from functools import partial
        pprint = partial(_rich_pprint, indent_guides=False, expand_all=True)
    except ImportError:
        from pprint import pprint
    results = parse_hwctrl_log_text(sample)
    results = parse_hwctrl_log_file("mayo/on_off_moon_176_D037T18_32_00.log")
    print(results)

    for index, result in enumerate(results, start=1):
        print(f"#{index} of {len(results)}")
        pprint(result)
        print()

    t = [x["timestamp"] for x in results]
    azimuth_error = [x["actual_azimuth"] - x["commanded_azimuth"] for x in results]
    elevation_error = [x["actual_elevation"] - x["commanded_elevation"] for x in results]