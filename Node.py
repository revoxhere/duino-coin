#!/usr/bin/env python3
##########################################
# Duino-Coin Public Node (v2.5.7)
# This is an early WIP version
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################

from socket import socket
from time import sleep
from hashlib import sha1
from random import randint
from json import dumps
from datetime import datetime
from traceback import format_exc
from signal import SIGINT, signal
from os import _exit, path, mkdir
from pathlib import Path
import configparser
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
from json import load as jsonload
from platform import system as plsystem

try:
    import requests
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") +
          "Requests is not installed. "
          + "Please install it using: python3 -m pip install requests."
          + "\nExiting in 15s.")
    sleep(15)
    _exit(1)

SOCKET_TIMEOUT = 25
AVAILABLE_PORTS = [
    2812,
    2813,
    2814,
    2815,
    2816,
    2817
]
VER = 2.57
RESOURCES_DIR = 'Node_' + str(VER) + '_resources'
config = configparser.ConfigParser()

#makes the resources folder if it didn't yet exist
if not path.exists(RESOURCES_DIR):
            mkdir(RESOURCES_DIR)

# Check if languages file exists, if not, download it
if not Path(RESOURCES_DIR + "/langs.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/dev/Resources/"
           + "Node_langs.json")
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

try:
    if not Path(RESOURCES_DIR + "/Node_config.cfg").is_file():
        # ------ Uncomment these lines inbetween when out of beta and extra languages are added
        #locale = getdefaultlocale()[0]
        #if locale.startswith("nl"):
        #    lang = "dutch"
        #else:
        # ------ Uncomment these lines inbetween when out of beta and extra languages are added
        lang = "english" # Add a [tab] here when the lines above are not commented
    else:
        # Read language variable from configfile
        try:
            config.read(RESOURCES_DIR + "/Node_config.cfg")
            lang = config["NODE"]["language"]
        except Exception:
            # If it fails, fallback to english
            lang = "english"
except Exception as error:
    lang = "english"

def getString(string_name):
    # Get string form language file
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name

try:  # Check if colorama is installed
    from colorama import Fore, Style, init
except:
    now = datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("colorama_not_installed"))
    sleep(15)
    _exit(1)

def get_fastest_connection(server_ip: str):
    connection_pool = []
    connection_pool_2 = []

    pretty_print(getString("searching_fastest_connection"))

    for i in range(len(AVAILABLE_PORTS)):
        try:
            connection_pool.append(socket())
            try:
                connection_pool[i].setblocking(0)
            except BlockingIOError:
                break
            connection_pool[i].connect((server_ip,AVAILABLE_PORTS[i]))
            connection_pool[i].settimeout(15) #reduces timeout when trying pools
            response = connection_pool[i].recv(100).decode()

            if response.startswith('2.'):
                pretty_print(getString("port_responded_1"),AVAILABLE_PORTS[i],getString("port_responded_2"))
                connection_pool[i].close()
                return AVAILABLE_PORTS[i]
        except:
            try:
                connection_pool_2.append(socket())
                connection_pool_2[i].connect((server_ip,AVAILABLE_PORTS[i]))
                connection_pool_2[i].settimeout(15) #reduces timeout when trying pools
                response = connection_pool_2[i].recv(100).decode()

                if response.startswith('2.'):
                    pretty_print(getString("port_responded_1"),AVAILABLE_PORTS[i],getString("port_responded_2"))
                    connection_pool_2[i].close()
                    return AVAILABLE_PORTS[i]
            except:
                pretty_print(getString("connection_timed_out_1"),AVAILABLE_PORTS[i],getString("connection_timed_out_2"))
                continue

class Resp:
    """
    Master node response config
    """
    SEPARATOR = ","
    ENDLINE = "\n"
    ENCODING = "utf-8"


class Font:
    """
    Colorama add-ons
    """
    def time():
        return datetime.now().strftime('%H:%M:%S ') + Style.RESET_ALL

    DIM = Fore.WHITE + Style.DIM
    SEP = "-------- "
    BOLD = Fore.YELLOW + Style.BRIGHT


def send_data(data: str, soc) -> None:
    data_b = bytes(data, encoding=Resp.ENCODING)
    try:
        soc.sendall(data_b)
    except:
        pretty_print(Font.time() + Fore.RED + getString("error_sending_data")
                     + str(format_exc()))


def recv_data(soc, limit=128) -> str:
    try:
        data = soc.recv(limit).decode(Resp.ENCODING)
    except:
        pretty_print(Font.time() + Fore.RED + getString("error_receiving_data_1")
                     + str(format_exc()))

    try:
        return data.rstrip(Resp.ENDLINE)
    except:
        pretty_print(Font.time() + Fore.RED + getString("error_receiving_data_2")
                     + str(format_exc()))


def pretty_print(*message):
    print(*message)

def handler(signal_received, frame):
    # SIGINT handler
    pretty_print(Fore.GREEN + getString("sigint_detected"))
    try:
        # Close previous socket connection (if any)
        socket.close()
    except Exception:
        pass
    _exit(0)

signal(SIGINT, handler)


class Node():
    def __init__(self):
        init(autoreset=True)
        pretty_print(Font.BOLD + Font.SEP + getString("duco_public_node"))
        pretty_print(getString("DOCSTRING"))

        if not Path(RESOURCES_DIR + "/Node_config.cfg").is_file():
            self.USERNAME = input(getString("enter_username"))
            file = open(RESOURCES_DIR + "/Node_config.cfg", "w")
            file.write("[NODE]\nusername = " + self.USERNAME + "\nlanguage = " + lang)
            file.close()
        else:
            config.read(RESOURCES_DIR + "/Node_config.cfg")
            self.USERNAME = config["NODE"]["username"]
            pretty_print(Font.time() + Fore.GREEN + getString("imported_username_1") + self.USERNAME + getString("imported_username_2"))

        self.connect()
        while True:
            self.sync()

    def connect(self):
        NODE_PORT = get_fastest_connection(str("server.duinocoin.com"))
        pretty_print(Font.time() + getString("connecting_master_node"),NODE_PORT)
        self.soc = socket()
        self.soc.connect((str("server.duinocoin.com"), int(NODE_PORT)))
        self.soc.settimeout(SOCKET_TIMEOUT)
        pretty_print(Font.time() + getString("node_on_version"), recv_data(self.soc))

    def sync(self):
        pretty_print(Font.time() + getString("requesting_task"))
        send_data("NODE", self.soc)
        try:
            sync_data = recv_data(self.soc).split(Resp.SEPARATOR)
            task = sync_data[0]

            if task == "CREATE_JOBS":
                pretty_print(Font.time() + Fore.GREEN
                             + getString("task_create_jobs"))
                last_hash = sync_data[1]
                difficulty = int(sync_data[2])
                pretty_print(Font.time() + Fore.GREEN + getString("successful_sync"))
                self.create_jobs(last_hash, difficulty)
            else:
                pretty_print(Font.time() + Fore.YELLOW + getString("no_tasks"))
                sleep(10)
        except:
            pretty_print(Font.time() + Fore.RED + getString("error_while_sync"))
            sleep(10)

    def create_jobs(self,
                    last_hash: str,
                    difficulty: int,
                    amount=10):
        self.created_shares = {}

        pretty_print(Font.time()
                     + getString("create_shares_1")
                     + str(amount)
                     + getString("create_shares_2")
                     + Font.BOLD
                     + last_hash[:6])

        for i in range(amount):
            numeric_result = randint(0, 100 * difficulty)
            expected_hash = sha1(
                bytes(last_hash+str(numeric_result),
                      encoding=Resp.ENCODING)
            ).hexdigest()

            self.created_shares[i] = {
                "lhash": last_hash,
                "ehash": expected_hash,
                "res":   numeric_result
            }
        pretty_print(Font.time() + Fore.GREEN + getString("finished_creating_jobs"))

        self.output_data = {
            "user": self.USERNAME,
            "jobs": self.created_shares
        }

        pretty_print(Font.time() + Fore.GREEN + getString("send_created_jobs"))
        self.send_jobs(self.output_data)

    def send_jobs(self, jobs):
        pretty_print(Font.time() + getString("syncing_jobs"))
        send_data(dumps(jobs), self.soc)

        feedback = recv_data(self.soc)
        if feedback == "OK":
            pretty_print(Font.time() + Fore.GREEN + getString("node_accepted_jobs"))
        else:
            pretty_print(Font.time() + Fore.RED + getString("node_rejected_jobs"))


if __name__ == "__main__":
    Node()
