import dataclasses
import json
from pathlib import Path
import time
from typing import Any, Literal, NamedTuple

import pandas as pd

from util.simple_log import logger
import g_over_t

class IndexInterval(NamedTuple):
    """Interval of indexes, INCLUSIVE"""
    start: int
    end: int


@dataclasses.dataclass
class AnalysisResults:
    elevation_columns: list[IndexInterval] | None = dataclasses.field(default=None, repr=False)

    def find_elevation_columns(self):
        pass

    def __post_init__(self) -> None:
        if self.elevation_columns is not None:
            self.elevation_columns = [
                IndexInterval(*tup)
                for tup
                in self.elevation_columns
            ]
    

@dataclasses.dataclass
class TestInfo:
    """Metadata about a given test"""
    description: str = ""
    power_meter_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    px6_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    hwctrl_log_data_relative_path: Path | None = dataclasses.field(default=None, repr=False)
    combined_data_csv_relative_path: Path | None = dataclasses.field(default=None, repr=False)
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


if __name__ == "__main__":
    # logger.setLevel("INFO")
    meta_data = TestInfo.load(R"tests\2024-03-26")
    logger.info(f"{meta_data=}")
    logger.info(f"{meta_data.data}")
    meta_data._create_combined_data()
    # meta_data.analysis_results.elevation_columns = [IndexInterval(0, 200)]
    meta_data.write_parameters()