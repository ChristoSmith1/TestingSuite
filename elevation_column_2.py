import dataclasses
import datetime
import functools
import logging
import math
import itertools
from pathlib import Path
import sys
from typing import Literal

from matplotlib.offsetbox import AnchoredText
import matplotlib.patches as mpl_patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from g_over_t import add_elapsed_time_column


logger = logging.getLogger(__file__)

try:
    # import nonexistent_package
    import rich
    from rich import logging as rich_logging

    rich_handler = rich_logging.RichHandler(
        omit_repeated_times=False,
        log_time_format="%X",
        level=logging.DEBUG,
        show_path=True,
        rich_tracebacks=True,
    )
    rich_handler.set_name("console")
    logger.addHandler(rich_handler)
except ImportError:
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    screen_handler.setFormatter(formatter)
    screen_handler.set_name("console")
    logger.addHandler(screen_handler)
    rich = None
    rich_logging = None

logger.setLevel(logging.DEBUG)
logger.info("INFO MESSAGE")
logger.debug("DEBUG MESSAGE")
try:
    1/0
except Exception as exc:
    logger.error(exc, exc_info=exc)


@dataclasses.dataclass(unsafe_hash=True)
class TestInfo:
    band: Literal["X", "S"] | None = None
    description: str = ""
    csv_path: Path | None = None

    def __post_init__(self) -> None:
        # Read from CSV, if dataframe not given
        # self.csv_path = self.csv_path
        self._data: pd.DataFrame | None = None

    @property
    def data(self) -> pd.DataFrame:
        if self._data is not None:
            return self._data
        
        logger.info(f"Attempting to read data from {self.csv_path}")
        self._data = pd.read_csv(
            self.csv_path,
            parse_dates=["timestamp"]
        )

        # Add 'elapsed' column
        if (
            self._data is not None
            and "elapsed" not in self._data.columns
        ):
            logger.debug(f"Adding 'elapsed' column.")
            self._data = add_elapsed_time_column(self._data)

        return self._data

    @functools.lru_cache(1)
    def duration(self) -> datetime.timedelta:
        return max(self.data["timestamp"]) - min(self.data["timestamp"])
    
    def all_plots(
        self,
        *,
        ignore: tuple[str] = ("timestamp_posix", ),
        prefer_x: tuple[str] = ("elapsed", ),
        prefer_y: tuple[str] = ("power", ),
    ) -> tuple[plt.Figure, list[plt.Axes]]:
        numeric_data = self.data.select_dtypes(include="number")
        logger.debug(f"{numeric_data.columns=}")

        columns = [column for column in numeric_data.columns if column not in ignore]
        logger.debug(f"{columns=}")

        combos = list(itertools.combinations(columns, 2))
        logger.debug(f"{combos=}")
        in_order_combos = []
        for index, (col1, col2) in enumerate(combos):
            x_col, y_col = col1, col2
            if col1 in prefer_x:
                x_col, y_col = col1, col2
            elif col2 in prefer_x:
                x_col, y_col = col2, col1
            elif col1 in prefer_y:
                x_col, y_col = col2, col1
            elif col2 in prefer_y:
                x_col, y_col = col1, col2
            in_order_combos.append((x_col, y_col))
            logger.debug(f"{index=} {x_col=} {y_col=}")
        logger.debug(f"{in_order_combos=}")

        n = len(combos)
        nrows = math.floor(math.sqrt(n))
        ncols = math.ceil(n / nrows)

        logger.debug(f"{n=} {nrows=} {ncols=}")

        fig, raw_ax = plt.subplots(nrows, ncols, layout="constrained")
        logger.debug(f"{fig=} {raw_ax=}")
        fig.suptitle(f"{self.description}   {self.csv_path}\n({len(numeric_data):,} total points; {len(numeric_data):,} points shown)")

        ax_2d: list[list[plt.Axes]]
        if n == 1:
            ax_2d = [[raw_ax]]
        elif nrows == 1 or ncols == 1:
            ax_2d = [raw_ax]
        else:
            ax_2d = raw_ax

        index = 0
        flattened_axes: list[plt.Axes] = []
        for ax_row in ax_2d:
            for ax in ax_row:
                if index >= n:
                    logger.debug(f"Removing index {index}")
                    ax.remove()
                else:
                    x_col, y_col = in_order_combos[index]
                    logger.debug(f"{index=} {x_col=} {y_col=}")
                    ax.plot(numeric_data[x_col], numeric_data[y_col])
                    first_point = (numeric_data[x_col].iloc[0], numeric_data[y_col].iloc[0])
                    last_point = (numeric_data[x_col].iloc[-1], numeric_data[y_col].iloc[-1])
                    ax.scatter([first_point[0]], [first_point[1]], color="#00ff00")
                    ax.scatter([last_point[0]], [last_point[1]], color="#ff0000")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    text = "SAMPLE SAMPLE\nSAMPLE SAMPLE"
                    text = ""
                    text += f"Start: ({first_point[0]:.2f}, {first_point[1]:.2f})"
                    text += f"\nEnd: ({last_point[0]:.2f}, {last_point[1]:.2f})"

                    min_x = min(numeric_data[x_col])
                    max_x = max(numeric_data[x_col])
                    min_y = min(numeric_data[y_col])
                    max_y = max(numeric_data[y_col])

                    text += f"\n{x_col}: [{min_x:.2f} to {max_x:.2f}]"
                    text += f"\n{y_col}: [{min_y:.2f} to {max_y:.2f}]"
                    
                    handle = mpl_patches.Rectangle((0,0), 1, 1, fc="white", ec="white", lw=0, alpha=0)
                    ax.legend([handle], [text], loc="best", fancybox=True, handlelength=0, handletextpad=0, framealpha=0.7, fontsize='small')

                    # anchored_text = AnchoredText(text, loc="best")
                    # ax.add_artist(anchored_text)
                    flattened_axes.append(ax)
                index += 1

        return fig, flattened_axes


for _ in range(100):
    x_band_test = TestInfo(
        band="X",
        csv_path=Path(R"april21govert/combined_filtered_XBand_April.csv"),
        description="April 2024, X-Band (3 moon tracks, 1 el. col.)"
    )

s_band_test = TestInfo(
    band="S",
    csv_path=Path(R"april21govert/combined_filtered_SBand_March.csv"),
    description="March 2024, S-Band (2 moonn tracks, 2 el. col.)"
)

test = x_band_test
# test = s_band_test
logger.info(test)
logger.info(test.data.columns)
logger.info(f"{test.data.dtypes=}")


logger.info(f"{test.duration()=}")

fig, ax = test.all_plots()
logger.info("Calling plt.show(). Control shifting to matplotlib window . . .")
plt.show()
logger.info("Control returned from matplotlib window.")


# converted = pd.to_datetime(x_band_test.data["timestamp"])

pass


class ElevationColumn:
    def __init__(
        self,
        test_info: TestInfo,
        *,
        immediate: bool = True
    ) -> None:
        self.test_info = test_info
        self._columns: None | list = None
        if immediate:
            self._find_columns()

    @property
    def columns(self):
        if self._columns is None:
            self._find_columns()
        return self._columns

    def _find_columns(self) -> None:
        pass