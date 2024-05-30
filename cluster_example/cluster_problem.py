"""
There is a hidden assumption in the clustering algorithm we've been using:
The values must be in sorted order. This is fine for our purposes, but might
not be for other purposes. (In general, this is considered bad in clustering)

This file just demonstrates a pathological case.
"""

from cluster_example.cluster_group import ClusterGroup


if __name__ == "__main__":
    # These are the numbers 1 through 10, in order
    ordered_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # These are the numbers 1 through 10, in a particular order
    # that will mess up our algorithm.
    pathological_data = [1, 4, 7, 10, 2, 5, 8, 3, 6, 9]
    
    ordered_cluster_group = ClusterGroup()
    for value in ordered_data:
        ordered_cluster_group.add_value(value)

    print(f"\nORDERED DATA:")
    print(f"data={ordered_data}")
    for cluster in ordered_cluster_group:
        print(f"Found a cluster: {cluster}")

    pathological_cluster_group = ClusterGroup()
    for value in pathological_data:
        pathological_cluster_group.add_value(value)

    print(f"\nPATHOLOGICAL DATA:")
    print(f"data={pathological_data}")
    for cluster in pathological_cluster_group:
        print(f"Found a cluster: {cluster}")