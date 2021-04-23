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
import json
import os
import psutil
import ssl
import sys
import smtplib
import traceback
from random import randint
from hashlib import sha1
from time import time, sleep
from sys import exit
from re import sub, match
from sqlite3 import connect as sqlconnection
from os import path as ospath
from kolka_module import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
from operator import itemgetter
# Duino-Coin server libraries
import pool_functions as PF
from server_functions import receive_data, send_data
# python3 -m pip install bcrypt
from bcrypt import checkpw, hashpw, gensalt
# python3 -m pip install fastrand
from fastrand import pcg32bounded as fastrandint
# python3 -m pip install gevent
import gevent
from gevent.server import StreamServer
# python3 -m pip install xxhash
from xxhash import xxh64
# python3 -m pip install shutil
from shutil import copyfile
# python3 -m pip install udatetime
import udatetime as utime

# Global variables
HOSTNAME = ""
PORT = 2811
DIFF_INCREASES_PER = 5000
DIFF_MULTIPLIER = 1.1
SAVE_TIME = 5
DB_TIMEOUT = 5
SERVER_VER = 2.4
READY_HASHES_NUM = 1000
MOTD = """Kolka is superior"""
MAX_MININIG_CONNECTIONS = 16
BLOCK_PROBABILITY = 1000000
BLOCK_REWARD = 7.7
UPDATE_MINERAPI_EVERY = 5
EXPECTED_SHARETIME = 10
BCRYPT_ROUNDS = 8
# DB files
DATABASE = 'crypto_database.db'
BLOCKCHAIN = 'duino_blockchain.db'
CONFIG_BASE_DIR = "config"
CONFIG_TRANSACTIONS = CONFIG_BASE_DIR + "/transactions.db"
CONFIG_BLOCKS = CONFIG_BASE_DIR + "/foundBlocks.db"
CONFIG_BANS = CONFIG_BASE_DIR + "/banned.txt"
CONFIG_WHITELIST = CONFIG_BASE_DIR + "/whitelisted.txt"
CONFIG_WHITELIST_USR = CONFIG_BASE_DIR + "/whitelistedUsernames.txt"

config = configparser.ConfigParser()
try:  # Read sensitive data from config file
    config.read('AdminData.ini')
    DUCO_EMAIL = config["main"]["duco_email"]
    DUCO_PASS = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    PoolPassword = config["main"]["PoolPassword"]
    wrapper_private_key = config["main"]["wrapper_private_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
except Exception as e:
    print("""Please create AdminData.ini config file first:
        [main]
        duco_email = ???
        duco_password = ???
        NodeS_Overide = ???
        PoolPassword = ???
        wrapper_private_key = ???
        NodeS_Username = ???""")
    exit()


global_blocks = 1
global_connections = 0
duco_price, duco_price_justswap, duco_price_nodes = 0, 0, 0
global_cpu_usage = 100
minerapi = {}
job_tiers = {}
balances_to_update = {}
pregenerated_jobs_avr = {}
pregenerated_jobs_due = {}
pregenerated_jobs_esp32 = {}
pregenerated_jobs_esp8266 = {}
banlist = []
whitelisted_usernames = []
whitelisted_ips = []
ip_list = {}
miners_per_user = {}
chip_ids = []


# Read banned usernames
with open(CONFIG_BANS, "r") as bannedusrfile:
    bannedusr = bannedusrfile.read().splitlines()
    for username in bannedusr:
        banlist.append(username)
    print("Loaded banned usernames file")

# Read whitelisted IPs
with open(CONFIG_WHITELIST, "r") as whitelistfile:
    whitelisted = whitelistfile.read().splitlines()
    for ip in whitelisted:
        whitelisted_ips.append(socket.gethostbyname(str(ip)))
    print("Loaded whitelisted IPs file")

# Read whitelisted usernames
with open(CONFIG_WHITELIST_USR, "r") as whitelistusrfile:
    whitelistedusr = whitelistusrfile.read().splitlines()
    for username in whitelistedusr:
        whitelisted_usernames.append(username)
    print("Loaded whitelisted usernames file")


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


def create_backup():
    """ Creates a backup folder every day """
    if not ospath.isdir('backups/'):
        os.mkdir('backups/')

    while True:
        today = datetime.date.today()
        if not ospath.isdir('backups/'+str(today)+'/'):
            os.mkdir('backups/'+str(today))
            copyfile(BLOCKCHAIN, "backups/"+str(today)+"/"+BLOCKCHAIN)
            copyfile(DATABASE, "backups/"+str(today)+"/"+DATABASE)
            sleep(5)
            with open("prices.txt", "a") as pricesfile:
                pricesfile.write("," + str(duco_price).rstrip("\n"))
            with open("pricesNodeS.txt", "a") as pricesNodeSfile:
                pricesNodeSfile.write(
                    "," + str(duco_price_nodes).rstrip("\n"))
            with open("pricesJustSwap.txt", "a") as pricesJustSwapfile:
                pricesJustSwapfile.write(
                    "," + str(duco_price_justswap).rstrip("\n"))
            admin_print("Backup finished")
        # Run every 6h
        sleep(3600*6)


def unbanip(ip):
    """ Unbans an IP """
    try:
        os.system("sudo iptables -D INPUT -s "
                  + str(ip)
                  + " -j DROP > /dev/null 2>&1")
    except Exception:
        pass


def permanent_ban(ip):
    """ Bans as IP """
    if (ip == "51.15.127.80"
        or ip == "wallet.duinocoin.com"
            or ip == "34.233.38.119"):
        pass
    else:
        os.system("sudo iptables -I INPUT -s "
                  + str(ip)
                  + " -j DROP")
        #ip_list.pop(ip)


def temporary_ban(ip):
    """ Temporarily bans IP """
    if (ip == "51.15.127.80"
        or ip == "wallet.duinocoin.com"
            or ip == "34.233.38.119"):
        pass
    else:
        os.system("sudo iptables -I INPUT -s "
                  + str(ip)
                  + " -j DROP")
        # Start auto-unban thread for this IP
        threading.Timer(120.0, unbanip, [ip]).start()
        #ip_list.pop(ip)


def countips():
    """ Counts connections per IP """
    while True:
        for ip in ip_list.copy():
            try:
                if ip_list[ip] > MAX_MININIG_CONNECTIONS*2:
                    if not ip in whitelisted_ips:
                        temporary_ban(ip)
            except Exception as e:
                print(e)
        sleep(7)


def resetips():
    """ Reset connections counter """
    while True:
        sleep(30)
        ip_list.clear()


def update_job_tiers():
    global job_tiers
    while True:
        job_tiers = {
            "EXTREME": {
                "difficulty": 950000,
                "reward": 0,
                "max_hashrate": 999999999
            },
            "XXHASH": {
                "difficulty": 50000,
                "reward": .0003,
                "max_hashrate": 4500000
            },
            "NET": {
                "difficulty": int(global_blocks
                                  / DIFF_INCREASES_PER
                                  * DIFF_MULTIPLIER) + 1,
                "reward": .0012811,
                "max_hashrate": 1000000
            },
            "MEDIUM": {
                "difficulty": int(50000 * DIFF_MULTIPLIER),
                "reward": .0012811,
                "max_hashrate": 500000
            },
            "LOW": {
                "difficulty": int(5000 * DIFF_MULTIPLIER),
                "reward": .0012811,
                "max_hashrate": 200000
            },
            "ESP32": {
                "difficulty": 500,
                "reward": .005,
                "max_hashrate": 13000
            },
            "ESP8266": {
                "difficulty": 500,
                "reward": .0035,
                "max_hashrate": 11000
            },
            "DUE": {
                "difficulty": 150,
                "reward": .0025,
                "max_hashrate": 50000
            },
            "AVR": {
                "difficulty": 4,
                "reward": .0045,
                "max_hashrate": 180
            }
        }
        create_jobs()
        sleep(30)


if not os.path.isfile(CONFIG_TRANSACTIONS):
    with sqlconnection(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT blocks FROM Server")
        global_blocks = int(datab.fetchone()[0])
        datab.execute("SELECT lastBlockHash FROM Server")
        global_last_block_hash = str(datab.fetchone()[0])


def create_jobs():
    """ Generate DUCO-S1A jobs for low-power devices """
    global_last_block_hash_cp = global_last_block_hash
    base_hash = sha1(global_last_block_hash_cp.encode('ascii'))
    temp_hash = None
    for i in range(READY_HASHES_NUM):
        temp_hash = base_hash.copy()
        avr_diff = job_tiers["AVR"]["difficulty"]
        rand = randint(0, 100 * avr_diff)
        temp_hash.update(str(rand).encode('ascii'))
        pregenerated_jobs_avr[i] = {
            "numeric_result": rand,
            "expected_hash": temp_hash.hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        temp_hash = base_hash.copy()
        due_diff = job_tiers["DUE"]["difficulty"]
        rand = randint(0, 100 * avr_diff)
        temp_hash.update(str(rand).encode('ascii'))
        pregenerated_jobs_due[i] = {
            "numeric_result": rand,
            "expected_hash": temp_hash.hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        temp_hash = base_hash.copy()
        esp32_diff = job_tiers["ESP32"]["difficulty"]
        rand = randint(0, 100 * esp32_diff)
        temp_hash.update(str(rand).encode('ascii'))
        pregenerated_jobs_esp32[i] = {
            "numeric_result": rand,
            "expected_hash": temp_hash.hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        temp_hash = base_hash.copy()
        esp8266_diff = job_tiers["ESP8266"]["difficulty"]
        rand = randint(0, 100 * esp8266_diff)
        temp_hash.update(str(rand).encode('ascii'))
        pregenerated_jobs_esp8266[i] = {
            "numeric_result": rand,
            "expected_hash": temp_hash.hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}


def get_pregenerated_job(req_difficulty):
    """ Get pregenerated job from pregenerated
        difficulty tiers
        Takes:      req_difficulty
        Outputs:    job ready to send to client"""
    if req_difficulty == "DUE":
        # Arduino Due
        difficulty = job_tiers["DUE"]["difficulty"]
        rand = randint(0, len(pregenerated_jobs_due) - 1)
        numeric_result = pregenerated_jobs_due[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_due[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_due[rand]["last_block_hash"]

    elif req_difficulty == "ESP32":
        # ESP32
        difficulty = job_tiers["ESP32"]["difficulty"]
        rand = randint(0, len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp32[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp32[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp32[rand]["last_block_hash"]

    elif req_difficulty == "ESP8266":
        # New ESP8266
        difficulty = job_tiers["ESP8266"]["difficulty"]
        rand = randint(0, len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp8266[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp8266[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp8266[rand]["last_block_hash"]

    else:
        # Arduino
        difficulty = job_tiers["AVR"]["difficulty"]
        rand = randint(0, len(pregenerated_jobs_avr) - 1)
        numeric_result = pregenerated_jobs_avr[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_avr[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_avr[rand]["last_block_hash"]
    return [last_block_hash, expected_hash, numeric_result, difficulty]


def floatmap(x, in_min, in_max, out_min, out_max):
    # Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def database_updater():
    while True:
        try:
            with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                for user in balances_to_update.copy():
                    amount_to_update = balances_to_update[user]
                    if amount_to_update > 0.0009:
                        amount_to_update = 0.0009
                    # print("Updating", user, amount_to_update)
                    datab.execute(
                        """UPDATE Users
                        SET balance = balance + ?
                        WHERE username = ?""",
                        (balances_to_update[user] / 50, user))
                    del balances_to_update[user]
                conn.commit()

            with sqlconnection(BLOCKCHAIN, timeout=DB_TIMEOUT) as conn:
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
        sleep(SAVE_TIME)


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
            - ban <username> - bans username""")

        elif command[0] == "clear":
            os.system('clear')

        elif command[0] == "ban":
            try:
                username = command[1]
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """UPDATE Users
                            set password = ?
                            where username = ?""",
                        (DUCO_PASS, username))
                    conn.commit()
                admin_print("Changed password")
            except Exception as e:
                admin_print("Error changing password: "+str(e))

            with open(CONFIG_BANS, 'a') as bansfile:
                bansfile.write(str(username) + "\n")
                admin_print("Added username to banlist")

            try:
                banlist.append(str(username))
                admin_print("Added username to blocked usernames")
            except Exception:
                admin_print("Error adding username to blocked usernames")

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
                os.system("sudo iptables -F INPUT")
                os.system('clear')
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                admin_print("Canceled")

        elif command[0] == "balance":
            try:
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    hashed_pass = hashpw(
                        command[2], gensalt(rounds=BCRYPT_ROUNDS))
                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set password = ?
                            where username = ?""",
                            (str(hashed_pass), command[1]))
                        conn.commit()
                        admin_print("Changed password of user " +
                                    str(command[1]))
                else:
                    admin_print("Canceled")
            except Exception as e:
                admin_print("Error: " + str(e))

        elif command[0] == "subtract":
            try:
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(balance)-float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")

        elif command[0] == "add":
            try:
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(balance)+float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
            except Exception:
                admin_print(
                    "User doesn't exist or you've entered wrong number")


def user_exists(username):
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
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
    sleeptime = floatmap(global_cpu_usage, 0, 100, 0, upper_limit)
    sleep(sleeptime)


def create_share_ducos1(last_block_hash, difficulty):
    """ Creates and returns a job for DUCO-S1 algo """
    try:
        numeric_result = randint(0, 100 * difficulty)
        expected_hash_str = bytes(
            str(last_block_hash)
            + str(numeric_result), encoding="utf8")
        expected_hash = sha1(expected_hash_str)
        job = [last_block_hash, expected_hash.hexdigest(), numeric_result]
        return job
    except Exception as e:
        print("DUCOS1 ERR:", e)


def create_share_xxhash(last_block_hash, difficulty):
    """ Creates and returns a job for XXHASH algo """
    try:
        numeric_result = randint(0, 100 * difficulty)
        expected_hash_str = bytes(
            str(last_block_hash)
            + str(numeric_result), encoding="utf8")
        expected_hash = xxh64(expected_hash_str, seed=2811)
        job = [last_block_hash, expected_hash.hexdigest(), numeric_result]
        return job
    except Exception as e:
        print("XXHASH ERR:", e)


def protocol_ducos1(data, connection, address):
    """ DUCO-S1 (and DUCO-S1A) Mining protocol handler
        Takes:  data (JOB,username,requested_difficulty),
                connection object, minerapi access
        Returns to main thread if non-mining data is submitted """
    global global_last_block_hash
    global global_blocks
    global miners_per_user

    accepted_shares, rejected_shares = 0, 0
    global_last_block_hash_cp = global_last_block_hash
    thread_miner_api = {}
    is_first_share = True
    thread_id = id(gevent.getcurrent())
    override_difficulty = ""

    connection.settimeout(60)
    while True:
        if is_first_share:
            try:
                username = str(data[1])
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    raise Exception("Incorrect username")
            except:
                send_data(
                    "BAD,Not enough data\n",
                    connection)
                raise Exception("Incorrect username")

            if username in banlist:
                permanent_ban(ip)
                raise Exception("User banned")

            try:
                # Parse starting difficulty from the client
                req_difficulty = str(data[2])
                if not req_difficulty in job_tiers:
                    req_difficulty = "NET"
            except:
                req_difficulty = "NET"
        else:
            data = receive_data(connection)

            if override_difficulty:
                req_difficulty = override_difficulty
            else:
                req_difficulty = data[2]

        if job_tiers[req_difficulty]["difficulty"] < 2500:
            job = get_pregenerated_job(req_difficulty)
            difficulty = job[3]

        elif is_first_share:
            try:
                difficulty = job_tiers[req_difficulty]["difficulty"]
            except:
                difficulty = "NET"

        else:
            difficulty = kolka_v3(
                sharetime, EXPECTED_SHARETIME, difficulty)

        # if not is_first_share:
            # """ There's a 16.6% to get a sharetime-exploit test
            #    (10 options, 11 and 12 = test; ergo 2 out of 12)
            #    TODO: Maybe make this more random """
            # Drop the nonce to force a lower sharetime
            #rand = fastrandint(10 * difficulty)
            # Set to true to avoid increasing the difficulty by magnitudes
            #is_sharetime_test = True
            # The expected sharetime should be about 10 times lower than before
            #expected_test_sharetime = sharetime / 10

        job = create_share_ducos1(global_last_block_hash_cp, difficulty)
        send_data(job[0] + "," + job[1] + "," + str(difficulty) + "\n",
                  connection)

        max_hashrate = job_tiers[req_difficulty]["max_hashrate"]
        numeric_result = job[2]

        job_sent_timestamp = utime.now()
        result = receive_data(connection)
        sharetime = (utime.now() - job_sent_timestamp).total_seconds()
        calculated_hashrate = int(numeric_result // sharetime)

        is_first_share = False
        #try:
            # If client submitted own hashrate, use it for the API
            #hashrate = float(result[1])
            #hashrate_is_estimated = False
        #except:
        hashrate = calculated_hashrate
        hashrate_is_estimated = False

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

        # if req_difficulty == "AVR":
        #     try:
        #         chipID = str(result[4])
        #         #chip_ids.append(chipID)
        #         # print("Chip ID:", chipID)
        #     except IndexError:
        #         chipID = "None"

        if accepted_shares % UPDATE_MINERAPI_EVERY == 0:
            thread_miner_api = {
                "User":         str(username),
                "Hashrate":     hashrate,
                "Is estimated": hashrate_is_estimated,
                "Sharetime":    sharetime,
                "Accepted":     accepted_shares,
                "Rejected":     rejected_shares,
                "Algorithm":    "DUCO-S1",
                "Diff":         difficulty,
                "Software":     str(miner_name),
                "Identifier":   str(rig_identifier)
            }
            minerapi[thread_id] = thread_miner_api

        if accepted_shares % UPDATE_MINERAPI_EVERY*2 == 0:
            global_blocks += UPDATE_MINERAPI_EVERY*2
            global_last_block_hash = job[1]

        if calculated_hashrate > max_hashrate:
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            try:
                balances_to_update[username] += penalty
            except:
                balances_to_update[username] = penalty

            override_difficulty = kolka_v2(req_difficulty, job_tiers)

            send_data("BAD\n", connection)

        elif int(result[0]) == job[2]:
            accepted_shares += 1

            try:
                workers = miners_per_user[username]
            except:
                workers = 1

            basereward = job_tiers[req_difficulty]["reward"]
            reward = kolka_v1(basereward, sharetime, difficulty, workers)

            try:
                balances_to_update[username] += reward
            except:
                balances_to_update[username] = reward

            if randint(0, BLOCK_PROBABILITY) == 1:
                reward = generate_block(
                    username, reward, job[1], connection)
                send_data("BLOCK\n", connection)
            else:
                send_data("GOOD\n", connection)

        else:
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            try:
                balances_to_update[username] += penalty
            except:
                balances_to_update[username] = penalty

            send_data("BAD\n", connection)


def protocol_xxhash(data, connection, address):
    """ XXHASH mining protocol handler
        Takes:  data (JOB,username,requested_difficulty),
                connection object, minerapi access
        Returns to main thread if non-mining data is submitted """
    global global_last_block_hash
    global global_blocks

    accepted_shares, rejected_shares = 0, 0
    global_last_block_hash_cp = global_last_block_hash
    thread_miner_api = {}
    is_first_share = True
    thread_id = id(gevent.getcurrent())
    override_difficulty = ""
    connection.settimeout(60)

    while True:
        if is_first_share:
            try:
                username = str(data[1])
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    raise Exception("Incorrect username")
            except Exception as e:
                print("Incorrect username:", e)
                send_data(
                    "BAD,Not enough data\n",
                    connection)
                    raise Exception("Incorrect username")

            if username in banlist:
                permanent_ban(ip)
                    raise Exception("User banned")

            req_difficulty = "NET"
        else:
            data = receive_data(connection)

            if override_difficulty:
                req_difficulty = override_difficulty
            else:
                req_difficulty = data[2]

        if is_first_share:
            difficulty = job_tiers["NET"]["difficulty"]

        else:
            difficulty = kolka_v3(
                sharetime, EXPECTED_SHARETIME, difficulty)

        job = create_share_xxhash(global_last_block_hash_cp, difficulty)
        send_data(str(job[0]) + "," + str(job[1]) + "," + str(difficulty) + "\n",
                  connection)

        max_hashrate = job_tiers[req_difficulty]["max_hashrate"]
        numeric_result = job[2]

        job_sent_timestamp = utime.now()
        result = receive_data(connection)
        sharetime = (utime.now() - job_sent_timestamp).total_seconds()
        calculated_hashrate = int(numeric_result / sharetime)

        is_first_share = False
        hashrate = calculated_hashrate
        hashrate_is_estimated = False

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

        if accepted_shares % UPDATE_MINERAPI_EVERY == 0:
            thread_miner_api = {
                "User":         str(username),
                "Hashrate":     hashrate,
                "Is estimated": hashrate_is_estimated,
                "Sharetime":    sharetime,
                "Accepted":     accepted_shares,
                "Rejected":     rejected_shares,
                "Algorithm":    "XXHASH",
                "Diff":         difficulty,
                "Software":     str(miner_name),
                "Identifier":   str(rig_identifier)
            }
            minerapi[thread_id] = thread_miner_api

        if accepted_shares % UPDATE_MINERAPI_EVERY*2 == 0:
            global_blocks += UPDATE_MINERAPI_EVERY*2
            global_last_block_hash = job[1]

        if calculated_hashrate > max_hashrate:
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            try:
                balances_to_update[username] += penalty
            except:
                balances_to_update[username] = penalty

            override_difficulty = kolka_v2(req_difficulty, job_tiers)

            send_data("BAD\n", connection)

        elif int(result[0]) == job[2]:
            accepted_shares += 1

            try:
                workers = miners_per_user[username]
            except:
                workers = 1

            basereward = job_tiers[req_difficulty]["reward"]
            reward = kolka_v1(basereward, sharetime, difficulty, workers)

            try:
                balances_to_update[username] += reward
            except:
                balances_to_update[username] = reward

            if randint(0, BLOCK_PROBABILITY) == 1:
                reward = generate_block(
                    username, reward, job[1], connection)
                send_data("BLOCK\n", connection)
            else:
                send_data("GOOD\n", connection)

        else:
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            try:
                balances_to_update[username] += penalty
            except:
                balances_to_update[username] = penalty

            send_data("BAD\n", connection)


def admin_print(*message):
    print(now().strftime("%H:%M:%S.%f:"), *message)


def now():
    return utime.now()


def get_cpu_usage():
    global global_cpu_usage
    while True:
        global_cpu_usage = psutil.cpu_percent()
        sleep(1)


def get_ram_usage():
    return psutil.virtual_memory()[2]


def hashrate_prefix(hashrate:int, accuracy:int):
    """ Input: hashrate as int
        Output rounded hashrate with scientific prefix as string """
    if hashrate >= 800000000:
        prefix = " GH/s"
        hashrate = hashrate / 1000000000
    elif hashrate >= 800000:
        prefix = " MH/s"
        hashrate = hashrate / 1000000
    elif hashrate >= 800:
        prefix = " kH/s"
        hashrate = hashrate / 1000
    else:
        prefix = " H/s"
    return str(round(hashrate, accuracy)) + str(prefix)


def count_registered_users():
    """ Count all registered users and returns an int """
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT COUNT(username) FROM Users")
        registeredUsers = datab.fetchone()[0]
        return int(registeredUsers)


def count_total_duco():
    """ Count all DUCO in accounts and return a float """
    try:
        with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT SUM(balance) FROM Users")
            total_duco = datab.fetchone()[0]
        return float(total_duco)
    except:
        return 0


def get_richest_users(num):
    """ Return a list of num richest users """
    leaders = []
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Users ORDER BY balance DESC")
        i = 0
        for row in datab.fetchall():
            leaders.append(
                str(round((float(row[3])), 4)) + " DUCO - " + row[0])
            i += 1
            if i > num:
                break
    return(leaders[:num])


def get_balance_list():
    """ Returns a dictionary of balances of all users """
    balances = {}
    with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
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
                "Memo":      str(row[5])}
    return transactions


def get_blocks_list():
    """ Returns a dictionary of all mined blocks """
    blocks = {}
    with sqlconnection(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Blocks")
        for row in datab.fetchall():
            blocks[row[3]] = {
                "Date": str(row[0].split(" ")[0]),
                "Time": str(row[0].split(" ")[1]),
                "Finder": str(row[1]),
                "Amount generated": float(row[2])}
    return blocks


def create_secondary_api_files():
    while True:
        with open('transactions.json', 'w') as outfile:
            json.dump(
                get_transaction_list(),
                outfile,
                indent=2,
                ensure_ascii=False)
        with open('foundBlocks.json', 'w') as outfile:
            json.dump(
                get_blocks_list(),
                outfile,
                indent=2,
                ensure_ascii=False)
        with open('balances.json', 'w') as outfile:
            json.dump(
                get_balance_list(),
                outfile,
                indent=2,
                ensure_ascii=False)
        sleep(15)


def create_main_api_file():
    """ Creates api.json file
        this will sooner or later be replaced with a RESTful flask api """
    while True:
        global miners_per_user
        ducos1_hashrate, xxhash_hashrate = 0, 0
        minerapi_public, miners_per_user = {}, {}
        miner_list = []
        for miner in minerapi.copy():
            try:
                # Add user hashrate to the server hashrate
                if minerapi[miner]["Algorithm"] == "DUCO-S1":
                    ducos1_hashrate += float(minerapi[miner]["Hashrate"])
                elif minerapi[miner]["Algorithm"] == "XXHASH":
                    xxhash_hashrate += float(minerapi[miner]["Hashrate"])
                miner_list.append(minerapi[miner]["User"])
            except KeyError:
                pass

        total_hashrate = hashrate_prefix(int(xxhash_hashrate + ducos1_hashrate), 4)
        xxhash_hashrate = hashrate_prefix(int(xxhash_hashrate), 1)
        ducos1_hashrate = hashrate_prefix(int(ducos1_hashrate), 1)

        for user in miner_list:
            miners_per_user[user] = miner_list.count(user)

        miners_per_user = OrderedDict(sorted(
            miners_per_user.items(),
            key=itemgetter(1),
            reverse=True))

        server_api = {
            "_Duino-Coin JSON API":  "https://github.com/revoxhere/duino-coin",
            "Server version":        SERVER_VER,
            "Active connections":    global_connections,
            "Open threads":          threading.activeCount(),
            "Server CPU usage":      global_cpu_usage,
            "Server RAM usage":      get_ram_usage(),
            "Last update":           str(now().strftime("%d/%m/%Y %H:%M:%S (UTC)")),
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
            "Top 10 richest miners": get_richest_users(10),
            "Active workers":        miners_per_user,
            "Miners":                "server.duinocoin.com/miners.json"}

        with open('api.json', 'w') as outfile:
            # Write JSON to file
            json.dump(
                server_api,
                outfile,
                indent=2,
                ensure_ascii=False)
        sleep(5)


def create_minerapi():
    while True:
        with open('miners.json', 'w') as outfile:
            json.dump(
                minerapi.copy(),
                outfile,
                indent=2,
                ensure_ascii=False)
        sleep(10)


def protocol_login(data, connection):
    """ Check if user password matches to the one stored
        in the database, returns bool as login state """
    username = str(data[1])
    password = str(data[2]).encode('utf-8')
    if user_exists(username):
        if match(r"^[A-Za-z0-9_-]*$", username):
            try:
                with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                send_data(
                    "NO,This user doesn\'t exist",
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
            admin_print("Sent registration email to " + email)
            return True
    except Exception as e:
        admin_print("Error sending registration email:", e)
        return False


def protocol_register(data, connection):
    """ Register a new user, return on error """
    username = str(data[1])
    unhashed_pass = str(data[2]).encode('utf-8')
    email = str(data[3])

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
        try:
            with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
        memo = sub(r'[^A-Za-z0-9 .()-]+', ' ', str(data[1]))
        recipient = str(data[2])
        amount = float(data[3])

        if memo == "-" or memo == "":
            memo = "None"

        if str(recipient) == str(username):
            send_data("NO,You\'re sending funds to yourself", connection)
            return

        if not user_exists(recipient):
            send_data("NO,Recipient doesn\'t exist", connection)
            return

        with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute(
                """SELECT *
                FROM Users
                WHERE username = ?""",
                (username,))
            balance = float(datab.fetchone()[3])

        if (str(amount) == ""
            or float(balance) <= float(amount)
                or float(amount) <= 0):
            send_data("NO,Incorrect amount", connection)
            return

        if float(balance) >= float(amount):
            with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
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
                    (f'{float(recipientbal):.20f}', recipient))
                conn.commit()

            with sqlconnection(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
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
        with sqlconnection(DATABASE, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("""SELECT *
                FROM Users
                WHERE username = ?""",
                          (username,))
            balance = str(datab.fetchone()[3])
            send_data(f'{float(balance):.20f}', connection)
            return
    except Exception as e:
        print(e)
        send_data("NO,Internal server error: "+str(e))
        return


def get_duco_prices():
    global duco_price
    global duco_price_nodes
    global duco_price_justswap
    while True:
        """ Gets DUCO price price from Coingecko """
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
        duco_price = round(xmg_usd / 10, 8)

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
                + "api/token/price?token=trx").json()
            trx_price = tronscan_api["price_in_usd"]

            duco_price_justswap = round(
                float(exchange_rate) * float(trx_price), 8)
        else:
            duco_price_justswap = 0
        sleep(60*10)


def protocol_get_transactions(data, connection):
    """ Sends last transactions involving username
        raises an exception on error """
    try:
        username = data[1]
        transaction_count = int(data[2])
        transactiondata = {}
        with sqlconnection(CONFIG_TRANSACTIONS, timeout=DB_TIMEOUT) as conn:
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
                    "Memo":      str(row[5])}

        transactionsToReturn = {}
        i = 0
        for transaction in OrderedDict(reversed(list(transactiondata.items()))):
            if (transactiondata[transaction]["Recipient"] == username
                    or transactiondata[transaction]["Sender"] == username):
                transactionsToReturn[str(i)] = transactiondata[transaction]
                i += 1
                if i >= transaction_count:
                    break

        transactionsToReturnStr = str(transactionsToReturn)
        send_data(transactionsToReturnStr, connection)
    except Exception as e:
        admin_print("Error getting transactions: " + str(e))
        send_data("NO,Internal server error: "+str(e), connection)


def handle(connection, address):
    """ Handler for every client """
    global global_connections
    thread_id = id(gevent.getcurrent())
    logged_in = False
    global_connections += 1
    try:
        if (address[0] == "51.15.127.80"
            or address[0] == "wallet.duinocoin.com"
                or address[0] == "34.233.38.119"):
            connection.settimeout(60*20)
        else:
            connection.settimeout(20)
        """ Send server version """
        send_data(SERVER_VER, connection)

        while True:
            # Wait until client sends data
            data = receive_data(connection)
            if not data:
                break

            elif data[0] == "JOB":
                """ Client requested the DUCO-S1 mining protocol,
                    it's not our job so we pass him to the
                    DUCO-S1 job handler """
                protocol_ducos1(data, connection, address)

            elif data[0] == "JOBXX":
                """ Pass the client to the
                    XXHASH job handler """
                protocol_xxhash(data, connection, address)

            elif data[0] == "LOGI":
                """ Client requested authentication """
                logged_in = protocol_login(data, connection)
                if logged_in:
                    username = data[1]
                    if username in banlist:
                        temporary_ban(address[0])
                else:
                    break

            elif data[0] == "REGI":
                """ Client requested registation """
                protocol_register(data, connection)

            elif data[0] == "BALA":
                """ Client requested balance check """
                if logged_in:
                    protocol_get_balance(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)

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

            elif data[0] == "POOLList":
                PF.PoolList(connection=connection)

            elif data[0] == "PoolLogin":
                POOLCLASS = PF.Pool_Function_class(connection=connection)
                POOLCLASS.login(data=data)

            elif data[0] == "PoolSync":
                global_blocks = POOLCLASS.sync(
                    data=data, global_blocks=global_blocks)

            elif data[0] == "PoolLogout":
                POOLCLASS.logout(data=data)

            elif data[0] == "PoolLoginAdd":
                PF.PoolLoginAdd(connection=connection,
                                data=data, PoolPassword=PoolPassword)

            elif data[0] == "PoolLoginRemove":
                PF.PoolLoginRemove(connection=connection,
                                   data=data, PoolPassword=PoolPassword)

    except Exception as e:
        pass
        #print("Problem handling request: ", e)
    finally:
        #print("Closing socket")
        if thread_id in minerapi:
            del minerapi[thread_id]

        global_connections -= 1
        connection.close()
        return


if __name__ == "__main__":
    admin_print("Duino-Coin Master Server is starting")
    admin_print("Launching background threads")
    threading.Thread(target=countips).start()
    threading.Thread(target=resetips).start()

    threading.Thread(target=get_duco_prices).start()
    threading.Thread(target=update_job_tiers).start()

    threading.Thread(target=database_updater).start()
    threading.Thread(target=create_backup).start()
    threading.Thread(target=get_cpu_usage).start()

    threading.Thread(target=create_main_api_file).start()
    threading.Thread(target=create_secondary_api_files).start()
    threading.Thread(target=create_minerapi).start()

    threading.Thread(target=input_management).start()
    try:
        admin_print("Master Server is listening on port", PORT)
        server = StreamServer((HOSTNAME, PORT), handle)
        server.serve_forever()
    except Exception as e:
        admin_print("Unexpected exception: ", e)
    finally:
        admin_print("Master Server is exiting, connections:", global_connections)
        os.execl(sys.executable, sys.executable, *sys.argv)
