from matplotlib import pyplot as plt
from test_info import TestInfo, all_tests
from util.plots import plot_all_test_info,HighlightInterval
from util import simple_log

simple_log.set_level("ERROR")

for test_info in all_tests():
    pass
    print(test_info.parameters_relative_path)
    plot_all_test_info(test_info)
    plt.show()
