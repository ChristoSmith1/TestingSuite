# from g_over_t import helloworld 

# helloworld("christo")

import g_over_t
import matplotlib.pyplot as plt
import numpy as np

#g_over_t.hello_world("david")
powerdata = g_over_t.read_power_file(r"merge_test\MSU_PowerMeter_GoverT_06022024_XXXXUTC_3.csv")
#print(powerdata)

pointingdata = g_over_t.read_px6_file(r"merge_test\GTprocedure_3.txt")
#print(pointingdata)

combineddata= g_over_t.combine_power_position(power_data=powerdata, position_data=pointingdata)
#print(combineddata)

g_over_t.write_csv(combineddata, r"test_goverttest.csv")

power_data_list = g_over_t.get_column(combineddata, "power")
#print(L)

elevation_data_list = g_over_t.get_column(combineddata, "elevation")

azimuth_data_list = g_over_t.get_column(combineddata, "azimuth")
#print(M)

timestamp_data_list = g_over_t.get_column(combineddata, "timestamp")

print (f"length = {len(azimuth_data_list)}")
print(f"length = {len(timestamp_data_list)}")
print(f"{len(timestamp_data_list)=}")
print(f"{len(azimuth_data_list)=}")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2,layout = "constrained")
fig.suptitle('Power vs. Time and Azimuth vs. Elevation')

ax1.plot(timestamp_data_list,power_data_list)
ax1.set_title('power vs. time')
ax1.set_ylabel('power in dB')
ax1.set_xlabel('Day + Time in UTC')

ax2.plot(timestamp_data_list,azimuth_data_list, 'tab:green')
ax2.set_title('time vs. az')
ax2.set_xlabel("time")
ax2.set_ylabel("azimuth")

ax3.plot(timestamp_data_list,elevation_data_list)
ax3.set_title('time vs. el')
ax3.set_xlabel("time")
ax3.set_ylabel("elevation")

ax4.plot(elevation_data_list,power_data_list, 'tab:red')
ax4.set_title('el vs. power')
ax4.set_xlabel("power")
ax4.set_ylabel("elevation")

# fig.tight_layout()
plt.show()
#need to adjust my code for actual analysis for elevation column.
    #delta in on moon off moon for "first power delta"
    #use that delta for anaylsis of elevation column
    #write this as a function in "g_over_t.py"
        #math + stats. What libraries will I need?
#How do I clean up this directory, it's an absolute travesty and I'm getting confused.