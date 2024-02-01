import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

####### STARTS THE CLOCK ON OPERATION AND CONFIRMS ADDRESS IN EVENT OF MULTIPLE MACHINES #########3

start_time = time.time() #start time of operations of the actual machine, and reading of data
rm = pyvisa.ResourceManager() #This lookes at all of the GPIB available resources and gives their addresses in a particular format
print(rm.list_resources()) #I want to make it so it lets me CHOOSE which resource I want to use, so that power meter is based on my input "choose insturment [1]etc."

power_meter = rm.open_resource('GPIB1::13::INSTR') #connects to the insturment of our choosing, hardcoded in at the moment.
print(power_meter.query('*IDN?')) #this asks the insturment to print its GPIB address, serial number and firmware version and works.

print(power_meter.query('SYST:RINT?')) #this is to make sure you are using the correct address interface

########TESTING AND CALIBRATION THAT CAN BE AUTOMATED ########
print(power_meter.write('CAL')) #this calibrates the insturment
sleep(20)
print(power_meter.write('ZE')) #this zeroe's the insturment
sleep(20)
power_meter.write('*TST?') # This makes the machine conduct a self test before beginning
sleep(20)
#the sleep cycles in the machine cal process above are their because while they are running, if I attempt to read out power it will crash

print(power_meter.query('*OPC?')) #this is the SCIP protocol for telling me operations are completed, currently prints "+5" implying syntax error
sleep(5)
input("Press Enter to continue...")

######## USER INPUTS #########
#number_of_readings =  int(input("How many times do you want to read?")) #This is the number of readings we wish to take
#pause_between_readings = float(input("How long do you want to pause between readings? Between .1 and 10 seconds"))
#if pause < 0:
#    print ("Please enter a positive number between 0.0 and 10")
#    pause_between_readings = float(input("How long do you want to pause between readings?"))
#print (pause_between_readings) #this is how long we pause between them

number_of_readings = 100 #This is the hard coded value for the first test we did on May 2, 2023
pause_between_readings = 0.10 #This is the hard coded value for the first test we did on May 2, 2023


#iter and pause are simple and useable but should be able to handle things like "hey you can't put a negative number here, or 'thats a letter!'""

############# CREATION OF CSV AND WRITING OF POWERS ###############
#Take user input for file naming convention
#filenumber = input("Input file number (1,2,etc.): ")

#opens a titles a CSV, should be in format Power_Reading_DISHNAME_Date.csv
#with open("MSU_PowerMeter_GoverT_09202023_2300UTC_" + filenumber + ".txt", "w") as file:
with open("MSU_PowerMeter_GoverT_01022024_YYYYUTC_" +"XXXX"+ ".txt", "w") as file:
     #these arrays are only generated below for the plotting of the data after completion of the testing
     array_p = []
     array_t = []
     for i in range(number_of_readings):
         power = round(float(power_meter.query('FETC:POW:AC?')),2)
         array_p.append(power)
         file.write(f"{datetime.utcnow()},{str(power)}\n")
         array_t.append(datetime.utcnow())
         print(i, datetime.utcnow(), power, "dBm") #printed for user benefit, to see how many iterations are left
         sleep(pause_between_readings)

print(f"Average = {sum(array_p) / len(array_p):0.2f}")

#The code below will eventuall be the basis for merging the az/el pointing file and the csv's we create with the power readings
#We will want to plot the Az/El/Time/Powers in a single plot that Y1 = Elevation, X1 = Azimuth, Y2 = Power Read in dBm, and X2 = Time in UTC

## reading two csv files
#AzEl = pd.read_csv('TestCombineA.csv')
#PowerReading = pd.read_csv('TestCombineB.csv')
  
## using merge function by setting how='inner'
#rawdata_together = pd.merge(AzEl, PowerReading, on='Time', how='inner')
  
## displaying result
#print(rawdata_together)

end_time = time.time() #this is the time the actual data gathering portion ends
elapsed_time = end_time - start_time #elapsed time helps us dial in how many readings we think will be useful and the time delays that match pointing the dish
print('Execution time of', number_of_readings, 'readings took' , elapsed_time, 'seconds') #execution time helps dial in the iterations and sleep times based on how long we have.

############## PLOTTING THE DATA #####################

#plt.plot(array_t,array_p,'r+')
#a, b = np.polyfit(array_t,array_p,1)
#plt.plot(array_t, a*array_t+b, color='steelblue', linestyle='--', linewidth=2)
#plt.ylabel("Power in dBm")
#plt.xlabel("Time in UTC (YYYY-MM-DD HH-MM-SS.MS)")
#plt.title("PowerMeter Readings over "+str(number_of_readings)+" readings")
#plt.show()


######## MATHEMATICAL Y-FACTOR ANALYSIS FOR G/T TESTING ######

######## GENERATING A REPORT IN PDF FORMAT WITH PLOTS, AND OTHER RESULTS ##########

#RESOURCES
#https://naic.edu/~phil/hardware/Misc/powerMeters/E4418-90029_prog_man.pdf
