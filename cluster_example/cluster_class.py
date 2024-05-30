"""
This is the same algorithm as cluster_original.py, but much of the cluster
logic is moved into a class called `Cluster`
"""

from cluster_example.cluster_original import SAMPLE_DATA, DEFAULT_CLUSTER_MARGIN


class Cluster:
    def __init__(
        self,
        margin: float = DEFAULT_CLUSTER_MARGIN
    ) -> None:
        """__init__ is a magic function name that tells Python to do
        some stuff every time someone makes a new instance of the
        type `Cluster`"""
        self.margin = margin
        self.values: list[float] = []

    def min_threshold(self) -> float:
        """Get the smallest value that can be added to this `Cluster` at
        this point. If `Cluster` is empty, this will be negative infinity.
        """
        if self.values:
            return min(self.values) - self.margin
        else:
            return float("-inf")
    
    def max_threshold(self) -> float:
        """Get the largest value that can be added to this`Cluster` at
        this point. If `Cluster` is empty, this will be infinity.
        """
        if self.values:
            return max(self.values) + self.margin
        else:
            return float("inf")

    def can_add_value(self, value: float) -> bool:
        """Can the given value be added to the `Cluster` at this point?"""
        return (
            self.min_threshold() <= value
            and value <= self.max_threshold()
        )

    def add_value(self, value: float) -> None:
        """Add the given value to the `Cluster`.
        Raises a `ValueError` if an invalid value is given."""
        if self.can_add_value(value):
            self.values.append(value)
        else:
            raise ValueError(
                f"Cannot add value {value!r}. "
                + f"Acceptable range is [{self.min_threshold()!r}, "
                + f"{self.max_threshold()!r}]"
            )
        
    def __str__(self) -> str:
        """This is a "magic" function name that tells Python how it
        should convert the `Cluster` to a string, such as when calling
        print()"""
        return str(self.values)


if __name__ == "__main__":
    data: list[float] = SAMPLE_DATA.copy()

    clusters: list[Cluster] = []
    """A list of all the clusters we will find"""

    cluster: Cluster = Cluster()
    """The active cluster that we will either expand or finish as we examine data points"""

    # Loop over the data
    while data:
        # Remove the first (i.e., the smallest) item from the list
        first_item = data.pop(0)

        if cluster.can_add_value(first_item):
            # This point IS close enough to be added to the working cluster
            # (or the working cluster is empty)
            cluster.add_value(first_item)
        else:
            # This point IS NOT close enough to be added to the working cluster
            # That means that we need to:
            
            # 1. add the working cluster to the list of completed clusters
            clusters.append(cluster)

            # 2. Make a new working cluster
            cluster = Cluster()

            # 3. Add this point to the (newly created) working cluster
            cluster.add_value(first_item)

    # Now we're outside the loop. It's possible (actually, it's almost
    # guaranteed) that there will be a cluster that hasn't been added to the
    # completed clusters. So we add it now.
    if cluster:
        clusters.append(cluster)

    # Print the cluster to the screen
    for cluster in clusters:
        print(f"Found a cluster: {cluster}")