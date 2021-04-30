#!/usr/bin/env python3
##########################################
# Duino-Coin Python PC Miner (v2.45)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
# Import libraries
import sys
from configparser import ConfigParser
from datetime import datetime
from hashlib import sha1
from json import load as jsonload
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
from os import _exit, execl, mkdir
from os import name as osname
from os import path, system
from pathlib import Path
from platform import system as plsystem
from re import sub
from signal import SIGINT, signal
from socket import socket
from statistics import mean
from subprocess import DEVNULL, Popen, check_call
from threading import Thread as thrThread
from time import ctime, sleep, strptime, time
from multiprocessing import Lock

thread_lock = Lock()


def install(package):
    # Install pip package automatically
    check_call([sys.executable, "-m", "pip", "install", package])
    execl(sys.executable, sys.executable, * sys.argv)


def now():
    # Return datetime object
    return datetime.now()


try:
    # Check if cpuinfo is installed
    import cpuinfo
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + "Cpuinfo is not installed. "
        + "Miner will try to install it. "
        + "If it fails, please manually install \"py-cpuinfo\"."
        + "\nIf you can\'t install it, use the Minimal-PC_Miner.")
    install("py-cpuinfo")


try:
    # Check if colorama is installed
    from colorama import Back, Fore, Style, init
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + "Colorama is not installed. "
        + "Miner will try to install it. "
        + "If it fails, please manually install \"colorama\"."
        + "\nIf you can\'t install it, use the Minimal-PC_Miner.")
    install("colorama")


try:
    # Check if requests is installed
    import requests
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + "Requests is not installed. "
        + "Miner will try to install it. "
        + "If it fails, please manually install \"requests\"."
        + "\nIf you can\'t install it, use the Minimal-PC_Miner.")
    install("requests")

try:
    # Check if pypresence is installed
    from pypresence import Presence
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + "Pypresence is not installed. "
        + "Miner will try to install it. "
        + "If it fails, please manually install \"pypresence\"."
        + "\nIf you can\'t install it, use the Minimal-PC_Miner.")
    install("pypresence")

try:
    # Check if xxhash is installed
    import xxhash
    xxhash_enabled = True
except ModuleNotFoundError:
    print(
        now().strftime("%H:%M:%S ")
        + "Xxhash is not installed. "
        + "Continuing without xxhash support.")
    xxhash_enabled = False


# Global variables
MINER_VER = "2.45"  # Version number
SOC_TIMEOUT = 30  # Socket timeout
RESOURCES_DIR = "PCMiner_" + str(MINER_VER) + "_resources"
donatorrunning = False
debug = "n"
rig_identiier = "None"
requested_diff = "NET"
algorithm = "DUCO-S1"
server_ip_file = ("https://raw.githubusercontent.com/"
                  + "revoxhere/"
                  + "duino-coin/gh-pages/"
                  + "serverip.txt")  # Serverip file
config = ConfigParser()
donation_level = 0
thread = []
totalhashrate_mean = []

# Create resources folder if it doesn't exist
if not path.exists(RESOURCES_DIR):
    mkdir(RESOURCES_DIR)

# Check if languages file exists
if not Path(RESOURCES_DIR + "/langs.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/master/Resources/"
           + "PC_Miner_langs.json")
    r = requests.get(url)
    with open(RESOURCES_DIR + "/langs.json", "wb") as f:
        f.write(r.content)

# Load language file
with open(RESOURCES_DIR + "/langs.json", "r", encoding="utf8") as lang_file:
    lang_file = jsonload(lang_file)

# OS X invalid locale hack
if plsystem() == "Darwin":
    if getlocale()[0] is None:
        setlocale(LC_ALL, "en_US.UTF-8")

# Check if miner is configured, if it isn't, autodetect language
try:
    if not Path(RESOURCES_DIR + "/Miner_config.cfg").is_file():
        locale = getdefaultlocale()[0]
        if locale.startswith("es"):
            lang = "spanish"
        elif locale.startswith("pl"):
            lang = "polish"
        elif locale.startswith("fr"):
            lang = "french"
        elif locale.startswith("ru"):
            lang = "russian"
        elif locale.startswith("de"):
            lang = "german"
        elif locale.startswith("tr"):
            lang = "turkish"
        elif locale.startswith("zh"):
            lang = "chinese_simplified"
        else:
            lang = "english"
    else:
        # Read language variable from configfile
        try:
            config.read(RESOURCES_DIR + "/Miner_config.cfg")
            lang = config["miner"]["language"]
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
        print(now().strftime(Style.DIM + "%H:%M:%S.%f ") + "DEBUG: " + text)


def title(title):
    # Set window title
    if osname == "nt":
        # Windows systems
        system("title " + title)
    else:
        # Most standard terminals
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def handler(signal_received, frame):
    # SIGINT handler
    if current_process().name == "MainProcess":
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


def Greeting():
    # Greeting message
    global greeting
    print(Style.RESET_ALL)

    if requested_diff == "LOW":
        diffName = getString("low_diff_short")
    elif requested_diff == "MEDIUM":
        diffName = getString("medium_diff_short")
    else:
        diffName = getString("net_diff_short")

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

    print(
        Style.DIM
        + Fore.YELLOW
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
        + Fore.YELLOW
        + " ‖ "
        + Style.NORMAL
        + Fore.YELLOW
        + "https://github.com/revoxhere/duino-coin")

    try:
        print(
            Style.DIM
            + Fore.YELLOW
            + " ‖ "
            + Style.NORMAL
            + Fore.RESET
            + "CPU: "
            + Style.BRIGHT
            + Fore.YELLOW
            + str(threadcount)
            + "x "
            + str(cpu["brand_raw"]))
    except Exception as e:
        debugOutput("Error displaying CPU message: " + str(e))

    if osname == "nt" or osname == "posix":
        print(
            Style.DIM
            + Fore.YELLOW
            + " ‖ "
            + Style.NORMAL
            + Fore.RESET
            + getString("donation_level")
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donation_level))
    print(
        Style.DIM
        + Fore.YELLOW
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + getString("algorithm")
        + Style.BRIGHT
        + Fore.YELLOW
        + algorithm
        + " @ "
        + diffName)
    print(
        Style.DIM
        + Fore.YELLOW
        + " ‖ "
        + Style.NORMAL
        + Fore.RESET
        + getString("rig_identifier")
        + Style.BRIGHT
        + Fore.YELLOW
        + rig_identiier)
    print(
        Style.DIM
        + Fore.YELLOW
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
                "OS is Windows, downloading developer donation executable")
            url = ("https://github.com/"
                   + "revoxhere/"
                   + "duino-coin/blob/useful-tools/"
                   + "DonateExecutableLinux?raw=true")
            r = requests.get(url)
            with open(RESOURCES_DIR + "/Donate_executable", "wb") as f:
                f.write(r.content)


def loadConfig():
    # Config loading section
    global username
    global efficiency
    global donation_level
    global debug
    global threadcount
    global requested_diff
    global rig_identiier
    global lang
    global algorithm

    # Initial configuration
    if not Path(RESOURCES_DIR + "/Miner_config.cfg").is_file():
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

        if xxhash_enabled:
            print(
                Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RESET
                + "1"
                + Style.NORMAL
                + " - DUCO-S1 ("
                + getString("recommended")
                + ")")
            print(
                Style.RESET_ALL
                + Style.BRIGHT
                + Fore.RESET
                + "2"
                + Style.NORMAL
                + " - XXHASH")
            algorithm = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_algorithm")
                + Fore.RESET
                + Style.BRIGHT)
        else:
            algorithm = "1"

        efficiency = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_intensity")
            + Fore.RESET
            + Style.BRIGHT)

        threadcount = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_threads")
            + str(cpu_count())
            + "): "
            + Fore.RESET
            + Style.BRIGHT)

        print(
            Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RESET
            + "1"
            + Style.NORMAL
            + " - "
            + getString("low_diff"))
        print(
            Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RESET
            + "2"
            + Style.NORMAL
            + " - "
            + getString("medium_diff"))
        print(
            Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RESET
            + "3"
            + Style.NORMAL
            + " - "
            + getString("net_diff"))

        requested_diff = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_difficulty")
            + Fore.RESET
            + Style.BRIGHT)

        rig_identiier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + getString("ask_rig_identifier")
            + Fore.RESET
            + Style.BRIGHT)

        if rig_identiier == "y" or rig_identiier == "Y":
            rig_identiier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_rig_name")
                + Fore.RESET
                + Style.BRIGHT)
        else:
            rig_identiier = "None"

        donation_level = "0"
        if osname == "nt" or osname == "posix":
            donation_level = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("ask_donation_level")
                + Fore.RESET
                + Style.BRIGHT)

        # Check wheter efficiency is correct
        efficiency = sub(r"\D", "", efficiency)
        if efficiency == "":
            efficiency = 95
        elif float(efficiency) > int(100):
            efficiency = 100
        elif float(efficiency) < int(1):
            efficiency = 1

        # Check wheter threadcount is correct
        threadcount = sub(r"\D", "", threadcount)
        if threadcount == "":
            threadcount = cpu_count()
        elif int(threadcount) > int(8):
            threadcount = 8
            print(
                Style.RESET_ALL
                + Style.BRIGHT
                + getString("max_threads_notice"))
        elif int(threadcount) < int(1):
            threadcount = 1

        # Check wheter algo setting is correct
        if algorithm == "2":
            algorithm = "XXHASH"
        else:
            algorithm = "DUCO-S1"

        # Check wheter diff setting is correct
        if requested_diff == "1":
            requested_diff = "LOW"
        elif requested_diff == "2":
            requested_diff = "MEDIUM"
        else:
            requested_diff = "NET"

        # Check wheter donation_level is correct
        donation_level = sub(r"\D", "", donation_level)
        if donation_level == "":
            donation_level = 1
        elif float(donation_level) > int(5):
            donation_level = 5
        elif float(donation_level) < int(0):
            donation_level = 0

        # Format data
        config["miner"] = {
            "username": username,
            "efficiency": efficiency,
            "threads": threadcount,
            "requested_diff": requested_diff,
            "donate": donation_level,
            "identifier": rig_identiier,
            "algorithm": algorithm,
            "language": lang,
            "debug": "n"
        }
        # Write data to configfile
        with open(RESOURCES_DIR + "/Miner_config.cfg", "w") as configfile:
            config.write(configfile)

        # Calulate efficiency for later use with sleep function
        efficiency = (100 - float(efficiency)) * 0.01

        print(Style.RESET_ALL + getString("config_saved"))

    else:
        # If config already exists, load data from it
        config.read(RESOURCES_DIR + "/Miner_config.cfg")
        username = config["miner"]["username"]
        efficiency = config["miner"]["efficiency"]
        threadcount = config["miner"]["threads"]
        requested_diff = config["miner"]["requested_diff"]
        donation_level = config["miner"]["donate"]
        algorithm = config["miner"]["algorithm"]
        rig_identiier = config["miner"]["identifier"]
        debug = config["miner"]["debug"]
        # Calulate efficiency for use with sleep function
        efficiency = (100 - float(efficiency)) * 0.01


def Donate():
    global donation_level
    global donatorrunning
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
        sleep(10)

    elif donatorrunning == False:
        if int(donation_level) == 5:
            cmd += "95"
        elif int(donation_level) == 4:
            cmd += "75"
        elif int(donation_level) == 3:
            cmd += "50"
        elif int(donation_level) == 2:
            cmd += "20"
        elif int(donation_level) == 1:
            cmd += "10"
        if int(donation_level) > 0:
            debugOutput(getString("starting_donation"))
            donatorrunning = True
            # Launch CMD as subprocess
            donateExecutable = Popen(
                cmd, shell=True, stderr=DEVNULL)
            prettyPrint(
                "sys0",
                getString("thanks_donation"),
                "warning")


def ducos1(
        lastBlockHash,
        expectedHash,
        difficulty):
    # DUCO-S1 algorithm
    # Measure starting time
    timeStart = time()
    base_hash = sha1(str(lastBlockHash).encode('ascii'))
    temp_hash = None
    # Loop from 1 too 100*diff
    for ducos1res in range(100 * int(difficulty) + 1):
        # Generate hash
        temp_hash = base_hash.copy()
        temp_hash.update(str(ducos1res).encode('ascii'))
        ducos1 = temp_hash.hexdigest()
        # Check if result was found
        if ducos1 == expectedHash:
            # Measure finish time
            timeStop = time()
            # Calculate hashrate
            timeDelta = timeStop - timeStart
            hashrate = ducos1res / timeDelta
            return [ducos1res, hashrate]


def ducos1xxh(
        lastBlockHash,
        expectedHash,
        difficulty):
    # XXHASH algorithm
    # Measure starting time
    timeStart = time()
    # Loop from 1 too 100*diff
    for ducos1xxres in range(100 * int(difficulty) + 1):
        # Generate hash
        ducos1xx = xxhash.xxh64(
            str(lastBlockHash) + str(ducos1xxres), seed=2811)
        ducos1xx = ducos1xx.hexdigest()
        # Check if result was found
        if ducos1xx == expectedHash:
            # Measure finish time
            timeStop = time()
            # Calculate hashrate
            timeDelta = timeStop - timeStart
            hashrate = ducos1xxres / timeDelta
            return [ducos1xxres, hashrate]


def Thread(
        threadid,
        accepted,
        rejected,
        requested_diff,
        khashcount,
        username,
        efficiency,
        rig_identiier,
        algorithm,
        hashrates_list,
        totalhashrate_mean):
    # Mining section for every thread
    while True:
        # Grab server IP and port
        while True:
            try:
                # Use request to grab data from raw github file
                res = requests.get(server_ip_file, data=None)
                if res.status_code == 200:
                    # Read content and split into lines
                    content = (res.content.decode().splitlines())
                    # Line 1 = IP
                    masterServer_address = content[0]
                    # Line 2 = port
                    masterServer_port = content[1]
                    debugOutput(
                        "Retrieved pool IP: "
                        + masterServer_address
                        + ":"
                        + str(masterServer_port))
                    break
            except Exception as e:
                # If there was an error with grabbing data from GitHub
                prettyPrint(
                    "net"
                    + str(threadid),
                    getString("data_error")
                    + Style.NORMAL
                    + Fore.RESET
                    + " (git err: "
                    + str(e)
                    + ")",
                    "error")
                debugOutput("GitHub error: " + str(e))
                sleep(10)

        # Connect to the server
        while True:
            try:
                soc = socket()
                # Establish socket connection to the server
                soc.connect((str(masterServer_address),
                             int(masterServer_port)))
                soc.settimeout(SOC_TIMEOUT)
                serverVersion = soc.recv(3).decode().rstrip(
                    "\n")  # Get server version
                debugOutput("Server version: " + serverVersion)
                if (float(serverVersion) <= float(MINER_VER)
                        and len(serverVersion) == 3):
                    # If miner is up-to-date, display a message and continue
                    prettyPrint(
                        "net"
                        + str(threadid),
                        getString("connected")
                        + Fore.RESET
                        + Style.NORMAL
                        + getString("connected_server")
                        + str(serverVersion)
                        + ")",
                        "success")
                    break

                else:
                    # Miner is outdated
                    prettyPrint(
                        "sys"
                        + str(threadid),
                        getString("outdated_miner")
                        + MINER_VER
                        + ") -"
                        + getString("server_is_on_version")
                        + serverVersion
                        + Style.NORMAL
                        + Fore.RESET
                        + getString("update_warning"),
                        "warning")
                    break
            except Exception as e:
                # Socket connection error
                prettyPrint(
                    "net"
                    + str(threadid),
                    getString("connecting_error")
                    + Style.NORMAL
                    + Fore.RESET
                    + " (net err: "
                    + str(e)
                    + ")",
                    "error")
                debugOutput("Connection error: " + str(e))
                sleep(10)

        if algorithm == "XXHASH":
            using_algo = getString("using_algo_xxh")
        else:
            using_algo = getString("using_algo")

        prettyPrint(
            "sys"
            + str(threadid),
            getString("mining_thread")
            + str(threadid)
            + getString("mining_thread_starting")
            + Style.NORMAL
            + Fore.RESET
            + using_algo
            + Fore.YELLOW
            + str(int(100 - efficiency * 100))
            + "% "
            + getString("efficiency"),
            "success")

        # Mining section
        while True:
            try:
                # If efficiency lower than 100...
                if float(100 - efficiency * 100) < 100:
                    # ...sleep some time
                    sleep(float(efficiency * 5))
                while True:
                    # Ask the server for job
                    if algorithm == "XXHASH":
                        soc.sendall(bytes(
                            "JOBXX,"
                            + str(username)
                            + ","
                            + str(requested_diff),
                            encoding="utf8"))
                    else:
                        soc.sendall(bytes(
                            "JOB,"
                            + str(username)
                            + ","
                            + str(requested_diff),
                            encoding="utf8"))

                    job = soc.recv(128).decode().rstrip("\n")
                    job = job.split(",")  # Get work from pool
                    debugOutput("Received: " + str(job))

                    if job[1] == "This user doesn't exist":
                        prettyPrint(
                            "cpu"
                            + str(threadid),
                            getString("mining_user")
                            + str(username)
                            + getString("mining_not_exist")
                            + Style.NORMAL
                            + Fore.RESET
                            + getString("mining_not_exist_warning"),
                            "error")
                        sleep(10)

                    elif job[0] and job[1] and job[2]:
                        diff = int(job[2])
                        debugOutput(str(threadid) +
                                    "Job received: "
                                    + str(job))
                        # If job received, continue to hashing algo
                        break

                while True:
                    # Call DUCOS-1 hasher
                    computetimeStart = time()
                    if algorithm == "XXHASH":
                        algo_back_color = Back.CYAN
                        result = ducos1xxh(job[0], job[1], diff)
                    else:
                        algo_back_color = Back.YELLOW
                        result = ducos1(job[0], job[1], diff)
                    computetimeStop = time()
                    # Measure compute time
                    computetime = computetimeStop - computetimeStart
                    # Convert it to miliseconds
                    computetime = computetime
                    # Read result from ducos1 hasher
                    ducos1res = result[0]
                    debugOutput("Thread "
                                + str(threadid)
                                + ": result found: "
                                + str(ducos1res))

                    # Convert H/s to kH/s
                    threadhashcount = int(result[1] / 1000)
                    # Add this thread's hash counter
                    # to the global hashrate counter
                    hashrates_list[threadid] = threadhashcount
                    # Calculate total hashrate of all thrads
                    sharehashrate = 0
                    for thread in hashrates_list.keys():
                        sharehashrate += hashrates_list[thread]
                    totalhashrate_mean.append(sharehashrate)
                    # Get average from the last 20 hashrate measurements
                    totalhashrate = mean(totalhashrate_mean[-20:])

                    while True:
                        # Send result of hashing algorithm to the server
                        soc.sendall(bytes(
                            str(ducos1res)
                            + ","
                            + str(threadhashcount * 1000)
                            + ","
                            + "Official PC Miner ("
                            + str(algorithm)
                            + ") v"
                            + str(MINER_VER)
                            + ","
                            + str(rig_identiier),
                            encoding="utf8"))

                        responsetimetart = now()
                        # Get feedback
                        feedback = soc.recv(8).decode().rstrip("\n")
                        responsetimestop = now()
                        # Measure server ping
                        ping = str(int(
                            (responsetimestop - responsetimetart).microseconds
                            / 1000))
                        debugOutput("Thread "
                                    + str(threadid)
                                    + ": Feedback received: "
                                    + str(feedback)
                                    + " Ping: "
                                    + str(ping))

                        if totalhashrate > 800:
                            # Format hashcount to MH/s
                            formattedhashcount = str(
                                "%03.2f" % round(totalhashrate / 1000, 2)
                                + " MH/s")
                        else:
                            # Stay with kH/s
                            formattedhashcount = str(
                                "%03.0f" % float(totalhashrate)
                                + " kH/s")

                        if (totalhashrate > 2000
                                and accepted.value % 10 == 0):
                            prettyPrint("sys0",
                                        " " + getString("max_hashrate_notice"),
                                        "warning")

                        if feedback == "GOOD":
                            # If result was correct
                            accepted.value += 1
                            title(
                                getString("duco_python_miner")
                                + str(MINER_VER)
                                + ") - "
                                + str(accepted.value)
                                + "/"
                                + str(accepted.value + rejected.value)
                                + getString("accepted_shares"))
                            with thread_lock:
                                print(
                                    Style.RESET_ALL
                                    + Fore.WHITE
                                    + now().strftime(Style.DIM + "%H:%M:%S ")
                                    + Style.BRIGHT
                                    + algo_back_color
                                    + Fore.RESET
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.GREEN
                                    + " ✓"
                                    + getString("accepted")
                                    + Fore.RESET
                                    + str(int(accepted.value))
                                    + "/"
                                    + str(int(accepted.value + rejected.value))
                                    + Fore.YELLOW
                                    + " ("
                                    + str(int(
                                        (accepted.value
                                            / (accepted.value + rejected.value)
                                         * 100)))
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.RESET
                                    + " ∙ "
                                    + str("%05.2f" % float(computetime))
                                    + "s"
                                    + Style.NORMAL
                                    + " ∙ "
                                    + Fore.BLUE
                                    + Style.BRIGHT
                                    + str(formattedhashcount)
                                    + Fore.RESET
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str("%02.0f" % int(ping))
                                    + "ms")

                        elif feedback == "BLOCK":
                            # If block was found
                            accepted.value += 1
                            title(
                                getString("duco_python_miner")
                                + str(MINER_VER)
                                + ") - "
                                + str(accepted.value)
                                + "/"
                                + str(accepted.value + rejected.value)
                                + getString("accepted_shares"))
                            with thread_lock:
                                print(
                                    Style.RESET_ALL
                                    + Fore.WHITE
                                    + now().strftime(Style.DIM + "%H:%M:%S ")
                                    + Style.BRIGHT
                                    + algo_back_color
                                    + Fore.RESET
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Back.RESET
                                    + Fore.CYAN
                                    + " ✓"
                                    + getString("block_found")
                                    + Fore.RESET
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + Fore.YELLOW
                                    + " ("
                                    + str(int(
                                        (accepted.value
                                            / (accepted.value + rejected.value)
                                         * 100)))
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.RESET
                                    + " ∙ "
                                    + str("%05.2f" % float(computetime))
                                    + "s"
                                    + Style.NORMAL
                                    + " ∙ "
                                    + Fore.BLUE
                                    + Style.BRIGHT
                                    + str(formattedhashcount)
                                    + Fore.RESET
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str("%02.0f" % int(ping))
                                    + "ms")

                        else:
                            # If result was incorrect
                            rejected.value += 1
                            title(
                                getString("duco_python_miner")
                                + str(MINER_VER)
                                + ") - "
                                + str(accepted.value)
                                + "/"
                                + str(accepted.value + rejected.value)
                                + getString("accepted_shares"))
                            with thread_lock:
                                print(
                                    Style.RESET_ALL
                                    + Fore.WHITE
                                    + now().strftime(Style.DIM + "%H:%M:%S ")
                                    + algo_back_color
                                    + Back.YELLOW
                                    + Fore.RESET
                                    + " cpu"
                                    + str(threadid)
                                    + " "
                                    + Style.BRIGHT
                                    + Back.RESET
                                    + Fore.RED
                                    + " ✗"
                                    + getString("rejected")
                                    + Fore.RESET
                                    + str(accepted.value)
                                    + "/"
                                    + str(accepted.value + rejected.value)
                                    + Fore.YELLOW
                                    + " ("
                                    + str(int(
                                        (accepted.value
                                            / (accepted.value + rejected.value)
                                         * 100)))
                                    + "%)"
                                    + Style.NORMAL
                                    + Fore.RESET
                                    + " ∙ "
                                    + str("%05.2f" % float(computetime))
                                    + "s"
                                    + Style.NORMAL
                                    + " ∙ "
                                    + Fore.BLUE
                                    + Style.BRIGHT
                                    + str(formattedhashcount)
                                    + Fore.RESET
                                    + Style.NORMAL
                                    + " @ diff "
                                    + str(diff)
                                    + " ∙ "
                                    + Fore.CYAN
                                    + "ping "
                                    + str("%02.0f" % int(ping))
                                    + "ms")
                        break
                    break
            except Exception as e:
                prettyPrint(
                    "net"
                    + str(threadid),
                    getString("error_while_mining")
                    + Style.NORMAL
                    + Fore.RESET
                    + " (mining err: "
                    + str(e)
                    + ")",
                    "error")
                debugOutput("Error while mining: " + str(e))
                sleep(5)
                break


def prettyPrint(messageType, message, state):
    # Print output messages in the DUCO "standard"
    # Usb/net/sys background
    if messageType.startswith("net"):
        background = Back.BLUE
    elif messageType.startswith("cpu"):
        background = Back.YELLOW
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


def initRichPresence():
    # Initialize Discord rich presence
    global RPC
    try:
        RPC = Presence(808045598447632384)
        RPC.connect()
        debugOutput("Discord rich presence initialized")
    except Exception as e:
        # Discord not launched
        debugOutput("Error launching Discord RPC thead: " + str(e))


def updateRichPresence():
    # Update rich presence status
    startTime = int(time())
    while True:
        try:
            # Calculate average total hashrate with prefix
            totalhashrate = mean(totalhashrate_mean[-20:])
            if totalhashrate > 800:
                totalhashrate = str(round(totalhashrate / 1000, 2)) + " MH/s"
            else:
                totalhashrate = str(round(totalhashrate, 1)) + " kH/s"

            RPC.update(
                details="Hashrate: " + str(totalhashrate),
                start=startTime,
                state="Acc. shares: "
                + str(accepted.value)
                + "/"
                + str(rejected.value + accepted.value),
                large_image="ducol",
                large_text="Duino-Coin, "
                + "a coin that can be mined with almost everything, "
                + "including AVR boards",
                buttons=[
                    {"label": "Learn more",
                     "url": "https://duinocoin.com"},
                    {"label": "Discord Server",
                     "url": "https://discord.gg/k48Ht5y"}])
            debugOutput("Rich presence updated")
        except Exception as e:
            # Discord not launched
            debugOutput("Error launching Discord RPC thead: " + str(e))
        sleep(15)  # 15 seconds to respect Discord rate limit


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    # Processor info
    cpu = cpuinfo.get_cpu_info()
    # Colorama
    init(autoreset=True)
    title(getString("duco_python_miner") + str(MINER_VER) + ")")

    try:
        from multiprocessing import (
            Manager, 
            Process, 
            Value, 
            cpu_count, 
            current_process
        )
        manager = Manager()
        # Multiprocessing globals
        khashcount = Value("i", 0)
        accepted = Value("i", 0)
        rejected = Value("i", 0)
        hashrates_list = manager.dict()
        totalhashrate_mean = manager.list()
    except Exception as e:
        print(e)
        prettyPrint(
            "sys0",
            " Multiprocessing is not available. "
            + "Please check permissions and/or your python installation. "
            + "Exiting in 15s.",
            "error")
        sleep(15)
        _exit(1)

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
            + " (config load err: "
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
        prettyPrint(
            "sys0",
            "Error displaying greeting message"
            + Style.NORMAL
            + Fore.RESET
            + " (greeting err: "
            + str(e)
            + ")",
            "error")
        debugOutput("Error displaying greeting message: " + str(e))

    try:
        # Start donation thread
        Donate()
    except Exception as e:
        debugOutput("Error launching donation thread: " + str(e))

    try:
        for x in range(int(threadcount)):
            # Launch duco mining threads
            thread.append(x)
            thread[x] = Process(
                target=Thread,
                args=(
                    x,
                    accepted,
                    rejected,
                    requested_diff,
                    khashcount,
                    username,
                    efficiency,
                    rig_identiier,
                    algorithm,
                    hashrates_list,
                    totalhashrate_mean))
            thread[x].start()
            sleep(0.1)
    except Exception as e:
        prettyPrint(
            "sys0",
            "Error launching CPU thread(s)"
            + Style.NORMAL
            + Fore.RESET
            + " (cpu launch err: "
            + str(e)
            + ")",
            "error")
        debugOutput("Error launching CPU thead(s): " + str(e))

    try:
        # Discord rich presence threads
        initRichPresence()
        thrThread(
            target=updateRichPresence).start()
    except Exception as e:
        debugOutput("Error launching Discord RPC thead: " + str(e))
