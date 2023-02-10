#!/usr/bin/env python3
"""
Duino-Coin Official PC Miner 3.4 © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin
Duino-Coin Team & Community 2019-2023
"""

from time import time, sleep, strptime, ctime
from hashlib import sha1
from socket import socket

from multiprocessing import cpu_count, current_process
from multiprocessing import Process, Manager, Semaphore
from threading import Thread
from datetime import datetime
from random import randint

from os import execl, mkdir, _exit
from subprocess import DEVNULL, Popen, check_call, PIPE
import pip
import sys
import base64 as b64
import os
import json
import zipfile
import traceback

from pathlib import Path
from re import sub
from random import choice
from platform import machine as osprocessor
from platform import python_version_tuple
from platform import python_version

from signal import SIGINT, signal
from locale import getdefaultlocale
from configparser import ConfigParser

import io

running_on_rpi = False
configparser = ConfigParser()
printlock = Semaphore(value=1)

# Python <3.5 check
f"Your Python version is too old. Duino-Coin Miner requires version 3.6 or above. Update your packages and try again"


def handler(signal_received, frame):
    """
    Nicely handle CTRL+C exit
    """
    if current_process().name == "MainProcess":
        pretty_print(
            get_string("sigint_detected")
            + Style.NORMAL
            + Fore.RESET
            + get_string("goodbye"),
            "warning")
    
    if not "raspi_leds" in user_settings:
        user_settings["raspi_leds"] = "y"
    
    if running_on_rpi and user_settings["raspi_leds"] == "y":
        # Reset onboard status LEDs
        os.system(
            'echo mmc0 | sudo tee /sys/class/leds/led0/trigger >/dev/null 2>&1')
        os.system(
            'echo 1 | sudo tee /sys/class/leds/led1/brightness >/dev/null 2>&1')

    if sys.platform == "win32":
        _exit(0)
    else: 
        Popen("kill $(ps awux | grep PC_Miner | grep -v grep | awk '{print $2}')",
              shell=True, stdout=PIPE)


def install(package):
    """
    Automatically installs python pip package and restarts the program
    """
    try:
        pip.main(["install",  package])
    except AttributeError:
        check_call([sys.executable, '-m', 'pip', 'install', package])

    execl(sys.executable, sys.executable, *sys.argv)

try:
    import requests
except ModuleNotFoundError:
    print("Requests is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install requests")
    install("requests")

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
    import cpuinfo
except ModuleNotFoundError:
    print("Cpuinfo is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install py-cpuinfo")
    install("py-cpuinfo")

try:    
    import psutil   
except ModuleNotFoundError: 
    print("Psutil is not installed. "   
          + "Miner will try to automatically install it "   
          + "If it fails, please manually execute " 
          + "python3 -m pip install psutil")    
    install("psutil")

try:
    from pypresence import Presence
except ModuleNotFoundError:
    print("Pypresence is not installed. "
          + "Miner will try to automatically install it "
          + "If it fails, please manually execute "
          + "python3 -m pip install pypresence")
    install("pypresence")


class Settings:
    """
    Class containing default miner and server settings
    """
    ENCODING = "UTF8"
    SEPARATOR = ","
    VER = 3.4
    DATA_DIR = "Duino-Coin PC Miner " + str(VER)
    TRANSLATIONS = ("https://raw.githubusercontent.com/"
                    + "revoxhere/"
                    + "duino-coin/master/Resources/"
                    + "PC_Miner_langs.json")
    TRANSLATIONS_FILE = "/Translations.json"
    SETTINGS_FILE = "/Settings.cfg"
    TEMP_FOLDER = "Temp"

    SOC_TIMEOUT = 20
    REPORT_TIME = 5*60
    DONATE_LVL = 0
    RASPI_LEDS = "y"
    RASPI_CPU_IOT = "y"

    try:
        # Raspberry Pi latin encoding users can't display this character
        BLOCK = " ‖ "
        "‖".encode(sys.stdout.encoding)
    except:
        BLOCK = " | "
    PICK = ""
    COG = " @"
    if (os.name != "nt"
        or bool(os.name == "nt"
                and os.environ.get("WT_SESSION"))):
        # Windows' cmd does not support emojis, shame!
        # Same for different encodinsg, for example the latin encoding doesn't support them
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
                pretty_print(get_string("updating"), "warning", "sys0")

                DATA_DIR = "Duino-Coin PC Miner " + str(data["tag_name"]) # Create new version config folder
                if not Path(DATA_DIR).is_dir():
                    mkdir(DATA_DIR)

                try:
                    configparser.read(str(Settings.DATA_DIR) + '/Settings.cfg') # read the previous config

                    configparser["PC Miner"] = {
                        "username":    configparser["PC Miner"]["username"],
                        "mining_key":   configparser["PC Miner"]["mining_key"],
                        "intensity":   configparser["PC Miner"]["intensity"],
                        "threads":     configparser["PC Miner"]["threads"],
                        "start_diff":  configparser["PC Miner"]["start_diff"],
                        "donate":      int(configparser["PC Miner"]["donate"]),
                        "identifier":  configparser["PC Miner"]["identifier"],
                        "algorithm":   configparser["PC Miner"]["algorithm"],
                        "language":    configparser["PC Miner"]["language"],
                        "soc_timeout": int(configparser["PC Miner"]["soc_timeout"]),
                        "report_sec":  int(configparser["PC Miner"]["report_sec"]),
                        "discord_rp":  configparser["PC Miner"]["discord_rp"]
                    }

                    with open(str(DATA_DIR) # save it on the new version folder
                            + '/Settings.cfg', 'w') as configfile:
                        configparser.write(configfile)
                    
                    pretty_print(Style.RESET_ALL + get_string('config_saved'), 
                                 "success", "sys0")
                except Exception as e:
                    pretty_print(f"Error saving configfile: {e}" + str(e), 
                                 "error", "sys0")
                    pretty_print("Config won't be carried to the next version",
                                 "warning", "sys0")

                if not os.path.exists(Settings.TEMP_FOLDER): # Make the Temp folder
                    os.makedirs(Settings.TEMP_FOLDER) 

                file_path = os.path.join(Settings.TEMP_FOLDER, zip_file)
                download_url = "https://github.com/revoxhere/duino-coin/releases/download/" + data["tag_name"] + "/" + zip_file

                if running_script:
                    file_path = os.path.join(".", "PC_Miner_"+data["tag_name"]+".py")
                    download_url = "https://raw.githubusercontent.com/revoxhere/duino-coin/master/PC_Miner.py"
                    
                r = requests.get(download_url, stream=True)
                if r.ok:
                    start = time()
                    dl = 0
                    file_size = int(r.headers["Content-Length"]) # Get file size
                    pretty_print(f"Saving update to: {os.path.abspath(file_path)}",
                                 "warning", "sys0")
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
                    pretty_print("Download complete", "success", "sys0")
                    if not running_script:
                        pretty_print("Unpacking archive", "warning", "sys0")
                        with zipfile.ZipFile(file_path, 'r') as zip_ref: # Unzip the file
                            for file in zip_ref.infolist():
                                if "PC_Miner" in file.filename:
                                    if sys.platform == "win32":
                                        file.filename = "PC_Miner_"+data["tag_name"]+".exe" # Rename the file
                                    else:
                                        file.filename = "PC_Miner_"+data["tag_name"] 
                                    zip_ref.extract(file, ".")
                        pretty_print("Unpacking complete", "success", "sys0")
                        os.remove(file_path) # Delete the zip file
                        os.rmdir(Settings.TEMP_FOLDER) # Delete the temp folder

                        if sys.platform == "win32":
                            os.startfile(os.getcwd() + "\\PC_Miner_"+data["tag_name"]+".exe") # Start the miner
                        else: # os.startfile is only for windows
                            os.system(os.getcwd() + "/PC_Miner_"+data["tag_name"]) 
                    else:
                        if sys.platform == "win32":
                            os.system(file_path)
                        else:
                            os.system("python3 " + file_path)
                    sys.exit() # Exit the program
                else:  # HTTP status code 4XX/5XX
                    pretty_print(f"Update failed: {r.status_code}: {r.text}",
                                 "error", "sys0")
            else:
                pretty_print("Update aborted", "warning", "sys0")
    except Exception as e:
        print(e)


class Algorithms:
    """
    Class containing algorithms used by the miner
    For more info about the implementation refer to the Duino whitepaper:
    https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf
    """
    def DUCOS1(last_h: str, exp_h: str, diff: int, eff: int):
        try:
            import libducohasher
            fasthash_supported = True
        except:
            fasthash_supported = False

        if fasthash_supported:
            time_start = time()

            hasher = libducohasher.DUCOHasher(bytes(last_h, encoding='ascii'))
            nonce = hasher.DUCOS1(
                bytes(bytearray.fromhex(exp_h)), diff, int(eff))

            time_elapsed = time() - time_start
            hashrate = nonce / time_elapsed

            return [nonce, hashrate]
        else:
            time_start = time()
            base_hash = sha1(last_h.encode('ascii'))

            for nonce in range(100 * diff + 1):
                temp_h = base_hash.copy()
                temp_h.update(str(nonce).encode('ascii'))
                d_res = temp_h.hexdigest()

                if eff != 0:
                    if nonce % 5000 == 0:
                        sleep(eff / 100)

                if d_res == exp_h:
                    time_elapsed = time() - time_start
                    hashrate = nonce / time_elapsed

                    return [nonce, hashrate]

            return [0, 0]


class Client:
    """
    Class helping to organize socket connections
    """
    def connect(pool: tuple):
        global s
        s = socket()
        s.settimeout(Settings.SOC_TIMEOUT)
        s.connect((pool))

    def send(msg: str):
        sent = s.sendall(str(msg).encode(Settings.ENCODING))
        return sent

    def recv(limit: int = 128):
        data = s.recv(limit).decode(Settings.ENCODING).rstrip("\n")
        return data

    def fetch_pool(retry_count=1):
        """
        Fetches the best pool from the /getPool API endpoint
        """

        while True:
            if retry_count > 60:
                retry_count = 60

            try:
                pretty_print(get_string("connection_search"),
                             "info", "net0")
                response = requests.get(
                    "https://server.duinocoin.com/getPool",
                    timeout=Settings.SOC_TIMEOUT).json()

                if response["success"] == True:
                    pretty_print(get_string("connecting_node")
                                 + response["name"],
                                 "info", "net0")

                    NODE_ADDRESS = response["ip"]
                    NODE_PORT = response["port"]

                    return (NODE_ADDRESS, NODE_PORT)

                elif "message" in response:
                    pretty_print(f"Warning: {response['message']}")
                    + (f", retrying in {retry_count*2}s",
                    "warning", "net0")

                else:
                    raise Exception("no response - IP ban or connection error")
            except Exception as e:
                if "Expecting value" in str(e):
                    pretty_print(get_string("node_picker_unavailable")
                                 + f"{retry_count*2}s {Style.RESET_ALL}({e})",
                                 "warning", "net0")
                else:
                    pretty_print(get_string("node_picker_error")
                                 + f"{retry_count*2}s {Style.RESET_ALL}({e})",
                                 "error", "net0")
            sleep(retry_count * 2)
            retry_count += 1


class Donate:
    def load(donation_level):
        if donation_level > 0:
            if os.name == 'nt':
                if not Path(
                        f"{Settings.DATA_DIR}/Donate.exe").is_file():
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableWindows.exe')
                    r = requests.get(url, timeout=Settings.SOC_TIMEOUT)
                    with open(f"{Settings.DATA_DIR}/Donate.exe",
                              'wb') as f:
                        f.write(r.content)
                    return
            elif os.name == "posix":
                if osprocessor() == "aarch64":
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableAARCH64')
                elif osprocessor() == "armv7l":
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableAARCH32')
                elif osprocessor() == "x86_64":
                    url = ('https://server.duinocoin.com/'
                           + 'donations/DonateExecutableLinux')
                else:
                    pretty_print(
                        "Donate executable unavailable: "
                        + f"{os.name} {osprocessor()}")
                    return
                if not Path(
                        f"{Settings.DATA_DIR}/Donate").is_file():
                    r = requests.get(url, timeout=Settings.SOC_TIMEOUT)
                    with open(f"{Settings.DATA_DIR}/Donate",
                              "wb") as f:
                        f.write(r.content)
                    return

    def start(donation_level):
        donation_settings = requests.get(
            "https://server.duinocoin.com/donations/settings.json").json()

        if os.name == 'nt':
            cmd = (f'cd "{Settings.DATA_DIR}" & Donate.exe '
                   + f'-o {donation_settings["url"]} '
                   + f'-u {donation_settings["user"]} '
                   + f'-p {donation_settings["pwd"]} '
                   + f'-s 4 -e {donation_level*5}')
        elif os.name == 'posix':
            cmd = (f'cd "{Settings.DATA_DIR}" && chmod +x Donate '
                   + '&& nice -20 ./Donate '
                   + f'-o {donation_settings["url"]} '
                   + f'-u {donation_settings["user"]} '
                   + f'-p {donation_settings["pwd"]} '
                   + f'-s 4 -e {donation_level*5}')

        if donation_level <= 0:
            pretty_print(
                Fore.YELLOW + get_string('free_network_warning').lstrip()
                + get_string('donate_warning').replace("\n", "\n\t\t")
                + Fore.GREEN + 'https://duinocoin.com/donate'
                + Fore.YELLOW + get_string('learn_more_donate'),
                'warning', 'sys0')
            sleep(5)

        if donation_level > 0:
            donateExecutable = Popen(cmd, shell=True, stderr=DEVNULL)
            pretty_print(get_string('thanks_donation').replace("\n", "\n\t\t"),
                         'error', 'sys0')


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
        val = str(round(val)) + " "
    return val + symbol

def get_rpi_temperature():
    output = Popen(args='cat /sys/class/thermal/thermal_zone0/temp',
                    stdout=PIPE,
                    shell=True).communicate()[0].decode()
    return round(int(output) / 1000, 2)


def periodic_report(start_time, end_time, shares,
                    blocks, hashrate, uptime):
    """
    Displays nicely formated uptime stats
    """
    
    raspi_iot_reading = ""
    
    if running_on_rpi and user_settings["raspi_cpu_iot"] == "y":
        raspi_iot_reading = f"{get_string('rpi_cpu_temp')} {get_rpi_temperature()}°C"

    seconds = round(end_time - start_time)
    pretty_print(get_string("periodic_mining_report")
                 + Fore.RESET + Style.NORMAL
                 + get_string("report_period")
                 + str(seconds) + get_string("report_time")
                 + get_string("report_body1")
                 + str(shares) + get_string("report_body2")
                 + str(round(shares/seconds, 1))
                 + get_string("report_body3")
                 + get_string("report_body7")
                 + str(blocks)
                 + get_string("report_body4")
                 + str(get_prefix("H/s", hashrate, 2))
                 + get_string("report_body5")
                 + str(int(hashrate*seconds))
                 + get_string("report_body6")
                 + get_string("total_mining_time")
                 + str(uptime)
                 + raspi_iot_reading, "success")


def calculate_uptime(start_time):
    """
    Returns seconds, minutes or hours passed since timestamp
    """
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


def pretty_print(msg: str = None,
                 state: str = "success",
                 sender: str = "sys0",
                 printlock=printlock):
    """
    Produces nicely formatted CLI output for messages:
    HH:MM:S |sender| msg
    """
    if sender.startswith("net"):
        bg_color = Back.BLUE
    elif sender.startswith("cpu"):
        bg_color = Back.YELLOW
    elif sender.startswith("sys"):
        bg_color = Back.GREEN

    if state == "success":
        fg_color = Fore.GREEN
    elif state == "info":
        fg_color = Fore.BLUE
    elif state == "error":
        fg_color = Fore.RED
    else:
        fg_color = Fore.YELLOW

    with printlock:
        print(Fore.WHITE + datetime.now().strftime(Style.DIM + "%H:%M:%S ")
            + Style.BRIGHT + bg_color + " " + sender + " "
            + Back.RESET + " " + fg_color + msg.strip())


def share_print(id, type,
                accept, reject,
                total_hashrate,
                computetime, diff, ping,
                back_color, reject_cause=None,
                printlock=printlock):
    """
    Produces nicely formatted CLI output for shares:
    HH:MM:S |cpuN| ⛏ Accepted 0/0 (100%) ∙ 0.0s ∙ 0 kH/s ⚙ diff 0 k ∙ ping 0ms
    """
    total_hashrate = get_prefix("H/s", total_hashrate, 2)
    diff = get_prefix("", int(diff), 0)

    def _blink_builtin(led="green"):
        if led == "green":
            os.system(
                'echo 1 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1')
            sleep(0.1)
            os.system(
                'echo 0 | sudo tee /sys/class/leds/led0/brightness >/dev/null 2>&1')
        else:
            os.system(
                'echo 1 | sudo tee /sys/class/leds/led1/brightness >/dev/null 2>&1')
            sleep(0.1)
            os.system(
                'echo 0 | sudo tee /sys/class/leds/led1/brightness >/dev/null 2>&1')
    
    if type == "accept":
        if running_on_rpi and user_settings["raspi_leds"] == "y":
            _blink_builtin()
        share_str = get_string("accepted")
        fg_color = Fore.GREEN
    elif type == "block":
        if running_on_rpi and user_settings["raspi_leds"] == "y":
            _blink_builtin()
        share_str = get_string("block_found")
        fg_color = Fore.YELLOW
    else:
        if running_on_rpi and user_settings["raspi_leds"] == "y":
            _blink_builtin("red")
        share_str = get_string("rejected")
        if reject_cause:
            share_str += f"{Style.NORMAL}({reject_cause}) "
        fg_color = Fore.RED

    with printlock:
        print(Fore.WHITE + datetime.now().strftime(Style.DIM + "%H:%M:%S ")
              + Fore.WHITE + Style.BRIGHT + back_color + Fore.RESET
              + f" cpu{id} " + Back.RESET + fg_color + Settings.PICK
              + share_str + Fore.RESET + f"{accept}/{(accept + reject)}"
              + Fore.YELLOW
              + f" ({(round(accept / (accept + reject) * 100))}%)"
              + Style.NORMAL + Fore.RESET
              + f" ∙ {('%04.1f' % float(computetime))}s"
              + Style.NORMAL + " ∙ " + Fore.BLUE + Style.BRIGHT
              + str(total_hashrate) + Fore.RESET + Style.NORMAL
              + Settings.COG + f" diff {diff} ∙ " + Fore.CYAN
              + f"ping {(int(ping))}ms")


def get_string(string_name):
    """
    Gets a string from the language file
    """
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return string_name


def check_mining_key(user_settings):
    if user_settings["mining_key"] != "None":
        key = '&k=' + b64.b64decode(user_settings["mining_key"]).decode('utf-8')
    else:
        key = ''

    response = requests.get(
        "https://server.duinocoin.com/mining_key"
            + "?u=" + user_settings["username"]
            + key,
        timeout=Settings.SOC_TIMEOUT
    ).json()

    if response["success"] and not response["has_key"]:
        # If user doesn't have a mining key

        user_settings["mining_key"] = "None"

        with open(Settings.DATA_DIR + Settings.SETTINGS_FILE,
            "w") as configfile:
            configparser.write(configfile)
            print(Style.RESET_ALL + get_string("config_saved"))
        sleep(1.5)   
        return

    if not response["success"]:
        if user_settings["mining_key"] == "None":
            pretty_print(get_string("mining_key_required"), "warning")
            mining_key = input("\t\t" + get_string("ask_mining_key")
                               + Style.BRIGHT + Fore.YELLOW)
            if mining_key == "": mining_key = "None" #replace empty input with "None" key
            user_settings["mining_key"] = b64.b64encode(
                mining_key.encode("utf-8")).decode('utf-8')
            configparser["PC Miner"] = user_settings

            with open(Settings.DATA_DIR + Settings.SETTINGS_FILE,
                      "w") as configfile:
                configparser.write(configfile)
                print(Style.RESET_ALL + get_string("config_saved"))
            sleep(1.5)
            check_mining_key(user_settings)
        else:
            pretty_print(get_string("invalid_mining_key"), "error")
            retry = input(get_string("key_retry"))
            if not retry or retry == "y" or retry == "Y":
                mining_key = input(get_string("ask_mining_key"))
                if mining_key == "": mining_key = "None" #replace empty input with "None" key
                user_settings["mining_key"] = b64.b64encode(
                    mining_key.encode("utf-8")).decode('utf-8')
                configparser["PC Miner"] = user_settings

                with open(Settings.DATA_DIR + Settings.SETTINGS_FILE,
                        "w") as configfile:
                    configparser.write(configfile)
                    print(Style.RESET_ALL + get_string("config_saved"))
                sleep(1.5)
                check_mining_key(user_settings)
            else:
                return


class Miner:
    def greeting():
        diff_str = get_string("net_diff_short")
        if user_settings["start_diff"] == "LOW":
            diff_str = get_string("low_diff_short")
        elif user_settings["start_diff"] == "MEDIUM":
            diff_str = get_string("medium_diff_short")

        current_hour = strptime(ctime(time())).tm_hour
        greeting = get_string("greeting_back")
        if current_hour < 12:
            greeting = get_string("greeting_morning")
        elif current_hour == 12:
            greeting = get_string("greeting_noon")
        elif current_hour > 12 and current_hour < 18:
            greeting = get_string("greeting_afternoon")
        elif current_hour >= 18:
            greeting = get_string("greeting_evening")

        print("\n" + Style.DIM + Fore.YELLOW + Settings.BLOCK + Fore.YELLOW
              + Style.BRIGHT + get_string("banner") + Style.RESET_ALL
              + Fore.MAGENTA + " (" + str(Settings.VER) + ") "
              + Fore.RESET + "2019-2023")

        print(Style.DIM + Fore.YELLOW + Settings.BLOCK + Style.NORMAL
              + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")

        if lang != "english":
            print(Style.DIM + Fore.YELLOW + Settings.BLOCK
                  + Style.NORMAL + Fore.RESET
                  + get_string("translation") + Fore.YELLOW
                  + get_string("translation_autor"))

        try:
            print(Style.DIM + Fore.YELLOW + Settings.BLOCK
                  + Style.NORMAL + Fore.RESET + "CPU: " + Style.BRIGHT
                  + Fore.YELLOW + str(user_settings["threads"])
                  + "x " + str(cpu["brand_raw"]))
        except:
            print(Style.DIM + Fore.YELLOW + Settings.BLOCK
                  + Style.NORMAL + Fore.RESET + "CPU: " + Style.BRIGHT
                  + Fore.YELLOW + str(user_settings["threads"])
                  + "x threads")

        if os.name == "nt" or os.name == "posix":
            print(Style.DIM + Fore.YELLOW
                  + Settings.BLOCK + Style.NORMAL + Fore.RESET
                  + get_string("donation_level") + Style.BRIGHT
                  + Fore.YELLOW + str(user_settings["donate"]))

        print(Style.DIM + Fore.YELLOW + Settings.BLOCK
              + Style.NORMAL + Fore.RESET + get_string("algorithm")
              + Style.BRIGHT + Fore.YELLOW + user_settings["algorithm"]
              + Settings.COG + " " + diff_str)

        if user_settings["identifier"] != "None":
            print(Style.DIM + Fore.YELLOW + Settings.BLOCK
                  + Style.NORMAL + Fore.RESET + get_string("rig_identifier")
                  + Style.BRIGHT + Fore.YELLOW + user_settings["identifier"])

        print(Style.DIM + Fore.YELLOW + Settings.BLOCK
              + Style.NORMAL + Fore.RESET + get_string("using_config")
              + Style.BRIGHT + Fore.YELLOW
              + str(Settings.DATA_DIR + Settings.SETTINGS_FILE))

        print(Style.DIM + Fore.YELLOW + Settings.BLOCK
              + Style.NORMAL + Fore.RESET + str(greeting)
              + ", " + Style.BRIGHT + Fore.YELLOW
              + str(user_settings["username"]) + "!\n")

    def preload():
        """
        Creates needed directories and files for the miner
        """
        global lang_file
        global lang

        if not Path(Settings.DATA_DIR).is_dir():
            mkdir(Settings.DATA_DIR)

        if not Path(Settings.DATA_DIR + Settings.TRANSLATIONS_FILE).is_file():
            with open(Settings.DATA_DIR + Settings.TRANSLATIONS_FILE,
                      "wb") as f:
                f.write(requests.get(Settings.TRANSLATIONS,
                                     timeout=Settings.SOC_TIMEOUT).content)

        with open(Settings.DATA_DIR + Settings.TRANSLATIONS_FILE, "r",
                  encoding=Settings.ENCODING) as file:
            lang_file = json.load(file)

        try:
            if not Path(Settings.DATA_DIR + Settings.SETTINGS_FILE).is_file():
                locale = getdefaultlocale()[0]
                if locale.startswith("es"):
                    lang = "spanish"
                elif locale.startswith("pl"):
                    lang = "polish"
                elif locale.startswith("fr"):
                    lang = "french"
                elif locale.startswith("jp"):
                    lang = "japanese"
                elif locale.startswith("fa"):
                    lang = "farsi"
                elif locale.startswith("mt"):
                    lang = "maltese"
                elif locale.startswith("ru"):
                    lang = "russian"
                elif locale.startswith("uk"):
                    lang = "ukrainian"
                elif locale.startswith("de"):
                    lang = "german"
                elif locale.startswith("tr"):
                    lang = "turkish"
                elif locale.startswith("pr"):
                    lang = "portuguese"
                elif locale.startswith("it"):
                    lang = "italian"
                elif locale.startswith("sk"):
                    lang = "slovak"
                elif locale.startswith("zh"):
                    lang = "chinese_simplified"
                elif locale.startswith("th"):
                    lang = "thai"
                elif locale.startswith("ko"):
                    lang = "korean"
                elif locale.startswith("id"):
                    lang = "indonesian"
                elif locale.startswith("cz"):
                    lang = "czech"
                else:
                    lang = "english"
            else:
                try:
                    configparser.read(Settings.DATA_DIR
                                      + Settings.SETTINGS_FILE)
                    lang = configparser["PC Miner"]["language"]
                except Exception:
                    lang = "english"
        except Exception as e:
            print("Error with lang file, falling back to english: " + str(e))
            lang = "english"

    def load_cfg():
        """
        Loads miner settings file or starts the config tool
        """
        if not Path(Settings.DATA_DIR + Settings.SETTINGS_FILE).is_file():
            print(Style.BRIGHT 
                  + get_string("basic_config_tool")
                  + Settings.DATA_DIR
                  + get_string("edit_config_file_warning")
                  + "\n"
                  + Style.RESET_ALL
                  + get_string("dont_have_account")
                  + Fore.YELLOW
                  + get_string("wallet")
                  + Fore.RESET
                  + get_string("register_warning"))

            correct_username = False
            while not correct_username:
                username = input(get_string("ask_username") + Style.BRIGHT)
                if not username:
                    username = choice(["revox", "Bilaboz"])

                r = requests.get(f"https://server.duinocoin.com/users/{username}", 
                             timeout=Settings.SOC_TIMEOUT).json()
                correct_username = r["success"]
                if not correct_username:
                    print(get_string("incorrect_username"))

            mining_key = input(Style.RESET_ALL + get_string("ask_mining_key") + Style.BRIGHT)
            if not mining_key:
                mining_key = "None"
            else:
                mining_key = b64.b64encode(mining_key.encode("utf-8")).decode('utf-8')

            algorithm = "DUCO-S1"

            intensity = sub(r"\D", "",
                            input(Style.NORMAL +
                                  get_string("ask_intensity") +
                                  Style.BRIGHT))

            if not intensity:
                intensity = 95
            elif float(intensity) > 100:
                intensity = 100
            elif float(intensity) < 1:
                intensity = 1

            threads = sub(r"\D", "",
                          input(Style.NORMAL + get_string("ask_threads")
                                + str(cpu_count()) + "): " + Style.BRIGHT))
            if not threads:
                threads = cpu_count()

            if int(threads) > 16:
                threads = 16
                print(Style.BRIGHT + Fore.BLUE 
                        + get_string("max_threads_notice") 
                        + Style.RESET_ALL)
            elif int(threads) < 1:
                threads = 1

            print(Style.BRIGHT
                  + "1" + Style.NORMAL + " - " + get_string("low_diff")
                  + "\n" + Style.BRIGHT
                  + "2" + Style.NORMAL + " - " + get_string("medium_diff")
                  + "\n" + Style.BRIGHT
                  + "3" + Style.NORMAL + " - " + get_string("net_diff"))
            start_diff = sub(r"\D", "",
                             input(Style.NORMAL + get_string("ask_difficulty")
                                   + Style.BRIGHT))
            if start_diff == "1":
                start_diff = "LOW"
            elif start_diff == "3":
                start_diff = "NET"
            else:
                start_diff = "MEDIUM"

            rig_id = input(Style.NORMAL + get_string("ask_rig_identifier")
                           + Style.BRIGHT)
            if rig_id.lower() == "y":
                rig_id = str(input(Style.NORMAL + get_string("ask_rig_name")
                                   + Style.BRIGHT))
            else:
                rig_id = "None"

            donation_level = '0'
            if os.name == 'nt' or os.name == 'posix':
                donation_level = input(Style.NORMAL
                                       + get_string('ask_donation_level')
                                       + Style.BRIGHT)

            donation_level = sub(r'\D', '', donation_level)
            if donation_level == '':
                donation_level = 1
            if float(donation_level) > int(5):
                donation_level = 5
            if float(donation_level) < int(0):
                donation_level = 0

            configparser["PC Miner"] = {
                "username":      username,
                "mining_key":    mining_key,
                "intensity":     intensity,
                "threads":       threads,
                "start_diff":    start_diff,
                "donate":        int(donation_level),
                "identifier":    rig_id,
                "algorithm":     algorithm,
                "language":      lang,
                "soc_timeout":   Settings.SOC_TIMEOUT,
                "report_sec":    Settings.REPORT_TIME,
                "raspi_leds":    Settings.RASPI_LEDS,
                "raspi_cpu_iot": Settings.RASPI_CPU_IOT,
                "discord_rp":    "y"}

            with open(Settings.DATA_DIR + Settings.SETTINGS_FILE,
                      "w") as configfile:
                configparser.write(configfile)
                print(Style.RESET_ALL + get_string("config_saved"))

        configparser.read(Settings.DATA_DIR
                          + Settings.SETTINGS_FILE)
        return configparser["PC Miner"]

    def m_connect(id, pool):
        retry_count = 0
        while True:
            try:
                if retry_count > 3:
                    pool = Client.fetch_pool()
                    retry_count = 0

                socket_connection = Client.connect(pool)
                POOL_VER = Client.recv(5)

                if id == 0:
                    Client.send("MOTD")
                    motd = Client.recv(512).replace("\n", "\n\t\t")

                    pretty_print(get_string("motd") + Fore.RESET + Style.NORMAL
                                 + str(motd), "success", "net" + str(id))

                    if float(POOL_VER) <= Settings.VER:
                        pretty_print(get_string("connected") + Fore.RESET
                                     + Style.NORMAL +
                                     get_string("connected_server")
                                     + str(POOL_VER) + ", " + pool[0] +")",
                                     "success", "net" + str(id))
                    else:
                        pretty_print(get_string("outdated_miner")
                                     + str(Settings.VER) + ") -"
                                     + get_string("server_is_on_version")
                                     + str(POOL_VER) + Style.NORMAL
                                     + Fore.RESET +
                                     get_string("update_warning"),
                                     "warning", "net" + str(id))
                        sleep(5)
                break
            except Exception as e:
                pretty_print(get_string('connecting_error')
                             + Style.NORMAL + f' (connection err: {e})',
                             'error', 'net0')
                retry_count += 1
                sleep(10)

    def mine(id: int, user_settings: list,
             blocks: int, pool: tuple,
             accept: int, reject: int,
             hashrate: list,
             single_miner_id: str,
             printlock):
        """
        Main section that executes the functionalities from the sections above.
        """
        using_algo = get_string("using_algo")
        pretty_print(get_string("mining_thread") + str(id)
                     + get_string("mining_thread_starting")
                     + Style.NORMAL + Fore.RESET + using_algo + Fore.YELLOW
                     + str(user_settings["intensity"])
                     + "% " + get_string("efficiency"),
                     "success", "sys"+str(id))

        last_report = time()
        r_shares, last_shares = 0, 0
        while True:
            try:
                Miner.m_connect(id, pool)
                while True:
                    try:
                        if user_settings["mining_key"] != "None":   
                            key = b64.b64decode(user_settings["mining_key"]).decode('utf-8')    
                        else:   
                            key = user_settings["mining_key"]

                        raspi_iot_reading = ""
                        if user_settings["raspi_cpu_iot"] == "y" and running_on_rpi:
                            # * instead of the degree symbol because nodes use basic encoding
                            raspi_iot_reading = f"CPU temperature:{get_rpi_temperature()}*C"

                        while True:
                            job_req = "JOB"
                            Client.send(job_req
                                        + Settings.SEPARATOR
                                        + str(user_settings["username"])
                                        + Settings.SEPARATOR
                                        + str(user_settings["start_diff"])
                                        + Settings.SEPARATOR
                                        + str(key)
                                        + Settings.SEPARATOR
                                        + str(raspi_iot_reading))

                            job = Client.recv().split(Settings.SEPARATOR)
                            if len(job) == 3:
                                break
                            else:
                                pretty_print(
                                    "Node message: " + str(job[1]),
                                    "warning")
                                sleep(3)

                        while True:
                            time_start = time()
                            back_color = Back.YELLOW

                            eff = 0
                            eff_setting = int(user_settings["intensity"])
                            if 99 > eff_setting >= 90:
                                eff = 0.005
                            elif 90 > eff_setting >= 70:
                                eff = 0.1
                            elif 70 > eff_setting >= 50:
                                eff = 0.8
                            elif 50 > eff_setting >= 30:
                                eff = 1.8
                            elif 30 > eff_setting >= 1:
                                eff = 3

                            result = Algorithms.DUCOS1(
                                job[0], job[1], int(job[2]), eff)
                            computetime = time() - time_start

                            hashrate[id] = result[1]
                            total_hashrate = sum(hashrate.values())
                            prep_identifier = user_settings['identifier']
                            if running_on_rpi:
                                if prep_identifier != "None":
                                    prep_identifier += " - RPi"
                                else:
                                    prep_identifier = "Raspberry Pi"
                                    
                            while True:
                                Client.send(f"{result[0]}"
                                            + Settings.SEPARATOR
                                            + f"{result[1]}"
                                            + Settings.SEPARATOR
                                            + "Official PC Miner"
                                            + f" {Settings.VER}"
                                            + Settings.SEPARATOR
                                            + f"{prep_identifier}"
                                            + Settings.SEPARATOR
                                            + Settings.SEPARATOR
                                            + f"{single_miner_id}")

                                time_start = time()
                                feedback = Client.recv(
                                ).split(Settings.SEPARATOR)
                                ping = (time() - time_start) * 1000

                                if feedback[0] == "GOOD":
                                    accept.value += 1
                                    share_print(id, "accept",
                                                accept.value, reject.value,
                                                total_hashrate,
                                                computetime, job[2], ping,
                                                back_color, printlock)

                                elif feedback[0] == "BLOCK":
                                    accept.value += 1
                                    blocks.value += 1
                                    share_print(id, "block",
                                                accept.value, reject.value,
                                                total_hashrate,
                                                computetime, job[2], ping,
                                                back_color, printlock)

                                elif feedback[0] == "BAD":
                                    reject.value += 1
                                    share_print(id, "reject",
                                                accept.value, reject.value,
                                                total_hashrate,
                                                computetime, job[2], ping,
                                                back_color, feedback[1], printlock)

                                if id == 0:
                                    end_time = time()
                                    elapsed_time = end_time - last_report
                                    if elapsed_time >= int(user_settings["report_sec"]):
                                        r_shares = accept.value - last_shares
                                        uptime = calculate_uptime(
                                            mining_start_time)
                                        periodic_report(last_report, end_time,
                                                        r_shares, blocks.value,
                                                        sum(hashrate.values()),
                                                        uptime)
                                        last_report = time()
                                        last_shares = accept.value
                                break
                            break
                    except Exception as e:
                        print(traceback.format_exc())
                        pretty_print(get_string("error_while_mining")
                                     + " " + str(e), "error", "net" + str(id))
                        sleep(5)
                        break
            except Exception as e:
                print(traceback.format_exc())
                pretty_print(get_string("error_while_mining")
                                     + " " + str(e), "error", "net" + str(id))


class Discord_rp:
    def connect():
        global RPC
        try:
            RPC = Presence(808045598447632384)
            RPC.connect()
            Thread(target=Discord_rp.update).start()
        except Exception as e:
            pretty_print(
                get_string("discord_launch_error") +
                Style.NORMAL + Fore.RESET + " " + str(e),
                "warning")
          

    def update():
        while True:
            try:
                total_hashrate = get_prefix("H/s", sum(hashrate.values()), 2)
                RPC.update(details="Hashrate: " + str(total_hashrate),
                           start=mining_start_time,
                           state=str(accept.value) + "/"
                           + str(reject.value + accept.value)
                           + " accepted shares",
                           large_image="ducol",
                           large_text="Duino-Coin, "
                           + "a coin that can be mined with almost everything"
                           + ", including Arduino boards",
                           buttons=[{"label": "Learn more",
                                     "url": "https://duinocoin.com"},
                                    {"label": "Join the Duino Discord",
                                     "url": "https://discord.gg/k48Ht5y"}])
            except Exception as e:
                pretty_print(
                    get_string("discord_update_error" +
                    Style.NORMAL + Fore.RESET + " " + str(e)),
                    "warning")
            sleep(15)


class Fasthash:
    def init():
        try:
            """
            Check whether libducohash fasthash is available
            to speed up the DUCOS1 work, created by @HGEpro
            """
            import libducohasher
            pretty_print(get_string("fasthash_available"), "info")
        except Exception as e:
            if int(python_version_tuple()[1]) <= 6:
                pretty_print(
                    (f"Your Python version is too old ({python_version()}).\n"
                     + "Fasthash accelerations and other features may not work"
                     + " on your outdated installation.\n"
                     + "We suggest updating your python to version 3.7 or higher."
                     ).replace("\n", "\n\t\t"), 'warning', 'sys0')
            else:
                pretty_print(
                    ("Fasthash accelerations are not available for your OS.\n"
                     + "If you wish to compile them for your system, visit:\n"
                     + "https://github.com/revoxhere/duino-coin/wiki/"
                     + "How-to-compile-fasthash-accelerations\n"
                     + f"(Libducohash couldn't be loaded: {str(e)})"
                     ).replace("\n", "\n\t\t"), 'warning', 'sys0')

    def load():
        if os.name == 'nt':
            if not Path("libducohasher.pyd").is_file():
                pretty_print(get_string("fasthash_download"), "info")
                url = ('https://server.duinocoin.com/'
                       + 'fasthash/libducohashWindows.pyd')
                r = requests.get(url, timeout=Settings.SOC_TIMEOUT)
                with open(f"libducohasher.pyd", 'wb') as f:
                    f.write(r.content)
                return
        elif os.name == "posix":
            if osprocessor() == "aarch64":
                url = ('https://server.duinocoin.com/'
                       + 'fasthash/libducohashPi4.so')
            elif osprocessor() == "armv7l":
                url = ('https://server.duinocoin.com/'
                       + 'fasthash/libducohashPi4_32.so')
            elif osprocessor() == "armv6l":
                url = ('https://server.duinocoin.com/'
                       + 'fasthash/libducohashPiZero.so')
            elif osprocessor() == "x86_64":
                url = ('https://server.duinocoin.com/'
                       + 'fasthash/libducohashLinux.so')
            else:
                pretty_print(
                    ("Fasthash accelerations are not available for your OS.\n"
                     + "If you wish to compile them for your system, visit:\n"
                     + "https://github.com/revoxhere/duino-coin/wiki/"
                     + "How-to-compile-fasthash-accelerations\n"
                     + f"(Invalid processor architecture: {osprocessor()})"
                     ).replace("\n", "\n\t\t"), 'warning', 'sys0')
                return
            if not Path("libducohasher.so").is_file():
                pretty_print(get_string("fasthash_download"), "info")
                r = requests.get(url, timeout=Settings.SOC_TIMEOUT)
                with open("libducohasher.so", "wb") as f:
                    f.write(r.content)
                return
        else:
            pretty_print(
                ("Fasthash accelerations are not available for your OS.\n"
                 + "If you wish to compile them for your system, visit:\n"
                 + "https://github.com/revoxhere/duino-coin/wiki/"
                 + "How-to-compile-fasthash-accelerations\n"
                 + f"(Invalid OS: {os.name})"
                 ).replace("\n", "\n\t\t"), 'warning', 'sys0')
            return


Miner.preload()
p_list = []
mining_start_time = time()

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    signal(SIGINT, handler)

    if sys.platform == "win32":
        os.system('') # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607

    check_updates()

    cpu = cpuinfo.get_cpu_info()
    accept = Manager().Value("i", 0)
    reject = Manager().Value("i", 0)
    blocks = Manager().Value("i", 0)
    hashrate = Manager().dict()

    user_settings = Miner.load_cfg()
    Miner.greeting()

    Fasthash.load()
    Fasthash.init()
    
    if not "raspi_leds" in user_settings:
        user_settings["raspi_leds"] = "y"
    if not "raspi_cpu_iot" in user_settings:
        user_settings["raspi_cpu_iot"] = "y"
    
    if user_settings["raspi_leds"] == "y":
        try:
            with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
                if 'raspberry pi' in m.read().lower():
                    running_on_rpi = True
                    pretty_print(
                        get_string("running_on_rpi") +
                        Style.NORMAL + Fore.RESET + " " +
                        get_string("running_on_rpi2"), "success")
        except:
            running_on_rpi = False

        if running_on_rpi:
            # Prepare onboard LEDs to be controlled
            os.system(
                'echo gpio | sudo tee /sys/class/leds/led1/trigger >/dev/null 2>&1')
            os.system(
                'echo gpio | sudo tee /sys/class/leds/led0/trigger >/dev/null 2>&1')

    if user_settings["raspi_cpu_iot"] == "y" and running_on_rpi:
        try:
            temp = get_rpi_temperature()
            pretty_print(get_string("iot_on_rpi") +
                         Style.NORMAL + Fore.RESET + " " +
                         f"{get_string('iot_on_rpi2')} {temp}°C",
                         "success")
        except Exception as e:
            print(e)
            user_settings["raspi_cpu_iot"] = "n"
    
    try:
        check_mining_key(user_settings)
    except Exception as e:
        print("Error checking mining key:", e)

    Donate.load(int(user_settings["donate"]))
    Donate.start(int(user_settings["donate"]))

    """
    Generate a random number that's used to
    group miners with many threads in the wallet
    """
    single_miner_id = randint(0, 2811)

    threads = int(user_settings["threads"])
    if threads > 16:
        threads = 16
        pretty_print(Style.BRIGHT
                     + get_string("max_threads_notice"))
    if threads > cpu_count():
        pretty_print(Style.BRIGHT
                     + get_string("system_threads_notice"),
                     "warning")
        sleep(10)

    fastest_pool = Client.fetch_pool()

    for i in range(threads):
        p = Process(target=Miner.mine,
                    args=[i, user_settings, blocks,
                          fastest_pool, accept, reject,
                          hashrate, single_miner_id, 
                          printlock])
        p_list.append(p)
        p.start()
        sleep(0.5)

    if user_settings["discord_rp"] == 'y':
        Discord_rp.connect()

    for p in p_list:
        p.join()
