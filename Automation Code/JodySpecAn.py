import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np

test = pyvisa.ResourceManager()
print(test.list_resources())

#powmet = test.open_resource("GPIB1::13::INSTR")
specan = test.open_resource("GPIB2::18::INSTR")

# j = 2.3

# specan.write("VAVG")
# specan.write(f"CF {j*1000}MHZ")
# specan.write(f"MF {j*1000}MHZ")


def measurePower():
    powmetmeas = []
    for i in range(50):

        # MAYO: The below line refers to `powmet`, which does not exist
        power = float(powmet.query("FETC:POW:AC?"))  # noqa: F821
        powmetmeas.append(power)
        print(power)
        time.sleep(0.1)
   
    specanPow = float(specan.query("MKA?"))

    return np.average(powmetmeas), specanPow, powmetmeas

testMeas = measurePower()
print(testMeas[:2])
print(testMeas[2])