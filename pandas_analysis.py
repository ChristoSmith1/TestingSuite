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
df.to_csv("sample.csv",index=False)

azimuthcol1_df=df.loc[(df['azimuth'] >= 199) & (df['azimuth'] <= 201)]
#azimuthcol2_df=df.loc[(df['azimuth'] >= 224) & (df['azimuth'] <= 226)]
azimuthcol2_df=df.loc[(df['azimuth'] >= 224) & (df['azimuth'] <= 226) & (df['elapsed_time'] >= 2974.8)]


# plt.plot(azimuthcol1_df["elevation"],azimuthcol1_df["power"])
plt.plot(azimuthcol2_df["elapsed_time"],azimuthcol2_df["elevation"])
plt.show()
