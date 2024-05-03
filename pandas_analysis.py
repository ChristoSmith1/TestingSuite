from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

csv_path = R"2024-03-26_results\combined_filtered.csv"
df=pd.read_csv(csv_path,parse_dates=["timestamp"])
# print(df)
# print("--------")
# print(df.dtypes)
# print("--------")

timemin=min(df["timestamp_posix"])
df["elapsed_time"]=df["timestamp_posix"]-timemin
df.to_csv("sample.csv",index=False)

azimuthcol1_df=df.loc[(df['azimuth'] >= 199) & (df['azimuth'] <= 201)]
#azimuthcol2_df=df.loc[(df['azimuth'] >= 224) & (df['azimuth'] <= 226)]
azimuthcol2_df=df.loc[(df['azimuth'] >= 224) & (df['azimuth'] <= 226) & (df['elapsed_time'] >= 2974.8)]


# Calculate the slope and y-intercept of the line of best fit
z = np.polyfit(azimuthcol1_df["elevation"], azimuthcol1_df["power"], 3)
p = np.poly1d(z)
z2 = np.polyfit(azimuthcol2_df["elevation"], azimuthcol2_df["power"], 3)
p2 = np.poly1d(z2)
# Plot the dataset and the line of best fit

# experimental uncertainty in measurement of power = +/-

# plt.plot(azimuthcol1_df["elevation"],azimuthcol1_df["power"])
# plt.plot(azimuthcol1_df["elevation"], p(azimuthcol1_df["elevation"]), "-r")
# plt.plot(azimuthcol2_df["elevation"],azimuthcol2_df["power"])
# plt.plot(azimuthcol2_df["elevation"], p(azimuthcol2_df["elevation"]), "-g")

plt.show()
