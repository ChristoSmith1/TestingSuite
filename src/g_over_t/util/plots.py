"""
Utility functions for plotting
"""

import itertools
import math
from typing import Collection, NamedTuple, Sequence
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys

# TODO: Tidy this up
sys.path.insert(0, R"./src/")

from g_over_t.test_info import TestInfo


def grid_subplots(
    n: int, 
    layout: str="constrained",
    **kwargs,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """A wrapper around `plt.subplots()` to create the most square grid possible.
    
    Remaining axes will be removed. So `grid_subplots(8)` will make a grid like
    
    ```
    +---+---+---+
    | 0 | 1 | 2 |
    +---+---+---+
    | 3 | 4 | 5 |
    +---+---+---+
    | 6 | 7 |   |
    +---+---+---+
    ```
    """
    nrows = round(math.sqrt(n))
    ncols = math.ceil(n / nrows)

    fig, ax_ = plt.subplots(nrows=nrows, ncols=ncols, layout="constrained", **kwargs)

    axes: list[plt.Axes] = []
    if n == 1:
        axes = [ax_]
    elif nrows == 1 or ncols == 1:
        axes = list(ax_)
    else:
        for row in ax_:
            axes.extend(row)

    if nrows * ncols > n:
        for index in range(n, nrows * ncols):
            print(f"Removing index {index}")
            axes[index].remove()
        
    return fig, axes


class HighlightInterval(NamedTuple):
    start: float
    end: float
    column_name: str
    color: str
    label: str | None = None


def plot_all(
    data: pd.DataFrame,
    *,
    prefer_x: Sequence[str] | None = None,
    prefer_y: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    highlights: Collection[HighlightInterval] | None = None
) -> tuple[plt.Figure, list[plt.Axes]]:
    """Plot all numeric values in a `pd.DataFrame` against each other.
    
    `prefer_x` columns will be plotted as the x-axis, if possible.
    `prefer_y` columns will be plotted as the y-axis, if possible.
    `exclude` columns will be ignored.
    """
    prefer_x = set(prefer_x or ())
    prefer_y = set(prefer_y or ())
    exclude = set(exclude or ())
    highlights = list(highlights or [])
    numeric_data = data.select_dtypes(include='number')
    columns = tuple(x for x in numeric_data.columns if x not in exclude)
    pairs = list(itertools.combinations(columns, 2))

    n = len(pairs)

    fig, axes = grid_subplots(n, layout="constrained")

    for index in range(n):
        ax = axes[index]
        x_col, y_col = pairs[index]
        if x_col in prefer_y or y_col in prefer_x:
            x_col, y_col = y_col, x_col
        ax.plot(numeric_data[x_col], numeric_data[y_col], color="#888888", linewidth=0.5)

        needs_legend = False
        # highlight
        for highlight in highlights:
            highlight_data = numeric_data[
                (numeric_data[highlight.column_name] <= highlight.end)
                & (numeric_data[highlight.column_name] >= highlight.start)
            ]
            ax.plot(highlight_data[x_col], highlight_data[y_col], color=highlight.color, label=highlight.label, linewidth=2)
            if highlight.label is not None:
                needs_legend = True

        # Green dot for first point
        ax.scatter([numeric_data[x_col].iloc[0]], [numeric_data[y_col].iloc[0]], color="#00ff00")

        # Red dot for last point
        ax.scatter([numeric_data[x_col].iloc[-1]], [numeric_data[y_col].iloc[-1]], color="#ff0000")
        ax.set_title(f"y={y_col!r}, x={x_col!r}")

        if needs_legend:
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys())
    
    return fig, axes


def plot_all_test_info(
    test_info: TestInfo,
    *,
    highlights: Collection[HighlightInterval] | None = None
) -> tuple[plt.Figure, list[plt.Axes]]:
    fig, ax = plot_all(
        test_info.data,
        exclude=["timestamp_posix"],
        prefer_x=["elapsed"],
        prefer_y=["power"],
        highlights = highlights,
    )
    fig.suptitle(f"{test_info.description}", fontsize=20)
    return fig, ax


if __name__ == "__main__":
    from g_over_t.test_info import march_info, april_info
    plot_all_test_info(
        april_info,
        highlights = [
            HighlightInterval(start=1140-55, end=1140, column_name="elapsed", color="#00bb00", label="ON"),
            HighlightInterval(start=1140+10, end=1140+10+55, column_name="elapsed", color="#bb0000", label="OFF"),

            HighlightInterval(start=1380-55, end=1380, column_name="elapsed", color="#00bb00", label="ON"),
            HighlightInterval(start=1380+10, end=1380+10+55, column_name="elapsed", color="#bb0000", label="OFF"),

            HighlightInterval(start=1618-55, end=1618, column_name="elapsed", color="#00bb00", label="ON"),
            HighlightInterval(start=1618+10, end=1618+10+55, column_name="elapsed", color="#bb0000", label="OFF"),

            HighlightInterval(start=1810, end=3840, column_name="elapsed", color="#0000ff", label="EL_COL"),
        ]
    )
    # plot_all(
    #     march_info.data,
    #     exclude=["timestamp_posix"],
    #     prefer_x=["elapsed"],
    #     prefer_y=["power"],
    # )
    plt.show()