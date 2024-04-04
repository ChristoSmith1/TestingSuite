from matplotlib import pyplot as plt
import pandas as pd

csv_path = R"2024-03-26_results\combined_filtered.csv"
df=pd.read_csv(csv_path,parse_dates=["timestamp"])
print(df)
print("--------")
print(df.dtypes)
print("--------")

timemin=min(df["timestamp_posix"])
df["elapsed_time"]=df["timestamp_posix"]-timemin




# elevation = df["elevation"]
# timemin= min(df["timestamp_posix"])
# print(f"timemin is {timemin}")
# timestamp_posix=df["timestamp_posix"]
# print(f"thetimestampposixisthis \n{timestamp_posix}")
# elapsed_time=timestamp_posix-timemin
# print(f"elapsed time is as follows \n {elapsed_time}")
# df["elapsed_time"]=elapsed_time
print(df)