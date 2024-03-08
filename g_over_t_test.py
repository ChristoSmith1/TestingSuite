# from g_over_t import helloworld 

# helloworld("christo")

import g_over_t

g_over_t.hello_world("david")
powerdata = g_over_t.read_power_file(r"POWER_METER_Sept_20\MSU_PowerMeter_GoverT_09202023_2000UTC_0.txt")
print(powerdata)

