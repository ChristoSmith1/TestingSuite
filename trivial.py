"""
Example of how to use `test_info` 
"""
# C:\Users\dcmay\dev\TestingSuite\src
import matplotlib.pyplot as plt

# Import these from `test_info.py` These are INSTANCES of the `TestInfo` class
from govert.test_info import march_info, april_info, TestInfo

info = march_info

# START

# Get the data (a DataFrame object) from info, which is a `TestInfo` instance
data = info.data

# Plot something
fig, ax = plt.subplots()
ax: plt.Axes
ax.plot(data["elapsed"], data["power"])
ax.set_xlabel("elapsed")
ax.set_ylabel("power")

# Get the description from the `TestInfo` object, and use that as the title
ax.set_title(info.description)

plt.show()

# END


# CHALLENGE: Convert the stuff between START and END to be a function that takes a `TestInfo` instance
# and plots power vs. time for that test.
# 
# The first line should look like this:
#
# def plot_power(info: TestInfo) -> None: