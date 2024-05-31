import pandas as pd


class DataFrameCluster:
    def __init__(
        self,
        cluster_column_name: str,
        margin: float = 2.0,
        original_data: pd.DataFrame | None = None,
    ) -> None:
        self.cluster_column_name = cluster_column_name
        self.margin = margin
        self._data: pd.DataFrame = pd.DataFrame()
        self._min_value: float = float("inf")
        self._max_value: float = float("-inf")

        if original_data is not None:
            self._data = pd.DataFrame({
                column_name: pd.Series(dtype=dtype)
                for column_name, dtype
                in original_data.dtypes.items()
            })
        else:
            self._data = pd.DataFrame()

        self._series: list[pd.Series] = []

    @property
    def data(self) -> pd.DataFrame:
        if self._series:
            self._finalize_dataframe()
        return self._data

    def _finalize_dataframe(self) -> None:
        self._data = pd.concat([self._data] + [series.to_frame().T for series in self._series])
        self._data.sort_values(self.cluster_column_name)
        self._data.reindex()
        self._series = []

    def min_cluster_column_threshold(self) -> float:
        if len(self) == 0:
            return float("-inf")
        else:
            return self._min_value - self.margin
    
    def __len__(self) -> int:
        return len(self._data) + len(self._series)

    def max_cluster_column_threshold(self) -> float:
        if len(self) == 0:
            return float("inf")
        else:
            return self._max_value + self.margin

    def _can_add_value(self, value: float) -> bool:
        return (
            self.min_cluster_column_threshold() <= value
            and value <= self.max_cluster_column_threshold()
        )
    
    def can_add_data_point(self, data_point: pd.Series) -> bool:
        # return True
        value = data_point[self.cluster_column_name]
        return self._can_add_value(value)        

    def add_data_point(self, data_point: pd.Series) -> None:
        value = data_point[self.cluster_column_name]
        if self.can_add_data_point(data_point):
            # self.data = pd.concat([self.data, data_point.to_frame().T])
            self._series.append(data_point)
            if value < self._min_value:
                self._min_value = value
            if self._max_value < value:
                self._max_value = value
            pass
        else:
            # pass
            raise ValueError(f"Cannot add data point with value {value}. Valid range is [{self.min_cluster_column_threshold()}, {self.max_cluster_column_threshold()}]")


if __name__ == "__main__":
    import datetime
    data = pd.read_csv(
        "2024-03-26_results/combined_filtered.csv",
        parse_dates=["timestamp"],
    )
    min_timestamp_posix = min(data["timestamp_posix"])
    data["elapsed"] = data["timestamp_posix"] - min_timestamp_posix
    print(data)

    cluster = DataFrameCluster(
        cluster_column_name="elapsed",
        margin = 2.0,
        original_data=data,
    )
    print(cluster)
    print(cluster._data.dtypes)



    point = data.iloc[10000]
    print(point)
    # cluster.add_data_point(point)
    print(f"{cluster._min_value = }")
    print(f"{cluster._max_value = }")
    print(f"{cluster.min_cluster_column_threshold() = }")
    print(f"{cluster.max_cluster_column_threshold() = }")
    print(cluster.data)
    # exit()
    # print(cluster.data)

    print(f"START @ {datetime.datetime.now():%X}")
    for index, series in data.iterrows():
        cluster.add_data_point(series)
    # cluster._data = pd.concat([series.to_frame().T for series in cluster.series])
    _ = cluster.data
    print(f"END @ {datetime.datetime.now():%X}")
    print(f"{len(cluster._data) = }")
    print(f"{len(cluster.data) = }")
    print(f"{len(cluster._data) = }")
    print(f"{cluster._min_value = }")
    print(f"{cluster._max_value = }")
    print(f"{cluster.min_cluster_column_threshold() = }")
    print(f"{cluster.max_cluster_column_threshold() = }")

    # print(f"{len(df) = }")
    exit()

    # exit()

    # print(data.dtypes, type(data.dtypes))

    # series = data.dtypes
    # for column_name, dtype in series.items():
    #     print(column_name, dtype)

    # df = pd.DataFrame({
    #     column_name: pd.Series(dtype=dtype)
    #     for column_name, dtype
    #     in series.items()
    # })
    # print(df)
    # print(df.dtypes)