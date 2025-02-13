import json
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep


test = pyvisa.ResourceManager()

def choose_device():
    resources = list(test.list_resources())
    for index, resource in enumerate(resources):
        resource_id = "todo"
        try:
            listed_device = test.open_resource(resource)
            query_response: str = listed_device.query("*IDN?")
            # query_response: str = listed_device.query("CF?")
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

def write_to_resource(resource: pyvisa.resources.Resource, message: str) -> int:
    print (f"about to write: {message}")
    response = resource.write(message)
    print(f"received response: {response}   type= {type(response)}")
    return response

def query_resource(resource: pyvisa.resources.Resource, message: str) -> str:
    print (f"about to query: {message}")
    response = resource.query(message)
    print(f"received response: {response}   type= {type(response)}")
    return response

DUT = choose_device()
# for i, v in enumerate(list(test.list_resources())):
#     print(f"[{i+1}] {v}")
# while True:
#     try:
#         device = list(test.list_resources())[int(input("Device Num: "))-1]
#         # device = list(test.list_resources())[4]
#         break
#     except ValueError:
#         print("Please input an integer")

# DUT = test.open_resource(device)

CF = write_to_resource(DUT,"CF 287000000")
units = str(query_resource(DUT,"AUNITS?")).strip()
stFreq = float(query_resource(DUT,"FA?"))
enFreq = float(query_resource(DUT,"FB?"))
traceDataRaw = query_resource(DUT,"TRA?").split(",")
traceData = np.array([float(i) for i in traceDataRaw])
# frequencies = [stFreq+(((enFreq-stFreq)/len(traceData))*i) for i in range(len(traceData))]
frequencies = [round(stFreq+(((enFreq-stFreq)/600)*i)) for i in range(601)]

# exit()
peak = float(DUT.write("MKPK"))
center = float(DUT.query("CF?"))
markerFreq = float(DUT.query("MKF?"))
markerPow = float(DUT.query("MKA?"))

print(f"CF:     {markerFreq}")
print(f"CF POW: {markerPow}")

number_of_iterations = 1000
"""number of times loop is run"""

plt.plot(frequencies, traceData)
plt.xlabel("Frequency [Hz]")
plt.ylabel(f"Amplitude [{units}]")
plt.title(f"Plot {stFreq} Hz - {enFreq} Hz")
plt.ylim(top=10)
plt.yticks()

def save_plot_and_csv(index: int) -> None:
    print(f"SAVING PLOT!!!")
    units = str(query_resource(DUT,"AUNITS?")).strip()
    stFreq = float(query_resource(DUT,"FA?"))
    enFreq = float(query_resource(DUT,"FB?"))
    traceDataRaw = query_resource(DUT,"TRA?").split(",")
    traceData = np.array([float(i) for i in traceDataRaw])
    # frequencies = [stFreq+(((enFreq-stFreq)/len(traceData))*i) for i in range(len(traceData))]
    frequencies = [round(stFreq+(((enFreq-stFreq)/600)*i)) for i in range(601)]
    plt.plot(frequencies, traceData, color="blue")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel(f"Amplitude [{units}]")
    plt.title(f"Plot {stFreq} Hz - {enFreq} Hz\n{datetime.utcnow()}")
    plt.ylim(top=10)
    plt.yticks()
    filename = datetime.utcnow().isoformat(timespec="seconds").replace(":", "_")
    filepath = f"data/lisa_t/{filename}.png"
    print(f"SAVING IMAGE TO {filepath}")

    filepath_json = filepath.replace(".png", ".json")

    dictionary = {}

    timestamp = datetime.utcnow()
    dictionary["timestamp"] = timestamp.isoformat()
    for freq, amp in zip(frequencies, traceData):
        dictionary[freq] = amp
    print(f"SAVING JSON to: {filepath_json}")
    with open(filepath_json, "w") as file:
        json.dump(dictionary, file, indent=2)
    plt.savefig(filepath)
    plt.clf()

timeStamp = datetime.now().timestamp()
with open(f"LISA_T_TEST2.csv", "w") as file:
    file.write("Datetime [UTC],  Center Freq [Hz], Marker Freq [Hz], Marker Power [dBm]\n")
    for index in range (number_of_iterations):
        peak = float(DUT.write("MKPK"))
        center = float(DUT.query("CF?"))
        markerFreq = float(DUT.query("MKF?"))
        markerPow = float(DUT.query("MKA?"))
        message = f"{datetime.utcnow()},{center},{peak},{markerFreq},{markerPow}"
        print(f"{index=}: " + message)
        file.write(message + "\n")
        sleep(1.5)

        if index % 4 == 0:
            save_plot_and_csv(index=index)
# plt.savefig(f"AstroForgePlots/Plot_{titleMod}_{stFreq}-{enFreq}_{timeStamp}.png")

# plt.show()