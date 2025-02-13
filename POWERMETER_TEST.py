import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

start_time = time.time()
rm = pyvisa.ResourceManager()
print(rm.list_resources())

power_meter = rm.open_resource('GPIB1::13::INSTR')
print(power_meter.query('*IDN?')) #this asks the insturment to print its GPIB address, serial number and firmware version and works.

#print(power_meter.query('SYST:RINT?'))
print(power_meter.write('CAL'))
sleep(20)
print(power_meter.write('ZE'))
sleep(20)
power_meter.write('*TST?') # This makes the machine conduct a self test before beginning
sleep(20)
print(power_meter.query('*OPC?'))

#iter =  int(input("How many times do you want to read?"))
#pause = int(input("How long do you want to pause between readings?"))

#with open("powerTest_RunForRecord_2.csv", "w") as file:
#     array_p = []
#     array_t = []
#     for i in range(iter):
#         power = round(float(power_meter.query('FETC:POW:AC?')),2)
#         array_p.append(power)
#         file.write(f"{datetime.utcnow()},{str(power)}\n")
#         array_t.append(datetime.utcnow())
#         print(i, datetime.utcnow(), power, "dBm")
#         sleep(pause)
#print(f"Average = {sum(array_p) / len(array_p):0.2f}")

#end_time = time.time() #this is the time the actual data gathering portion ends
#elapsed_time = end_time - start_time
#print('Execution time:', elapsed_time, 'seconds') #execution time helps dial in the iterations and sleep times

# plt.plot(array_t,array_p,'r+')
#plt.ylabel("Power in dBm")
#plt.xlabel("Time in UTC (YYYY-MM-DD HH-MM-SS.MS)")
#plt.title("PowerMeter Readings over"+str(iter)+"readings")
#plt.show()

