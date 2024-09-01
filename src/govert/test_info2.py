from collections.abc import Generator
import os
from pathlib import Path
from typing import Any, Literal, NamedTuple, Self, Union
import pandas as pd
import pydantic

from govert.util.simple_log import logger


TESTS_DIRECTORY = Path("tests")
"""Base directory for all the things. By default, it's `{workspace}/tests/`"""

logger.debug(f"Initializing with {TESTS_DIRECTORY=}")


class Analysis(pydantic.BaseModel):
    test_info: Union["TestInfo", None] = pydantic.Field(
        default=None,
        repr=False,

    )
    """Pointer to parent info"""
    description: str = ""

    # Do not ever serialize pointer to parent
    # to avoid circular references
    @pydantic.field_serializer("test_info", mode="wrap")
    def serialize(
        self,
        test_info: Union["TestInfo", None],
        handler: pydantic.SerializerFunctionWrapHandler,
    ) -> None:
        return None


class ElapsedTimeInterval(NamedTuple):
    """INCLUSIVE elapsed times"""
    start: float
    end: float

    def subset_df(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return the portion of `data` that has `elapsed` within this interval (inclusive)"""
        assert "elapsed" in data.columns
        return data[
            (data["elapsed"] >= self.start)
            & (data["elapsed"] <= self.end)
        ]


class OnOffPairIntervals(pydantic.BaseModel):
    on_interval: ElapsedTimeInterval
    off_interval: ElapsedTimeInterval


class ElevationColumnAnalysis(Analysis):
    description: str = "Elevation column analysis"
    column_intervals: list[ElapsedTimeInterval] = pydantic.Field(
        default_factory=list,
        repr=False,
    )

    def columns(self) -> Generator[pd.DataFrame, None, None]:
        for interval in self.column_intervals:
            yield interval.subset_df(self.test_info.data)


class OnOffMoonAnalysis(Analysis):
    description: str = "Elevation column analysis"
    pair_intervals: list[OnOffPairIntervals] = pydantic.Field(
        default_factory=list,
        repr=False,
    )

    def pairs(self) -> Generator[tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """Yields tuples of `(on_data, off_data)`"""
        for pair_interval in self.pair_intervals:
            yield (
                pair_interval.on_interval.subset_df(self.test_info.data),
                pair_interval.off_interval.subset_df(self.test_info.data),
            )

class TestInfo(pydantic.BaseModel):
    description: str = ""
    elevation_column_analysis: ElevationColumnAnalysis | None = pydantic.Field(
        default=None,
        repr=False,
    )
    on_off_moon_analysis: OnOffMoonAnalysis | None = pydantic.Field(
        default=None,
        repr=False,
    )

    root_tests_path: Path = pydantic.Field(
        default=TESTS_DIRECTORY,
        repr=False,
    )
    """Root directory of all tests"""

    path: Path | None = None
    """relative path from root tests to this test's folder"""

    power_meter_data_relative_path: Path | None = pydantic.Field(
        default=None,
        repr=False,
    )
    px6_data_relative_path: Path | None = pydantic.Field(default=None, repr=False)
    hwctrl_log_data_relative_path: Path | None = pydantic.Field(
        default=None,
        repr=False,
    )
    combined_data_csv_relative_path: Path | None = pydantic.Field(
        default=Path("analysis_data/data.csv"),
        repr=False,
    )
    parameters_relative_path: Path | None = pydantic.Field(
        default=None,
        repr=False,
    )
    pointing_data_source: Literal["hwctrl", "px6"] = pydantic.Field(
        default="hwctrl",
        repr=False,
    )

    # @pydantic.field_validator("elevation_column_analysis", mode="after")
    # def validate_analysis(self, value: ElevationColumnAnalysis | None):
    #     if value:
    #         value.test_info = self
    #     return value

    # @pydantic.field_validator("root_tests_path", mode="after")
    # def _tests_directory_path_validator(cls, value: Path):
    #     if not value.exists():
    #         raise FileNotFoundError(f"Directory {value!r} does not exist.")
    #     return value


    @pydantic.model_validator(mode="after")
    def post_load(self) -> None:
        # Set self as the parent of the analyses
        if self.elevation_column_analysis:
            self.elevation_column_analysis.test_info = self
        if self.on_off_moon_analysis:
            self.on_off_moon_analysis.test_info = self


        self._data: pd.DataFrame | None = None
        return self
        # raise RuntimeError("YO")

    @classmethod
    def load(cls, path: Path) -> Self:
        """Load the test from the parameters on disk.
        
        Can pass path to the folder or to `parameters.json`"""
        path = Path(path)
        if path.is_dir():
            path = path / "parameters.json"
        return TestInfo.model_validate_json(path.read_text())

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._load_data()
        return self._data
    
    @data.setter
    def data(self, value: pd.DataFrame) -> None:
        self._data = value

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
            
    @property
    def test_folder_path(self) -> Path | None:
        if self.path:
            return (self.root_tests_path / self.path).expanduser().resolve()
            return (self.root_tests_path / self.path)
        else:
            return None
    
    @property
    def parameters_json_path(self) -> Path | None:
        if self.test_folder_path:
            return self.test_folder_path / "parameters.json"
    
    @classmethod
    def init(
        cls,
        name: str,
        description: str = "",
    ) -> Self:
        if not description:
            description = name
        rv = TestInfo(
            path=Path(name),
            description=description,
        )
        rv.write_parameters()
        return rv

    def write_parameters(self):
        if not self.parameters_json_path:
            raise ValueError(f"Cannot write to JSON because 'parameters_json_path' is not set")
        folder = self.parameters_json_path.parent
        if not folder.exists():
            logger.debug(f"Creating folder {folder!r}")
            folder.mkdir(parents=True)
        
        logger.info(f"Saving test metadata to {self.parameters_json_path!r}")
        self.parameters_json_path.write_text(
            self.model_dump_json(indent=2),
        )


if __name__ == "__main__":
    info = TestInfo(
        # root_tests_path=Path(R"./tests"),
        # root_tests_path=Path(R"./fake_tests"),
        pointing_data_source="hwctrl",
        path=Path(R"sample"),
    )
    print(f"{info=!r}")
    print(f"{info=!s}")

    json = info.model_dump_json(indent=2)
    print(json)
    new_info = TestInfo.model_validate_json(json)
    print(f"{new_info = }")
    # exit()

    print(f"{info.test_folder_path = }")
    print(f"{info.parameters_json_path = }")

    # info.write_parameters()
    sample_info = TestInfo.init("sample")

    print(f"{sample_info.parameters_json_path = }")
    # json = sample_info.parameters_json_path.read_text()
    # print(json)
    new_info = TestInfo.model_validate_json(json)
    print(f"{new_info = }")

    el_col = ElevationColumnAnalysis(test_info=new_info,)
    on_off = OnOffMoonAnalysis(test_info=new_info,)
    print(f"{el_col = }")

    new_info.elevation_column_analysis = el_col
    new_info.on_off_moon_analysis = on_off
    print(new_info.model_dump_json(indent=2))
    print(new_info)

    loaded_data = TestInfo.model_validate_json(new_info.model_dump_json(indent=2))
    pass

    loaded_data = TestInfo.load(R"tests\sample")

    print(repr(loaded_data))