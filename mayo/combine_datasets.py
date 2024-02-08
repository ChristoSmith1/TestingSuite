"""
Functions to combine datasets
"""
import csv
import datetime
from pathlib import Path
from typing import Literal, Sequence
import interpolator
import merge_test.merge_px6_powerdata as merge

def convert_timestamp_to_float(data: list[dict[str, datetime.datetime | float]]) -> None:
    """Convert the entries' `"timestamp"` values from `datetime.datetime` objects to `float` objects"""
    for item in data:
        timestamp_dt: datetime.datetime = item["timestamp"]
        timestamp_float: float = float(timestamp_dt.timestamp())
        item["timestamp_float"] = timestamp_float
        item["timestamp_dt"] = timestamp_dt
        del item["timestamp"]

def join_datasets(
    *,
    left_data: list[dict[str, datetime.datetime | float]],
    right_data: list[dict[str, datetime.datetime | float]],
    left_index_key: str = "timestamp_float",
    right_index_key: str = "timestamp_float",
    source: Literal["left", "right"] = "left",
    interpolation_method: Literal["linear", "cubic", "pchip"] = "linear",
):
    if source == "left":
        source_data = left_data
        source_index_key = left_index_key
        other_data = right_data
        other_index_key = right_index_key
    elif source == "right":
        source_data = right_data
        source_index_key = right_index_key
        other_data = left_data
        other_index_key = left_index_key
    else:
        raise ValueError(f"Invalid rouce {source!r}")
    other_interpolator = interpolator.Interpolator(
        data=other_data,
        x_key = other_index_key,
        extrapolate=False,
        method=interpolation_method,
    )

    rv = []
    for item in source_data:
        # print(f"")
        x: float = item[source_index_key]

        new_item = item.copy()
        for y_key in other_interpolator.y_keys:
            new_item[y_key] = other_interpolator(x, y_key)
        rv.append(new_item)
    return rv

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
    power_data = merge.read_power_file(merge.POWER_METER_CSV_PATH)
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

    result = join_datasets(
        left_data=pointing_data,
        right_data=power_data,
        source="right",
    )

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
        ]
    )

    # print(pointing_interpolator)

    import matplotlib.pyplot as plt
    
    timestamp_dt = merge.get_column(pointing_data, "timestamp_dt")
    azimuth = merge.get_column(pointing_data, "azimuth")
    elevation = merge.get_column(pointing_data, "elevation")

    plt.plot(timestamp_dt, azimuth, label="azimuth", color="red")
    plt.scatter(timestamp_dt, azimuth, label="azimuth", color="red")
    # plt.plot(timestamp_dt, elevation, label="elevation", color="blue")
    # plt.scatter(timestamp_dt, elevation, label="elevation", color="blue")
    plt.legend()
    plt.show()