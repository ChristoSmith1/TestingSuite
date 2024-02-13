
import datetime
from typing import Any

from mayo.interpolator import Interpolator

def combine(
    power_data: list[dict[str, Any]],
    position_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    # add timestamp_float key to all data
    for row in power_data:
        timestamp_dt: datetime.datetime = row['timestamp']
        timestamp_float = timestamp_dt.timestamp()
        row['timestamp_float'] = timestamp_float
    for row in position_data:
        timestamp_dt: datetime.datetime = row['timestamp']
        timestamp_float = timestamp_dt.timestamp()
        row['timestamp_float'] = timestamp_float

    interpolator = Interpolator(position_data,"timestamp_float")
    print(interpolator)
    
    # creating a L.D.S. with time, power, az, el
    return_value=[]
    for power_data_row in power_data:
        timestamp_float = power_data_row['timestamp_float']
        timestamp_dt = power_data_row['timestamp']
        power = power_data_row['power']
        azimuth = interpolator(timestamp_float,'azimuth')
        elevation = interpolator(timestamp_float,'elevation')
        print(f"{timestamp_float=} {timestamp_dt=} {power=}  {azimuth=}  {elevation=}")
        output_row_dict = {
            'timestamp_posix': timestamp_float,
            'timestamp': timestamp_dt,
            'power': power,
            'azimuth': azimuth,
            'elevation': elevation,

        }
        return_value.append(output_row_dict)
    return return_value
    



if __name__ == "__main__":
    from mayo.write_csv import write_csv
    pass
    from merge_test.merge_px6_powerdata import read_power_file, read_px6_file
    position_data = read_px6_file('merge_test/GTprocedure_3.txt')
    power_data = read_power_file('merge_test/MSU_PowerMeter_GoverT_06022024_XXXXUTC_3.csv')
    print('MAYO')
    print(position_data)
    print("now its time for power data!")
    print(power_data)
    print('finished')
    combined_data = combine(power_data,position_data)
    write_csv(combined_data,'combinedtest01.csv')
