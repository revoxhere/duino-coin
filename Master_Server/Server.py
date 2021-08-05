#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server (v2.6.1)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################

# Import libraries
import threading
import multiprocessing
import socket
import datetime
import configparser
import requests
import os
import psutil
import ssl
import sys
import json
import smtplib
import subprocess
import traceback
import libducohash
from statistics import mean
from random import randint
from hashlib import sha1
from time import time
from sys import exit
from re import sub, match
from sqlite3 import connect as sqlconn
from os import path as ospath
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
from operator import itemgetter
# python3 -m pip install colorama
from colorama import Back, Fore, Style, init
# python3 -m pip install bcrypt
from bcrypt import checkpw, hashpw, gensalt
# python3 -m pip install fastrand
from fastrand import pcg32bounded as fastrandint
# python3 -m pip install gevent
import gevent
from gevent import sleep
from gevent.server import StreamServer
from gevent.pool import Pool
# python3 -m pip install xxhash
from xxhash import xxh64
# python3 -m pip install shutil
from shutil import copyfile
# python3 -m pip install udatetime
import udatetime as utime
import resource

"""
Global variables
"""
HOSTNAME = ""
PORTS = [
    2809,  # Websocket proxy
    2810,  # Pools
    2811,  # General purpose
    2812,  # General purpose
    2813   # General purpose
]
MOTD = """\
You are connected to the Duino-Coin master server.
Have fun!
"""
DIFF_INCREASES_PER = 24000  # net difficulty
DIFF_MULTIPLIER = 1
SAVE_TIME = 10  # in seconds
DB_TIMEOUT = 60
SOCKET_TIMEOUT = 10
BACKLOG = None  # spawn connection instantly
SERVER_VER = 2.6  # announced to clients
READY_HASHES_NUM = 500  # in shares
BLOCK_PROBABILITY = 500000  # 1 in X
BLOCK_PROBABILITY_XXH = 10000  # 1 in X
BLOCK_REWARD = 28.11  # duco
UPDATE_MINERAPI_EVERY = 2  # in shares
EXPECTED_SHARETIME = 15  # in seconds
MAX_REJECTED_SHARES = 5
BCRYPT_ROUNDS = 6
DECIMALS = 10  # max float precision
MAX_WORKERS = 25
PING_SLEEP_TIME = 0.5  # in seconds
MAX_NUMBER_OF_PINGS = 3
TEMP_BAN_TIME = 60  # in seconds

"""
IO files location
"""

CONFIG_BASE_DIR = "config"
DATABASE = CONFIG_BASE_DIR + '/crypto_database.db'
BLOCKCHAIN = CONFIG_BASE_DIR + '/duino_blockchain.db'
CONFIG_TRANSACTIONS = CONFIG_BASE_DIR + "/transactions.db"
CONFIG_BLOCKS = CONFIG_BASE_DIR + "/foundBlocks.db"
CONFIG_MINERAPI = CONFIG_BASE_DIR + "/minerapi.db"
CONFIG_BANS = CONFIG_BASE_DIR + "/banned.txt"
CONFIG_JAIL = CONFIG_BASE_DIR + "/jailed.txt"
CONFIG_WHITELIST = CONFIG_BASE_DIR + "/whitelisted.txt"
CONFIG_WHITELIST_USR = CONFIG_BASE_DIR + "/whitelistedUsernames.txt"
API_JSON_URI = "api.json"

config = configparser.ConfigParser()
try:
    # Read sensitive data from config file
    config.read('config/AdminData.ini')
    DUCO_EMAIL = config["main"]["duco_email"]
    DUCO_PASS = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    PoolPassword = config["main"]["PoolPassword"]
    WRAPPER_KEY = config["main"]["wrapper_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
except Exception as e:
    print("""Please create config/AdminData.ini config file first:
        [main]
        duco_email = ???
        duco_password = ???
        NodeS_Overide = ???
        PoolPassword = ???
        wrapper_private_key = ???
        NodeS_Username = ???
        wrapper_key = ???""", e)
    exit()

global_blocks = 1
duco_prices = {
    "xmg":  0.0065,
    "bch":  0.0065,
    "xrp":  0.0065,
    "dgb":  0.0065,
    "trx":  0.0065,
    "nano": 0.0065,
    "justswap": 0.0065,
    "nodes": 0.0065
}
pregenerated_jobs = {
    "avr": {},
    "due": {},
    "mega": {},
    "arm": {},
    "esp32": {},
    "esp8266": {}
}
global_last_block_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
global_cpu_usage, global_ram_usage = 50, 50
global_connections = 1
minerapi = {}
job_tiers = {}
balances_to_update = {}
disconnect_list = []
banlist = []
whitelisted_usernames = []
whitelisted_ips = []
connections_per_ip = {}
miners_per_user = {}
chip_ids = {}
jail = []
workers = {}
registrations = {}
estimated_profits = {}
last_block = "DUCO-S1"
cached_balances = {}
cached_logins = {}
mpproc = []
lock = threading.Lock()

# Registration email - text version
text = """\
Hi there!
Your e-mail address has been successfully verified
and you are now registered on the Duino-Coin network!
We hope you'll have a great time using Duino-Coin.
If you have any difficulties there are a lot of guides
on our website: https://duinocoin.com/getting-started
You can also join our Discord server:
https://discord.gg/duinocoin to chat, take part in
giveaways, trade and get help from other Duino-Coin users.
Happy mining!
Sincerely, the Duino-Coin Team"""

# Registration email - HTML version
html = """\
<html>
  <body>
    <img src="https://github.com/revoxhere/duino-coin/raw/master/Resources/ducobanner.png?raw=true"
    width="360px" height="auto"><br>
    <h3>Hi there!</h3>
    <h4>Your e-mail address has been successfully verified
    and you are now registered on the Duino-Coin network!</h4>
    <p>We hope you'll have a great time using Duino-Coin.
    <br>If you have any difficulties there are a lot of
    <a href="https://duinocoin.com/getting-started">guides
    on our website</a>.<br>
       You can also join our
       <a href="https://discord.gg/duinocoin">Discord server</a>
       to chat, take part in giveaways, trade and get
       help from other Duino-Coin users.<br><br>
       Happy mining!<br>
       <italic>Sincerely, the Duino-Coin Team</italic>
    </p>
  </body>
</html>
"""

# Ban email - text version
textBan = """\
Hi there!
We have noticed behavior on your account that
does not comply with our terms of service.
As a result, your account has been
permanently banned.
Sincerely, hte Duino-Coin Team"""

# Ban email - HTML version
htmlBan = """\
<html>
  <body>
    <img src="https://github.com/revoxhere/duino-coin/raw/master/Resources/ducobanner.png?raw=true"
    width="360px" height="auto"><br>
    <h3>Hi there!</h3>
    <h4>We have noticed behavior on your account that does not comply with our
    <a href="https://github.com/revoxhere/duino-coin#terms-of-service">
    terms of service
    <p>As a result, your account has been permanently banned.<br>
       <italic>Sincerely, the Duino-Coin Team</italic>
    </p>
  </body>
</html>
"""


def create_backup():
    """
    Creates a backup folder every day
    """
    counter = 0
    while True:
        if not ospath.isdir('backups/'):
            os.mkdir('backups/')

        today = datetime.date.today()
        if not ospath.isdir('backups/'+str(today)+'_0/'):
            while duco_prices["xmg"] <= 0:
                pass
            else:
                with open("charts/prices.txt",
                          "a") as pricesfile:
                    pricesfile.write(
                        "," + str(duco_prices["xmg"]).rstrip("\n"))
                with open("charts/prices_trx.txt",
                          "a") as pricesfile:
                    pricesfile.write(
                        "," + str(duco_prices["trx"]).rstrip("\n"))
                with open("charts/prices_bch.txt",
                          "a") as pricesfile:
                    pricesfile.write(
                        "," + str(duco_prices["bch"]).rstrip("\n"))
                with open("charts/pricesNodeS.txt",
                          "a") as pricesNodeSfile:
                    pricesNodeSfile.write(
                        "," + str(duco_prices["nodes"]).rstrip("\n"))
                with open("charts/pricesJustSwap.txt",
                          "a") as pricesJustSwapfile:
                    pricesJustSwapfile.write(
                        "," + str(duco_prices["justswap"]).rstrip("\n"))

        if not ospath.isdir('backups/'+str(today)+'_'+str(counter)+'/'):
            os.mkdir('backups/'+str(today)+'_'+str(counter))
            copyfile(BLOCKCHAIN,
                     "backups/"+str(today) +
                     '_'+str(counter)+"/"
                     + BLOCKCHAIN.replace(CONFIG_BASE_DIR, ""))
            copyfile(DATABASE,
                     "backups/"+str(today) +
                     '_'+str(counter)+"/"
                     + DATABASE.replace(CONFIG_BASE_DIR, ""))
            copyfile(CONFIG_BLOCKS,
                     "backups/"+str(today) +
                     '_'+str(counter)+"/foundBlocks.db")
            copyfile(CONFIG_TRANSACTIONS,
                     "backups/"+str(today) +
                     '_'+str(counter)+"/transactions.db")
            admin_print("Successfully created backup for " + str(today))

        hours = 1
        counter += 1
        sleep(60*60*hours)


def perm_ban(ip):
    if not ip in whitelisted_ips:
        os.system("sudo iptables -A INPUT -s " +
                  str(ip)+" -j DROP >/dev/null 2>&1")


def unban(ip):
    os.system("sudo iptables -D INPUT -s "+str(ip)+" -j DROP >/dev/null 2>&1")


def temporary_ban(ip):
    if not ip in whitelisted_ips:
        os.system("sudo iptables -A INPUT -s " +
                  str(ip)+" -j DROP >/dev/null 2>&1")
        threading.Timer(TEMP_BAN_TIME, unban, [ip]).start()


def update_job_tiers():
    global job_tiers
    while True:
        job_tiers = {
            "EXTREME": {
                "difficulty": int(1500000 * DIFF_MULTIPLIER),
                "reward": 0,
                "max_hashrate": 999999999
            },
            "XXHASH": {
                "difficulty": int(100000 * DIFF_MULTIPLIER),
                "reward": .0006,
                "max_hashrate": 900000
            },
            "NET": {
                "difficulty": int(global_blocks
                                  / DIFF_INCREASES_PER
                                  * DIFF_MULTIPLIER) + 1,
                "reward": .0015811,
                "max_hashrate": 1000000
            },
            "MEDIUM": {
                "difficulty": int(75000 * DIFF_MULTIPLIER),
                "reward": .0012811,
                "max_hashrate": 500000
            },
            "LOW": {
                "difficulty": int(7500 * DIFF_MULTIPLIER),
                "reward": .0022811,
                "max_hashrate": 250000
            },
            "ESP32": {
                "difficulty": int(1500 * DIFF_MULTIPLIER),
                "reward": .00175,  # 0.00375
                "max_hashrate": 16000
            },
            "ESP8266": {
                "difficulty": int(1000 * DIFF_MULTIPLIER),
                "reward": .00015,  # 0.0045
                "max_hashrate": 13000
            },
            "DUE": {
                "difficulty": int(444 * DIFF_MULTIPLIER),
                "reward": .003,
                "max_hashrate": 6500
            },
            "ARM": {
                "difficulty": int(128 * DIFF_MULTIPLIER),
                "reward": .003,
                "max_hashrate": 1280
            },
            "MEGA": {
                "difficulty": int(16 * DIFF_MULTIPLIER),
                "reward": .004,
                "max_hashrate": 500
            },
            "AVR": {
                "difficulty": int(6 * DIFF_MULTIPLIER),
                "reward": .005,
                "max_hashrate": 225
            }
        }
        sleep(60)


def create_jobs():
    """
    Generate DUCO-S1A jobs for low-power devices
    """
    while True:
        global_last_block_hash_cp = global_last_block_hash
        base_hash = sha1(global_last_block_hash_cp.encode('ascii'))
        temp_hash = None
        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            avr_diff = job_tiers["AVR"]["difficulty"]
            rand = fastrandint(100 * avr_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["avr"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            due_diff = job_tiers["DUE"]["difficulty"]
            rand = fastrandint(100 * due_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["due"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            arm_diff = job_tiers["ARM"]["difficulty"]
            rand = fastrandint(100 * arm_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["arm"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            mega_diff = job_tiers["MEGA"]["difficulty"]
            rand = fastrandint(100 * mega_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["mega"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            esp32_diff = job_tiers["ESP32"]["difficulty"]
            rand = fastrandint(100 * esp32_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["esp32"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            esp8266_diff = job_tiers["ESP8266"]["difficulty"]
            rand = fastrandint(100 * esp8266_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs["esp8266"][i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}
        sleep(60)


def get_pregenerated_job(req_difficulty):
    """
    Get pregenerated job from pregenerated
    difficulty tiers
    Takes:   req_difficulty
    Outputs: job ready to send to client
    """

    if req_difficulty == "AVR":
        # Arduino
        difficulty = job_tiers["AVR"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["avr"]) - 1)
        numeric_result = pregenerated_jobs["avr"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["avr"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["avr"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "DUE":
        # Arduino Due
        difficulty = job_tiers["DUE"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["due"]) - 1)
        numeric_result = pregenerated_jobs["due"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["due"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["due"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "ARM":
        # ARM boards
        difficulty = job_tiers["ARM"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["arm"]) - 1)
        numeric_result = pregenerated_jobs["arm"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["arm"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["arm"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "MEGA":
        # megaAVR boards
        difficulty = job_tiers["MEGA"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["mega"]) - 1)
        numeric_result = pregenerated_jobs["mega"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["mega"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["mega"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "ESP8266":
        # ESP8266
        difficulty = job_tiers["ESP8266"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["esp8266"]) - 1)
        numeric_result = pregenerated_jobs["esp8266"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["esp8266"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["esp8266"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    else:
        # ESP32
        difficulty = job_tiers["ESP32"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs["esp32"]) - 1)
        numeric_result = pregenerated_jobs["esp32"][rand]["numeric_result"]
        expected_hash = pregenerated_jobs["esp32"][rand]["expected_hash"]
        last_block_hash = pregenerated_jobs["esp32"][rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def transaction_queue_handle(queue):
    # Internal db queue
    admin_print("Successfully started database transaction queue")
    while True:
        s = queue.qsize()
        if s > 0:
            #admin_print(str(s) + " to execute!")
            timeStart = time()

            with sqlconn(DATABASE,
                         timeout=DB_TIMEOUT) as datab:
                for i in range(s):
                    try:
                        datab.execute(queue.get())
                        queue.task_done()
                    except Exception as e:
                        print(traceback.format_exc())
                datab.commit()

            timeEnd = time()
            timeElapsed = round(timeEnd - timeStart, 2)
            #admin_print("Internal db commited - " + str(timeElapsed) + "s\n")

            if timeElapsed < 10:
                sleep(10-timeElapsed)
        sleep(1)


def database_updater():
    global balances_to_update
    while True:
        qsize = queue.qsize()
        sleep((qsize*0.01)+1)
        try:
            for user in balances_to_update.copy():
                if user in jail:
                    balances_to_update["giveaways"] = balances_to_update[user]
                    balances_to_update[user] = balances_to_update[user] * -3

                if user in disconnect_list or user in banlist:
                    balances_to_update[user] = 0

                amount_to_update = balances_to_update[user] / 2

                if amount_to_update / 30 > 0.2:
                    amount_to_update = floatmap(
                        amount_to_update / 30, 0.02, 1, 0.0002, 0.0025
                    )

                if amount_to_update > 0:
                    increment_balance(user, amount_to_update)

                balances_to_update.pop(user)
        except Exception:
            admin_print("Error adding user to DB queue: "
                        + str(traceback.format_exc()))


def chain_updater():
    db_err_counter = 0
    while True:
        sleep(60*5)
        try:
            with sqlconn(BLOCKCHAIN,
                         timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute(
                    """UPDATE Server
                    SET blocks = ?""",
                    (global_blocks,))
                datab.execute(
                    """UPDATE Server
                    SET lastBlockHash = ?""",
                    (global_last_block_hash,))
                conn.commit()
        except Exception as e:
            admin_print("Chain database error:", e)


def get_balance(user: str):
    try:
        with sqlconn(DATABASE,
                     timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT *
                        FROM Users
                        WHERE username = ?""",
                (user,))
            try:
                balance = round(datab.fetchone()[3], DECIMALS)
                return balance
            except:
                raise Exception("User doesn't exist")
    except Exception as e:
        # admin_print("Error returning balance: " + str(e))
        raise Exception("User doesn't exist")


def increment_balance(user: str, amount: float):
    try:
        if match(r"^[A-Za-z0-9_-]*$", user):
            sql_str = ("UPDATE Users SET balance = balance + "
                       + str(amount)
                       + " WHERE username = \'"
                       + str(user) + "\'")
            queue.put(sql_str)
    except Exception as e:
        admin_print("Error adding user to the queue: " + str(e))


def create_transaction(sender: str,
                       recipient: str,
                       amount: float,
                       block_hash: str,
                       memo="None"):
    try:
        timestamp = now().strftime("%d/%m/%Y %H:%M:%S")
        with sqlconn(CONFIG_TRANSACTIONS,
                     timeout=DB_TIMEOUT) as datab:
            datab.execute(
                """INSERT INTO Transactions
                (timestamp, username, recipient, amount, hash, memo)
                VALUES(?, ?, ?, ?, ?, ?)""",
                (timestamp,
                    sender,
                    recipient,
                    amount,
                    block_hash,
                    memo))
            datab.commit()
    except Exception as e:
        admin_print("Error saving transaction: " + str(e))


def input_management():
    while True:
        command = input(
            now().strftime(
                Style.DIM
                + Fore.WHITE
                + "%H:%M:%S.%f:")
            + Fore.YELLOW
            + Style.BRIGHT
            + " DUCO Server $ "
            + Style.RESET_ALL
        ).split(" ")

        if command[0] == "help":
            admin_print("""Available commands:
            - help - shows this help menu
            - balance <user> - prints user balance
            - set <user> <number> - sets user balance to number
            - subtract <user> <number> - subtract number from user balance
            - add <user> <number> - add number to user balance
            - clear - clears the console
            - exit - exits DUCO server
            - restart - restarts DUCO server
            - changeusername <user> <newuser> - changes username
            - changpass <user> <newpass> - changes password
            - remove <username> - removes user
            - ban <username> - bans username
            - jail <username> - jails username
            - pass <username> <password> - verify password of user
            """)

        elif command[0] == "jail":
            jail.append(str(command[1]))
            admin_print("Added "+str(command[1]) + " to earnings jail")
            admin_print("Do you want to save the user in jail file?")
            confirm = input("  y/N")
            if confirm == "Y" or confirm == "y":
                with open(CONFIG_JAIL, 'a') as jailfile:
                    jailfile.write(str(command[1]) + "\n")
                    admin_print("Added username to jaillist")

        elif command[0] == "clear":
            os.system('clear')

        elif command[0] == "ban":
            protocol_ban(command[1])

        elif command[0] == "exit":
            admin_print("Are you sure you want to exit DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
                for proc in mpproc:
                    proc.terminate()
                os._exit(0)
            else:
                admin_print("Canceled")

        elif command[0] == "restart":
            admin_print("Are you sure you want to restart DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
                for proc in mpproc:
                    proc.terminate()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                admin_print("Canceled")

        elif command[0] == "remove":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    old_username = str(datab.fetchone()[0])

                admin_print("Remove user "
                            + old_username
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """DELETE FROM Users
                            WHERE username = ?""",
                            (old_username,))
                        conn.commit()
                        admin_print("Removed user " + str(command[1]))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error: " + str(e))

        elif command[0] == "balance":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    balance = str(datab.fetchone()[3])
                    admin_print(command[1] + "'s balance: " + str(balance))
            except Exception:
                admin_print("User doesn't exist")

        elif command[0] == "set":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    balance = str(datab.fetchone()[3])

                admin_print(command[1]
                            + "'s balance is "
                            + str(balance)
                            + ", set it to "
                            + str(float(command[2]))
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(command[2]), command[1]))
                        conn.commit()

                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """SELECT *
                            FROM Users
                            WHERE username = ?""",
                            (command[1],))
                        balance = str(datab.fetchone()[3])
                        admin_print("User balance is now " + str(balance))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error setting balance: " + str(e))

        elif command[0] == "changeusername":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    old_username = str(datab.fetchone()[0])

                admin_print("Change "
                            + command[1]
                            + "'s username to "
                            + str(command[2])
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set username = ?
                            where username = ?""",
                            (str(command[2]), command[1]))
                        conn.commit()
                        admin_print("Changed username to " + str(command[2]))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error: " + str(e))

        elif command[0] == "changepass":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    username = str(datab.fetchone()[0])

                admin_print("Change "
                            + command[1]
                            + "'s password to "
                            + str(command[2])
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    password = hashpw(command[2].encode(
                        'utf-8'), gensalt(rounds=BCRYPT_ROUNDS))
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set password = ?
                            where username = ?""",
                            (password, command[1]))
                        conn.commit()
                        admin_print("Changed password of user " +
                                    str(command[1]))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error: " + str(e))

        elif command[0] == "pass":
            try:
                password = str(command[2]).encode('utf-8')
                username = str(command[1])
                if user_exists(username):
                    try:
                        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                            # User exists, read his password
                            datab = conn.cursor()
                            datab.execute(
                                """SELECT *
                                FROM Users
                                WHERE username = ?""",
                                (str(username),))
                            stored_password = datab.fetchone()[1]
                    except Exception as e:
                        admin_print(
                            "Error getting password of user "
                            + username + ": "
                            + str(e))

                    try:
                        if checkpw(password, stored_password):
                            admin_print("Correct password")
                        else:
                            admin_print("Invalid password")
                    except:
                        if checkpw(password, stored_password.encode('utf-8')):
                            admin_print("Correct password")
                        else:
                            admin_print("Invalid password")
                else:
                    admin_print("This account doesn\'t exist")
            except Exception as e:
                print(e)

        elif command[0] == "changemail":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    username = str(datab.fetchone()[0])

                admin_print("Change "
                            + command[1]
                            + "'s email to "
                            + str(command[2])
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE,
                                 timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set email = ?
                            where username = ?""",
                            (password, command[1]))
                        conn.commit()
                        admin_print("Changed email of user " +
                                    str(command[1]))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error: " + str(e))

        elif command[0] == "subtract":
            try:
                balance = get_balance(command[1])
                admin_print(command[1]
                            + "'s balance is "
                            + str(balance)
                            + ", subtract "
                            + str(float(command[2]))
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    increment_balance(str(command[1]), -float(command[2]))
                    admin_print(
                        "Successfully added balance change to the queue")

                    import random
                    random = random.randint(0, 77777)
                    if random < 37373:
                        global_last_block_hash_cp = sha1(
                            bytes(str(command[0])+str(command[1])+str(random),
                                  encoding='ascii')).hexdigest()
                    else:
                        global_last_block_hash_cp = xxh64(
                            bytes(str(command[0])+str(command[1])+str(random),
                                  encoding='ascii'), seed=2811).hexdigest()

                    create_transaction(command[1],
                                       "coinexchange",
                                       command[2],
                                       global_last_block_hash_cp,
                                       "DUCO Exchange transaction")
                    admin_print("Successfully generated transaction: " +
                                global_last_block_hash_cp)
                else:
                    admin_print("Canceled")
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")

        elif command[0] == "add":
            try:
                balance = get_balance(command[1])
                admin_print(command[1]
                            + "'s balance is "
                            + str(balance)
                            + ", add "
                            + str(float(command[2]))
                            + "?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    increment_balance(str(command[1]), float(command[2]))
                    admin_print(
                        "Successfully added balance change to the queue")

                    import random
                    random = random.randint(0, 77777)
                    if random < 37373:
                        global_last_block_hash_cp = sha1(
                            bytes(str(command[0])+str(command[1])+str(random),
                                  encoding='ascii')).hexdigest()
                    else:
                        global_last_block_hash_cp = xxh64(
                            bytes(str(command[0])+str(command[1])+str(random),
                                  encoding='ascii'), seed=2811).hexdigest()

                    create_transaction("coinexchange",
                                       command[1],
                                       command[2],
                                       global_last_block_hash_cp,
                                       "DUCO Exchange transaction")
                    admin_print("Successfully generated transaction: " +
                                global_last_block_hash_cp)
                else:
                    admin_print("Canceled")
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")


def user_exists(username: str):
    with sqlconn(DATABASE,
                 timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("""SELECT username
            FROM Users
            WHERE
            username = ?""", (username,))
        data = datab.fetchall()
        if len(data) <= 0:
            return False
        else:
            return True


def email_exists(email: str):
    with sqlconn(DATABASE,
                 timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("""SELECT email
            FROM Users
            WHERE
            email = ?""",
                      (email,))
        data = datab.fetchall()
        if len(data) <= 0:
            return False
        else:
            return True


def protocol_ban(username: str):
    with open(CONFIG_BANS, 'a') as bansfile:
        bansfile.write(str(username) + "\n")
        admin_print("Added username to banlist")

    try:
        banlist.append(str(username))
        admin_print("Added username to blocked usernames")
    except Exception as e:
        admin_print(
            "Error adding username to blocked usernames: " + str(e))

    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT *
            FROM Users
            WHERE username = ?""",
                (username,))
            email = str(datab.fetchone()[2])

            message = MIMEMultipart("alternative")
            message["Subject"] = "ToS violation on account " + \
                str(username)
            message["From"] = DUCO_EMAIL
            message["To"] = email

            part1 = MIMEText(textBan, "plain")
            part2 = MIMEText(htmlBan, "html")
            message.attach(part1)
            message.attach(part2)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com",
                                  465, context=context) as smtpserver:
                smtpserver.login(DUCO_EMAIL, DUCO_PASS)
                smtpserver.sendmail(
                    DUCO_EMAIL, email, message.as_string())
            admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))

    try:
        recipient = "giveaways"
        global_last_block_hash_cp = global_last_block_hash
        memo = "Kolka ban"

        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT *
                FROM Users
                WHERE username = ?""",
                (username,))
            balance = float(datab.fetchone()[3])
            amount = balance

        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()

            balance -= float(amount)
            datab.execute(
                """UPDATE Users
                set balance = ?
                where username = ?""",
                (balance, username))

            datab.execute(
                """SELECT *
                FROM Users
                WHERE username = ?""",
                (recipient,))
            recipientbal = float(datab.fetchone()[3])

            recipientbal += float(amount)
            datab.execute(
                """UPDATE Users
                set balance = ?
                where username = ?""",
                (round(float(recipientbal), DECIMALS), recipient))
            conn.commit()

        with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            formatteddatetime = now().strftime("%d/%m/%Y %H:%M:%S")
            datab.execute(
                """INSERT INTO Transactions
                (timestamp, username, recipient, amount, hash, memo)
                VALUES(?, ?, ?, ?, ?, ?)""",
                (formatteddatetime,
                    username,
                    recipient,
                    amount,
                    global_last_block_hash_cp,
                    memo))
            conn.commit()
        admin_print("Transferred balance to giveaways account")
    except Exception as e:
        admin_print("Error transfering balance: " +
                    traceback.format_exc())


def generate_block(username, reward, new_block_hash, connection, xxhash=False):
    if xxhash:
        algo = "XXHASH"
    else:
        algo = "DUCO-S1"
    reward += BLOCK_REWARD
    with sqlconn(CONFIG_BLOCKS,
                 timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        timestamp = now().strftime("%d/%m/%Y %H:%M:%S")
        datab.execute(
            """INSERT INTO
            Blocks(
            timestamp,
            finder,
            amount,
            hash)
            VALUES(?, ?, ?, ?)""",
            (timestamp, username + " (" + algo + ")",
                reward, new_block_hash))
        conn.commit()
    # admin_print(algo + " block found by " + str(username))
    send_data("BLOCK\n", connection)
    return reward


def sleep_by_cpu_usage(upper_limit):
    """ Suspends execution depending on current cpu usage """
    sleeptime = floatmap(global_cpu_usage, 0, 100, 0, upper_limit)
    sleep(sleeptime)


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


def check_workers(ip_workers, usr_workers):
    if max(ip_workers, usr_workers) > MAX_WORKERS:
        return True
    else:
        return False


def create_share(last_block_hash, difficulty, xxhash=False):
    """ Creates and returns a job for DUCO-S1 algo """
    last_block_hash_cp = last_block_hash
    try:
        try:
            numeric_result = fastrandint(100 * difficulty)
        except:
            numeric_result = randint(0, 100 * difficulty)

        expected_hash_str = str(
            str(last_block_hash_cp)
            + str(numeric_result))
        if xxhash:
            expected_hash = xxh64(
                bytes(expected_hash_str, encoding='ascii'), seed=2811
            ).hexdigest()
        else:
            try:
                expected_hash = libducohash.hash(expected_hash_str)
            except:
                expected_hash = sha1(
                    bytes(expected_hash_str, encoding='ascii')
                ).hexdigest()

        job = [last_block_hash_cp, expected_hash, numeric_result]
        return job
    except Exception as e:
        admin_print("Error creating share: " + str(e))


def protocol_mine(data, connection, address, using_xxhash=False):
    """
    DUCO-S1 (-S1A) & XXHASH Mining protocol handler
    Takes:  data (JOB,username,requested_difficulty),
            connection object, minerapi access
    Returns to main thread if non-mining data is submitted
    """

    global global_last_block_hash
    global global_blocks
    global workers
    global minerapi
    global balances_to_update
    global last_block
    global PING_SLEEP_TIME

    ip_addr = address[0].replace("::ffff:", "")
    thread_id = id(gevent.getcurrent())
    accepted_shares, rejected_shares, reward = 0, 0, 0
    thread_miner_api = {}
    is_first_share = True
    override_difficulty = ""

    while True:
        global_last_block_hash_cp = global_last_block_hash
        if is_first_share:
            try:
                username = str(data[1])
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    return thread_id
            except:
                send_data(
                    "BAD,No username supplied\n",
                    connection)
                return thread_id

            if not username:
                send_data(
                    "BAD,This user doesn't exist\n",
                    connection)
                return thread_id
            elif username in banlist:
                if not username in whitelisted_usernames:
                    perm_ban(ip_addr)
                sleep(5)
                return thread_id

            try:
                chip_ids[username] = []
            except:
                pass

            try:
                this_user_miners = max(workers[ip_addr], workers[username])
            except:
                this_user_miners = 1

            if using_xxhash:
                req_difficulty = "XXHASH"
            else:
                try:
                    # Parse starting difficulty from the client
                    req_difficulty = str(data[2])

                    if "JOB" in req_difficulty:
                        # Very bad error correction from esps
                        req_difficulty.rstrip("JOB")

                    if not req_difficulty in job_tiers:
                        req_difficulty = "NET"
                except:
                    req_difficulty = "NET"
        else:
            data = receive_data(connection, limit=64)

            if not data:
                return thread_id

            if override_difficulty != "":
                req_difficulty = override_difficulty
            else:
                req_difficulty = data[2]

                if "JOB" in req_difficulty:
                    # Error correction from some esps
                    req_difficulty.replace("JOB", "")

                if not req_difficulty in job_tiers:
                    req_difficulty = "NET"

        try:
            if (job_tiers[req_difficulty]["difficulty"]
                    <= job_tiers["ESP32"]["difficulty"]):
                job = get_pregenerated_job(req_difficulty)
                difficulty = job[3]

            elif is_first_share:
                if using_xxhash:
                    difficulty = job_tiers["XXHASH"]["difficulty"]
                else:
                    try:
                        difficulty = job_tiers[req_difficulty]["difficulty"]
                    except:
                        difficulty = job_tiers["NET"]["difficulty"]

            else:
                difficulty = kolka_v3(
                    sharetime, EXPECTED_SHARETIME, difficulty)
        except:
            difficulty = job_tiers["NET"]["difficulty"]

        try:
            ip_workers = workers[ip_addr]
        except:
            ip_workers = 1
        try:
            usr_workers = miners_per_user[username]
        except:
            usr_workers = 1

        if check_workers(ip_workers, usr_workers):
            if not username in whitelisted_usernames:
                send_data(
                    "BAD,Too many workers\n",
                    connection)
                if not ip_addr in whitelisted_ips:
                    perm_ban(ip_addr)
                return thread_id

       # if req_difficulty != "AVR":
       #     send_data(
       #         "BAD,Only AVR mining is enabled on the server",
       #         connection)
       #     return thread_id

        if (job_tiers[req_difficulty]["difficulty"]
                > job_tiers["ESP32"]["difficulty"]):
            if using_xxhash:
                job = create_share(
                    global_last_block_hash_cp, difficulty, xxhash=True
                )
            else:
                try:
                    job = libducohash.create_share(
                        global_last_block_hash_cp, str(difficulty)
                    )
                except:
                    job = create_share(
                        global_last_block_hash_cp, difficulty
                    )

        # Sending job
        send_data(job[0] + "," + job[1] + "," + str(difficulty) + "\n",
                  connection)
        job_sent_timestamp = utime.now()
        connection.settimeout(EXPECTED_SHARETIME*4)

        # Receiving the result
        number_of_pings = 0
        time_spent_on_sending = 0
        while number_of_pings < MAX_NUMBER_OF_PINGS:
            result = receive_data(connection)
            if not result:
                return thread_id
            elif result[0] == "JOB":
                send_data(job[0] + "," + job[1] + "," + str(difficulty) + "\n",
                          connection)
                sleep(PING_SLEEP_TIME)
            elif result[0] == 'PING':
                start_sending = utime.now()
                send_data('Pong!', connection)
                time_spent_on_sending += (utime.now() -
                                          start_sending).total_seconds()
                """
                Avoiding dos attacks: check number_of_pings
                to close connection with too many pings
                """
                number_of_pings += 1
                sleep(PING_SLEEP_TIME)
            else:
                break
        difference = utime.now() - job_sent_timestamp
        sharetime = difference.total_seconds()

        connection.settimeout(SOCKET_TIMEOUT)

        if using_xxhash:
            max_hashrate = job_tiers["XXHASH"]["max_hashrate"]
        else:
            max_hashrate = job_tiers[req_difficulty]["max_hashrate"]
        numeric_result = int(job[2])

        # Calculating sharetime respecting sleeptime for ping
        sharetime -= (number_of_pings*PING_SLEEP_TIME)+time_spent_on_sending
        hashrate = int(numeric_result / sharetime)

        try:
            reported_hashrate = round(float(result[1]))
            hashrate_is_estimated = False
        except:
            reported_hashrate = hashrate
            hashrate_is_estimated = True

        wrong_chip_id = False
        if (req_difficulty == "AVR"
            or req_difficulty == "MEGA"
                or req_difficulty == "ARM"):
            try:
                chip_id = str(result[4]).rstrip()
                if not check_id(chip_id):
                    wrong_chip_id = True
            except:
                chip_id = ""
                wrong_chip_id = True

            chip_ids[username].append(chip_id)

        if rejected_shares > MAX_REJECTED_SHARES:
            if not ip_addr in whitelisted_ips:
                temporary_ban(ip_addr)
            sleep(5)
            return thread_id

        if username in banlist:
            if not username in whitelisted_usernames:
                if not ip_addr in whitelisted_ips:
                    perm_ban(ip_addr)
                sleep(5)
                return thread_id

        if (accepted_shares > 0
                and accepted_shares % UPDATE_MINERAPI_EVERY == 0):
            """
            These things don't need to run every share
            """
            if is_first_share:
                try:
                    workers[ip_addr] += 1
                except:
                    workers[ip_addr] += 1
                try:
                    workers[username] += 1
                except:
                    workers[username] = 1

            try:
                # Check miner software for unallowed characters
                miner_name = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[2])
            except:
                miner_name = "Unknown miner"

            try:
                # Check rig identifier for unallowed characters
                rig_identifier = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[3])
            except:
                rig_identifier = "None"

            if abs(reported_hashrate-hashrate) > 20000:
                reported_hashrate = hashrate
                hashrate_is_estimated = True

            thread_miner_api = {
                "User":         str(username),
                "Is estimated": str(hashrate_is_estimated),
                "Sharetime":    sharetime,
                "Accepted":     accepted_shares,
                "Rejected":     rejected_shares,
                "Diff":         difficulty,
                "Software":     str(miner_name),
                "Identifier":   str(rig_identifier),
                "Earnings":     reward
            }

            thread_miner_api["Hashrate"] = reported_hashrate
            thread_miner_api["Hashrate_calc"] = hashrate

            if using_xxhash:
                thread_miner_api["Algorithm"] = "XXHASH"
            else:
                thread_miner_api["Algorithm"] = "DUCO-S1"

            minerapi[thread_id] = thread_miner_api

            global_blocks += UPDATE_MINERAPI_EVERY
            global_last_block_hash = job[1]

        if (hashrate > max_hashrate
                or reported_hashrate > max_hashrate):
            if req_difficulty == "AVR" or req_difficulty == "ARM":
                if (hashrate > max_hashrate*50
                        or reported_hashrate > max_hashrate*50):
                    if not ip_addr in whitelisted_ips:
                        perm_ban(ip_addr)
                    sleep(5)
                    return thread_id

            """
            Kolka V2 hashrate check
            """
            rejected_shares += 1
            accepted_shares -= 1

            if not using_xxhash:
                override_difficulty = kolka_v2(req_difficulty, job_tiers)

            send_data(
                "You have been moved to a higher difficulty tier\n",
                connection)

        elif int(result[0]) == int(numeric_result):
            """
            Correct result received
            """
            accepted_shares += 1

            if using_xxhash:
                if (fastrandint(BLOCK_PROBABILITY_XXH) == 1):
                    reward = generate_block(
                        username, reward, job[1], connection, xxhash=True)
                else:
                    basereward = job_tiers[req_difficulty]["reward"]
                    reward = kolka_v1(hashrate, difficulty, this_user_miners)
                    if wrong_chip_id:
                        reward = reward / 10
                        # TODO
                    send_data("GOOD\n", connection)
            else:
                if (fastrandint(BLOCK_PROBABILITY) == 1):
                    reward = generate_block(
                        username, reward, job[1], connection)
                else:
                    basereward = job_tiers[req_difficulty]["reward"]
                    reward = kolka_v1(hashrate, difficulty, this_user_miners)
                    if wrong_chip_id:
                        reward = reward / 10
                        # TODO
                    send_data("GOOD\n", connection)

            if accepted_shares > UPDATE_MINERAPI_EVERY:
                try:
                    balances_to_update[username] += reward
                except:
                    balances_to_update[username] = reward
        else:
            """
            Incorrect result received
            """
            rejected_shares += 1
            accepted_shares -= 1

            send_data("BAD\n", connection)

        is_first_share = False

    return thread_id


def admin_print(message: str):
    with lock:
        if "Error" in message:
            fg_color = Fore.RED
        elif "Success" in message:
            fg_color = Fore.GREEN
        elif "?" in message:
            fg_color = Fore.CYAN
        else:
            fg_color = Fore.WHITE

        print(now().strftime(
            Style.DIM
            + Fore.WHITE
            + "%H:%M:%S.%f:"),
            Style.BRIGHT
            + fg_color
            + message)


def now():
    return utime.now()


def get_sys_usage():
    global global_cpu_usage
    global global_ram_usage
    global global_connections

    def _get_connections():
        connections = subprocess.run(
            'sudo netstat -anp | grep ESTABLISHED | wc -l',
            stdout=subprocess.PIPE,
            shell=True
        ).stdout.decode().rstrip()
        return int(connections)

    while True:
        global_connections = _get_connections()

        cpu = floatmap(psutil.cpu_percent(), 0, 100, 0, 75)

        # global_cpu_usage.append(cpu)
        global_cpu_usage = cpu
        # global_ram_usage.append(psutil.virtual_memory()[2])
        global_ram_usage = psutil.virtual_memory()[2]

        sleep(SAVE_TIME)


def hashrate_prefix(hashrate: int, accuracy: int):
    """
    Input: hashrate as int
    Output rounded hashrate with scientific prefix as string
    """
    if hashrate >= 900000000:
        prefix = " GH/s"
        hashrate = hashrate / 1000000000
    elif hashrate >= 900000:
        prefix = " MH/s"
        hashrate = hashrate / 1000000
    elif hashrate >= 900:
        prefix = " kH/s"
        hashrate = hashrate / 1000
    else:
        prefix = " H/s"
    return str(round(hashrate, accuracy)) + str(prefix)


def power_prefix(wattage: int, accuracy: int):
    """
    Input: hattage as int
    Output rounded wattage with scientific prefix as string
    """
    if wattage >= 1000000000:
        prefix = " GW"
        wattage = wattage / 1000000000
    elif wattage >= 1000000:
        prefix = " MW"
        wattage = wattage / 1000000
    elif wattage >= 1000:
        prefix = " kW"
        wattage = wattage / 1000
    else:
        prefix = " W"
    return str(round(wattage, accuracy)) + str(prefix)


def count_registered_users():
    """
    Count all registered users and return an int
    """
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT COUNT(username) FROM Users")
            registeredUsers = datab.fetchone()[0]
            return int(registeredUsers)
    except:
        return 0


def count_total_duco():
    """
    Count all DUCO in accounts and return a float
    """
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT SUM(balance) FROM Users")
            total_duco = datab.fetchone()[0]
        return float(total_duco)
    except:
        return 0


def get_richest_users(num):
    """
    Return a list of num richest users
    """
    leaders = []
    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("""SELECT *
            FROM Users
            ORDER BY balance DESC
            LIMIT """ + str(num))
        for row in datab.fetchall():
            leaders.append(
                str(round((float(row[3])), 4)) + " DUCO - " + row[0])
    return(leaders)


def get_balance_list():
    """
    Returns a dictionary of balances of all users
    """
    balances = {}
    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute(
            """SELECT *
            FROM Users
            ORDER BY balance DESC""")
        for row in datab.fetchall():
            if float(row[3]) > 0:
                balances[str(row[0])] = str(float(row[3])) + " DUCO"
            else:
                """
                Stop when rest of the balances are just empty accounts
                """
                break
    return(balances)


def get_transaction_list():
    """
    Returns a dictionary of all transactions
    """
    transactions = {}
    with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Transactions")
        for row in datab.fetchall():
            transactions[str(row[4])] = {
                "Date":      str(row[0].split(" ")[0]),
                "Time":      str(row[0].split(" ")[1]),
                "Sender":    str(row[1]),
                "Recipient": str(row[2]),
                "Amount":    float(row[3]),
                "Hash":      str(row[4]),
                "Memo":      str(row[5])
            }
    return transactions


def get_blocks_list():
    """
    Returns a dictionary with all mined blocks
    """
    blocks = {}
    with sqlconn(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Blocks")
        for row in datab.fetchall():
            blocks[row[3]] = {
                "Date": str(row[0].split(" ")[0]),
                "Time": str(row[0].split(" ")[1]),
                "Finder": str(row[1]),
                "Amount generated": float(row[2])
            }
    return blocks


def create_secondary_api_files():
    while True:
        with open('foundBlocks.json', 'w') as outfile:
            json.dump(
                get_blocks_list(),
                outfile,
                indent=2,
                ensure_ascii=False
            )
        sleep(SAVE_TIME)

        with open('balances.json', 'w') as outfile:
            json.dump(
                get_balance_list(),
                outfile,
                indent=2,
                ensure_ascii=False
            )

        sleep(SAVE_TIME)

        with open('transactions.json', 'w') as outfile:
            json.dump(
                get_transaction_list(),
                outfile,
                indent=2,
                ensure_ascii=False
            )
        sleep(SAVE_TIME)


def create_main_api_file():
    """
    Creates api.json file containing
    information about the server and
    connected miners
    """
    global miners_per_user

    while True:
        sleep(SAVE_TIME)

        total_hashrate, net_wattage = 0, 0
        ducos1_hashrate, xxhash_hashrate = 0, 0
        minerapi_public, miners_per_user = {}, {}
        miner_list = []
        miner_dict = {
            "GPU": 0,
            "CPU": 0,
            "RPi": 0,
            "ESP32": 0,
            "ESP8266": 0,
            "Arduino": 0,
            "Other": 0
        }

        try:
            for miner in minerapi.copy():
                try:
                    # Add miner hashrate to the server hashrate
                    if minerapi[miner]["Algorithm"] == "DUCO-S1":
                        try:
                            ducos1_hashrate += minerapi[miner]["Hashrate_calc"]
                        except:
                            ducos1_hashrate += minerapi[miner]["Hashrate"]
                    else:
                        try:
                            xxhash_hashrate += minerapi[miner]["Hashrate_calc"]
                        except:
                            xxhash_hashrate += minerapi[miner]["Hashrate"]

                    # Calculate power usage
                    software = minerapi[miner]["Software"].upper()
                    identifier = minerapi[miner]["Identifier"].upper()

                    if ("AVR" in software
                        or "I2C" in software
                            or "ARDUINO" in software):
                        # 0,2W for Arduino @ peak 40mA/5V
                        net_wattage += 0.2
                        miner_dict["Arduino"] += 1

                    elif "ESP32" in software:
                        # 1,4W (but 2 cores) for ESP32 @ peak 480mA/3,3V
                        net_wattage += 0.7
                        miner_dict["ESP32"] += 1

                    elif "ESP8266" in software:
                        # 1,3W for ESP8266 @ peak 400mA/3,3V
                        net_wattage += 1.3
                        miner_dict["ESP8266"] += 1

                    elif ("PC" in software
                          or "WEB" in software):
                        if ("RASPBERRY" in identifier
                                or "PI" in identifier):
                            # 3,875 for one Pi4 core - Pi4 max 15,8W
                            net_wattage += 3.875
                            miner_dict["RPi"] += 1

                        else:
                            # ~70W for typical CPU and 8 mining threads
                            # (9W per mining thread)
                            net_wattage += 9
                            miner_dict["CPU"] += 1

                    elif ("OPENCL" in software
                          or "GPU" in software):
                        net_wattage += 50
                        miner_dict["GPU"] += 1

                    else:
                        net_wattage += 5
                        miner_dict["Other"] += 1

                    username = minerapi[miner]["User"]
                    try:
                        miners_per_user[username] += 1
                    except:
                        miners_per_user[username] = 1

                except Exception as e:
                    pass

            net_wattage = power_prefix(float(net_wattage), 2)
            total_hashrate = hashrate_prefix(
                int(xxhash_hashrate + ducos1_hashrate), 4)
            xxhash_hashrate = hashrate_prefix(int(xxhash_hashrate), 1)
            ducos1_hashrate = hashrate_prefix(int(ducos1_hashrate), 1)

            miners_per_user = OrderedDict(
                sorted(
                    miners_per_user.items(),
                    key=itemgetter(1),
                    reverse=True
                )
            )

            kolka_dict = {
                "Jailed": len(jail),
                "Banned": len(banlist)
            }

            server_api = {
                "Duino-Coin Server API": "github.com/revoxhere/duino-coin",
                "Server version":        SERVER_VER,
                "Active connections":    global_connections,
                "Open threads":          threading.activeCount(),
                "Server CPU usage":      round(global_cpu_usage, 1),
                "Server RAM usage":      round(global_ram_usage, 1),
                "Last update":           now().strftime(
                    "%d/%m/%Y %H:%M:%S (UTC)"),
                "Net energy usage":      net_wattage,
                "Pool hashrate":         total_hashrate,
                "DUCO-S1 hashrate":      ducos1_hashrate,
                "XXHASH hashrate":       xxhash_hashrate,
                "Duco price":            duco_prices[max(duco_prices,
                                                         key=duco_prices.get)],
                "Duco price XMG":        duco_prices["xmg"],
                "Duco price BCH":        duco_prices["bch"],
                "Duco price TRX":        duco_prices["trx"],
                "Duco price XRP":        duco_prices["xrp"],
                "Duco price DGB":        duco_prices["dgb"],
                "Duco Node-S price":     duco_prices["nodes"],
                "Duco JustSwap price":   duco_prices["justswap"],
                "Registered users":      count_registered_users(),
                "All-time mined DUCO":   count_total_duco(),
                "Current difficulty":    job_tiers["NET"]["difficulty"],
                "Mined blocks":          global_blocks,
                "Last block hash":       global_last_block_hash[:10],
                "Kolka":                 kolka_dict,
                "Miner distribution":    miner_dict,
                "Top 10 richest miners": get_richest_users(10),
                "Active workers":        miners_per_user
            }

            with open(API_JSON_URI, 'w') as outfile:
                json.dump(
                    server_api,
                    outfile,
                    ensure_ascii=False)

        except Exception:
            admin_print("Error creating main api.json file:"
                        + str(traceback.format_exc()))


def create_minerapi():
    """
    Creates miners.json file
    containing detailed information about
    every miner and also saves them to
    the minerapi database
    """
    global minerapi
    while True:
        sleep(SAVE_TIME)

        memory_datab.execute("DELETE FROM Miners")

        for threadid in minerapi.copy():
            try:
                memory_datab.execute(
                    """INSERT INTO Miners
                    (threadid, username, hashrate,
                    sharetime, accepted, rejected,
                    diff, software, identifier, algorithm)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (threadid,
                     minerapi[threadid]["User"],
                     minerapi[threadid]["Hashrate"],
                     minerapi[threadid]["Sharetime"],
                     minerapi[threadid]["Accepted"],
                     minerapi[threadid]["Rejected"],
                     minerapi[threadid]["Diff"],
                     minerapi[threadid]["Software"],
                     minerapi[threadid]["Identifier"],
                     minerapi[threadid]["Algorithm"]))
            except:
                pass
        memory.commit()

        with sqlconn(CONFIG_MINERAPI) as disk_conn:
            memory.backup(disk_conn)
            disk_conn.commit()


def protocol_login(data, connection):
    """
    Check if user password matches to the one stored
    in the database, returns bool as login state
    """
    username = str(data[1])
    password = str(data[2]).encode('utf-8')

    global cached_logins
    if username in cached_logins:
        if cached_logins[username] == password:
            send_data("OK", connection)
            return True
        else:
            send_data("NO,Invalid password",
                      connection)
            return False

    elif user_exists(username):
        if match(r"^[A-Za-z0-9_-]*$", username):
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    # User exists, read his password
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (str(username),))
                    stored_password = datab.fetchone()[1]
            except Exception as e:
                admin_print("Error loggin-in user " + username + ": " + str(e))
                send_data("NO,Error looking up account: " + str(e),
                          connection)
                return False

            if len(stored_password) == 0:
                send_data("NO,This user doesn\'t exist",
                          connection)
                return False

            elif (password == stored_password
                  or password == DUCO_PASS.encode('utf-8')
                  or password == NodeS_Overide.encode('utf-8')):
                cached_logins[username] = password
                send_data("OK", connection)
                return True

            try:
                if checkpw(password, stored_password):
                    cached_logins[username] = password
                    send_data("OK", connection)
                    return True

                else:
                    send_data("NO,Invalid password",
                              connection)
                    return False
            except:
                if checkpw(password, stored_password.encode('utf-8')):
                    cached_logins[username] = password
                    send_data("OK", connection)
                    return True

                else:
                    send_data("NO,Invalid password",
                              connection)
                    return False
        else:
            send_data("NO,Unallowed characters used",
                      connection)
            return False
    else:
        send_data("NO,This account doesn\'t exist",
                  connection)
        return False


def send_registration_email(username, email):
    message = MIMEMultipart("alternative")
    message["Subject"] = ("Welcome on the Duino-Coin network, "
                          + str(username)
                          + "! "
                          + u"\U0001F44B")
    try:
        message["From"] = DUCO_EMAIL
        message["To"] = email
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(
                DUCO_EMAIL, DUCO_PASS)
            smtp.sendmail(
                DUCO_EMAIL, email, message.as_string())
            # admin_print("Sent registration email to " + email)
            return True
    except Exception as e:
        # admin_print("Error sending registration email:", e)
        return False


def protocol_register(data, connection, address):
    """
    Register a new user, return on error
    """
    username = str(data[1])
    unhashed_pass = str(data[2]).encode('utf-8')
    email = str(data[3]).replace("REGI", "")
    ip = address[0].replace("::ffff:", "")

    """
    Do some basic checks
    """
    if not match(r"^[A-Za-z0-9_-]*$", username):
        send_data(
            "NO,You have used unallowed characters in the username",
            connection)
        return

    if len(username) > 64 or len(unhashed_pass) > 128 or len(email) > 64:
        send_data(
            "NO,Submited data is too long",
            connection)
        return

    if user_exists(username):
        send_data(
            "NO,This username is already registered",
            connection)
        return

    if not "@" in email or not "." in email:
        send_data(
            "NO,You have provided an invalid e-mail address",
            connection)
        return

    if email_exists(email):
        send_data(
            "NO,This e-mail address was already used",
            connection)
        return

    try:
        password = hashpw(unhashed_pass, gensalt(rounds=BCRYPT_ROUNDS))
    except Exception as e:
        send_data(
            "NO,Bcrypt error: " +
            str(e) + ", plase try using a different password",
            connection)
        return

    if send_registration_email(username, email):
        """
        Register a new account if  the registration
        e-mail was sent successfully
        """
        registrations[ip] = 1
        while True:
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """INSERT INTO Users
                        (username, password, email, balance)
                        VALUES(?, ?, ?, ?)""",
                        (username, password, email, .0))
                    conn.commit()
                    break
            except:
                pass
        send_data("OK", connection)
        return
    else:
        send_data("NO,Error sending verification e-mail", connection)
        return


def protocol_send_funds(data, connection, username):
    """
    Transfers funds from one account to another
    """
    try:
        global_last_block_hash_cp = global_last_block_hash
        memo = sub(r'[^A-Za-z0-9 .()-:/!#_+-]+', ' ', str(data[1]))
        recipient = str(data[2])

        try:
            amount = float(data[3])
        except:
            send_data("NO,Incorrect amount", connection)
            return

        if memo == "-" or not memo:
            memo = "None"

        if (not match(r"^[A-Za-z0-9_-]*$", recipient)
                or not match(r"^[A-Za-z0-9_-]*$", username)):
            send_data("NO,Invalid characters in usernames", connection)
            return

        if not user_exists(username):
            send_data("NO,This user doesn't exist", connection)
            return

        if recipient in jail:
            send_data("NO,Can\'t send funds to that user", connection)
            return

        if username in jail:
            send_data("NO,BONK - go to duco jail", connection)
            return

        if str(recipient) == str(username):
            send_data("NO,You\'re sending funds to yourself", connection)
            return

        if not user_exists(recipient):
            send_data("NO,Recipient doesn\'t exist", connection)
            return

        if not user_exists(username):
            send_data("NO,Sender doesn\'t exist", connection)
            return

        balance = get_balance(username)
        recipientbal = get_balance(recipient)

        if not balance or not recipientbal:
            send_data("NO,Incorrect sender or recipient balance", connection)
            return

        if not amount or float(amount) <= 0:
            send_data("NO,Incorrect amount", connection)
            return

        if (float(balance) <= float(amount)):
            send_data("NO,Incorrect amount", connection)
            return

        if float(balance) >= float(amount):
            balance -= float(amount)
            recipientbal += float(amount)

            while True:
                try:
                    with sqlconn(DATABASE,
                                 timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute('PRAGMA journal_mode=wal')
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (balance, username))
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (round(float(recipientbal), DECIMALS), recipient))
                        conn.commit()
                        break
                except:
                    pass

            create_transaction(username,
                               recipient,
                               amount,
                               global_last_block_hash_cp,
                               memo)

            send_data(
                "OK,Successfully transferred funds,"
                + str(global_last_block_hash_cp),
                connection)
        return
    except Exception as e:
        admin_print("Error sending funds from " + username
                    + " to " + recipient + ": " + str(traceback.format_exc()))
        send_data(
            "NO,Internal server error: "
            + str(e),
            connection)
        return


def protocol_get_balance(data, connection, username):
    """
    Sends balance of user to the client
    raises an exception on error,
    uses cached values when needed
    """
    global cached_balances
    try:
        if username in cached_balances:
            last_cache_time = cached_balances[username]["last"]
            if (now() - last_cache_time).total_seconds() <= SAVE_TIME:
                send_data(
                    round(float(cached_balances[username]["bal"]), DECIMALS),
                    connection)
                return
            else:
                balance = get_balance(username)
                send_data(round(float(balance), DECIMALS), connection)

                cached_balances[username] = {
                    "bal": balance,
                    "last": now()
                }
                return
        else:
            balance = get_balance(username)
            send_data(round(float(balance), DECIMALS), connection)

            cached_balances[username] = {
                "bal": balance,
                "last": now()
            }
            return
    except Exception as e:
        send_data("NO,Internal server error: "+str(e), connection)
        return


def protocol_change_pass(data, connection, username):
    """
    Changes password of user
    """
    try:
        old_password = data[1].encode('utf-8')
        new_password = data[2].encode("utf-8")

        new_password_encrypted = hashpw(
            new_password, gensalt(rounds=BCRYPT_ROUNDS))

        try:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""SELECT *
                        FROM Users
                        WHERE username = ?""",
                              (username,))
                old_password_database = datab.fetchone()[1].encode('utf-8')
        except:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""SELECT *
                        FROM Users
                        WHERE username = ?""",
                              (username,))
                old_password_database = datab.fetchone()[1]

        if (checkpw(old_password, old_password_database)
                or old_password == DUCO_PASS.encode('utf-8')):
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""UPDATE Users
                        set password = ?
                        where username = ?""",
                              (new_password_encrypted, username))
                conn.commit()
                admin_print("Changed password of user " + username)
                send_data("OK,Your password has been changed", connection)
        else:
            admin_print("Passwords of user " + username + " don't match")
            send_data("NO,Your old password doesn't match!", connection)
    except Exception as e:
        admin_print("Error changing password: " + str(e))
        send_data("NO,Internal server error: " + str(e), connection)


def get_duco_prices():
    global duco_prices
    while True:
        try:
            """
            Fetch exchange rates from DUCO exchange API
            """
            de_api = requests.get("https://github.com/revoxhere/duco-exchange/"
                                  + "raw/master/api/v1/rates",
                                  data=None).json()["result"]
            exchange_rate_xmg = de_api["xmg"]["sell"]
            exchange_rate_bch = de_api["bch"]["sell"]
            exchange_rate_trx = de_api["trx"]["sell"]
            exchange_rate_xrp = de_api["xrp"]["sell"]
            exchange_rate_dgb = de_api["dgb"]["sell"]
            exchange_rate_nano = de_api["nano"]["sell"]

            """
            Get pairs prices from Coingecko
            """
            while True:
                try:
                    coingecko_api = requests.get(
                        "https://api.coingecko.com/"
                        + "api/v3/simple/price?ids="
                        + "magi,tron,bitcoin-cash,ripple,digibyte,nano"
                        + "&vs_currencies=usd",
                        data=None
                    ).json()
                    break
                except:
                    pass

            """
            Calculate prices from exchange rates
            """
            xmg_usd = float(coingecko_api["magi"]["usd"])
            duco_prices["xmg"] = round(
                xmg_usd * exchange_rate_xmg, 8
            )

            bch_usd = float(coingecko_api["bitcoin-cash"]["usd"])
            duco_prices["bch"] = round(
                bch_usd * exchange_rate_bch, 8
            )

            xrp_usd = float(coingecko_api["ripple"]["usd"])
            duco_prices["xrp"] = round(
                xrp_usd * exchange_rate_xrp, 8
            )

            dgb_usd = float(coingecko_api["digibyte"]["usd"])
            duco_prices["dgb"] = round(
                dgb_usd * exchange_rate_dgb, 8
            )

            trx_usd = float(coingecko_api["tron"]["usd"])
            duco_prices["trx"] = round(
                trx_usd * exchange_rate_trx, 8
            )

            nano_usd = float(coingecko_api["nano"]["usd"])
            duco_prices["nano"] = round(
                nano_usd * exchange_rate_nano, 8
            )

            """
            Gets DUCO price from the Node-S exchange
            """
            try:
                node_api = requests.get(
                    "http://www.node-s.co.za/"
                    + "api/v1/duco/exchange_rate",
                    data=None).json()

                duco_prices["nodes"] = round(
                    float(node_api["value"]), 8
                )
            except:
                duco_prices["nodes"] = 0

            """
            Gets wDUCO price from JustSwap exchange
            """
            try:
                justswap_api = requests.get(
                    "https://apilist.tronscan.org/"
                    + "api/account?address="
                    + "TRAoFeB7n8Tt4nZGTRB8La4UP4i84bsoMh",
                    data=None).json()

                # Converts values back to floats
                trxBal = int(
                    justswap_api["tokens"][0]["balance"]) / 100000
                wducoBal = int(
                    justswap_api["tokens"][-1]["balance"]) / 100000

                # JustSwap pool exchange rate
                exchange_rate = trxBal / wducoBal

                duco_prices["justswap"] = round(
                    float(exchange_rate) * float(trx_usd), 8
                )
            except:
                duco_prices["justswap"] = 0
        except Exception as e:
            admin_print("Error fetching prices: " + str(e))
        sleep(360)


def protocol_get_transactions(data, connection):
    """
    Sends last transactions involving username
    raises an exception on error
    """
    try:
        username = data[1]
        transaction_count = int(data[2])
        transactiondata = {}
        if transaction_count > 15:
            transaction_count = 15
        with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT * FROM Transactions")
            rows = datab.fetchall()

        for row in rows:
            transactiondata[str(row[4])] = {
                "Date":      str(row[0].split(" ")[0]),
                "Time":      str(row[0].split(" ")[1]),
                "Sender":    str(row[1]),
                "Recipient": str(row[2]),
                "Amount":    float(row[3]),
                "Hash":      str(row[4]),
                "Memo":      str(row[5])
            }
        transactiondata = OrderedDict(
            reversed(
                list(transactiondata.items())
            )
        )

        transactionsToReturn = {}
        i = 0
        for transaction in transactiondata:
            if (transactiondata[transaction]["Recipient"] == username
                    or transactiondata[transaction]["Sender"] == username):
                transactionsToReturn[str(i)] = transactiondata[transaction]
                i += 1
                if i >= transaction_count:
                    break

        transactionsToReturnStr = str(transactionsToReturn)
        send_data(transactionsToReturnStr, connection)
    except Exception as e:
        # admin_print("Error getting transactions: " + str(e))
        send_data("NO,Internal server error: " + str(e), connection)
        raise Exception("Error getting transactions")


def protocol_node(data, connection):
    """
    BIG TODO!
    Send sync data containing
    last block hash and difficulty
    that the node will generate jobs for
    """
    global pregenerated_jobs
    thread_id = id(gevent.getcurrent())
    accepted = 0
    try:
        if fastrandint(10) > 3:
            task = "CREATE_JOBS"
            diff_level = "AVR"
            global_last_block_hash_cp = global_last_block_hash

            sync_data = (task
                         + ","
                         + global_last_block_hash_cp
                         + ","
                         + str(job_tiers[diff_level]["difficulty"])
                         + "\n")

            sleep_by_cpu_usage(3)
            send_data(sync_data, connection)
            output = connection.recv(8096).decode()
            sleep_by_cpu_usage(5)

            if output:
                output_js = eval(output)
                username = output_js["user"]
                accepted += 1

                pregenerated_jobs["avr"] = output_js["jobs"]

                thread_miner_api = {
                    "User":         str(username),
                    "Is estimated": str(0),
                    "Sharetime":    0,
                    "Accepted":     accepted,
                    "Rejected":     0,
                    "Diff":         0,
                    "Software":     str("NODE"),
                    "Identifier":   str("Public Duino-Coin node (BETA)")
                }

                thread_miner_api["Hashrate"] = 0
                thread_miner_api["Hashrate_calc"] = 0
                thread_miner_api["Algorithm"] = "NODE"
                minerapi[thread_id] = thread_miner_api

                send_data("OK\n", connection)
                sleep_by_cpu_usage(3)
        else:
            task = "NO_TASK"

            sync_data = (task
                         + ","
                         + ""
                         + ","
                         + str(0)
                         + "\n")
            send_data(sync_data, connection)
            sleep_by_cpu_usage(5)

    except Exception as e:
        print(traceback.format_exc())


def handle(connection, address):
    """
    Handler for every connected client
    """
    global global_blocks
    global global_last_block_hash
    global minerapi
    global balances_to_update
    global global_connections
    global disconnect_list

    logged_in = False

    ip_addr = address[0].replace("::ffff:", "")

    if ip_addr == "127.0.0.1" or ip_addr == "149.91.88.18":
        connection.settimeout(60*10)
    else:
        connection.settimeout(SOCKET_TIMEOUT)

    try:
        """
        Send server version
        """
        send_data(SERVER_VER, connection)

        try:
            connections_per_ip[ip_addr] += 1
        except Exception:
            connections_per_ip[ip_addr] = 1

        while True:
            """
            Wait until client sends data
            """
            data = receive_data(connection)

            if not data:
                break

            if data[0] == "LOGI":
                """
                Client requested authentication
                """
                logged_in = protocol_login(data, connection)
                if logged_in:
                    username = data[1]
                    if username in banlist:
                        if not username in whitelisted_usernames:
                            perm_ban(ip_addr)
                        break
                else:
                    break

            # MINING FUNCTIONS
            elif data[0] == "DISC":
                username = data[1]
                if data[1] == JoyBed_pass:
                    disconnect_list.append(username)
                    send_data(
                        "OK,Added "+str(username)+" to disconnect list",
                        connection)
                else:
                    send_data("NO,Incorred password", connection)

            elif data[0] == "JOB":
                """ 
                Client requested the DUCO-S1 mining protocol,
                it's not our job so we pass him to the
                DUCO-S1 job handler 
                """
                thread_id = protocol_mine(data, connection, address)
                username = data[1]
                #send_data("NO,Update your miner", connection)
                break

            elif data[0] == "JOBXX":
                """ 
                Same situation as above, just use the XXHASH switch 
                """
                thread_id = protocol_mine(
                    data, connection, address, using_xxhash=True)
                username = data[1]
                #send_data("NO,Update your miner", connection)
                break

            # USER FUNCTIONS

            elif data[0] == "BALA":
                """ 
                Client requested balance check 
                """
                if logged_in:
                    protocol_get_balance(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

           # elif data[0] == "NODE":
                """ 
                Client is a node
                """
                # protocol_node(data, connection)

            elif data[0] == "UEXI":
                """ 
                Client requested to check wheter user is registered 
                """
                if user_exists(data[1]):
                    send_data("OK,User is registered", connection)
                else:
                    send_data("NO,User is not registered", connection)

            elif data[0] == "REGI":
                """ 
                Client requested registation 
                """
                protocol_register(data, connection, address)
                break

            elif data[0] == "CHGP":
                """ 
                Client requested password change 
                """
                if logged_in:
                    protocol_change_pass(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "GTXL":
                """ 
                Client requested transaction list 
                """
                protocol_get_transactions(data, connection)

            elif data[0] == "SEND":
                """ 
                Client requested funds transfer 
                """
                if logged_in:
                    protocol_send_funds(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "PING":
                """ 
                Client requested a ping response 
                """
                send_data("Pong!", connection)

            elif data[0] == "MOTD":
                """ 
                Client requested to send him the MOTD 
                """
                send_data(MOTD, connection)

            # WRAPPED DUCO FUNCTIONS by yanis

            elif data[0] == "WRAP":
                if logged_in:
                    admin_print(
                        "Starting wrapping protocol by " + username)
                    try:
                        amount = str(data[1])
                        tron_address = str(data[2])
                    except IndexError:
                        send_data("NO,Not enough data", connection)
                        break
                    else:
                        wrapfeedback = protocol_wrap_wduco(
                            username, tron_address, amount)
                        if wrapfeedback:
                            send_data(wrapfeedback, connection)
                        else:
                            send_data("OK,Nothing returned", connection)
                else:
                    send_data("NO,Not logged in", connection)

            elif data[0] == "UNWRAP":
                if logged_in:
                    if use_wrapper and wrapper_permission:
                        admin_print(
                            "Starting unwraping protocol by " + username)
                        try:
                            amount = str(data[1])
                            tron_address = str(data[2])
                        except IndexError:
                            send_data("NO,Not enough data", connection)
                            break
                        else:
                            unwrapfeedback = protocol_unwrap_wduco(
                                username, tron_address, amount)
                            if unwrapfeedback:
                                send_data(unwrapfeedback, connection)
                            else:
                                send_data("OK,Nothing returned", connection)
                    else:
                        send_data("NO,Wrapper is disabled", connection)
                else:
                    send_data("NO,Not logged in", connection)

            # POOL FUNCTIONS

            elif data[0] == "PoolLogin":
                # print("Pool logging in")
                Pool = PF.Pool(connection=connection)
                Pool.login(data=data)

            elif data[0] == "PoolSync":
                connection.settimeout(90)
                # print("Pool syncing")
                try:
                    blocks_to_add,\
                        poolConnections,\
                        poolWorkers,\
                        rewards,\
                        error = Pool.sync(data)

                    global_blocks += blocks_to_add

                    if rewards:
                        for user in rewards:
                            amount_to_update = rewards[user]
                            if (amount_to_update
                                    and match(r"^[A-Za-z0-9_-]*$", user)):
                                balances_to_update[user] = amount_to_update

                    if poolWorkers:
                        for threadid in minerapi.copy():
                            if len(str(threadid)) < 11:
                                del minerapi[threadid]

                        for worker in poolWorkers.copy():
                            try:
                                minerapi[worker] = poolWorkers[worker]
                            except Exception as e:
                                print(e)
                except Exception:
                    print(traceback.format_exc())

            elif data[0] == "PoolLogout":
                Pool = PF.Pool(connection=connection)
                Pool.logout(data=data)

            elif data[0] == "PoolLoginAdd":
                PF.pool_login_add(connection=connection,
                                  data=data,
                                  PoolPassword=PoolPassword)

            elif data[0] == "PoolLoginRemove":
                PF.pool_login_remove(connection=connection,
                                     data=data,
                                     PoolPassword=PoolPassword)
            else:
                break

    except Exception:
        pass
        # print(traceback.format_exc())
    finally:
        # print("Closing socket")
        try:
            del minerapi[thread_id]
        except:
            pass

        try:
            connections_per_ip[ip_addr] -= 1
            if connections_per_ip[ip_addr] <= 0:
                del connections_per_ip[ip_addr]
        except:
            pass

        try:
            workers[ip_addr] -= 1
            if workers[ip_addr] <= 0:
                del workers[ip_addr]
        except:
            pass

        connection.close()

        return


def countips():
    """ 
    Check if address is making more than
    n connections in a peroid of n seconds,
    if so - ban the IP
    """
    while True:
        for ip in connections_per_ip.copy():
            try:
                if (connections_per_ip[ip] > 50
                        and not ip in whitelisted_ips):
                    temporary_ban(ip)
            except:
                pass
        sleep(5)


def resetips():
    """ 
    Reset connections per address values every n sec 
    """
    while True:
        sleep(30)
        connections_per_ip.clear()


def duino_stats_restart_handle():
    while True:
        if ospath.isfile("config/restart_signal"):
            os.remove("config/restart_signal")
            admin_print("Server restarted by Duino-Stats command")
            # os.system('sudo iptables -F INPUT')
            os.execl(sys.executable, sys.executable, *sys.argv)
        sleep(3)


def create_databases():
    global global_last_block_hash
    global global_blocks
    global memory_datab
    global memory

    """ 
    In-memory db for minerapi,
    later gets dumped to json and db files -
    check create_minerapi and protocol_mine
    """
    memory = sqlconn(":memory:",
                     check_same_thread=False)
    memory_datab = memory.cursor()

    memory_datab.execute(
        """CREATE TABLE
        IF NOT EXISTS
        Miners(
        threadid   TEXT,
        username   TEXT,
        hashrate   REAL,
        sharetime  REAL,
        accepted   INTEGER,
        rejected   INTEGER,
        diff       INTEGER,
        software   TEXT,
        identifier TEXT,
        algorithm  TEXT)""")
    memory_datab.execute(
        """CREATE INDEX 
        IF NOT EXISTS
        miner_id 
        ON Miners(Identifier)""")
    memory.commit()

    if not os.path.isfile(CONFIG_TRANSACTIONS):
        with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """CREATE TABLE
                IF NOT EXISTS
                Transactions(
                timestamp TEXT,
                username TEXT,
                recipient TEXT,
                amount REAL,
                hash TEXT,
                memo TEXT)""")
            conn.commit()

    if not os.path.isfile(CONFIG_BLOCKS):
        with sqlconn(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """CREATE TABLE
                IF NOT EXISTS
                Blocks(
                timestamp TEXT,
                finder TEXT,
                amount REAL,
                hash TEXT)""")
            conn.commit()

    if not ospath.isfile(DATABASE):
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """CREATE TABLE
                IF NOT EXISTS
                Users(username TEXT,
                password TEXT,
                email TEXT,
                balance REAL)""")
            conn.commit()

    if not ospath.isfile(BLOCKCHAIN):
        # SHA1 of duino-coin
        global_last_block_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
        global_blocks = 1
        with sqlconn(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """CREATE TABLE
                IF NOT EXISTS
                Server(blocks REAL,
                lastBlockHash TEXT)""")
            datab.execute(
                """INSERT
                INTO Server(blocks,
                lastBlockHash) VALUES(?, ?)""",
                (global_blocks, global_last_block_hash))
            conn.commit()
    else:
        with sqlconn(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT blocks FROM Server")
            global_blocks = int(datab.fetchone()[0])
            datab.execute("SELECT lastBlockHash FROM Server")
            global_last_block_hash = str(datab.fetchone()[0])

    with sqlconn(DATABASE) as datab:
        datab.execute(
            """CREATE INDEX 
            IF NOT EXISTS 
            user_id 
            ON Users(username)""")
        datab.execute("PRAGMA journal_mode = WAL")
        datab.commit()

    with sqlconn(CONFIG_TRANSACTIONS) as datab:
        datab.execute(
            """CREATE INDEX 
            IF NOT EXISTS 
            tx_id 
            ON Transactions(hash)""")
        datab.execute("PRAGMA journal_mode = WAL")
        datab.commit()

    with sqlconn(CONFIG_BLOCKS) as datab:
        datab.execute(
            """CREATE INDEX 
            IF NOT EXISTS 
            block_id 
            ON Blocks(hash)""")
        datab.execute("PRAGMA journal_mode = WAL")
        datab.commit()


def load_configfiles():
    global banlist
    global whitelisted
    global whitelistedusr
    global jail

    with open(CONFIG_JAIL, "r") as jailedfile:
        jailedusr = jailedfile.read().splitlines()
        for username in jailedusr:
            jail.append(username)
        admin_print("Successfully loaded jailed usernames file")

    with open(CONFIG_BANS, "r") as bannedusrfile:
        bannedusr = bannedusrfile.read().splitlines()
        for username in bannedusr:
            banlist.append(username)
        admin_print("Successfully loaded banned usernames file")

    with open(CONFIG_WHITELIST, "r") as whitelistfile:
        whitelisted = whitelistfile.read().splitlines()
        for ip in whitelisted:
            try:
                whitelisted_ips.append(socket.gethostbyname(str(ip)))
            except:
                pass
        admin_print("Successfully loaded whitelisted IPs file")

    with open(CONFIG_WHITELIST_USR, "r") as whitelistusrfile:
        whitelistedusr = whitelistusrfile.read().splitlines()
        for username in whitelistedusr:
            whitelisted_usernames.append(username)
        admin_print("Successfully loaded whitelisted usernames file")


def autorestarter():
    sleep(61*60)
    admin_print("Autorestarting")
    for proc in mpproc:
        proc.terminate()
    os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    init(autoreset=True)
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
    queue = multiprocessing.Manager().JoinableQueue()
    load_configfiles()
    create_databases()

    admin_print(Style.BRIGHT
                + Fore.YELLOW
                + "Duino-Coin Master Server is starting")

    import pool_functions as PF
    from kolka_module import *
    from server_functions import *
    from kolka_chip_module import *
    try:
        from wrapped_duco_functions import *
    except:
        pass

    admin_print("Launching background threads")
    threading.Thread(target=autorestarter).start()

    threading.Thread(target=get_duco_prices).start()
    threading.Thread(target=duino_stats_restart_handle).start()

    threading.Thread(target=countips).start()
    threading.Thread(target=resetips).start()
    threading.Thread(target=get_sys_usage).start()

    threading.Thread(target=update_job_tiers).start()
    threading.Thread(target=create_jobs).start()

    threading.Thread(target=chain_updater).start()
    threading.Thread(target=database_updater).start()
    transaction_queue = multiprocessing.Process(
        target=transaction_queue_handle,
        args=[queue, ],
        daemon=True)
    transaction_queue.start()
    mpproc.append(transaction_queue)

    threading.Thread(target=create_main_api_file).start()
    threading.Thread(target=create_minerapi).start()
    threading.Thread(target=create_secondary_api_files).start()

    threading.Thread(target=create_backup).start()

    def _server_handler(port):
        server_thread = StreamServer(
            (HOSTNAME, port),
            handle=handle,
            backlog=BACKLOG
        )
        admin_print("Successfully started TCP server on port " + str(port))
        server_thread.serve_forever()

    for port in PORTS:
        threading.Thread(target=_server_handler,
                         args=[int(port), ]).start()
        sleep(0.01)

    input_management()
