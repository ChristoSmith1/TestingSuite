"""
Functions to combine datasets
"""
import csv
import datetime
from pathlib import Path
from typing import Literal, Sequence
import merge_test.merge_px6_powerdata as merge

def convert_timestamp_to_float(data: list[dict[str, datetime.datetime | float]]) -> None:
    """Convert the entries' `"timestamp"` values from `datetime.datetime` objects to `float` objects"""
    for item in data:
        timestamp_dt: datetime.datetime = item["timestamp"]
        timestamp_float: float = float(timestamp_dt.timestamp())
        item["timestamp_float"] = timestamp_float
        item["timestamp_dt"] = timestamp_dt
        del item["timestamp"]

def convert_timestamp(
    timestamp: datetime.datetime,
    coerce_naive_to_utc: bool = True,
    sep: str = "T",
) -> str:
    if coerce_naive_to_utc and timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.UTC)
    return timestamp.isoformat(sep=sep,timespec="microseconds")

def write_csv(
    data: list[dict[str, datetime.datetime | float]],
    path: Path | str,
    fieldnames: Sequence[str] | None = None,
):
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
                if isinstance(value, datetime.datetime):
                    # value = value.replace(tzinfo=datetime.UTC)
                    # value_string = value.isoformat(sep="T")
                    row[key] = convert_timestamp(value)
            writer.writerow(row)


if __name__ == "__main__":
    power_data = merge.read_power_file(merge.POWER_METER_CSV_PATH_3)
    convert_timestamp_to_float(power_data)

    pointing_data = merge.read_px6_file(r"mayo/sample_px6.txt")
    print(pointing_data)
    convert_timestamp_to_float(pointing_data)

    # pointing_interpolator = interpolator.Interpolator(
    #     data=pointing_data,
    #     x_key="timestamp_float",
    #     method="cubic",
    #     extrapolate=False,
    # )
    result = power_data

    for index, item in enumerate(result):
        print(f"{index}  {item}")

    write_csv(
        data=result,
        path = Path("./mayo/output.csv"),
        fieldnames=[
            "power",
            "timestamp_float",
            "timestamp_dt",
            "elevation",
            "azimuth",
        ],
    )

    # print(pointing_interpolator)