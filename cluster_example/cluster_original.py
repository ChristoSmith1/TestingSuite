"""
This is the original way we implemented this on 2024-05-25.

It's a direct copy/paste of the code from combined_filtered_analysis.py,
with some comments added.
"""


SAMPLE_DATA: list[float] = [3,4,5,9,10,11]
DEFAULT_CLUSTER_MARGIN: float = 2.0

if __name__ == "__main__":
    data: list[float] = SAMPLE_DATA.copy()

    clusters: list[list[float]] = []
    """A list of all the clusters we will find"""

    cluster: list[float] = []
    """The active cluster that we will either expand or finish as we examine data points"""

    # Loop over the `data` list until it's empty
    while data:
        # Remove the first (i.e., the smallest) item from the list
        first_item = data.pop(0)

        if not cluster:
            # If the working cluster is empty, we know we can add this current point to it
            cluster.append(first_item)
        else:
            # If the working cluster is NOT empty, we check to see if the point
            # is close enough to be added
            smallest_cluster_value = min(cluster)
            largest_cluster_value = max(cluster)
            min_cluster_threshold = smallest_cluster_value - DEFAULT_CLUSTER_MARGIN
            max_cluster_threshold = smallest_cluster_value + DEFAULT_CLUSTER_MARGIN
            if (
                min_cluster_threshold <= first_item
                and first_item <= max_cluster_threshold
            ):
                # This point IS close enough to be added to the working cluster
                cluster.append(first_item)
            else:
                # This point IS NOT close enough to be added to the working cluster
                # That means that we need to:
                
                # 1. add the working cluster to the list of completed clusters
                clusters.append(cluster)

                # 2. Make a new working cluster
                cluster = []

                # 3. Add this point to the (newly created) working cluster
                cluster.append(first_item)

    # Now we're outside the loop. It's possible (actually, it's almost
    # guaranteed) that there will be a cluster that hasn't been added to the
    # completed clusters. So we add it now.
    if cluster:
        clusters.append(cluster)

    # Print the clusters to the screen
    for cluster in clusters:
        print(f"Found a cluster: {cluster}")

