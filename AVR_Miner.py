#!/usr/bin/env python3
##########################################
# Duino-Coin Python AVR Miner (v2.4)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
# Import libraries
import socket
import threading
import time
import sys
import os
import re
import subprocess
import configparser
import datetime
import locale
import json
import platform
from pathlib import Path
from signal import signal, SIGINT


def install(package):
    # Install pip package automatically
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    if os.name == "nt":
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    else:
        os.execl(sys.executable, sys.executable, *sys.argv)


def now():
    # Return datetime object
    return datetime.datetime.now()


try:
    # Check if pyserial is installed
    import serial
    import serial.tools.list_ports
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + 'Pyserial is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "pyserial" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install("pyserial")

try:
    # Check if colorama is installed
    from colorama import init, Fore, Back, Style
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + 'Colorama is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "colorama" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install("colorama")

try:
    # Check if requests is installed
    import requests
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + 'Requests is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "requests" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install("requests")

try:
    # Check if pypresence is installed
    from pypresence import Presence
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + 'Pypresence is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "pypresence" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install("pypresence")

# Global variables
minerVersion = "2.4"  # Version number
timeout = 15  # Socket timeout
resourcesFolder = "AVRMiner_" + str(minerVersion) + "_resources"
shares = [0, 0]
diff = 0
donatorrunning = False
job = ""
debug = "n"
rigIdentifier = "None"
# Serverip file
serveripfile = ("https://raw.githubusercontent.com/"
                + "revoxhere/"
                + "duino-coin/gh-pages/serverip.txt")
config = configparser.ConfigParser()
donationlevel = 0
hashrate = 0

# Create resources folder if it doesn't exist
if not os.path.exists(resourcesFolder):
    os.mkdir(resourcesFolder)

# Check if languages file exists
if not Path(resourcesFolder + "/langs.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/master/Resources/"
           + "AVR_Miner_langs.json")
    r = requests.get(url)
    with open(resourcesFolder + "/langs.json", "wb") as f:
        f.write(r.content)

# Load language file
with open(resourcesFolder + "/langs.json", "r", encoding="utf8") as lang_file:
    lang_file = json.load(lang_file)

# OS X invalid locale hack
if platform.system() == 'Darwin':
    if locale.getlocale()[0] is None:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Check if miner is configured, if it isn't, autodetect language
if not Path(resourcesFolder + "/Miner_config.cfg").is_file():
    locale = locale.getdefaultlocale()[0]
    if locale.startswith("es"):
        lang = "spanish"
    elif locale.startswith("sk"):
        lang = "slovak"
    elif locale.startswith("ru"):
        lang = "russian"
    elif locale.startswith("pl"):
        lang = "polish"
    elif locale.startswith("fr"):
        lang = "french"
    else:
        lang = "english"
else:
    try:
        # Read language from configfile
        config.read(resourcesFolder + "/Miner_config.cfg")
        lang = config["arduminer"]["language"]
    except Exception:
        # If it fails, fallback to english
        lang = "english"


def getString(string_name):
    # Get string form language file
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name


def debugOutput(text):
    # Debug output
    if debug == "y":
        print(
            Style.RESET_ALL
            + now().strftime(Style.DIM + "%H:%M:%S.%f ")
            + "DEBUG: "
            + str(text))


def title(title):
    # Window title
    if os.name == "nt":
        os.system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def Connect():
    # Server connection
    global masterServer_address, masterServer_port
    while True:
        try:
            try:
                socket.close()
            except Exception:
                pass
            debugOutput("Connecting to "
                        + str(masterServer_address)
                        + str(":")
                        + str(masterServer_port))
            socConn = socket.socket()
            # Establish socket connection to the server
            socConn.connect((str(masterServer_address), int(masterServer_port)))
            # Get server version
            serverVersion = socConn.recv(3).decode().rstrip("\n")
            debugOutput("Server version: " + serverVersion)
            if (float(serverVersion) <= float(minerVersion)
                    and len(serverVersion) == 3):
                # If miner is up-to-date, display a message and continue
                print(
                    Style.RESET_ALL
                    + now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.BLUE
                    + Fore.WHITE
                    + " net0 "
                    + Back.RESET
                    + Fore.YELLOW
                    + getString("connected")
                    + Style.RESET_ALL
                    + Fore.WHITE
                    + getString("connected_server")
                    + str(serverVersion)
                    + ")")
                break
            else:
                print(
                    Style.RESET_ALL
                    + now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.GREEN
                    + Fore.WHITE
                    + " sys0 "
                    + Back.RESET
                    + Fore.RED
                    + " Miner is outdated (v"
                    + minerVersion
                    + "),"
                    + Style.RESET_ALL
                    + Fore.RED
                    + getString("server_is_on_version")
                    + serverVersion
                    + getString("update_warning"))
                time.sleep(10)
                break
        except Exception as e:
            print(
                Style.RESET_ALL
                + now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.BRIGHT
                + Back.BLUE
                + Fore.WHITE
                + " net0 "
                + Back.RESET
                + Style.BRIGHT
                + Fore.RED
                + getString("connecting_error")
                + Style.NORMAL
                + " ("
                + str(e)
                + ")")
            debugOutput("Connection error: " + str(e))
            time.sleep(10)
            restart_miner()
    return socConn


def connectToAVR(com):
    while True:
        try:
            # Close previous serial connections (if any)
            comConn.close()
        except Exception:
            pass

        try:
            # Establish serial connection
            comConn = serial.Serial(
                com,
                baudrate=115200,
                timeout=5)
            print(
                now().strftime(
                    Style.RESET_ALL
                    + Style.DIM
                    + "%H:%M:%S ")
                + Style.RESET_ALL
                + Style.BRIGHT
                + Back.MAGENTA
                + Fore.WHITE
                + " usb"
                + str(''.join(filter(str.isdigit, com)))
                + " "
                + Style.RESET_ALL
                + Style.BRIGHT
                + Fore.GREEN
                + getString("board_on_port")
                + str(com)
                + getString("board_is_connected")
                + Style.RESET_ALL)
            return comConn

        except Exception as e:
            debugOutput("Error connecting to AVR: " + str(e))
            print(
                Style.RESET_ALL
                + now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.BRIGHT
                + Back.MAGENTA
                + Fore.WHITE
                + " usb"
                + str(''.join(filter(str.isdigit, com)))
                + " "
                + Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RED
                + getString("board_connection_error")
                + str(com)
                + getString("board_connection_error2")
                + Style.NORMAL
                + " ("
                + str(e)
                + ")")
            time.sleep(10)


def handler(signal_received, frame):
    # SIGINT handler
    print("\n"
          + now().strftime(
              Style.RESET_ALL
              + Style.DIM
              + "%H:%M:%S ")
          + Style.BRIGHT
          + Back.GREEN
          + Fore.WHITE
          + " sys0 "
          + Back.RESET
          + Fore.YELLOW
          + getString("sigint_detected")
          + Style.NORMAL
          + Fore.WHITE
          + getString("goodbye"))
    try:
        # Close previous socket connection (if any)
        socket.close()
    except Exception:
        pass
    os._exit(0)


# Enable signal handler
signal(SIGINT, handler)


def loadConfig():
    # Config loading section
    global pool_address
    global pool_port
    global username
    global donationlevel
    global avrport
    global debug
    global requestedDiff
    global rigIdentifier

    # Initial configuration section
    if not Path(str(resourcesFolder) + "/Miner_config.cfg").is_file():
        print(
            Style.BRIGHT
            + getString("basic_config_tool")
            + resourcesFolder
            + getString("edit_config_file_warning"))

        print(
            Style.RESET_ALL
            + getString("dont_have_account")
            + Fore.YELLOW
            + getString("wallet")
            + Fore.WHITE
            + getString("register_warning"))

        username = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_username")
            + Fore.WHITE
            + Style.BRIGHT)

        print(Style.RESET_ALL
              + Fore.YELLOW
              + getString("ports_message"))
        portlist = serial.tools.list_ports.comports()
        for port in portlist:
            print(Style.RESET_ALL
                  + Style.BRIGHT
                  + Fore.WHITE
                  + "  "
                  + str(port))
        print(Style.RESET_ALL
              + Fore.YELLOW
              + getString("ports_notice"))

        avrport = ""
        while True:
            avrport += input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_avrport")
                + Fore.WHITE
                + Style.BRIGHT)
            confirmation = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_anotherport")
                + Fore.WHITE
                + Style.BRIGHT)
            if confirmation == "y" or confirmation == "Y":
                avrport += ","
            else:
                break

        requestedDiffSelection = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_higherdiff")
            + Fore.WHITE
            + Style.BRIGHT)
        if requestedDiffSelection == "y" or requestedDiffSelection == "Y":
            requestedDiff = "ESP32"
        else:
            requestedDiff = "AVR"

        rigIdentifier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_rig_identifier")
            + Fore.WHITE
            + Style.BRIGHT)
        if rigIdentifier == "y" or rigIdentifier == "Y":
            rigIdentifier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_rig_name")
                + Fore.WHITE
                + Style.BRIGHT)
        else:
            rigIdentifier = "None"

        donationlevel = "0"
        if os.name == "nt" or os.name == "posix":
            donationlevel = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_donation_level")
                + Fore.WHITE
                + Style.BRIGHT)

        # Check wheter donationlevel is correct
        donationlevel = re.sub("\D", "", donationlevel)
        if donationlevel == '':
            donationlevel = 1
        if float(donationlevel) > int(5):
            donationlevel = 5
        if float(donationlevel) < int(0):
            donationlevel = 0

        # Format data
        config["arduminer"] = {
            "username": username,
            "avrport": avrport,
            "donate": donationlevel,
            "language": lang,
            "identifier": rigIdentifier,
            "difficulty": requestedDiff,
            "debug": "n"}

        # Write data to file
        with open(str(resourcesFolder)
                  + "/Miner_config.cfg", "w") as configfile:
            config.write(configfile)

        avrport = avrport.split(",")
        print(Style.RESET_ALL + getString("config_saved"))

    else:  # If config already exists, load from it
        config.read(str(resourcesFolder) + "/Miner_config.cfg")
        username = config["arduminer"]["username"]
        avrport = config["arduminer"]["avrport"]
        avrport = avrport.split(",")
        donationlevel = config["arduminer"]["donate"]
        debug = config["arduminer"]["debug"]
        rigIdentifier = config["arduminer"]["identifier"]
        requestedDiff = config["arduminer"]["difficulty"]


def Greeting():
    # Greeting message depending on time
    global greeting
    print(Style.RESET_ALL)

    current_hour = time.strptime(time.ctime(time.time())).tm_hour

    if current_hour < 12:
        greeting = getString("greeting_morning")
    elif current_hour == 12:
        greeting = getString("greeting_noon")
    elif current_hour > 12 and current_hour < 18:
        greeting = getString("greeting_afternoon")
    elif current_hour >= 18:
        greeting = getString("greeting_evening")
    else:
        greeting = getString("greeting_back")

    # Startup message
    print(
        " ‖ "
        + Fore.YELLOW
        + Style.BRIGHT
        + getString("banner")
        + Style.RESET_ALL
        + Fore.WHITE
        + " (v"
        + str(minerVersion)
        + ") 2019-2021")
    print(" ‖ " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")

    print(
        " ‖ "
        + Fore.WHITE
        + getString("avr_on_port")
        + Style.BRIGHT
        + Fore.YELLOW
        + " ".join(avrport))

    if os.name == "nt" or os.name == "posix":
        print(
            " ‖ "
            + Fore.WHITE
            + getString("donation_level")
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donationlevel))
    print(
        " ‖ "
        + Fore.WHITE
        + getString("algorithm")
        + Style.BRIGHT
        + Fore.YELLOW
        + "DUCO-S1A @ "
        + str(requestedDiff)
        + " diff")

    print(
        Style.RESET_ALL
        + " ‖ "
        + Fore.WHITE
        + getString("rig_identifier")
        + Style.BRIGHT
        + Fore.YELLOW
        + rigIdentifier)

    print(
        " ‖ "
        + Fore.WHITE
        + str(greeting)
        + ", "
        + Style.BRIGHT
        + Fore.YELLOW
        + str(username)
        + "!\n")

    if os.name == "nt":
        # Initial miner executable section
        if not Path(resourcesFolder + "/Donate_executable.exe").is_file():
            debugOutput(
                "OS is Windows, downloading developer donation executable")
            url = ("https://github.com/"
                   + "revoxhere/"
                   + "duino-coin/blob/useful-tools/"
                   + "DonateExecutableWindows.exe?raw=true")
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable.exe", "wb") as f:
                f.write(r.content)
    elif os.name == "posix":
        # Initial miner executable section
        if not Path(resourcesFolder + "/Donate_executable").is_file():
            debugOutput(
                "OS is Windows, downloading developer donation executable")
            url = ("https://github.com/"
                   + "revoxhere/"
                   + "duino-coin/blob/useful-tools/"
                   + "DonateExecutableLinux?raw=true")
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable", "wb") as f:
                f.write(r.content)


def restart_miner():
    try:
        if donatorrunning:
            donateExecutable.terminate()
    except Exception as e:
        print("Error closing donate executable: " + str(e))
    try:
        if os.name == "nt":
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        else:
            os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print("Error when restarting miner: " + str(e))


def Donate():
    global donationlevel
    global donatorrunning
    global donateExecutable
    if os.name == "nt":
        cmd = (
            "cd "
            + resourcesFolder
            + "& Donate_executable.exe "
            + "-o stratum+tcp://xmg.minerclaim.net:7008 "
            + "-u revox.donate "
            + "-p x -s 4 -e ")
    elif os.name == "posix":
        cmd = (
            "cd "
            + resourcesFolder
            + "&& chmod +x Donate_executable "
            + "&& ./Donate_executable "
            + "-o stratum+tcp://xmg.minerclaim.net:7008 "
            + "-u revox.donate "
            + "-p x -s 4 -e ")
    if int(donationlevel) <= 0:
        print(
            now().strftime(
                Style.DIM
                + "%H:%M:%S ")
            + Style.RESET_ALL
            + Style.BRIGHT
            + Back.GREEN
            + Fore.WHITE
            + " sys0 "
            + Back.RESET
            + Fore.YELLOW
            + getString("free_network_warning")
            + Style.BRIGHT
            + Fore.YELLOW
            + getString("donate_warning")
            + Style.RESET_ALL
            + Fore.GREEN
            + "https://duinocoin.com/donate"
            + Style.BRIGHT
            + Fore.YELLOW
            + getString("learn_more_donate")
            + Style.RESET_ALL)
        time.sleep(10)
    elif donatorrunning == False:
        if int(donationlevel) == 5:
            cmd += "95"
        elif int(donationlevel) == 4:
            cmd += "75"
        elif int(donationlevel) == 3:
            cmd += "50"
        elif int(donationlevel) == 2:
            cmd += "20"
        elif int(donationlevel) == 1:
            cmd += "10"
        if int(donationlevel) > 0:
            debugOutput(getString("starting_donation"))
            donatorrunning = True
            # Launch CMD as subprocess
            donateExecutable = subprocess.Popen(
                cmd, shell=True, stderr=subprocess.DEVNULL)
            print(
                now().strftime(
                    Style.DIM
                    + "%H:%M:%S ")
                + Style.RESET_ALL
                + Style.BRIGHT
                + Back.GREEN
                + Fore.WHITE
                + " sys0 "
                + Back.RESET
                + Fore.RED
                + getString("thanks_donation")
                + Style.RESET_ALL)


def initRichPresence():
    # Initialize Discord rich presence
    global RPC
    try:
        RPC = Presence(808056068113563701)
        RPC.connect()
        debugOutput("Discord rich presence initialized")
    except Exception:
        # Discord not launched
        pass


def updateRichPresence():
    # Update rich presence status
    startTime = int(time.time())
    while True:
        try:
            RPC.update(
                details="Hashrate: " + str(hashrate) + " H/s",
                start=startTime,
                state="Acc. shares: "
                + str(shares[0])
                + "/"
                + str(shares[0] + shares[1]),
                large_image="ducol",
                large_text="Duino-Coin, "
                + "a coin that can be mined with almost everything, "
                + "including AVR boards",
                buttons=[
                    {"label": "Learn more",
                     "url": "https://duinocoin.com"},
                    {"label": "Discord Server",
                     "url": "https://discord.gg/k48Ht5y"}])
        except Exception:
            # Discord not launched
            pass
        # 15 seconds to respect Discord's rate limit
        time.sleep(15)


def AVRMine(com):
    # Mining section
    errorCounter = 0
    global hashrate
    global masterServer_address
    global masterServer_port
    while True:
        # Grab server IP and port
        while True:
            try:
                # Use request to grab data from raw github file
                res = requests.get(serveripfile, data=None)
                if res.status_code == 200:
                    # Read content and split into lines
                    content = (res.content.decode().splitlines())
                    masterServer_address = content[0]  # Line 1 = pool address
                    masterServer_port = content[1]  # Line 2 = pool port
                    debugOutput(
                        "Retrieved pool IP: "
                        + masterServer_address
                        + ":"
                        + str(masterServer_port))
                    # Connect to the server
                    socConn = Connect()
                    break
            except Exception as e:
                # If there was an error with grabbing data from GitHub
                print(
                    Style.RESET_ALL
                    + now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.BLUE
                    + Fore.WHITE
                    + " net"
                    + str(''.join(filter(str.isdigit, com)))
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + getString("data_error")
                    + Style.NORMAL
                    + " (git err: "
                    + str(e)
                    + ")")
                debugOutput("GitHub error: " + str(e))
                time.sleep(10)

        while True:
            try:
                # Connect to the serial port
                comConn = connectToAVR(com)
                print(
                    Style.RESET_ALL
                    + now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.GREEN
                    + Fore.WHITE
                    + " sys"
                    + str(''.join(filter(str.isdigit, com)))
                    + " "
                    + Back.RESET
                    + Fore.YELLOW
                    + getString("mining_start")
                    + Style.RESET_ALL
                    + Fore.WHITE
                    + getString("mining_algorithm")
                    + str(com)
                    + ")")
                break

            except Exception as e:
                print(
                    Style.RESET_ALL
                    + now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.MAGENTA
                    + Fore.WHITE
                    + " usb"
                    + str(''.join(filter(str.isdigit, com)))
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + getString("mining_avr_connection_error")
                    + Style.NORMAL
                    + " (avr connection err: "
                    + str(e)
                    + ")")
                time.sleep(5)

        while True:
            while True:
                try:
                    # Send job request
                    debugOutput("Requested job from the server")
                    socConn.send(
                        bytes(
                            "JOB,"
                            + str(username)
                            + ","
                            + str(requestedDiff),
                            encoding="utf8"))
                    # Retrieve work
                    job = socConn.recv(85).decode()
                    # Split received data
                    job = job.rstrip("\n").split(",")

                    # Check if username is correct
                    if job[1] == "This user doesn't exist":
                        print(
                            Style.RESET_ALL
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.RESET_ALL
                            + Style.BRIGHT
                            + Back.BLUE
                            + Fore.WHITE
                            + " sys0 "
                            + Back.RESET
                            + Fore.RED
                            + getString("mining_user")
                            + Fore.WHITE
                            + str(username)
                            + Fore.RED
                            + getString("mining_not_exist")
                            + getString("mining_not_exist_warning"))
                        time.sleep(10)

                    # If job was received, continue
                    elif job[0] and job[1] and job[2]:
                        diff = int(job[2])
                        debugOutput("Job received: " + " ".join(job))
                        break
                except Exception as e:
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.BLUE
                        + Fore.WHITE
                        + " net0 "
                        + Back.RESET
                        + Style.BRIGHT
                        + Fore.RED
                        + getString("connecting_error")
                        + Style.NORMAL
                        + " (net err: "
                        + str(e)
                        + ")")
                    debugOutput("Connection error: " + str(e))
                    time.sleep(10)
                    restart_miner()

            while True:
                while True:
                    try:
                        # Write data to AVR board
                        comConn.write(bytes(
                            str(job[0]
                                + ","
                                + job[1]
                                + ","
                                + job[2]
                                + ","),
                            encoding="utf8"))
                        debugOutput("Sent job to AVR")

                        # Read the result
                        result = comConn.readline().decode()
                        # print(repr(result))
                        result = result.rstrip("\n").split(",")

                        if result != "" and result != " ":
                            debugOutput("Received from AVR: "
                                        + " ".join(result))
                            break
                        else:
                            raise Exception("Empty data")

                    except Exception as e:
                        errorCounter += 1
                        if errorCounter >= 5:
                            debugOutput(
                                "Reconnecting to AVR - too many errors")
                            print(
                                Style.RESET_ALL
                                + now().strftime(
                                    Style.DIM
                                    + "%H:%M:%S ")
                                + Style.BRIGHT
                                + Back.MAGENTA
                                + Fore.WHITE
                                + " usb"
                                + str(''.join(filter(str.isdigit, com)))
                                + " "
                                + Back.RESET
                                + Fore.RED
                                + getString("mining_avr_not_responding")
                                + Style.NORMAL
                                + " (errorCounter > 5: "
                                + str(e)
                                + ")")
                            comConn = connectToAVR(com)
                            errorCounter = 0
                        debugOutput(
                            "Exception with to serial: " + str(e))
                        time.sleep(0.5)

                try:
                    debugOutput("Received result (" + str(result[0]) + ")")
                    debugOutput("Received time (" + str(result[1]) + ")")
                    ducos1result = result[0]
                    # Convert AVR time to seconds
                    computetime = round(int(result[1]) / 1000000, 3)
                    # Calculate hashrate
                    hashrate = round(
                        int(result[0]) / int(result[1]) * 1000000, 2)
                    debugOutput("Calculated hashrate (" + str(hashrate) + ")")
                    try:
                        chipID = result[2]
                        debugOutput(
                            "Received chip ID (" + str(result[2]) + ")")
                        # Check if user is using the latest Arduino code
                        # This is not used yet anywhere, but will soon be added
                        # as yet another a security measure in the Kolka V4
                        # security system for identifying AVR boards
                        if (not chipID.startswith("DUCOID")
                                or len(chipID) != 21):
                            raise Exception("Wrong start string")
                    except Exception:
                        print(
                            Style.RESET_ALL
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.WHITE
                            + " usb"
                            + str(''.join(filter(str.isdigit, com)))
                            + " "
                            + Back.RESET
                            + Fore.YELLOW
                            + " Possible incorrect chipID!"
                            + " This will cause problems with the future"
                            + " release of Kolka security system")
                        chipID = "None"
                except Exception as e:
                    debugOutput("Error splitting data: " + str(e))
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " usb"
                        + str(''.join(filter(str.isdigit, com)))
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + getString("mining_avr_connection_error")
                        + Style.NORMAL
                        + " (err splitting avr data: "
                        + str(e)
                        + ")")
                    time.sleep(5)
                    break

                try:
                    # Send result to the server
                    socConn.send(
                        bytes(
                            str(ducos1result)
                            + ","
                            + str(hashrate)
                            + ",Official AVR Miner (DUCO-S1A) v"
                            + str(minerVersion)
                            + ","
                            + str(rigIdentifier)
                            + ","
                            + str(chipID),
                            encoding="utf8"))
                except Exception as e:
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.BLUE
                        + Fore.WHITE
                        + " net0 "
                        + Back.RESET
                        + Style.BRIGHT
                        + Fore.RED
                        + getString("connecting_error")
                        + Style.NORMAL
                        + " ("
                        + str(e)
                        + ")")
                    debugOutput("Connection error: " + str(e))
                    time.sleep(10)
                    restart_miner()

                while True:
                    try:
                        responsetimetart = now()
                        # Get feedback
                        feedback = socConn.recv(48).decode().rstrip("\n")
                        responsetimestop = now()
                        # Measure server ping
                        timeDelta = (responsetimestop -
                                     responsetimetart).microseconds
                        ping = round(timeDelta / 1000)
                        debugOutput("Successfully retrieved feedback: " +
                                    str(feedback) + " with ping: " + str(ping))
                        break
                    except Exception:
                        print(
                            Style.RESET_ALL
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.BRIGHT
                            + Back.BLUE
                            + Fore.WHITE
                            + " net0 "
                            + Back.RESET
                            + Style.BRIGHT
                            + Fore.RED
                            + getString("connecting_error")
                            + Style.NORMAL
                            + " ("
                            + str(e)
                            + ")")
                        print("Error parsing response: " +
                              str(e) + ", restarting miner")
                        restart_miner()

                if feedback == "GOOD":
                    # If result was correct
                    shares[0] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " usb"
                        + str(''.join(filter(str.isdigit, com)))
                        + " "
                        + Back.RESET
                        + Fore.GREEN
                        + " ✓"
                        + getString("accepted")
                        + Fore.WHITE
                        + str(int(shares[0]))
                        + "/"
                        + str(int(shares[0] + shares[1]))
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0]
                                   / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ∙ "
                        + str(f"%01.3f" % float(computetime))
                        + "s"
                        + Style.NORMAL
                        + " ∙ "
                        + Fore.BLUE
                        + Style.BRIGHT
                        + str(round(hashrate))
                        + " H/s"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " @ diff "
                        + str(diff)
                        + " ∙ "
                        + Fore.CYAN
                        + "ping "
                        + str(f"%02.0f" % int(ping))
                        + "ms")
                    break  # Repeat

                elif feedback == "BLOCK":
                    # If block was found
                    shares[0] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " usb"
                        + str(''.join(filter(str.isdigit, com)))
                        + " "
                        + Back.RESET
                        + Fore.CYAN
                        + " ✓"
                        + getString("block_found")
                        + Fore.WHITE
                        + str(int(shares[0]))
                        + "/"
                        + str(int(shares[0] + shares[1]))
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0]
                                   / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ∙ "
                        + str(f"%01.3f" % float(computetime))
                        + "s"
                        + Style.NORMAL
                        + " ∙ "
                        + Fore.BLUE
                        + Style.BRIGHT
                        + str(int(hashrate))
                        + " H/s"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " @ diff "
                        + str(diff)
                        + " ∙ "
                        + Fore.CYAN
                        + "ping "
                        + str(f"%02.0f" % int(ping))
                        + "ms")
                    break

                else:
                    # If result was incorrect
                    shares[1] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        Style.RESET_ALL
                        + now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " usb"
                        + str(''.join(filter(str.isdigit, com)))
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + " ✗"
                        + getString("rejected")
                        + Fore.WHITE
                        + str(int(shares[0]))
                        + "/"
                        + str(int(shares[0] + shares[1]))
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0]
                                   / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ∙ "
                        + str(f"%01.3f" % float(computetime))
                        + "s"
                        + Style.NORMAL
                        + " ∙ "
                        + Fore.BLUE
                        + Style.BRIGHT
                        + str(int(hashrate))
                        + " H/s"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " @ diff "
                        + str(diff)
                        + " ∙ "
                        + Fore.CYAN
                        + "ping "
                        + str(f"%02.0f" % int(ping))
                        + "ms")
                    break  # Repeat
                break


if __name__ == "__main__":
    # Colorama
    init(autoreset=True)
    # Window title
    title(getString("duco_avr_miner") + str(minerVersion) + ")")

    try:
        # Load config file or create new one
        loadConfig()
        debugOutput("Config file loaded")
    except Exception as e:
        print(
            Style.RESET_ALL
            + now().strftime(Style.DIM + "%H:%M:%S ")
            + Style.BRIGHT
            + Back.GREEN
            + Fore.WHITE
            + " sys0 "
            + Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RED
            + getString("load_config_error")
            + resourcesFolder
            + getString("load_config_error_warning")
            + Style.NORMAL
            + " ("
            + str(e)
            + ")")
        debugOutput("Error reading configfile: " + str(e))
        time.sleep(10)
        os._exit(1)

    try:
        # Display greeting message
        Greeting()
        debugOutput("Greeting displayed")
    except Exception as e:
        debugOutput("Error displaying greeting message: " + str(e))

    try:
        # Start donation thread
        Donate()
    except Exception as e:
        debugOutput("Error launching donation thread: " + str(e))

    try:
        # Launch avr duco mining threads
        for port in avrport:
            threading.Thread(
                target=AVRMine,
                args=(port,)).start()
    except Exception as e:
        debugOutput("Error launching AVR thead(s): " + str(e))

    try:
        # Discord rich presence threads
        initRichPresence()
        threading.Thread(
            target=updateRichPresence).start()
    except Exception as e:
        debugOutput("Error launching Discord RPC thead: " + str(e))
