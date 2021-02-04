import os
import sys

board = input("Enter your board name (Uno, Nano, Mega): ")
port = input("Enter the port where the board is: ")

def windows():
    if board == "Nano" or "Uno":
        os.system(f".\\avrdude\\avrdude.exe -c arduino -P {port} -p atmega328p -b 115200 -U flash:w:avrminer.hex")
        print("Done!")
        exit()
    elif board == "Mega":
        mega_model = input("Enter your mega model (1280, 2560): ")
        if mega_model == "1280" or "2560":
            os.system("cd Arduino_Code")
            os.system(f"\\avrdude\\avrdude.exe -c arduino -P {port} -p atmega{mega_model} -b 115200 -U flash:w:avrminer.hex")
            print("Done!")
            exit()
        else:
            print("Your mega model isn't correct, please try again.")
            exit()
    else:
        print("Your board isn't correct, please re-run the script and enter the correct options")
        exit()

def linux():
    if board == "Nano" or "Uno":
        os.system(f"avrdude -c arduino -P {port} -p atmega328p -b 115200 -U flash:w:avrminer.hex")
        print("Done!")
        exit()
    elif board == "Mega":
        mega_model = input("Enter your mega model (1280, 2560): ")
        if mega_model == "1280" or "2560":
            os.system("cd Arduino_Code")
            os.system(f"avrdude -c arduino -P {port} -p atmega{mega_model} -b 115200 -U flash:w:avrminer.hex")
            print("Done!")
            exit()
        else:
            print("Your mega model isn't correct, please try again.")
            exit()
    else:
        print("Your board isn't correct, please re-run the script and enter the correct options")
        exit()

if sys.platform == "win32":
    windows()
else:
    linux()

