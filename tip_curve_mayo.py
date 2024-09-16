from typing import overload
import matplotlib.pyplot as plt
import numpy as np

from g_over_t.test_info import TestInfo, ElapsedInterval, march_info
from g_over_t.util import plots



# SOME CONSTANTS:
T_M = 255.0
"""Mean Effective Radiating Temperature of Atmosphere, in K. Always assumed to be 255K"""

T_CMB = 2.725
"""Cosmic Microwave Background Temperature, in K. Always assumed to be 2.725K"""


def L(theta: float | np.ndarray) -> float | np.ndarray:
    """Atmospheric Loss Factor L(theta). Unitless
    
    NOTE: `theta` MUST be in RADIANS!"""
    return 10 ** (A(theta) / 10)


def T_op(
    T_moon: float,
    Y: float,
    theta: float
) ->  float:
    """T_op = System Operating Noise Temperature [K]

    See https://scholarworks.moreheadstate.edu/cgi/viewcontent.cgi?article=1943&context=msu_theses_dissertations
    equation 4.10

    This paper: https://tmo.jpl.nasa.gov/progress_report/42-166/166C.pdf
    Suggests T_moon = 135.9 for S-Band and 189.1 for X-Band. IDK if that's right.

    Args:
        T_moon (float): Unit: K. Likely 135.9 for S-Band and 189.1 for X-Band
        Y (float): Y-factor. Dimensionless?
        theta (np.ndarray | float): elevation IN RADIANS
    """    

    numerator = T_moon / L(theta) - Y * T_CMB / L(theta)
    denominator = Y - 1
    return numerator / denominator

def A(
    elevation_radians: np.ndarray,
    a_zen: float = 1.0
) -> np.ndarray:
    """Calculate atmospheric attenuation `A(theta)`

    `elevation_radians` in RADIANS
    `a_zen` = Zenith Atmospheric Attenuation [dB]

    NOTE: elevation must be in RADIANS!
    """
    return a_zen / np.sin(elevation_radians)


def tip_curve(
    test_info: TestInfo,
    interval: ElapsedInterval,
    t_op: float,
    p_off: float,
):
    """Calulate the tip curve

    Equation is T(elevation) = T_op * 10 ^ ((P(elevation) - P_off) / 10)
    """

    data = interval.subset_df(test_info.data)
    print(f"{len(data) = }")

    fig, axes = plots.grid_subplots(3)

    power_array = np.array(data["power"], dtype=np.float64)
    elevation_array_degrees = np.array(data["elevation"], dtype=np.float64)
    elevation_array_radians = np.radians(elevation_array_degrees)

    ax0 = axes[0]
    # x_col = "elevation (radians)"
    # y_col = "power"
    ax0.plot(elevation_array_degrees, power_array)
    ax0.set_xlabel(f"Elevation (degrees)")
    ax0.set_ylabel(f"Power (dBm)")

    # # p_off = calculate_p_off(test_info)
    # p_off = -40.52  # Power (in dBm)
    # # t_op = calculate_t_op(test_info)
    # t_op = 67.012

    t = t_op * 10 ** ((power_array - p_off) / 10)

    t = T_op(
        theta=elevation_array_radians,
        T_moon = 135.9,
        Y = 5.2
    )

    ax1 = axes[1]
    ax1.plot(elevation_array_degrees, t)
    ax1.set_xlabel(f"Elevation (degrees)")
    ax1.set_ylabel(f"Temperature (K)")
    ax1.set_title(f"Using t_op={t_op:0.5f} p_off={p_off:0.5f}")

    ax2 = axes[2]
    ax2.plot(elevation_array_degrees, 1 / np.sin(elevation_array_radians))
    ax2.set_title("Relative air column mass")
    ax2.set_ylabel("Relative air column mass (90deg elevation = 1.0)")
    ax2.set_xlabel(f"Elevation (degrees)")

    fig.suptitle(test_info.description)
    plt.show()


    pass

# def calculate_t_op(
#     test_info: TestInfo,
# ) -> float:
#     pass

# def calculate_p_off(
#     test_info: TestInfo,
# ) -> float:
#     pass


if __name__ == "__main__":
    interval_1=ElapsedInterval(1877, 2898)
    interval_2=ElapsedInterval(2982, 3972)
    interval = interval_2

    # plots.plot_all_test_info(
    #     march_info,
    #     show=True,
    #     highlights=[
    #         plots.HighlightInterval(
    #             start=interval.start,
    #             end=interval.end,
    #             column_name=interval.column,
    #             color="orange"
    #         )
    #     ]
    # )
    tip = tip_curve(
        test_info=march_info,
        interval = interval,
        t_op=67.012,
        p_off=-40.52,
    )
