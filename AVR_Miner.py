#!/usr/bin/env python3
##########################################
# Duino-Coin AVR Miner (v2.2)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################
import socket, threading, time, re, subprocess, configparser, sys, datetime, os, json  # Import libraries
from pathlib import Path
from signal import signal, SIGINT


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    os.execl(sys.executable, sys.executable, *sys.argv)


def now():
    return datetime.datetime.now()


try:  # Check if pyserial is installed
    import serial
    import serial.tools.list_ports
except:
    print(
        now().strftime("%H:%M:%S ")
        + 'Pyserial is not installed. Miner will try to install it. If it fails, please manually install "pyserial" python3 package.\nIf you can\'t install it, use the Minimal-PC_Miner.'
    )
    install("pyserial")

try:  # Check if colorama is installed
    from colorama import init, Fore, Back, Style
except:
    print(
        now().strftime("%H:%M:%S ")
        + 'Colorama is not installed. Miner will try to install it. If it fails, please manually install "colorama" python3 package.\nIf you can\'t install it, use the Minimal-PC_Miner.'
    )
    install("colorama")

try:  # Check if requests is installed
    import requests
except:
    print(
        now().strftime("%H:%M:%S ")
        + 'Requests is not installed. Miner will try to install it. If it fails, please manually install "requests" python3 package.\nIf you can\'t install it, use the Minimal-PC_Miner.'
    )
    install("requests")

try:
    from pypresence import Presence
except:
    print(
        'Pypresence is not installed. Wallet will try to install it. If it fails, please manually install "pypresence" python3 package.'
    )
    install("pypresence")

# Global variables
minerVersion = "2.2"  # Version number
timeout = 30  # Socket timeout
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
connectionMessageShown = False

if not os.path.exists(resourcesFolder):
    os.mkdir(resourcesFolder)  # Create resources folder if it doesn't exist


def debugOutput(text):
    if debug == "y":
        print(
            now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S.%f ")
            + "DEBUG: "
            + text
        )


def title(title):
    if os.name == "nt":
        os.system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def handler(
    signal_received, frame
):  # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
    print(
        now().strftime(Style.RESET_ALL + Style.DIM + "\n%H:%M:%S ")
        + Style.BRIGHT
        + Back.GREEN
        + Fore.WHITE
        + " sys0 "
        + Back.RESET
        + Fore.YELLOW
        + " SIGINT detected - Exiting gracefully."
        + Style.NORMAL
        + Fore.WHITE
        + " See you soon!"
    )
    try:
        soc.close()
    except:
        pass
    os._exit(0)


signal(SIGINT, handler)  # Enable signal handler


def loadConfig():  # Config loading section
    global pool_address, pool_port, username, donationlevel, avrport, debug, requestedDiff, rigIdentifier

    if not Path(
        str(resourcesFolder) + "/Miner_config.cfg"
    ).is_file():  # Initial configuration section
        print(
            Style.BRIGHT
            + "\nDuino-Coin basic configuration tool\nEdit "
            + str(resourcesFolder)
            + "/Miner_config.cfg file later if you want to change it."
        )

        print(
            Style.RESET_ALL
            + "Don't have an Duino-Coin account yet? Use "
            + Fore.YELLOW
            + "Wallet"
            + Fore.WHITE
            + " to register on server.\n"
        )

        username = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Enter your Duino-Coin username: "
            + Style.BRIGHT
        )

        print(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Configuration tool has found the following ports:"
        )
        portlist = serial.tools.list_ports.comports()
        for port in portlist:
            print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "  " + str(port))
        print(
            Style.RESET_ALL
            + Fore.YELLOW
            + "If you can't see your board here, make sure the it is properly connected and the program has access to it (admin/sudo rights)."
        )
        avrport = ""
        while True:
            avrport += input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Enter your board serial port (e.g. COM1 (Windows) or /dev/ttyUSB1 (Unix)): "
                + Style.BRIGHT
            )
            confirmation = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Do you want to add another board? (y/N): "
                + Style.BRIGHT
            )
            if confirmation == "y" or confirmation == "Y":
                avrport += ","
            else:
                break

        requestedDiffSelection = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Do you want to use a higher difficulty (only for Arduino DUE boards) (y/N): "
            + Style.BRIGHT
        )
        if requestedDiffSelection == "y" or requestedDiffSelection == "Y":
            requestedDiff = "ESP32"
        else:
            requestedDiff = "AVR"

        rigIdentifier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Do you want to add an identifier (name) to this rig? (y/N) "
            + Style.BRIGHT
        )
        if rigIdentifier == "y" or rigIdentifier == "Y":
            rigIdentifier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Enter desired rig name: "
                + Style.BRIGHT
            )
        else:
            rigIdentifier = "None"

        donationlevel = "0"
        if os.name == "nt" or os.name == "posix":
            donationlevel = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Set developer donation level (0-5) (recommended: 1), this will not reduce your earnings: "
                + Style.BRIGHT
            )

        donationlevel = re.sub(
            "\D", "", donationlevel
        )  # Check wheter donationlevel is correct
        if float(donationlevel) > int(5):
            donationlevel = 5
        if float(donationlevel) < int(0):
            donationlevel = 0
        config["arduminer"] = {  # Format data
            "username": username,
            "avrport": avrport,
            "donate": donationlevel,
            "debug": "n",
            "identifier": rigIdentifier,
            "difficulty": requestedDiff,
        }

        with open(
            str(resourcesFolder) + "/Miner_config.cfg", "w"
        ) as configfile:  # Write data to file
            config.write(configfile)
        avrport = avrport.split(",")
        print(Style.RESET_ALL + "Config saved! Launching the miner")

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
        greeting = "Have a wonderful morning"
    elif current_hour == 12:
        greeting = "Have a tasty noon"
    elif current_hour > 12 and current_hour < 18:
        greeting = "Have a peaceful afternoon"
    elif current_hour >= 18:
        greeting = "Have a cozy evening"
    else:
        greeting = "Welcome back"

    print(
        " > "
        + Fore.YELLOW
        + Style.BRIGHT
        + "Official Duino-Coin © AVR Miner"
        + Style.RESET_ALL
        + Fore.WHITE
        + " (v"
        + str(minerVersion)
        + ") 2019-2021"
    )  # Startup message
    print(" > " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
    print(
        " > "
        + Fore.WHITE
        + "AVR board(s) on port(s): "
        + Style.BRIGHT
        + Fore.YELLOW
        + " ".join(avrport)
    )
    if os.name == "nt" or os.name == "posix":
        print(
            " > "
            + Fore.WHITE
            + "Donation level: "
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donationlevel)
        )
    print(
        " > "
        + Fore.WHITE
        + "Algorithm: "
        + Style.BRIGHT
        + Fore.YELLOW
        + "DUCO-S1A @ "
        + str(requestedDiff)
        + " diff"
    )
    print(
        Style.RESET_ALL
        + " > "
        + Fore.WHITE
        + "Rig identifier: "
        + Style.BRIGHT
        + Fore.YELLOW
        + rigIdentifier
    )
    print(
        " > "
        + Fore.WHITE
        + str(greeting)
        + ", "
        + Style.BRIGHT
        + Fore.YELLOW
        + str(username)
        + "!\n"
    )

    if os.name == "nt":
        if not Path(
            resourcesFolder + "/Donate_executable.exe"
        ).is_file():  # Initial miner executable section
            debugOutput("OS is Windows, downloading developer donation executable")
            url = "https://github.com/revoxhere/duino-coin/blob/useful-tools/DonateExecutableWindows.exe?raw=true"
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable.exe", "wb") as f:
                f.write(r.content)
    elif os.name == "posix":
        if not Path(
            resourcesFolder + "/Donate_executable"
        ).is_file():  # Initial miner executable section
            debugOutput("OS is Windows, downloading developer donation executable")
            url = "https://github.com/revoxhere/duino-coin/blob/useful-tools/DonateExecutableLinux?raw=true"
            r = requests.get(url)
            with open(resourcesFolder + "/Donate_executable", "wb") as f:
                f.write(r.content)


def Donate():
    global donationlevel, donatorrunning, donateExecutable
    if os.name == "nt":
        cmd = (
            "cd "
            + resourcesFolder
            + "& Donate_executable.exe -o stratum+tcp://blockmasters.co:6033 -u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR -p AVRmW,c=XMG,d=16 -s 4 -e "
        )
    elif os.name == "posix":
        cmd = (
            "cd "
            + resourcesFolder
            + "&& chmod +x Donate_executable && ./Donate_executable -o stratum+tcp://blockmasters.co:6033 -u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR -p AVRmL,c=XMG,d=16 -s 4 -e "
        )
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
            + " Duino-Coin network is a completely free service and will always be."
            + Style.BRIGHT
            + Fore.YELLOW
            + "\nWe don't take any fees from your mining.\nYou can really help us maintain the server and low-fee exchanges by donating.\nVisit "
            + Style.RESET_ALL
            + Fore.GREEN
            + "https://duinocoin.com/donate"
            + Style.BRIGHT
            + Fore.YELLOW
            + " to learn more about how you can help :)"
            + Style.RESET_ALL
        )
        time.sleep(10)
    if donatorrunning == False:
        if int(donationlevel) == 5:
            cmd += "100"
        elif int(donationlevel) == 4:
            cmd += "85"
        elif int(donationlevel) == 3:
            cmd += "60"
        elif int(donationlevel) == 2:
            cmd += "30"
        elif int(donationlevel) == 1:
            cmd += "15"
        if int(donationlevel) > 0:  # Launch CMD as subprocess
            debugOutput("Starting donation process")
            donatorrunning = True
            donateExecutable = subprocess.Popen(
                cmd, shell=True, stderr=subprocess.DEVNULL
            )
            print(
                now().strftime(Style.DIM + "%H:%M:%S ")
                + Style.RESET_ALL
                + Style.BRIGHT
                + Back.GREEN
                + Fore.WHITE
                + " sys0 "
                + Back.RESET
                + Fore.RED
                + " Thank You for being an awesome donator ❤️ \nYour donation will help us maintain the server and allow further development"
                + Style.RESET_ALL
            )


def initRichPresence():
    global RPC
    try:
        RPC = Presence(808056068113563701)
        RPC.connect()
    except:  # Discord not launched
        pass


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
                large_text="Duino-Coin, a cryptocurrency that can be mined with Arduino boards",
                buttons=[
                    {"label": "Learn more", "url": "https://duinocoin.com"},
                    {"label": "Discord Server", "url": "https://discord.gg/k48Ht5y"},
                ],
            )
        except:  # Discord not launched
            pass
        time.sleep(15)  # 15 seconds to respect discord's rate limit


def AVRMine(com):  # Mining section
    global hash_count, connectionMessageShown, hashrate
    while True:
        while True:
            try:
                res = requests.get(
                    serveripfile, data=None
                )  # Use request to grab data from raw github file
                if res.status_code == 200:  # Check for response
                    content = (
                        res.content.decode().splitlines()
                    )  # Read content and split into lines
                    masterServer_address = content[0]  # Line 1 = pool address
                    masterServer_port = content[1]  # Line 2 = pool port
                    debugOutput(
                        "Retrieved pool IP: "
                        + masterServer_address
                        + ":"
                        + str(masterServer_port)
                    )
                    break
            except:  # If it wasn't, display a message
                print(
                    now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                    + Style.BRIGHT
                    + Back.BLUE
                    + Fore.WHITE
                    + " net"
                    + str(com[-1:].lower())
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + " Error retrieving data from GitHub! Retrying in 10s."
                )
                if debug == "y":
                    raise
                time.sleep(10)
        while True:  # This section connects to the server
            try:
                socId = socket.socket()
                socId.connect(
                    (str(masterServer_address), int(masterServer_port))
                )  # Connect to the server
                serverVersion = socId.recv(3).decode()  # Get server version
                debugOutput("Server version: " + serverVersion)
                if (
                    float(serverVersion) <= float(minerVersion)
                    and len(serverVersion) == 3
                    and connectionMessageShown != True
                ):  # If miner is up-to-date, display a message and continue
                    connectionMessageShown = True
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.BLUE
                        + Fore.WHITE
                        + " net0 "
                        + Back.RESET
                        + Fore.YELLOW
                        + " Connected"
                        + Style.RESET_ALL
                        + Fore.WHITE
                        + " to master Duino-Coin server (v"
                        + str(serverVersion)
                        + ")"
                    )
                elif connectionMessageShown != True:
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
                        + " server is on v"
                        + serverVersion
                        + ", please download latest version from https://github.com/revoxhere/duino-coin/releases/"
                    )
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
                    + " Error connecting to the server. Retrying in 10s"
                    + Style.RESET_ALL
                )
                if debug == "y":
                    raise
                time.sleep(10)
        while True:
            try:  # Close previous serial connections (if any)
                com.close()
            except:
                pass
            try:
                comConnection = serial.Serial(
                    com,
                    115200,
                    timeout=3,
                    write_timeout=3,
                    inter_byte_timeout=1,
                )
                print(
                    now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Back.MAGENTA
                    + Fore.WHITE
                    + " "
                    + str(com[-4:].lower())
                    + " "
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Fore.GREEN
                    + " AVR on port "
                    + str(com[-4:])
                    + " is connected"
                    + Style.RESET_ALL
                )
                break
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
                    + " "
                    + str(com[-4:].lower())
                    + " "
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Fore.RED
                    + " AVR connection error on port "
                    + str(com[-4:])
                    + ", please check wether it's plugged in or not"
                    + Style.RESET_ALL
                )
                time.sleep(10)

        first_share = True
        avr_not_initialized = True
        while avr_not_initialized:
            try:
                ready = comConnection.readline().decode()  # AVR will send ready signal
                debugOutput("Received start word (" + str(ready) + ")")
                print(
                    now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Back.GREEN
                    + Fore.WHITE
                    + " sys"
                    + str(com[-1:])
                    + " "
                    + Back.RESET
                    + Fore.YELLOW
                    + " AVR mining thread is starting"
                    + Style.RESET_ALL
                    + Fore.WHITE
                    + " using DUCO-S1A algorithm ("
                    + str(com)
                    + ")"
                )
                avr_not_initialized = False
            except:
                while connection_error:
                    connection_error = True
                    time.sleep(10)
                    print(
                        now().strftime(Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " "
                        + str(com[-4:].toLower())
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + " Error connecting to the AVR! Retrying in 10s."
                    )
                else:
                    connection_error = False
                    avr_not_initialized = True
        while True:
            while True:
                try:
                    job_not_received = True
                    while job_not_received:
                        socId.send(
                            bytes(
                                "JOB," + str(username) + "," + str(requestedDiff),
                                encoding="utf8",
                            )
                        )  # Send job request
                        try:
                            job = socId.recv(1024).decode()  # Retrieves work from pool
                            debugOutput("Received job")
                            job_not_received = False
                        except:
                            break
                    job = job.split(",")  # Split received data to job and difficulty
                    try:
                        if job[0] and job[1] and job[2]:
                            debugOutput("Job received: " + str(job))
                            diff = job[2]
                            break  # If job received, continue
                    except IndexError:
                        debugOutput("IndexError, retrying")
                except:
                    if debug == "y":
                        raise
                    break

            try:  # Write data to AVR board
                try:
                    comConnection.write(bytes("start\n", encoding="utf8"))  # start word
                    debugOutput("Written start word")
                    comConnection.write(
                        bytes(
                            str(job[0] + "\n" + job[1] + "\n" + job[2] + "\n"),
                            encoding="utf8",
                        )
                    )  # hash
                    debugOutput("Send job to arduino")
                except:
                    ConnectToAVR()
                    continue
                wrong_avr_result = True
                wrong_results = 0
                while wrong_avr_result:
                    result = comConnection.readline().decode()  # Read the result
                    debugOutput(str("result: ") + str(result))
                    if result == "":
                        wrong_avr_result = True
                        wrong_results = wrong_results + 1
                        if first_share or wrong_results > 5:
                            wrong_avr_result = False
                            print(
                                now().strftime(Style.DIM + "%H:%M:%S ")
                                + Style.RESET_ALL
                                + Style.BRIGHT
                                + Back.MAGENTA
                                + Fore.WHITE
                                + " avr "
                                + Back.RESET
                                + Fore.RED
                                + " Arduino is taking longer than expected, sending it a new job "
                            )
                    else:
                        wrong_avr_result = False
                        first_share = False
                        wrong_results = 0
                if first_share or wrong_results > 5:
                    continue
                result = result.split(",")
                try:
                    debugOutput("Received result (" + str(result[0]) + ")")
                    debugOutput("Received time (" + str(result[1]) + ")")
                    computetime = round(
                        int(result[1]) / 1000000, 3
                    )  # Convert AVR time to s
                    hashrate = round(int(result[0]) / int(result[1]) * 1000000, 2)
                    debugOutput("Calculated hashrate (" + str(hashrate) + ")")
                except:
                    break
                try:
                    socId.send(
                        bytes(
                            str(result[0])
                            + ","
                            + str(hashrate)
                            + ",Official AVR Miner v"
                            + str(minerVersion)
                            + ","
                            + str(rigIdentifier),
                            encoding="utf8",
                        )
                    )  # Send result back to the server
                except:
                    break
            except:
                break

            while True:
                responsetimetart = now()
                feedback_not_received = True
                while feedback_not_received:
                    try:
                        feedback = socId.recv(64).decode()  # Get feedback
                    except socket.timeout:
                        feedback_not_received = True
                        debugOutput("Timeout while getting feedback, retrying")
                    except ConnectionResetError:
                        debugOutput("Connection was reset, reconnecting")
                        feedback_not_received = True
                        break
                    except ConnectionAbortedError:
                        debugOutput("Connection was aborted, reconnecting")
                        feedback_not_received = True
                        break
                    else:
                        responsetimestop = now()  # Measure server ping
                        ping = responsetimestop - responsetimetart  # Calculate ping
                        ping = str(int(ping.microseconds / 1000))  # Convert to ms
                        feedback_not_received = False
                        debugOutput("Successfully retrieved feedback")

                if feedback == "GOOD":  # If result was good
                    shares[0] = (
                        shares[0] + 1
                    )  # Share accepted  = increment correct shares counter by 1
                    title(
                        "Duino-Coin AVR Miner (v"
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + " accepted shares"
                    )
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " "
                        + str(com[-4:].lower())
                        + " "
                        + Back.RESET
                        + Fore.GREEN
                        + " Accepted "
                        + Fore.WHITE
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ⁃ "
                        + Style.BRIGHT
                        + Fore.WHITE
                        + str(computetime)
                        + "s"
                        + Style.NORMAL
                        + " - "
                        + str(hashrate)
                        + " H/s @ diff "
                        + str(diff)
                        + " ⁃ "
                        + Fore.BLUE
                        + "ping "
                        + ping
                        + "ms"
                    )
                    break  # Repeat

                elif feedback == "BLOCK":  # If result was good
                    shares[0] = (
                        shares[0] + 1
                    )  # Share accepted  = increment correct shares counter by 1
                    title(
                        "Duino-Coin AVR Miner (v"
                        + str(minerVersion)
                        + ") - "
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + " accepted shares"
                    )
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " "
                        + str(com[-4:].lower())
                        + " "
                        + Back.RESET
                        + Fore.CYAN
                        + " Block found "
                        + Fore.WHITE
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ⁃ "
                        + Style.BRIGHT
                        + Fore.WHITE
                        + str(computetime)
                        + "s"
                        + Style.NORMAL
                        + " - "
                        + str(hashrate)
                        + " H/s @ diff "
                        + str(diff)
                        + " ⁃ "
                        + Fore.BLUE
                        + "ping "
                        + ping
                        + "ms"
                    )
                    break  # Repeat

                elif feedback == "INVU":  # If user doesn't exist
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.BLUE
                        + Fore.WHITE
                        + " net"
                        + str(com[-1:])
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + " User "
                        + str(username)
                        + " doesn't exist."
                        + Style.RESET_ALL
                        + Fore.RED
                        + " Make sure you've entered the username correctly. Please check your config file. Retrying in 10s"
                    )
                    time.sleep(10)

                elif feedback == "ERR":  # If server says that it encountered an error
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.BLUE
                        + Fore.WHITE
                        + " net"
                        + str(com[-1:])
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + " Internal server error."
                        + Style.RESET_ALL
                        + Fore.RED
                        + " Retrying in 10s"
                    )
                    time.sleep(10)

                else:  # If result was bad
                    shares[1] += 1  # Share rejected = increment bad shares counter by 1
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.RESET_ALL
                        + Style.BRIGHT
                        + Back.MAGENTA
                        + Fore.WHITE
                        + " "
                        + str(com[-4:].lower())
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + " Rejected "
                        + Fore.WHITE
                        + str(shares[0])
                        + "/"
                        + str(shares[0] + shares[1])
                        + Back.RESET
                        + Fore.YELLOW
                        + " ("
                        + str(int((shares[0] / (shares[0] + shares[1]) * 100)))
                        + "%)"
                        + Style.NORMAL
                        + Fore.WHITE
                        + " ⁃ "
                        + Style.BRIGHT
                        + Fore.WHITE
                        + str(computetime)
                        + "s"
                        + Style.NORMAL
                        + " - "
                        + str(hashrate)
                        + " H/s @ diff "
                        + str(diff)
                        + " ⁃ "
                        + Fore.BLUE
                        + "ping "
                        + ping
                        + "ms"
                    )
                    break  # Repeat


if __name__ == "__main__":
    init(autoreset=True)  # Enable colorama
    title("Duino-Coin AVR Miner (v" + str(minerVersion) + ")")
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
            + " Error loading the configfile ("
            + resourcesFolder
            + "/Miner_config.cfg). Try removing it and re-running configuration. Exiting in 10s"
            + Style.RESET_ALL
        )
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
        for port in avrport:
            threading.Thread(
                target=AVRMine, args=(port,)
            ).start()  # Launch avr duco mining threads
    except:
        if debug == "y":
            raise

    initRichPresence()
    threading.Thread(target=updateRichPresence).start()
