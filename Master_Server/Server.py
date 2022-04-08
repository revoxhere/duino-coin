#!/usr/bin/env python3
"""
Duino-Coin Master Server © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin-rest-api
Duino-Coin Team & Community 2019-2022
"""

import threading
import multiprocessing

import socket
import datetime
import configparser
# python3 -m pip install requests
import requests
import os
# python3 -m pip install psutil
import psutil
import ssl
import sys
import json
import smtplib
import subprocess
import traceback
import resource
import ast

from statistics import mean
from random import randint, choice
from hashlib import sha1
from time import time, mktime
from sys import exit
from re import sub, match
from supersqlite import sqlite3
sqlconn = sqlite3.connect
#from sqlite3 import connect as sqlconn
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
# python3 -m pip install shutil
from shutil import copyfile
from datetime import datetime as utime
# python -m pip install py3-validate-email
from validate_email import validate_email
import base64
import redis
from importlib import reload



"""
Load balancing
"""
SYNC_SERVERS = [
    {
        "name": "REST instance",
        "path": "",
        "port": 22
    },
    {
        "name": "SVKO vps",
        "path": "",
        "port": 22
    }
]

"""
Server
"""
HOSTNAME = "0.0.0.0"
PORTS = [
    # Pool ports for nginx load balancer
    2806,  # Pools
    2807,  # Pools
    2808,  # Pools
    2809,  # Pools
    2810,  # Pools
    2811,  # General purpose
    2812,  # General purpose
    2813,  # General purpose
    2814,  # General purpose
    2815   # General purpose
]
SERVER_VER = 3.0  # announced to clients
SAVE_TIME = 10  # in seconds
BCRYPT_ROUNDS = 6
DECIMALS = 20  # max float precision
TEMP_BAN_TIME = 15  # in minutes
DB_TIMEOUT = 5
MINERAPI_SAVE_TIME = 10

"""
Mining
"""
DIFF_INCREASES_PER = 24000  # net difficulty
DIFF_MULTIPLIER = 1
BLOCK_PROBABILITY = 500000  # 1 in X
BLOCK_REWARD = 28.11  # duco
UPDATE_MINERAPI_EVERY = 2  # shares
EXPECTED_SHARETIME = 15  # in seconds
MAX_WORKERS = 50
PING_SLEEP_TIME = 0.1  # in seconds
MAX_NUMBER_OF_PINGS = 3
MAX_REJECTED_SHARES = 5
MOTD = """\
You are connected to the Duino-Coin master server.
Have fun!
"""

"""
Gevent
"""
BACKLOG = 0
POOL_SIZE = 10240
SOCKET_TIMEOUT = 15

"""
IO files location
"""
CONFIG_BASE_DIR = "config"
DATABASE = CONFIG_BASE_DIR + '/crypto_database.db'
POOL_DATABASE = CONFIG_BASE_DIR + '/pools_database.db'
BLOCKCHAIN = CONFIG_BASE_DIR + '/duino_blockchain.db'
CONFIG_TRANSACTIONS = CONFIG_BASE_DIR + "/transactions.db"
CONFIG_BLOCKS = CONFIG_BASE_DIR + "/foundBlocks.db"
CONFIG_MINERAPI = CONFIG_BASE_DIR + "/minerapi.db"
CONFIG_ALTS = CONFIG_BASE_DIR + "/alt_accounts.db"
CONFIG_BANS = CONFIG_BASE_DIR + "/banned.txt"
CONFIG_JAIL = CONFIG_BASE_DIR + "/jailed.txt"
CONFIG_WHITELIST = CONFIG_BASE_DIR + "/whitelisted.txt"
CONFIG_WHITELIST_USR = CONFIG_BASE_DIR + "/whitelistedUsernames.txt"
API_JSON_URI = "api.json"
CONFIG_JAIL_DUMP = "/home/debian/websites/poolsyncdata/jailed.json"

config = configparser.ConfigParser()
try:
    # Read sensitive data from config file
    config.read('config/AdminData.ini')
    DUCO_EMAIL = config["main"]["duco_email"]
    DUCO_EMAIL_V = config["main"]["duco_email_v"]
    DUCO_PASS = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    PoolPassword = config["main"]["PoolPassword"]
    WRAPPER_KEY = config["main"]["wrapper_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
    CAPTCHA_SECRET_KEY = config["main"]["captcha"]
    BCH_SECRET_KEY = config["main"]["bch"]
    TRX_SECRET_KEY = config["main"]["trx"]
except Exception as e:
    print("""Please create config/AdminData.ini config file first:
        [main]
        duco_email = ???
        duco_email_v = ???
        duco_password = ???
        NodeS_Overide = ???
        PoolPassword = ???
        wrapper_private_key = ???
        NodeS_Username = ???
        wrapper_key = ???
        captcha = ???
        bch = ???
        trx = ???""", e)
    exit()

duco_prices = {
    "xmg":  0.00025,
    "bch":  0.00003,
    "trx":  0.00008,
    "nano": 0.00001,
    "sunswap": 0.00001,
    "nodes": 0.0,
    "furim": 0.0
}
DUCO_EMAIL_V = DUCO_EMAIL
global_blocks = 1
global_last_block_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
global_cpu_usage, global_ram_usage, global_connections = 35, 50, 1000
minerapi, pool_rewards, balance_queue, tx_queue = {}, {}, {}, {}
lastsync = {"master-server": 0}
disconnect_list, banlist = [], []
whitelisted_usernames, whitelisted_ips = [], []
connections_per_ip, miners_per_user = {}, {}
chip_ids, workers, registrations = {}, {}, []
jail, mpproc, pool_infos = [], [], []
cached_balances, cached_logins = {}, {}
lock = threading.Lock()
shop_mercy_list = []
shop_bowtie_list = []
last_block = "DUCO-S1"
blocked_miners = []

with open('config/emails/register.html', 'r') as file:
    html_registered = file.read()

with open('config/emails/verified.html', 'r') as file:
    html_verification_success = file.read()

with open('config/emails/verified_loved.html', 'r') as file:
    html_verification_loved = file.read()

with open('config/emails/verified_rejected.html', 'r') as file:
    html_verification_rejected = file.read()

with open('config/emails/verified_no_usr.html', 'r') as file:
    html_verification_rejected_username = file.read()

with open('config/emails/verified_ask.html', 'r') as file:
    html_verification_ask = file.read()

with open('config/emails/ban.html', 'r') as file:
    html_ban = file.read()

with open('config/emails/buy_finished.html', 'r') as file:
    html_buy_finished = file.read()


def create_backup():
    sleep(10)
    while 1:
        if not ospath.isdir('backups/'):
            os.mkdir('backups/')

        timestamp = now().strftime("%Y-%m-%d_%H-%M-%S")
        os.mkdir('backups/'+str(timestamp))

        today = now().strftime("%Y-%m-%d")
        try:
            for key in duco_prices:
                try:
                    day = datetime.date.today()
                    day_unix = int(mktime(day.timetuple()))
                    with sqlconn("charts/prices.db",
                                 timeout=DB_TIMEOUT) as datab:
                        datab.execute(
                            f"""INSERT INTO prices_{key}
                                (day_unix, day, price)
                                VALUES(?, ?, ?)""",
                            (day_unix, day, duco_prices[key]))
                except:
                    pass
            admin_print("Successfully saved prices")
        except:
            print(traceback.format_exc())

        copyfile(BLOCKCHAIN,
                 "backups/"+str(timestamp)+"/"
                 + BLOCKCHAIN.replace(CONFIG_BASE_DIR, ""))
        copyfile(DATABASE,
                 "backups/"+str(timestamp)+"/"
                 + DATABASE.replace(CONFIG_BASE_DIR, ""))
        copyfile(CONFIG_BLOCKS,
                 "backups/"+str(timestamp)+"/foundBlocks.db")
        copyfile(CONFIG_TRANSACTIONS,
                 "backups/"+str(timestamp)+"/transactions.db")

        # Backup also to svko vps and duino rest
        os.system(
            "rsync -avzhq --exclude 'backups' --exclude 'config/ipbans'"
            + " -e 'ssh -p 22' /home/debian/duino-coin-master-server"
            + " --rsync-path='nice -n 12 rsync' --timeout=30"
            + " ")
        os.system(
            "rsync -avzhq --exclude 'backups' --exclude 'config/ipbans'"
            + " -e 'ssh -p 22' /home/debian/duino-coin-master-server"
            + " --rsync-path='nice -n 12 rsync' --timeout=30"
            + " ")

        admin_print("Successfully created backup for " + str(timestamp))
        sleep(60*60)


def perm_ban(ip):
    if not ip in whitelisted_ips:
        print(f"Banning {ip}")
        os.system(f"sudo csf -d {ip}")


def temporary_ban(ip):
    if not ip in whitelisted_ips:
        print(f"Temp-banning {ip}")
        os.system(f"sudo csf -td {ip}")


def update_pool_rewards():
    global shop_mercy_list
    global shop_bowtie_list
    global pool_rewards
    while 1:
        try:
            with open('../websites/poolsyncdata/poolrewards.json', 'r') as f:
                pool_rewards = json.load(f)
        except Exception as e:
            admin_print(f"Error loading rewards: {e}")
        
        shop_mercy_list = []
        shop_bowtie_list = []
        for user in shop_redis.keys():
            user_items = shop_redis.get(user)
            if not user_items:
                user_items = []
            else:
                user_items = user_items.decode().split(",")
                user_items = list(set([int(i) for i in user_items]))

                if 3 in user_items:
                    shop_bowtie_list.append(user.decode())
                if 4 in user_items:
                    shop_mercy_list.append(user.decode())

        #print(len(shop_mercy_list), len(shop_bowtie_list))

        sleep(60)


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def balance_queue_handler(queue):
    # Internal db queue
    admin_print("Successfully started balance queue")
    while 1:
        s = queue.qsize()
        if s > 200:
            # admin_print(str(s) + " to execute")
            timeStart = time()

            with sqlconn(DATABASE,
                         timeout=DB_TIMEOUT) as datab:
                num = 0
                for i in range(s):
                    task = queue.get()
                    num += 1
                    try:
                        datab.execute(task)
                        queue.task_done()
                    except:
                        # Retry until task is done
                        pass

                i = 0
                while i < 5:
                    try:
                        datab.commit()
                        break
                    except sqlite3.OperationalError as e:
                        admin_print(f"Warning: sqlite operational err ({e}) - retry #{i}")
                        i += 1
                        
            timeEnd = time()
            timeElapsed = round(timeEnd - timeStart, 2)
            if i > 0:
                admin_print(f"Success: internal db commited  with {s} updates in "
                        + f"{timeElapsed}s (retries: {i})")

            if timeElapsed < SAVE_TIME:
                sleep(SAVE_TIME-timeElapsed)
        else:
            sleep(SAVE_TIME)


def transaction_queue_handler(queue):
    # Internal db queue
    admin_print("Successfully started transaction queue")
    while 1:
        s = queue.qsize()
        if s > 0:
            #admin_print(str(s) + "txs to execute")
            timeStart = time()

            with sqlconn(CONFIG_TRANSACTIONS,
                         timeout=DB_TIMEOUT) as datab:
                for i in range(s):
                    task = queue.get()
                    try:
                        datab.execute(task)
                        queue.task_done()
                    except:
                        # Retry until task is done
                        pass

                i = 0
                while i < 5:
                    try:
                        datab.commit()
                        break
                    except sqlite3.OperationalError as e:
                        admin_print(f"Warning: sqlite operational err (tx) ({e}) - retry #{i}")
                        i += 1

            timeEnd = time()
            timeElapsed = round(timeEnd - timeStart, 2)
            if i > 0:
                admin_print(f"Success: internal tx db commited  with {s} updates in "
                        + f"{timeElapsed}s (retries: {i})")

            if timeElapsed < SAVE_TIME:
                sleep(SAVE_TIME-timeElapsed)
        else:
            sleep(SAVE_TIME)


def database_updater():
    global balance_queue
    while 1:
        timeS = time()
        for user in balance_queue.copy():
            try:
                if user in disconnect_list or user in banlist:
                    try:
                        del balance_queue[user]
                    except:
                        pass
                    continue

                if user in jail:
                    try:
                        balance_queue["giveaways"] = balance_queue[user]
                        balance_queue[user] = balance_queue[user] * -3
                    except:
                        pass

                if user in balance_queue:
                    if round(balance_queue[user]) == round(BLOCK_REWARD):
                        threading.Thread(
                            target=generate_block,
                            args=[user, balance_queue[user], None, None]
                        ).start()

                    elif balance_queue[user] > 0.0075:
                        balance_queue[user] = 0.0075

                    if user in shop_mercy_list and user in shop_bowtie_list:
                        # Kolka mercy and bow tie upgrade
                        increment_balance(user, balance_queue[user] * 1.20)
                    elif user in shop_mercy_list:
                        # Kolka mercy upgrade
                        increment_balance(user, balance_queue[user] * 1.15)
                    elif user in shop_bowtie_list:
                        # Bow tie upgrade
                        increment_balance(user, balance_queue[user] * 1.05)
                    else:
                        increment_balance(user, balance_queue[user])
                        
                    try:
                        del balance_queue[user]
                    except:
                        pass
            except Exception as e:
                admin_print(f"DB updater err: {traceback.format_exc()}")

        # if len(balance_queue):
        #     admin_print(f"DB max: {max(balance_queue, key=balance_queue.get)}")

        timeE = time()
        timeEl = timeE - timeS
        if timeEl < SAVE_TIME:
            sleep(SAVE_TIME-timeEl)


def chain_updater():
    db_err_counter = 0
    while 1:
        sleep(60*15)
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


def put_to_queue(command: str, database=None):
    try:
        if not database:
            queue.put(command)
        elif database == "TX":
            tx_queue.put(command)
        else:
            print("Unknown:", database)
    except Exception as e:
        admin_print("Error adding command to the queue: " + str(e))


def create_transaction(sender: str,
                       recipient: str,
                       amount: float,
                       memo="None",
                       last_block_hash=None):
    i = 0
    while i < 3:
        try:
            timestamp = now().strftime("%d/%m/%Y %H:%M:%S")

            randomz = randint(-281100000, 281100000)
            last_block_hash = sha1(
                bytes(str(randomz*0.0000003)
                      + str(sender)
                      + str(amount)
                      + str(memo),
                      encoding='ascii')).hexdigest()

            sql_str = (
                f"INSERT INTO Transactions(timestamp, username, recipient, amount, hash, memo)"
              + f" VALUES('{timestamp}', '{sender}', '{recipient}', '{amount}', '{last_block_hash}', '{memo}')"
            )
            tx_queue.put(sql_str)
            break

        except Exception as e:
            admin_print("Error saving transaction: " + str(e))
            i += 1
            sleep(1)


def input_management():
    while 1:
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
            - exit - exits DUCO server
            - clear - clears the console
            - help - shows this help menu
            - unban <usr> - unbans an user
            - ban <username> - bans username
            - restart - restarts DUCO server
            - remove <username> - removes user
            - jail <username> - jails username
            - setv <usr> - set <usr> as verified
            - verify <usr> - send verify request
            - balance <user> - prints user balance
            - unsetv <usr> -set <usr> as unverified
            - changemail <user> <email> - change email
            - pools - returns info about last pool updates
            - connections - show the number of connections
            - dump-minerapi - dumps minerapi to a json file
            - changpass <user> <newpass> - changes password
            - unjail <usr> - removes user from the jail file
            - set <user> <number> - sets user balance to number
            - changeusername <user> <newuser> - changes username
            - pass <username> <password> - verify password of user
            - insert <usr> <pwd> <mail> <bal> - inserts user to db
            - info <username> - returns infos of an account (mail, ...)
            - stakereset <username> - removes staking balance from user
            - add <user> <number> - moves DUCO from coinexchange to user
            - subtract <user> <number> - moves DUCO from user to coinexchange
            """)

        elif command[0] == "unban":
            admin_print(unban(command[1]))

        elif command[0] == "unjail":
            admin_print(unjail(command[1]))

        elif command[0] == "dump-minerapi":
            try:
                path = "/home/debian/minerapi_dump" + str(randint(0, 9999)) + ".json"
                copy = minerapi.copy()
                with open(path, 'w') as f:
                    json.dump(copy, f)
                admin_print("dumped minerapi to " + path)
            except Exception as e:
                print(str(e))

        elif command[0] == "insert":
            created = str(now().strftime("%d/%m/%Y %H:%M:%S"))
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute(
                    """INSERT INTO Users
                    (username, password, email, balance, created)
                    VALUES(?, ?, ?, ?, ?)""",
                    (command[1], command[2], command[3], command[4], created))
                conn.commit()
                admin_print("Successfully added user")

        elif command[0] == "stakereset":
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute(
                    """UPDATE Users
                    set stake = ?
                    where username = ?""",
                    (0, command[1]))
                conn.commit()
            admin_print(f"Removed staking from {username}")

        elif command[0] == "pools":
            admin_print("Last infos about pool updates:")
            for info in pool_infos[-15:]:
                admin_print("  " + info)

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

        elif command[0] == "verify":
            protocol_verify(command[1])

        elif command[0] == "setv":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    verify = str(datab.fetchone()[5])

                admin = input("  Enter admins username: ")
                if not admin:
                    admin = "revox"

                admin_print(command[1]
                            + "'s verification: "
                            + str(verify).split(",")[0]
                            + ", set it to yes?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set rig_verified = ?
                            where username = ?""",
                            (f"yes,{time()},{admin}", command[1]))
                        conn.commit()
                    admin_print("User is now marked as verified")
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error setting verification: " + str(e))
            threading.Thread(
                target=protocol_verified_mail, 
                args=[command[1], admin]
            ).start()

        elif command[0] == "unsetv":
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    verify = str(datab.fetchone()[5])

                admin_print(command[1]
                            + "'s verification: "
                            + str(verify)
                            + ", set it to no?")

                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set rig_verified = ?
                            where username = ?""",
                            ("no", command[1]))
                        conn.commit()
                        admin_print("User is now marked as NOT verified")
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error unsetting verification: " + str(e))

        elif command[0] == "info":
            if not user_exists(command[1]):
                admin_print("Error: username doesn't exist")
            else:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (command[1],))
                    infos = datab.fetchone()
                if not infos:
                    admin_print("couldn't fetch infos for username " + command[1])
                else:
                    try:
                        print("Username: " + infos[0])
                        print("Email: " + infos[2])
                        print("Balance: " + str(infos[3]))
                        print("Acc creation: " + infos[4])
                        print("Verified: " + infos[5])
                        print("Last seen: " + str(
                            auth_redis.get(command[1]).decode()))
                        print("Stake: " + str(infos[7]))
                    except Exception as e:
                        admin_print("Error: " + str(e))


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

        elif command[0] == "connections":
            admin_print("Current number of connections: " +
                        str(global_connections))

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
                            (command[2], command[1]))
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
                    increment_balance("coinexchange", float(command[2]))
                    admin_print(
                        "Successfully added balance change to the queue")
                    create_transaction(command[1],
                                       "coinexchange",
                                       command[2],
                                       "DUCO Exchange transaction")
                    admin_print("Successfully generated transaction")
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
                    confirm = input("  Send DUCO Exchange buy email? Y/n")
                    if confirm == "Y" or confirm == "y" or confirm == "":
                        threading.Thread(
                            target=buy_finished_mail,
                            args=[str(command[1]), float(command[2])]
                        ).start()
                    increment_balance(str(command[1]), float(command[2]))
                    #increment_balance("coinexchange", -float(command[2]))
                    admin_print(
                        "Successfully added balance change to the queue")
                    create_transaction("coinexchange",
                                       command[1],
                                       command[2],
                                       "DUCO Exchange transaction")
                    admin_print("Successfully generated transaction")
                else:
                    admin_print("Canceled")
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")


def user_exists(username: str):
    try:
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
            return True
    except:
        return False


def user_verified(username: str):
    try:
        with sqlconn(DATABASE,
                     timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                FROM Users
                WHERE
                username = ?""", (username,))
            data = datab.fetchone()[5]
            if "yes" in data.lower():
                return True
            return False
    except Exception as e:
        return False


def email_exists(email: str):
    try:
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
            return True
    except:
        return False


def protocol_verified_mail(username: str, admin: str):
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
        message["Subject"] = "✅ Your mining rig is now verified"
        message["From"] = DUCO_EMAIL_V
        message["To"] = email

        email_body = html_verification_success.replace(
            "{user}", str(username)).replace(
            "{admin}", str(admin))
        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465, context=context) as smtpserver:
            smtpserver.login(DUCO_EMAIL_V, DUCO_PASS)
            smtpserver.sendmail(
                DUCO_EMAIL_V, email, message.as_string())
            admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))


def protocol_loved_verified_mail(username: str, admin: str):
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
        message["Subject"] = "✔️ Your mining rig is now verified"
        message["From"] = DUCO_EMAIL_V
        message["To"] = email

        email_body = html_verification_loved.replace(
            "{user}", str(username)).replace(
            "{admin}", str(admin))
        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465, context=context) as smtpserver:
            smtpserver.login(DUCO_EMAIL_V, DUCO_PASS)
            smtpserver.sendmail(
                DUCO_EMAIL_V, email, message.as_string())
        admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))


def protocol_unverified_mail(username: str, admin: str, reason: str = ""):
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
        message["Subject"] = ("❌ Your verification"
                              + " request has been rejected")
        message["From"] = DUCO_EMAIL_V
        message["To"] = email

        if not reason:
            email_body = html_verification_rejected.replace(
                "{user}", str(username)).replace(
                "{admin}", str(admin))
        else:
            email_body = html_verification_rejected_username.replace(
                "{user}", str(username)).replace(
                "{admin}", str(admin))

        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465, context=context) as smtpserver:
            smtpserver.login(DUCO_EMAIL_V, DUCO_PASS)
            smtpserver.sendmail(
                DUCO_EMAIL_V, email, message.as_string())
        admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))


def protocol_verify(username: str):
    with open("to_verify.txt", 'a') as file:
        file.write(str(username) + " " + str(now()) + "\n")
        admin_print("Added username to verify list")

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
        message["Subject"] = "📷 Verify your Duino-Coin mining rig"
        message["From"] = DUCO_EMAIL_V
        message["To"] = email

        email_body = html_verification_ask.replace("{user}", str(username))
        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465, context=context) as smtpserver:
            smtpserver.login(DUCO_EMAIL_V, DUCO_PASS)
            smtpserver.sendmail(
                DUCO_EMAIL_V, email, message.as_string())
        admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))


def buy_finished_mail(username: str, amount: float):
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
        message["Subject"] = ("💰 Your DUCO buy request is done!")
        message["From"] = DUCO_EMAIL
        message["To"] = email

        email_body = html_buy_finished.replace(
            "{user}", str(username)).replace("{amount}", str(amount))
        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465, context=context) as smtpserver:
            smtpserver.login(DUCO_EMAIL, DUCO_PASS)
            smtpserver.sendmail(
                DUCO_EMAIL, email, message.as_string())
        admin_print("Sent email to " + str(email))
    except Exception as e:
        admin_print("Error sending email: " + str(e))


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

    def send_ban_email(username):
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = ("🚫 Terms of Service violation "
                                  + "on your Duino-Coin wallet")
            message["From"] = DUCO_EMAIL
            message["To"] = email

            email_body = html_ban.replace("{user}", str(username))
            part = MIMEText(email_body, "html")
            message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com",
                                  465, context=context) as smtpserver:
                smtpserver.login(DUCO_EMAIL, DUCO_PASS)
                smtpserver.sendmail(
                    DUCO_EMAIL, email, message.as_string())
            admin_print("Sent email to " + str(email))
        except Exception as e:
            admin_print("Error sending email: " + str(e))

    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute(
            """SELECT *
        FROM Users
        WHERE username = ?""",
            (username,))
        email = str(datab.fetchone()[2])
    threading.Thread(target=send_ban_email, args=[username, ]).start()

    try:
        recipient = "giveaways"
        memo = "Account locked by Kolka"

        # Generate TXID
        random = randint(-281200, 281200)
        global_last_block_hash_cp = sha1(
            bytes(str(username)+str(recipient)+str(random)+str(memo),
                  encoding='utf8')).hexdigest()

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

        create_transaction(username, recipient,
                           amount, memo)
        admin_print("Transferred balance to giveaways account")
    except Exception as e:
        admin_print("Error transfering balance: " +
                    traceback.format_exc())

def unban(username):
    banlist = []
    with open(CONFIG_BANS, "r") as bannedusrfile:
        bannedusr = bannedusrfile.read().splitlines()
        for user in bannedusr:
            banlist.append(user.strip())

    if not username in banlist:
        return "User isn't banned"

    try:
        banlist.remove(username)

        banlist = list(set(banlist))
        with open(CONFIG_BANS, "w") as bannedusrfile:
            for user in banlist:
                bannedusrfile.write(user + "\n")

        return "User unbanned"
    except Exception as e:
        return str(e)


def unjail(username):
    jailedusr = []
    with open(CONFIG_JAIL, "r") as jailedusrfile:
        jailedusrfile = jailedusrfile.read().splitlines()
        for user in jailedusrfile:
            jailedusr.append(user.strip())

    if not username or not username in jailedusr:
        return "User isn't jailed"

    try:
        jailedusr.remove(username)

        jailedusr = list(set(jailedusr))
        with open(CONFIG_JAIL, "w") as jailedusrfile:
            for user in jailedusr:
                jailedusrfile.write(user + "\n")

        return "User unjailed"
    except Exception as e:
        return str(e)
        

def generate_block(username, reward, new_block_hash, connection, xxhash=False):
    algo = "DUCO-S1"
    if connection:
        reward += BLOCK_REWARD

    if not new_block_hash:
        random = randint(-281100, 281100)
        new_block_hash = sha1(
            bytes(str(username)+str(reward)+str(random),
                  encoding='ascii')).hexdigest()

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

    admin_print(algo + " block found by " + str(username))
    if connection:
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
    DUCO-S1 Mining protocol handler
    Takes:  data (JOB,username,requested_difficulty),
            connection object, minerapi access
    Returns to main thread if non-mining data is submitted
    """

    global global_last_block_hash
    global global_blocks
    global workers
    global minerapi
    global balance_queue
    global last_block
    global PING_SLEEP_TIME

    ip_addr = address[0].replace("::ffff:", "")
    thread_id = id(gevent.getcurrent())
    accepted_shares, rejected_shares, reward = 0, 0, 0
    thread_miner_api = {}
    is_first_share = True
    override_difficulty = ""

    while 1:
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

            if not user_exists(username):
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
                this_user_miners = workers[username]
            except:
                this_user_miners = 1

            try:
                # Parse starting difficulty from the client
                req_difficulty = str(data[2])

                if "JOB" in req_difficulty:
                    # Error correction from some esps
                    req_difficulty.strip("JOB")

                if not req_difficulty in pool_rewards:
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
                    req_difficulty.strip("JOB")

                if not req_difficulty in pool_rewards:
                    req_difficulty = "NET"

        try:
            if is_first_share:
                try:
                    difficulty = pool_rewards[req_difficulty]["difficulty"]
                except:
                    difficulty = pool_rewards["NET"]["difficulty"]

            else:
                difficulty = kolka_v3(
                    sharetime, EXPECTED_SHARETIME,
                    difficulty)
        except:
            difficulty = pool_rewards["NET"]["difficulty"]

        difficulty = difficulty * 100000000

        try:
            usr_workers = miners_per_user[username]
        except:
            usr_workers = 1

        if check_workers(0, usr_workers):
            if not username in whitelisted_usernames:
                send_data(
                    "BAD,Too many workers\n",
                    connection)
                if not ip_addr in whitelisted_ips:
                    perm_ban(ip_addr)
                return thread_id

        try:
            job = libducohash.create_share(
                global_last_block_hash_cp, str(difficulty))
        except:
            job = create_share(
                global_last_block_hash_cp, difficulty)

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
        try:
            if req_difficulty == "AVR":
                result[0] = str(int(result[0], 2))
        except Exception:
            send_data("BAD,Please update your miner", connection)
            return thread_id

        connection.settimeout(SOCKET_TIMEOUT)

        max_hashrate = pool_rewards[req_difficulty]["max_hashrate"]
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
                if not kolka_chip_module.check_id(chip_id):
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

            send_data(
                "BAD,You have been moved to a higher difficulty tier\n",
                connection)

        elif int(result[0]) == int(numeric_result):
            """
            Correct result received
            """
            accepted_shares += 1

            if (fastrandint(BLOCK_PROBABILITY) == 1):
                reward = generate_block(
                    username, reward, job[1], connection)
            else:
                basereward = pool_rewards[req_difficulty]["reward"]
                reward = kolka_v1(hashrate, difficulty,
                                  this_user_miners, req_difficulty)
                if wrong_chip_id:
                    reward = 0
                send_data("GOOD\n", connection)

            if accepted_shares > UPDATE_MINERAPI_EVERY:
                try:
                    balance_queue[username] += reward / 3.33
                except:
                    balance_queue[username] = reward / 3.33
        else:
            """
            Incorrect result received
            """
            rejected_shares += 1
            accepted_shares -= 1

            send_data("BAD\n", connection)

        is_first_share = False

        if accepted_shares % UPDATE_MINERAPI_EVERY == 0:
            """
            These things don't need to run every share
            """
            if is_first_share:
                try:
                    workers[username] += 1
                except:
                    workers[username] = 1

            try:
                # Check miner software for unallowed characters
                miner_name = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[2])
                if not SERVER_VER in miner_name:
                    send_data("BAD,Please update your miner", connection)
                    return thread_id
            except:
                miner_name = "Unknown miner"

            try:
                # Check rig identifier for unallowed characters
                rig_identifier = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[3])
            except:
                rig_identifier = "None"

            try:
                wallet_id = int(result[5])
            except:
                wallet_id = None

            if abs(reported_hashrate-hashrate) > 20000:
                reported_hashrate = hashrate
                hashrate_is_estimated = True

            thread_miner_api = {
                "u":   str(username),
                "h":   hashrate,
                "s":   sharetime,
                "a":   accepted_shares,
                "r":   rejected_shares,
                "d":   difficulty,
                "sft": str(miner_name),
                "id":  str(rig_identifier),
                "t":   int(time()),
                "p":   "master-server",
                "wd":  wallet_id
            }

            thread_miner_api["al"] = "DUCO-S1"

            minerapi[thread_id] = thread_miner_api

            global_blocks += UPDATE_MINERAPI_EVERY
            global_last_block_hash = job[1]

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


def get_connections():
    global_connections = subprocess.run(
        'sudo ss -s',
        stdout=subprocess.PIPE,
        shell=True
    ).stdout.decode().rstrip().splitlines()[0].strip("Total: ")

    return int(global_connections)


def get_sys_usage():
    global global_cpu_usage
    global global_ram_usage
    global global_connections
    cpu_list, mem_list, conn_list = [], [], []

    while 1:
        conn_list.append(get_connections())
        global_connections = int(mean(conn_list[-SAVE_TIME*60:]))

        cpu_list.append(
            floatmap(psutil.cpu_percent(), 0, 100, 0, 75))
        global_cpu_usage = mean(cpu_list[-SAVE_TIME*60:])

        mem_list.append(
            floatmap(psutil.virtual_memory()[2], 0, 100, 0, 75))
        global_ram_usage = mean(mem_list[-SAVE_TIME*60:])

        sleep(SAVE_TIME)


def scientific_prefix(symbol: str, value: float, accuracy: int, giga=False):
    """
    Input: symbol to add, value
    Output rounded value with scientific prefix as string
    """
    if value >= 900000000000 and giga:
        prefix = " T"
        value = value / 1000000000000
    elif value >= 900000000 and giga:
        prefix = " G"
        value = value / 1000000000
    elif value >= 900000:
        prefix = " M"
        value = value / 1000000
    elif value >= 900:
        prefix = " k"
        value = value / 1000
    else:
        prefix = " "
    return (
        str(round(value, accuracy))
        + str(prefix)
        + str(symbol))


def fix_db():
    # hacky wacky fix xD
    os.system(
        "sudo chmod 777")
    #for proc in mpproc:
     #   proc.terminate()
    #os.execl(sys.executable, sys.executable, *sys.argv)


def count_registered_users():
    """
    Count all registered users and return an int
    """
    while 1:
        try:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("SELECT COUNT(username) FROM Users")
                registeredUsers = datab.fetchone()[0]
                return int(registeredUsers)
        except:
            fix_db()


def count_total_duco():
    """
    Count all DUCO in accounts and return a float
    """
    while 1:
        try:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("SELECT SUM(balance) FROM Users")
                total_duco = datab.fetchone()[0]
                break
        except:
            fix_db()

    ignored_usernames = ["celoDUCO", "maticDUCO", "bscDUCO"]
    for username in ignored_usernames:
        total_duco = total_duco - get_balance(username)

    return float(total_duco)


def get_richest_users(limit):
    """
    Return a list of n richest users
    """
    leaders = []
    ignored_usernames = ["celoDUCO", "maticDUCO", "bscDUCO"]

    while 1:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                FROM Users
                ORDER BY balance DESC
                LIMIT """ + str(limit))
            rows = datab.fetchall()
            break

    for row in rows:
        try:
            if row[3] not in ignored_usernames:
                leaders.append(
                    str(round((float(row[3])), DECIMALS))
                    + " DUCO - "
                    + row[0])
        except Exception as e:
            print(e, row)

    return leaders


def get_balances(min_bal=0.1):
    """
    Returns a dictionary of balances of all users
    """
    balances = {}
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT *
                FROM Users
                ORDER BY balance DESC""")
            rows = datab.fetchall()

        for row in rows:
            if float(row[3]) > min_bal:
                balances[str(row[0])] = float(row[3])
            else:
                """
                Stop when rest of the balances are just empty accounts
                """
                break
    except:
        pass

    return balances


def get_last_transactions(limit=5):
    """
    Returns a dictionary with last n transactions
    """
    transactions = []
    transactions_dict = {}
    while True:
        try:
            with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Transactions")
                rows = datab.fetchall()
            break
        except:
            pass

    for row in rows:
        transactions.append({
            "Date":      str(row[0].split(" ")[0]),
            "Time":      str(row[0].split(" ")[1]),
            "Sender":    str(row[1]),
            "Recipient": str(row[2]),
            "Amount":    float(row[3]),
            "Hash":      str(row[4]),
            "Memo":      str(sub(r"[^A-Za-z0-9 .-:!#_+-]+", ' ', str(row[5])))
        })

    for transaction in transactions[-limit:]:
        transactions_dict[transaction["Hash"]] = transaction

    return transactions_dict


def get_last_blocks(limit=20):
    """
    Returns a dictionary with last n mined blocks
    """
    blocks = []
    blocks_dict = {}
    with sqlconn(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Blocks")
        rows = datab.fetchall()

    for row in rows:
        blocks.append({
            "Date":             str(row[0].split(" ")[0]),
            "Time":             str(row[0].split(" ")[1]),
            "Finder":           str(row[1]),
            "Amount generated": float(row[2]),
            "Hash":             str(row[3])
        })

    for block in blocks[-limit:]:
        blocks_dict[block["Hash"]] = block

    return blocks_dict


def create_secondary_api_files():
    while 1:
        with open('foundBlocks.json', 'w') as outfile:
            json.dump(
                get_last_blocks(),
                outfile,
                ensure_ascii=False)

        with open('balances.json', 'w') as outfile:
            json.dump(
                get_balances(),
                outfile,
                ensure_ascii=False)

        with open('transactions.json', 'w') as outfile:
            json.dump(
                get_last_transactions(),
                outfile,
                ensure_ascii=False)

        sleep(30)


def sync_db(files, destination, port=22):
    """
    Syncs files to a different server
    """
    files_path = ""
    for file in files:
        files_path += f"er/{file} "

    os.system(f"rsync -avhq --no-compress --timeout=30 "
            + f"-e 'ssh -T -x -p {port}' "
            + f"{files_path} {destination}")


def sync_dbs(server):
    while 1:
        time_start = time()
        try:
            sync_db([
                    DATABASE, 
                    CONFIG_MINERAPI, 
                    CONFIG_TRANSACTIONS, 
                    POOL_DATABASE,
                    "config/prices.json",
                    "config/banned.txt"
                ], 
                server["path"], server["port"])
        except Exception as e:
            print(e)

        time_el = round(time() - time_start, 2)
        #admin_print(f"Syncing {server['name']} took {time_el}s")
        if time_el < SAVE_TIME / 2:
            sleep(SAVE_TIME/2 - time_el)


def create_main_api_file():
    """
    Creates api.json file containing
    information about the server and
    connected miners
    """
    global miners_per_user

    sleep(5)
    richest = get_richest_users(10)
    while 1:
        timeS = time()
        total_hashrate_list = []
        total_hashrate, net_wattage = 0, 0
        ducos1_hashrate, xxhash_hashrate = 0, 0
        minerapi_public, miners_per_user = {}, {}
        miner_list = []
        miner_dict = {
            "GPU": 0,
            "CPU": 0,
            "RPi": 0,
            "Phone": 0,
            "Web": 0,
            "ESP32": 0,
            "ESP8266": 0,
            "Arduino": 0,
            "Other": 0,
            "All": 0}
        hashrates = {}
        try:
            for miner in minerapi.copy():
                try:
                    username = minerapi[miner]["u"]
                    if username in banlist or minerapi[miner]["h"] > 10_000_000:
                        continue

                    if minerapi[miner]["al"] == "DUCO-S1":
                        ducos1_hashrate += minerapi[miner]["h"]
                    else:
                        xxhash_hashrate += minerapi[miner]["h"]

                    software = minerapi[miner]["sft"].upper()
                    identifier = minerapi[miner]["id"].upper()
                    hashrate = minerapi[miner]["h"]

                    # Calculate power usage
                    if ("AVR" in software
                            or "I2C" in software
                            or "ARDUINO" in software):
                        # 0.2W for Arduinos
                        net_wattage += 0.2
                        miner_dict["Arduino"] += 1

                    elif "ESP32" in software:
                        # 0.7W (2 cores) for ESP32
                        net_wattage += 0.4
                        miner_dict["ESP32"] += 1

                    elif "ESP8266" in software:
                        # 0.5W for ESP8266
                        net_wattage += 0.5
                        miner_dict["ESP8266"] += 1

                    elif "WEB" in software:
                        net_wattage += 1
                        miner_dict["Web"] += 1

                    elif ("OPENCL" in software
                          or "GPU" in software):
                        net_wattage += 50
                        miner_dict["GPU"] += 1

                    elif ("ANDROID" in software
                          or "PHONE" in software
                          or "ROUTER" in software):
                        net_wattage += 0.25
                        miner_dict["Phone"] += 1

                    elif ("PC" in software
                          or "NONCE" in software
                          or "DOCKER" in software):
                        if ("RASPBERRY" in identifier
                                or "PI" in identifier):
                            net_wattage += 1.75
                            miner_dict["RPi"] += 1
                        else:
                            net_wattage += 6.25
                            miner_dict["CPU"] += 1
                    else:
                        net_wattage += 0
                        miner_dict["Other"] += 1
                except Exception as e:
                    pass

            for key in miner_dict:
                miner_dict[key] = round(miner_dict[key])

            miner_dict["All"] = sum(miner_dict.values())

            net_wattage = scientific_prefix("W", net_wattage, 2)

            total_hashrate_list.append(xxhash_hashrate + ducos1_hashrate)
            total_hashrate = scientific_prefix(
                "H/s", mean(total_hashrate_list[-100:]), 2)
            xxhash_hashrate = scientific_prefix("H/s", xxhash_hashrate, 1, True)
            ducos1_hashrate = scientific_prefix("H/s", ducos1_hashrate, 1, True)

            miners_per_user = OrderedDict(
                sorted(
                    miners_per_user.items(),
                    key=itemgetter(1),
                    reverse=True))

            kolka_dict = {
                "Jailed": len(jail),
                "Banned": len(banlist)}

            current_time = now().strftime("%d/%m/%Y %H:%M:%S (UTC)")
            max_price = duco_prices[max(duco_prices, key=duco_prices.get)]

            duco_prices["pancake"] = 0.0000524598
            duco_prices["sushi"] = 0.0000594892
            duco_prices["max"] = max_price

            for key in duco_prices:
                duco_prices[key] = round(duco_prices[key], 6)

            server_api = {
                "Duino-Coin Server API": "github.com/revoxhere/duino-coin",
                "Server version":        SERVER_VER,
                "Active connections":    global_connections,
                "Open threads":          threading.activeCount(),
                "Server CPU usage":      round(global_cpu_usage, 1),
                "Server RAM usage":      round(global_ram_usage, 1),
                "Last update":           current_time,
                "Last sync":             timeS,
                "Net energy usage":      net_wattage,
                "Pool hashrate":         total_hashrate,
                "DUCO-S1 hashrate":      ducos1_hashrate,
                "XXHASH hashrate":       xxhash_hashrate,
                "Duco price":            duco_prices["max"],
                "Duco price XMG":        duco_prices["xmg"],
                "Duco price BCH":        duco_prices["bch"],
                "Duco price TRX":        duco_prices["trx"],
                "Duco price NANO":       duco_prices["nano"],
                "Duco Node-S price":     duco_prices["nodes"],
                "Duco Furim price":      duco_prices["furim"],
                "Duco SunSwap price":    duco_prices["sunswap"],
                "Duco PancakeSwap price": duco_prices["pancake"],
                "Duco SushiSwap price":  duco_prices["sushi"],
                "Registered users":      count_registered_users(),
                "All-time mined DUCO":   count_total_duco(),
                "Current difficulty":    pool_rewards["NET"]["difficulty"],
                "Mined blocks":          global_blocks,
                "Last block hash":       global_last_block_hash,
                "Kolka":                 kolka_dict,
                "Miner distribution":    miner_dict,
                "Top 10 richest miners": richest}

            with open(API_JSON_URI, 'w') as outfile:
                json.dump(server_api, outfile,
                          ensure_ascii=False, sort_keys=True)

            with open("config/prices.json", "w") as outfile:
                json.dump(duco_prices, outfile,
                          ensure_ascii=False, sort_keys=True)

        except Exception:
            admin_print("Error creating main api.json file:"
                        + str(traceback.format_exc()))

        timeE = time()
        timeEl = timeE - timeS
        if timeEl < SAVE_TIME:
            sleep(SAVE_TIME-timeEl)

cached_keys = {}
def create_minerapi():
    """
    Creates a database with the miners
    that is later used to provide user info
    in the REST API
    """
    global minerapi, MINERAPI_SAVE_TIME, cached_keys

    def check_miner_key(username, miner_key):
        try:
            key = miner_key_redis.get(username)

            if not key:
                with sqlconn(DATABASE, timeout=1) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                            FROM Users
                            WHERE username = ?""",
                        (str(username), ))
                    data = datab.fetchone()

                if not data:
                    return False

                key = data[6]
                miner_key_redis.set(username, key)

            try:
                key = key.decode()
            except:
                pass
            
            if (not str(key).strip() 
                or str(key).strip() == "0" 
                or str(key).strip() == "None"
                or base64.b64decode(
                    key
                ).decode().strip().capitalize() == "None"):
                # No key enabled
                # print(username, "no key enabled")
                return True
            elif key == miner_key:
                # Check if key matches
                # print(username, "key matches", miner_key, key)
                return True
            else:
                # Key not matching
                # print(username, "invalid key", miner_key, key.decode())
                return False
        except Exception as e:
            #print("Key db check err:", e, username, miner_key)
            return True

    while 1:
        timeS = time()
        memory_datab.execute("DELETE FROM Miners")

        def unsetv(username):
            pass

        miners_per_user = {}
        minerapi_cp = minerapi.copy()
        for threadid in minerapi.copy():
            try:
                try:
                    kolkaid = int(minerapi_cp[threadid]["c"])
                except Exception as e:
                    kolkaid = 0

                try:
                    software = str(minerapi_cp[threadid]["sft"])
                except:
                    try:
                        del balance_queue[username]
                    except KeyError:
                        pass
                    try:
                        minerapi_cp.pop(threadid)
                    except KeyError:
                        pass
                    continue

                try:
                    rigid = str(minerapi_cp[threadid]["id"])
                except:
                    rigid = "None"

                username = minerapi_cp[threadid]["u"]
                if username in banlist or username in jail:
                    username = "giveaways"

                try:
                    miner_key = minerapi_cp[threadid]["pw"]
                    if not check_miner_key(username, miner_key):
                        if "rw" in minerapi_cp[threadid]:
                            try:
                                balance_queue[username] -= minerapi_cp[threadid]["rw"] / 1000
                            except KeyError:
                                pass
                        else:
                            try:
                                del balance_queue[username]
                            except KeyError:
                                pass
                        try:
                            minerapi_cp.pop(threadid)
                        except KeyError:
                            pass
                        continue
                except Exception as e:
                    print("Key check err:", e)

                for entry in blocked_miners:
                    if entry in rigid.lower() or entry in software.lower():
                        try:
                            del balance_queue[username]
                        except KeyError:
                            pass
                        try:
                            minerapi_cp.pop(threadid)
                        except KeyError:
                            pass
                        continue

                try:
                    hashrate = float(minerapi_cp[threadid]["h"])
                except:
                    try:
                        del balance_queue[username]
                    except KeyError:
                        pass
                    try:
                        minerapi_cp.pop(threadid)
                    except KeyError:
                        pass
                    continue

                try:
                    if "k" in minerapi_cp[threadid]:
                        kolka_chip_id = minerapi_cp[threadid]["k"].strip()
                        if kolka_chip_id:
                            if not new_check(kolka_chip_id, software)[0]:
                                print(username, new_check(kolka_chip_id, software)[1], software)
                                try:
                                    minerapi_cp.pop(threadid)
                                except KeyError:
                                    pass
                                try:
                                    del balance_queue[username]
                                except KeyError:
                                    pass
                                continue
                except:
                    pass

                try:
                    miners_per_user[username] += 1
                except:
                    miners_per_user[username] = 1

                try:
                    if miners_per_user[username] > MAX_WORKERS:
                        # print(username, miners_per_user[username])
                        try:
                            minerapi_cp.pop(threadid)
                        except KeyError:
                            pass
                        try:
                            del balance_queue[username]
                        except KeyError:
                            pass
                        continue
                except Exception as e:
                    print(e)

                try:
                    pool = str(minerapi_cp[threadid]["p"])
                except:
                    pool = "Unknown pool"

                try:
                    wallet_id = int(minerapi_cp[threadid]["wd"])
                except:
                    if "PC" in software or "Android" in software:
                        wallet_id = 0
                    else:
                        wallet_id = None
                
                last_miner_share = minerapi_cp[threadid]["t"]
                pool_sync_time = lastsync[pool]

                # Put miner in the db
                memory_datab.execute(
                    """INSERT INTO Miners
                    (threadid, username, hashrate, sharetime,
                    accepted, rejected, diff, software, identifier,
                    algorithm, pool, walletid, kolkaid)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        threadid,
                        username,
                        hashrate,
                        minerapi_cp[threadid]["s"],
                        minerapi_cp[threadid]["a"],
                        minerapi_cp[threadid]["r"],
                        minerapi_cp[threadid]["d"],
                        software,
                        rigid,
                        minerapi_cp[threadid]["al"],
                        pool,
                        wallet_id,
                        kolkaid)
                )

                # Pop inactive miners from the API
                if pool_sync_time != 0:
                    difference = float(pool_sync_time) - \
                        float(last_miner_share)
                else:
                    difference = time() - float(last_miner_share)
                difference_server = time() - float(last_miner_share)
                if (difference > SAVE_TIME*2 or difference_server > 60*5):
                    minerapi_cp.pop(threadid)

                minerapi = minerapi_cp
            except Exception as e:
                #continue
                print(traceback.format_exc())
        memory.commit()

        with sqlconn(CONFIG_MINERAPI) as disk_conn:
            memory.backup(disk_conn)
            disk_conn.commit()

        timeE = time()
        timeEl = abs(timeE - timeS)
        # admin_print(f"Creating minerapi took {timeEl}s")
        if timeEl < MINERAPI_SAVE_TIME:
            sleep(MINERAPI_SAVE_TIME-timeEl)


def protocol_login(data, connection):
    """
    Check if user password matches to the one stored
    in the database, returns bool as login state
    """
    username = str(data[1])
    password = str(data[2]).encode('utf-8')

    if user_exists(username):
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
    message["Subject"] = (u"\U0001F44B" +
                          " Welcome on the Duino-Coin network, "
                          + str(username)
                          + "!")
    try:
        message["From"] = DUCO_EMAIL
        message["To"] = email

        email_body = html_registered.replace("{user}", str(username))
        part = MIMEText(email_body, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(
                DUCO_EMAIL, DUCO_PASS)
            smtp.sendmail(
                DUCO_EMAIL, email, message.as_string())
            return True
    except Exception as e:
        try:
            message["From"] = DUCO_EMAIL_V
            message["To"] = email

            email_body = html_registered.replace("{user}", str(username))
            part = MIMEText(email_body, "html")
            message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                                  context=context) as smtp:
                smtp.login(
                    DUCO_EMAIL_V, DUCO_PASS)
                smtp.sendmail(
                    DUCO_EMAIL_V, email, message.as_string())
                return True
        except:
            print(traceback.format_exc())
            return False


def protocol_register(data, connection, address):
    """
    Register a new user, return on error
    """
    global registrations
    username = str(data[1])
    unhashed_pass = str(data[2]).encode('utf-8')
    email = str(data[3]).replace("REGI", "")
    ip = address[0].replace("::ffff:", "")

    send_data("NO,Please use the webwallet (wallet.duinocoin.com)", connection)
    return

    if ip in registrations or alt_check(ip, username)[0]:
        send_data(
            "NO,You have already registered",
            connection)
        return

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

    if not validate_email(email, check_smtp=False):
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
        created = str(now().strftime("%d/%m/%Y %H:%M:%S"))
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """INSERT INTO Users
                (username, password, email, balance, created)
                VALUES(?, ?, ?, ?, ?)""",
                (username, password, email, .0, created))
            conn.commit()
        registrations.append(ip)
        print("Registered", username, email, unhashed_pass)
        send_data("OK", connection)
        return
    else:
        send_data("NO,Error sending verification e-mail", connection)
        return


def alt_check(ip_addr: str, username: str, save=True, legacy=True):
    state = False
    alts = None

    try:
        if ip_addr in whitelisted_ips or username in whitelisted_usernames:
            return (False, None)

        with sqlconn(CONFIG_ALTS, timeout=DB_TIMEOUT)as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                             FROM alt_accounts
                             WHERE ip_addr = ?""",
                          (ip_addr, ))
            row = datab.fetchone()

        if row:
            existing_usernames = row[1].split(",")
            if not username in existing_usernames:
                existing_usernames.append(username)

            if username != existing_usernames[0]:
                with sqlconn(CONFIG_ALTS) as conn:
                    datab = conn.cursor()
                    datab.execute("""UPDATE alt_accounts
                                     SET usernames = ?
                                     WHERE ip_addr = ?""",
                                  (",".join(existing_usernames), ip_addr))
                    conn.commit()

                if len(existing_usernames) > 2:
                    state = True
                    
                if legacy:
                    alts = str(" ".join(existing_usernames))
                else:
                    alts = str(existing_usernames)
        else:
            with sqlconn(CONFIG_ALTS) as conn:
                datab = conn.cursor()
                datab.execute("""INSERT INTO alt_accounts(
                                    ip_addr, usernames
                                ) VALUES(?, ?)""",
                              (ip_addr, username))
                conn.commit()

    except Exception as e:
        print(traceback.format_exc())

    return (state, alts)


def acc_check(address: str, username: str, save=True):
    state = False
    accs = None

    try:
        if username in whitelisted_usernames:
            return (False, None)

        with sqlconn(CONFIG_ALTS)as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                             FROM chain_accounts
                             WHERE address = ?""",
                          (address, ))
            row = datab.fetchone()

        if row != username:
            state = True
            accs = str(row)
        else:
            with sqlconn(CONFIG_ALTS, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""INSERT INTO chain_accounts(
                                    username, address
                                ) VALUES(?, ?)""",
                              (username, address))
                conn.commit()

    except Exception as e:
        print(traceback.format_exc())

    return (state, accs)


def protocol_send_funds(data, connection, username, ip_addr):
    """
    Transfers funds from one account to another
    """
    try:
        memo = sub(r"[^A-Za-z0-9 .-:!#_+-]+", ' ', str(data[1]))
        if len(str(memo)) > 256:
            memo = str(memo[0:256]) + "..."

        # Generate TXID
        random = randint(-281100, 281100)
        global_last_block_hash_cp = sha1(
            bytes(str(username)+str(data)+str(random)+str(memo),
                  encoding='ascii')).hexdigest()

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

        if not user_verified(username):
            send_data("NO,Account not verified", connection)
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

        #altfeed = alt_check(ip_addr, username)
        # if altfeed[0]:
        #    send_data(
        #       f"NO,You're using alt-account(s): {altfeed[1]}",
        #       connection)
        #    return

        acccheck = acc_check(memo, username)
        if acccheck[0]:
            send_data(
                f"NO,This address has been already used: {acccheck[1]}",
                connection)
            return

        if float(balance) >= float(amount):
            balance -= float(amount)
            recipientbal += float(amount)

            while 1:
                try:
                    with sqlconn(DATABASE,
                                 timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
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

            create_transaction(username, recipient,
                               amount, memo, global_last_block_hash_cp)

            admin_print(f"Successfully sent {amount} DUCO "
                        + f"from {username} to {recipient}")

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
            if (now() - last_cache_time).total_seconds() <= 10:
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
    while 1:
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
            exchange_rate_nano = de_api["nano"]["sell"]

            """
            Get pairs prices from Coingecko
            """
            while 1:
                try:
                    coingecko_api = requests.get(
                        "https://api.coingecko.com/"
                        + "api/v3/simple/price?ids="
                        + "tron,bitcoin-cash,ripple,"
                        + "digibyte,nano,fujicoin,bitcoin,"
                        + "ravencoin"
                        + "&vs_currencies=usd",
                        data=None
                    ).json()
                    break
                except:
                    sleep(60)

            """
            Calculate prices from exchange rates
            """

            try:
                xmg_btc = 0
                r = requests.get('https://btcpop.co/api/market-public.php').json()
                for row in r:
                    if row["ticker"] == "XMG":
                        xmg_btc = float(row["lastTradePrice"])
                        break
            except:
                xmg_btc = 0

            btc_usd = float(coingecko_api["bitcoin"]["usd"])
            duco_prices["xmg"] = round(
                exchange_rate_xmg * (xmg_btc * btc_usd), 8
            )

            bch_usd = float(coingecko_api["bitcoin-cash"]["usd"])
            duco_prices["bch"] = round(
                bch_usd * exchange_rate_bch, 8
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
            Gets DUCO price from the Furim P2P exchange
            """
            try:
                furim_api = requests.get(
                    "https://exchange.furim.xyz/price",
                    data=None).json()

                furim_price = round(
                    float(furim_api["lastprice_trx"]) * trx_usd, 8
                )

                duco_prices["furim"] = furim_price
            except Exception as e:
                duco_prices["furim"] = 0.0

            """
            Gets wDUCO price from sunswap exchange
            """
            try:
                sunswap_api = requests.get(
                    "https://apilist.tronscan.org/"
                    + "api/account?address="
                    + "TRAoFeB7n8Tt4nZGTRB8La4UP4i84bsoMh",
                    data=None).json()

                # Converts values back to floats
                trxBal = int(
                    sunswap_api["tokens"][0]["balance"]) / 100000
                wducoBal = int(
                    sunswap_api["tokens"][-1]["balance"]) / 100000

                # Sunswap pool exchange rate
                exchange_rate = trxBal / wducoBal

                duco_prices["sunswap"] = round(
                    float(exchange_rate) * float(trx_usd), 8
                )
            except:
                duco_prices["sunswap"] = 0.0

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
                "Memo":      str(sub(
                    r"[^A-Za-z0-9 .-:!#_+-]+",
                    ' ', str(row[5])))
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


def handle(connection, address):
    """
    Handler for every connected client
    """
    global global_blocks
    global global_last_block_hash
    global minerapi
    global balance_queue
    global global_connections
    global disconnect_list
    global pool_infos
    global lastsync

    data = None
    logged_in = False
    ip_addr = address[0].replace("::ffff:", "")
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

        while 1:
            """
            Wait until client sends data
            """
            data = receive_data(connection, limit=2048)
            if not data:
                break

            # POOL FUNCTIONS

            if data[0] == "PoolSync":
                try:
                    blocks_to_add,\
                        poolConnections,\
                        poolWorkers,\
                        rewards,\
                        error = Pool.sync(data)
                    global_blocks += blocks_to_add

                    for user in rewards:
                        amount_to_update = rewards[user]
                        if (amount_to_update
                                and match(r"^[A-Za-z0-9_-]*$", user)):
                            try:
                                balance_queue[user] += amount_to_update
                            except:
                                balance_queue[user] = amount_to_update

                    for worker in poolWorkers:
                        try:
                            minerapi[worker] = poolWorkers[worker]
                            minerapi[worker]["t"] = time()
                        except Exception as e:
                            continue

                    timestamp = str(now().strftime("%H:%M:%S"))
                    pool_infos.append(timestamp
                                      + " - Pool synced "
                                      + str(len(rewards))
                                      + " rewards")

                    lastsync[str(info['name'])] = time()

                    send_data("SyncOK\n", connection)
                except Exception as e:
                    print(traceback.format_exc())

            elif data[0] == "PoolLogin":
                try:
                    timestamp = str(now().strftime("%H:%M:%S"))
                    info = str(data[1])
                    info = ast.literal_eval(info)
                    info = json.loads(info)
                    pool_infos.append(timestamp
                                      + " - Pool "
                                        + info['identifier']
                                        + " logged in")
                    Pool = PF.Pool(connection=connection)
                    Pool.login(data=data)
                except Exception as e:
                    send_data(f"Error,{e}\n", connection)

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

            elif data[0] == "Queue":
                if ip_addr == "127.0.0.1":
                    put_to_queue(data[1].replace("@", ","))
                else:
                    print("Not localhost", ip_addr, queue)
                    send_data("Not allowed", connection)

            elif data[0] == "TxQueue":
                if ip_addr == "127.0.0.1":
                    put_to_queue(data[1].replace("@", ","), "TX")
                else:
                    print("Not localhost", ip_addr, queue)
                    send_data("Not allowed", connection)

            elif data[0] == "VER":
                send_data(SERVER_VER, connection)

            elif data[0] == "LOGI":
                """ Client requested authentication """
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
                #thread_id = protocol_mine(data, connection, address)
                #username = data[1]
                sleep(SOCKET_TIMEOUT-1)
                send_data("BAD,Please mine on the pool", connection)
                break

            # USER FUNCTIONS

            elif data[0] == "BALA":
                """Client requested balance check"""
                if logged_in:
                    protocol_get_balance(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "UEXI":
                """Client requested reqistration check"""
                if user_exists(data[1]):
                    send_data("OK,User is registered", connection)
                else:
                    send_data("NO,User is not registered", connection)

            elif data[0] == "REGI":
                """Client requested registation"""
                protocol_register(data, connection, address)
                break

            elif data[0] == "CHGP":
                """Client requested password change"""
                if (logged_in
                    and not username in jail
                        and not username in banlist):
                    protocol_change_pass(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "GTXL":
                """Client requested transaction list"""
                protocol_get_transactions(data, connection)

            elif data[0] == "SEND":
                """Client requested funds transfer"""
                if (logged_in
                    and not username in jail
                        and not username in banlist):
                    protocol_send_funds(data, connection, username, ip_addr)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "PING":
                """Client requested a ping response"""
                send_data("Pong!", connection)

            elif data[0] == "MOTD":
                """Client requested to send him the MOTD"""
                send_data(MOTD, connection)

            # WRAPPED DUCO FUNCTIONS by yanis

            elif data[0] == "WRAP":
                if (logged_in
                    and not username in jail
                        and not username in banlist):
                    admin_print(
                        "Starting wrapping protocol by " + username)
                    try:
                        amount = str(data[1])
                        tron_address = str(data[2])
                    except IndexError:
                        send_data("NO,Not enough data", connection)
                        break
                    else:
                        altfeed = alt_check(ip_addr, username)
                        if altfeed[0]:
                            send_data(
                                f"You're using alt-account(s): {altfeed[1]}",
                                connection)
                        else:
                            if user_verified(username):
                                wrapfeedback = protocol_wrap_wduco(
                                    username, tron_address, amount)
                                if wrapfeedback:
                                    send_data(wrapfeedback, connection)
                                else:
                                    send_data(
                                        "OK,Nothing returned", connection)
                            else:
                                send_data("NO,User not verified", connection)
                else:
                    send_data("NO,Not logged in", connection)

            elif data[0] == "UNWRAP":
                if logged_in:
                    if use_wrapper and wrapper_permission:
                        admin_print(
                            "Starting unwraping protocol by " + username)
                        try:
                            amount = str(data[1])
                            if amount > 1500:
                                send_data("NO,Invalid amount", connection)
                                break
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
            else:
                break

    except Exception:
        pass
        # print(traceback.format_exc())
    finally:
        #print(ip_addr, "closing socket", data)

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

        connection.close()


def countips():
    """
    Check if address is making more than
    n connections in a peroid of n seconds,
    if so - ban the IP
    """
    while 1:
        for ip in connections_per_ip.copy():
            try:
                if (connections_per_ip[ip] > 50
                        and not ip in whitelisted_ips):
                    temporary_ban(ip)
            except:
                pass
        sleep(10)


def resetips():
    """
    Reset connections per address values every n sec
    """
    while 1:
        sleep(30)
        connections_per_ip.clear()


def duino_stats_restart_handle():
    while 1:
        if ospath.isfile("config/restart_signal"):
            os.remove("config/restart_signal")
            admin_print("Server restarted by Duino-Stats command")
            for proc in mpproc:
                proc.terminate()
            os.execl(sys.executable, sys.executable, *sys.argv)
        sleep(5)


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
    memory_datab.execute("PRAGMA synchronous = FULL")
    memory.commit()

    memory_datab.execute(
        """
        CREATE TABLE
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
        algorithm  TEXT,
        pool       TEXT,
        walletid   TEXT,
        threads    INTEGER,
        kolkaid    INTEGER)
        """)
    memory_datab.execute(
        """CREATE INDEX
        IF NOT EXISTS
        username
        ON Miners(username)""")
    memory.commit()

    try:
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
                    memo TEXT,
                    id INTEGER
                    NOT NULL PRIMARY KEY
                    AUTOINCREMENT UNIQUE)""")
                conn.commit()

        #for db in [DATABASE, CONFIG_BLOCKS, CONFIG_ALTS]:
        #    with sqlconn(db, timeout=DB_TIMEOUT) as conn:
        #        datab = conn.cursor()
        #        datab.execute("REINDEX")
        #        admin_print(f"Reindexed {db}")
        #        conn.commit()
        #    with sqlconn(db, timeout=DB_TIMEOUT) as conn:
        #        datab = conn.cursor()
        #        datab.execute("PRAGMA optimize")
        #        admin_print(f"Optimized {db}")
        #        conn.commit()

        # with sqlconn(DATABASE) as conn:
        #     conn.execute("PRAGMA synchronous=MEMORY")

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
                    Users(
                        "username" TEXT,
                        "password" TEXT,
                        "email" TEXT,
                        "balance" REAL,
                        "created" TEXT DEFAULT 'before 23.08.2021',
                        "rig_verified" TEXT DEFAULT 'No',
                        "last_seen" INTEGER DEFAULT 0,
                        "stake" INTEGER DEFAULT 0
                    )""")
                conn.commit()

        #with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
        #    datab = conn.cursor()
        #    datab.execute(
        #        """ALTER TABLE Users ADD COLUMN "stake" INTEGER DEFAULT 0""")
        #    conn.commit()
        #    print("added column")

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

        #with sqlconn(DATABASE) as datab:
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        user_id
        #        ON Users(username)""")
        #    datab.commit()

        #with sqlconn(CONFIG_ALTS) as conn:
        #    datab = conn.cursor()
        #    datab.execute(
        #        """CREATE TABLE
        #            IF NOT EXISTS
        #            alt_accounts(
        #            ip_addr TEXT UNIQUE,
        #            usernames TEXT)""")
        #    datab.execute(
        #        """CREATE TABLE
        #           IF NOT EXISTS
        #            chain_accounts(
        #            address TEXT,
        #            username TEXT)""")
        #    conn.commit()

        with sqlconn(CONFIG_ALTS) as datab:
            #datab.execute(
            #    "pragma temp_store = memory;")
            #datab.execute(
            #    "pragma synchronous = normal;")
            datab.execute(
                "pragma journal_mode = WAL;")
            #datab.execute(
            #    "pragma mmap_size = 30000000000;")
            datab.commit()

        #with sqlconn(CONFIG_ALTS) as datab:
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        address
        #        ON chain_accounts(address)""")
        #    datab.commit()

        #with sqlconn(CONFIG_TRANSACTIONS) as datab:
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        tx_id
        #        ON Transactions(hash)""")
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        username
        #        ON Transactions(username)""")
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        recipient
        #        ON Transactions(recipient)""")
            #datab.execute(
            #    "pragma temp_store = memory;")
            #datab.execute(
            #    "pragma synchronous = normal;")
            #datab.execute(
            #    "pragma journal_mode = WAL;")
            #datab.execute(
            #    "pragma mmap_size = 30000000000;")
            #datab.commit()

        #with sqlconn(CONFIG_BLOCKS) as datab:
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        block_id
        #        ON Blocks(hash)""")
        #    datab.execute(
        #        """CREATE INDEX
        #        IF NOT EXISTS
        #        finder
        #        ON Blocks(finder)""")
            #datab.execute(
            #    "pragma temp_store = memory;")
            #datab.execute(
            #    "pragma synchronous = normal;")
            #datab.execute(
            #    "pragma journal_mode = WAL;")
            #datab.execute(
            #    "pragma mmap_size = 30000000000;")
            #datab.commit()
    except Exception as e:
        print(traceback.format_exc())
        for db in [DATABASE, CONFIG_BLOCKS, CONFIG_ALTS, CONFIG_TRANSACTIONS]:
            os.system(f"sudo chmod 777 {db}")
            os.system(f"sudo chmod +x {db}")
            create_databases()


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

    with open(CONFIG_JAIL_DUMP, 'w') as outfile:
        json.dump(
            jailedusr,
            outfile,
            ensure_ascii=False)

    with open(CONFIG_BANS, "r") as bannedusrfile:
        bannedusr = bannedusrfile.read().splitlines()
        for username in bannedusr:
            banlist.append(username)
        admin_print("Successfully loaded banned usernames file")

    with open('/home/debian/websites/poolsyncdata/bans.json', 'w') as outfile:
        json.dump(
            bannedusr,
            outfile,
            ensure_ascii=False)

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
    sleep(5*60)
    admin_print("Autorestarting")
    for proc in mpproc:
        proc.terminate()
    os.execl(sys.executable, sys.executable, *sys.argv)


def master_pool():
    while 1:
        try:
            poolCpu = float(global_cpu_usage)
            poolRam = float(global_ram_usage)
            poolConnections = int(get_connections())

            hide_this_pool = "True"
            # if poolCpu > 50 or poolRam > 50:
            #    hide_this_pool = "True"
            POOL_DATABASE = "config/pools_database.db"
            poolID = DUCO_PASS

            with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""UPDATE PoolList
                    SET cpu = ?,
                    ram = ?,
                    connections = ?,
                    hidden = ?
                    WHERE identifier = ?""",
                              (poolCpu,
                               poolRam,
                               poolConnections,
                               hide_this_pool,
                               poolID))
                conn.commit()
        except Exception as e:
            print("pool save err", e)
        sleep(30)


load_configfiles()

if __name__ == "__main__":
    init(autoreset=True)

    create_databases()
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

    queue = multiprocessing.Manager().JoinableQueue()
    tx_queue = multiprocessing.Manager().JoinableQueue()

    shop_redis = redis.Redis(host='localhost', port=6379, db=4)
    miner_key_redis = redis.Redis(host='localhost', port=6379, db=3)
    auth_redis = redis.Redis(host='localhost', port=6379, db=2)

    admin_print(Style.BRIGHT + Fore.YELLOW
                + f"Duino-Coin Master Server is starting: {os.getpid()}")

    import pool_functions as PF
    from kolka_module import *
    from server_functions import *
    import kolka_chip_module
    try:
        from wrapped_duco_functions import *
    except Exception as e:
        print(e)

    admin_print("Launching background threads")

    # threading.Thread(target=autorestarter).start()

    # threading.Thread(target=master_pool).start()
    threading.Thread(target=get_duco_prices).start()
    threading.Thread(target=duino_stats_restart_handle).start()

    # threading.Thread(target=countips).start()
    # threading.Thread(target=resetips).start()
    threading.Thread(target=get_sys_usage).start()

    threading.Thread(target=update_pool_rewards).start()
    threading.Thread(target=chain_updater).start()
    threading.Thread(target=database_updater).start()

    balance_queue_p = multiprocessing.Process(
        target=balance_queue_handler,
        args=[queue, ],
        daemon=True)
    balance_queue_p.start()
    mpproc.append(balance_queue_p)

    transaction_queue_p = multiprocessing.Process(
        target=transaction_queue_handler,
        args=[tx_queue, ],
        daemon=True)
    transaction_queue_p.start()
    mpproc.append(transaction_queue_p)

    for server in SYNC_SERVERS:
        ms = multiprocessing.Process(target=sync_dbs, args=[server, ])
        ms.start()
        mpproc.append(ms)

    threading.Thread(target=create_main_api_file).start()
    threading.Thread(target=create_minerapi).start()
    threading.Thread(target=create_secondary_api_files).start()
    threading.Thread(target=create_backup).start()

    def _server_handler(port):
        server_thread = StreamServer(
            (HOSTNAME, port),
            handle=handle,
            backlog=BACKLOG,
            spawn=Pool(POOL_SIZE))
        admin_print("Successfully started TCP server on port " + str(port))
        server_thread.serve_forever()

    for port in PORTS:
        threading.Thread(target=_server_handler,
                         args=[int(port), ]).start()

    sleep(0.5)
    while 1:
        try:
            input_management()
        except:
            pass
pass
