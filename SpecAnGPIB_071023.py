import pyvisa
import time
from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

ResourceList = pyvisa.ResourceManager()
print(ResourceList.list_resources())
specan = ResourceList.open_resource("GPIB2::18::INSTR")

# CF 2GHZ      :sets the Center Frequency to 2 GHz
# CHANPRW?:    :gets channel power
# CHPWRBW 2GHZ :changes the channel power bandwidth to 2 GHz
# ERR?         :returns the queue of error codes
# FA 2GHZ      :sets the start frequency to 2 GHz
# FB 3GHZ      :sets the end frequency to 3 GHz
# MF?          :Querys the marker Frequency
# MF           :Same as MF?
# MKF 3GHZ     :Sets Marker Frequency
# MKNOISE?     :Measures the noise (Unsure if this outputs anything more than 1 or 0)
# MKA?         :Querys the power at the marker
# SP 1MHZ      :Sets the span to 1 MHz
# MKPK HI      :Marker to highest peak

specan.write(f"CF 2.0356005 GHZ")
specan.write(f"SP 10MHZ")
MK = float(specan.query(f"MF?"))
DB = float(specan.query(f"MKA?"))

for i in range (2):
    print (datetime.now(),",",MK,",",DB)
#    print(specan.query("MKA?"))
#    print(specan.query("MF?"))
    sleep(10)
for j in range (5):
    print (datetime.now(),",",MK,",",DB)
#    print(specan.query("MKA?"))
#    print(specan.query("MF?"))
    sleep(10)
for k in range (2):
    print (datetime.now(),",",MK,",",DB)
#    print(specan.query("MKA?"))
#    print(specan.query("MF?"))
    sleep(10)
#with open("MSU_SpecAn_Thermal_10072023.txt", "w") as file:
#        for i in range (6000000):
#            file.write((datetime.now(),",",str(MK),",",str(DB)))
#            sleep (10)
#        file.close()