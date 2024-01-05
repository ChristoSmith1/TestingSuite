""""
import pandas as pd
  
# reading two csv files
AzEl = pd.read_csv('TestCombineA.csv')
PowerReading = pd.read_csv('TestCombineB.csv')
  
# using merge function by setting how='inner'
rawdata_together = pd.merge(AzEl, PowerReading, on='Time', how='inner')
  
  # displaying result
print(AzEl)
print(PowerReading)
print(rawdata_together)

#MergedFile = pd.write_csv()
#We're not here yet
"""

def display_menu():
   print("\nMenu:")
   print("1. Option 1")
   print("2. Option 2")
   print("3. Option 3")
   print("4. Option 4")
   print("5. Exit")

def get_user_choice():
   while True:
       try:
           choice = int(input("\nEnter your choice (1-5): "))
           if 1 <= choice <= 5:
               return choice
           else:
               print("Invalid choice. Please enter a number between 1 and 5.")
       except ValueError:
           print("Invalid input. Please enter a number.")

def main():
   while True:
       display_menu()
       choice = get_user_choice()

       if choice == 1:
           # Perform actions for option 1
           print("You selected Option 1")
       elif choice == 2:
           # Perform actions for option 2
           print("You selected Option 2")
       elif choice == 3:
           # Perform actions for option 3
           print("You selected Option 3")
       elif choice == 4:
           # Perform actions for option 4
           print("You selected Option 4")
       elif choice == 5:
           print("Exiting program...")
           break

if __name__ == "__main__":
   main()