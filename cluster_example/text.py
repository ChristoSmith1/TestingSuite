# Create an instance of the type `list`
# and call it `my_list`
my_list = list()

# Append 5 to `my_list`
# 
# Note the period. This calls the `append`
# function of the `list` type
my_list.append(5)

from cluster_example.cluster_class import Cluster, SAMPLE_DATA

data: list[float] = SAMPLE_DATA.copy()
clusters: list[Cluster] = []
cluster: Cluster = Cluster()
while data:
    first_item = data.pop(0)
    if cluster.can_add_value(first_item):
        cluster.add_value(first_item)
    else:
        clusters.append(cluster)
        cluster = Cluster()
        cluster.add_value(first_item)

if cluster:
    clusters.append(cluster)

print(clusters)
# Prints:
# [[3, 4, 5], [9, 10, 11]]


# Print the cluster to the screen
for cluster in clusters:
    print(f"Found a cluster: {cluster}")
