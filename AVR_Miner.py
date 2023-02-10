#!/usr/bin/env python3
"""
Duino-Coin Official AVR Miner 3.4 © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin
Duino-Coin Team & Community 2019-2023
"""

from os import _exit, mkdir
from os import name as osname
from os import path
from os import system as ossystem
from platform import machine as osprocessor
from platform import system
import sys

from configparser import ConfigParser
from pathlib import Path

from json import load as jsonload
from random import choice
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
import zipfile

from re import sub
from socket import socket
from datetime import datetime
from statistics import mean
from signal import SIGINT, signal
from time import ctime, sleep, strptime, time
import pip

from subprocess import DEVNULL, Popen, check_call, call
from threading import Thread
from threading import Lock as thread_lock
from threading import Semaphore

import base64 as b64

import os
printlock = Semaphore(value=1)


# Python <3.5 check
f"Your Python version is too old. Duino-Coin Miner requires version 3.6 or above. Update your packages and try again"


def install(package):
    try:
        pip.main(["install",  package])
    except AttributeError:
        check_call([sys.executable, '-m', 'pip', 'install', package])
    call([sys.executable, __file__])


try:
    from serial import Serial
    import serial.tools.list_ports
except ModuleNotFoundError:
    print("Pyserial is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install pyserial")
    install('pyserial')

try:
    import requests
except ModuleNotFoundError:
    print("Requests is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install requests")
    install('requests')

try:
    from colorama import Back, Fore, Style, init
    init(autoreset=True)
except ModuleNotFoundError:
    print("Colorama is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install colorama")
    install("colorama")

try:
    from pypresence import Presence
except ModuleNotFoundError:
    print("Pypresence is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install pypresence")
    install("pypresence")

try:
    import psutil
except ModuleNotFoundError:
    print("Psutil is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install psutil")
    install("psutil")

def now():
    return datetime.now()


def port_num(com):
    return str(''.join(filter(str.isdigit, com)))


class Settings:
    VER = '3.4'
    SOC_TIMEOUT = 15
    REPORT_TIME = 120
    AVR_TIMEOUT = 10
    BAUDRATE = 115200
    DATA_DIR = "Duino-Coin AVR Miner " + str(VER)
    SEPARATOR = ","
    ENCODING = "utf-8"
    TEMP_FOLDER = "Temp"

    try:
        # Raspberry Pi latin users can't display this character
        "‖".encode(sys.stdout.encoding)
        BLOCK = " ‖ "
    except:
        BLOCK = " | "
    PICK = ""
    COG = " @"
    if (osname != "nt"
        or bool(osname == "nt"
                and os.environ.get("WT_SESSION"))):
        # Windows' cmd does not support emojis, shame!
        # And some codecs same, for example the Latin-1 encoding don`t support emoji
        try:
            "⛏ ⚙".encode(sys.stdout.encoding) # if the terminal support emoji
            PICK = " ⛏"
            COG = " ⚙"
        except UnicodeEncodeError: # else
            PICK = ""
            COG = " @"

def check_updates():
    """
    Function that checks if the miner is updated.
    Downloads the new version and restarts the miner.
    """
    try:
        data = requests.get(
            "https://api.github.com/repos/revoxhere/duino-coin/releases/latest"
        ).json()

        zip_file = "Duino-Coin_" + data["tag_name"] + "_linux.zip"
        if sys.platform == "win32":
            zip_file = "Duino-Coin_" + data["tag_name"] + "_windows.zip"

        process = psutil.Process(os.getpid())
        running_script = False # If the process is from script
        if "python" in process.name():
            running_script = True

        if float(Settings.VER) < float(data["tag_name"]): # If is outdated
            update = input(Style.BRIGHT + get_string("new_version"))
            if update == "Y" or update == "y":
                pretty_print("sys0", get_string("updating"), "warning")

                DATA_DIR = "Duino-Coin AVR Miner " + str(data["tag_name"]) # Create new version config folder
                if not path.exists(DATA_DIR):
                    mkdir(DATA_DIR)

                try:
                    config.read(str(Settings.DATA_DIR) + '/Settings.cfg') # read the previous config

                    config["AVR Miner"] = {
                        'username':         config["AVR Miner"]['username'],
                        'avrport':          config["AVR Miner"]['avrport'],
                        'donate':           int(config["AVR Miner"]['donate']),
                        'language':         config["AVR Miner"]['language'],
                        'identifier':       config["AVR Miner"]['identifier'],
                        'debug':            config["AVR Miner"]['debug'],
                        "soc_timeout":      int(config["AVR Miner"]["soc_timeout"]),
                        "avr_timeout":      float(config["AVR Miner"]["avr_timeout"]),
                        "discord_presence": config["AVR Miner"]["discord_presence"],
                        "periodic_report":  int(config["AVR Miner"]["periodic_report"]),
                        "mining_key":       config["AVR Miner"]["mining_key"]
                    }

                    with open(str(DATA_DIR) # save it on the new version folder
                            + '/Settings.cfg', 'w') as configfile:
                        config.write(configfile)

                    pretty_print("sys0", Style.RESET_ALL + get_string('config_saved'), "success")
                except Exception as e:
                    pretty_print("sys0", f"Error saving configfile: {e}" + str(e), "error")
                    pretty_print("sys0", "Config won't be carried to the next version", "warning")

                if not os.path.exists(Settings.TEMP_FOLDER): # Make the Temp folder
                    os.makedirs(Settings.TEMP_FOLDER) 

                file_path = os.path.join(Settings.TEMP_FOLDER, zip_file)
                download_url = "https://github.com/revoxhere/duino-coin/releases/download/" + data["tag_name"] + "/" + zip_file

                if running_script:
                    file_path = os.path.join(".", "AVR_Miner_"+data["tag_name"]+".py")
                    download_url = "https://raw.githubusercontent.com/revoxhere/duino-coin/master/AVR_Miner.py"
                    
                r = requests.get(download_url, stream=True)
                if r.ok:
                    start = time()
                    dl = 0
                    file_size = int(r.headers["Content-Length"]) # Get file size
                    pretty_print("sys0", 
                        f"Saving update to: {os.path.abspath(file_path)}", "warning")
                    with open(file_path, 'wb') as f: 
                        for chunk in r.iter_content(chunk_size=1024 * 8): # Download file in chunks
                            if chunk:
                                dl += len(chunk)
                                done = int(50 * dl / file_size)
                                dl_perc = str(int(100 * dl / file_size))

                                if running_script:
                                    done = int(12.5 * dl / file_size)
                                    dl_perc = str(int(22.5 * dl / file_size))

                                sys.stdout.write(
                                    "\r%s [%s%s] %s %s" % (
                                        dl_perc + "%", 
                                        '#' * done, 
                                        ' ' * (50-done),
                                        str(round(os.path.getsize(file_path) / 1024 / 1024, 2)) + " MB ",
                                        str((dl // (time() - start)) // 1024) + " KB/s")) # ProgressBar
                                sys.stdout.flush()
                                f.write(chunk)
                                f.flush()
                                os.fsync(f.fileno())
                    pretty_print("sys0", "Download complete", "success")
                    if not running_script:
                        pretty_print("sys0", "Unpacking archive", "warning")
                        with zipfile.ZipFile(file_path, 'r') as zip_ref: # Unzip the file
                            for file in zip_ref.infolist():
                                if "AVR_Miner" in file.filename:
                                    if sys.platform == "win32":
                                        file.filename = "AVR_Miner_"+data["tag_name"]+".exe" # Rename the file
                                    else:
                                        file.filename = "AVR_Miner_"+data["tag_name"] 
                                    zip_ref.extract(file, ".")
                        pretty_print("sys0", "Unpacking complete", "success")
                        os.remove(file_path) # Delete the zip file
                        os.rmdir(Settings.TEMP_FOLDER) # Delete the temp folder

                        if sys.platform == "win32":
                            os.startfile(os.getcwd() + "\\AVR_Miner_"+data["tag_name"]+".exe") # Start the miner
                        else: # os.startfile is only for windows
                            os.system(os.getcwd() + "/AVR_Miner_"+data["tag_name"]) 
                    else:
                        if sys.platform == "win32":
                            os.system(file_path)
                        else:
                            os.system("python3 " + file_path)
                    sys.exit() # Exit the program
                else:  # HTTP status code 4XX/5XX
                    pretty_print( "sys0", f"Update failed: {r.status_code}: {r.text}", "error")
            else:
                pretty_print("sys0", "Update aborted", "warning")
    except Exception as e:
        print(e)
        sys.exit()

def check_mining_key(user_settings):
    user_settings = user_settings["AVR Miner"]

    if user_settings["mining_key"] != "None":
        key = "&k=" + b64.b64decode(user_settings["mining_key"]).decode('utf-8')
    else:
        key = ''

    response = requests.get(
        "https://server.duinocoin.com/mining_key"
            + "?u=" + user_settings["username"]
            + key,
        timeout=10
    ).json()

    if response["success"] and not response["has_key"]: # if the user doesn't have a mining key
        user_settings["mining_key"] = "None"
        config["AVR Miner"] = user_settings

        with open(Settings.DATA_DIR + '/Settings.cfg',
            "w") as configfile:
            config.write(configfile)
            print("sys0",
                Style.RESET_ALL + get_string("config_saved"),
                "info")
        sleep(1.5)   
        return

    if not response["success"]:
        if user_settings["mining_key"] == "None":
            pretty_print(
                "sys0",
                get_string("mining_key_required"),
                "warning")

            mining_key = input("Enter your mining key: ")
            user_settings["mining_key"] = b64.b64encode(mining_key.encode("utf-8")).decode('utf-8')
            config["AVR Miner"] = user_settings

            with open(Settings.DATA_DIR + '/Settings.cfg',
                      "w") as configfile:
                config.write(configfile)
                print("sys0",
                    Style.RESET_ALL + get_string("config_saved"),
                    "info")
            sleep(1.5)
            check_mining_key(config)
        else:
            pretty_print(
                "sys0",
                get_string("invalid_mining_key"),
                "error")

            retry = input("You want to retry? (y/n): ")
            if retry == "y" or retry == "Y":
                mining_key = input("Enter your mining key: ")
                user_settings["mining_key"] = b64.b64encode(mining_key.encode("utf-8")).decode('utf-8')
                config["AVR Miner"] = user_settings

                with open(Settings.DATA_DIR + '/Settings.cfg',
                        "w") as configfile:
                    config.write(configfile)
                print("sys0",
                    Style.RESET_ALL + get_string("config_saved"),
                    "info")
                sleep(1.5)
                check_mining_key(config)
            else:
                return


class Client:
    """
    Class helping to organize socket connections
    """
    def connect(pool: tuple):
        s = socket()
        s.settimeout(Settings.SOC_TIMEOUT)
        s.connect((pool))
        return s

    def send(s, msg: str):
        sent = s.sendall(str(msg).encode(Settings.ENCODING))
        return True

    def recv(s, limit: int = 128):
        data = s.recv(limit).decode(Settings.ENCODING).rstrip("\n")
        return data

    def fetch_pool():
        while True:
            pretty_print("net0", get_string("connection_search"),
                         "info")
            try:
                response = requests.get(
                    "https://server.duinocoin.com/getPool",
                    timeout=10).json()

                if response["success"] == True:
                    pretty_print("net0", get_string("connecting_node")
                                 + response["name"],
                                 "info")

                    NODE_ADDRESS = response["ip"]
                    NODE_PORT = response["port"]
                    
                    return (NODE_ADDRESS, NODE_PORT)

                elif "message" in response:
                    pretty_print(f"Warning: {response['message']}"
                                 + ", retrying in 15s", "warning", "net0")
                    sleep(15)
                else:
                    raise Exception(
                        "no response - IP ban or connection error")
            except Exception as e:
                if "Expecting value" in str(e):
                    pretty_print("net0", get_string("node_picker_unavailable")
                                 + f"15s {Style.RESET_ALL}({e})",
                                 "warning")
                else:
                    pretty_print("net0", get_string("node_picker_error")
                                 + f"15s {Style.RESET_ALL}({e})",
                                 "error")
                sleep(15)


class Donate:
    def load(donation_level):
        if donation_level > 0:
            if osname == 'nt':
                if not Path(
                        f"{Settings.DATA_DIR}/Donate.exe").is_file():
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableWindows.exe')
                    r = requests.get(url, timeout=15)
                    with open(f"{Settings.DATA_DIR}/Donate.exe",
                              'wb') as f:
                        f.write(r.content)
            elif osname == "posix":
                if osprocessor() == "aarch64":
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableAARCH64')
                elif osprocessor() == "armv7l":
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableAARCH32')
                else:
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableLinux')
                if not Path(
                        f"{Settings.DATA_DIR}/Donate").is_file():
                    r = requests.get(url, timeout=15)
                    with open(f"{Settings.DATA_DIR}/Donate",
                              "wb") as f:
                        f.write(r.content)

    def start(donation_level):
        donation_settings = requests.get(
            "https://server.duinocoin.com/donations/settings.json").json()

        if os.name == 'nt':
            cmd = (f'cd "{Settings.DATA_DIR}" & Donate.exe '
                   + f'-o {donation_settings["url"]} '
                   + f'-u {donation_settings["user"]} '
                   + f'-p {donation_settings["pwd"]} '
                   + f'-s 4 -e {donation_level*2}')
        elif os.name == 'posix':
            cmd = (f'cd "{Settings.DATA_DIR}" && chmod +x Donate '
                   + '&& nice -20 ./Donate '
                   + f'-o {donation_settings["url"]} '
                   + f'-u {donation_settings["user"]} '
                   + f'-p {donation_settings["pwd"]} '
                   + f'-s 4 -e {donation_level*2}')

        if donation_level <= 0:
            pretty_print(
                'sys0', Fore.YELLOW
                + get_string('free_network_warning').lstrip()
                + get_string('donate_warning').replace("\n", "\n\t\t")
                + Fore.GREEN + 'https://duinocoin.com/donate'
                + Fore.YELLOW + get_string('learn_more_donate'),
                'warning')
            sleep(5)

        if donation_level > 0:
            debug_output(get_string('starting_donation'))
            donateExecutable = Popen(cmd, shell=True, stderr=DEVNULL)
            pretty_print('sys0',
                         get_string('thanks_donation').replace("\n", "\n\t\t"),
                         'error')


shares = [0, 0, 0]
hashrate_mean = []
ping_mean = []
diff = 0
donator_running = False
job = ''
debug = 'n'
discord_presence = 'y'
rig_identifier = 'None'
donation_level = 0
hashrate = 0
config = ConfigParser()
mining_start_time = time()

if not path.exists(Settings.DATA_DIR):
    mkdir(Settings.DATA_DIR)

if not Path(Settings.DATA_DIR + '/Translations.json').is_file():
    url = ('https://raw.githubusercontent.com/'
           + 'revoxhere/'
           + 'duino-coin/master/Resources/'
           + 'AVR_Miner_langs.json')
    r = requests.get(url, timeout=5)
    with open(Settings.DATA_DIR + '/Translations.json', 'wb') as f:
        f.write(r.content)

# Load language file
with open(Settings.DATA_DIR + '/Translations.json', 'r',
          encoding='utf8') as lang_file:
    lang_file = jsonload(lang_file)

# OS X invalid locale hack
if system() == 'Darwin':
    if getlocale()[0] is None:
        setlocale(LC_ALL, 'en_US.UTF-8')

try:
    if not Path(Settings.DATA_DIR + '/Settings.cfg').is_file():
        locale = getdefaultlocale()[0]
        if locale.startswith('es'):
            lang = 'spanish'
        elif locale.startswith('sk'):
            lang = 'slovak'
        elif locale.startswith('ru'):
            lang = 'russian'
        elif locale.startswith('pl'):
            lang = 'polish'
        elif locale.startswith('de'):
            lang = 'german'
        elif locale.startswith('fr'):
            lang = 'french'
        elif locale.startswith('jp'):
            lang = 'japanese'
        elif locale.startswith('tr'):
            lang = 'turkish'
        elif locale.startswith('it'):
            lang = 'italian'
        elif locale.startswith('pt'):
            lang = 'portuguese'
        elif locale.startswith('zh'):
            lang = 'chinese_simplified'
        elif locale.startswith('th'):
            lang = 'thai'
        elif locale.startswith('az'):
            lang = 'azerbaijani'
        elif locale.startswith('nl'):
            lang = 'dutch'
        elif locale.startswith('ko'):
            lang = 'korean'
        elif locale.startswith("id"):
            lang = "indonesian"
        elif locale.startswith("cz"):
            lang = "czech"
        else:
            lang = 'english'
    else:
        try:
            config.read(Settings.DATA_DIR + '/Settings.cfg')
            lang = config["AVR Miner"]['language']
        except Exception:
            lang = 'english'
except:
    lang = 'english'


def get_string(string_name: str):
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file['english']:
        return lang_file['english'][string_name]
    else:
        return string_name


def get_prefix(symbol: str,
               val: float,
               accuracy: int):
    """
    H/s, 1000 => 1 kH/s
    """
    if val >= 1_000_000_000_000:  # Really?
        val = str(round((val / 1_000_000_000_000), accuracy)) + " T"
    elif val >= 1_000_000_000:
        val = str(round((val / 1_000_000_000), accuracy)) + " G"
    elif val >= 1_000_000:
        val = str(round((val / 1_000_000), accuracy)) + " M"
    elif val >= 1_000:
        val = str(round((val / 1_000))) + " k"
    else:
        if symbol:
            val = str(round(val)) + " "
        else:
            val = str(round(val))
    return val + symbol


def debug_output(text: str):
    if debug == 'y':
        print(Style.RESET_ALL + Fore.WHITE
              + now().strftime(Style.DIM + '%H:%M:%S.%f ')
              + Style.NORMAL + f'DEBUG: {text}')


def title(title: str):
    if osname == 'nt':
        """
        Changing the title in Windows' cmd
        is easy - just use the built-in
        title command
        """
        ossystem('title ' + title)
    else:
        """
        Most *nix terminals use
        this escape sequence to change
        the console window title
        """
        try:
            print('\33]0;' + title + '\a', end='')
            sys.stdout.flush()
        except Exception as e:
            print(e)


def handler(signal_received, frame):
    pretty_print(
        'sys0', get_string('sigint_detected')
        + Style.NORMAL + Fore.RESET
        + get_string('goodbye'), 'warning')

    _exit(0)


# Enable signal handler
signal(SIGINT, handler)


def load_config():
    global username
    global donation_level
    global avrport
    global hashrate_list
    global debug
    global rig_identifier
    global discord_presence
    global SOC_TIMEOUT

    if not Path(str(Settings.DATA_DIR) + '/Settings.cfg').is_file():
        print(
            Style.BRIGHT + get_string('basic_config_tool')
            + Settings.DATA_DIR
            + get_string('edit_config_file_warning'))

        print(
            Style.RESET_ALL + get_string('dont_have_account')
            + Fore.YELLOW + get_string('wallet') + Fore.RESET
            + get_string('register_warning'))

        correct_username = False
        while not correct_username:
            username = input(
                Style.RESET_ALL + Fore.YELLOW
                + get_string('ask_username')
                + Fore.RESET + Style.BRIGHT)
            if not username:
                username = choice(["revox", "Bilaboz"])

            r = requests.get(f"https://server.duinocoin.com/users/{username}", 
                             timeout=Settings.SOC_TIMEOUT).json()
            correct_username = r["success"]
            if not correct_username:
                print(get_string("incorrect_username"))

        mining_key = input(Style.RESET_ALL + Fore.YELLOW
                           + get_string("ask_mining_key")
                           + Fore.RESET + Style.BRIGHT)
        if not mining_key:
            mining_key = "None"
        else:
            mining_key = b64.b64encode(mining_key.encode("utf-8")).decode('utf-8')

        print(Style.RESET_ALL + Fore.YELLOW
              + get_string('ports_message'))
        portlist = serial.tools.list_ports.comports(include_links=True)

        for port in portlist:
            print(Style.RESET_ALL
                  + Style.BRIGHT + Fore.RESET
                  + '  ' + str(port))
        print(Style.RESET_ALL + Fore.YELLOW
              + get_string('ports_notice'))

        port_names = []
        for port in portlist:
            port_names.append(port.device)

        avrport = ''
        while True:
            current_port = input(
                Style.RESET_ALL + Fore.YELLOW
                + get_string('ask_avrport')
                + Fore.RESET + Style.BRIGHT)

            if current_port in port_names:
                avrport += current_port
                confirmation = input(
                    Style.RESET_ALL + Fore.YELLOW
                    + get_string('ask_anotherport')
                    + Fore.RESET + Style.BRIGHT)

                if confirmation == 'y' or confirmation == 'Y':
                    avrport += ','
                else:
                    break
            else:
                print(Style.RESET_ALL + Fore.RED
                      + 'Please enter a valid COM port from the list above')

        rig_identifier = input(
            Style.RESET_ALL + Fore.YELLOW
            + get_string('ask_rig_identifier')
            + Fore.RESET + Style.BRIGHT)
        if rig_identifier == 'y' or rig_identifier == 'Y':
            rig_identifier = input(
                Style.RESET_ALL + Fore.YELLOW
                + get_string('ask_rig_name')
                + Fore.RESET + Style.BRIGHT)
        else:
            rig_identifier = 'None'

        donation_level = '0'
        if osname == 'nt' or osname == 'posix':
            donation_level = input(
                Style.RESET_ALL + Fore.YELLOW
                + get_string('ask_donation_level')
                + Fore.RESET + Style.BRIGHT)

        donation_level = sub(r'\D', '', donation_level)
        if donation_level == '':
            donation_level = 1
        if float(donation_level) > int(5):
            donation_level = 5
        if float(donation_level) < int(0):
            donation_level = 0
        donation_level = int(donation_level)

        config["AVR Miner"] = {
            'username':         username,
            'avrport':          avrport,
            'donate':           donation_level,
            'language':         lang,
            'identifier':       rig_identifier,
            'debug':            'n',
            "soc_timeout":      45,
            "avr_timeout":      10,
            "discord_presence": "y",
            "periodic_report":  60,
            "mining_key":       mining_key}

        with open(str(Settings.DATA_DIR)
                  + '/Settings.cfg', 'w') as configfile:
            config.write(configfile)

        avrport = avrport.split(',')
        print(Style.RESET_ALL + get_string('config_saved'))
        hashrate_list = [0] * len(avrport)

    else:
        config.read(str(Settings.DATA_DIR) + '/Settings.cfg')
        username = config["AVR Miner"]['username']
        avrport = config["AVR Miner"]['avrport']
        avrport = avrport.replace(" ", "").split(',')
        donation_level = int(config["AVR Miner"]['donate'])
        debug = config["AVR Miner"]['debug']
        rig_identifier = config["AVR Miner"]['identifier']
        Settings.SOC_TIMEOUT = int(config["AVR Miner"]["soc_timeout"])
        Settings.AVR_TIMEOUT = float(config["AVR Miner"]["avr_timeout"])
        discord_presence = config["AVR Miner"]["discord_presence"]
        Settings.REPORT_TIME = int(config["AVR Miner"]["periodic_report"])
        hashrate_list = [0] * len(avrport)


def greeting():
    global greeting
    print(Style.RESET_ALL)

    current_hour = strptime(ctime(time())).tm_hour
    if current_hour < 12:
        greeting = get_string('greeting_morning')
    elif current_hour == 12:
        greeting = get_string('greeting_noon')
    elif current_hour > 12 and current_hour < 18:
        greeting = get_string('greeting_afternoon')
    elif current_hour >= 18:
        greeting = get_string('greeting_evening')
    else:
        greeting = get_string('greeting_back')

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Fore.YELLOW
        + Style.BRIGHT + get_string('banner')
        + Style.RESET_ALL + Fore.MAGENTA
        + f' {Settings.VER}' + Fore.RESET
        + ' 2019-2023')

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Style.NORMAL + Fore.MAGENTA
        + 'https://github.com/revoxhere/duino-coin')

    if lang != "english":
        print(
            Style.DIM + Fore.MAGENTA
            + Settings.BLOCK + Style.NORMAL
            + Fore.RESET + lang.capitalize()
            + " translation: " + Fore.MAGENTA
            + get_string("translation_autor"))

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Style.NORMAL
        + Fore.RESET + get_string('avr_on_port')
        + Style.BRIGHT + Fore.YELLOW
        + ' '.join(avrport))

    if osname == 'nt' or osname == 'posix':
        print(
            Style.DIM + Fore.MAGENTA + Settings.BLOCK
            + Style.NORMAL + Fore.RESET
            + get_string('donation_level') + Style.BRIGHT
            + Fore.YELLOW + str(donation_level))

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Style.NORMAL
        + Fore.RESET + get_string('algorithm')
        + Style.BRIGHT + Fore.YELLOW
        + 'DUCO-S1A ⚙ AVR diff')

    if rig_identifier != "None":
        print(
            Style.DIM + Fore.MAGENTA
            + Settings.BLOCK + Style.NORMAL
            + Fore.RESET + get_string('rig_identifier')
            + Style.BRIGHT + Fore.YELLOW + rig_identifier)

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Style.NORMAL
        + Fore.RESET + get_string("using_config")
        + Style.BRIGHT + Fore.YELLOW 
        + str(Settings.DATA_DIR + '/Settings.cfg'))

    print(
        Style.DIM + Fore.MAGENTA
        + Settings.BLOCK + Style.NORMAL
        + Fore.RESET + str(greeting) + ', '
        + Style.BRIGHT + Fore.YELLOW
        + str(username) + '!\n')


def init_rich_presence():
    # Initialize Discord rich presence
    global RPC
    try:
        RPC = Presence(905158274490441808)
        RPC.connect()
        Thread(target=update_rich_presence).start()
    except Exception as e:
        #print("Error launching Discord RPC thread: " + str(e))
        pass


def update_rich_presence():
    startTime = int(time())
    while True:
        try:
            total_hashrate = get_prefix("H/s", sum(hashrate_list), 2)
            RPC.update(details="Hashrate: " + str(total_hashrate),
                       start=mining_start_time,
                       state=str(shares[0]) + "/"
                       + str(shares[0] + shares[1])
                       + " accepted shares",
                       large_image="avrminer",
                       large_text="Duino-Coin, "
                       + "a coin that can be mined with almost everything"
                       + ", including AVR boards",
                       buttons=[{"label": "Visit duinocoin.com",
                                 "url": "https://duinocoin.com"},
                                {"label": "Join the Discord",
                                 "url": "https://discord.gg/k48Ht5y"}])
        except Exception as e:
            print("Error updating Discord RPC thread: " + str(e))

        sleep(15)


def pretty_print(sender: str = "sys0",
                 msg: str = None,
                 state: str = "success"):
    """
    Produces nicely formatted CLI output for messages:
    HH:MM:S |sender| msg
    """
    if sender.startswith("net"):
        bg_color = Back.BLUE
    elif sender.startswith("avr"):
        bg_color = Back.MAGENTA
    else:
        bg_color = Back.GREEN

    if state == "success":
        fg_color = Fore.GREEN
    elif state == "info":
        fg_color = Fore.BLUE
    elif state == "error":
        fg_color = Fore.RED
    else:
        fg_color = Fore.YELLOW

    with thread_lock():
        print(Fore.WHITE + datetime.now().strftime(Style.DIM + "%H:%M:%S ")
              + bg_color + Style.BRIGHT + " " + sender + " "
              + Back.RESET + " " + fg_color + msg.strip())


def share_print(id, type, accept, reject, total_hashrate,
                computetime, diff, ping, reject_cause=None):
    """
    Produces nicely formatted CLI output for shares:
    HH:MM:S |avrN| ⛏ Accepted 0/0 (100%) ∙ 0.0s ∙ 0 kH/s ⚙ diff 0 k ∙ ping 0ms
    """
    try:
        diff = get_prefix("", int(diff), 0)
    except:
        diff = "?"

    try:
        total_hashrate = get_prefix("H/s", total_hashrate, 2)
    except:
        total_hashrate = "? H/s"

    if type == "accept":
        share_str = get_string("accepted")
        fg_color = Fore.GREEN
    elif type == "block":
        share_str = get_string("block_found")
        fg_color = Fore.YELLOW
    else:
        share_str = get_string("rejected")
        if reject_cause:
            share_str += f"{Style.NORMAL}({reject_cause}) "
        fg_color = Fore.RED

    with thread_lock():
        print(Fore.WHITE + datetime.now().strftime(Style.DIM + "%H:%M:%S ")
              + Fore.WHITE + Style.BRIGHT + Back.MAGENTA + Fore.RESET
              + " avr" + str(id) + " " + Back.RESET
              + fg_color + Settings.PICK + share_str + Fore.RESET
              + str(accept) + "/" + str(accept + reject) + Fore.MAGENTA
              + " (" + str(round(accept / (accept + reject) * 100)) + "%)"
              + Style.NORMAL + Fore.RESET
              + " ∙ " + str("%04.1f" % float(computetime)) + "s"
              + Style.NORMAL + " ∙ " + Fore.BLUE + Style.BRIGHT
              + str(total_hashrate) + Fore.RESET + Style.NORMAL
              + Settings.COG + f" diff {diff} ∙ " + Fore.CYAN
              + f"ping {(int(ping))}ms")


def mine_avr(com, threadid, fastest_pool):
    global hashrate
    start_time = time()
    report_shares = 0
    last_report_share = 0
    while True:
        while True:
            try:
                ser.close()
                pretty_print('sys' + port_num(com),
                             f"No response from the board. Closed port {com}",
                             'success')
                sleep(2)
            except:
                pass
            try:
                ser = Serial(com, baudrate=int(Settings.BAUDRATE),
                             timeout=int(Settings.AVR_TIMEOUT))
                """
                Sleep after opening the port to make
                sure the board resets properly after
                receiving the DTR signal
                """
                sleep(2)
                break
            except Exception as e:
                pretty_print(
                    'sys'
                    + port_num(com),
                    get_string('board_connection_error')
                    + str(com)
                    + get_string('board_connection_error2')
                    + Style.NORMAL
                    + Fore.RESET
                    + f' (avr connection err: {e})',
                    'error')
                sleep(10)

        retry_counter = 0
        while True:
            try:
                if retry_counter > 3:
                    fastest_pool = Client.fetch_pool()
                    retry_counter = 0

                debug_output(f'Connecting to {fastest_pool}')
                s = Client.connect(fastest_pool)
                server_version = Client.recv(s, 6)

                if threadid == 0:
                    if float(server_version) <= float(Settings.VER):
                        pretty_print(
                            'net0', get_string('connected')
                            + Style.NORMAL + Fore.RESET
                            + get_string('connected_server')
                            + str(server_version) + ")",
                            'success')
                    else:
                        pretty_print(
                            'sys0', f' Miner is outdated (v{Settings.VER}) -'
                            + get_string('server_is_on_version')
                            + server_version + Style.NORMAL
                            + Fore.RESET + get_string('update_warning'),
                            'warning')
                        sleep(10)

                    Client.send(s, "MOTD")
                    motd = Client.recv(s, 1024)

                    if "\n" in motd:
                        motd = motd.replace("\n", "\n\t\t")

                    pretty_print("net" + str(threadid),
                                 get_string("motd") + Fore.RESET
                                 + Style.NORMAL + str(motd),
                                 "success")
                break
            except Exception as e:
                pretty_print('net0', get_string('connecting_error')
                             + Style.NORMAL + f' (connection err: {e})',
                             'error')
                retry_counter += 1
                sleep(10)

        pretty_print('sys' + port_num(com),
                     get_string('mining_start') + Style.NORMAL + Fore.RESET
                     + get_string('mining_algorithm') + str(com) + ')',
                     'success')

        # Perform a hash test to assign the starting diff
        prev_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
        exp_hash = "d0beba883d7e8cd119ea2b0e09b78f60f29e0968"
        exp_result = 50
        while True:
            try:
                debug_output(com + ': Sending hash test to the board')
                ser.write(bytes(str(prev_hash
                                    + Settings.SEPARATOR
                                    + exp_hash
                                    + Settings.SEPARATOR
                                    + "10"
                                    + Settings.SEPARATOR),
                                encoding=Settings.ENCODING))
                debug_output(com + ': Reading hash test from the board')
                result = ser.read_until(b'\n').decode().strip().split(',')
                ser.flush()

                if result[0] and result[1]:
                    _ = int(result[0], 2)
                    debug_output(com + f': Result: {result[0]}')
                else:
                    raise Exception("No data received from the board")
                if int(result[0], 2) != exp_result:
                   raise Exception(com + f': Incorrect result received!')

                computetime = round(int(result[1], 2) / 1000000, 5)
                num_res = int(result[0], 2)
                hashrate_test = round(num_res / computetime, 2)
                break
            except Exception as e:
                debug_output(str(e))

        start_diff = "AVR"
        if hashrate_test > 6000:
            start_diff = "ESP8266H"
            
        elif hashrate_test > 4500:
            start_diff = "ESP8266"
            
        elif hashrate_test > 1000:
            start_diff = "DUE"
            
        elif hashrate_test > 500:
            start_diff = "ARM"
            
        elif hashrate_test > 300:
            start_diff = "MEGA"

        pretty_print('sys' + port_num(com), 
                    get_string('hashrate_test') 
                    + get_prefix("H/s", hashrate_test, 2)
                    + Fore.RESET
                    + get_string('hashrate_test_diff') 
                    + start_diff)

        while True:
            try:
                if config["AVR Miner"]["mining_key"] != "None":
                    key = b64.b64decode(config["AVR Miner"]["mining_key"]).decode()
                else:
                    key = config["AVR Miner"]["mining_key"]

                debug_output(com + ': Requesting job')
                Client.send(s, 'JOB'
                            + Settings.SEPARATOR
                            + str(username)
                            + Settings.SEPARATOR
                            + start_diff
                            + Settings.SEPARATOR
                            + str(key)
                )
                job = Client.recv(s, 128).split(Settings.SEPARATOR)
                debug_output(com + f": Received: {job[0]}")

                try:
                    diff = int(job[2])
                except:
                    pretty_print("sys" + port_num(com),
                                 f" Node message: {job[1]}", "warning")
                    sleep(3)
            except Exception as e:
                pretty_print('net' + port_num(com),
                             get_string('connecting_error')
                             + Style.NORMAL + Fore.RESET
                             + f' (err handling result: {e})', 'error')
                sleep(3)
                break

            retry_counter = 0
            while True:
                if retry_counter > 3:
                    break

                try:
                    debug_output(com + ': Sending job to the board')
                    ser.write(bytes(str(job[0]
                                        + Settings.SEPARATOR
                                        + job[1]
                                        + Settings.SEPARATOR
                                        + job[2]
                                        + Settings.SEPARATOR),
                                    encoding=Settings.ENCODING))
                    debug_output(com + ': Reading result from the board')
                    result = ser.read_until(b'\n').decode().strip().split(',')

                    if result[0] and result[1]:
                        _ = int(result[0], 2)
                        debug_output(com + f': Result: {result[0]}')
                        break
                    else:
                        raise Exception("No data received from AVR")
                except Exception as e:
                    debug_output(com + f': Retrying data read: {e}')
                    ser.flush()
                    retry_counter += 1
                    continue

            if retry_counter > 3:
                break

            try:
                computetime = round(int(result[1], 2) / 1000000, 5)
                num_res = int(result[0], 2)
                hashrate_t = round(num_res / computetime, 2)

                hashrate_mean.append(hashrate_t)
                hashrate = mean(hashrate_mean[-5:])
                hashrate_list[threadid] = hashrate
            except Exception as e:
                pretty_print('sys' + port_num(com),
                             get_string('mining_avr_connection_error')
                             + Style.NORMAL + Fore.RESET
                             + ' (no response from the board: '
                             + f'{e}, please check the connection, '
                             + 'port setting or reset the AVR)', 'warning')
                break

            try:
                Client.send(s, str(num_res)
                            + Settings.SEPARATOR
                            + str(hashrate_t)
                            + Settings.SEPARATOR
                            + f'Official AVR Miner {Settings.VER}'
                            + Settings.SEPARATOR
                            + str(rig_identifier)
                            + Settings.SEPARATOR
                            + str(result[2]))

                responsetimetart = now()
                feedback = Client.recv(s, 64).split(",")
                responsetimestop = now()

                time_delta = (responsetimestop -
                              responsetimetart).microseconds
                ping_mean.append(round(time_delta / 1000))
                ping = mean(ping_mean[-10:])
                diff = get_prefix("", int(diff), 0)
                debug_output(com + f': retrieved feedback: {" ".join(feedback)}')
            except Exception as e:
                pretty_print('net' + port_num(com),
                             get_string('connecting_error')
                             + Style.NORMAL + Fore.RESET
                             + f' (err handling result: {e})', 'error')
                debug_output(com + f': error parsing response: {e}')
                sleep(5)
                break

            if feedback[0] == 'GOOD':
                shares[0] += 1
                printlock.acquire()
                share_print(port_num(com), "accept",
                            shares[0], shares[1], hashrate,
                            computetime, diff, ping)
                printlock.release()
            elif feedback[0] == 'BLOCK':
                shares[0] += 1
                shares[2] += 1
                printlock.acquire()
                share_print(port_num(com), "block",
                            shares[0], shares[1], hashrate,
                            computetime, diff, ping)
                printlock.release()
            elif feedback[0] == 'BAD':
                shares[1] += 1
                printlock.acquire()
                share_print(port_num(com), "reject",
                            shares[0], shares[1], hashrate,
                            computetime, diff, ping, feedback[1])
                printlock.release()
            else:
                printlock.acquire()
                share_print(port_num(com), "reject",
                            shares[0], shares[1], hashrate,
                            computetime, diff, ping, feedback)
                printlock.release()

            title(get_string('duco_avr_miner') + str(Settings.VER)
                  + f') - {shares[0]}/{(shares[0] + shares[1])}'
                  + get_string('accepted_shares'))

            end_time = time()
            elapsed_time = end_time - start_time
            if threadid == 0 and elapsed_time >= Settings.REPORT_TIME:
                report_shares = shares[0] - last_report_share
                uptime = calculate_uptime(mining_start_time)

                periodic_report(start_time, end_time, report_shares,
                                shares[2], hashrate, uptime)
                start_time = time()
                last_report_share = shares[0]


def periodic_report(start_time, end_time, shares,
                    block, hashrate, uptime):
    seconds = round(end_time - start_time)
    pretty_print("sys0",
                 " " + get_string('periodic_mining_report')
                 + Fore.RESET + Style.NORMAL
                 + get_string('report_period')
                 + str(seconds) + get_string('report_time')
                 + get_string('report_body1')
                 + str(shares) + get_string('report_body2')
                 + str(round(shares/seconds, 1))
                 + get_string('report_body3')
                 + get_string('report_body7') + str(block)
                 + get_string('report_body4')
                 + str(int(hashrate)) + " H/s" + get_string('report_body5')
                 + str(int(hashrate*seconds)) + get_string('report_body6')
                 + get_string('total_mining_time') + str(uptime), "success")


def calculate_uptime(start_time):
    uptime = time() - start_time
    if uptime >= 7200: # 2 hours, plural
        return str(uptime // 3600) + get_string('uptime_hours')
    elif uptime >= 3600: # 1 hour, not plural
        return str(uptime // 3600) + get_string('uptime_hour')
    elif uptime >= 120: # 2 minutes, plural
        return str(uptime // 60) + get_string('uptime_minutes')
    elif uptime >= 60: # 1 minute, not plural
        return str(uptime // 60) + get_string('uptime_minute')
    else: # less than 1 minute
        return str(round(uptime)) + get_string('uptime_seconds')    


if __name__ == '__main__':
    init(autoreset=True)
    title(f"{get_string('duco_avr_miner')}{str(Settings.VER)})")

    if sys.platform == "win32":
        os.system('') # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607

    check_updates()

    try:
        load_config()
        debug_output('Config file loaded')
    except Exception as e:
        pretty_print(
            'sys0', get_string('load_config_error')
            + Settings.DATA_DIR + get_string('load_config_error_warning')
            + Style.NORMAL + Fore.RESET + f' ({e})', 'error')
        debug_output(f'Error reading configfile: {e}')
        sleep(10)
        _exit(1)

    try:
        greeting()
        debug_output('Greeting displayed')
    except Exception as e:
        debug_output(f'Error displaying greeting message: {e}')

    try:
        check_mining_key(config)
    except Exception as e:
        debug_output(f'Error checking miner key: {e}')

    if donation_level > 0:
        try:
            Donate.load(donation_level)
            Donate.start(donation_level)
        except Exception as e:
            debug_output(f'Error launching donation thread: {e}')

    try:
        fastest_pool = Client.fetch_pool()
        threadid = 0
        for port in avrport:
            Thread(target=mine_avr,
                   args=(port, threadid,
                         fastest_pool)).start()
            threadid += 1
    except Exception as e:
        debug_output(f'Error launching AVR thread(s): {e}')

    if discord_presence == "y":
        try:
            init_rich_presence()
        except Exception as e:
            debug_output(f'Error launching Discord RPC thread: {e}')
