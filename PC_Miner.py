#!/usr/bin/env python3
##########################################
# Duino-Coin Python PC Miner (v2.2)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
import socket, statistics, threading, multiprocessing, time, re, subprocess, hashlib, configparser, sys, datetime, os  # Import libraries
from pathlib import Path
from signal import signal, SIGINT
import locale, json


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
minerVersion = "2.2"  # Version number
timeout = 30  # Socket timeout
resourcesFolder = "PCMiner_" + str(minerVersion) + "_resources"
hash_mean = []
donatorrunning = False
debug = "n"
rigIdentifier = "None"
useLowerDiff = "n"
serveripfile = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"  # Serverip file
config = configparser.ConfigParser()
donationlevel = 0

if not os.path.exists(resourcesFolder):
    os.mkdir(resourcesFolder)  # Create resources folder if it doesn't exist

if not Path(  # Check if languages file exists
    resourcesFolder + "/langs.json"
).is_file():  # Initial miner executable section
    url = "https://raw.githubusercontent.com/revoxhere/duino-coin/master/Resources/PC_Miner_langs.json"
    r = requests.get(url)
    with open(resourcesFolder + "/langs.json", "wb") as f:
        f.write(r.content)

with open(f"{resourcesFolder}/langs.json", "r", encoding="utf8") as lang_file:
    lang_file = json.load(lang_file)

if not Path(  # Check if miner is configured, if it isn't, autodetect language
    resourcesFolder + "/Miner_config.cfg"
).is_file():
    locale = locale.getdefaultlocale()[0]
    if (
        locale == "es_ES"
        or locale == "es_AR"
        or locale == "es_BO"
        or locale == "es_CL"
        or locale == "es_CO"
        or locale == "es_CR"
        or locale == "es_DO"
        or locale == "es_EC"
        or locale == "es_SV"
        or locale == "es_GT"
        or locale == "es_HN"
        or locale == "es_MX"
        or locale == "es_NI"
        or locale == "es_PA"
        or locale == "es_PY"
        or locale == "es_PE"
        or locale == "es_PR"
        or locale == "es_UY"
        or locale == "es_VE"
    ):
        lang = "spanish"

    elif locale == "pl_PL":
        lang = "polish"

    elif (
        locale == "fr_FR"
        or locale == "fr_BE"
        or locale == "fr_CA"
        or locale == "fr_LU"
        or locale == "fr_CH"
    ):
        lang = "french"

    elif locale == "ru_RU" or locale == "ru_MO":
        lang = "russian"

    elif (
        locale == "de_DE"
        or locale == "de_AT"
        or locale == "de_LI"
        or locale == "de_LU"
        or locale == "de_CH"
    ):
        lang = "german"

    else:
        lang = "english"
else:
    try:  # Read language from configfile
        config.read(resourcesFolder + "/Miner_config.cfg")
        lang = config["miner"]["language"]
    except:  # If it fails, fallback to english
        lang = "english"


def getString(string_name):
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name


def debugOutput(text):
    if debug == "y":
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
        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
        + Style.BRIGHT
        + Back.GREEN
        + Fore.WHITE
        + " sys0 "
        + Back.RESET
        + Fore.YELLOW
        + getString("sigint_detected")
        + Style.NORMAL
        + Fore.WHITE
        + getString("goodbye")
    )
    handlerShown = True
    try:
        soc.close()
    except:
        pass
    os._exit(0)


signal(SIGINT, handler)  # Enable signal handler


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

    print(
        Style.RESET_ALL
        + " > "
        + Fore.YELLOW
        + Style.BRIGHT
        + getString("banner")
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
        if debug == "y":
            raise
    if os.name == "nt" or os.name == "posix":
        print(
            Style.RESET_ALL
            + " > "
            + Fore.WHITE
            + getString("donation_level")
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donationlevel)
        )
    if useLowerDiff == "y":
        diffName = getString("medium_diff")
    else:
        diffName = getString("net_diff")
    print(
        Style.RESET_ALL
        + " > "
        + Fore.WHITE
        + getString("algorithm")
        + Style.BRIGHT
        + Fore.YELLOW
        + "DUCO-S1 @ "
        + diffName
    )
    print(
        Style.RESET_ALL
        + " > "
        + Fore.WHITE
        + getString("rig_identifier")
        + Style.BRIGHT
        + Fore.YELLOW
        + rigIdentifier
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


def hashrateCalculator(hashcount, khashcount):  # Hashes/sec calculation
    while True:
        hash_mean.append(
            hashcount.value / 1000
        )  # Append last hashcount in kH to the list
        hashcount.value = 0  # Reset the counter
        khashcount.value = int(
            statistics.mean(hash_mean[-50:])
        )  # Calculate average hashrate from last 20 hashrate measurements
        time.sleep(1)


def loadConfig():  # Config loading section
    global username, efficiency, donationlevel, debug, threadcount, useLowerDiff, rigIdentifier, lang

    if not Path(
        resourcesFolder + "/Miner_config.cfg"
    ).is_file():  # Initial configuration section
        print(
            Style.BRIGHT
            + getString("basic_config_tool")
            + resourcesFolder
            + getString("edit_config_file_warning")
        )

        print(
            Style.RESET_ALL
            + getString("dont_have_account")
            + Fore.YELLOW
            + getString("wallet")
            + Fore.WHITE
            + getString("register_warning")
        )

        username = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_username")
            + Fore.WHITE
            + Style.BRIGHT
        )

        efficiency = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_intensity")
            + Fore.WHITE
            + Style.BRIGHT
        )

        threadcount = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_threads")
            + str(multiprocessing.cpu_count())
            + "): "
            + Fore.WHITE
            + Style.BRIGHT
        )

        useLowerDiff = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_lower_difficulty")
            + Fore.WHITE
            + Style.BRIGHT
        )

        rigIdentifier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_rig_identifier")
            + Fore.WHITE
            + Style.BRIGHT
        )
        if rigIdentifier == "y" or rigIdentifier == "Y":
            rigIdentifier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_rig_name")
                + Fore.WHITE
                + Style.BRIGHT
            )
        else:
            rigIdentifier = "None"

        donationlevel = "0"
        if os.name == "nt" or os.name == "posix":
            donationlevel = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_donation_level")
                + Fore.WHITE
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
        if int(threadcount) > int(8):
            threadcount = 8
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
            "donate": donationlevel,
            "identifier": rigIdentifier,
            "language": lang,
            "debug": "n",
        }
        with open(
            resourcesFolder + "/Miner_config.cfg", "w"
        ) as configfile:  # Write data to file
            config.write(configfile)
        efficiency = (
            100 - float(efficiency)
        ) * 0.01  # Calulate efficiency for use with sleep function
        print(Style.RESET_ALL + getString("config_saved"))

    else:  # If config already exists, load from it
        config.read(resourcesFolder + "/Miner_config.cfg")
        username = config["miner"]["username"]
        efficiency = config["miner"]["efficiency"]
        efficiency = (
            100 - float(efficiency)
        ) * 0.01  # Calulate efficiency for use with sleep function
        threadcount = config["miner"]["threads"]
        useLowerDiff = config["miner"]["useLowerDiff"]
        donationlevel = config["miner"]["donate"]
        rigIdentifier = config["miner"]["identifier"]
        debug = config["miner"]["debug"]


def Donate():
    global donationlevel, donatorrunning, donateExecutable

    if os.name == "nt":
        cmd = (
            "cd "
            + resourcesFolder
            + "& Donate_executable.exe -o stratum+tcp://blockmasters.co:6033 -u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR -p PCmW,c=XMG,d=16 -s 4 -e "
        )
    elif os.name == "posix":
        cmd = (
            "cd "
            + resourcesFolder
            + "&& chmod +x Donate_executable && ./Donate_executable -o stratum+tcp://blockmasters.co:6033 -u 9RTb3ikRrWExsF6fis85g7vKqU1tQYVFuR -p PCmL,c=XMG,d=16 -s 4 -e "
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
                + getString("thanks_donation")
            )


def Thread(
    threadid,
    hashcount,
    accepted,
    rejected,
    useLowerDiff,
    khashcount,
    username,
    efficiency,
    rigIdentifier,
):
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
                    + getString("data_error")
                )
                if debug == "y":
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
                        + " net"
                        + str(threadid)
                        + " "
                        + Back.RESET
                        + Fore.YELLOW
                        + getString("connected")
                        + Style.RESET_ALL
                        + Fore.WHITE
                        + getString("connected_server")
                        + str(serverVersion)
                        + ")"
                    )

                else:
                    print(
                        now().strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ")
                        + Style.BRIGHT
                        + Back.GREEN
                        + Fore.WHITE
                        + " sys"
                        + str(threadid)
                        + " "
                        + Back.RESET
                        + Fore.RED
                        + getString("outdated_miner")
                        + minerVersion
                        + "),"
                        + Style.RESET_ALL
                        + Fore.RED
                        + getString("server_is_on_version")
                        + serverVersion
                        + getString("update_warning")
                    )
                break
            except:
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
                    + Fore.RED
                    + getString("connecting_error")
                    + Style.RESET_ALL
                )
                if debug == "y":
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
            + getString("mining_thread")
            + str(threadid)
            + getString("mining_thread_starting")
            + Style.RESET_ALL
            + Fore.WHITE
            + getString("using_algo")
            + Fore.YELLOW
            + str(int(100 - efficiency * 100))
            + f"% {getString('efficiency')}"
        )
        while True:  # Mining section
            try:
                if float(100 - efficiency * 100) < 100:
                    time.sleep(
                        float(efficiency * 5)
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
                    diff = int(job[2])

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
                        hashcount.value += threadhashcount  # Add this thread hash counter to the global counter
                        debugOutput(str(threadid) + "Result found: " + str(ducos1res))
                        while True:
                            soc.send(
                                bytes(
                                    f"{str(ducos1res)},{str(threadhashcount)},Official Python Miner v{str(minerVersion)},{str(rigIdentifier)}",
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
                            if khashcount.value > 1000:
                                formattedhashcount = str(
                                    f"%01.2f" % round(khashcount.value / 1000, 2)
                                    + " MH/s"
                                )
                            else:
                                formattedhashcount = str(
                                    f"%03.0f" % float(khashcount.value) + " kH/s"
                                )
                            debugOutput("Ping: " + ping)

                            if feedback == "GOOD":  # If result was good
                                accepted.value += 1  # Share accepted = increment feedback shares counter by 1
                                title(
                                    getString("duco_python_miner")
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + getString("accepted_shares")
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
                                    + getString("accepted")
                                    + Fore.WHITE
                                    + str(int(accepted.value))
                                    + "/"
                                    + str(int(accepted.value + rejected.value))
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
                                    + " ∙ "
                                    + Style.BRIGHT
                                    + Fore.BLUE
                                    + str(formattedhashcount)
                                    + Fore.WHITE
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str(f"%02.0f" % int(ping))
                                    + "ms"
                                )
                                break  # Repeat

                            elif feedback == "BLOCK":  # If block was found
                                accepted.value += 1  # Share accepted = increment feedback shares counter by 1
                                title(
                                    getString("duco_python_miner")
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + getString("accepted_shares")
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
                                    + getString("block_found")
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
                                    + " ∙ "
                                    + Style.BRIGHT
                                    + Fore.BLUE
                                    + str(formattedhashcount)
                                    + Fore.WHITE
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str(f"%02.0f" % int(ping))
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
                                    + getString("internal_server_error")
                                    + Style.RESET_ALL
                                    + Fore.RED
                                    + getString("retrying")
                                )
                                time.sleep(10)

                            elif feedback == "INVU":  # If user doesn't exist
                                print(
                                    now().strftime(
                                        Style.RESET_ALL + Style.DIM + "%H:%M:%S "
                                    )
                                    + Style.RESET_ALL
                                    + Style.BRIGHT
                                    + Back.BLUE
                                    + Fore.WHITE
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.RED
                                    + getString("mining_user")
                                    + str(username)
                                    + getString("mining_not_exist")
                                    + Style.RESET_ALL
                                    + Fore.RED
                                    + getString("mining_not_exist_warning")
                                )
                                time.sleep(10)

                            else:  # If result was bad
                                rejected.value += 1  # Share rejected = increment bad shares counter by 1
                                title(
                                    getString("duco_python_miner")
                                    + str(minerVersion)
                                    + ") - "
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + getString("accepted_shares")
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
                                    + getString("rejected")
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
                                    + " ∙ "
                                    + Style.BRIGHT
                                    + Fore.BLUE
                                    + str(formattedhashcount)
                                    + Fore.WHITE
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str(f"%02.0f" % int(ping))
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
                    + getString("error_while_mining")
                    + Style.RESET_ALL
                )
                if debug == "y":
                    raise
                time.sleep(5)
                break


def initRichPresence():
    global RPC
    try:
        RPC = Presence(808045598447632384)
        RPC.connect()
    except:  # Discord not launched
        if debug == "y":
            raise


def updateRichPresence():
    startTime = int(time.time())
    while True:
        try:
            hashcount = statistics.mean(hash_mean[-50:])
            if hashcount > 1000:
                hashcount = str(round(hashcount / 1000, 2)) + " MH/s"
            else:
                hashcount = str(int(hashcount)) + " kH/s"
            RPC.update(
                details="Hashrate: " + str(hashcount),
                start=startTime,
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
            debugOutput("Rich presence updated")
        except:  # Discord not launched
            if debug == "y":
                raise
        time.sleep(15)  # 15 seconds to respect Discord rate limit


if __name__ == "__main__":
    multiprocessing.freeze_support()
    cpu = cpuinfo.get_cpu_info()  # Processor info
    init(autoreset=True)  # Enable colorama
    title(getString("duco_python_miner") + str(minerVersion) + ")")

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
            args=(
                x,
                hashcount,
                accepted,
                rejected,
                useLowerDiff,
                khashcount,
                username,
                efficiency,
                rigIdentifier,
            ),
        )
        thread[x].start()
        time.sleep(0.1)
    initRichPresence()
    threading.Thread(target=updateRichPresence).start()
