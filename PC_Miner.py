#!/usr/bin/env python3
##########################################
# Duino-Coin Python Miner (v2.0)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################
import socket, statistics, threading, multiprocessing, time, re, subprocess, hashlib, configparser, sys, datetime, os  # Import libraries
from pathlib import Path
from signal import signal, SIGINT


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    os.execl(sys.executable, sys.executable, *sys.argv)


def now():
    return datetime.datetime.now()


try:  # Check if cpuinfo is installed
    import cpuinfo
    from multiprocessing import freeze_support
except:
    print(
        now().strftime("%H:%M:%S ")
        + 'Cpuinfo is not installed. Miner will try to install it. If it fails, please manually install "py-cpuinfo" python3 package.\nIf you can\'t install it, use the Minimal-PC_Miner.'
    )
    install("py-cpuinfo")

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
minerVersion = "2.0"  # Version number
connectionMessageShown = False
timeout = 5  # Socket timeout
resourcesFolder = "PCMiner_" + str(minerVersion) + "_resources"
hash_mean = []
donatorrunning = False
debug = False
useLowerDiff = "n"
username = ""
serveripfile = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"  # Serverip file
config = configparser.ConfigParser()
autorestart = 0
donationlevel = 0
efficiency = 0

if not os.path.exists(resourcesFolder):
    os.mkdir(resourcesFolder)  # Create resources folder if it doesn't exist


def debugOutput(text):
    if debug == True:
        print(now().strftime(Style.DIM + "%H:%M:%S.%f ") + "DEBUG: " + text)


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


def Greeting():  # Greeting message depending on time
    global autorestart, greeting
    print(Style.RESET_ALL)

    if float(autorestart) <= 0:
        autorestart = 0
        autorestartmessage = "disabled"
    if float(autorestart) > 0:
        autorestartmessage = "every " + str(autorestart) + " minutes"

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
        Style.RESET_ALL
        + " > "
        + Fore.YELLOW
        + Style.BRIGHT
        + "Official Duino-Coin © Python Miner"
        + Style.RESET_ALL
        + Fore.WHITE
        + " (v"
        + str(minerVersion)
        + ") 2019-2021"
    )  # Startup message
    print(
        Style.RESET_ALL
        + " > "
        + Fore.YELLOW
        + "https://github.com/revoxhere/duino-coin"
    )
    try:
        print(
            Style.RESET_ALL
            + " > "
            + Fore.WHITE
            + "CPU: "
            + Style.BRIGHT
            + Fore.YELLOW
            + str(threadcount)
            + "x "
            + str(cpu["brand_raw"])
        )
    except:
        if debug == True:
            raise
    if os.name == "nt" or os.name == "posix":
        print(
            Style.RESET_ALL
            + " > "
            + Fore.WHITE
            + "Donation level: "
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donationlevel)
        )
    print(
        Style.RESET_ALL
        + " > "
        + Fore.WHITE
        + "Algorithm: "
        + Style.BRIGHT
        + Fore.YELLOW
        + "DUCO-S1"
    )
    print(
        Style.RESET_ALL
        + " > "
        + Fore.WHITE
        + "Autorestarter: "
        + Style.BRIGHT
        + Fore.YELLOW
        + str(autorestartmessage)
    )
    print(
        Style.RESET_ALL
        + " > "
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
            url = "https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true"
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


def hashrateCalculator(hashcount, khashcount):  # Hashes/sec calculation
    while True:
        hash_mean.append(hashcount.value / 1000)  # Append last hashcount to the list
        khashcount.value = int(statistics.mean(hash_mean))  # Calculate average hashrate
        hashcount.value = 0  # Reset the counter
        time.sleep(1)


def autorestarter():  # Autorestarter
    time.sleep(float(autorestart) * 60)
    try:
        donateExecutable.terminate()  # Stop the donation process (if running)
    except:
        pass
    for x in thread:
        x.terminate()
    print(
        now().strftime(Style.DIM + "%H:%M:%S ")
        + Style.RESET_ALL
        + Style.BRIGHT
        + Back.GREEN
        + Fore.WHITE
        + " sys0 "
        + Back.RESET
        + Fore.YELLOW
        + " Autorestarting the miner"
    )
    os.execl(sys.executable, sys.executable, *sys.argv)


def loadConfig():  # Config loading section
    global username, efficiency, autorestart, donationlevel, debug, threadcount, useLowerDiff

    if not Path(
        resourcesFolder + "/Miner_config.cfg"
    ).is_file():  # Initial configuration section
        print(
            Style.BRIGHT
            + "\nDuino-Coin basic configuration tool\nEdit "
            + resourcesFolder
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
            Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT
        )
        efficiency = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Set mining intensity (1-100)% (recommended: 100): "
            + Style.BRIGHT
        )
        threadcount = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Set mining threads (recommended for your system: "
            + str(multiprocessing.cpu_count())
            + "): "
            + Style.BRIGHT
        )
        useLowerDiff = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "Do you want to use lower difficulty for mining (for slower systems)? (y/N) "
            + Style.BRIGHT
        )
        autorestart = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + "If you want, set after how many minutes miner will restart (recommended: 30): "
            + Style.BRIGHT
        )
        donationlevel = "0"
        if os.name == "nt" or os.name == "posix":
            donationlevel = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + "Set developer donation level (0-5) (recommended: 1), this will not reduce your earnings: "
                + Style.BRIGHT
            )

        efficiency = re.sub("\D", "", efficiency)  # Check wheter efficiency is correct
        if float(efficiency) > int(100):
            efficiency = 100
        if float(efficiency) < int(1):
            efficiency = 1

        threadcount = re.sub(
            "\D", "", threadcount
        )  # Check wheter threadcount is correct
        if int(threadcount) > int(24):
            threadcount = 24
        if int(threadcount) < int(1):
            threadcount = 1

        if useLowerDiff == "y" or useLowerDiff == "Y":
            useLowerDiff = "y"
        else:
            useLowerDiff = "n"

        donationlevel = re.sub(
            "\D", "", donationlevel
        )  # Check wheter donationlevel is correct
        if float(donationlevel) > int(5):
            donationlevel = 5
        if float(donationlevel) < int(0):
            donationlevel = 0

        config["miner"] = {  # Format data
            "username": username,
            "efficiency": efficiency,
            "threads": threadcount,
            "useLowerDiff": useLowerDiff,
            "autorestart": autorestart,
            "donate": donationlevel,
            "debug": False,
        }

        with open(
            resourcesFolder + "/Miner_config.cfg", "w"
        ) as configfile:  # Write data to file
            config.write(configfile)
        efficiency = (
            100 - float(efficiency)
        ) * 0.01  # Calulate efficiency for use with sleep function
        print(Style.RESET_ALL + "Config saved! Launching the miner")

    else:  # If config already exists, load from it
        config.read(resourcesFolder + "/Miner_config.cfg")
        username = config["miner"]["username"]
        efficiency = config["miner"]["efficiency"]
        efficiency = (
            100 - float(efficiency)
        ) * 0.01  # Calulate efficiency for use with sleep function
        threadcount = config["miner"]["threads"]
        useLowerDiff = config["miner"]["useLowerDiff"]
        autorestart = config["miner"]["autorestart"]
        donationlevel = config["miner"]["donate"]
        debug = config["miner"]["debug"]


def Donate():
    global donationlevel, donatorrunning, donateExecutable

    if os.name == "nt":
        cmd = (
            "cd "
            + resourcesFolder
            + "& Donate_executable.exe -o stratum+tcp://xmg.minerclaim.net:3333 -u revox.donate -p x -e "
        )
    elif os.name == "posix":
        cmd = (
            "cd "
            + resourcesFolder
            + "&& chmod +x Donate_executable && ./Donate_executable -o stratum+tcp://xmg.minerclaim.net:3333 -u revox.donate -p x -e "
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
            + " Duino-Coin network is a completely free service and will always be"
            + Style.BRIGHT
            + Fore.YELLOW
            + "\nWe don't take any fees from your mining.\nYou can really help us maintain the server and low-fee exchanges by donating.\nVisit "
            + Style.RESET_ALL
            + Fore.GREEN
            + "https://duinocoin.com/donate"
            + Style.BRIGHT
            + Fore.YELLOW
            + " to learn more about how you can help :)"
        )
        time.sleep(5)
    if donatorrunning == False:
        if int(donationlevel) == 5:
            cmd += "100"
        elif int(donationlevel) == 4:
            cmd += "75"
        elif int(donationlevel) == 3:
            cmd += "50"
        elif int(donationlevel) == 2:
            cmd += "25"
        elif int(donationlevel) == 1:
            cmd += "10"
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
            )


def Thread(threadid, hashcount, accepted, rejected, useLowerDiff, khashcount):
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
                    + str(threadid)
                    + " "
                    + Back.RESET
                    + Fore.RED
                    + " Error retrieving data from GitHub! Retrying in 10s."
                )
                if debug == True:
                    raise
                time.sleep(10)
        while True:  # This section connects to the server
            try:
                soc = socket.socket()
                soc.connect(
                    (str(masterServer_address), int(masterServer_port))
                )  # Connect to the server
                serverVersion = soc.recv(3).decode()  # Get server version
                debugOutput("Server version: " + serverVersion)
                if (
                    float(serverVersion) <= float(minerVersion)
                    and len(serverVersion) == 3
                ):  # If miner is up-to-date, display a message and continue
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
                if debug == True:
                    raise
        print(
            now().strftime(Style.DIM + "%H:%M:%S ")
            + Style.RESET_ALL
            + Style.BRIGHT
            + Back.GREEN
            + Fore.WHITE
            + " sys"
            + str(threadid)
            + " "
            + Back.RESET
            + Fore.YELLOW
            + " Mining thread #"
            + str(threadid)
            + " is starting"
            + Style.RESET_ALL
            + Fore.WHITE
            + " using DUCO-S1 algorithm with "
            + Fore.YELLOW
            + str(100 - (100 * int(efficiency)))
            + "% efficiency"
        )
        while True:  # Mining section
            try:
                if float(efficiency) < 100:
                    time.sleep(
                        float(efficiency)
                    )  # Sleep to achieve lower efficiency if less than 100 selected
                while True:
                    if useLowerDiff == "n":
                        soc.send(
                            bytes(f"JOB,{str(username)}", encoding="utf8")
                        )  # Send job request
                    else:
                        soc.send(
                            bytes(f"JOB,{str(username)},MEDIUM", encoding="utf8")
                        )  # Send job request with lower diff
                    job = soc.recv(128).decode()  # Get work from pool
                    job = job.split(",")  # Split received data to job and difficulty
                    diff = job[2]

                    if job[0] and job[1] and job[2]:
                        debugOutput(str(threadid) + "Job received: " + str(job))
                        break  # If job received, continue to hashing algo

                threadhashcount = 0  # Reset hash counter for this thread
                for ducos1res in range(
                    100 * int(diff) + 1
                ):  # Loop from 1 too 100*diff)
                    ducos1 = hashlib.sha1(
                        str(job[0] + str(ducos1res)).encode("utf-8")
                    ).hexdigest()  # Generate hash
                    threadhashcount += (
                        1  # Increment hash counter for hashrate calculator
                    )
                    if job[1] == ducos1:  # If result is even with job, send the result
                        hashcount.value += threadhashcount  # Add this thread hash counter to the global counter\

                        debugOutput(str(threadid) + "Result found: " + str(ducos1res))
                        while True:
                            soc.send(
                                bytes(
                                    f"{str(ducos1res)},{str(threadhashcount)},Official Python Miner v{str(minerVersion)}",
                                    encoding="utf8",
                                )
                            )  # Send result of hashing algorithm to the server
                            responsetimetart = now()
                            feedback = soc.recv(4).decode()  # Get feedback
                            debugOutput(
                                str(threadid) + "Feedback received: " + str(feedback)
                            )
                            responsetimestop = now()  # Measure server ping
                            ping = responsetimestop - responsetimetart  # Calculate ping
                            ping = str(int(ping.microseconds / 1000))  # Convert to ms
                            debugOutput("Ping: " + ping)

                            if feedback == "GOOD":  # If result was good
                                accepted.value += 1  # Share accepted = increment feedback shares counter by 1
                                title(
                                    "Duino-Coin Python Miner (v"
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + " accepted shares"
                                )
                                print(
                                    now().strftime(
                                        Style.RESET_ALL + Style.DIM + "%H:%M:%S "
                                    )
                                    + Style.BRIGHT
                                    + Back.YELLOW
                                    + Fore.WHITE
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.GREEN
                                    + " Accepted "
                                    + Fore.WHITE
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + Back.RESET
                                    + Fore.YELLOW
                                    + " ("
                                    + str(
                                        int(
                                            (
                                                accepted.value
                                                / (accepted.value + rejected.value)
                                                * 100
                                            )
                                        )
                                    )
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.WHITE
                                    + " ⁃ "
                                    + Style.BRIGHT
                                    + Fore.WHITE
                                    + str(khashcount.value)
                                    + " kH/s"
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ⁃ "
                                    + Fore.BLUE
                                    + "ping "
                                    + ping
                                    + "ms"
                                )
                                break  # Repeat

                            elif feedback == "BLOCK":  # If block was found
                                accepted.value += 1  # Share accepted = increment feedback shares counter by 1
                                title(
                                    "Duino-Coin Python Miner (v"
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + " accepted shares"
                                )
                                print(
                                    now().strftime(
                                        Style.RESET_ALL + Style.DIM + "%H:%M:%S "
                                    )
                                    + Style.BRIGHT
                                    + Back.YELLOW
                                    + Fore.WHITE
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.CYAN
                                    + " Block found "
                                    + Fore.WHITE
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + Back.RESET
                                    + Fore.YELLOW
                                    + " ("
                                    + str(
                                        int(
                                            (
                                                accepted.value
                                                / (accepted.value + rejected.value)
                                                * 100
                                            )
                                        )
                                    )
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.WHITE
                                    + " ⁃ "
                                    + Style.BRIGHT
                                    + Fore.WHITE
                                    + str(khashcount.value)
                                    + " kH/s"
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ⁃ "
                                    + Fore.BLUE
                                    + "ping "
                                    + ping
                                    + "ms"
                                )
                                break  # Repeat

                            elif feedback == "ERR":  # If server reports internal error
                                print(
                                    now().strftime(
                                        Style.RESET_ALL + Style.DIM + "%H:%M:%S "
                                    )
                                    + Style.BRIGHT
                                    + Back.BLUE
                                    + Fore.WHITE
                                    + " net"
                                    + str(threadid)
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
                                rejected.value += 1  # Share rejected = increment bad shares counter by 1
                                title(
                                    "Duino-Coin Python Miner (v"
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + " accepted shares"
                                )
                                print(
                                    now().strftime(Style.DIM + "%H:%M:%S ")
                                    + Style.RESET_ALL
                                    + Style.BRIGHT
                                    + Back.YELLOW
                                    + Fore.WHITE
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.RED
                                    + " Rejected "
                                    + Fore.WHITE
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + Back.RESET
                                    + Fore.YELLOW
                                    + " ("
                                    + str(
                                        int(
                                            (
                                                accepted.value
                                                / (accepted.value + rejected.value)
                                                * 100
                                            )
                                        )
                                    )
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.WHITE
                                    + " ⁃ "
                                    + Style.BRIGHT
                                    + Fore.WHITE
                                    + str(khashcount.value)
                                    + " kH/s"
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ⁃ "
                                    + Fore.BLUE
                                    + "ping "
                                    + ping
                                    + "ms"
                                )
                                break  # Repeat
                        break  # Repeat
            except Exception as e:
                print(
                    now().strftime(Style.DIM + "%H:%M:%S ")
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Back.BLUE
                    + Fore.WHITE
                    + " net"
                    + str(threadid)
                    + " "
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + Fore.MAGENTA
                    + " Master server timeout - restarting in 5s."
                    + Style.RESET_ALL
                )
                raise
                if debug == True:
                    raise
                time.sleep(5)
                break


def initRichPresence():
    global RPC
    try:
        RPC = Presence(808045598447632384)
        RPC.connect()
    except:  # Discord not launched
        pass


def updateRichPresence():
    while True:
        try:
            RPC.update(
                details="Hashrate: " + str(int(statistics.mean(hash_mean))) + " kH/s",
                state="Acc. shares: "
                + str(accepted.value)
                + "/"
                + str(rejected.value + accepted.value),
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


if __name__ == "__main__":
    multiprocessing.freeze_support()
    cpu = cpuinfo.get_cpu_info()  # Processor info
    init(autoreset=True)  # Enable colorama
    title("Duino-Coin Python Miner (v" + str(minerVersion) + ")")

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
        if debug == True:
            raise
        time.sleep(10)
        os._exit(1)
    try:
        Greeting()  # Display greeting message
        debugOutput("Greeting displayed")
    except:
        if debug == True:
            raise
    try:  # Setup autorestarter
        if float(autorestart) > 0:
            debugOutput("Enabled autorestarter for " + str(autorestart) + " minutes")
            threading.Thread(target=autorestarter).start()
        else:
            debugOutput("Autorestarter is disabled")
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
            + " Error in the autorestarter. Check configuration file ("
            + resources
            + "/Miner_config.cfg). Exiting in 10s"
            + Style.RESET_ALL
        )
        if debug == True:
            raise
        time.sleep(10)
        os._exit(1)
    try:
        Donate()  # Start donation thread
    except:
        if debug == True:
            raise

    hashcount = multiprocessing.Value("i", 0)
    khashcount = multiprocessing.Value("i", 0)
    accepted = multiprocessing.Value("i", 0)
    rejected = multiprocessing.Value("i", 0)

    threading.Thread(
        target=hashrateCalculator, args=(hashcount, khashcount)
    ).start()  # Start hashrate calculator

    thread = []
    for x in range(int(threadcount)):  # Launch duco mining threads
        thread.append(x)
        thread[x] = multiprocessing.Process(
            target=Thread,
            args=(x, hashcount, accepted, rejected, useLowerDiff, khashcount),
        )
        thread[x].start()
        time.sleep(0.05)

    initRichPresence()
    threading.Thread(target=updateRichPresence).start()
