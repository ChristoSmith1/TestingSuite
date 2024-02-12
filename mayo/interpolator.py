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
        extrapolate: bool = False
    ) -> None:
        self.x = list(x)
        self.y = list(y)
        self.min_x = min(self.x)
        self.max_x = max(self.x)
        self.extrapolate = extrapolate

    @functools.lru_cache(maxsize=None)
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
        extrapolate: bool = False
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
        if isinstance(self.xs[0], datetime.datetime):
            self.xs: list[datetime.datetime]
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
    
    min_x = -1.0
    max_x = 11.0
    count = 1000

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
        in np.linspace(min_x, max_x, count)
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
        in np.linspace(min_x, max_x, count)
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
        in np.linspace(min_x, max_x, count)
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