#!/usr/bin/env python3
##########################################
# Duino-Coin Python AVR Miner (v2.3)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
# Import libraries
import socket, threading, time, sys, os
import re, subprocess, configparser, datetime
import locale, json, platform
from pathlib import Path
from signal import signal, SIGINT

# Install pip package automatically
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    os.execl(sys.executable, sys.executable, *sys.argv)

# Return datetime object
def now():
    return datetime.datetime.now()

try:
    # Check if pyserial is installed
    import serial
    import serial.tools.list_ports
except:
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
except:
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
except:
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
except:
    print(
        now().strftime("%H:%M:%S ")
        + 'Pypresence is not installed. '
        + 'Wallet will try to install it. '
        + 'If it fails, please manually install "pypresence" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install("pypresence")

# Global variables
minerVersion = "2.3"  # Version number
timeout = 15  # Socket timeout
resourcesFolder = "AVRMiner_" + str(minerVersion) + "_resources"
shares = [0, 0]
diff = 0
donatorrunning = False
job = ""
debug = "n"
rigIdentifier = "None"
serveripfile = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"  # Serverip file
config = configparser.ConfigParser()
donationlevel = 0
hashrate = 0

# Create resources folder if it doesn't exist
if not os.path.exists(resourcesFolder):
    os.mkdir(resourcesFolder)  

# Check if languages file exists
if not Path(resourcesFolder + "/langs.json").is_file():
    url = "https://raw.githubusercontent.com/revoxhere/duino-coin/master/Resources/AVR_Miner_langs.json"
    r = requests.get(url)
    with open(resourcesFolder + "/langs.json", "wb") as f:
        f.write(r.content)

# Load language file
with open(f"{resourcesFolder}/langs.json", "r", encoding="utf8") as lang_file:
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
# Read language from configfile
else:
    try:  
        config.read(resourcesFolder + "/Miner_config.cfg")
        lang = config["arduminer"]["language"]
    except:
        # If it fails, fallback to english
        lang = "english"

# Get string form language file
def getString(string_name):
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name

# Debug output
def debugOutput(text):
    if debug == "y":
        print(now().strftime(Style.DIM + "%H:%M:%S.%f ") + "DEBUG: " + text)

# Set window title
def title(title):
    if os.name == "nt":
        os.system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()

# server connection
def Connect():
    global masterServer_address, masterServer_port
    while True:
        try:
            try:
                socket.close()
            except:
                pass
            debugOutput("Connecting to " + str(masterServer_address) + str(":") + str(masterServer_port))
            socId = socket.socket()
            # Establish socket connection to the server
            socId.connect((str(masterServer_address), int(masterServer_port)))
            # Get server version
            serverVersion = socId.recv(3).decode()
            debugOutput("Server version: " + serverVersion)
            if (float(serverVersion) <= float(minerVersion)and len(serverVersion) == 3):
                # If miner is up-to-date, display a message and continue
                print(
                    now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
                    now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
        except:
            print(
                now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.RESET_ALL
                + Style.BRIGHT
                + Back.BLUE
                + Fore.WHITE
                + " net0 "
                + Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RED
                + getString("connecting_error")
                + Style.RESET_ALL)
            if debug == "y":
                raise
            time.sleep(5)
    return socId


def connectToAVR(com):
    while True:
        try:
            # Close previous serial connections (if any)
            comConnection.close()
        except:
            pass
        try:
            # Establish serial connection
            comConnection = serial.Serial(
                com,
                115200,
                timeout=5,
                write_timeout=5,
                inter_byte_timeout=5)
            print(
                now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
            return comConnection
        except:
            debugOutput("Error connecting to AVR")
            if debug == "y":
                raise
            print(
                now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.RESET_ALL
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
                + Style.RESET_ALL)
            time.sleep(10)


# SIGINT handler
def handler(signal_received, frame):
    print(
        "\n"
        + now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
        soc.close()
    except:
        pass
    os._exit(0)

# Enable signal handler
signal(SIGINT, handler)

 # Config loading section
def loadConfig(): 
    global pool_address, pool_port, username, donationlevel, avrport, debug, requestedDiff, rigIdentifier

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

        print(Style.RESET_ALL + Fore.YELLOW + getString("ports_message"))
        portlist = serial.tools.list_ports.comports()
        for port in portlist:
            print(Style.RESET_ALL + Style.BRIGHT + Fore.WHITE + "  " + str(port))
        print(Style.RESET_ALL + Fore.YELLOW + getString("ports_notice"))

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
        with open(str(resourcesFolder) + "/Miner_config.cfg", "w") as configfile:
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


def Greeting():  # Greeting message depending on time
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
            debugOutput("OS is Windows, downloading developer donation executable")
            url = "https://github.com/revoxhere/duino-coin/blob/useful-tools/DonateExecutableWindows.exe?raw=true"
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable.exe", "wb") as f:
                f.write(r.content)
    elif os.name == "posix":
        # Initial miner executable section
        if not Path(resourcesFolder + "/Donate_executable").is_file():  
            debugOutput("OS is Windows, downloading developer donation executable")
            url = "https://github.com/revoxhere/duino-coin/blob/useful-tools/DonateExecutableLinux?raw=true"
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable", "wb") as f:
                f.write(r.content)

def restart_miner():
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except:
        print("Permission error")


def Donate():
    global donationlevel, donatorrunning, donateExecutable
    if os.name == "nt":
        cmd = (
            "cd "
            + resourcesFolder
            + "& Donate_executable.exe -o "
            + "stratum+tcp://mine.nlpool.nl:6033 "
            + "-u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR "
            + "-p AVRmW,c=XMG,d=6 -s 4 -e ")
    elif os.name == "posix":
        cmd = (
            "cd "
            + resourcesFolder
            + "&& chmod +x Donate_executable && "
            + "./Donate_executable -o "
            + "stratum+tcp://mine.nlpool.nl:6033 "
            + "-u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR "
            + "-p AVRmL,c=XMG,d=6 -s 4 -e ")
    if int(donationlevel) <= 0:
        print(
            now().strftime(Style.DIM + "%H:%M:%S ")
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
        time.sleep(5)
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
            donateExecutable = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL)
            print(
                now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.RESET_ALL
                + Style.BRIGHT
                + Back.GREEN
                + Fore.WHITE
                + " sys0 "
                + Back.RESET
                + Fore.RED
                + getString("thanks_donation")
                + Style.RESET_ALL)

# Initialize Discord rich presence
def initRichPresence():
    global RPC
    try:
        RPC = Presence(808056068113563701)
        RPC.connect()
        debugOutput("Discord rich presence initialized")
    except:  # Discord not launched
        pass

# Update rich presence status
def updateRichPresence():
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
                large_text="Duino-Coin, a coin that can be mined with almost everything, including AVR boards",
                buttons=[
                    {"label": "Learn more", "url": "https://duinocoin.com"},
                    {"label": "Discord Server", "url": "https://discord.gg/k48Ht5y"}])
        except:  # Discord not launched
            pass
        time.sleep(15)  # 15 seconds to respect discord's rate limit

# Mining section
def AVRMine(com):  
    global hash_count, hashrate, masterServer_address, masterServer_port
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
                    break
            except:  # If there was an error with grabbing data from GitHub
                print(
                    now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.BLUE
                    + Fore.WHITE
                    + " net"
                    + str(''.join(filter(str.isdigit, com)))
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + getString("data_error"))
                if debug == "y":
                    raise
                time.sleep(10)

        while True:
            # Connect to the server
            socId = Connect()
            # Connect to the serial port
            comConnection = connectToAVR(com)
            try:
                # Receive ready signal from AVR
                ready = comConnection.readline().decode()
                debugOutput("Received start word (" + str(ready) + ")")
                print(
                    now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.RESET_ALL
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
            except:
                print(
                    now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Back.MAGENTA
                    + Fore.WHITE
                    + " usb"
                    + str(''.join(filter(str.isdigit, com)))
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + getString("mining_avr_connection_error"))
                comConnection = connectToAVR(com)

        while True:
            while True:
                try:
                    # Send job request
                    debugOutput("Requested job")
                    socId.send(
                        bytes(
                            "JOB,"
                            + str(username)
                            + ","
                            + str(requestedDiff),
                            encoding="utf8")) 
                    job = socId.recv(85).decode()  # Retrieve work
                    job = job.split(",")  # Split received data

                    # Check if username is correct
                    try:
                        if job[1] == "This user doesn't exist":
                            print(
                                now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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

                        # If job received, continue
                        elif job[0] and job[1] and job[2]:
                            diff = int(job[2])
                            debugOutput("Job received: " + str(job))
                            break
                    except:
                        restart_miner()
                except:
                    restart_miner()

            while True:
                # Write data to AVR board
                while True:
                    try:
                        # Send start word
                        comConnection.write(bytes("start\n", encoding="utf8"))  
                        debugOutput("Written start word")
                        # Send job to AVR
                        comConnection.write(
                            bytes(
                                str(job[0]
                                    + "\n"
                                    + job[1]
                                    + "\n"
                                    + job[2]
                                    + "\n"),
                                encoding="utf8"))
                        debugOutput("Sent job to arduino")
                        break
                    except:
                        try:
                            comConnection.close()
                        except:
                            pass
                        comConnection = connectToAVR(com)
                        debugOutput("Reconnecting to avr")
                wrong_results = 0
                while True:
                    try:
                        result = comConnection.readline().decode()  # Read the result
                        if result == "":
                            wrong_results += 1
                            if wrong_results > 5:
                                wrong_avr_result = False
                                print(
                                    now().strftime(Style.DIM + "%H:%M:%S ")
                                    + Style.RESET_ALL
                                    + Style.BRIGHT
                                    + Back.GREEN
                                    + Fore.WHITE
                                    + " sys0 "
                                    + Back.RESET
                                    + Fore.RED
                                    + getString("mining_avr_not_responding"))
                                try:
                                    os.execl(sys.executable, sys.executable, *sys.argv)
                                except:
                                    print("Permission error")
                        else:
                            break
                    except:
                        print(
                            now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.RESET_ALL
                            + Style.BRIGHT
                            + Back.GREEN
                            + Fore.WHITE
                            + " sys0 "
                            + Back.RESET
                            + Fore.RED
                            + getString("mining_avr_connection_error"))
                        time.sleep(5)
                        try:
                            os.execl(sys.executable, sys.executable, *sys.argv)
                        except:
                            print("Permission error")

                try:
                    # Receive result from AVR
                    result = result.split(",")
                    debugOutput("Received result (" + str(result[0]) + ")")
                    debugOutput("Received time (" + str(result[1]) + ")")
                    # Convert AVR time to seconds
                    computetime = round(int(result[1]) / 1000000, 3)  
                    # Calculate hashrate
                    hashrate = round(int(result[0]) / int(result[1]) * 1000000, 2)
                    debugOutput("Calculated hashrate (" + str(hashrate) + ")")
                except:
                    break
                try:
                    # Send result to the server
                    socId.send(
                        bytes(
                            str(result[0])
                            + ","
                            + str(hashrate)
                            + ",Official AVR Miner v"
                            + str(minerVersion)
                            + ","
                            + str(rigIdentifier),
                            encoding="utf8")) 
                except:
                    restart_miner()

                while True:
                    try:
                        responsetimetart = now()
                        # Get feedback
                        feedback = socId.recv(48).decode()  
                        responsetimestop = now()
                        # Measure server ping
                        ping = str(int((responsetimestop - responsetimetart).microseconds / 1000))
                        feedback_not_received = False
                        debugOutput("Successfully retrieved feedback")
                        break
                    except:
                        restart_miner()

                if feedback == "GOOD":
                    # If result was correct
                    shares[0] = (shares[0] + 1)
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
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

                elif feedback == "BLOCK":
                    # If block was found
                    shares[0] = (shares[0] + 1)
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
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
                    shares[1] = (shares[1] + 1)
                    title(
                        getString("duco_avr_miner")
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
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
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
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
    init(autoreset=True)  # Colorama
    title(getString("duco_avr_miner") + str(minerVersion) + ")")
    try:
        loadConfig()  # Load config file or create new one
        debugOutput("Config file loaded")
    except:
        print(
            now().strftime(Style.DIM + "%H:%M:%S ")
            + Style.RESET_ALL
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
            + Style.RESET_ALL)
        if debug == "y":
            raise
        time.sleep(10)
        os._exit(1)
    try:
        Greeting()  # Display greeting message
        debugOutput("Greeting displayed")
    except:
        if debug == "y":
            raise
    try:
        Donate()  # Start donation thread
    except:
        if debug == "y":
            raise

    try:
        # Launch avr duco mining threads
        for port in avrport:
            threading.Thread(
                target=AVRMine,
                args=(port,)).start()  
    except:
        raise

    # Discord rich presence threads
    try:
        initRichPresence()
        threading.Thread(target=updateRichPresence).start()
    except:
        if debug == "y":
            raise
