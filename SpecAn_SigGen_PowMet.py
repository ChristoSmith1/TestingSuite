import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

#This program is designed to use configuration files, user inputs, or hard coded 'presets' to conduct testing
#there will be generic settings and schema for various testing based on user inputs

#The section below starts time so that if there are events in place that need to happen in parallel
#there's a uniform time. datetime.timenow() is used in other instances of data collection, futhermore
#it shows all available resources so in the event it doesn't properly access the address it can be
#hard coded in.

start_time = time.time()
rm = pyvisa.ResourceManager()
print(rm.list_resources())

#the section below opens the GPIB addresses as shown:
power_meter = rm.open_resource("GPIB1::13::INSTR")
spec_an = rm.open_resource("GPIB1::18::INSTR")
sig_gen = rm.open_resource("GPIB1::20::INSTR")

#Starting each various test:

def display_menu():
   print("\nMenu:")
   print("1. X-band freq characterization")
   print("2. S-band freq characterization")
   print("3. X-band G/T")
   print("4. S-band G/T")
   print("5. Manual testing")
   print("6. Calibration/Manual inputs")
   print("7. Show me a previous test result")

def get_user_choice():
   while True:
       try:
           choice = int(input("\nEnter your choice (1-7): "))
           if 1 <= choice <= 7:
               return choice
           else:
               print("Invalid choice. Please enter a number between 1 and 7.")
       except ValueError:
           print("Invalid input. Please enter a number.")

def powermeter_stuff():
    #if they choose automated stuff ingest config files otherwise ask for user inputs
    #print(power_meter.query('*IDN?')) #this asks the insturment to print its GPIB address, serial number and firmware version and works.
##BELOW IS OLD CODE FOR CHECKING, ZEROING, AND USING THE POWER METER!#####
#print(power_meter.query('SYST:RINT?'))
#print(power_meter.write('CAL'))
#sleep(20)
#print(power_meter.write('ZE'))
#sleep(20)
#power_meter.write('*TST?') # This makes the machine conduct a self test before beginning
#sleep(20)
#print(power_meter.query('*OPC?'))

#iter =  int(input("How many times do you want to read?"))
#pause = int(input("How long do you want to pause between readings?"))


#end_time = time.time() #this is the time the actual data gathering portion ends
#elapsed_time = end_time - start_time
#print('Execution time:', elapsed_time, 'seconds') #execution time helps dial in the iterations and sleep times

def sig_gen_stuff():
    #if they choose automated stuff ingest config files otherwise ask for user inputs

def spec_an_stuff():
    #if they choose automated stuff ingest config files otherwise ask for user inputs

def write_reports():
    #the code to use various things from the other functions defined here and utilize them to create pdf reports based on analysis
       #BELOW IS SORT OF HOW WE WROTE SOME OF THE CODE TO make one csv
       #We need to turn stuff into a pdf after some analysis. There's gonna be nestinga 
#     with open("powerTest_RunForRecord_2.csv", "w") as file:
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
def main():
   while True:
       display_menu()
       choice = get_user_choice()

       if choice == 1:
           #X-band characterization schema
           print ("X-band frequency characterization beginning now.")
           # ingest config files
           # do testing?

       elif choice == 2:
           #S-band characterization schema
           print ("S-band frequency characterization beginning now.")
           # ingest config files
           # do testing?

       elif choice == 3:
           # X-band G/T schema
           print("X-band G/T")
           #zero and cal PMeter
           #POWER METER CODE
                #write to text file, date_time, power in dB
                #compare to px6? compare with milas code?
           #Generate pdf report with graphs!

       elif choice == 4:
           # G/T schema
           print("S-band G/T")
           #zero and cal PMeter
           #POWER METER CODE as in the function above...
                #write to text file, date_time, power in dB
                #compare to px6? compare with milas code?
           #Generate pdf report with graphs!

       elif choice == 5:
           print("Manual Inputs")
           # proceed with manual inputs. Ask if user wants to use all 3 machines or just one
            #nested loop "Which machines do you want to use?"
           
       elif choice == 6:
           print("Calibrations")
           #test, zero, cal, check equipment
            #nested loop "Which machines do you want to use?"
                #manual calibration inputs
                #no archival results necessary
           
       elif choice == 7:
           print("Below are the archived tests...")
           #print archived tests of various sorts. Should we make a mySQL database?
            #???
           break

if __name__ == "__main__":
   main()


#Appendix A (user manuals as available online for various equipment)
    #power meter:
   #https://naic.edu/~phil/hardware/Misc/powerMeters/E4418-90029_prog_man.pdf
    #signal generator:
   #https://www.keysight.com/us/en/assets/9018-05514/service-manuals/9018-05514.pdf
    #spectrum analyzer:
   #SPECTRUM_ANALYZER_URL

#Coding shortcuts/various commands for Agilent 4418B Power Meter
   #"*IDN?" shows the serial number and firmware version of the power meter
   #"XXXX"
   #"XXXXX"
   #other functionality

#Coding shortcuts/various commands for HP 8563E Spectrum Analyzer
   #"MKA"
   #"MKF"
   #video averaging
   #other functionality

#Coding shortcuts/various commands for HP 8762A Signal Generator
   #description of other choices for the P-string that control frequency, vernier, power level, etc.