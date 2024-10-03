import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, least_squares
from test_info import sept_info,april_info,sept_info2,all_tests
from tip_curve import tip_curve

import random

def test(theta, c1, c2, c3):
    return c1 + c2*(90-theta)+c3*(90-theta)**2
    # return a * (1 - np.exp(b * np.arcsin(np.degrees(x))))


# x_min = 5
# x_max = 80
# size = 1000
# xs = np.linspace(x_min, x_max, size)

for test_info in all_tests():
    elevation,temperature = tip_curve(test_info)

    # ys_observed = (
    #     test(xs, *[a_actual, b_actual, c_actual])
    #     + np.random.normal(size=size) / 10
    # )


    popt, pcov = curve_fit(
        test,
        elevation,
        temperature,
        # method="lm",
        # p0=[10, 0.02,  -10],
        # bounds=(
        #     np.array([0, 0, 0]),
        #     np.array([5, .1, 10])

        # ),
        maxfev=5000,
    )


    # popt, pcov = least_squares(
    #     test,
    #     xs,
    #     ys_observed,
    #     method="lm",
    #     # p0=[10, 0.1,  -10],
    # )


    print(f"{popt=}")
    print(f"{pcov=}")


    ys_fit = test(elevation, *popt)


    fig, ax = plt.subplots()
    ax: plt.Axes

    ax.set_title(test_info.description)
    ax.plot(
        elevation,
        temperature,
        label=f"observed",
        marker="+",
        color = "#cccccc",
    )
    ax.plot(
        elevation,
        ys_fit,
        label=f"fit",
        color="blue",
        linewidth=2,
    )
    ax.legend()
    plt.show()


    print(curve_fit)