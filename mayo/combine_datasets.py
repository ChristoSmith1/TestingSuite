"""
Functions to combine datasets
"""
import datetime
import interpolator
import merge_test.merge_px6_powerdata as merge

def convert_timestamp_to_float(data: list[dict[str, datetime.datetime | float]]) -> None:
    """Convert the entries' `"timestamp"` values from `datetime.datetime` objects to `float` objects"""
    for item in data:
        timestamp_dt: datetime.datetime = item["timestamp"]
        timestamp_float: float = float(timestamp_dt.timestamp())
        item["timestamp_float"] = timestamp_float
        item["timestamp_dt"] = timestamp_dt

if __name__ == "__main__":
    power_data = merge.read_power_file(merge.POWER_METER_CSV_PATH)
    convert_timestamp_to_float(power_data)

    pointing_data = merge.read_px6_file(r"mayo/sample_px6.txt")
    print(pointing_data)
    convert_timestamp_to_float(pointing_data)

    pointing_interpolator = interpolator.Interpolator(
        data=pointing_data,
        x_key="timestamp_float",
        method="linear",
        extrapolate=False,
    )

    print(pointing_interpolator)

    import matplotlib.pyplot as plt
    
    t = merge.get_column(pointing_data, "timestamp_dt")
    az = merge.get_column(pointing_data, "azimuth")
    el = merge.get_column(pointing_data, "elevation")

    plt.plot(t, az)
    plt.scatter(t, az)
    plt.show()