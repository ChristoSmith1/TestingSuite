import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())

pm = rm.open_resource('GPIB1::13::INSTR')
pm.query('SER?')
#print(pm.query('*IDN?')) #this asks the insturment to print its GPIB address, serial number and firmware version and works.

#print(pm.query('SENS:AVER?'))

#with open("powerTest.txt", "w") as file:
#    while True:
#        power = round(float(pm.query('FETC:POW:AC?')))
#	    write(str(power)+"\n")
#        print(power)