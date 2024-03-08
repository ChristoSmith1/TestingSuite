import pyvisa
from datetime import datetime as dt
import time
import numpy as np
from os import system

#Jody Caudill March 7th 2024

def commandFrequency(freq: int):
    mag = "GFEDCBA@"
    symbol = mag[int(np.log10(freq)-3)]
    frequency = str(freq).ljust(8,"0")
    return f"{symbol}{frequency}j1"

def commandFrequencyGHz(freq: float):
    mag = "GFEDCBA@"
    symbol = mag[int(np.log10(freq*1e9)-3)]
    frequency = str(int(freq*1e9)).ljust(8,"0")
    return f"{symbol}{frequency}j0"

def commandPower(power: int):
    powerCommands = "0123456789:;"
    # if abs(power) < 50:
        # raise Exception("Power is too high must be <= -50")
    # if abs(power) > 110:
        # raise Exception("Power is too low must be >= -110")
    symbol = powerCommands[abs(int(np.floor(power/10)))]
    return f"K{symbol}"

def changeTerminal(string: str):
    system("cls")
    print(string)

def getIntInput(Query):
    try:
        answer = int(input(Query))
    except ValueError:
        print("Please only input integers")
    except KeyboardInterrupt:
        exit()
    return answer


test = pyvisa.ResourceManager()


specAn = test.open_resource('GPIB2::18::INSTR')
sigGen = test.open_resource('GPIB2::20::INSTR')

with open(r"BPFChar.cnfg", "r") as file:
    Values = [float(i.split(":")[1]) for i in file.readlines()[:8]]
    startFreq = int(round(Values[0]*1e9, -1))
    endFreq = int(round(Values[1]*1e9, -1))
    stepSize = int(Values[2]*1e6)
    span = int(Values[3])*1000
    startPow = int(Values[4])
    endPow = int(Values[5])
    powers = list(range(startPow, endPow+10, 10))
    numSidePeaks = int(Values[6])
    videoAveraging = int(Values[7])
    numSteps = round((endFreq-startFreq)/stepSize)
    frequencies = [int(round(startFreq+(stepSize*i),-1)) for i in range(numSteps)]
    rawTimeRemaining = 17*len(frequencies)*len(powers)
    hours = np.floor(rawTimeRemaining/3600)
    minutes = np.floor(((rawTimeRemaining/3600)-hours)*60)
    seconds = (((rawTimeRemaining/3600)-hours)*60-minutes)*60
    print(f"Starting Frequency: {startFreq} Hz\nEnding Frequency: {endFreq} Hz\nSpan: {span} KHz\nStep Size: {stepSize} Hz\nStarting Power: {startPow} dBm\nEnding Power: {endPow} dBm\n# of Steps: {numSteps}\nEstimate: {hours:0.0f} H {minutes:0.0f} M {seconds:0.0f} S")
    if input("Proceed [Y/N]: ").upper().strip("\n") in ["N"]:
        exit()


with open(r"BPFTest4.csv", "w") as file:
    file.write("time, Power [dBm], Center Frequency [Hz], ")
    for i in range(1, int(numSidePeaks/2)+1):
        file.write(f"Polling Frequency [Hz] {i}, Polling Frequency Power [dBm] {i}, ")
    file.write("Center Peak [Hz], Center Peak power [dBm], ")
    for i in range(int(numSidePeaks/2)+1, numSidePeaks+1):
        file.write(f"Polling Frequency [Hz] {i}, Polling Frequency Power [dBm] {i}, ")
    file.write("\n")

count = 0
totalPoints = len(frequencies)*len(powers)
changeTerminal(f"{(count/totalPoints)*100:0.1f}% {count}/{totalPoints}\nTime Remaining: Calculating")
# changeTerminal(f"{(count/totalPoints)*100:0.1f}% [{str('#'*int(20*(count/totalPoints))).ljust(20)}]")

specAn.write(f"SP {span}HZ")
for setPow in powers:
    for j in frequencies:
        startTime = time.perf_counter()
        with open(r"BPFTest4.csv", "a") as file:
            pollingFrequencies = [int(round((span*(-(numSidePeaks/2)+i))/(numSidePeaks+1))+j) for i in range(numSidePeaks+1)]
            sigGen.write(commandFrequencyGHz(j/1e9))
            sigGen.write(commandPower(setPow))
            sigGen.write("L0") # Vernier Nob Command
            specAn.write(f"CF {round(j/1e6, )}MHZ")
            # specAn.write(f"VAVG {videoAveraging}")
            time.sleep(2)

            pollFrequencies = []
            pollPowers = []

            for i in pollingFrequencies:
                specAn.write(f"mkf {i}HZ")
                # time.sleep(1)
                pollFrequencies.append(float(specAn.query("MF?")))
                pollPowers.append(float(specAn.query("MKA?")))
            specAn.write(f"mkf {pollFrequencies[int(len(pollFrequencies)/2)]}HZ")
            specAn.write("MKPK")
            pollFrequencies[int(numSidePeaks/2)] = float(specAn.query("MF?")) #The issue is the spectrum analyzer does not see 0 Hz as a peak
            pollPowers[int(numSidePeaks/2)] = float(specAn.query("MKA?"))

            potentialPeaks = [0 for j in range(numSidePeaks+1)]
            potentialPeakPowers = [0 for j in range(numSidePeaks+1)]

            for i in list(range(int(numSidePeaks/2)+1))[::-1]:
                specAn.write("MKPK NL")
                potentialPeaks[i] = float(specAn.query("MF?"))
                potentialPeakPowers[i] = float(specAn.query("MKA?"))
            specAn.write(f"mkf {pollFrequencies[int(len(pollFrequencies)/2)]}HZ")
            specAn.write("mkpk")
            for i in list(range(int(numSidePeaks/2)+2, numSidePeaks)):
                specAn.write("MKPK NR")
                potentialPeaks[i] = float(specAn.query("MF?"))
                potentialPeakPowers[i] = float(specAn.query("MKA?"))        
            
            for ind, val in enumerate(potentialPeaks): # Replaces points with detected side peaks.
                for k, v in enumerate(pollFrequencies):
                    if val <= v + span/(numSidePeaks+1) and val >= v - span/(numSidePeaks+1):
                        if k == int(len(pollFrequencies)/2):
                            # print("continued")
                            continue
                        pollFrequencies[k] = val
                        pollPowers[k] = potentialPeakPowers[ind]


            file.write(f"{dt.now()}, {setPow}, {j}")
            for freq, pow in zip(pollFrequencies, pollPowers):
                file.write(f", {freq:0.0f}, {pow}")
            file.write("\n")

            count += 1
            endTime = time.perf_counter()
            rawTimeRemaining = (endTime-startTime)*(totalPoints-count)
            hours = np.floor(rawTimeRemaining/3600)
            minutes = np.floor(((rawTimeRemaining/3600)-hours)*60)
            seconds = (((rawTimeRemaining/3600)-hours)*60-minutes)*60
            changeTerminal(f"{(count/totalPoints)*100:0.1f}% {count}/{totalPoints}\nTime Remaining: {hours:0.0f} H {minutes:0.0f} M {seconds:0.0f} S")
            # changeTerminal(f"{(count/totalPoints)*100:0.1f}% [{str('#'*int(20*(count/totalPoints))).ljust(20)}]\nTime Remaining: {hours:0.0f} H {minutes:0.0f} M {seconds:0.0f} S")
