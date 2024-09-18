"""
Utility functions for plotting
"""

from dataclasses import dataclass
import itertools
import math
from pathlib import Path
from typing import Any, Collection, Literal, NamedTuple, Sequence
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys

# # TODO: Tidy this up
# sys.path.insert(0, R"./src/")

from test_info import ColumnInclusiveInterval, TestInfo
from util import simple_log


def grid_subplots(
    n: int,
    layout: Literal["constrained"] | None = "constrained",
    **kwargs,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """A wrapper around `plt.subplots()` to create the most square grid possible.

    Excess axes will be removed. So `grid_subplots(8)` will make a grid like

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
    if layout:
        kwargs["layout"] = layout
    fig, ax_ = plt.subplots(nrows=nrows, ncols=ncols, **kwargs)

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


@dataclass
class HighlightInterval:
    interval: ColumnInclusiveInterval
    color: str = "#ff0000"
    """Color to highlight in the plot"""
    label: str | None = None
    """What to put in the legend, or `None` to not add this highlight to legend"""
    linewidth: float = 2.0
    """matplotlib default = 1.0."""


def plot_one(
    data: pd.DataFrame,
    *,
    x_column_name: str,
    y_column_name: str,
    color: str = "#888888",
    linewidth: float = 0.5,
    highlights: Collection[HighlightInterval] | None = None,
    interval: ColumnInclusiveInterval | None = None,
    ax: plt.Axes | None = None,
    fig: plt.Figure | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    if (ax and not fig) or (fig and not ax):
        raise ValueError(f"If passing 'fig', must also pass 'ax'")
    if not ax:
        subplots_kwargs = {}
        subplots_kwargs["layout"] = "constrained"
        fig, [ax] = grid_subplots(1, **subplots_kwargs)
    highlights = list(highlights or [])

    if interval:
        data = interval.subset_data_frame(data)
    
    ax.plot(
        data[x_column_name], data[y_column_name], color=color, linewidth=linewidth,
    )

    # highlight
    needs_legend = False
    for highlight in highlights:
        highlight_data = data[
            (data[highlight.interval.name] <= highlight.interval.end)
            & (data[highlight.interval.name] >= highlight.interval.start)
        ]
        ax.plot(
            highlight_data[x_column_name],
            highlight_data[y_column_name],
            color=highlight.color,
            label=highlight.label,
            linewidth=highlight.linewidth,
        )
        if highlight.label is not None:
            needs_legend = True

    # Green dot for first point
    ax.scatter(
        [data[x_column_name].iloc[0]],
        [data[y_column_name].iloc[0]],
        color="#00ff00",
    )

    # Red dot for last point
    ax.scatter(
        [data[x_column_name].iloc[-1]],
        [data[y_column_name].iloc[-1]],
        color="#ff0000",
    )
    ax.set_title(f"y={y_column_name!r}, x={x_column_name!r}")

    if needs_legend:
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())

    return fig, ax


def plot_all(
    data: pd.DataFrame,
    *,
    prefer_x: Sequence[str] | None = None,
    prefer_y: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    color: str = "#888888",
    linewidth: float = 0.5,
    highlights: Collection[HighlightInterval] | None = None,
    interval: ColumnInclusiveInterval | None = None,
    fig: plt.Figure | None = None,
    axes: Sequence[plt.Axes] | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """Plot all numeric values in a `pd.DataFrame` against each other.

    `prefer_x` columns will be plotted as the x-axis, if possible.
    `prefer_y` columns will be plotted as the y-axis, if possible.
    `exclude` columns will be ignored.

    If given, `highlights` will apply the given highlighting to the plots.
    If given, `interval` will only plot the data within the given interval.
    """
    prefer_x = set(prefer_x or ())
    prefer_y = set(prefer_y or ())
    exclude = set(exclude or ())
    highlights = list(highlights or ())

    if interval:
        data = interval.subset_data_frame(data)

    numeric_data = data.select_dtypes(include="number")
    columns = tuple(x for x in numeric_data.columns if x not in exclude)
    pairs = list(itertools.combinations(columns, 2))

    n = len(pairs)

    if (fig and not axes) or (not fig and axes):
        raise ValueError(f"If passing 'fig', must also pass 'axes'.")

    if not fig:
        fig, axes = grid_subplots(n, layout="constrained")

    for index in range(n):
        ax = axes[index]
        x_column_name, y_column_name = pairs[index]
        
        # Do we need to flip columns?
        if x_column_name in prefer_y or y_column_name in prefer_x:
            x_column_name, y_column_name = y_column_name, x_column_name
        
        plot_one(
            data=numeric_data,
            x_column_name=x_column_name,
            y_column_name=y_column_name,
            fig=fig,
            ax=ax,
            highlights=highlights,
            interval=interval,
            color=color,
            linewidth=linewidth,
        )

    return fig, axes


def plot_all_test_info(
    test_info: TestInfo,
    *,
    highlights: Collection[HighlightInterval] | None = None,
    interval: ColumnInclusiveInterval | None = None,
    color: str = "#888888",
    linewidth: float = 0.5,
) -> tuple[plt.Figure, list[plt.Axes]]:
    fig, ax = plot_all(
        test_info.data,
        exclude=["timestamp_posix"],
        prefer_x=["elapsed"],
        prefer_y=["power"],
        highlights=highlights,
        interval=interval,
        color=color,
        linewidth=linewidth
    )
    fig.suptitle(f"{test_info.description}", fontsize=20)
    return fig, ax


def save_figure(
    fig: plt.Figure,
    test_info: TestInfo,
    relative_path: Path | str = "./figure.png",
    size_inches: tuple[float, float] = (16, 9),
    dpi: float = 300,
) -> Path:
    """Save the figure in the test's "figures" folder.

    With defaults, creates a 16inch by 9inch image at 300dpi,
    meaning the image is 4800x2700 pixels, which is quite large.

    Args:
        fig (plt.Figure): _description_
        test_info (TestInfo): _description_
        relative_path (Path | str, optional): _description_. Defaults to "./figure.png".
        size_inches (tuple[float, float], optional): _description_. Defaults to (16, 9).
        dpi (float | None, optional): _description_. Defaults to 200.

    Returns:
        Path: _description_
    """
    path = (test_info.figures_path / relative_path).expanduser().resolve()
    folder = path.parent
    if not folder.exists():
        simple_log.debug(f"Creating folder {folder}")
        folder.mkdir(parents=True, exist_ok=True)
    if size_inches:
        fig.set_size_inches(size_inches)
    if not dpi:
        dpi = fig.get_dpi()
    fig.savefig(path, dpi=dpi)
    simple_log.info(f"Saved figure to {path}")
    return path


if __name__ == "__main__":
    simple_log.set_level("DEBUG")
    from test_info import march_info, april_info, sept_info, sept_info2
    test_info = sept_info2
    fig, axes = plot_all_test_info(
        test_info=test_info,
        highlights=[
            HighlightInterval(
                ColumnInclusiveInterval(start=939, end=2945),
                color="#0000ff",
                label="EL_COL_0",
            ),
            HighlightInterval(
                ColumnInclusiveInterval(start=3120, end=5105),
                color="#00ff00",
                label="EL_COL_1",
            ),
            HighlightInterval(
                ColumnInclusiveInterval(start=5270, end=7260),
                color="#ff0000",
                label="EL_COL_2",
            ),
            HighlightInterval(
                ColumnInclusiveInterval(start=7420, end=9420),
                color="#cccc00",
                label="EL_COL_4",
            ),
        ],
    )

    save_figure(
        fig=fig,
        test_info=test_info,
        # dpi=200,
    )
    plt.show()
