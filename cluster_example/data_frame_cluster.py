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
            self._finalize_data_frame()
        return self._data

    def _finalize_data_frame(self) -> None:
        self._data = pd.concat([self._data] + [series.to_frame().T for series in self._series])
        self._data.sort_values(self.cluster_column_name)
        self._data.reindex()
        self._series = []
        
    def min_value(self) -> float:
        if len(self) == 0:
            return float("-inf")
        else:
            return self._min_value
        
    def max_value(self) -> float:
        if len(self) == 0:
            return float("inf")
        else:
            return self._max_value

    def min_cluster_column_threshold(self) -> float:
        return self.min_value() - self.margin

    def max_cluster_column_threshold(self) -> float:
        return self.max_value() + self.margin

    def __len__(self) -> int:
        return len(self._data) + len(self._series)

    def can_add_value(self, value: float) -> bool:
        return (
            self.min_cluster_column_threshold() <= value
            and value <= self.max_cluster_column_threshold()
        )
    
    def can_add_data_point(self, data_point: pd.Series) -> bool:
        # return True
        value = data_point[self.cluster_column_name]
        return self.can_add_value(value)
    
    def can_merge(self, other: "DataFrameCluster") -> bool:
        if self.margin != other.margin:
            return False
        if self.cluster_column_name != other.cluster_column_name:
            return False
        if len(self) == 0 or len(other) == 0:
            return True
        if self.can_add_value(other.min_value()):
            return True
        if self.can_add_value(other.max_value()):
            return True
        if other.can_add_value(self.min_value()):
            return True
        if other.can_add_value(self.max_value()):
            return True
        return False

    def merge(
        self,
        other: "DataFrameCluster",
        *,
        skip_validation: bool = False,
    ) -> "DataFrameCluster":
        if (
            not skip_validation
            or not self.can_merge(other)
        ):
            raise ValueError(f"Cannot merge.")
        rv = DataFrameCluster(
            cluster_column_name=self.cluster_column_name,
            margin=self.margin,
            original_data=self.data,
        )
        for index, series in self.data.iterrows():
            rv.add_data_point(series, skip_validation = True)
        for index, series in other.data.iterrows():
            rv.add_data_point(series, skip_validation = True)
        # rv._finalize_data_frame()
        return rv

    def add_data_point(
        self,
        data_point: pd.Series,
        *,
        skip_validation: bool = False,
    ) -> None:
        value = data_point[self.cluster_column_name]
        if skip_validation or self.can_add_data_point(data_point):
            self._series.append(data_point)
            if value < self._min_value:
                self._min_value = value
            if self._max_value < value:
                self._max_value = value
            pass
        else:
            raise ValueError(
                f"Cannot add data point with value {value}. Valid range is "
                + f"[{self.min_cluster_column_threshold()}, {self.max_cluster_column_threshold()}]"
            )


def make_clusters(
    data: pd.DataFrame,
    cluster_column_name: str,
    margin: float = 2.0,
    *,
    merge: bool = False,    # Attempt to merge afterwards
    sorted: bool = False,   # Assume data is sorted
) -> list[DataFrameCluster, None, None]:
    print(f"++++ BEGIN make_cluster {datetime.datetime.now():%X} ++++")
    clusters: list[DataFrameCluster] = []
    # rows_iterated_over = 0
    for index, row_series in data.iterrows():
        if sorted:
            # If we assume sorted values, we only have to check against the most recent cluster
            clusters_to_check = clusters[-1 : ]
        else:
            # If not sorted, we have to check all clusters
            clusters_to_check = clusters

        # rows_iterated_over += 1
        found = False
        for cluster in clusters_to_check:
            if cluster.can_add_data_point(row_series):
                cluster.add_data_point(row_series)
                found = True
                break
        if not found:
            cluster = DataFrameCluster(
                original_data=data,
                cluster_column_name=cluster_column_name,
                margin=margin,
            )
            cluster.add_data_point(row_series)
            clusters.append(cluster)

    if merge:
        # def total_length() -> float:
        #     return sum((len(cluster) for cluster in clusters))
        print(f"++++ BEGIN MERGE {datetime.datetime.now():%X} ++++ [{len(clusters)=}]")
        clusters.sort(key=lambda cluster: cluster.min_value())

        keep_searching = True
        loop_count = 0
        while keep_searching:
            print(f"  ++ BEGIN MAIN LOOP #{loop_count} {datetime.datetime.now():%X} ++++ [{len(clusters)=}]")
            loop_count += 1
            keep_searching = False
            for left_index in reversed(range(len(clusters) - 1)):
                right_index = left_index + 1
                left_cluster = clusters[left_index]
                right_cluster = clusters[right_index]

                if left_cluster.can_merge(right_cluster):
                    keep_searching = True
                    combined_cluster = left_cluster.merge(right_cluster)
                    clusters[left_index] = combined_cluster
                    clusters.pop(right_index)
                    pass
        print(f"++++ FINISH MERGE {datetime.datetime.now():%X} ++++ [{len(clusters)=}]")
    print(f"++++ FINISH make_cluster {datetime.datetime.now():%X} ++++")
    return clusters


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

    def filter_function(value: float) -> bool:
        return int(value) % 10 < 1
    
    data_subset = data.loc[data["elapsed"].apply(filter_function)]
    # data_subset = data.loc[data["elapsed"] > 500]
    data_shuffled = data.sample(frac=1.0, random_state=40351)
    data_shuffled.reindex()
    print(f"{len(data) = }")
    print(f"{len(data_shuffled) = }")
    # exit()
    pass

    clusters = make_clusters(
        # data=data_subset,
        # data=data_shuffled,
        data=data,

        cluster_column_name="elapsed",
        # margin=10.0,
        # margin=1.0,
        margin=0.143693 * 2.5,
        # margin=0.1,
        # margin=0.01,
        # merge=True,
        sorted=True,
    )
    for index in range(len(clusters)):
        cluster = clusters[index]
        print(f"{index=}   {len(cluster)=}   {cluster.min_value()=}   {cluster.max_value()=}   [{cluster.min_value() + min_timestamp_posix}, {cluster.max_value() + min_timestamp_posix}]")
    print(f"{len(clusters) = }")
    print(f"{len(clusters[0]) = }")
    print(f"{len(clusters[-1]) = }")
    total_length = sum((
        len(cluster)
        for cluster
        in clusters
    ))
    print(f"{total_length=}")

    import matplotlib.pyplot as plt
    import random
    random.seed(40351)
    def random_color() -> str:
        chars = "0123456789abcdef"
        chars = "456789abcdef"
        return "#" + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)

    # fig, ax = plt.subplots()
    # ax: plt.Axes
    # for index, cluster in enumerate(clusters):
    #     ax.scatter(
    #         cluster.data["elapsed"],
    #         cluster.data["elapsed"],
    #         label=f"{index}",
    #         color=random_color()
    #     )
    # ax.legend()
    # plt.show()

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