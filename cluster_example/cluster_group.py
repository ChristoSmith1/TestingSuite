"""
Makes a new class, called `ClusterGroup`, that handles our whole algorithm
internally.

Note how little code and logic goes into the `if __name__ == "__main__"` when
we do it this way.
"""

from typing import Iterator
from cluster_example.cluster_class import Cluster, DEFAULT_CLUSTER_MARGIN, SAMPLE_DATA


class ClusterGroup:
    def __init__(
        self,
        margin: float = DEFAULT_CLUSTER_MARGIN
    ) -> None:
        self.margin = margin
        self.clusters: list[Cluster] = []
    
    def add_value(self, value: float) -> None:
        found = False
        # Loop over the existing clusters, seeing if any of them can
        # add the new value
        for cluster in self.clusters:
            if cluster.can_add_value(value):
                cluster.add_value(value)
                found = True
                break
        
        # If none of the clusters can add the value, make a new cluster
        # with just this one value
        if not found:
            cluster = Cluster(margin=self.margin)
            cluster.add_value(value)
            self.clusters.append(cluster)

    def __iter__(self) -> Iterator[Cluster]:
        """Another "magic" method that lets us iterate with
        `for cluster in cluster_group`
        """
        return iter(self.clusters)


if __name__ == "__main__":
    data: list[float] = SAMPLE_DATA.copy()

    cluster_group: ClusterGroup = ClusterGroup()
    """A group of all the clusters we will find"""

    # Loop over the data
    while data:
        # Remove the first (i.e., the smallest) item from the list
        first_item = data.pop(0)

        # Add the item to the cluster group
        cluster_group.add_value(first_item)

    # Print the clusters to the screen
    for cluster in cluster_group:
        print(f"Found a cluster: {cluster}")