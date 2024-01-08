import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt

start_time = time.time() #start time of operations of the actual machine, and reading of data

rm = pyvisa.ResourceManager() #This lookes at all of the GPIB available resources and gives their addresses in a particular format
print(rm.list_resources()) #I want to make it so it lets me CHOOSE which resource I want to use, so that power meter is based on my input "choose insturment [1]etc."
number_of_readings = 100 #This is the hard coded value for the first test we did on May 2, 2023
pause_between_readings = 9.00 #This is the hard coded value for the first test we did on May 2, 2023

########### SPECTRUM ANALYZER ###############

#1::18 is spectrum analyzer

#SpecAn = rm.open_resource("GPIB1::18::INSTR")

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

start_frq=22106000
end_frq=22206000
frq=0
frq_step=1000
list =[":",9,8,7]#6,5,4,3,2,1,0)
frq=start_frq
SigGen = rm.open_resource("GPIB1::20::INSTR")
'''
with open("MSU_S_Band_gain_linearity_test_23_01_08" + ".txt", "w") as file:
    for i in range(((end_frq-start_frq)/frq_step)):
        for j in power:
            SigGen.write("P0"+str(frq)+"Z0K"+str(j)+"L0M0N6O1")
            pwr=str(j)
            sleep(pause_between_readings)
            print((str(datetime.utcnow()),str(frq),str(pwr)))
            file.write(f"{datetime.utcnow()},{frq.strip()},{str(pwr)}\n")
        #frq=frq+frq_step
print("testing is finshed")
#print(SigGen.query("P084500000Z0K3L0M0N6O1"))
'''
powerlist=len(list)
with open("MSU_S_Band_gain_linearity_test_23_01_08" + ".txt", "w") as file:
    for j in range(powerlist):
        print(j)
        SigGen.write("P0"+str(frq)+"Z0K"+str(list[j])+"L0M0N6O1")
        pwr=str(list[j])
        sleep(pause_between_readings)
        print((str(datetime.utcnow()),str(frq),str(pwr)))
        file.write(f"{datetime.utcnow()},{str(frq).strip()},{str(pwr)}\n")
##########POWER METER####################

#Power_Meter = rm.open_resource("GPIB1::13::INSTR")

