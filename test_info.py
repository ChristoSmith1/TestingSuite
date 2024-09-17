import dataclasses
import functools
import json
from pathlib import Path
import time
from typing import Any, Generator, Literal, NamedTuple

import pandas as pd

from util import simple_log
from util.simple_log import logger
import g_over_t

# class IndexInterval(NamedTuple):
#     """Interval of indexes, INCLUSIVE"""
#     start: int
#     end: int


ROOT_TESTS_PATH = Path(__file__).parent


@functools.total_ordering
@dataclasses.dataclass
class ColumnInclusiveInterval:
    """An arbitrary inclusive interval, usually to be applied
    to a specific column of a `pd.DataFrame`, usually the "elapsed" column."""
    start: float
    end: float
    name: str = "elapsed"

    def __iter__(self):
        return iter((self.start, self.end))
    
    def __lt__(self, other: "ColumnInclusiveInterval") -> bool:
        if isinstance(other, ColumnInclusiveInterval):
            return tuple(self) < tuple(other)
        return NotImplemented
    
    def __eq__(self, other: "ColumnInclusiveInterval") -> bool:
        if isinstance(other, ColumnInclusiveInterval):
            return tuple(self) == tuple(other)
        return NotImplemented

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> "ColumnInclusiveInterval":
        return ColumnInclusiveInterval(**dict_)
    
    @classmethod
    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def __str__(self) -> str:
        return f"{self.name!r} in [{self.start}, {self.end}]"
    
    def __contains__(self, value: float) -> bool:
        return self.start <= value <= self.end
    
    def permissive_union(self, other: "ColumnInclusiveInterval") -> "ColumnInclusiveInterval":
        """Allows union of non-overlapping intervals. So `[10, 20]` and `[30, 40]` will give `[10, 40]`"""
        assert self.name == other.name
        return ColumnInclusiveInterval(
            start = min(self.start, other.start),
            end = max(self.end, other.end),
            name = self.name
        )

    def strict_union(self, other: "ColumnInclusiveInterval") -> "ColumnInclusiveInterval":
        assert self.overlaps(other)
        assert self.name == other.name
        return ColumnInclusiveInterval(
            start = min(self.start, other.start),
            end = max(self.end, other.end),
            name = self.name
        )
    
    def intersect(self, other: "ColumnInclusiveInterval") -> "ColumnInclusiveInterval":
        assert self.overlaps(other)
        assert self.name == other.name
        return ColumnInclusiveInterval(
            start = max(self.start, other.start),
            end = min(self.end, other.end),
            name = self.name
        )

    def overlaps(self, other: "ColumnInclusiveInterval") -> None:
        """Determine if two intervals overlap"""
        return (
            self.start in other
            or self.end in other
            or other.start in self
            or other.end in self
        )

    def subset_data_frame(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a subset (a view) of the given data frame where `start <= data[name] <= end`"""
        assert self.name in data.columns
        return data[
            (data[self.name] >= self.start)
            & (data[self.name] <= self.end)
        ]


@functools.total_ordering
@dataclasses.dataclass
class OnOffMoonPair:
    """A pair of intervals representing a single on/off observation"""
    on: ColumnInclusiveInterval
    off: ColumnInclusiveInterval

    def __post_init__(self) -> None:
        if isinstance(self.on, dict):
            self.on = ColumnInclusiveInterval(**self.on)
        if isinstance(self.off, dict):
            self.off = ColumnInclusiveInterval(**self.off)

    def total_interval(self) -> ColumnInclusiveInterval:
        """Total interval of the on/off pair"""
        return self.on.permissive_union(self.off)

    def __iter__(self):
        return iter((self.on, self.off))

    def __lt__(self, other: "OnOffMoonPair") -> bool:
        if isinstance(other, OnOffMoonPair):
            return tuple(self) < tuple(other)
        return NotImplemented

    def __eq__(self, other: "OnOffMoonPair") -> bool:
        if isinstance(other, OnOffMoonPair):
            return tuple(self) == tuple(other)
        return NotImplemented

@dataclasses.dataclass
class AnalysisResults:
    elevation_columns: list[ColumnInclusiveInterval] | None = dataclasses.field(default=None)
    """Identified elevation columns"""

    on_off_moon_pairs: list[OnOffMoonPair] | None = dataclasses.field(default=None)
    """Identified pairs"""

    def elevation_column_interval(self) -> ColumnInclusiveInterval | None:
        """Total interval of all elevation columns"""
        if not self.elevation_columns:
            return None
        rv = self.elevation_columns[0]
        for column in self.elevation_columns[1 : ]:
            rv = rv.permissive_union(column)
        return rv

    def __post_init__(self) -> None:
        if self.elevation_columns and isinstance(self.elevation_columns[0], dict):
            self.elevation_columns = [
                ColumnInclusiveInterval(**dict_)
                for dict_
                in self.elevation_columns
            ]

        if self.on_off_moon_pairs and isinstance(self.on_off_moon_pairs[0], dict):
            self.on_off_moon_pairs = [
                OnOffMoonPair(**dict_)
                for dict_
                in self.on_off_moon_pairs
            ]
    

@dataclasses.dataclass
class TestInfo:
    """Metadata about a given test"""
    description: str = ""
    power_meter_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    px6_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    hwctrl_log_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    combined_data_csv_relative_path: Path | None = dataclasses.field(
        default=Path("analysis_data/data.csv"),
        repr=False,
    )
    parameters_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    pointing_data_source: Literal["hwctrl", "px6"] = "hwctrl"
    # test_folder_path: Path | None = dataclasses.field(default=None, repr=False)
    analysis_results: AnalysisResults | None = dataclasses.field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.power_meter_data_relative_path is not None:
            self.power_meter_data_relative_path = Path(self.power_meter_data_relative_path)
        if self.px6_data_relative_path is not None:
            self.px6_data_relative_path = Path(self.px6_data_relative_path)
        if self.hwctrl_log_data_relative_path is not None:
            self.hwctrl_log_data_relative_path = Path(self.hwctrl_log_data_relative_path)
            self.combined_data_csv_relative_path = Path("./analysis_data/data.csv")
        if self.combined_data_csv_relative_path is not None:
            self.combined_data_csv_relative_path = Path(self.combined_data_csv_relative_path)
        if self.parameters_relative_path is not None:
            self.parameters_relative_path = Path(self.parameters_relative_path)
        
        if isinstance(self.analysis_results, dict):
            self.analysis_results = AnalysisResults(**self.analysis_results)
        elif self.analysis_results is None:
            self.analysis_results = AnalysisResults()

        self.pointing_data_source = str(self.pointing_data_source).strip().casefold()

        self._data: pd.DataFrame | None = None

    @property
    def elevation_column_data_list(self) -> list[pd.DataFrame]:
        rv = []
        for elevation_column in self.analysis_results.elevation_columns:
            rv.append(elevation_column.subset_data_frame(self.data))
        return rv 

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._load_data()
        return self._data
        
    @data.setter
    def data(self, value: pd.DataFrame) -> None:
        self._data = value

    def _get_power_data(self) -> list[dict[str, Any]]:
        """Get power data as a `list[dict[str, Any]]`"""
        power_meter_path = self.test_folder_path / self.power_meter_data_relative_path
        if not power_meter_path:
            error_message = f"'power_meter_data_path' not specified."
            raise ValueError(error_message)
        elif not power_meter_path.exists():
            error_message = f"'power_meter_data_path' file does not exist: {power_meter_path}"
            raise FileNotFoundError(error_message)

        logger.debug(f"Reading power data from {power_meter_path}")        
        return g_over_t.read_power_file(power_meter_path)

    def _get_pointing_data(self) -> list[dict[str, Any]]:
        """Get pointing data as a `list[dict[str, Any]]`"""
        if self.pointing_data_source == "px6":
            path = self.test_folder_path / self.px6_data_relative_path
            logger.debug(f"Loading pointing data from PX6 file: {path}")
            return g_over_t.read_px6_file(path)
        elif self.pointing_data_source == "hwctrl":
            path = self.test_folder_path / self.hwctrl_log_data_relative_path
            logger.debug(f"Loading pointing data from HWCTRL file: {path}")
            return g_over_t.parse_hwctrl_log_file(path)
        else:
            message = f"Invalid 'pointing_data_source': {self.pointing_data_source!r}. Valid choices are 'hwctrl' or 'px6"
            logger.error(message)
            raise ValueError(message)


    def _create_combined_data(self) -> None:
        """Create the combined data from raw files. Does a few things:

        1. Loads the power data and pointing data (PX6 or HWCTRL) from file
        2. Merges them with the interpolator
        3. Creates a DataFrame
        4. Adds the "elapsed" column
        5. Saves that as a CSV, clobbering any existing file
        """
        logger.debug(f"Building data set from raw files")
        self._data = None

        power_data = self._get_power_data()
        logger.debug(f"Read {len(power_data):,} power datapoints from {power_data[0]['timestamp']} to {power_data[-1]['timestamp']}")

        position_data = self._get_pointing_data()
        logger.debug(f"Loaded pointing data. {len(position_data):,} data points from {position_data[0]['timestamp']} to {position_data[-1]['timestamp']}")

        logger.info(f"Beginning data merge. Might take awhile, might not.")
        merge_start_time = time.monotonic()
        combined_data = g_over_t.combine_power_position(
            power_data=power_data,
            position_data=position_data
        )
        merge_time = time.monotonic() - merge_start_time
        logger.info(f"Finished data merge in {merge_time:.3f} seconds. {len(combined_data):,} data points in combined.")

        # Filter the NANs
        combined_data = g_over_t.filter_out_nan(combined_data)
        self._data = g_over_t.convert_to_dataframe(combined_data)

        logger.info(f"After filtering NAN rows, there are {len(combined_data):,} data points in combined")
        logger.debug(f"First data point:")
        logger.debug(self._data.iloc[0])
        logger.debug(f"Last data point:")
        logger.debug(self._data.iloc[-1])

        self._data = g_over_t.convert_to_dataframe(combined_data)

        # Go ahead and add the elapsed column automatically
        if "elapsed" not in self._data.columns:
            logger.debug(f"Adding 'elapsed' column")
            self._data = g_over_t.add_elapsed_time_column(self._data)

        # Finally, write that to the CSV
        self.write_data()

    def _load_data(self) -> None:
        """Load the combined data into `self._data` as a Pandas DataFrame.
        
        Will read the existing CSV, if it exists. Otherwise, will create from raw data.
        """
        logger.info(f"DataFrame not yet loaded. Attempting to load now.")
        # Read from the CSV, if there is one
        if self.combined_data_csv_relative_path:
            combined_data_csv_path = self.test_folder_path / self.combined_data_csv_relative_path
            if combined_data_csv_path.exists():
                logger.debug(f"Loading from existing CSV at '{combined_data_csv_path}'")
                self._data = pd.read_csv(
                    combined_data_csv_path,
                    parse_dates=["timestamp"],
                )
                return
        
        # Otherwise, create from the raw files
        self._create_combined_data()

    @classmethod
    def init(cls, path: Path | str) -> None:
        """Init an empty json"""
        path = Path(path).expanduser().resolve()
        logger.info(f"Creating empty json in folder {path}")
        path.mkdir(parents=True, exist_ok=True)
        info = TestInfo()
        info.write_parameters(path / "parameters.json")
        raw_data_folder_path = path / "raw_data"
        raw_data_folder_path.mkdir(parents=True, exist_ok=True)

    def write_data(self, path: Path | str | None = None) -> None:
        if not path and not self.combined_data_csv_relative_path:
            message = f"Cannot write data without specifying a CSV path."
            logger.error(message)
            raise ValueError(message)

        if path:
            path = Path(path).expanduser().resolve()
        else:
            path = (self.test_folder_path / self.combined_data_csv_relative_path).expanduser().resolve()
        
        logger.debug(f"Attempting to save data to {path}")
        if not path.parent.exists():
            logger.debug(f"Creating folder {path.parent}")
            path.parent.mkdir(parents=True, exist_ok=True)
        self.data.to_csv(path, index=False)
        logger.info(f"Successfully saved combined data to {path}")

    def _get_hwctrl_data(self):
        logger.debug(f"Attempting to get HWCTRL log data.")
        if not self.hwctrl_log_data_relative_path:
            logger.debug(f"No HWCTRL log specified in {self.parameters_relative_path}")
            return None
        hwctrl_log_path = self.test_folder_path / self.hwctrl_log_data_relative_path
        logger.debug(f"Attempting to read {hwctrl_log_path}")

        if not hwctrl_log_path.exists():
            logger.warning(f"HWCTRL log file path is given, but file does not exist: {hwctrl_log_path}")
            return None
        return g_over_t.parse_hwctrl_log_file(hwctrl_log_path)
        
    def _get_px6_data(self):
        logger.debug(f"Attempting to get PX6 data.")
        if not self.px6_data_relative_path:
            logger.debug(f"No PX6 data file specified in {self.parameters_relative_path}")
            return None
        px6_meter_path = self.test_folder_path / self.px6_data_relative_path
        logger.debug(f"Attempting to read {px6_meter_path}")

        if not px6_meter_path.exists():
            logger.warning(f"PX6 log file path is given, but file does not exist: {px6_meter_path}")
            return None
        return g_over_t.read_px6_file(px6_meter_path)

    @property
    def test_folder_path(self) -> Path | None:
        if self.parameters_relative_path:
            return Path(self.parameters_relative_path).parent.expanduser().resolve()
        else:
            return None

    @property
    def figures_path(self) -> Path | None:
        """Path to the "figures" folder. Will be `{test_folder_path}/figures/` """
        if self.test_folder_path:
            return self.test_folder_path / "figures"
        else:
            return None

    def write_parameters(self, path: Path | str | None = None) -> None:
        path = path or self.parameters_relative_path
        if not path:
            raise ValueError(f"Cannot save without a file path.")
        dictionary = dataclasses.asdict(self)
        json_text = json.dumps(dictionary, default=str, indent=4)
        logger.debug(f"Writing to '{path}'")
        path.write_text(json_text, encoding="utf-8")


    @classmethod
    def load(cls, path: Path | str) -> "TestInfo":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"The file/folder does not exist: {path}")
        if path.is_dir():
            json_paths = list(path.glob("*.json"))
            if len(json_paths) == 0:
                raise FileNotFoundError(f"No *.json files found in {path}")
            elif len(json_paths) > 1:
                message = f"Multiple *.json files exist in {path}: "
                message += f"[{', '.join((json_path.name for json_path in json_paths))}]"
                raise RuntimeError(message)
            else:
                return cls.load(json_paths[0])
        else:
            logger.debug(f"Loading metadata from '{path}'")
            dictionary = json.loads(path.read_text())
            dictionary["parameters_relative_path"] = path
            rv = TestInfo(**dictionary)
            logger.debug(f"Loaded metadata for test folder '{rv.test_folder_path}'")
            return rv

march_info = TestInfo.load("tests/2024-03-26")
"""Test from MARCH 2024"""

april_info = TestInfo.load("tests/2024-04-22")
"""Test from APRIL 2024"""

sept_info = TestInfo.load("tests/2024-09-05")
"""Test 1 from September 2024"""

sept_info2 = TestInfo.load("tests/2024-09-05-2")
"""Test 2 from September 2024"""


def all_test_paths() -> list[Path]:
    """"""
    return sorted(ROOT_TESTS_PATH.rglob("parameters.json"))


def all_tests() -> Generator[TestInfo, None, None]:
    for path in all_test_paths():
        yield TestInfo.load(path)


if __name__ == "__main__":
    # logger.setLevel("INFO")
    # meta_data = TestInfo.load(R"tests\2024-04-22")
    # logger.info(f"{meta_data=}")
    # logger.info(f"{meta_data.data}")
    # meta_data._create_combined_data()
    # meta_data.analysis_results.elevation_columns = [IndexInterval(0, 200)]
    # meta_data.write_parameters()

    # TestInfo.init(R"tests\sample")

    info = TestInfo.load("tests/2024-09-05-2")
    logger.info(info.data)

    d = dataclasses.asdict(info)

    from rich.pretty import pprint

    pprint(d)
    
    print(info.analysis_results.on_off_moon_pairs)

    pair = OnOffMoonPair(
        on=ColumnInclusiveInterval(100, 200),
        off=ColumnInclusiveInterval(250, 350),
    )
    pair2 = OnOffMoonPair(**{'on': {'start': 100, 'end': 200, 'name': 'elapsed'}, 'off': {'start': 250, 'end': 350, 'name': 'elapsed'}})
    print(f"{pair=}")
    print(f"{pair2=}")
    print(dataclasses.asdict(pair))
    # results = AnalysisResults(elevation_columns= [{'start': 100.0, 'end': 200.0, 'name': 'elapsed'}])

    print(info.analysis_results)

    simple_log.set_level("WARNING")
    tests = list(all_tests())

    for index, test in enumerate(tests):
        length = len(test.data)
        print(f"{index=} {test.parameters_relative_path} {length=}")

    # print(f"{results = }")

    info = TestInfo.load("tests/2024-09-11/parameters.json")
    print(f"{len(info.data) = }")
    info.write_parameters()