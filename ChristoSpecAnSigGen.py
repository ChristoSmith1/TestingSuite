import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

start_time = time.time() #start time of operations of the actual machine, and reading of data

rm = pyvisa.ResourceManager() #This lookes at all of the GPIB available resources and gives their addresses in a particular format
print(rm.list_resources()) #I want to make it so it lets me CHOOSE which resource I want to use, so that power meter is based on my input "choose insturment [1]etc."
number_of_readings = 100 #This is the hard coded value for the first test we did on May 2, 2023
pause_between_readings = 1.00 #This is the hard coded value for the first test we did on May 2, 2023

########### SPECTRUM ANALYZER ###############

#1::18 is spectrum analyzer

SpecAn = rm.open_resource("GPIB1::18::INSTR")

"""
print(SpecAn.query('MKF?'))
(SpecAn.write('MKPK'))
print(SpecAn.query('MKA?'))

#write values using start time as first column in csv
#time,CF,MKA
with open("MSU_SpecAn_Testing_01_02_2024" + ".txt", "w") as file:
     #these arrays are only generated below for the plotting of the data after completion of the testing
     array_p = []
     array_t = []
     for i in range(number_of_readings):
         Center_Frequency=(str(SpecAn.query('CF?')))
         Marker_Frequency=(str(SpecAn.query('MKF?')))
         power = round(float(SpecAn.query('MKA?')),2)
         array_p.append(power)
         file.write(f"{datetime.utcnow()},{Center_Frequency.strip()},{Marker_Frequency.strip()},{str(power)}\n")
         array_t.append(datetime.utcnow())
         print(i, datetime.utcnow(), power, "dBm") #printed for user benefit, to see how many iterations are left
         sleep(pause_between_readings)
"""

##############SIGNAL GENERATOR##################
#sig gen started first because we want everything to follow what happens in the loop

frq=84500000
pwr=9

SigGen = rm.open_resource("GPIB1::20::INSTR")
for i in range(number_of_readings):
    frq=frq+10000
    pwr=pwr+1
#    print(frq)
    SigGen.write("P0"+str(frq)+"Z0K"+str(pwr)+"L0M0N6O1")
    SpecAn = rm.open_resource("GPIB1::18::INSTR")
    (SpecAn.write("CF 8450MHZ"))
    (SpecAn.write("MKPK"))
    MarkF=(SpecAn.query('MKF?'))
    SpecPow=(SpecAn.query('MKA?'))
    Power_Meter = rm.open_resource("GPIB1::13::INSTR")
    meter = (Power_Meter.query("FETC:POW:AC?"))
    sleep(pause_between_readings)
    print((str(datetime.utcnow()),meter,MarkF,SpecPow,frq))
#print(SigGen.query("P084500000Z0K3L0M0N6O1"))

##########POWER METER####################

#Power_Meter = rm.open_resource("GPIB1::13::INSTR")

