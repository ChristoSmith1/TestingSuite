#Christo Smith July 11 2023
#SpecAn Playground
#Various commands are listed below and will be used to increase automation:

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

import pyvisa
import time
from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

ResourceList = pyvisa.ResourceManager()
print(ResourceList.list_resources())
#this currently prints the resource list but doesn't really help
#what I would like is to have it print the resource list, let us see what each resource is by query
#at which point we can assign names to the resources which they take to be the variable name moving forward


SpecAn = ResourceList.open_resource("GPIB2::18::INSTR")

#print(SpecAn.query(f"ID?"))
#print(SpecAn.query(f"REV?"))
#print(SpecAn.query(f"SER?"))
SpecAn.write("CF 8.465GHZ")
SpecAn.write("SP 100KHZ")
for i in range (100000):
    SpecAn.write(f"MKPK HI")
    print(datetime.now(),SpecAn.query("MF?"),SpecAn.query("MKA?"))
    sleep(i)



