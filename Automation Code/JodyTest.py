import pyvisa
from time import sleep
from time import time

test = pyvisa.ResourceManager()
print(test.list_resources())
power_meter = test.open_resource('GPIB1::13::INSTR')

with open("powerTest_RunForRecord_1.csv", "w") as file:
     for i in range(20):
         power = round(float(power_meter.query('FETC:POW:AC?')),2)
         file.write(f"{time()},{str(power)}\n")
         print(time(), power)
#         sleep(3)
def write_csv(output_file: str, text: str) -> None:
    with open(output_file, "a", encoding="utf8") as file:
        file.write(text)

output_file = "output.csv"
with open(output_file, "w") as file:
    file.write("")


array = []
for i in range(100):
    power = float(power_meter.query('FETC:POW:AC?'))
    array.append(power)
    write_csv(output_file, f"{time()},{power}\n")
    print(i, time(), power)
    sleep(.05)

print(f"Average = {sum(array) / len(array):0.2f}")