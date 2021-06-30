#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server (v2.5)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################

# Import libraries
import threading
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

""" Global variables """
HOSTNAME = ""
LEGACY_PORT = 2811
WALLET_PORT = 2812
PC_PORT = 2813
AVR_PORT = 2814
ESP_PORT = 2815
MOTD = """\
You are connected to the official Duino-Coin server.
Please make sure you're using release 2.5 or 2.5.1 to get good stability.
Have fun mining!
"""
DIFF_INCREASES_PER = 24000  # net difficulty
DIFF_MULTIPLIER = 1
SAVE_TIME = 5  # in seconds
DB_TIMEOUT = 5
BACKLOG = None  # default for gevent is 128
POOL_SIZE = 5000
SERVER_VER = 2.5  # announced to clients
READY_HASHES_NUM = 5000  # in shares
BLOCK_PROBABILITY = 1000000  # 1 in X
BLOCK_REWARD = 28.11  # duco
UPDATE_MINERAPI_EVERY = 3  # in shares
EXPECTED_SHARETIME = 10  # in seconds
MAX_REJECTED_SHARES = 5
BCRYPT_ROUNDS = 6
DECIMALS = 20  # max float precision
MAX_WORKERS = 24
PING_SLEEP_TIME = 0.5  # in seconds
MAX_NUMBER_OF_PINGS = 3
TEMP_BAN_TIME = 120  # in seconds

""" IO files location """
DATABASE = 'crypto_database.db'
BLOCKCHAIN = 'duino_blockchain.db'
CONFIG_BASE_DIR = "config"
CONFIG_TRANSACTIONS = CONFIG_BASE_DIR + "/transactions.db"
CONFIG_BLOCKS = CONFIG_BASE_DIR + "/foundBlocks.db"
CONFIG_MINERAPI = CONFIG_BASE_DIR + "/minerapi.db"
CONFIG_BANS = CONFIG_BASE_DIR + "/banned.txt"
CONFIG_WHITELIST = CONFIG_BASE_DIR + "/whitelisted.txt"
CONFIG_WHITELIST_USR = CONFIG_BASE_DIR + "/whitelistedUsernames.txt"
API_JSON_URI = "api.json"

config = configparser.ConfigParser()
try:
    # Read sensitive data from config file
    config.read('AdminData.ini')
    DUCO_EMAIL = config["main"]["duco_email"]
    DUCO_PASS = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    PoolPassword = config["main"]["PoolPassword"]
    WRAPPER_KEY = config["main"]["wrapper_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
except Exception as e:
    print("""Please create AdminData.ini config file first:
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
duco_price, duco_price_justswap, duco_price_nodes = 0, 0, 0
global_last_block_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
global_cpu_usage, global_ram_usage = [50], [50]
global_connections = 1
minerapi = {}
job_tiers = {}
balances_to_update = {}
pregenerated_jobs_avr = {}
pregenerated_jobs_due = {}
pregenerated_jobs_arm = {}
pregenerated_jobs_mega = {}
pregenerated_jobs_esp32 = {}
pregenerated_jobs_esp8266 = {}
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

# Registration email - text version
text = """\
Hi there!
Your e-mail address has been successfully verified
and you are now registered on the Duino-Coin network!
We hope you'll have a great time using Duino-Coin.
If you have any difficulties there are a lot of guides
on our website: https://duinocoin.com/getting-started
You can also join our Discord server:
https://discord.gg/kvBkccy to chat, take part in
giveaways, trade and get help from other Duino-Coin users.
Happy mining!
Sincerely, Duino-Coin Team"""

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
       <a href="https://discord.gg/kvBkccy">Discord server</a>
       to chat, take part in giveaways, trade and get
       help from other Duino-Coin users.<br><br>
       Happy mining!<br>
       <italic>Sincerely, Duino-Coin Team</italic>
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
Sincerely, Duino-Coin Team"""

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
    </a>.</h4>
    <p>As a result, your account has been permanently banned.<br>
       <italic>Sincerely, Duino-Coin Team</italic>
    </p>
  </body>
</html>
"""


def create_backup():
    """ Creates a backup folder every day """
    counter = 0
    while True:
        if not ospath.isdir('backups/'):
            os.mkdir('backups/')

        today = datetime.date.today()
        if not ospath.isdir('backups/'+str(today)+'_0/'):
            sleep(5)
            with open("prices.txt", "a") as pricesfile:
                pricesfile.write("," + str(duco_price).rstrip("\n"))
            with open("pricesNodeS.txt", "a") as pricesNodeSfile:
                pricesNodeSfile.write(
                    "," + str(duco_price_nodes).rstrip("\n"))
            with open("pricesJustSwap.txt", "a") as pricesJustSwapfile:
                pricesJustSwapfile.write(
                    "," + str(duco_price_justswap).rstrip("\n"))

        if not ospath.isdir('backups/'+str(today)+'_'+str(counter)+'/'):
            os.mkdir('backups/'+str(today)+'_'+str(counter))
            copyfile(BLOCKCHAIN, "backups/"+str(today) +
                     '_'+str(counter)+"/"+BLOCKCHAIN)
            copyfile(DATABASE, "backups/"+str(today) +
                     '_'+str(counter)+"/"+DATABASE)
            copyfile(CONFIG_BLOCKS, "backups/"+str(today) +
                     '_'+str(counter)+"/foundBlocks.db")
            copyfile(CONFIG_TRANSACTIONS, "backups/"+str(today) +
                     '_'+str(counter)+"/transactions.db")
            admin_print("Backup finished")

        hours = 6
        counter += 1
        sleep(60*60*hours)


def perm_ban(ip):
    """ Bans an IP """
    if not ip in whitelisted_ips:
        os.system("sudo ipset add banned-hosts "+str(ip)+" >/dev/null 2>&1")


def unban(ip):
    """ Unbans an IP """
    os.system("sudo ipset del banned-hosts "+str(ip)+" >/dev/null 2>&1")


def temporary_ban(ip):
    """ Temporarily bans an IP """
    if not ip in whitelisted_ips:
        os.system("sudo ipset add banned-hosts "+str(ip)+" >/dev/null 2>&1")
        threading.Timer(TEMP_BAN_TIME, unban, [ip]).start()


def update_job_tiers():
    global job_tiers
    while True:
        job_tiers = {
            "EXTREME": {
                "difficulty": 1500000,
                "reward": 0,
                "max_hashrate": 999999999
            },
            "XXHASH": {
                "difficulty": 750000,
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
                "difficulty": int(1200 * DIFF_MULTIPLIER),
                "reward": .00175,  # 0.00375
                "max_hashrate": 16000
            },
            "ESP8266": {
                "difficulty": int(1000 * DIFF_MULTIPLIER),
                "reward": .00015,  # 0.0045
                "max_hashrate": 13000
            },
            "DUE": {
                "difficulty": int(300 * DIFF_MULTIPLIER),
                "reward": .003,
                "max_hashrate": 7000
            },
            "ARM": {
                "difficulty": int(100 * DIFF_MULTIPLIER),
                "reward": .003,
                "max_hashrate": 5000
            },
            "MEGA": {
                "difficulty": int(16 * DIFF_MULTIPLIER),
                "reward": .004,
                "max_hashrate": 400
            },
            "AVR": {
                "difficulty": 6,
                "reward": .005,
                "max_hashrate": 240
            }
        }
        sleep(60)


def create_jobs():
    """ Generate DUCO-S1A jobs for low-power devices """
    while True:
        global_last_block_hash_cp = global_last_block_hash
        base_hash = sha1(global_last_block_hash_cp.encode('ascii'))
        temp_hash = None
        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            avr_diff = job_tiers["AVR"]["difficulty"]
            rand = fastrandint(100 * avr_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_avr[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            due_diff = job_tiers["DUE"]["difficulty"]
            rand = fastrandint(100 * due_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_due[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            arm_diff = job_tiers["ARM"]["difficulty"]
            rand = fastrandint(100 * arm_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_arm[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            mega_diff = job_tiers["MEGA"]["difficulty"]
            rand = fastrandint(100 * mega_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_mega[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            esp32_diff = job_tiers["ESP32"]["difficulty"]
            rand = fastrandint(100 * esp32_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_esp32[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}

        for i in range(int(READY_HASHES_NUM)):
            temp_hash = base_hash.copy()
            esp8266_diff = job_tiers["ESP8266"]["difficulty"]
            rand = fastrandint(100 * esp8266_diff)
            temp_hash.update(str(rand).encode('ascii'))
            pregenerated_jobs_esp8266[i] = {
                "numeric_result": rand,
                "expected_hash": temp_hash.hexdigest(),
                "last_block_hash": str(global_last_block_hash_cp)}
        sleep(60)


def get_pregenerated_job(req_difficulty):
    """ Get pregenerated job from pregenerated
        difficulty tiers
        Takes:      req_difficulty
        Outputs:    job ready to send to client"""

    if req_difficulty == "AVR":
        # Arduino
        difficulty = job_tiers["AVR"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_avr) - 1)
        numeric_result = pregenerated_jobs_avr[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_avr[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_avr[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "DUE":
        # Arduino Due
        difficulty = job_tiers["DUE"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_due) - 1)
        numeric_result = pregenerated_jobs_due[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_due[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_due[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "ARM":
        # ARM boards
        difficulty = job_tiers["ARM"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_arm) - 1)
        numeric_result = pregenerated_jobs_arm[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_arm[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_arm[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "MEGA":
        # megaAVR boards
        difficulty = job_tiers["MEGA"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_mega) - 1)
        numeric_result = pregenerated_jobs_mega[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_mega[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_mega[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    elif req_difficulty == "ESP8266":
        # ESP8266
        difficulty = job_tiers["ESP8266"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp8266[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp8266[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp8266[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]

    else:
        # ESP32
        difficulty = job_tiers["ESP32"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp32[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp32[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp32[rand]["last_block_hash"]
        return [last_block_hash, expected_hash, numeric_result, difficulty]


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def database_updater():
    db_err_counter = 0
    while True:
        try:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                for user in balances_to_update.copy():
                    amount_to_update = balances_to_update[user]

                    if amount_to_update > 0.2:
                        amount_to_update = amount_to_update / 100
                    if amount_to_update > 0.02:
                        amount_to_update = floatmap(
                            amount_to_update, 0.02, 0.5, 0.02, 0.025)

                    try:
                        estimated_profits[user].append(amount_to_update)
                    except:
                        estimated_profits[user] = []
                        estimated_profits[user].append(amount_to_update)

                    datab.execute(
                        """UPDATE Users
                        SET balance = balance + ?
                        WHERE username = ?""",
                        (amount_to_update, user))
                    balances_to_update.pop(user)
                conn.commit()
        except Exception as e:
            admin_print("Database error:", e)
            db_err_counter += 1
            if db_err_counter >= 5:
                admin_print("Restarting server - too many DB errs")
                os.execl(sys.executable, sys.executable, *sys.argv)
        sleep(SAVE_TIME)


def chain_updater():
    db_err_counter = 0
    while True:
        try:
            with sqlconn(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
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
            admin_print("Database error:", e)
            db_err_counter += 1
            if db_err_counter > 5:
                admin_print("Restarting server - too many DB errs")
                os.execl(sys.executable, sys.executable, *sys.argv)
        sleep(SAVE_TIME*3)


def input_management():
    sleep(.2)
    while True:
        command = input("DUCO Console $ ")
        command = command.split(" ")

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
            - chips <username> - shows chip ids
            - profit <username> - shows estimated profit
            - pass <username> <password> - verify password of user""")

        elif command[0] == "chips":
            try:
                username = command[1]
                print(" ".join(chip_ids[username]))
            except Exception as e:
                print(e)

        elif command[0] == "profit":
            try:
                admin_print("Estimated daily profit: " +
                            str(mean(
                                estimated_profits[command[1]][-100:])*17280))
            except Exception as e:
                print(e)

        elif command[0] == "jail":
            jail.append(str(command[1]))
            admin_print("Added "+str(command[1]) + " to earnings jail")

        elif command[0] == "clear":
            os.system('clear')

        elif command[0] == "ban":
            try:
                username = command[1]
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """UPDATE Users
                            set password = ?
                            where username = ?""",
                        (DUCO_PASS, username))
                    conn.commit()
                admin_print("Changed password")
            except Exception as e:
                admin_print("Error changing password: " + str(e))

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
                    admin_print("Sent email to", str(email))
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

        elif command[0] == "exit":
            admin_print("Are you sure you want to exit DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
                os._exit(0)
            else:
                admin_print("Canceled")

        elif command[0] == "restart":
            admin_print("Are you sure you want to restart DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
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
                    print(password)
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
                    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                            + ", subtract "
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
                            (float(balance)-float(command[2]), command[1]))
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

                    global_last_block_hash_cp = global_last_block_hash
                    with sqlconn(CONFIG_TRANSACTIONS,
                                 timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        formatteddatetime = now().strftime("%d/%m/%Y %H:%M:%S")
                        datab.execute(
                            """INSERT INTO Transactions
                            (timestamp, username, recipient, amount, hash, memo)
                            VALUES(?, ?, ?, ?, ?, ?)""",
                            (formatteddatetime,
                                command[1],
                                "coinexchange",
                                command[2],
                                global_last_block_hash_cp,
                                "DUCO Exchange transaction"))
                        conn.commit()
                else:
                    admin_print("Canceled")
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")

        elif command[0] == "add":
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
                            + ", add "
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
                            (float(balance)+float(command[2]), command[1]))
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

                    global_last_block_hash_cp = global_last_block_hash
                    with sqlconn(CONFIG_TRANSACTIONS,
                                 timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        formatteddatetime = now().strftime("%d/%m/%Y %H:%M:%S")
                        datab.execute(
                            """INSERT INTO Transactions
                            (timestamp, username, recipient, amount, hash, memo)
                            VALUES(?, ?, ?, ?, ?, ?)""",
                            (formatteddatetime,
                                "coinexchange",
                                command[1],
                                command[2],
                                global_last_block_hash_cp,
                                "DUCO Exchange transaction"))
                        conn.commit()
                else:
                    admin_print("Canceled")
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")


def user_exists(username):
    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
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


def email_exists(email):
    with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
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


def generate_block(username, reward, new_block_hash, connection, xxhash=False):
    if xxhash:
        algo = "XXHASH"
    else:
        algo = "DUCO-S1"
    reward += BLOCK_REWARD
    with sqlconn(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
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
    admin_print("Block found by " + username)
    send_data("BLOCK\n", connection)
    return reward


def sleep_by_cpu_usage(upper_limit):
    """ Suspends execution depending on current cpu usage """
    sleeptime = floatmap(global_cpu_usage[-1], 0, 100, 0, upper_limit)
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


def create_share_ducos1(last_block_hash, difficulty):
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
                bytes(expected_hash_str, encoding='ascii')).hexdigest()

        job = [last_block_hash_cp, expected_hash, numeric_result]
        return job
    except Exception as e:
        print("DUCOS1 ERR:", e)


def create_share_xxhash(last_block_hash, difficulty):
    """ Creates and returns a job for XXHASH algo """
    last_block_hash_cp = last_block_hash
    try:
        try:
            numeric_result = fastrandint(100 * difficulty)
        except:
            numeric_result = randint(0, 100 * difficulty)
        expected_hash_str = bytes(
            str(last_block_hash_cp)
            + str(numeric_result
                  ), encoding="utf-8")
        expected_hash = xxh64(expected_hash_str, seed=2811)
        job = [last_block_hash_cp, expected_hash.hexdigest(), numeric_result]
        return job
    except Exception as e:
        print("XXHASH ERR:", e)


def protocol_mine(data, connection, address, using_xxhash=False):
    """ DUCO-S1 (-S1A) & XXHASH Mining protocol handler
        Takes:  data (JOB,username,requested_difficulty),
                connection object, minerapi access
        Returns to main thread if non-mining data is submitted """

    global global_last_block_hash
    global global_blocks
    global workers
    global PING_SLEEP_TIME

    ip_addr = address[0].replace("::ffff:", "")
    accepted_shares, rejected_shares = 0, 0
    thread_miner_api = {}
    is_first_share = True
    thread_id = id(gevent.getcurrent())
    override_difficulty = ""
    reward = 0

    while True:
        global_last_block_hash_cp = global_last_block_hash
        if is_first_share:
            try:
                username = str(data[1])
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    break
                if username in banlist:
                    if not username in whitelisted_usernames:
                        perm_ban(ip_addr)
                    sleep(5)
                    break

            except:
                send_data(
                    "BAD,Not enough data\n",
                    connection)
                break

            try:
                chip_ids[username] = []
            except:
                pass

            if using_xxhash:
                req_difficulty = "XXHASH"
            else:
                try:
                    # Parse starting difficulty from the client
                    req_difficulty = str(data[2])
                    if not req_difficulty in job_tiers:
                        req_difficulty = "NET"
                except:
                    req_difficulty = "NET"
        else:
            data = receive_data(connection, limit=48)

            if override_difficulty != "":
                req_difficulty = override_difficulty
            else:
                req_difficulty = data[2]

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
                temporary_ban(ip_addr)
                break

        if (job_tiers[req_difficulty]["difficulty"]
                > job_tiers["ESP32"]["difficulty"]):
            if using_xxhash:
                job = create_share_xxhash(
                    global_last_block_hash_cp, difficulty)
            else:
                job = libducohash.create_share(
                    global_last_block_hash_cp, str(difficulty))
        # Sending job
        send_data(job[0] + "," + job[1] + "," + str(difficulty) + "\n",
                  connection)
        job_sent_timestamp = utime.now()
        connection.settimeout(120)

        # Receiving the result
        number_of_pings = 0
        time_spent_on_sending = 0
        while number_of_pings < MAX_NUMBER_OF_PINGS:
            result = receive_data(connection)
            if not result:
                return thread_id
            if result[0] == 'PING':
                start_sending = utime.now()
                send_data('Pong!', connection)
                time_spent_on_sending += (utime.now() -
                                          start_sending).total_seconds()
                """ Avoiding dos attacks: check number_of_pings
                    to close connection with too many pings """
                number_of_pings += 1
                sleep(PING_SLEEP_TIME)
            else:
                break
        difference = utime.now() - job_sent_timestamp
        sharetime = difference.total_seconds()

        connection.settimeout(15)

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
        if (not using_xxhash
            and req_difficulty == "AVR"
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
            break

        if username in banlist:
            if not username in whitelisted_usernames:
                if not ip_addr in whitelisted_ips:
                    perm_ban(ip_addr)
                sleep(5)
                break

        if (accepted_shares > 0
                and accepted_shares % UPDATE_MINERAPI_EVERY == 0
                and hashrate < 1000000):
            """ These things don't need to run every share """
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

            if abs(reported_hashrate-hashrate) > 10000:
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
                "Last share":   now(),
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

        if hashrate > max_hashrate:
            if hashrate > max_hashrate*10:
                if not ip_addr in whitelisted_ips:
                    temporary_ban(ip_addr)
                sleep(5)
                break

            """ Kolka V2 hashrate check """
            rejected_shares += 1
            accepted_shares -= 1

            if not using_xxhash:
                override_difficulty = kolka_v2(req_difficulty, job_tiers)

            sleep(3)
            send_data("BAD\n", connection)

        elif int(result[0]) == int(numeric_result):
            """ Correct result received """
            accepted_shares += 1

            if accepted_shares > UPDATE_MINERAPI_EVERY:
                try:
                    if workers[ip_addr] < workers[username]:
                        this_user_miners = workers[username]
                    else:
                        this_user_miners = workers[ip_addr]
                except:
                    this_user_miners = 1

                basereward = job_tiers[req_difficulty]["reward"]
                reward = kolka_v1(hashrate, difficulty, this_user_miners)
                if wrong_chip_id:
                    reward = reward / 10
                    # TODO

                if username in jail:
                    try:
                        balances_to_update[username] += reward * -3
                    except:
                        balances_to_update[username] = reward * -3
                    try:
                        balances_to_update["giveaways"] += reward
                    except:
                        balances_to_update["giveaways"] = reward
                else:
                    try:
                        balances_to_update[username] += reward
                    except:
                        balances_to_update[username] = reward

            if fastrandint(BLOCK_PROBABILITY) != 1:
                send_data("GOOD\n", connection)
            else:
                """ Block found """
                if using_xxhash:
                    reward = generate_block(
                        username, reward, job[1], connection, xxhash=True)
                else:
                    reward = generate_block(
                        username, reward, job[1], connection)
        else:
            """ Incorrect result received """
            rejected_shares += 1
            accepted_shares -= 1

            send_data("BAD\n", connection)

        is_first_share = False
        sleep(hashrate/200000)
    return thread_id


def admin_print(*message):
    print(now().strftime("%H:%M:%S.%f:"), *message)


def now():
    return utime.now()


def get_sys_usage():
    global global_cpu_usage
    global global_ram_usage
    global global_connections

    def _get_connections(port):
        connections = subprocess.run(
            'sudo netstat -anp | grep -w ' +
            str(port) + ' | grep ESTABLISHED | wc -l',
            stdout=subprocess.PIPE,
            shell=True
        ).stdout.decode().rstrip()
        return int(connections)

    while True:
        global_connections = _get_connections(2811)
        global_connections += _get_connections(2812)
        global_connections += _get_connections(2813)
        global_connections += _get_connections(2814)
        global_connections += _get_connections(2815)

        global_cpu_usage.append(psutil.cpu_percent())
        global_ram_usage.append(psutil.virtual_memory()[2])
        sleep(SAVE_TIME)


def hashrate_prefix(hashrate: int, accuracy: int):
    """ Input: hashrate as int
        Output rounded hashrate with scientific prefix as string """
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
    """ Input: hattage as int
        Output rounded wattage with scientific prefix as string """
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
    """ Count all registered users and returns an int """
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT COUNT(username) FROM Users")
            registeredUsers = datab.fetchone()[0]
            return int(registeredUsers)
    except:
        return 0


def count_total_duco():
    """ Count all DUCO in accounts and return a float """
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT SUM(balance) FROM Users")
            total_duco = datab.fetchone()[0]
        return float(total_duco)
    except:
        return 0


def get_richest_users(num):
    """ Return a list of num richest users """
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
    """ Returns a dictionary of balances of all users """
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
                # Stop when rest of the balances are just empty accounts
                break
    return(balances)


def get_transaction_list():
    """ Returns a dictionary of all transactions """
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
    """ Returns a dictionary of all mined blocks """
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
                indent=1,
                ensure_ascii=False
            )
        with open('balances.json', 'w') as outfile:
            json.dump(
                get_balance_list(),
                outfile,
                indent=1,
                ensure_ascii=False
            )
        with open('transactions.json', 'w') as outfile:
            json.dump(
                get_transaction_list(),
                outfile,
                indent=1,
                ensure_ascii=False
            )
        sleep(60)


def create_main_api_file():
    """ Creates api.json file
        this will sooner or later be replaced with a RESTful api """
    global miners_per_user

    while True:
        try:
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
            for miner in minerapi.copy():
                try:
                    a = minerapi[miner]["Last share"]
                    b = now()

                    difference = b - a

                    if difference.seconds > 60:
                        minerapi.pop(miner)
                except:
                    try:
                        minerapi.pop(miner)
                    except:
                        pass
                else:
                    try:
                        # Add miner hashrate to the server hashrate
                        if minerapi[miner]["Algorithm"] == "DUCO-S1":
                            ducos1_hashrate += minerapi[miner]["Hashrate_calc"]
                        else:
                            xxhash_hashrate += minerapi[miner]["Hashrate_calc"]

                        # Calculate power usage
                        software = minerapi[miner]["Software"]
                        identifier = minerapi[miner]["Identifier"]

                        if "ESP32" in software.upper():
                            # 1,4W (but 2 cores) for ESP32 @ peak 480mA/3,3V
                            net_wattage += 0.7
                            miner_dict["ESP32"] += 1

                        elif "ESP8266" in software.upper():
                            # 1,3W for ESP8266 @ peak 400mA/3,3V
                            net_wattage += 1.3
                            miner_dict["ESP8266"] += 1

                        elif "AVR" in software.upper():
                            # 0,2W for Arduino @ peak 40mA/5V
                            net_wattage += 0.2
                            miner_dict["Arduino"] += 1

                        elif ("PC" in software.upper()
                              or "WEB" in software.upper()):
                            if ("RASPBERRY" in identifier.upper()
                                    or "PI" in identifier.upper()):
                                # 3,875 for one Pi4 core - Pi4 max 15,8W
                                net_wattage += 3.875
                                miner_dict["RPi"] += 1

                            else:
                                # ~70W for typical CPU and 8 mining threads
                                # (9W per mining thread)
                                net_wattage += 9
                                miner_dict["CPU"] += 1

                        elif ("OPENCL" in software.upper()
                              or "GPU" in software.upper()):
                            net_wattage += 50
                            miner_dict["GPU"] += 1

                        else:
                            net_wattage += 5
                            miner_dict["Other"] += 1

                        miner_list.append(minerapi[miner]["User"])
                    except:
                        pass

            net_wattage = power_prefix(float(net_wattage), 2)
            total_hashrate = hashrate_prefix(
                int(xxhash_hashrate + ducos1_hashrate), 4)
            xxhash_hashrate = hashrate_prefix(int(xxhash_hashrate), 1)
            ducos1_hashrate = hashrate_prefix(int(ducos1_hashrate), 1)

            for user in miner_list:
                miners_per_user[user] = miner_list.count(user)

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
                "Server CPU usage":      round(mean(global_cpu_usage[-5:])),
                "Server RAM usage":      round(mean(global_ram_usage[-5:])),
                "Last update":           now().strftime(
                    "%d/%m/%Y %H:%M:%S (UTC)"),
                "Net energy usage":      net_wattage,
                "Pool hashrate":         total_hashrate,
                "DUCO-S1 hashrate":      ducos1_hashrate,
                "XXHASH hashrate":       xxhash_hashrate,
                "Duco price":            duco_price,
                "Duco Node-S price":     duco_price_nodes,
                "Duco JustSwap price":   duco_price_justswap,
                "Registered users":      count_registered_users(),
                "All-time mined DUCO":   count_total_duco(),
                "Current difficulty":    job_tiers["NET"]["difficulty"],
                "Mined blocks":          global_blocks,
                "Last block hash":       global_last_block_hash[:10]+"...",
                "Kolka":                 kolka_dict,
                "Miner distribution":    miner_dict,
                "Top 10 richest miners": get_richest_users(10),
                "Active workers":        miners_per_user
            }

            with open(API_JSON_URI, 'w') as outfile:
                json.dump(
                    server_api,
                    outfile,
                    indent=1,
                    ensure_ascii=False)
        except Exception:
            print("API err:", traceback.format_exc())

        sleep(SAVE_TIME)


def create_minerapi():
    """ Creates miners.json file """
    while True:
        memory_datab.execute("DELETE FROM Miners")
        memory.commit()

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

        sleep(SAVE_TIME)

        # with open("miners.json", 'w') as outfile:
        # json.dump(
        # minerapi.copy(),
        # outfile,
        # indent=1,
        # ensure_ascii=False
        # )


def protocol_login(data, connection):
    """ Check if user password matches to the one stored
        in the database, returns bool as login state """
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
                send_data("OK", connection)
                return True

            try:
                if checkpw(password, stored_password):
                    send_data("OK", connection)
                    return True

                else:
                    send_data("NO,Invalid password",
                              connection)
                    return False
            except:
                if checkpw(password, stored_password.encode('utf-8')):
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
            #admin_print("Sent registration email to " + email)
            return True
    except Exception as e:
        #admin_print("Error sending registration email:", e)
        return False


def protocol_register(data, connection, address):
    """ Register a new user, return on error """
    username = str(data[1])
    unhashed_pass = str(data[2]).encode('utf-8')
    email = str(data[3]).replace("REGI", "")

    ip = address[0].replace("::ffff:", "")

    """ Do some basic checks """
    if not match(r"^[A-Za-z0-9_-]*$", username):
        send_data("NO,Unallowed characters used", connection)
        return

    if len(username) > 64 or len(unhashed_pass) > 128 or len(email) > 64:
        send_data("NO,Data too long", connection)
        return

    if user_exists(username):
        send_data("NO,This username is already registered", connection)
        return

    if not "@" in email or not "." in email:
        send_data("NO,Incorrect e-mail address", connection)
        return

    if email_exists(email):
        send_data("NO,This e-mail address was already used", connection)
        return

    try:
        password = hashpw(unhashed_pass, gensalt(rounds=BCRYPT_ROUNDS))
    except Exception as e:
        send_data("NO,Bcrypt error: " + str(e), connection)
        return

    if send_registration_email(username, email):
        """ Register a new account if  the registration
            e-mail was sent sucessfully """
        registrations[ip] = 1
        try:
            with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute(
                    """INSERT INTO Users
                    (username, password, email, balance)
                    VALUES(?, ?, ?, ?)""",
                    (username, password, email, .0))
                conn.commit()
                send_data("OK", connection)
                return
        except Exception as e:
            send_data("NO,Database error: " + str(e), connection)
            return
    else:
        send_data("NO,Error sending verification e-mail", connection)
        return


def protocol_send_funds(data, connection, username):
    """ Transfer funds from one account to another """
    try:
        global_last_block_hash_cp = global_last_block_hash
        memo = sub(r'[^A-Za-z0-9 .()-:/!#_+-]+', ' ', str(data[1]))
        recipient = str(data[2])
        amount = float(data[3])

        if memo == "-" or memo == "":
            memo = "None"

        if str(recipient) in jail:
            send_data("NO,Can\'t send funds to that user", connection)
            return

        if str(username) in jail:
            send_data("NO,BONK - go to duco jail", connection)
            return

        if str(recipient) == str(username):
            send_data("NO,You\'re sending funds to yourself", connection)
            return

        if not user_exists(recipient):
            send_data("NO,Recipient doesn\'t exist", connection)
            return

        while True:
            try:
                with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (username,))
                    balance = float(datab.fetchone()[3])
                    break
            except:
                pass

        if (str(amount) == ""
            or float(balance) <= float(amount)
                or float(amount) <= 0):
            send_data("NO,Incorrect amount", connection)
            return

        if float(balance) >= float(amount):
            while True:
                try:
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
                        break
                except:
                    pass

            while True:
                try:
                    with sqlconn(CONFIG_TRANSACTIONS,
                                 timeout=DB_TIMEOUT) as conn:
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
                        send_data(
                            "OK,Successfully transferred funds,"
                            + str(global_last_block_hash_cp),
                            connection)
                        break
                except:
                    pass
            return
    except Exception as e:
        admin_print("Error sending funds from " + username
                    + " to " + recipient + ": " + str(e))
        send_data(
            "NO,Internal server error: "
            + str(e),
            connection)
        return


def protocol_get_balance(data, connection, username):
    """ Sends balance of user to the client
        raises an exception on error """
    try:
        with sqlconn(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                FROM Users
                WHERE username = ?""",
                          (username,))
            balance = str(datab.fetchone()[3])
            send_data(round(float(balance), DECIMALS), connection)
    except Exception as e:
        send_data("NO,Internal server error: "+str(e))
        raise Exception(e)


def protocol_change_pass(data, connection, username):
    """ Changes password of user """
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
        admin_print("Error changing password:", e)
        send_data("NO,Internal server error: " + str(e), connection)


def get_duco_prices():
    global duco_price
    global duco_price_nodes
    global duco_price_justswap
    while True:
        """ Gets XMG price price from Coingecko """
        coingecko_api = requests.get(
            "https://api.coingecko.com/"
            + "api/v3/simple/"
            + "price?ids=magi&vs_currencies=usd",
            data=None)
        if coingecko_api.status_code == 200:
            coingecko_content = json.loads(coingecko_api.content.decode())
            xmg_usd = float(coingecko_content["magi"]["usd"])
        else:
            xmg_usd = .03
        """ Calculate DUCO price by the guaranteed 10:1 exchange rate
            in the DUCO Exchange """
        duco_price = round(xmg_usd * 0.25, 8)

        """ Gets DUCO price from the Node-S exchange """
        node_api = requests.get(
            "http://www.node-s.co.za/"
            + "api/v1/duco/exchange_rate",
            data=None)
        if node_api.status_code == 200:
            node_content = json.loads(node_api.content.decode())
            duco_price_nodes = round(float(node_content["value"]), 8)
        else:
            duco_price_nodes = 0

        """ Gets wDUCO price from JustSwap exchange """
        justswap_api = requests.get(
            "https://apilist.tronscan.org/"
            + "api/account?address="
            + "TRAoFeB7n8Tt4nZGTRB8La4UP4i84bsoMh",
            data=None)
        if justswap_api.status_code == 200:
            justswap_content = json.loads(justswap_api.content.decode())
            # Converts values back to floats
            trxBal = int(justswap_content["tokens"][0]["balance"]) / 100000
            wducoBal = int(justswap_content["tokens"][2]["balance"]) / 100000
            # JustSwap pool exchange rate is TRC bal divided by wDUCO bal
            exchange_rate = trxBal / wducoBal

            # Get current TRX price
            tronscan_api = requests.get(
                "https://apilist.tronscan.org/"
                + "api/token/price?token=trx",
                data=None)
            if tronscan_api.status_code == 200:
                tronscan_content = json.loads(tronscan_api.content.decode())
                trx_price = tronscan_content["price_in_usd"]
            else:
                trx_price = 0.03

            duco_price_justswap = round(
                float(exchange_rate) * float(trx_price), 8
            )
        else:
            duco_price_justswap = 0
        sleep(360)


def protocol_get_transactions(data, connection):
    """ Sends last transactions involving username
        raises an exception on error """
    try:
        username = data[1]
        transaction_count = int(data[2])
        transactiondata = {}
        if transaction_count > 15:
            transaction_count = 15
        with sqlconn(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT * FROM Transactions")
            for row in datab.fetchall():
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
        send_data("NO,Internal server error: "+str(e), connection)
        raise Exception("Error getting transactions")


def handle(connection, address):
    """ Handler for every client """
    global global_blocks
    global global_last_block_hash
    logged_in = False

    ip_addr = address[0].replace("::ffff:", "")
    if ip_addr == "127.0.0.1":
        connection.settimeout(1600)
    else:
        connection.settimeout(15)

    try:
        """ Send server version """
        send_data(SERVER_VER, connection)

        try:
            connections_per_ip[ip_addr] += 1
        except Exception:
            connections_per_ip[ip_addr] = 1

        while True:
            sleep(0)
            # Wait until client sends data
            data = receive_data(connection)

            if not data:
                break

            if data[0] == "LOGI":
                """ Client requested authentication """
                logged_in = protocol_login(data, connection)
                if logged_in:
                    username = data[1]
                    if username in banlist:
                        if not username in whitelisted_usernames:
                            perm_ban(ip_addr)
                        sleep(5)
                        break
                else:
                    break

            # MINING FUNCTIONS

            elif data[0] == "JOB":
                """ Client requested the DUCO-S1 mining protocol,
                    it's not our job so we pass him to the
                    DUCO-S1 job handler """
                thread_id = protocol_mine(data, connection, address)
                username = data[1]

            elif data[0] == "JOBXX":
                """ Same situation as above, just use the XXHASH switch """
                thread_id = protocol_mine(
                    data, connection, address, using_xxhash=True)
                username = data[1]

            # USER FUNCTIONS

            elif data[0] == "BALA":
                """ Client requested balance check """
                if logged_in:
                    protocol_get_balance(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)

            elif data[0] == "ESTP":
                """ Client requested estimate profit check
                    check def database_updater to see where this data comes from """
                try:
                    send_data(
                        str(mean(estimated_profits[data[1]][-100:])*17280),
                        connection)
                except Exception as e:
                    send_data(str(e), connection)

            elif data[0] == "UEXI":
                """ Client requested to check wheter user is registered """
                if user_exists(data[1]):
                    send_data("OK,User is registered", connection)
                else:
                    send_data("NO,User is not registered", connection)

            elif data[0] == "REGI":
                """ Client requested registation """
                protocol_register(data, connection, address)

            elif data[0] == "CHGP":
                """ Client requested password change """
                if logged_in:
                    protocol_change_pass(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "GTXL":
                """ Client requested transaction list """
                protocol_get_transactions(data, connection)

            elif data[0] == "SEND":
                """ Client requested funds transfer """
                if logged_in:
                    protocol_send_funds(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)
                    break

            elif data[0] == "PING":
                """ Client requested a ping response """
                send_data("Pong!", connection)

            elif data[0] == "MOTD":
                """ Client requested to send him the MOTD """
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

            elif data[0] == "POOLList":
                PF.PoolList(connection=connection)

            elif data[0] == "PoolLogin":
                POOLCLASS = PF.Pool_Function_class(connection=connection)
                POOLCLASS.login(data=data)

            elif data[0] == "PoolSync":
                blocks_to_add = POOLCLASS.sync(data, global_blocks)
                global_blocks += blocks_to_add

            elif data[0] == "PoolPreSync":
                sync_data = POOLCLASS.pre_sync(connection)
                blocks_to_add = POOLCLASS.sync(sync_data, global_blocks)
                global_blocks += blocks_to_add

            elif data[0] == "PoolLogout":
                POOLCLASS = PF.Pool_Function_class(connection=connection)
                POOLCLASS.logout(data=data)

            elif data[0] == "PoolLoginAdd":
                PF.PoolLoginAdd(connection=connection,
                                data=data,
                                PoolPassword=PoolPassword)

            elif data[0] == "PoolLoginRemove":
                PF.PoolLoginRemove(connection=connection,
                                   data=data,
                                   PoolPassword=PoolPassword)
            else:
                break

            sleep(0)

    except Exception:
        pass
        # print(traceback.format_exc())
    finally:
        # print("Closing socket")
        try:
            minerapi.pop(thread_id)
        except:
            pass

        try:
            connections_per_ip[ip_addr] -= 1
            if connections_per_ip[ip_addr] <= 0:
                connections_per_ip.pop(ip_addr)
        except:
            pass

        try:
            workers[ip_addr] -= 1
            if workers[ip_addr] <= 0:
                workers.pop(ip_addr)
        except:
            pass

        connection.close()

        return False


def countips():
    """ Check if someone is making more than
        n connections in a peroid of n seconds,
        if so - ban the IP - easy anti-ddos system """
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
    """ Reset connections per IP values every n sec """
    while True:
        sleep(30)
        connections_per_ip.clear()


def duino_stats_restart_handle():
    while True:
        if ospath.isfile("config/restart_signal"):
            os.remove("config/restart_signal")
            admin_print("Server restarted by Duino-Stats command")
            #os.system('sudo iptables -F INPUT')
            os.execl(sys.executable, sys.executable, *sys.argv)
        sleep(3)


if __name__ == "__main__":
    # Read banned usernames
    with open(CONFIG_BANS, "r") as bannedusrfile:
        bannedusr = bannedusrfile.read().splitlines()
        for username in bannedusr:
            banlist.append(username)
        admin_print("Loaded banned usernames file")

    # Read whitelisted IPs
    with open(CONFIG_WHITELIST, "r") as whitelistfile:
        whitelisted = whitelistfile.read().splitlines()
        for ip in whitelisted:
            whitelisted_ips.append(socket.gethostbyname(str(ip)))
        admin_print("Loaded whitelisted IPs file")

    # Read whitelisted usernames
    with open(CONFIG_WHITELIST_USR, "r") as whitelistusrfile:
        whitelistedusr = whitelistusrfile.read().splitlines()
        for username in whitelistedusr:
            whitelisted_usernames.append(username)
        admin_print("Loaded whitelisted usernames file")

    """ In-memory db for minerapi """
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

    # Duino-Coin server libraries
    import pool_functions as PF
    from kolka_module import *
    from server_functions import *
    from kolka_chip_module import *
    from wrapped_duco_functions import *

    admin_print("Duino-Coin Master Server is starting")
    admin_print("Launching background threads")
    threading.Thread(target=create_backup).start()

    # threading.Thread(target=countips).start()
    # threading.Thread(target=resetips).start()

    threading.Thread(target=duino_stats_restart_handle).start()
    threading.Thread(target=get_duco_prices).start()
    threading.Thread(target=get_sys_usage).start()

    threading.Thread(target=update_job_tiers).start()
    threading.Thread(target=create_jobs).start()
    threading.Thread(target=database_updater).start()

    threading.Thread(target=create_main_api_file).start()
    threading.Thread(target=create_minerapi).start()
    threading.Thread(target=create_secondary_api_files).start()

    try:
        def _server_w():
            server_thread_wallet = StreamServer(
                (HOSTNAME, WALLET_PORT),
                handle,
                backlog=BACKLOG,
                spawn=Pool(POOL_SIZE))
            admin_print("Wallet server is running")
            server_thread_wallet.serve_forever()
        threading.Thread(target=_server_w).start()

        def _server_p():
            server_thread_pc = StreamServer(
                (HOSTNAME, PC_PORT),
                handle,
                backlog=BACKLOG,
                spawn=Pool(POOL_SIZE))
            admin_print("PC server is running")
            server_thread_pc.serve_forever()
        threading.Thread(target=_server_p).start()

        def _server_a():
            server_thread_arduino = StreamServer(
                (HOSTNAME, AVR_PORT),
                handle,
                backlog=BACKLOG,
                spawn=Pool(POOL_SIZE))
            admin_print("AVR server is running")
            server_thread_arduino.serve_forever()
        threading.Thread(target=_server_a).start()

        def _server_e():
            server_thread_esp = StreamServer(
                (HOSTNAME, ESP_PORT),
                handle,
                backlog=BACKLOG,
                spawn=Pool(POOL_SIZE))
            admin_print("ESP server is running")
            server_thread_esp.serve_forever()
        threading.Thread(target=_server_e).start()

        def _server_l():
            server_thread = StreamServer((HOSTNAME, LEGACY_PORT),
                                         handle,
                                         backlog=BACKLOG,
                                         spawn=Pool(POOL_SIZE))
            admin_print("Legacy server is running")
            server_thread.serve_forever()
        threading.Thread(target=_server_l).start()

        input_management()
    except Exception as e:
        admin_print("Unexpected exception", e)
    finally:
        admin_print("Master Server is exiting")
        os.execl(sys.executable, sys.executable, *sys.argv)
