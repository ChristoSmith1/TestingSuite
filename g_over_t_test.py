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

L = g_over_t.get_column(combineddata, "power")
print(L)

M = g_over_t.get_column(combineddata, "azimuth")
#print(M)

plt.plot(L,M)
plt.show
#why doesn't this actually show any sort of plot

#need to adjust my code for actual analysis for elevation column.
    #delta in on moon off moon for "first power delta"
    #use that delta for anaylsis of elevation column
    #write this as a function in "g_over_t.py"
        #math + stats. What libraries will I need?
#How do I clean up this directory, it's an absolute travesty and I'm getting confused.