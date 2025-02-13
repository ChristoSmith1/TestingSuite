#Jody Caudill, June 9 2023
import pyvisa
import time
import matplotlib.pyplot as plt

test = pyvisa.ResourceManager()
print(test.list_resources())

DUT = test.open_resource('GPIB1::18::INSTR')

with open("charactizerationAutomation\specan.cnfg", "r") as file:
    data = file.readlines()

    FreqCenter = float(data[0].split(":")[1].strip("\n"))*10e6
    Span = float(data[1].split(":")[1].strip("\n"))*10e6
    stepSize = float(data[2].split(":")[1].strip("\n"))

minFreq = FreqCenter - Span/2
maxFreq = FreqCenter + Span/2

numPoints = Span/stepSize

print(FreqCenter)
print(Span)
print(stepSize)
print(minFreq)
print(maxFreq)
print(numPoints)

points2Check = [minFreq+stepSize*i for i in range(int(numPoints))]

print(round(points2Check[0]/10e6,4))

pointPowers = []

for i in points2Check:
    DUT.write(f"MKF {round(i/10e6,4)}MHZ")
    pointPowers.append(float(DUT.query(f"MKA?")))

plt.plot(points2Check, pointPowers)
plt.xlabel("Frequencies [Hz]")
plt.ylabel("Powers [dBm]")
plt.show()


# CF 2GHZ      :sets the Center Frequency to 2 GHz
# CHANPRW?:    :gets channel power
# CHPWRBW 2GHZ :changes the channel power bandwidth to 2 GHz
# ERR?         :returns the queue of error codes
# FA 2GHZ      :sets the start frequency to 2 GHz
# FB 3GHZ      :sets the end frequency to 3 GHz
# MF?          :Querys the marker Frequency
# MF           :Same as MF?
# MKF 3GHZ     :Sets Marker Frequency
# MKNOISE?     :Measures the noise (Unsure if this outputs anything more than 1 or 0)
# MKA?         :Querys the power at the marker
# SP 1MHZ      :Sets the span to 1 MHz