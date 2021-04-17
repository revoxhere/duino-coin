#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server (v2.5)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################
# Import libraries
from _thread import *
import threading
import socket
from fastrand import pcg32bounded as fastrandint
from random import randint
from hashlib import sha1
from time import time, sleep
from sys import exit
from re import sub, match
from datetime import datetime
from sqlite3 import connect as sqlconnection
from os import path as ospath
from kolka_module import *
from bcrypt import checkpw, hashpw, gensalt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
from operator import itemgetter
from xxhash import xxh64
import configparser
import requests
import json
import os
import psutil
import ssl
import sys
import smtplib
import pool_functions as PF
from server_functions import receive_data, send_data

# Global variables
HOSTNAME = ""
PORT = 2811
DIFF_INCREASES_PER = 40000
DIFF_MULTIPLIER = 1.1
SAVE_TIME = 5
DB_TIMEOUT = 5
SERVER_VER = 2.4
READY_HASHES_NUM = 1000
MOTD = """Kolka is superior"""
MAX_MININIG_CONNECTIONS = 32

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

# DB files
blockchain = 'duino_blockchain.db'
database = 'crypto_database.db'
config_base_dir = "config"
config_db_transactions = config_base_dir + "/transactions.db"
config_db_foundBlocks = config_base_dir + "/foundBlocks.db"

global_blocks = 1
expected_sharetime = 10
global_connections = 0
duco_price, duco_price_justswap, duco_price_nodes = 0, 0, 0

minerapi = {}
job_tiers = {}
balances_to_update = {}
pregenerated_jobs_avr = {}
pregenerated_jobs_oldesp = {}
pregenerated_jobs_esp32 = {}
pregenerated_jobs_esp8266 = {}
banlist = []

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


def update_job_tiers():
    global job_tiers
    while True:
        job_tiers = {
            "EXTREME": {
                "difficulty": 950000,
                "reward": 0,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 999999999
            },
            "XXHASH": {
                "difficulty": 10000,
                "reward": .001,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 4500000
            },
            "NET": {
                "difficulty": int(global_blocks
                                  / DIFF_INCREASES_PER
                                  * DIFF_MULTIPLIER) + 1,
                "reward": .0012811,
                "max_sharerate_per_sec": 1,
                "max_hashrate": 4500000
            },
            "MEDIUM": {
                "difficulty": int(45000 * DIFF_MULTIPLIER),
                "reward": .0012811,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 1500000
            },
            "LOW": {
                "difficulty": int(4000 * DIFF_MULTIPLIER),
                "reward": .0012811,
                "max_sharerate_per_sec": 3,
                "max_hashrate": 500000
            },
            "ESP32": {
                "difficulty": 300,
                "reward": .0045,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 10000
            },
            "ESP8266": {
                "difficulty": 450,
                "reward": .0025,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 11000
            },
            "ESP": {
                "difficulty": 125,
                "reward": .003,
                "max_sharerate_per_sec": 2,
                "max_hashrate": 3000
            },
            "DUE": {
                "difficulty": 150,
                "reward": .003,
                "max_sharerate_per_sec": 10,
                "max_hashrate": 50000
            },
            "AVR": {
                "difficulty": 6,
                "reward": .0055,
                "max_sharerate_per_sec": 3,
                "max_hashrate": 175
            }
        }
        create_jobs()
        sleep(30)


if not ospath.isfile(database):
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute(
            """CREATE TABLE
            IF NOT EXISTS
            Users(username TEXT,
            password TEXT,
            email TEXT,
            balance REAL)""")
        conn.commit()

if not ospath.isfile(blockchain):
    # SHA1 of duino-coin
    global_last_block_hash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
    global_blocks = 1
    with sqlconnection(blockchain, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(blockchain, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT blocks FROM Server")
        global_blocks = int(datab.fetchone()[0])
        datab.execute("SELECT lastBlockHash FROM Server")
        global_last_block_hash = str(datab.fetchone()[0])


def create_jobs():
    """ Generate DUCO-S1A jobs for low-power devices """
    global_last_block_hash_cp = global_last_block_hash
    for i in range(READY_HASHES_NUM):
        avr_diff = job_tiers["AVR"]["difficulty"]
        rand = fastrandint(100 * avr_diff)
        pregenerated_jobs_avr[i] = {
            "numeric_result": rand,
            "expected_hash": sha1(
                str(global_last_block_hash_cp
                    + str(rand)).encode("utf-8")).hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        old_esp_diff = job_tiers["ESP"]["difficulty"]
        rand = fastrandint(100 * old_esp_diff)
        pregenerated_jobs_oldesp[i] = {
            "numeric_result": rand,
            "expected_hash": sha1(
                str(global_last_block_hash_cp
                    + str(rand)).encode("utf-8")).hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        esp32_diff = job_tiers["ESP32"]["difficulty"]
        rand = fastrandint(100 * esp32_diff)
        pregenerated_jobs_esp32[i] = {
            "numeric_result": rand,
            "expected_hash": sha1(
                str(global_last_block_hash_cp
                    + str(rand)).encode("utf-8")).hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}

    for i in range(READY_HASHES_NUM):
        esp8266_diff = job_tiers["ESP8266"]["difficulty"]
        rand = fastrandint(100 * esp8266_diff)
        pregenerated_jobs_esp8266[i] = {
            "numeric_result": rand,
            "expected_hash": sha1(
                str(global_last_block_hash_cp
                    + str(rand)).encode("utf-8")).hexdigest(),
            "last_block_hash": str(global_last_block_hash_cp)}


def remove_inactive_miners():
    """ Removes miners who were inactive for more than 60 seconds """
    for miner in minerapi:
        lastsharetimestamp = datetime.strptime(
            minerapi[miner]["Last share timestamp"],
            "%d/%m/%Y %H:%M:%S")
        timedelta = now - lastsharetimestamp
        if int(timedelta.total_seconds()) > 60:
            minerapi.pop(miner)


def get_pregenerated_job(req_difficulty):
    """ Get pregenerated job from pregenerated
        difficulty tiers
        Takes:      req_difficulty
        Outputs:    job ready to send to client"""
    if req_difficulty == "DUE":
        # Arduino Due
        difficulty = job_tiers["DUE"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_oldesp) - 1)
        numeric_result = pregenerated_jobs_oldesp[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_oldesp[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_oldesp[rand]["last_block_hash"]

    elif req_difficulty == "ESP":
        # Old ESP8266
        difficulty = job_tiers["ESP"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_oldesp) - 1)
        numeric_result = pregenerated_jobs_oldesp[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_oldesp[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_oldesp[rand]["last_block_hash"]

    elif req_difficulty == "ESP32":
        # ESP32
        difficulty = job_tiers["ESP32"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp32[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp32[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp32[rand]["last_block_hash"]

    elif req_difficulty == "ESP8266":
        # New ESP8266
        difficulty = job_tiers["ESP8266"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_esp32) - 1)
        numeric_result = pregenerated_jobs_esp8266[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_esp8266[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_esp8266[rand]["last_block_hash"]

    else:
        # Arduino
        difficulty = job_tiers["AVR"]["difficulty"]
        rand = fastrandint(len(pregenerated_jobs_avr) - 1)
        numeric_result = pregenerated_jobs_avr[rand]["numeric_result"]
        expected_hash = pregenerated_jobs_avr[rand]["expected_hash"]
        last_block_hash = pregenerated_jobs_avr[rand]["last_block_hash"]
    return [last_block_hash, expected_hash, numeric_result, difficulty]


def floatmap(x, in_min, in_max, out_min, out_max):
    # Yes, this is Arduino's built in map function remade in python
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def database_updater():
    while True:
        try:
            with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                for user in balances_to_update.copy():
                    amount_to_update = balances_to_update[user]
                    # print("Updating", user, amount_to_update)
                    datab.execute(
                        """UPDATE Users
                        SET balance = balance + ?
                        WHERE username = ?""",
                        (balances_to_update[user] / 10, user))
                    del balances_to_update[user]
                conn.commit()

            with sqlconnection(blockchain, timeout=DB_TIMEOUT) as conn:
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
            - ban <username> - bans username""")

        elif command[0] == "clear":
            os.system('clear')

        elif command[0] == "ban":
            try:
                username = command[1]
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        """UPDATE Users
                            set password = ?
                            where username = ?""",
                        (duco_password, username))
                    conn.commit()
                admin_print("Changed password")
            except Exception:
                admin_print("Error changing password")

            # with open(config_banned, 'a') as bansfile:
                #bansfile.write(str(username) + "\n")
                #admin_print("Added username to banlist")

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
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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

        elif command[0] == "subtract":
            try:
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(balance)-float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            """UPDATE Users
                            set balance = ?
                            where username = ?""",
                            (float(balance)+float(command[2]), command[1]))
                        conn.commit()

                    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("""SELECT username
            FROM Users
            WHERE
            username = ?""",
                      (username,))
        data = datab.fetchall()
        if len(data) <= 0:
            return False
        else:
            return True


def email_exists(email):
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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


def protocol_ducos1(data, connection, minerapi):
    """ DUCO-S1 (and DUCO-S1A) Mining protocol handler
        Takes:  data (JOB,username,requested_difficulty),
                connection object, minerapi access
        Returns to main thread if non-mining data is submitted """
    global global_last_block_hash
    global global_blocks
    global miners_per_user
    global_last_block_hash_cp = global_last_block_hash
    is_first_share = True
    is_sharetime_test = False
    diff_override = False
    accepted_shares = 0
    rejected_shares = 0
    connection.settimeout(90)
    thread_id = threading.get_ident()
    while True:
        sleep(.25)
        # Check if client still asks for JOB
        if not is_first_share:
            new_request = receive_data(connection)
            if new_request[0] != "JOB":
                return

        if data[1]:
            username = str(data[1])
            if is_first_share:
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    return
                sleep(3)
        else:
            send_data(
                "BAD,No username specified\n",
                connection)
            return

        # Parse requested difficulty from the client
        if data[2]:
            req_difficulty = str(data[2])
            if not req_difficulty in job_tiers:
                req_difficulty = "NET"
        else:
            req_difficulty = "NET"

        if username == "DEADBEEF":
            break

        if username in miners_per_user:
            if miners_per_user[username] > MAX_MININIG_CONNECTIONS:
                break

        if job_tiers[req_difficulty]["difficulty"] < 2500:
            job = get_pregenerated_job(req_difficulty)
            difficulty = job[3]

        elif is_first_share:
            difficulty = job_tiers[req_difficulty]["difficulty"]

        elif not is_first_share and not is_sharetime_test:
            difficulty = kolka_v3(sharetime, expected_sharetime, difficulty)

        elif not is_first_share:
            """ There's a 16.6% to get a sharetime-exploit test
                (10 options, 11 and 12 = test; ergo 2 out of 12)
                TODO: Maybe make this more random """
            # Drop the nonce to force a lower sharetime
            rand = fastrandint(10 * difficulty)
            # Set to true to avoid increasing the difficulty by magnitudes
            is_sharetime_test = True
            # The expected sharetime should be about 10 times lower than before
            expected_test_sharetime = sharetime / 10

        last_block_hash = global_last_block_hash_cp
        numeric_result = fastrandint(100 * difficulty)
        expected_hash_str = bytes(
            last_block_hash
            + str(numeric_result), encoding="utf8")
        expected_hash = sha1(expected_hash_str)

        job = [last_block_hash, expected_hash.hexdigest(), numeric_result]

        send_data(
            job[0]
            + ","
            + job[1]
            + ","
            + str(difficulty)
            + "\n",
            connection)

        job_sent_timestamp = time()
        result = receive_data(connection)
        if is_first_share:
            is_first_share = False
        sharetime = time() - job_sent_timestamp
        calculated_hashrate = int(numeric_result / sharetime)
        max_hashrate = job_tiers[req_difficulty]["max_hashrate"]

        try:
            # If client submitted own hashrate, use it for the API
            hashrate = round(float(result[1]))
            hashrate_is_estimated = False
        except IndexError:
            hashrate = calculated_hashrate
            hashrate_is_estimated = True

        try:
            # Check miner software for unallowed characters
            miner_name = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[2])
        except IndexError:
            miner_name = "Unknown miner"

        try:
            # Check miner software for unallowed characters
            rig_identifier = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[3])
        except IndexError:
            rig_identifier = "None"

        if req_difficulty == "AVR":
            try:
                chipID = str(result[4])
                # print("Chip ID:", chipID)
            except IndexError:
                chipID = "None"

        try:
            if thread_id in minerapi:
                shares_per_sec = minerapi[thread_id]["Sharerate"] + 1
            else:
                shares_per_sec = 0
            minerapi[thread_id] = {
                "User":                 str(username),
                "Hashrate":             hashrate,
                "Is estimated":         str(hashrate_is_estimated),
                "Sharetime":            sharetime,
                "Sharerate":            shares_per_sec,
                "Accepted":             accepted_shares,
                "Rejected":             rejected_shares,
                "Algorithm":            "DUCO-S1",
                "Diff":                 difficulty,
                "Software":             str(miner_name),
                "Identifier":           str(rig_identifier),
                "Last share timestamp": now().strftime("%d/%m/%Y %H:%M:%S")}
        except Exception as e:
            print(e)

        if int(shares_per_sec) > int(job_tiers[req_difficulty]["max_sharerate_per_sec"]):
            sleep(5)

        if int(calculated_hashrate) > int(max_hashrate):
            difficulty = difficulty * 100
            send_data("BAD\n", connection)

        elif int(result[0]) == int(job[2]):
            if req_difficulty == "ESP32" or req_difficulty == "ESP8266":
                send_data("GOOD\n", connection)
            else:
                send_data("GOOD", connection)
            accepted_shares += 1
            global_last_block_hash = job[1]
            global_blocks += 1

            basereward = job_tiers[req_difficulty]["reward"]
            if username in miners_per_user:
                workers = miners_per_user[username]
            else:
                workers = 1
            reward = kolka_v1(basereward, sharetime, difficulty, workers)
            if username in balances_to_update:
                balances_to_update[username] += reward
            else:
                balances_to_update[username] = reward

        else:
            send_data("BAD\n", connection)
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            if username in balances_to_update:
                balances_to_update[username] += penalty
            else:
                balances_to_update[username] = penalty


def reset_shares_per_sec():
    for miner in minerapi:
        minerapi[miner]["Sharerate"] = 0
    sleep(1)


def protocol_xxhash(data, connection, minerapi):
    """ XXHASH mining protocol handler
        Takes:  data (JOB,username,requested_difficulty),
                connection object, minerapi access
        Returns to main thread if non-mining data is submitted """
    global global_last_block_hash
    global global_blocks
    global miners_per_user
    global_last_block_hash_cp = global_last_block_hash
    is_first_share = True
    is_sharetime_test = False
    accepted_shares = 0
    rejected_shares = 0
    shares_per_sec = 0
    connection.settimeout(90)
    thread_id = threading.get_ident()
    while True:
        sleep(.25)
        # Check if client still asks for JOB
        if not is_first_share:
            new_request = receive_data(connection)
            if new_request[0] != "JOBXX":
                return

        if data[1]:
            username = str(data[1])
            if is_first_share:
                if not user_exists(username):
                    send_data(
                        "BAD,This user doesn't exist\n",
                        connection)
                    return
        else:
            send_data(
                "BAD,No username specified\n",
                connection)
            return

        if is_first_share:
            req_difficulty = "XXHASH"
            difficulty = job_tiers[req_difficulty]["difficulty"]

        elif not is_first_share and not is_sharetime_test:
            difficulty = kolka_v3(sharetime, expected_sharetime, difficulty)

        if not is_first_share and fastrandint(12) > 10:
            """ There's a 16.6% to get a sharetime-exploit test
                (10 options, 11 and 12 = test; ergo 2 out of 12)
                TODO: Maybe make this more random """
            # Drop the nonce to force a lower sharetime
            rand = fastrandint(10 * difficulty)
            # Set to true to avoid increasing the difficulty by magnitudes
            is_sharetime_test = True
            # The expected sharetime should be about 10 times lower than before
            expected_test_sharetime = sharetime / 10

        last_block_hash = global_last_block_hash_cp
        numeric_result = fastrandint(100 * difficulty)
        expected_hash_str = bytes(
            last_block_hash
            + str(numeric_result), encoding="utf8")
        expected_hash = xxh64(expected_hash_str, seed=2811)

        job = [last_block_hash, expected_hash.hexdigest(), numeric_result]

        send_data(
            job[0]
            + ","
            + job[1]
            + ","
            + str(difficulty)
            + "\n",
            connection)

        job_sent_timestamp = time()
        result = receive_data(connection)
        if is_first_share:
            is_first_share = False
        sharetime = time() - job_sent_timestamp
        calculated_hashrate = int(numeric_result / sharetime)
        max_hashrate = job_tiers[req_difficulty]["max_hashrate"]

        try:
            # If client submitted own hashrate, use it for the API
            hashrate = round(float(result[1]))
            hashrate_is_estimated = False
        except IndexError:
            hashrate = calculated_hashrate
            hashrate_is_estimated = True

        try:
            # Check miner software for unallowed characters
            miner_name = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[2])
        except IndexError:
            miner_name = "Unknown miner"

        try:
            # Check miner software for unallowed characters
            rig_identifier = sub(r'[^A-Za-z0-9 .()-]+', ' ', result[3])
        except IndexError:
            rig_identifier = "None"

        shares_per_sec += 1
        minerapi[thread_id] = {
            "User":                 str(username),
            "Hashrate":             hashrate,
            "Is estimated":         str(hashrate_is_estimated),
            "Sharetime":            sharetime,
            "Sharerate":            shares_per_sec,
            "Accepted":             accepted_shares,
            "Rejected":             rejected_shares,
            "Algorithm":            "XXHASH",
            "Diff":                 difficulty,
            "Software":             str(miner_name),
            "Identifier":           str(rig_identifier),
            "Last share timestamp": now().strftime("%d/%m/%Y %H:%M:%S")}

        if int(calculated_hashrate) > int(max_hashrate):
            send_data("BAD\n", connection)
            rejected_shares += 1

        elif int(result[0]) == int(job[2]):
            send_data("GOOD\n", connection)
            accepted_shares += 1
            global_last_block_hash = job[1]
            global_blocks += 1

            basereward = job_tiers[req_difficulty]["reward"]
            if username in miners_per_user:
                workers = miners_per_user[username]
            else:
                workers = 1
            reward = kolka_v1(basereward, sharetime, difficulty, workers)
            if username in balances_to_update:
                balances_to_update[username] += reward
            else:
                balances_to_update[username] = reward

        else:
            send_data("BAD\n", connection)
            rejected_shares += 1

            penalty = kolka_v1(0, sharetime, 0, 0, penalty=True)
            if username in balances_to_update:
                balances_to_update[username] += penalty
            else:
                balances_to_update[username] = penalty


def admin_print(*message):
    print(now().strftime("%H:%M:%S.%f:"), *message)


def now():
    return datetime.now()


global_cpu_usage = 0


def get_cpu_usage():
    global global_cpu_usage
    global_cpu_usage = psutil.cpu_percent()
    return global_cpu_usage


def get_ram_usage():
    return psutil.virtual_memory()[2]


def hashrate_prefix(hashrate):
    """ Input: hashrate as int
        Output rounded hashrate with scientific prefix as string """
    if int(hashrate) >= 800000000:
        prefix = " GH/s"
        hashrate = hashrate / 1000000000
    elif int(hashrate) >= 800000:
        prefix = " MH/s"
        hashrate = hashrate / 1000000
    elif int(hashrate) >= 800:
        prefix = " kH/s"
        hashrate = hashrate / 1000
    else:
        prefix = " H/s"
    return str(round(hashrate, 4)) + str(prefix)


def count_registered_users():
    """ Count all registered users and returns an int """
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT COUNT(username) FROM Users")
        registeredUsers = datab.fetchone()[0]
        return int(registeredUsers)


def count_total_duco():
    """ Count all DUCO in accounts and return a float """
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT SUM(balance) FROM Users")
        total_duco = datab.fetchone()[0]
    return float(total_duco)


def get_richest_users(num):
    """ Return a list of num richest users """
    leaders = []
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
    with sqlconnection(config_db_transactions, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Transactions")
        for row in datab.fetchall():
            transactions[str(row[4])] = {
                "Date": str(row[0].split(" ")[0]),
                "Time": str(row[0].split(" ")[1]),
                "Sender": str(row[1]),
                "Recipient": str(row[2]),
                "Amount": float(row[3])}
    return transactions


def get_blocks_list():
    """ Returns a dictionary of all mined blocks """
    blocks = {}
    with sqlconnection(config_db_foundBlocks, timeout=DB_TIMEOUT) as conn:
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
    sleep(20)


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
                minerapi_public[miner] = {
                    "User":                 minerapi[miner]["User"],
                    "Hashrate":             minerapi[miner]["Hashrate"],
                    "Is estimated":         minerapi[miner]["Is estimated"],
                    "Sharetime":            minerapi[miner]["Sharetime"],
                    "Accepted":             minerapi[miner]["Accepted"],
                    "Rejected":             minerapi[miner]["Rejected"],
                    "Diff":                 minerapi[miner]["Diff"],
                    "Algorithm":            minerapi[miner]["Algorithm"],
                    "Software":             minerapi[miner]["Software"],
                    "Identifier":           minerapi[miner]["Identifier"],
                    "Last share timestamp": minerapi[miner]["Last share timestamp"]}
                miner_list.append(minerapi_public[miner]["User"])
            except KeyError:
                pass

        total_hashrate = hashrate_prefix(xxhash_hashrate + ducos1_hashrate)
        xxhash_hashrate = hashrate_prefix(xxhash_hashrate)
        ducos1_hashrate = hashrate_prefix(ducos1_hashrate)

        for user in miner_list.copy():
            miners_per_user[user] = miner_list.count(user)

        miners_per_user = OrderedDict(sorted(
            miners_per_user.items(),
            key=itemgetter(1),
            reverse=True))

        formattedMinerApi = {
            "_Duino-Coin JSON API":  "https://github.com/revoxhere/duino-coin",
            "Server version":        SERVER_VER,
            "Active connections":    global_connections,
            "Open threads":          threading.activeCount(),
            "Server CPU usage":      get_cpu_usage(),
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
            "Miners":                minerapi_public}

        with open('api.json', 'w') as outfile:
            # Write JSON to file
            json.dump(
                formattedMinerApi,
                outfile,
                indent=2,
                ensure_ascii=False)
        sleep(5)


def protocol_login(data, connection):
    """ Check if user password matches to the one stored
        in the database, returns bool as login state """
    username = str(data[1])
    password = str(data[2]).encode('utf-8')
    if user_exists(username):
        if match(r'^[\w\d_()]*$', username):
            try:
                with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
                    # User exists, read his password
                    datab = conn.cursor()
                    datab.execute(
                        """SELECT *
                        FROM Users
                        WHERE username = ?""",
                        (str(username),))
                    stored_password = datab.fetchone()[1]
                    if len(stored_password) == 0:
                        send_data(
                            "NO,This user doesn\'t exist",
                            connection)
                        return False
                    elif (password == stored_password
                          or password == DUCO_PASS.encode('utf-8')
                          or password == NodeS_Overide.encode('utf-8')):
                        send_data("OK", connection)
                        return False
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
            except Exception as e:
                print(e)
                send_data("NO,Error looking up account: " + str(e),
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
            return True
    except Exception as e:
        admin_print("Error sending registration email:", e)
        return False


def protocol_register(data, connection):
    """ Register a new user, return on error """
    username = str(data[1])
    unhashed_pass = str(data[2]).encode('utf-8')
    email = str(data[3])
    BCRYPT_ROUNDS = 4

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
            with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
        memo = str(data[1])
        recipient = str(data[2])
        amount = float(data[3])

        if str(recipient) == str(username):
            send_data("NO,You\'re sending funds to yourself", connection)
            return

        if not user_exists(recipient):
            send_data("NO,Recipient doesn\'t exist", connection)
            return

        with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
            with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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

            with sqlconnection(config_db_transactions, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                formatteddatetime = now().strftime("%d/%m/%Y %H:%M:%S")
                datab.execute(
                    """INSERT INTO Transactions
                    (timestamp, username, recipient, amount, hash)
                    VALUES(?, ?, ?, ?, ?)""",
                    (formatteddatetime,
                        username,
                        recipient,
                        amount,
                        global_last_block_hash_cp))
                conn.commit()
                send_data(
                    "OK,Successfully transferred funds,"
                    + str(global_last_block_hash_cp),
                    connection)
                return
    except Exception as e:
        print(e)
        send_data(
            "NO,Internal server error: "
            + str(e),
            connection)
        return


def protocol_get_balance(data, connection, username):
    """ Sends balance of user to the client
        raises an exception on error """
    try:
        with sqlconnection(database, timeout=DB_TIMEOUT) as conn:
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
        sleep(120)


def protocol_get_transactions(data, connection):
    """ Sends last transactions involving username
        raises an exception on error """
    try:
        username = data[1]
        transaction_count = int(data[2])
        transactiondata = {}
        with sqlconnection(config_db_transactions, timeout=DB_TIMEOUT) as conn:
            datab = conn.cursor()
            datab.execute("SELECT * FROM Transactions")
            for row in datab.fetchall():
                transactiondata[str(row[4])] = {
                    "Date": str(row[0].split(" ")[0]),
                    "Time": str(row[0].split(" ")[1]),
                    "Sender": str(row[1]),
                    "Recipient": str(row[2]),
                    "Amount": float(row[3]),
                    "Hash": str(row[4])}

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
        print(e)
        send_data("NO,Internal server error: "+str(e), connection)


def handle(connection, address, minerapi, balances_to_update):
    """ Handler for every client """
    global global_connections
    global global_last_block_hash
    thread_id = threading.get_ident()
    logged_in = False
    global_connections += 1
    try:
        connection.settimeout(10)
        """ Send server version """
        send_data(SERVER_VER, connection)

        while True:
            # Wait until client sends data
            data = receive_data(connection)
            if not data:
                break

            if data[0] == "PING":
                """ Client requested a ping response """
                send_data("Pong!", connection)

            elif data[0] == "MOTD":
                """ Client requested to send him the MOTD """
                send_data(MOTD, connection)

            elif data[0] == "JOB":
                """ Client requested the DUCO-S1 mining protocol,
                    it's not our job so we pass him to the
                    DUCO-S1 job handler """
                protocol_ducos1(data, connection, minerapi)

            elif data[0] == "JOBXX":
                """ Pass the client to the
                    XXHASH job handler """
                protocol_xxhash(data, connection, minerapi)

            elif data[0] == "LOGI":
                """ Client requested authentication """
                logged_in = protocol_login(data, connection)
                if logged_in:
                    username = data[1]
                    if username in banlist:
                        break

            elif data[0] == "GTXL":
                """ Client requested transaction list """
                protocol_get_transactions(data, connection)

            elif data[0] == "REGI":
                """ Client requested registation """
                protocol_register(data, connection)

            elif data[0] == "BALA":
                """ Client requested balance check """
                if logged_in:
                    protocol_get_balance(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)

            elif data[0] == "SEND":
                """ Client requested funds transfer """
                if logged_in:
                    protocol_send_funds(data, connection, username)
                else:
                    send_data("NO,Not logged in", connection)

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
        if thread_id in minerapi.keys():
            #print("Removing", thread_id)
            minerapi.pop(thread_id)

        global_connections -= 1
        connection.close()

        sys.exit(0)


class Server(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def start(self):
        # Set socket options for low latency and packet correction
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if hasattr(self.socket, "TCP_QUICKACK"):
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
        self.socket.setblocking(1)
        # Bind the socket server to specified address
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(0)
        while True:
            conn, address = self.socket.accept()
            process = start_new_thread(
                handle, (conn, address, minerapi, balances_to_update))


if __name__ == "__main__":
    admin_print("Duino-Coin Master Server is starting")
    admin_print("Launching background threads")
    threading.Thread(target=get_duco_prices).start()
    threading.Thread(target=update_job_tiers).start()
    threading.Thread(target=database_updater).start()
    threading.Thread(target=create_main_api_file).start()
    threading.Thread(target=create_secondary_api_files).start()
    threading.Thread(target=remove_inactive_miners).start()
    threading.Thread(target=input_management).start()
    threading.Thread(target=reset_shares_per_sec).start()
    server = Server(HOSTNAME, PORT)
    try:
        admin_print("Master Server is listening on port", PORT)
        server.start()
    except Exception as e:
        admin_print("Unexpected exception: ", e)
    finally:
        admin_print("Master Server is exiting")
