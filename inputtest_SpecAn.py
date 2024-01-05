import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

#iter = input("How many times do you want to read?")
#pause = input("How long do you want to pause between readings?")
#print(iter)

rm = pyvisa.ResourceManager()
print(rm.list_resources())
specan = rm.open_resource('GPIB1::18::INSTR')
print(specan.query('CF?'))

#print(specan.query('FA?'))

#while True:
#    command = input("> ")#.strip("\n")
#    try:
        # if "?" in command:
        #     output = specan.query(command)
        #     print(output)
        # else:
        #     specan.write(command)
#        output = specan.query(command)
#        print(output)
#    except KeyboardInterrupt:
#        specan.close()
#        break


#####RESOURCES#######
###https://testworld.com/wp-content/uploads/user-guide-keysight-agilent-8561e-8562e-8563e-8564e-8565e-8561ec-8562ec-8563ec-8564ec-8565ec-spectrum-analyzers.pdf
###ESPECIALLY AROUND PAGE 303 in Chapeter 5. Great stuff.

