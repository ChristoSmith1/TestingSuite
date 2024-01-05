# Python standard library package imports should go first:
# Anything from this list: https://docs.python.org/3/library/index.html
import datetime
import time

# You had "from time import sleep", and then in the code, you had "sleep(.1)"
# There's nothing wrong with that, but it's generally better to go
# "import time" and then use "time.sleep(.1)" in your code. This is a concept
# called "namespace segregation" which becomes a bigger deal when you have
# bigger projects. For example, There is a "time.sleep()" and a "threading.sleep()",
# you'll want to keep those things seperate, if you're using both modules.
# That being said, there are a few common exceptions where "from [module] import [thing]"
# is preferred. "pathlib.Path" and everything from the "typing" module are the main ones.
# Like this:
from pathlib import Path
from typing import List
# Third party package imports should go next:
# This is where numpy, pandas, and matplotlib go, if you're using them.
import pyvisa
# Your own module import should go last, if you ever have any:
# import morehead.space_science_center as ssc
# Anything with CAPITAL_LETTERS should be a constant, meaning
# that it won't change. (Note that you can still change it if
# you want. There are no real constants in Python. But you shouldn't.)
#
# pathlib.Path objects are great for dealing with file paths
# I recommend them for literally every use case instead of just using strings
OUTPUT_FILE_PATH: Path = Path("./output.csv")
# Since this is a Path object and not just a string, I can do things like
# OUTPUT_FILE_PATH.absolute() to get the absolute path of this file.
# on my PC (Linux) here, that gives me:

# PosixPath('/home/dmayo/PycharmProjects/playground/christo/output.csv')
# Other things to check out:

# OUTPUT_FILE_PATH.glob("*") # Get all the items in a folder
# OUTPUT_FILE_PATH.rglob("*") # Get all the items in a folder, including all of its child folders
# OUTPUT_FILE_PATH.is_file() # Is this path a file?
# OUTPUT_FILE_PATH.is_dir() # Is this path a folder?
# OUTPUT_FILE_PATH.parent # What folder is this item in?
# OUTPUT_FILE_PATH.exists() # Is there anything at this location


# Write functions that do one simple thing

def write_file_line(

file_path: Path,

line: str,

mode: str="a",

encoding: str="utf8",

) -> None:

"""Write a single line to a file. The line should NOT have a newline at the end.


Encoding will be UTF8 by default. Mode will be "append" by default.


Args:

file_path (Path): File path to write to

line (str): Line to write

mode (str, optional): File write mode. Defaults to "a".

encoding (str, optional): File encoding. Defaults to "utf8".

"""

if not file_path:

return

with open(file_path, mode, encoding=encoding) as file:

file.write(line)

file.write("\n")


def get_value_dummy(

*args,

**kwargs,

) -> float:

"""A dummy function to take the place of `get_value_from_resource`

on PC's without a connection to any pyvisa devices. Always returns -123.456

"""

return -123.456


def get_float_value_from_resource(

resource: pyvisa.resources.MessageBasedResource,

query: str,

) -> float:

"""Send given query to given resource, and interpret the result as a float.

"""

value = float(resource.query(query))

return value


def run_test(

repetitions: int,

delay_seconds: float,

resource: pyvisa.resources.MessageBasedResource,

query: str,

csv_path: Path = OUTPUT_FILE_PATH,

) -> None:

"""Run the test. Repeat `repetitions` times, with a delay of `delay_seconds` seconds.


Saves output to the given CSV path and displays the average on the screen


Args:

repetitions (int): Number of iterations to do

delay_seconds (float): Delay (in seconds) between tests

csv_path (Path): File to output results to. Defaults to OUTPUT_FILE_PATH

"""

print(f"Running test on resource \"{resource}\", with query \"{query}\"")

print(f"Repeating {repetitions} times, with delay of {delay_seconds} seconds.")

if csv_path:

# Create the file and write the header

csv_path.write_text("iso_time,unix_time,power\n", encoding="utf8")

# The above line is exactly the same as:

# with open(csv_path, "w", encoding="utf8") as file:

# file.write("iso_time,unix_time,power\n")


value_list: List[float] = []

for count in range(repetitions):

# I have this "if resource" thing so that I can test (most of)

# this program on my computer by using a dummy value.

# Often a good practice so you can test as much of the program as possible

# before hooking it up to the valuable, resource-limited device

# (I did this for everything in SMC, for example.)

if resource:

# Get the value from the power meter.

# That's one self-contained thing, so it goes in its own function

value = get_float_value_from_resource(

resource=resource,

query=query,

)

else:

print(f"WARNING! No resource, so using dummy value.")

value = get_value_dummy()


# Get the time.

# I'm showing you how to get it in two different formats here,

# But you probably don't need that.

current_time = datetime.datetime.now()

current_time_iso = current_time.isoformat()

current_time_unix = current_time.timestamp()


# Add the value to the list of results so that you can average it

value_list.append(value)


# Write the result to your CSV

write_file_line(

file_path=csv_path,

line=f"{current_time_iso},{current_time_unix},{value}",

)


# Let the user know what's going on!

# Remember that writing to the console is actually very slow, by

# computer standards. If you're trying to repeat this 1,000x per second,

# you won't be able to do that.

# 

# RULE OF THUMB that I use: A print() statement takes about 10 milliseconds to execute

print(f"[{current_time.isoformat()}] iteration #{count+1} of {repetitions}. value={value}")


# Do the delay.

# This is not super-duper precise. If you need to record measurements EXACTLY every 100.0 milliseconds,

# you'll need another approach (and I don't know what that approach would be).

time.sleep(delay_seconds)


# Calculate the average and print it to the screen.

average = sum(value_list) / len(value_list)

print(f"Average is {average}")




# I know that the

# if __name__ == "__main__":

# thing is weird. I know that. It's just how you have to do stuff in Python.

# The idea is that when you RUN the file, Python sets the __name__

# special variable name to the string "__main__", but when you

# IMPORT the file, that doesn't happen.

# So later, when you turn this into a Python module and go

# 

# import christo_power_meter_test

# 

# in some other Python file, all the stuff above (the function definitions,

# etc.) will be done, but the stuff below (actually running a specific test)

# will not be.

#

# The stuff that your script actually DOES should be below this line (and indented).

# 

# If that's confusing, don't worry about it.

if __name__ == "__main__":

# This is some debug info you can put in a script.

# Not mandatory, but can be useful

import sys

import os

print(f"Running Python version {sys.version}")

print(f"Running Python executable {sys.executable}")

python_path = "\n " + "\n ".join(sys.path)

print(f"Python path is {python_path}")

print(f"Excuting file {__file__}")

print(f"PWD is {os.getcwd()}")


# Here's where we first try to connect to the power meter

# This is where the program is most likely to fail,

# So I have this rigged up to where "power_meter" will be set to

# None if it can't be connected, which will trigger using fake

# numbers later.

# THIS IS LIKELY NOT WHAT YOU WANT FOR ACTUAL USE! But it's what

# you have to do if you don't have access to the thing.

try:

# This was originally called "test"

# which is generally a bad name

resource_manager = pyvisa.ResourceManager()


print(f"Available resources:")

for resource in resource_manager.list_resources():

print(f" {resource}")


# This was originally called "DUT", and IDK what that stands for

# In general, longer variable names are better.

# Also, variables in Python should be snake_case, except for constants

# which are CAPITAL_WITH_UNDERSCORES and class names, which are PascalCase

power_meter = resource_manager.open_resource("GPIB0::13::INSTR")

except ValueError as exc:

print(f"ERROR! Unable to connect to power meter. Setting power_meter_resource to None.\nError was {exc}.")

power_meter = None


# Run the test!

run_test(

repetitions=100,

delay_seconds=.1,

resource=power_meter,

query="FETC:POW:AC?",

)