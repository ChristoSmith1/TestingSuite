import pyvisa
from time import time
from time import sleep
import time
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


####### STARTS THE CLOCK ON OPERATION AND CONFIRMS ADDRESS IN EVENT OF MULTIPLE MACHINES #########
test = pyvisa.ResourceManager()

###################################
def choose_device():
    resources = list(test.list_resources())
    for index, resource in enumerate(resources):
        resource_id = "todo"
        try:
            listed_device = test.open_resource(resource)
            query_response: str = listed_device.query("*IDN?")
            resource_id = query_response.strip()
            # print (f"{query_response = } ")
        except Exception as exc:
            resource_id = "not available"
        print(f"[{index}] {resource} {resource_id}")

    user_input = input("select a number for your device: ")
    user_input_int = int(user_input)
    chosen_device_name = resources[user_input_int]
    chosen_device = test.open_resource(chosen_device_name)
    return chosen_device
    
if __name__ == "__main__":
        # while True:
        #     try:
        #         device = list(test.list_resources())[int(input("Device Num: "))]
        #         break
        #     except ValueError:
        #         print("Please input an integer")

        # power_meter = test.open_resource(device)
    #######################################
    power_meter=choose_device()

    start_time = time.time() #start time of operations of the actual machine, and reading of data
######## USER INPUTS #########
    # number_of_readings =  int(input("How many times do you want to read?")) #This is the number of readings we wish to take
    # pause_between_readings = float(input("How long do you want to pause between readings? Between .1 and 10 seconds"))
    number_of_readings = 30
    pause_between_readings = 1
    array_p = []
    array_t = []
    for i in range(number_of_readings):
            power = round(float(power_meter.query('FETC:POW:AC?')),2)
            array_p.append(power)
            # file.write(f"{datetime.utcnow()},{str(power)}\n")
            array_t.append(datetime.utcnow())
            print(i, datetime.utcnow(), power, "dBm") #printed for user benefit, to see how many iterations are left
            sleep(pause_between_readings)

    print(f"Average = {sum(array_p) / len(array_p):0.2f}")