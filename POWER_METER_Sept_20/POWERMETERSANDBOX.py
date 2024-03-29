import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

####### STARTS THE CLOCK ON OPERATION AND CONFIRMS ADDRESS IN EVENT OF MULTIPLE MACHINES #########3

#start_time = time.time() #start time of operations of the actual machine, and reading of data
rm = pyvisa.ResourceManager() #This lookes at all of the GPIB available resources and gives their addresses in a particular format
print(rm.list_resources()) #I want to make it so it lets me CHOOSE which resource I want to use, so that power meter is based on my input "choose insturment [1]etc."
power_meter = rm.open_resource('GPIB1::13::INSTR')
power = round(float(power_meter.query('FETC:POW:AC?')),2)
for i in range(1000):
    print(power)