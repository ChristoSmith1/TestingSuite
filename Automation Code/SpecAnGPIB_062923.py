#Christo Smith
#June 29 2023
#This is code roughly based on the work done between Jody Caudill and myself
#The goal is to program, read, and write the functionality of an HP SpecAn through SCPI commands

import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

ResourceList = pyvisa.ResourceManager() #initially called 'test' we need something more explicit
# print(ResourceList.list_resources())

powmet = ResourceList.open_resource("GPIB1::13::INSTR")
#These are harcoded in. What we need to do is have the list printed with GPIB address and then pass particular
#addresses to 'powmet' and 'specan' because it changes based on operating computer
specan = ResourceList.open_resource("GPIB1::18::INSTR")

# j = 2.3

# specan.write("VAVG")
# specan.write(f"CF {j*1000}MHZ")
# specan.write(f"MF {j*1000}MHZ")


def measurePower():
    powmetmeas = []
    for i in range(50):
        power = float(powmet.query("FETC:POW:AC?"))
        powmetmeas.append(power)
        print(power)
        time.sleep(0.1)
   
    specanPow = float(specan.query("MKA?"))

    return np.average(powmetmeas), specanPow, powmetmeas

testMeas = measurePower()
print(testMeas[:2])
print(testMeas[2])