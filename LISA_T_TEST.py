import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep

#GOAL, have this run on a loop wherein it creates a .csv of a SpecAn reading at a single instant with frequencies and powers
#then have it create a visual trace in the plotting portion and save it as "Mission_DateTime_TracePlot_#.png" or whatever the standard 
#output of python is. Then do that again 1 minute later whether a plot that is showing has been closed or not

specan = pyvisa.ResourceManager()

for i, v in enumerate(list(specan.list_resources())):
    print(f"[{i+1}] {v}")
while True:
    try:
        # device = list(test.list_resources())[int(input("Device Num: "))-1]
        device = list(specan.list_resources())[4]
        break
    except ValueError:
        print("Please input an integer")

DUT = specan.open_resource(device)
#DUT = Device Under Test

# CF = DUT.write("CF=22680000")
units = str(DUT.query("AUNITS?")).strip()
stFreq = float(DUT.query("FA?"))
enFreq = float(DUT.query("FB?"))
traceDataRaw = DUT.query("TRA?").split(",")
traceData = np.array([float(i) for i in traceDataRaw])
# frequencies = [stFreq+(((enFreq-stFreq)/len(traceData))*i) for i in range(len(traceData))]
frequencies = [round(stFreq+(((enFreq-stFreq)/600)*i)) for i in range(601)]

peak = float(DUT.write("MKPK"))
center = float(DUT.query("CF?"))
markerFreq = float(DUT.query("MKF?"))
markerPow = float(DUT.query("MKA?"))

print(f"CF:     {markerFreq}")
print(f"CF POW: {markerPow}")

timed = 1000

# plt.plot(frequencies, traceData)
# plt.xlabel("Frequency [Hz]")
# plt.ylabel(f"Amplitude [{units}]")
# plt.title(f"Plot {stFreq} Hz - {enFreq} Hz")
# plt.ylim(top=10)
# plt.yticks()

timeStamp = datetime.now().timestamp()
with open(f"LISA_T_TEST2.csv", "w") as file:
    file.write("Datetime [UTC],  Center Freq [Hz], Marker Freq [Hz], Marker Power [dBm]\n")
    for i in range (timed):
        # peak = float(DUT.write("MKPK"))
        # center = float(DUT.query("CF?"))
        # markerFreq = float(DUT.query("MKF?"))
        # markerPow = float(DUT.query("MKA?"))
        file.write(f"{datetime.utcnow()},{center},{peak},{markerFreq},{markerPow}\n")
        sleep(1.5)
# plt.savefig(f"AstroForgePlots/Plot_{titleMod}_{stFreq}-{enFreq}_{timeStamp}.png")

plt.show()