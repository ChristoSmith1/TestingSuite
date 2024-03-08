from merge_test.merge_px6_powerdata import read_power_file, read_px6_file
from mayo.parse_hwctrl_log import parse_hwctrl_log_file
from mayo.combine_position_power import combine


POWER_DATA_PATH = "whatever/power.csv"
PX6_DATA_PATH = "whatever/px6.txt"
HWCTRL_LOG_PATH = "hwctrl.log"


power_data = read_power_file(POWER_DATA_PATH)
# position_data = read_px6_file(PX6_DATA_PATH)
position_data = parse_hwctrl_log_file(HWCTRL_LOG_PATH)

combined_data = combine(power_data, position_data)

# DO ANALYSIS

