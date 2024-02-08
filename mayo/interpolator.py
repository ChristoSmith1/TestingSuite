"""
Functions related to interpolation

In general, valid interpolation types are `linear`, `cubic`, or `pchip`
"""

import datetime
import functools
from typing import Literal, Protocol, Sequence

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator


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
    ) -> None:
        self.x = list(x)
        self.y = list(y)

    @functools.lru_cache(maxsize=None)
    def __call__(self, x: float) -> float:
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
    ) -> None:
        self.x_key = x_key
        self.data = data
        self.y_keys = {
            key
            for key
            in data[0]
            if key != self.x_key
        }
        # if len(self.y_keys) == 1:
        #     self.y_key = next(iter(self.y_keys))
        # else:
        #     self.y_key = None
        
        self.method = method
        self.xs = [item[x_key] for item in data]

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
            )

    def _create_cubic_interpolators(self) -> None:
        for y_key in self.y_keys:
            ys = [item[y_key] for item in self.data]
            self._interpolators[y_key] = CubicSpline(
                x=self.xs,
                y=ys,
            )

    def _create_pchip_interpolators(self) -> None:
        for y_key in self.y_keys:
            ys = [item[y_key] for item in self.data]
            self._interpolators[y_key] = PchipInterpolator(
                x=self.xs,
                y=ys,
            )


if __name__ == "__main__":
    import math
    def make_data(
        minimum: float = 0.0,
        maximum: float = 10.0,
        count: int = 10,
    ) -> list[dict[str, float]]:
        rv = []
        for t in np.linspace(minimum, maximum, count):
            rv.append({
                "time": float(t),
                "sin": math.sin(t),
                "cos": math.cos(t),
            })
        return rv
    
    data = make_data()
    print(data)
    interpolator_linear = Interpolator(
        data=data,
        x_key="time",
        method="linear"
    )
    print(interpolator_linear)

    interpolator_cubic = Interpolator(
        data=data,
        x_key="time",
        method="cubic"
    )
    print(interpolator_cubic)

    interpolator_pchip = Interpolator(
        data=data,
        x_key="time",
        method="pchip"
    )
    print(interpolator_pchip)

    import matplotlib.pyplot as plt
    data_time = [item["time"] for item in data]
    data_sin = [item["sin"] for item in data]
    data_cos = [item["cos"] for item in data]

    interpolated_linear = [
        {
            "time": t,
            "sin": interpolator_linear(t, "sin"),
            "cos": interpolator_linear(t, "cos"),
        }
        for t
        in np.linspace(0.0, 10.0, 1000)
    ]
    interpolated_linear_time = [item["time"] for item in interpolated_linear]
    interpolated_linear_sin = [item["sin"] for item in interpolated_linear]
    interpolated_linear_cos = [item["cos"] for item in interpolated_linear]

    interpolated_cubic = [
        {
            "time": t,
            "sin": interpolator_cubic(t, "sin"),
            "cos": interpolator_cubic(t, "cos"),
        }
        for t
        in np.linspace(0.0, 10.0, 1000)
    ]
    interpolated_cubic_time = [item["time"] for item in interpolated_cubic]
    interpolated_cubic_sin = [item["sin"] for item in interpolated_cubic]
    interpolated_cubic_cos = [item["cos"] for item in interpolated_cubic]

    interpolated_pchip = [
        {
            "time": t,
            "sin": interpolator_pchip(t, "sin"),
            "cos": interpolator_pchip(t, "cos"),
        }
        for t
        in np.linspace(0.0, 10.0, 1000)
    ]
    interpolated_pchip_time = [item["time"] for item in interpolated_pchip]
    interpolated_pchip_sin = [item["sin"] for item in interpolated_pchip]
    interpolated_pchip_cos = [item["cos"] for item in interpolated_pchip]

    plt.scatter(data_time, data_sin, label="Actual points", color="black")
    plt.plot(interpolated_linear_time, interpolated_linear_sin, label="Linear interp", color="blue")
    plt.plot(interpolated_cubic_time, interpolated_cubic_sin, label="Cubic interp", color="red")
    plt.plot(interpolated_pchip_time, interpolated_pchip_sin, label="Pchip interp", color="green")
    plt.xlabel("time")
    plt.ylabel("value")
    plt.legend()
    plt.show()
    exit()



class Px6Interpolator:
    def __init__(
        self,
        data: list[dict],
        method: Literal["linear", "cubic", "pchip"] = "linear",
    ) -> None:
        self.data = data
        self.method = method


        self.datetimes: list[datetime.datetime] = [x["timestamp"] for x in self.data]
        self.azimuths: list[float] = [x["azimuth"] for x in self.data]
        self.elevations: list[float] = [x["elevation"] for x in self.data]

        self.timestamps: list[float] = [x.timestamp() for x in self.datetimes]

        self.first_datetime = min(self.datetimes)
        self.last_datetime = max(self.datetimes)

        self.first_timestamp = min(self.timestamps)
        self.last_timestamp = max(self.timestamps)

        self.azimuth_interpolator: _FloatInterpolator
        self.elevation_interpolator: _FloatInterpolator

        if self.method == "linear":
            self.azimuth_interpolator = LinearSpline(
                x=self.timestamps,
                y=self.azimuths,
            )
            self.elevation_interpolator = LinearSpline(
                x=self.timestamps,
                y=self.elevations,
            )
        elif self.method == "cubic":
            self.azimuth_interpolator = CubicSpline(
                x=self.timestamps,
                y=self.azimuths,
            )
            self.elevation_interpolator = CubicSpline(
                x=self.timestamps,
                y=self.elevations,
            )
        elif self.method == "pchip":
            self.azimuth_interpolator = PchipInterpolator(
                x=self.timestamps,
                y=self.azimuths,
            )
            self.elevation_interpolator = PchipInterpolator(
                x=self.timestamps,
                y=self.elevations,
            )
        else:
            raise ValueError(f"Invalid interpolation method: {self.method}")
    # <__main__.Px6Interpolator object at 0x00000232ED0DEBD0>
    # <__main__.Px6Interpolator(method=linear) object at 0x000002014D413B10>
    def __repr__(self) -> str:
        return f"<{self.__module__}.{self.__class__.__qualname__}(method={self.method}) object at 0x{id(self):0>16X}>"

    def __call__(self, datetime_: datetime.datetime) -> tuple[float, float]:
        
        if datetime_ < self.first_datetime or datetime_ > self.last_datetime:
            raise ValueError(f"Received timestamp {datetime_} [{t}] outside valid range [{self.first_timestamp}, {self.last_timestamp}]")

        t = datetime_.timestamp()

        az = self.azimuth_interpolator(t)
        el = self.elevation_interpolator(t)

        return az, el
    


if __name__ == "__main__":
    # PX6_FILE_PATH = "sample_px6.txt"
    import sys
    from pathlib import Path
    root_path = Path(__file__).expanduser().resolve().parent.parent
    sys.path.insert(0, root_path.__fspath__())
    PX6_FILE_PATH = "sample_data\moon_2024_01_06_px6.txt"
    from merge_test import merge_px6_powerdata
    data = merge_px6_powerdata.read_px6_file(PX6_FILE_PATH)
    print(data)

    linear_interpolater = Px6Interpolator(data, method="linear")
    cubic_interpolater = Px6Interpolator(data, method="cubic")
    pchip_interpolater = Px6Interpolator(data, method="pchip")
    # print(linear_interpolater)
    # # print(linear_interpolater(timestamp=datetime.datetime.now()))
    # print(f"{linear_interpolater.timestamps}")
    # print(f"{linear_interpolater.azimuths}")
    # print(f"{linear_interpolater.elevations}")
    # # now = datetime.datetime.now()
    # # print(now.timestamp())

    timestamps = []
    linear_azimuths = []
    linear_elevations = []
    cubic_azimuths = []
    cubic_elevations = []
    pchip_azimuths = []
    pchip_elevations = []
    for timestamp in np.linspace(
        linear_interpolater.first_timestamp,
        linear_interpolater.last_timestamp,
        10
    ):
        # time = start_time + datetime.timedelta(seconds=seconds)
        time = datetime.datetime.fromtimestamp(timestamp)
        linear_az, linear_el = linear_interpolater(time)
        cubic_az, cubic_el = cubic_interpolater(time)
        pchip_az, pchip_el = pchip_interpolater(time)

        timestamps.append(time.timestamp())
        linear_azimuths.append(linear_az)
        linear_elevations.append(linear_el)
        cubic_azimuths.append(cubic_az)
        cubic_elevations.append(cubic_el)
        pchip_azimuths.append(pchip_az)
        pchip_elevations.append(pchip_el)
        # print(f"{time}  {linear_az}  {linear_el}")

    actual_az = [x["azimuth"] for x in linear_interpolater.data]
    actual_el = [x["elevation"] for x in linear_interpolater.data]
    import matplotlib.pyplot as plt
    # plt.scatter(linear_interpolater.azimuths, linear_interpolater.elevations, label="actual", color="black")
    plt.plot(linear_azimuths, linear_elevations, label="linear")
    plt.plot(cubic_azimuths, cubic_elevations, label="cubic")
    # plt.plot(pchip_azimuths, pchip_elevations, label="pchip")
    plt.plot(actual_az, actual_el, label="px6")
    plt.xlabel("Azimuth")
    plt.ylabel("Elevation")
    plt.title("Moon sky position, 2024-01-06\nfrom Morehead, KY")
    plt.legend()
    plt.show()
    print(linear_interpolater)

    class MyClass:
        def __repr__(self) -> str:
            return f"<{self.__module__}.{self.__class__.__qualname__} object at 0x{id(self):0>16X}>"



    obj = MyClass()
    print(obj)




