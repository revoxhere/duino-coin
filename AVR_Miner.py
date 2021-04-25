#!/usr/bin/env python3
##########################################
# Duino-Coin Python AVR Miner (v2.45)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
# Import libraries
import sys
from configparser import ConfigParser
from datetime import datetime
from json import load as jsonload
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
from os import _exit, execl, mkdir
from os import name as osname
from os import path
from os import system as ossystem
from pathlib import Path
from platform import system
from re import sub
from signal import SIGINT, signal
from socket import socket
from subprocess import DEVNULL, Popen, check_call
from threading import Thread as thrThread
from threading import Lock
from time import ctime, sleep, strptime, time
import select


def install(package):
    # Install pip package automatically
    check_call([sys.executable, "-m", "pip", "install", package])
    execl(sys.executable, sys.executable, *sys.argv)


def now():
    # Return datetime object
    return datetime.now()


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
    from colorama import Back, Fore, Style, init
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
MINER_VER = "2.45"  # Version number
SOCKET_TIMEOUT = 30
AVR_TIMEOUT = 7
RESOURCES_DIR = "AVRMiner_" + str(MINER_VER) + "_resources"
shares = [0, 0]
diff = 0
donator_running = False
job = ""
debug = "n"
rig_identifier = "None"
# Serverip file
server_ip_file = ("https://raw.githubusercontent.com/"
                  + "revoxhere/"
                  + "duino-coin/gh-pages/serverip.txt")
donation_level = 0
hashrate = 0
config = ConfigParser()
thread_lock = Lock()

# Create resources folder if it doesn't exist
if not path.exists(RESOURCES_DIR):
    mkdir(RESOURCES_DIR)

# Check if languages file exists
if not Path(RESOURCES_DIR + "/langs.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/master/Resources/"
           + "AVR_Miner_langs.json")
    r = requests.get(url)
    with open(RESOURCES_DIR + "/langs.json", "wb") as f:
        f.write(r.content)

# Load language file
with open(RESOURCES_DIR + "/langs.json", "r", encoding="utf8") as lang_file:
    lang_file = jsonload(lang_file)

# OS X invalid locale hack
if system() == 'Darwin':
    if getlocale()[0] is None:
        setlocale(LC_ALL, 'en_US.UTF-8')

# Check if miner is configured, if it isn't, autodetect language
try:
    if not Path(RESOURCES_DIR + "/Miner_config.cfg").is_file():
        locale = getdefaultlocale()[0]
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
        elif locale.startswith("tr"):
            lang = "turkish"
        elif locale.startswith("zh"):
            lang = "chinese_simplified"
        else:
            lang = "english"
    else:
        try:
            # Read language from configfile
            config.read(RESOURCES_DIR + "/Miner_config.cfg")
            lang = config["arduminer"]["language"]
        except Exception:
            # If it fails, fallback to english
            lang = "english"
except:
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
    if osname == "nt":
        # Windows systems
        ossystem("title " + title)
    else:
        # Most standard terminals
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def Connect():
    # Server connection
    global masterServer_address
    global masterServer_port
    global SOCKET_TIMEOUT
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
            socConn = socket()
            socConn.settimeout(SOCKET_TIMEOUT)
            # Establish socket connection to the server
            socConn.connect(
                (str(masterServer_address), int(masterServer_port)))
            # Get server version
            ready = select.select([socConn], [], [], SOCKET_TIMEOUT)
            if ready[0]:
                serverVersion = socConn.recv(10).decode().rstrip("\n")
            debugOutput("Server version: " + serverVersion)
            if (float(serverVersion) <= float(MINER_VER)
                    and len(serverVersion) == 3):
                # If miner is up-to-date, display a message and continue
                prettyPrint(
                    "net0",
                    getString("connected")
                    + Style.NORMAL
                    + Fore.RESET
                    + getString("connected_server")
                    + str(serverVersion)
                    + ")",
                    "success")
                break
            else:
                prettyPrint(
                    "sys0",
                    " Miner is outdated (v"
                    + MINER_VER
                    + ") -"
                    + getString("server_is_on_version")
                    + serverVersion
                    + Style.NORMAL
                    + Fore.RESET
                    + getString("update_warning"),
                    "warning")
                sleep(10)
                break
        except Exception as e:
            prettyPrint(
                "net0",
                getString("connecting_error")
                + Style.NORMAL
                + " ("
                + str(e)
                + ")",
                "error")
            debugOutput("Connection error: " + str(e))
            sleep(10)
    return socConn


def connectToAVR(com):
    global AVR_TIMEOUT
    try:
        # Close previous serial connections (if any)
        comConn.close()
    except Exception:
        pass

    # Establish serial connection
    comConn = serial.Serial(
        com,
        baudrate=115200,
        timeout=AVR_TIMEOUT)
    prettyPrint(
        "usb"
        + str(''.join(filter(str.isdigit, com))),
        getString("board_on_port")
        + Fore.YELLOW
        + str(com)
        + Style.NORMAL
        + Fore.RESET
        + getString("board_is_connected"),
        "success")
    return comConn


def handler(signal_received, frame):
    # SIGINT handler
    prettyPrint(
        "sys0",
        getString("sigint_detected")
        + Style.NORMAL
        + Fore.RESET
        + getString("goodbye"),
        "warning")
    try:
        # Close previous socket connection (if any)
        socket.close()
    except Exception:
        pass
    _exit(0)


# Enable signal handler
signal(SIGINT, handler)


def loadConfig():
    # Config loading section
    global username
    global donation_level
    global avrport
    global debug
    global requestedDiff
    global rig_identifier

    # Initial configuration section
    if not Path(str(RESOURCES_DIR) + "/Miner_config.cfg").is_file():
        print(
            Style.BRIGHT
            + getString("basic_config_tool")
            + RESOURCES_DIR
            + getString("edit_config_file_warning"))

        print(
            Style.RESET_ALL
            + getString("dont_have_account")
            + Fore.YELLOW
            + getString("wallet")
            + Fore.RESET
            + getString("register_warning"))

        username = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_username")
            + Fore.RESET
            + Style.BRIGHT)

        print(Style.RESET_ALL
              + Fore.YELLOW
              + getString("ports_message"))
        portlist = serial.tools.list_ports.comports()
        for port in portlist:
            print(Style.RESET_ALL
                  + Style.BRIGHT
                  + Fore.RESET
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
                + Fore.RESET
                + Style.BRIGHT)
            confirmation = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_anotherport")
                + Fore.RESET
                + Style.BRIGHT)
            if confirmation == "y" or confirmation == "Y":
                avrport += ","
            else:
                break

        requestedDiffSelection = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_higherdiff")
            + Fore.RESET
            + Style.BRIGHT)
        if requestedDiffSelection == "y" or requestedDiffSelection == "Y":
            requestedDiff = "ESP32"
        else:
            requestedDiff = "AVR"

        rig_identifier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_rig_identifier")
            + Fore.RESET
            + Style.BRIGHT)
        if rig_identifier == "y" or rig_identifier == "Y":
            rig_identifier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_rig_name")
                + Fore.RESET
                + Style.BRIGHT)
        else:
            rig_identifier = "None"

        donation_level = "0"
        if osname == "nt" or osname == "posix":
            donation_level = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_donation_level")
                + Fore.RESET
                + Style.BRIGHT)

        # Check wheter donation_level is correct
        donation_level = sub(r"\D", "", donation_level)
        if donation_level == '':
            donation_level = 1
        if float(donation_level) > int(5):
            donation_level = 5
        if float(donation_level) < int(0):
            donation_level = 0

        # Format data
        config["arduminer"] = {
            "username": username,
            "avrport": avrport,
            "donate": donation_level,
            "language": lang,
            "identifier": rig_identifier,
            "difficulty": requestedDiff,
            "debug": "n"}

        # Write data to file
        with open(str(RESOURCES_DIR)
                  + "/Miner_config.cfg", "w") as configfile:
            config.write(configfile)

        avrport = avrport.split(",")
        print(Style.RESET_ALL + getString("config_saved"))

    else:  # If config already exists, load from it
        config.read(str(RESOURCES_DIR) + "/Miner_config.cfg")
        username = config["arduminer"]["username"]
        avrport = config["arduminer"]["avrport"]
        avrport = avrport.split(",")
        donation_level = config["arduminer"]["donate"]
        debug = config["arduminer"]["debug"]
        rig_identifier = config["arduminer"]["identifier"]
        requestedDiff = config["arduminer"]["difficulty"]


def Greeting():
    # Greeting message depending on time
    global greeting
    print(Style.RESET_ALL)

    current_hour = strptime(ctime(time())).tm_hour

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
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Fore.YELLOW
        + Style.BRIGHT
        + getString("banner")
        + Style.RESET_ALL
        + Fore.MAGENTA
        + " (v"
        + str(MINER_VER)
        + ") "
        + Fore.RESET
        + "2019-2021")

    print(
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Style.NORMAL
        + Fore.MAGENTA
        + "https://github.com/revoxhere/duino-coin")

    print(
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + getString("avr_on_port")
        + Style.BRIGHT
        + Fore.YELLOW
        + " ".join(avrport))

    if osname == "nt" or osname == "posix":
        print(
            Style.DIM
            + Fore.MAGENTA
            + " ‖ "
            + Style.NORMAL
            + Fore.RESET
            + getString("donation_level")
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donation_level))
    print(
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + getString("algorithm")
        + Style.BRIGHT
        + Fore.YELLOW
        + "DUCO-S1A @ "
        + str(requestedDiff)
        + " diff")

    print(
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + getString("rig_identifier")
        + Style.BRIGHT
        + Fore.YELLOW
        + rig_identifier)

    print(
        Style.DIM
        + Fore.MAGENTA
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + str(greeting)
        + ", "
        + Style.BRIGHT
        + Fore.YELLOW
        + str(username)
        + "!\n")

    if osname == "nt":
        # Initial miner executable section
        if not Path(RESOURCES_DIR + "/Donate_executable.exe").is_file():
            debugOutput(
                "OS is Windows, downloading developer donation executable")
            url = ("https://github.com/"
                   + "revoxhere/"
                   + "duino-coin/blob/useful-tools/"
                   + "DonateExecutableWindows.exe?raw=true")
            r = requests.get(url)
            with open(RESOURCES_DIR + "/Donate_executable.exe", "wb") as f:
                f.write(r.content)
    elif osname == "posix":
        # Initial miner executable section
        if not Path(RESOURCES_DIR + "/Donate_executable").is_file():
            debugOutput(
                "OS is *nix, downloading developer donation executable")
            url = ("https://github.com/"
                   + "revoxhere/"
                   + "duino-coin/blob/useful-tools/"
                   + "DonateExecutableLinux?raw=true")
            r = requests.get(url)
            with open(RESOURCES_DIR + "/Donate_executable", "wb") as f:
                f.write(r.content)


def restart_miner():
    try:
        if donator_running:
            donateExecutable.terminate()
    except Exception as e:
        prettyPrint(
            "sys0",
            "Error closing donate executable"
            + Style.NORMAL
            + Fore.RESET
            + " ("
            + str(e)
            + ")",
            "error")
    try:
        execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        prettyPrint(
            "sys0",
            "Error restarting miner"
            + " ("
            + str(e)
            + ")",
            "error")


def Donate():
    global donation_level
    global donator_running
    global donateExecutable

    if osname == "nt":
        cmd = (
            "cd "
            + RESOURCES_DIR
            + "& Donate_executable.exe "
            + "-o stratum+tcp://xmg.minerclaim.net:7008 "
            + "-u revox.donate "
            + "-p x -s 4 -e ")

    elif osname == "posix":
        cmd = (
            "cd "
            + RESOURCES_DIR
            + "&& chmod +x Donate_executable "
            + "&& ./Donate_executable "
            + "-o stratum+tcp://xmg.minerclaim.net:7008 "
            + "-u revox.donate "
            + "-p x -s 4 -e ")

    if int(donation_level) <= 0:
        prettyPrint(
            "sys0",
            Fore.YELLOW
            + getString("free_network_warning")
            + getString("donate_warning")
            + Fore.GREEN
            + "https://duinocoin.com/donate"
            + Fore.YELLOW
            + getString("learn_more_donate"),
            "warning")
        sleep(5)

    elif donator_running == False:
        if int(donation_level) == 5:
            cmd += "50"
        elif int(donation_level) == 4:
            cmd += "40"
        elif int(donation_level) == 3:
            cmd += "30"
        elif int(donation_level) == 2:
            cmd += "20"
        elif int(donation_level) == 1:
            cmd += "10"
        if int(donation_level) > 0:
            debugOutput(getString("starting_donation"))
            donator_running = True
            # Launch CMD as subprocess
            donateExecutable = Popen(
                cmd, shell=True, stderr=DEVNULL)
            prettyPrint(
                "sys0",
                getString("thanks_donation"),
                "warning")


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
    startTime = int(time())
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
        sleep(15)


def prettyPrint(messageType, message, state):
    # Print output messages in the DUCO "standard"
    # Usb/net/sys background
    if messageType.startswith("net"):
        background = Back.BLUE
    elif messageType.startswith("usb"):
        background = Back.MAGENTA
    if messageType.startswith("sys"):
        background = Back.GREEN

    # Text color
    if state == "success":
        color = Fore.GREEN
    elif state == "warning":
        color = Fore.YELLOW
    else:
        color = Fore.RED

    with thread_lock:
        print(Style.RESET_ALL
              + Fore.WHITE
              + now().strftime(Style.DIM + "%H:%M:%S ")
              + Style.BRIGHT
              + background
              + " "
              + messageType
              + " "
              + Back.RESET
              + color
              + Style.BRIGHT
              + message
              + Style.NORMAL
              + Fore.RESET)


def AVRMine(com):
    # Mining section
    errorCounter = 0
    global hashrate
    global masterServer_address
    global masterServer_port
    global MINER_VER
    global SOCKET_TIMEOUT
    while True:
        # Grab server IP and port
        while True:
            try:
                # Use request to grab data from raw github file
                res = requests.get(server_ip_file, data=None)
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
                prettyPrint(
                    "net"
                    + str(''.join(filter(str.isdigit, com))),
                    getString("data_error")
                    + Style.NORMAL
                    + Fore.RESET
                    + " (git err: "
                    + str(e)
                    + ")",
                    "error")
                debugOutput("GitHub error: " + str(e))
                sleep(10)

        while True:
            try:
                # Connect to the serial port
                comConn = connectToAVR(com)
                prettyPrint(
                    "sys"
                    + str(''.join(filter(str.isdigit, com))),
                    getString("mining_start")
                    + Style.NORMAL
                    + Fore.RESET
                    + getString("mining_algorithm")
                    + str(com)
                    + ")",
                    "success")
                break

            except Exception as e:
                prettyPrint(
                    "usb"
                    + str(''.join(filter(str.isdigit, com))),
                    getString("mining_avr_connection_error")
                    + Style.NORMAL
                    + Fore.RESET
                    + " (avr connection err: "
                    + str(e)
                    + ")",
                    "error")
                sleep(10)

        while True:
            while True:
                try:
                    # Send job request
                    debugOutput("Requested job from the server")
                    socConn.sendall(
                        bytes(
                            "JOB,"
                            + str(username)
                            + ","
                            + str(requestedDiff),
                            encoding="utf8"))
                    # Retrieve work
                    ready = select.select([socConn], [], [], SOCKET_TIMEOUT)
                    if ready[0]:
                        job = socConn.recv(100).decode()
                    # Split received data
                    job = job.rstrip("\n").split(",")

                    # Check if username is correct
                    if job[1] == "This user doesn't exist":
                        prettyPrint(
                            "net"
                            + str(''.join(filter(str.isdigit, com))),
                            getString("mining_user")
                            + str(username)
                            + getString("mining_not_exist")
                            + Style.NORMAL
                            + Fore.RESET
                            + getString("mining_not_exist_warning"),
                            "error")
                        sleep(10)

                    # If job was received, continue
                    elif job[0] and job[1] and job[2]:
                        diff = int(job[2])
                        debugOutput("Job received: " + " ".join(job))
                        break
                except Exception as e:
                    prettyPrint(
                        "net"
                        + str(''.join(filter(str.isdigit, com))),
                        getString("connecting_error")
                        + Style.NORMAL
                        + Fore.RESET
                        + " (net err: "
                        + str(e)
                        + ")",
                        "error")
                    debugOutput("Connection error: " + str(e))
                    sleep(10)
                    restart_miner()

            while True:
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

                            if result != "" and result[0] and result[1]:
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
                                prettyPrint(
                                    "usb"
                                    + str(''.join(filter(str.isdigit, com))),
                                    getString("mining_avr_not_responding")
                                    + Style.NORMAL
                                    + Fore.RESET
                                    + " (errorCounter > 5: "
                                    + str(e)
                                    + ")",
                                    "error")
                                restart_miner()
                            debugOutput(
                                "Exception with to serial: " + str(e))
                            sleep(1)

                    try:
                        debugOutput("Received result (" + str(result[0]) + ")")
                        debugOutput("Received time (" + str(result[1]) + ")")
                        ducos1result = result[0]
                        # Convert AVR time to seconds
                        computetime = round(int(result[1]) / 1000000, 3)
                        # Calculate hashrate
                        hashrate = round(
                            int(result[0]) / int(result[1]) * 1000000, 2)
                        debugOutput(
                            "Calculated hashrate (" + str(hashrate) + ")")
                        if int(hashrate) > 10000:
                            raise Exception(
                                "Response too fast - possible AVR error")
                        try:
                            chipID = result[2]
                            debugOutput(
                                "Received chip ID (" + str(result[2]) + ")")
                            # Check if user is using the latest Arduino code
                            # This is not used yet anywhere, but will soon be
                            # added as yet another a security measure in the
                            # Kolka security system for identifying AVR boards
                            if (not chipID.startswith("DUCOID")
                                    or len(chipID) < 21):
                                raise Exception("Wrong chipID string")
                        except Exception:
                            prettyPrint(
                                "usb"
                                + str(''.join(filter(str.isdigit, com))),
                                " Possible incorrect chipID!"
                                + Style.NORMAL
                                + Fore.RESET
                                + " This will cause problems with the future"
                                + " release of Kolka security system",
                                "warning")
                            chipID = "None"
                        break
                    except Exception as e:
                        prettyPrint(
                            "usb"
                            + str(''.join(filter(str.isdigit, com))),
                            getString("mining_avr_connection_error")
                            + Style.NORMAL
                            + Fore.RESET
                            + " (err splitting avr data: "
                            + str(e)
                            + ")",
                            "error")
                        debugOutput("Error splitting data: " + str(e))
                        sleep(1)

                try:
                    # Send result to the server
                    socConn.sendall(
                        bytes(
                            str(ducos1result)
                            + ","
                            + str(hashrate)
                            + ",Official AVR Miner (DUCO-S1A) v"
                            + str(MINER_VER)
                            + ","
                            + str(rig_identifier)
                            + ","
                            + str(chipID),
                            encoding="utf8"))
                except Exception as e:
                    prettyPrint(
                        "net"
                        + str(''.join(filter(str.isdigit, com))),
                        getString("connecting_error")
                        + Style.NORMAL
                        + Fore.RESET
                        + " ("
                        + str(e)
                        + ")",
                        "error")
                    debugOutput("Connection error: " + str(e))
                    sleep(10)
                    restart_miner()

                while True:
                    try:
                        responsetimetart = now()
                        # Get feedback
                        ready = select.select(
                            [socConn], [], [], SOCKET_TIMEOUT)
                        if ready[0]:
                            feedback = socConn.recv(48).decode().rstrip("\n")
                        responsetimestop = now()
                        # Measure server ping
                        timeDelta = (responsetimestop -
                                     responsetimetart).microseconds
                        ping = round(timeDelta / 1000)
                        debugOutput("Successfully retrieved feedback: " +
                                    str(feedback) + " with ping: " + str(ping))
                        break
                    except Exception as e:
                        prettyPrint(
                            "net"
                            + str(''.join(filter(str.isdigit, com))),
                            getString("connecting_error")
                            + Style.NORMAL
                            + Fore.RESET
                            + " (err parsing response: "
                            + str(e)
                            + ")",
                            "error")
                        debugOutput("Error parsing response: " +
                                    str(e) + ", restarting miner")
                        sleep(1)
                        restart_miner()

                if feedback == "GOOD":
                    # If result was correct
                    shares[0] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(MINER_VER)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + " usb"
                            + str(''.join(filter(str.isdigit, com)))
                            + " "
                            + Back.RESET
                            + Fore.GREEN
                            + " ✓"
                            + getString("accepted")
                            + Fore.RESET
                            + str(int(shares[0]))
                            + "/"
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + " ("
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + "%)"
                            + Style.NORMAL
                            + Fore.RESET
                            + " ∙ "
                            + str("%01.3f" % float(computetime))
                            + "s"
                            + Style.NORMAL
                            + " ∙ "
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(round(hashrate))
                            + " H/s"
                            + Style.NORMAL
                            + Fore.RESET
                            + " @ diff "
                            + str(diff)
                            + " ∙ "
                            + Fore.CYAN
                            + "ping "
                            + str("%02.0f" % int(ping))
                            + "ms")

                elif feedback == "BLOCK":
                    # If block was found
                    shares[0] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(MINER_VER)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + " usb"
                            + str(''.join(filter(str.isdigit, com)))
                            + " "
                            + Back.RESET
                            + Fore.CYAN
                            + " ✓"
                            + getString("block_found")
                            + Fore.RESET
                            + str(int(shares[0]))
                            + "/"
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + " ("
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + "%)"
                            + Style.NORMAL
                            + Fore.RESET
                            + " ∙ "
                            + str("%01.3f" % float(computetime))
                            + "s"
                            + Style.NORMAL
                            + " ∙ "
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(int(hashrate))
                            + " H/s"
                            + Style.NORMAL
                            + Fore.RESET
                            + " @ diff "
                            + str(diff)
                            + " ∙ "
                            + Fore.CYAN
                            + "ping "
                            + str("%02.0f" % int(ping))
                            + "ms")

                else:
                    # If result was incorrect
                    shares[1] += 1
                    title(
                        getString("duco_avr_miner")
                        + str(MINER_VER)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + getString("accepted_shares"))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + "%H:%M:%S ")
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + " usb"
                            + str(''.join(filter(str.isdigit, com)))
                            + " "
                            + Back.RESET
                            + Fore.RED
                            + " ✗"
                            + getString("rejected")
                            + Fore.RESET
                            + str(int(shares[0]))
                            + "/"
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + " ("
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + "%)"
                            + Style.NORMAL
                            + Fore.RESET
                            + " ∙ "
                            + str("%01.3f" % float(computetime))
                            + "s"
                            + Style.NORMAL
                            + " ∙ "
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(int(hashrate))
                            + " H/s"
                            + Style.NORMAL
                            + Fore.RESET
                            + " @ diff "
                            + str(diff)
                            + " ∙ "
                            + Fore.CYAN
                            + "ping "
                            + str("%02.0f" % int(ping))
                            + "ms")
                break


if __name__ == "__main__":
    # Colorama
    init(autoreset=True)
    # Window title
    title(getString("duco_avr_miner") + str(MINER_VER) + ")")

    try:
        # Load config file or create new one
        loadConfig()
        debugOutput("Config file loaded")
    except Exception as e:
        prettyPrint(
            "sys0",
            getString("load_config_error")
            + RESOURCES_DIR
            + getString("load_config_error_warning")
            + Style.NORMAL
            + Fore.RESET
            + " ("
            + str(e)
            + ")",
            "error")
        debugOutput("Error reading configfile: " + str(e))
        sleep(10)
        _exit(1)

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
            thrThread(
                target=AVRMine,
                args=(port,)).start()
    except Exception as e:
        debugOutput("Error launching AVR thead(s): " + str(e))

    try:
        # Discord rich presence threads
        initRichPresence()
        thrThread(
            target=updateRichPresence).start()
    except Exception as e:
        debugOutput("Error launching Discord RPC thead: " + str(e))
