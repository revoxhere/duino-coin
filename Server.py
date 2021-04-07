#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server Remastered (v2.4)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################
import requests
import ast
import smtplib
import sys
import ssl
import socket
import re
import math
import random
import hashlib
import xxhash
import datetime
import requests
import smtplib
import ssl
import sqlite3
import bcrypt
import time
import os.path
import json
import logging
import threading
import configparser
import fastrand
import os
import psutil
import statistics
from _thread import *
from shutil import copyfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
from operator import itemgetter
import quickemailverification

# Server will use this as hostname to bind to (localhost on Windows, 0.0.0.0 on Linux in most cases)
host = ""
# Server will listen on this port (official server uses 2811)
port = 2811
# Server version which will be sent to the clients (official server uses latest release version number)
serverVersion = 2.3
PoolVersion = 0.1
# Difficulty will increase every x blocks (official server uses 5k)
diff_incrase_per = 5000
# Maximum number of clients using mining protocol per IP and username
max_mining_connections = 24
# Maximum number of logged-in clients per IP
max_login_connections = 28
# Maximum number of connections that haven't sent any data yet
max_unauthorized_connections = 28
# Number of pregenerated jobs for AVR, ESP and ESP32 diffs in mining section;
# used to massively reduce load on the server (official server uses 1000)
hashes_num = 1000
# Rewards
shares_per_sec_reset = 1
max_rejected_shares = 20
big_block_reward = 7.77
reward_multiplier = 0.77
higher_diffs_basereward = 0.0002811
expected_sharetime_sec = 7
big_block_probability = 1000000
# Database access times out after this many seconds (default: 5)
database_timeout = 5
socket_listen_num = 0
# Wheter to enable wDUCO wrapper
use_wrapper = True
wrapper_permission = False
config = configparser.ConfigParser()
lock = threading.Lock()

try:  # Read sensitive data from config file
    config.read('AdminData.ini')
    duco_email = config["main"]["duco_email"]
    duco_password = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    PoolPassword = config["main"]["PoolPassword"]
    wrapper_private_key = config["main"]["wrapper_private_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
    emailchecker_private_key = config["main"]["emailchecker_private_key"]
    client = quickemailverification.Client(
        str(emailchecker_private_key).replace("\n", ""))
except Exception:
    print("""Please create AdminData.ini config file first:
        [main]
        duco_email = ???
        duco_password = ???
        NodeS_Overide = ???
        PoolPassword = ???
        wrapper_private_key = ???
        NodeS_Username = ???
        emailchecker_private_key = ???""")
    exit()

# Registration email - text version
text = """\
Hi there!
Your e-mail address has been successfully verified and you are now registered on the Duino-Coin network!
We hope you'll have a great time using Duino-Coin.
If you have any difficulties there are a lot of guides on our website: https://duinocoin.com/getting-started
You can also join our Discord server: https://discord.gg/kvBkccy to chat, take part in giveaways, trade and get help from other Duino-Coin users.
Happy mining!
Sincerely, Duino-Coin Team"""

# Registration email - HTML version
html = """\
<html>
  <body>
    <img src="https://github.com/revoxhere/duino-coin/raw/master/Resources/ducobanner.png?raw=true" width="360px" height="auto"><br>
    <h3>Hi there!</h3>
    <h4>Your e-mail address has been successfully verified and you are now registered on the Duino-Coin network!</h4>
    <p>We hope you'll have a great time using Duino-Coin.<br>If you have any difficulties there are a lot of <a href="https://duinocoin.com/getting-started">guides on our website</a>.<br>
       You can also join our <a href="https://discord.gg/kvBkccy">Discord server</a> to chat, take part in giveaways, trade and get help from other Duino-Coin users.<br><br>
       Happy mining!<br>
       <italic>Sincerely, Duino-Coin Team</italic>
    </p>
  </body>
</html>
"""

# Ban email - text version
textBan = """\
Hi there!
We have noticed behavior on your account that does not comply with our terms of service.
Your account has been permanently banned.
Sincerely, Duino-Coin Team"""

# Ban email - HTML version
htmlBan = """\
<html>
  <body>
    <img src="https://github.com/revoxhere/duino-coin/raw/master/Resources/ducobanner.png?raw=true" width="360px" height="auto"><br>
    <h3>Hi there!</h3>
    <h4>We have noticed behavior on your account that does not comply with our <a href="https://github.com/revoxhere/duino-coin#terms-of-service">terms of service</a>.</h4>
    <p>Your account has been permanently banned.<br>
       <italic>Sincerely, Duino-Coin Team</italic>
    </p>
  </body>
</html>
"""

minerapi = {}
connections = {}
balancesToUpdate = {}
connectedUsers = 0
globalCpuUsage = 0
ducoPrice = 0.01
percarray = []
memarray = []
readyHashesAVR = {}
readyHashesESP = {}
readyHashesESP32 = {}

database = 'crypto_database.db'  # User data database location
if not os.path.isfile(database):
    # Create it if it doesn't exist
    with sqlite3.connect(database, timeout=database_timeout) as conn:
        datab = conn.cursor()
        datab.execute(
            '''CREATE TABLE IF NOT EXISTS Users(username TEXT, password TEXT, email TEXT, balance REAL)''')
        conn.commit()

blockchain = 'duino_blockchain.db'  # Blockchain database location
if not os.path.isfile(blockchain):
    # Create it if it doesn't exist
    with sqlite3.connect(blockchain, timeout=database_timeout) as blockconn:
        try:
            with open("config/lastblock", "r+") as lastblockfile:
                # If old database is found, read lastBlockHash from it
                lastBlockHash = lastblockfile.readline()
        except Exception:
            # First block - SHA1 of "duino-coin"
            lastBlockHash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d"
        try:
            with open("config/blocks", "r+") as blockfile:
                # If old database is found, read mined blocks amount from it
                blocks = blockfile.readline()
        except Exception:
            blocks = 1  # Start from 1
        blockdatab = blockconn.cursor()
        blockdatab.execute(
            '''CREATE TABLE IF NOT EXISTS Server(blocks REAL, lastBlockHash TEXT)''')
        blockdatab.execute(
            "INSERT INTO Server(blocks, lastBlockHash) VALUES(?, ?)", (blocks, lastBlockHash))
        blockconn.commit()
else:
    with sqlite3.connect(blockchain, timeout=database_timeout) as blockconn:
        blockdatab = blockconn.cursor()
        blockdatab.execute("SELECT blocks FROM Server")
        # Read amount of mined blocks
        blocks = int(blockdatab.fetchone()[0])
        blockdatab.execute("SELECT lastBlockHash FROM Server")
        # Read lastblock's hash
        lastBlockHash = str(blockdatab.fetchone()[0])

if not os.path.isfile("config/transactions.db"):
    # Create transactions database if it doesn't exist
    with sqlite3.connect("config/transactions.db", timeout=database_timeout) as conn:
        datab = conn.cursor()
        datab.execute(
            '''CREATE TABLE IF NOT EXISTS Transactions(timestamp TEXT, username TEXT, recipient TEXT, amount REAL, hash TEXT)''')
        conn.commit()

if not os.path.isfile("config/foundBlocks.db"):
    # Create transactions database if it doesn't exist
    with sqlite3.connect("config/foundBlocks.db", timeout=database_timeout) as conn:
        datab = conn.cursor()
        datab.execute(
            '''CREATE TABLE IF NOT EXISTS Blocks(timestamp TEXT, finder TEXT, amount REAL, hash TEXT)''')
        conn.commit()

if use_wrapper:
    import tronpy  # Tronpy isn't default installed, install it with "python3 -m pip install tronpy"
    from tronpy.keys import PrivateKey, PublicKey
    # Wrapper public key
    wrapper_public_key = PrivateKey(bytes.fromhex(
        wrapper_private_key)).public_key.to_base58check_address()
    tron = tronpy.Tron(network="mainnet")
    # wDUCO contract
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U")
    wrapper_permission = wduco.functions.checkWrapperStatus(wrapper_public_key)


def adminLog(messagetype, message):
    # TODO
    if messagetype != "bans":
        now = datetime.datetime.now()
        print(now.strftime("%H:%M:%S") + " " + message)


def createBackup():
    # Create backups folder if it doesn't exist
    if not os.path.isdir('backups/'):
        os.mkdir('backups/')

    while True:
        today = datetime.date.today()
        if not os.path.isdir('backups/'+str(today)+'/'):
            os.mkdir('backups/'+str(today))
            copyfile(blockchain, "backups/"+str(today)+"/"+blockchain)
            copyfile(database, "backups/"+str(today)+"/"+database)
            time.sleep(5)
            with open("prices.txt", "a") as pricesfile:
                pricesfile.write("," + str(ducoPrice).rstrip("\n"))
            with open("pricesNodeS.txt", "a") as pricesNodeSfile:
                pricesNodeSfile.write(
                    "," + str(getDucoPriceNodeS()).rstrip("\n"))
            with open("pricesJustSwap.txt", "a") as pricesJustSwapfile:
                pricesJustSwapfile.write(
                    "," + str(getDucoPriceJustSwap()).rstrip("\n"))
        # Run every 6h
        time.sleep(3600*6)
        adminLog("system", "Backup finished")


def getDucoPrice():
    # Calcualte DUCO price price from coingecko
    global ducoPrice
    while True:
        coingecko = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=magi&vs_currencies=usd", data=None)
        if coingecko.status_code == 200:
            geckocontent = coingecko.content.decode()
            geckocontentjson = json.loads(geckocontent)
            xmgusd = float(geckocontentjson["magi"]["usd"])
        else:
            xmgusd = .03
        # 1:10 (XMG:DUCO) exchange rate
        ducoPrice = round(float(xmgusd) / 10, 8)
        time.sleep(120)


def getDucoPriceNodeS():
    # Get DUCO price from Node-S exchange
    nodeS = requests.get(
        "http://www.node-s.co.za/api/v1/duco/exchange_rate", data=None)
    if nodeS.status_code == 200:
        nodeScontent = nodeS.content.decode()
        nodeScontentjson = json.loads(nodeScontent)
        ducousd = float(nodeScontentjson["value"])
    else:
        ducousd = .015
    return ducousd


def getDucoPriceJustSwap():
    # Get DUCO price from JustSwap exchange
    justswap = requests.get(
        "https://api.justswap.io/v2/allpairs?page_size=9000&page_num=2", data=None)
    if justswap.status_code == 200:
        justswapcontent = justswap.content.decode()
        justswapcontentjson = json.loads(justswapcontent)
        ducotrx = float(
            justswapcontentjson["data"]["0_TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U"]["price"])
    else:
        ducotrx = .25
    coingecko = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd", data=None)
    if coingecko.status_code == 200:
        geckocontent = coingecko.content.decode()
        geckocontentjson = json.loads(geckocontent)
        trxusd = float(geckocontentjson["tron"]["usd"])
    else:
        trxusd = .05
    ducousd = round(ducotrx * trxusd, 8)
    return ducousd


def getRegisteredUsers():
    # Count all registered users
    while True:
        try:
            with sqlite3.connect(database, timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT COUNT(username) FROM Users")
                registeredUsers = datab.fetchone()[0]
                break
        except Exception:
            pass
    return registeredUsers


def getMinedDuco():
    # Count all mined DUCO
    while True:
        try:
            with sqlite3.connect(database, timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT SUM(balance) FROM Users")
                allMinedDuco = datab.fetchone()[0]
                break
        except Exception:
            pass
    return allMinedDuco


def getLeaders():
    # Get leaderboard of 10 DUCO holders
    while True:
        try:
            leadersdata = []
            with sqlite3.connect(database, timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Users ORDER BY balance DESC")
                i = 0
                for row in datab.fetchall():
                    leadersdata.append(f"{round((float(row[3])), 4)} DUCO - {row[0]}")
                    i += 1
                    if i > 10:
                        break
                break
        except Exception:
            pass
    return(leadersdata[:10])


def getAllBalances():
    # Get all balances list
    while True:
        try:
            baldata = {}
            with sqlite3.connect(database, timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Users ORDER BY balance DESC")
                for row in datab.fetchall():
                    if float(row[3]) > 0:
                        baldata[str(row[0])] = str(
                            round((float(row[3])), 8)) + " DUCO"
                    else:
                        # Stop when rest of the balances are just 0
                        break
                break
        except Exception:
            pass
    return(baldata)


def getTransactions():
    # Get transactions
    while True:
        try:
            transactiondata = {}
            with sqlite3.connect("config/transactions.db", timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Transactions")
                for row in datab.fetchall():
                    transactiondata[str(row[4])] = {
                        "Date": str(row[0].split(" ")[0]),
                        "Time": str(row[0].split(" ")[1]),
                        "Sender": str(row[1]),
                        "Recipient": str(row[2]),
                        "Amount": float(row[3])}
            break
        except Exception:
            pass
    return transactiondata


def getBlocks():
    # Get big blocks
    while True:
        try:
            transactiondata = {}
            with sqlite3.connect("config/foundBlocks.db", timeout=database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Blocks")
                for row in datab.fetchall():
                    transactiondata[row[3]] = {
                        "Date": str(row[0].split(" ")[0]),
                        "Time": str(row[0].split(" ")[1]),
                        "Finder": str(row[1]),
                        "Amount generated": float(row[2])}
        except Exception as e:
            print(e)
        with open('foundBlocks.json', 'w') as outfile:  # Write JSON big blocks to file
            json.dump(transactiondata, outfile, indent=2, ensure_ascii=False)
        #adminLog("system", "Updated block JSON data")
        time.sleep(120)


def cpuUsageThread():
    # CPU and RAM usage %
    while True:
        percarray.append(round(psutil.cpu_percent(interval=1)))
        memarray.append(psutil.virtual_memory()[2])
        time.sleep(3)


def API():
    # Update main server info and miner API file
    serverHashratearray = []
    while True:
        try:
            now = datetime.datetime.now()
            diff = int(blocks / diff_incrase_per)
            minerList = []
            usernameMinerCounter = {}
            minerapipublic = {}
            usernameMinerCounter_sorted = {}
            serverHashrate_not_smoothed = 0
            serverHashrate = 0
            serverHashrateArray = []
            hashrate = 0
            for x in minerapi.copy():
                try:
                    lastsharetimestamp = datetime.datetime.strptime(
                        minerapi[x]["Last share timestamp"], "%d/%m/%Y %H:%M:%S")  # Convert string back to datetime format
                    timedelta = now - lastsharetimestamp  # Get time delta
                    # Remove workers inactive for more than 30 seconds from the API
                    if int(timedelta.total_seconds()) > 30:
                        minerapi.pop(x)
                    # Add user hashrate to the server hashrate
                    serverHashrate_not_smoothed += float(
                        minerapi[x]["Hashrate"])
                except Exception:
                    pass

            serverHashrateArray.append(serverHashrate_not_smoothed)
            serverHashrate = statistics.mean(serverHashrateArray[-200:])

            if serverHashrate >= 800000000:
                prefix = " GH/s"
                serverHashrate = serverHashrate / 1000000000
            elif serverHashrate >= 800000:
                prefix = " MH/s"
                serverHashrate = serverHashrate / 1000000
            elif serverHashrate >= 800:
                prefix = " kH/s"
                serverHashrate = serverHashrate / 1000
            else:
                prefix = " H/s"

            for miner in minerapi.copy():
                try:
                    minerapipublic[miner] = {
                        "User":         str(minerapi[miner]["User"]),
                        "Hashrate":     minerapi[miner]["Hashrate"],
                        "Is estimated": str(minerapi[miner]["Is estimated"]),
                        "Sharetime":    minerapi[miner]["Sharetime"],
                        "Accepted":     minerapi[miner]["Accepted"],
                        "Rejected":     minerapi[miner]["Rejected"],
                        "Diff":         minerapi[miner]["Diff"],
                        "Algorithm":    minerapi[miner]["Algorithm"],
                        "Software":     str(minerapi[miner]["Software"]),
                        "Identifier":   str(minerapi[miner]["Identifier"]),
                        "Last share timestamp": str(minerapi[miner]["Last share timestamp"])}
                except Exception:
                    pass

            for thread in minerapipublic.copy():
                try:
                    # Append miners to formattedMinerApi["Miners"][id of thread]
                    minerList.append(minerapipublic[thread]["User"])
                except Exception:
                    pass

            for i in minerList.copy():
                # Count miners for every username
                usernameMinerCounter[i] = minerList.count(i)

            usernameMinerCounter_sorted = OrderedDict(sorted(
                usernameMinerCounter.items(),
                key=itemgetter(1),
                reverse=True))

            formattedMinerApi = {  # Prepare server API data
                "_Duino-Coin Public master server JSON API": "https://github.com/revoxhere/duino-coin",
                "Server version":        float(serverVersion),
                "Active connections":    int(connectedUsers),
                "Server CPU usage":      float(round(statistics.mean(percarray[-20:]), 2)),
                "Server RAM usage":      float(round(statistics.mean(memarray[-20:]), 2)),
                "Last update":           str(now.strftime("%d/%m/%Y %H:%M:%S (UTC)")),
                "Pool hashrate":         str(round(serverHashrate, 4))+prefix,
                # Get price from global
                "Duco price":            float(round(ducoPrice, 6)),
                # Call getRegisteredUsers function
                "Registered users":      int(getRegisteredUsers()),
                # Call getMinedDuco function
                "All-time mined DUCO":   int(getMinedDuco()),
                "Current difficulty":    int(diff),
                "Mined blocks":          int(blocks),
                "Last block hash":       str(lastBlockHash)[:10]+"...",
                # Call getLeaders function
                "Top 10 richest miners": getLeaders(),
                "Active workers":        usernameMinerCounter_sorted,
                "Miners":                minerapipublic}

            with open('api.json', 'w') as outfile:
                # Write JSON to file
                json.dump(
                    formattedMinerApi,
                    outfile,
                    indent=2,
                    ensure_ascii=False)
            time.sleep(5)
        except Exception:
            pass


def UpdateOtherAPIFiles():
    # Update API files
    while True:
        with open('balances.json', 'w') as outfile:
            # Write JSON balances to file
            json.dump(
                getAllBalances(),
                outfile,
                indent=2,
                ensure_ascii=False)
        with open('transactions.json', 'w') as outfile:
            # Write JSON transactions to file
            json.dump(
                getTransactions(),
                outfile,
                indent=2,
                ensure_ascii=False)
        time.sleep(10)


def UpdateDatabase():
    # Update database files every 5 seconds
    error_counter = 0
    while True:
        while True:
            try:
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    for user in balancesToUpdate.copy():
                        if not float(balancesToUpdate[user]) <= 0:
                            if float(balancesToUpdate[user]) > 0.0009:
                                balancesToUpdate[user] = 0.0009
                            datab.execute(
                                "UPDATE Users set balance = balance + ? where username = ?", (float(balancesToUpdate[user]), user))
                        balancesToUpdate.pop(user)
            except Exception as e:
                print("Error updating balances:", str(e))
                error_counter += 1

        while True:
            try:
                with lock:
                    # Update blocks counter and lastblock's hash
                    with sqlite3.connect(blockchain, timeout=database_timeout) as blockconn:
                        blockdatab = blockconn.cursor()
                        blockdatab.execute(
                            "UPDATE Server set blocks = ? ", (blocks,))
                        blockdatab.execute(
                            "UPDATE Server set lastBlockHash = ?", (lastBlockHash,))
                        blockconn.commit()
                        break
            except Exception as e:
                print("Error updating blockchain:", str(e))
                error_counter += 1
        if error_counter > 5:
            print("Restarting because of database errors")
            os.execl(sys.executable, sys.executable, *sys.argv)
        time.sleep(5)


def InputManagement():
    # Console
    time.sleep(0.5)
    while True:
        userInput = input("Duino-Coin $ ")
        userInput = userInput.split(" ")

        if userInput[0] == "help":
            print("""Available commands:
            - help - shows this help menu
            - balance <user> - prints user balance
            - set <user> <number> - sets user balance to number
            - subtract <user> <number> - subtract number from user balance
            - add <user> <number> - add number to user balance
            - clear - clears console
            - exit - exits DUCO server
            - restart - restarts DUCO server
            - ban <username> - bans username""")

        elif userInput[0] == "clear":
            os.system('clear')

        elif userInput[0] == "ban":
            try:
                username = userInput[1]
                try:
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "UPDATE Users set password = ? where username = ?", (duco_password, username))
                        conn.commit()
                    print("Step 1 - Changed password")
                except Exception:
                    print("Step 1 - Error changing password")
                try:
                    with open('config/banned.txt', 'a') as bansfile:
                        bansfile.write(str(username) + "\n")
                        print("Step 2 - Added username to banlist")
                except Exception:
                    print("Step 2 - Error adding username to banlist")

                try:
                    banlist.append(str(username))
                    print("Step 2 - Added username to blocked usernames")
                except Exception:
                    print("Step 3 - Error adding username to blocked usernames")

                try:
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (username,))
                        email = str(datab.fetchone()[2])  # Fetch email of user

                    message = MIMEMultipart("alternative")
                    message["Subject"] = "ToS violation on account " + \
                        str(username)
                    message["From"] = duco_email
                    message["To"] = email
                    # Turn email data into plain/html MIMEText objects
                    part1 = MIMEText(textBan, "plain")
                    part2 = MIMEText(htmlBan, "html")
                    message.attach(part1)
                    message.attach(part2)
                    # Create secure connection with server and send an email
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtpserver:
                        smtpserver.login(
                            duco_email, duco_password)
                        smtpserver.sendmail(
                            duco_email, email, message.as_string())
                    print("Step 4 - Sent email to", str(email))
                except Exception as e:
                    print("Step 4 - Error sending email to", str(email), str(e))
            except Exception:
                print("Provide a username first")

        elif userInput[0] == "exit":
            print("  Are you sure you want to exit DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
                s.close()
                os._exit(0)
            else:
                print("Canceled")

        elif userInput[0] == "restart":
            print("  Are you sure you want to restart DUCO server?")
            confirm = input("  Y/n")
            if confirm == "Y" or confirm == "y" or confirm == "":
                os.system("sudo iptables -F INPUT")
                os.system('clear')
                s.close()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                print("Canceled")

        elif userInput[0] == "balance":
            try:
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                    balance = str(datab.fetchone()[3])  # Fetch balance of user
                    print(userInput[1] + "'s balance: " + str(balance))
            except Exception:
                print("User doesn't exist")

        elif userInput[0] == "set":
            try:
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                    balance = str(datab.fetchone()[3])  # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " + str(balance) +
                      ", set it to " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(
                            userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                        # Fetch balance of user
                        balance = str(datab.fetchone()[3])
                    print("User balance is now " + str(balance))
                else:
                    print("Canceled")
            except Exception:
                print("User doesn't exist or you've entered wrong number")

        elif userInput[0] == "subtract":
            try:
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                    balance = str(datab.fetchone()[3])  # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " + str(balance) +
                      ", subtract " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(
                            balance)-float(userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                        # Fetch balance of user
                        balance = str(datab.fetchone()[3])
                    print("User balance is now " + str(balance))
                else:
                    print("Canceled")
            except Exception:
                print("User doesn't exist or you've entered wrong number")

        elif userInput[0] == "add":
            try:
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    datab.execute(
                        "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                    balance = str(datab.fetchone()[3])  # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " +
                      str(balance) + ", add " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(
                            balance)+float(userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (userInput[1],))
                        # Fetch balance of user
                        balance = str(datab.fetchone()[3])
                    print("User balance is now " + str(balance))
                else:
                    print("Canceled")
            except Exception:
                print("User doesn't exist or you've entered wrong number")


def createHashes():
    # Generate DUCO-S1 jobs
    while True:
        for i in range(hashes_num):
            rand = fastrand.pcg32bounded(100 * 4.5)
            readyHashesAVR[i] = {
                "Result": rand,
                "Hash": hashlib.sha1(
                    str(lastBlockHash
                        + str(rand)).encode("utf-8")).hexdigest(),
                "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
            rand = fastrand.pcg32bounded(100 * 125)
            readyHashesESP[i] = {
                "Result": rand,
                "Hash": hashlib.sha1(
                    str(lastBlockHash
                        + str(rand)).encode("utf-8")).hexdigest(),
                "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
            rand = fastrand.pcg32bounded(100 * 275)
            readyHashesESP32[i] = {
                "Result": rand,
                "Hash": hashlib.sha1(
                    str(lastBlockHash
                        + str(rand)).encode("utf-8")).hexdigest(),
                "LastBlockHash": str(lastBlockHash)}

        time.sleep(10)  # Refresh every 10s


def wraptx(duco_username, address, amount):
    # wDUCO wrapper
    adminLog("wrapper",
        "TRON wrapper called by " + duco_username)
    txn = wduco.functions.wrap(
        address,
        duco_username,
        int(float(amount)*10**6)
    ).with_owner(
        wrapper_public_key
    ).fee_limit(5_000_000).build().sign(
        PrivateKey(
            bytes.fromhex(wrapper_private_key)))
    txn = txn.broadcast()
    adminLog("wrapper",
        "Sent wrap tx to TRON network by " + duco_username)
    feedback = txn.result()
    return feedback


def unwraptx(duco_username, recipient, amount, private_key, public_key):
    # wDUCO unwrapper
    txn = wduco.functions.initiateWithdraw(
        duco_username,
        recipient,
        int(float(amount)*10**6)
    ).with_owner(
        PublicKey(PrivateKey(
            bytes.fromhex(wrapper_public_key)))
    ).fee_limit(5_000_000).build().sign(
        PrivateKey(
            bytes.fromhex(wrapper_private_key)))
    feedback = txn.broadcast().wait()
    return feedback


def confirmunwraptx(duco_username, recipient, amount):
    # wDUCO unwrap confirmer
    txn = wduco.functions.confirmWithdraw(
        duco_username,
        recipient,
        int(float(amount)*10**6)
    ).with_owner(
        wrapper_public_key
    ).fee_limit(5_000_000
                ).build().sign(
        PrivateKey(
            bytes.fromhex(wrapper_private_key)))
    txn = txn.broadcast()
    adminLog("unwrapper", "Sent confirm tx to tron network by", duco_username)
    return feedback


def handle(c, ip):
    c.settimeout(15)
    # Thread for every connection
    # These globals are used in the statistics API
    global connectedUsers, minerapi
    # These globals hold the current block count and last accepted hash
    global blocks, lastBlockHash
    # Variables for every thread
    username = ""
    poolID = ""
    firstshare = True
    # Set to true if a sharetime-test is being executed
    sharetime_test = False
    # Set according to the sharetime the miner had on higher difficulties
    # Only used during sharetime-exploit tests
    expected_test_sharetime = 0
    acceptedShares = 0
    rejectedShares = 0
    connectedUsers += 1
    overrideDiff = ""
    try:
        connections[ip] += 1
    except Exception:
        connections[ip] = 1

    # Send server version
    c.send(bytes(str(serverVersion), encoding="utf8"))

    while True:
        try:
            data2 = c.recv(256).decode()  # Receive data from client
            if not data2:
                # Exit loop if no data received
                break
            else:
                # Split incoming data
                data = data2.rstrip("\n").split(",")

                if data[0] == "PoolSync":
                    leng_of_base = 9
                    new_data = (data2[leng_of_base:])
                    data = ['PoolSync', new_data]

                elif data[0] == "PoolLoginAdd":
                    leng_of_base = 14 + len(data[1])
                    new_data = (data2[leng_of_base:])
                    data = ['PoolLoginAdd', data[1], new_data]

                elif data[0] == "PoolLogin":
                    leng_of_base = 10
                    new_data = (data2[leng_of_base:])
                    data = ['PoolLogin', new_data]
                c.settimeout(60)

            # print('new_data', data)

            if str(data[0]) == "PING":
                """Simple ping response"""
                try:
                    c.send(bytes("Pong!", encoding='utf8'))
                except Exception:
                    break

            elif str(data[0]) == "JOB":
                """Mining protocol for DUCO-S1"""
                if username == "":
                    try:
                        username = str(data[1])
                        if username == "":
                            c.send(bytes("BAD,Not enough data", encoding='utf8'))
                            break
                    except IndexError:
                        c.send(bytes("BAD,Not enough data", encoding='utf8'))
                        break
                if username in banlist:
                    ban(ip)
                    break

                if firstshare:
                    try:
                        workers[username] += 1
                    except Exception:
                        workers[username] = 1

                # Check if there aren't too much connections per IP
                if (connections[ip] > max_mining_connections
                        and not ip in whitelisted):
                    rejectedShares += 1
                    time.sleep(15)
                    c.send(bytes("BAD,Too many connections", encoding='utf8'))
                    # Close this thread
                    break

                # Check if there aren't too much connections per username
                if (workers[username] > max_mining_connections
                        and not username in whitelistedUsernames):
                    rejectedShares += 1
                    time.sleep(15)
                    c.send(bytes("BAD,Too many connections", encoding='utf8'))
                    # Close this thread
                    break

                try:
                    customDiff = str(data[2])
                    if customDiff == "":
                        customDiff = "NET"
                except IndexError:
                    customDiff = "NET"

                if firstshare:
                    if overrideDiff == "EXTREME" or customDiff == "EXTREME":
                        # Custom difficulty 950k
                        diff = 950000
                        # Practically no limits
                        max_hashrate = 999999999
                        max_shares_per_sec = 10

                    elif overrideDiff == "NET" or customDiff == "NET":
                        # Network difficulty
                        diff = int(blocks / diff_incrase_per)
                        # Max 2 MH/s
                        max_hashrate = 2000000
                        max_shares_per_sec = 1

                    elif overrideDiff == "MEDIUM" or customDiff == "MEDIUM":
                        # Diff for medium computers 30k
                        diff = 30000
                        # Max 1 MH/s
                        max_hashrate = 1000000
                        max_shares_per_sec = 2

                    elif customDiff == "LOW":
                        # Diff for webminers or slow computers 3k
                        diff = 3000
                        # Max 200 kH/s
                        max_hashrate = 200000
                        max_shares_per_sec = 2

                    elif customDiff == "ESP32":
                        # optimal diff for low power devices like ESP32
                        diff = 275
                        basereward = 0.00045
                        # Not overclocked ESP32 chips won't make more than ~10 kH/s
                        max_hashrate = 10000
                        max_shares_per_sec = 3

                    elif customDiff == "ESP32NL":
                        diff = 275
                        basereward = 0.00045
                        max_hashrate = 80000000000000000000
                        max_shares_per_sec = 30

                    elif customDiff == "ESP":
                        # DEPRECATED DIFF FOR ESP8266 MINERS BELOW VERSION 2.4
                        # Optimal diff for low power devices like ESP8266
                        diff = 125
                        basereward = 0.00055
                        # Not overclocked ESP8266 chips won't make more than ~3 kH/s
                        max_hashrate = 3000
                        max_shares_per_sec = 3

                    elif customDiff == "ESP8266":
                        # DIFF FOR NEW ESP8266 MINERS
                        # Optimal diff for low power devices like ESP8266
                        diff = 275
                        basereward = 0.00025
                        # Not overclocked ESP8266 chips won't make more than ~9 kH/s
                        max_hashrate = 10000
                        max_shares_per_sec = 3

                    elif customDiff == "AVR":
                        # Optimal diff for very low power devices like Arduino
                        diff = 5
                        basereward = 0.00055
                        # Not overclocked Arduino chips won't make more than ~155 H/s
                        max_hashrate = 155
                        max_shares_per_sec = 3

                if customDiff == "AVR":
                    randomChoice = random.randint(
                        0, len(readyHashesAVR) - 1)
                    rand = readyHashesAVR[randomChoice]["Result"]
                    newBlockHash = readyHashesAVR[randomChoice]["Hash"]
                    lastBlockHash_copy = readyHashesAVR[randomChoice]["LastBlockHash"]
                elif customDiff == "ESP":
                    randomChoice = random.randint(
                        0, len(readyHashesESP) - 1)
                    rand = readyHashesESP[randomChoice]["Result"]
                    newBlockHash = readyHashesESP[randomChoice]["Hash"]
                    lastBlockHash_copy = readyHashesESP[randomChoice]["LastBlockHash"]
                elif customDiff == "ESP32" or customDiff == "ESP32NL" or customDiff == "ESP8266":
                    randomChoice = random.randint(
                        0, len(readyHashesESP32) - 1)
                    rand = readyHashesESP32[randomChoice]["Result"]
                    newBlockHash = readyHashesESP32[randomChoice]["Hash"]
                    lastBlockHash_copy = readyHashesESP32[randomChoice]["LastBlockHash"]

                # Check if websocket proxy isn't used for anything else than webminer
                if customDiff != "LOW" and ip == "51.15.127.80":
                    break

                # Check if diffs that don't use pregenerated shares are used
                if (customDiff == "LOW"
                    or customDiff == "MEDIUM"
                    or customDiff == "NET"
                    or customDiff == "EXTREME"
                    or overrideDiff == "MEDIUM"
                    or overrideDiff == "NET"
                        or overrideDiff == "EXTREME"):

                    # Copy the current block hash as it can be changed by other threads
                    lastBlockHash_copy = lastBlockHash
                    expected_sharetime = expected_sharetime_sec * 1000
                    basereward = higher_diffs_basereward

                    if overrideDiff == "EXTREME" or customDiff == "EXTREME":
                        basereward = 0

                    if not firstshare and not sharetime_test:
                        try:
                            # Part of Kolka V3 - variable difficulty section
                            # Calculate the diff multiplier
                            p = 2 - sharetime / expected_sharetime

                            # Checks whether sharetime was higher than expected or has exceeded the buffer of 10%
                            # (p = 1 equals to sharetime = expected_sharetime)
                            if p < 1 or p > 1.1:
                                # Has met either condition thus the diff gets set
                                new_diff = int(diff * p)
                                # Checks whether the diff is lower than 0 (sharetime was way higher than expected)
                                if new_diff < 0:
                                    # Divided by abs(p) + 2 to drastically lower the diff
                                    # +2 is added to avoid dividing by +-0.x
                                    # *0.9 is used to decrease it when the sharetime is 3x higher than expected
                                    # everything is rounded down (floored) to not make the 0.9 useless
                                    # +1 is added to avoid getting diffs equal to 0
                                    new_diff = math.floor(
                                        int(diff / (abs(p) + 2)) * 0.9) + 1
                                # Check if sharetime was exactly double than expected
                                elif new_diff == 0:
                                    # Thus roughly half the difficulty
                                    new_diff = int(diff * 0.5)
                                diff = int(new_diff)
                            else:
                                # Hasn't met any of the conditions ( > 1 and < 1.1) thus leave diff
                                diff = int(diff)
                        except Exception as e:
                            print(e)
                    else:
                        time.sleep(3)

                    # Kolka V4
                    # Checks whether a sharetime-test was executed
                    try:
                        if sharetime_test:
                            sharetime_test = False
                            # Calculates how far apart they are (in percent)
                            p = sharetime / expected_test_sharetime
                            # Checks whether the sharetime took more than 50% longer than it should've
                            if p > 1.5:
                                rejectedShares += 1
                                # Calculate penalty dependent on share submission time - Kolka V1 combined with V4
                                penalty = float(
                                    int(int(sharetime) ** 2) * math.ceil(p / 10) / 1000000000) * -1
                                try:
                                    # Add username to the dict so it will be decremented in the next DB update
                                    balancesToUpdate[username] += penalty
                                except Exception:
                                    balancesToUpdate[username] = penalty
                    except Exception as e:
                        print(e)

                    # Generate result in range of the difficulty
                    rand = fastrand.pcg32bounded(100 * diff)

                    # Experimental Kolka V4
                    # There's a 16.6% to get a sharetime-exploit test
                    # (10 options, 11 and 12 = test; ergo 2 out of 12)
                    try:
                        if fastrand.pcg32bounded(12) > 10 and not firstshare:
                            # Drastically dropping the nonce to force a lower sharetime
                            # TODO: Maybe make this more random
                            rand = fastrand.pcg32bounded(10 * diff)
                            # Set to true to avoid increasing the difficulty by magnitudes
                            sharetime_test = True
                            # The expected sharetime should be about 10 times lower than it was before
                            expected_test_sharetime = sharetime / 10
                    except Exception as e:
                        print(e)

                    # Create the DUCO-S1 hash
                    newBlockHash = hashlib.sha1(
                        str(str(lastBlockHash_copy)
                            + str(rand)
                            ).encode("utf-8")).hexdigest()

                if customDiff == "ESP32" or customDiff == "ESP" or customDiff == "ESP32NL" or customDiff == "ESP8266":
                    # ESPs expect job ending with \n
                    # TODO: this will soon be pushed also to the other miners
                    try:
                        c.send(bytes(
                            str(lastBlockHash_copy)
                            + ","
                            + str(newBlockHash)
                            + ","
                            + str(diff)
                            + "\n",
                            encoding='utf8'))  # Send hashes and diff hash to the miner
                    except Exception:
                        break
                else:
                    # Send lastblockhash, expectedhash and diff to the client
                    try:
                        # Send hashes and diff hash to the miner
                        c.send(bytes(
                            str(lastBlockHash_copy)
                            + ","
                            + str(newBlockHash)
                            + ","
                            + str(diff),
                            encoding='utf8'))
                    except Exception:
                        break

                # Measure starting time
                jobsent = datetime.datetime.now()
                try:
                    # Wait until client solves hash
                    response = c.recv(512).decode().split(",")
                    result = response[0]
                except Exception:
                    break
                # Measure ending time
                resultreceived = datetime.datetime.now()

                # Time from start of hash computing to finding the result
                sharetime = resultreceived - jobsent
                # Get total ms
                sharetime = int(sharetime.total_seconds() * 1000)

                try:
                    hashrateCalculated = int(rand / (sharetime / 1000))
                except Exception:
                    hashrateCalculated = 1
                try:
                    # If client submitted hashrate, use it for the API
                    hashrate = float(response[1])
                    hashrateEstimated = False
                except Exception:
                    # If not, use the calculation
                    hashrate = hashrateCalculated
                    hashrateEstimated = True
                try:
                    # Check miner software for unallowed characters
                    minerUsed = re.sub(
                        '[^A-Za-z0-9 .()-]+', ' ', response[2])
                    # Check miner software for unallowed characters
                    minerIdentifier = re.sub(
                        '[^A-Za-z0-9 .()-]+', ' ', response[3])
                except Exception:
                    minerUsed = "Unknown miner"
                    minerIdentifier = "None"

                if customDiff == 'AVR':
                    try:
                        chipID = str(response[4])
                        #print("Chip ID:", chipID)
                    except IndexError:
                        pass

                try:
                    # Prepare miner API
                    try:
                        shares_per_sec = minerapi[str(
                            threading.get_ident())]["Sharerate"] + 1
                    except Exception:
                        shares_per_sec = 0
                    now = datetime.datetime.now()
                    lastsharetimestamp = now.strftime("%d/%m/%Y %H:%M:%S")
                    minerapi[str(threading.get_ident())] = {
                        "User":         str(username),
                        "Hashrate":     hashrate,
                        "Is estimated": str(hashrateEstimated),
                        "Sharetime":    sharetime,
                        "Sharerate":    shares_per_sec,
                        "Accepted":     acceptedShares,
                        "Rejected":     rejectedShares,
                        "Algorithm":    "DUCO-S1",
                        "Diff":         diff,
                        "Software":     str(minerUsed),
                        "Identifier":   str(minerIdentifier),
                        "Last share timestamp": str(lastsharetimestamp)}
                except Exception:
                    pass

                # Kolka V3
                # Move miner to higher diff tier if his hashrate is too high
                if int(hashrateCalculated) > int(max_hashrate):
                    # Set to adjust the starting diff again (see roughly line 860)
                    firstshare = True
                    # Move the difficulty up by one tier
                    if customDiff == "AVR":
                        overrideDiff = "MEDIUM"
                    if customDiff == "ESP":
                        overrideDiff = "ESP32"
                    if customDiff == "ESP32":
                        overrideDiff = "LOW"
                    if customDiff == "LOW":
                        overrideDiff = "MEDIUM"
                    if customDiff == "MEDIUM":
                        overrideDiff = "NET"
                    if customDiff == "NET":
                        overrideDiff = "EXTREME"

                # If the received result was correct
                if str(result) == str(rand) and int(hashrateCalculated) <= int(max_hashrate):
                    firstshare = False
                    acceptedShares += 1

                    try:
                        # Check if miner didn't exceed max sharerate per second
                        # Kolka V2
                        if minerapi[str(threading.get_ident())]["Sharerate"] > max_shares_per_sec:
                            # If he did, throttle him
                            time.sleep(15)
                    except Exception:
                        pass

                    # Calculate the reward - Kolka V1
                    if customDiff == "EXTREME" or overrideDiff == "EXTREME":
                        reward = (float(sharetime)
                                  / 100000000
                                  + workers[username]
                                  / 100000) / workers[username]
                    else:
                        reward = (reward_multiplier * basereward
                                  + float(sharetime) / 10000000000
                                  + float(diff) / 1000000000
                                  - workers[username] / 10000000)

                    # Low probability to find a "big block"
                    blockfound = random.randint(1, big_block_probability)
                    if int(blockfound) == 1:
                        # Add some DUCO to the reward
                        reward += big_block_reward
                        # Write to the big block database
                        with sqlite3.connect("config/foundBlocks.db", timeout=database_timeout) as bigblockconn:
                            datab = bigblockconn.cursor()
                            now = datetime.datetime.now()
                            formatteddatetime = now.strftime(
                                "%d/%m/%Y %H:%M:%S")
                            datab.execute('''INSERT INTO Blocks(timestamp, finder, amount, hash) VALUES(?, ?, ?, ?)''', (
                                formatteddatetime, username + " (DUCO-S1)", reward, newBlockHash))
                            bigblockconn.commit()
                        adminLog("duco", "Block found " + formatteddatetime + " by " +
                                 username)
                        # Send feedback that block was found
                        try:
                            c.send(bytes("BLOCK", encoding="utf8"))
                        except Exception:
                            break
                    else:
                        if str(customDiff) == "ESP32" or str(customDiff) == "ESP" or customDiff == "ESP8266":
                            # ESPs expect newline in the feedback
                            # TODO: this will soon be added to all the miners
                            try:
                                #print("Sending good esp feedback", username)
                                c.send(bytes("GOOD\n", encoding="utf8"))
                            except Exception:
                                break
                        else:
                            # Send feedback that result was correct
                            try:
                                c.send(bytes("GOOD", encoding="utf8"))
                            except Exception:
                                break
                    try:
                        # Add username to the dict so it will be incremented in the next DB update
                        balancesToUpdate[username] += reward
                    except Exception:
                        balancesToUpdate[username] = reward

                    # Increase global amount of shares and update block hash
                    blocks += 1
                    lastBlockHash = newBlockHash

                # If incorrect result was received
                else:
                    rejectedShares += 1
                    # Calculate penalty dependent on share submission time - Kolka V1
                    penalty = float(int(int(sharetime) ** 2) / 1000000000) * -1
                    try:
                        # Add username to the dict so it will be decremented in the next DB update
                        balancesToUpdate[username] += penalty
                    except Exception:
                        balancesToUpdate[username] = penalty

                    if str(customDiff) == "ESP32" or str(customDiff) == "ESP" or customDiff == "ESP8266":
                        try:
                            # ESPs expect newline in the feedback
                            # TODO: this will soon be added to all the miners
                            c.send(bytes("BAD\n", encoding="utf8"))
                        except Exception:
                            break
                    else:
                        try:
                            # Send feedback that incorrect result was received
                            c.send(bytes("BAD", encoding="utf8"))
                        except Exception:
                            break

            elif str(data[0]) == "JOBXX":
                """Mining protocol for XXHASH"""
                if username == "":
                    try:
                        username = str(data[1])
                        if username == "":
                            c.send(bytes("BAD,Not enough data\n", encoding='utf8'))
                            break
                    except IndexError:
                        c.send(bytes("BAD,Not enough data\n", encoding='utf8'))
                        break
                if username in banlist:
                    ban(ip)
                    break

                if firstshare:
                    try:
                        workers[username] += 1
                    except Exception:
                        workers[username] = 1

                # Check if there aren't too much connections per IP
                if (connections[ip] > max_mining_connections
                        and not ip in whitelisted):
                    rejectedShares += 1
                    c.send(bytes("BAD,Too many connections\n", encoding='utf8'))
                    # Close this thread
                    break

                # Check if there aren't too much connections per username
                if (workers[username] > max_mining_connections
                        and not username in whitelistedUsernames):
                    rejectedShares += 1
                    c.send(bytes("BAD,Too many connections\n", encoding='utf8'))
                    # Close this thread
                    break

                # Network difficulty
                diff = int(blocks / diff_incrase_per)
                max_shares_per_sec = 1
                # Max 3 MH/s
                max_hashrate = 3000000

                # Copy the current block hash as it can be changed by other threads
                lastBlockHash_copy = lastBlockHash
                expected_sharetime = expected_sharetime_sec * 1000
                basereward = higher_diffs_basereward / 30

                if not firstshare:
                    try:
                        # Part of Kolka V3 - variable difficulty section
                        # Calculate the diff multiplier
                        p = 2 - sharetime / expected_sharetime

                        # Checks whether sharetime was higher than expected or has exceeded the buffer of 10%
                        # (p = 1 equals to sharetime = expected_sharetime)
                        if p < 1 or p > 1.1:
                            # Has met either condition thus the diff gets set
                            new_diff = int(diff * p)
                            # Checks whether the diff is lower than 0 (sharetime was way higher than expected)
                            if new_diff < 0:
                                # Divided by abs(p) + 2 to drastically lower the diff
                                # +2 is added to avoid dividing by +-0.x
                                # *0.9 is used to decrease it when the sharetime is 3x higher than expected
                                # everything is rounded down (floored) to not make the 0.9 useless
                                # +1 is added to avoid getting diffs equal to 0
                                new_diff = math.floor(
                                    int(diff / (abs(p) + 2)) * 0.9) + 1
                            # Check if sharetime was exactly double than expected
                            elif new_diff == 0:
                                # Thus roughly half the difficulty
                                new_diff = int(diff * 0.5)
                            diff = int(new_diff)
                        else:
                            # Hasn't met any of the conditions ( > 1 and < 1.1) thus leave diff
                            diff = int(diff)
                    except Exception as e:
                        print(e)
                else:
                    time.sleep(3)

                # Generate result in range of the difficulty
                rand = fastrand.pcg32bounded(100 * diff)
                # Create the xxhash hash
                newBlockHash = xxhash.xxh64(
                    str(str(lastBlockHash_copy) + str(rand)), seed=2811).hexdigest()

                # Send lastblockhash, expectedhash and diff to the client
                try:
                    # Send hashes and diff hash to the miner
                    c.send(bytes(
                        str(lastBlockHash_copy)
                        + ","
                        + str(newBlockHash)
                        + ","
                        + str(diff)
                        + "\n",
                        encoding='utf8'))
                except Exception:
                    break

                # Measure starting time
                jobsent = datetime.datetime.now()
                try:
                    # Wait until client solves hash
                    response = c.recv(128).decode().split(",")
                except Exception:
                    break
                result = response[0]
                # Measure ending time
                resultreceived = datetime.datetime.now()

                # Time from start of hash computing to finding the result
                sharetime = resultreceived - jobsent
                # Get total ms
                sharetime = int(sharetime.total_seconds() * 1000)

                try:
                    hashrateCalculated = int(rand / (sharetime / 1000))
                except Exception:
                    hashrateCalculated = 1
                try:
                    # If client submitted hashrate, use it for the API
                    hashrate = float(response[1])
                    hashrateEstimated = False
                except Exception:
                    # If not, use the calculation
                    hashrate = hashrateCalculated
                    hashrateEstimated = True
                try:
                    # Check miner software for unallowed characters
                    minerUsed = re.sub(
                        '[^A-Za-z0-9 .()-]+', ' ', response[2])
                    # Check miner software for unallowed characters
                    minerIdentifier = re.sub(
                        '[^A-Za-z0-9 .()-]+', ' ', response[3])
                except Exception:
                    minerUsed = "Unknown miner"
                    minerIdentifier = "None"

                try:
                    # Prepare miner API
                    try:
                        shares_per_sec = minerapi[str(
                            threading.get_ident())]["Sharerate"] + 1
                    except Exception:
                        shares_per_sec = 0
                    now = datetime.datetime.now()
                    lastsharetimestamp = now.strftime("%d/%m/%Y %H:%M:%S")
                    minerapi[str(threading.get_ident())] = {
                        "User":         str(username),
                        "Hashrate":     hashrate,
                        "Is estimated": str(hashrateEstimated),
                        "Sharetime":    sharetime,
                        "Sharerate":    shares_per_sec,
                        "Accepted":     acceptedShares,
                        "Rejected":     rejectedShares,
                        "Algorithm":    "XXHASH",
                        "Diff":         diff,
                        "Software":     str(minerUsed),
                        "Identifier":   str(minerIdentifier),
                        "Last share timestamp": str(lastsharetimestamp)}
                except Exception:
                    pass

                # If the received result was correct
                if str(result) == str(rand) and int(hashrateCalculated) <= int(max_hashrate):
                    firstshare = False
                    acceptedShares += 1

                    try:
                        # Check if miner didn't exceed max sharerate per second
                        # Kolka V2
                        if minerapi[str(threading.get_ident())]["Sharerate"] > max_shares_per_sec:
                            # If he did, throttle him
                            time.sleep(15)
                    except Exception:
                        pass

                    reward = reward_multiplier * \
                        (basereward + float(sharetime) /
                         100000000 + float(diff) / 100000000)

                    # Low probability to find a "big block"
                    blockfound = random.randint(1, big_block_probability)
                    if int(blockfound) == 1:
                        # Add some DUCO to the reward
                        reward += big_block_reward
                        # Write to the big block database
                        with sqlite3.connect("config/foundBlocks.db", timeout=database_timeout) as bigblockconn:
                            datab = bigblockconn.cursor()
                            now = datetime.datetime.now()
                            formatteddatetime = now.strftime(
                                "%d/%m/%Y %H:%M:%S")
                            datab.execute('''INSERT INTO Blocks(timestamp, finder, amount, hash) VALUES(?, ?, ?, ?)''', (
                                formatteddatetime, username + " (XXHASH)", reward, newBlockHash))
                            bigblockconn.commit()
                        adminLog("duco", "Block found " + formatteddatetime + " by " +
                                 username)
                        # Send feedback that block was found
                        try:
                            c.send(bytes("BLOCK\n", encoding="utf8"))
                        except Exception:
                            break
                    else:
                        # Send feedback that result was correct
                        try:
                            c.send(bytes("GOOD\n", encoding="utf8"))
                        except Exception:
                            break

                    try:
                        # Add username to the dict so it will be incremented in the next DB update
                        balancesToUpdate[username] += reward
                    except Exception:
                        balancesToUpdate[username] = reward

                    # Increase global amount of shares and update block hash
                    blocks += 1
                    lastBlockHash = newBlockHash

                # If incorrect result was received
                else:
                    rejectedShares += 1
                    # Calculate penalty dependent on share submission time - Kolka V1
                    penalty = float(int(int(sharetime) ** 2) / 1000000000) * -1
                    try:
                        # Add username to the dict so it will be decremented in the next DB update
                        balancesToUpdate[username] += penalty
                    except Exception:
                        balancesToUpdate[username] = penalty

                    try:
                        # Send feedback that incorrect result was received
                        c.send(bytes("BAD\n", encoding="utf8"))
                    except Exception:
                        break

            elif str(data[0]) == "LOGI":
                """User login protocol"""
                try:
                    username = str(data[1])
                    password = str(data[2]).encode('utf-8')
                    if (connections[ip] > max_login_connections
                        and not ip in whitelisted
                            and not username in whitelistedUsernames):
                        adminLog("bans", "Banning IP: " + ip +
                                 " in login section, account: " + username)
                        ban(ip)
                        break
                    if username in banlist:
                        ban(ip)
                        break
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                # Check username for unallowed characters
                if re.match(r'^[\w\d_()]*$', username):
                    try:
                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                            # User exists, read his password
                            datab = conn.cursor()
                            datab.execute(
                                "SELECT * FROM Users WHERE username = ?", (str(username),))
                            stored_password = datab.fetchone()[1]
                    except Exception:
                        # Disconnect user which username doesn't exist, close the connection
                        c.send(bytes("NO,This user doesn't exist", encoding='utf8'))
                        break

                    try:
                        # User can supply bcrypt version of the password
                        if (password == stored_password
                            or password == duco_password.encode('utf-8')
                                or password == NodeS_Overide.encode('utf-8')):
                            # Send feedback about sucessfull login
                            c.send(bytes("OK", encoding='utf8'))
                        elif bcrypt.checkpw(password, stored_password):
                            # Send feedback about sucessfull login
                            c.send(bytes("OK", encoding='utf8'))
                        else:  # Disconnect user which password isn't valid, close the connection
                            c.send(
                                bytes("NO,Password is invalid", encoding='utf8'))
                            break
                    except Exception:
                        try:
                            stored_password = str(
                                stored_password).encode('utf-8')
                            if (bcrypt.checkpw(password, stored_password)
                                or password == duco_password.encode('utf-8')
                                    or password == NodeS_Overide.encode('utf-8')):
                                # Send feedback about sucessfull login
                                c.send(bytes("OK", encoding='utf8'))
                            else:  # Disconnect user which password isn't valid, close the connection
                                c.send(
                                    bytes("NO,Password is invalid", encoding='utf8'))
                                break
                        except Exception:
                            c.send(
                                bytes("NO,This user doesn't exist", encoding='utf8'))
                            break

                else:  # User used unallowed characters, close the connection
                    c.send(
                        bytes("NO,You have used unallowed characters", encoding='utf8'))
                    break

            elif str(data[0]) == "BALA" and str(username) != "":
                """Balance return protocol"""
                try:
                    while True:
                        try:
                            with sqlite3.connect(database, timeout=database_timeout) as conn:
                                datab = conn.cursor()
                                datab.execute(
                                    "SELECT * FROM Users WHERE username = ?", (username,))
                                # Fetch balance of user
                                balance = str(datab.fetchone()[3])
                                # Send it as 20 digit float
                                c.send(bytes(str(f'{float(balance):.20f}'), encoding="utf8"))
                                break
                        except Exception:
                            pass
                except Exception:
                    break

            elif str(data[0]) == "REGI":
                """New user registration protocol"""
                try:
                    username = str(data[1])
                    unhashed_pass = str(data[2]).encode('utf-8')
                    email = str(data[3])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                if re.match("^[A-Za-z0-9_-]*$", username) and len(username) < 64 and len(unhashed_pass) < 64 and len(email) < 128:
                    password = bcrypt.hashpw(
                        unhashed_pass, bcrypt.gensalt(rounds=4))  # Encrypt password
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT COUNT(username) FROM Users WHERE username = ?", (username,))
                        if int(datab.fetchone()[0]) == 0:
                            quickemailverification = client.quickemailverification()
                            # Email address which need to be verified
                            response = quickemailverification.verify(email)
                            resp = response.body
                            if resp["result"] == "valid" and resp["disposable"] == "false" and resp["safe_to_send"] == "true":
                                message = MIMEMultipart("alternative")
                                message["Subject"] = "Welcome on Duino-Coin network, " + \
                                    str(username)+"! " + u"\U0001F44B"
                                message["From"] = duco_email
                                message["To"] = email
                                try:
                                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                                        datab = conn.cursor()
                                        datab.execute(
                                            '''INSERT INTO Users(username, password, email, balance) VALUES(?, ?, ?, ?)''', (username, password, email, 0.0))
                                        conn.commit()
                                    adminLog("duco", "New user registered: " +
                                             username + " with email: " + email)
                                    c.send(bytes("OK", encoding='utf8'))
                                    try:
                                        # Turn email data into plain/html MIMEText objects
                                        part1 = MIMEText(text, "plain")
                                        part2 = MIMEText(html, "html")
                                        message.attach(part1)
                                        message.attach(part2)
                                        # Create secure connection with server and send an email
                                        context = ssl.create_default_context()
                                        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtpserver:
                                            smtpserver.login(
                                                duco_email, duco_password)
                                            smtpserver.sendmail(
                                                duco_email, email, message.as_string())
                                    except Exception:
                                        adminLog(
                                            "duco", "Error sending registration email to " + email)
                                except Exception:
                                    c.send(
                                        bytes("NO,Error registering user", encoding='utf8'))
                                    break
                            else:
                                c.send(
                                    bytes("NO,E-mail is invalid", encoding='utf8'))
                                break
                        else:
                            c.send(
                                bytes("NO,This account already exists", encoding='utf8'))
                            break
                else:
                    c.send(bytes(
                        "NO,You have used unallowed characters or data is too long", encoding='utf8'))
                    break

            elif str(data[0]) == "CHGP" and str(username) != "":
                """Password change protocol"""
                try:
                    oldPassword = data[1]
                    newPassword = data[2]
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                try:
                    oldPassword = oldPassword.encode('utf-8')
                    newPassword = newPassword.encode("utf-8")
                    newPassword_encrypted = bcrypt.hashpw(
                        newPassword, bcrypt.gensalt(rounds=4))
                except Exception:
                    c.send(bytes("NO,Bcrypt error", encoding="utf8"))
                    adminLog(
                        "duco", "Bcrypt error when changing password of user " + username)
                    break
                try:
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (username,))
                        old_password_database = datab.fetchone()[1]
                    adminLog("duco", "Fetched old password")
                except Exception:
                    c.send(bytes("NO,Incorrect username", encoding="utf8"))
                    adminLog(
                        "duco", "Incorrect username reported, most likely a DB error")
                    break
                try:
                    if bcrypt.checkpw(oldPassword, old_password_database.encode('utf-8')) or oldPassword == duco_password.encode('utf-8'):
                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                "UPDATE Users set password = ? where username = ?", (newPassword_encrypted, username))
                            conn.commit()
                            adminLog(
                                "duco", "Changed password of user " + username)
                            try:
                                c.send(
                                    bytes("OK,Your password has been changed", encoding='utf8'))
                            except Exception:
                                break
                    else:
                        adminLog("duco", "Passwords of user " +
                                 username + " don't match")
                        try:
                            server.send(
                                bytes("NO,Your old password doesn't match!", encoding='utf8'))
                        except Exception:
                            break
                except Exception:
                    if bcrypt.checkpw(oldPassword, old_password_database) or oldPassword == duco_password.encode('utf-8'):
                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                "UPDATE Users set password = ? where username = ?", (newPassword_encrypted, username))
                            conn.commit()
                            adminLog(
                                "duco", "Changed password of user " + username)
                            try:
                                c.send(
                                    bytes("OK,Your password has been changed", encoding='utf8'))
                            except Exception:
                                break
                    else:
                        print("Passwords dont match")
                        try:
                            server.send(
                                bytes("NO,Your old password doesn't match!", encoding='utf8'))
                        except Exception:
                            break

            elif str(data[0]) == "SEND" and str(username) != "":
                """Sending funds protcol"""
                try:
                    recipient = str(data[2])
                    amount = float(data[3])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                #adminLog("duco", "Sending protocol called by " + username)
                lastBlockHash_copy = lastBlockHash
                while True:
                    try:
                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                "SELECT * FROM Users WHERE username = ?", (username,))
                            # Get current balance of sender
                            balance = float(datab.fetchone()[3])
                            #adminLog("duco", "Read senders balance: " + str(balance))
                            break
                    except Exception:
                        pass

                if str(recipient) == str(username):
                    try:
                        c.send(
                            bytes("NO,You're sending funds to yourself", encoding='utf8'))
                    except Exception:
                        break
                if str(amount) == "" or str(recipient) == "" or float(balance) <= float(amount) or float(amount) <= 0:
                    try:
                        c.send(bytes("NO,Incorrect amount", encoding='utf8'))
                        adminLog(
                            "duco", "Incorrect amount supplied: " + str(amount))
                    except Exception:
                        break
                try:
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute(
                            "SELECT * FROM Users WHERE username = ?", (recipient,))
                        # Get receipents' balance
                        recipientbal = float(datab.fetchone()[3])
                    if float(balance) >= float(amount) and str(recipient) != str(username) and float(amount) >= 0:
                        try:
                            # Remove amount from senders' balance
                            balance -= float(amount)
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                                            datab = conn.cursor()
                                            datab.execute(
                                                "UPDATE Users set balance = ? where username = ?", (balance, username))
                                            conn.commit()
                                            #adminLog("duco", "Updated senders balance: " + str(balance))
                                            break
                                    except Exception:
                                        pass
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                                            datab = conn.cursor()
                                            datab.execute(
                                                "SELECT * FROM Users WHERE username = ?", (recipient,))
                                            # Get receipents' balance
                                            recipientbal = float(
                                                datab.fetchone()[3])
                                            #adminLog("duco", "Read recipients balance: " + str(recipientbal))
                                            break
                                    except Exception:
                                        pass
                            recipientbal += float(amount)
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout=database_timeout) as conn:
                                            datab = conn.cursor()  # Update receipents' balance
                                            datab.execute("UPDATE Users set balance = ? where username = ?", (f'{float(recipientbal):.20f}', recipient))
                                            conn.commit()
                                            #adminLog("duco", "Updated recipients balance: " + str(recipientbal))
                                        with sqlite3.connect("config/transactions.db", timeout=database_timeout) as tranconn:
                                            datab = tranconn.cursor()
                                            now = datetime.datetime.now()
                                            formatteddatetime = now.strftime(
                                                "%d/%m/%Y %H:%M:%S")
                                            datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (
                                                formatteddatetime, username, recipient, amount, lastBlockHash_copy))
                                            tranconn.commit()
                                        c.send(bytes(
                                            "OK,Successfully transferred funds,"+str(lastBlockHash_copy), encoding='utf8'))
                                        adminLog("duco", "Transferred " + str(round(amount, 2)) +
                                                 " DUCO from " + str(username) + " to " + str(recipient))
                                        break
                                    except Exception:
                                        pass
                        except Exception:
                            try:
                                c.send(
                                    bytes("NO,Error occured while sending funds", encoding='utf8'))
                            except Exception:
                                break
                except Exception:
                    try:
                        adminLog("duco", "Invalid recipient: " + recipient)
                        c.send(bytes("NO,Recipient doesn't exist", encoding='utf8'))
                    except Exception:
                        break

            elif str(data[0]) == "GTXL":
                """Transactions involving specific user protocol"""
                try:
                    username = str(data[1])
                    num = int(data[2])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                while True:
                    try:
                        transactiondata = {}
                        with sqlite3.connect("config/transactions.db", timeout=database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Transactions")
                            for row in datab.fetchall():
                                transactiondata[str(row[4])] = {
                                    "Date": str(row[0].split(" ")[0]),
                                    "Time": str(row[0].split(" ")[1]),
                                    "Sender": str(row[1]),
                                    "Recipient": str(row[2]),
                                    "Amount": float(row[3])}
                        break
                    except Exception as e:
                        print(e)
                try:
                    transactionsToReturn = {}
                    i = 0
                    for transaction in OrderedDict(reversed(list(transactiondata.items()))):
                        if transactiondata[transaction]["Recipient"] == username or transactiondata[transaction]["Sender"] == username:
                            transactionsToReturn[str(
                                i)] = transactiondata[transaction]
                            i += 1
                            if i >= num:
                                break
                    try:
                        transactionsToReturnStr = str(transactionsToReturn)
                        c.send(bytes(str(transactionsToReturnStr), encoding='utf8'))
                    except Exception as e:
                        print(e)
                        break
                except Exception as e:
                    print(e)
                    pass


            ################################## Pool Login ####################################
            elif str(data[0]) == "PoolLogin":
                try:
                    info = str(data[1])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                try:
                    info = ast.literal_eval(info)
                    poolHost = info['host']
                    poolPort = info['port']
                    poolVersion_sent = info['version']
                    poolID = info['identifier']
                except Exception as e:
                    print(e)
                    c.send(bytes(f"NO,Error: {e}", encoding='utf8'))
                    break

                if str(poolVersion_sent) == str(PoolVersion):
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        c2 = conn.cursor()
                        c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT)''')

                        c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
                        if (c2.fetchall()[0][0]) == 0:
                            c.send(bytes("NO,Identifier not found", encoding='utf8'))
                            break

                        c2.execute("UPDATE PoolList SET ip = ?, port = ?, Status = ? WHERE identifier = ?",(poolHost, poolPort, "True", poolID))

                        conn.commit()

                        c.send(bytes("LoginOK", encoding='utf8'))
                else:
                    c.send(bytes("LoginFailed", encoding='utf8'))

            ################################## Pool add Node ####################################
            elif str(data[0]) == "PoolLoginAdd":
                try:
                    password = str(data[1])
                    info = str(data[2])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                try:
                    info = ast.literal_eval(info)
                    poolName = info['name']
                    poolHost = info['host']
                    poolPort = info['port']
                    poolID = info['identifier']
                except Exception as e:
                    print(e)
                    c.send(bytes(f"NO,Error: {e}", encoding='utf8'))
                    break

                if password == PoolPassword:
                    with sqlite3.connect(database, timeout=database_timeout) as conn:
                        c2 = conn.cursor()
                        c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT)''')
                        c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
                        if (c2.fetchall()[0][0]) == 0:
                            c2.execute("INSERT INTO PoolList(identifier, name, ip, port, Status) VALUES(?, ?, ?, ?, ?)",(poolID, poolName, poolHost, poolPort, "False"))

                            conn.commit()
                            c.send(bytes("LoginOK", encoding='utf8'))

                        else:
                            c.send(bytes("NO,Identifier not found", encoding='utf8'))
                            break
                else:
                    c.send(bytes("NO,Password Incorrect", encoding='utf8'))



            ################################## Pool Sync ####################################
            elif str(data[0]) == "PoolSync" and str(poolID) != "":
                try:
                    info = str(data[1])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                try:
                    info = ast.literal_eval(info)
                    rewards = info['rewards']
                    blocks_to_add = int(info['blocks']['blockIncrease'])
                except Exception as e:
                    print(e)
                    c.send(bytes(f"NO,Error: {e}", encoding='utf8'))
                    break

                # ============

                blocks += blocks_to_add

                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    datab = conn.cursor()
                    for user in rewards.keys():
                        datab.execute("UPDATE Users set balance = balance + ?  where username = ?", (float(rewards[user]), user))
                    conn.commit()

                # ============
                data_send = {"totalBlocks": blocks,
                            "diffIncrease": diff_incrase_per}

                data_send = (str(data_send)).replace("\'", "\"")

                c.send(bytes(f"SyncOK,{data_send}", encoding='utf8'))



            ################################## Pool Logout ####################################
            elif str(data[0]) == "PoolLogout":
                try:
                    poolID = str(data[1])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break


                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    c2 = conn.cursor()
                    c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT)''')

                    c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
                    if (c2.fetchall()[0][0]) == 0:
                        c.send(bytes("NO,Identifier not found", encoding='utf8'))
                        break

                    c2.execute("UPDATE PoolList SET Status = ? WHERE identifier = ?",("False", poolID))

                    conn.commit()

                    c.send(bytes("LogoutOK", encoding='utf8'))


            ################################## Pool List ####################################
            elif str(data[0]) == "POOLList":
                with sqlite3.connect(database, timeout=database_timeout) as conn:
                    c2 = conn.cursor()
                    c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT)''')

                    c2.execute("SELECT name, ip, port, Status FROM PoolList")
                    info = c2.fetchall()

                    c.send(bytes(f"{info}", encoding='utf8'))


            ######################################################################
            elif str(data[0]) == "WRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    adminLog(
                        "wrapper", "Starting wrapping protocol by " + username)
                    try:
                        amount = str(data[1])
                        tron_address = str(data[2])
                    except IndexError:
                        c.send(bytes("NO,Not enough data", encoding="utf8"))
                        break
                    try:
                        with sqlite3.connect(database) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                "SELECT * FROM Users WHERE username = ?", (username,))
                            # Get current balance
                            balance = float(datab.fetchone()[3])
                    except Exception:
                        c.send(bytes("NO,Can't check balance", encoding='utf8'))
                        break

                    if float(balance) < float(amount) or float(amount) <= 0:
                        try:
                            c.send(bytes("NO,Incorrect amount", encoding='utf8'))
                        except Exception:
                            break
                    elif float(balance) >= float(amount) and float(amount) > 0:
                        if float(amount) < 10:
                            try:
                                c.send(
                                    bytes("NO,minimum amount is 10 DUCO", encoding="utf8"))
                                adminLog("wrapper", "Amount is below 10 DUCO")
                            except Exception:
                                break
                        else:
                            balancebackup = balance
                            adminLog(
                                "wrapper", "Backed up balance: " + str(balancebackup))
                            try:
                                adminLog(
                                    "wrapper", "All checks done, initiating wrapping routine")
                                # Remove amount from senders' balance
                                balance -= float(amount)
                                adminLog(
                                    "wrapper", "DUCO removed from pending balance")
                                with sqlite3.connect(database) as conn:
                                    datab = conn.cursor()
                                    datab.execute(
                                        "UPDATE Users set balance = ? where username = ?", (balance, username))
                                    conn.commit()
                                adminLog(
                                    "wrapper", "DUCO balance sent to DB, sending tron transaction")
                                adminLog("wrapper", "Tron wrapper called")
                                txn = wduco.functions.wrap(tron_address, int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                adminLog("wrapper", "Txid: " + txn.txid)
                                txn = txn.broadcast()
                                adminLog(
                                    "wrapper", "Sent wrap tx to TRON network")
                                trontxfeedback = txn.result()

                                if trontxfeedback:
                                    try:
                                        c.send(
                                            bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        adminLog(
                                            "wrapper", "Successful wrapping")
                                        try:
                                            with sqlite3.connect("config/transactions.db", timeout=database_timeout) as tranconn:
                                                datab = tranconn.cursor()
                                                now = datetime.datetime.now()
                                                formatteddatetime = now.strftime(
                                                    "%d/%m/%Y %H:%M:%S")
                                                datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (
                                                    formatteddatetime, username, str("wrapper - ")+str(tron_address), amount, lastBlockHash))
                                                tranconn.commit()
                                            c.send(
                                                bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        except Exception:
                                            pass
                                    except Exception:
                                        break
                                else:
                                    try:
                                        datab.execute(
                                            "UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                        c.send(
                                            bytes("NO,Unknown error, transaction reverted", encoding="utf8"))
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                    else:
                        c.send(bytes("NO,Wrapper disabled", encoding="utf8"))
                        adminLog("wrapper", "Wrapper is disabled")

            ######################################################################
            elif str(data[0]) == "UNWRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    adminLog(
                        "unwrapper", "Starting unwraping protocol by " + username)
                    amount = str(data[1])
                    tron_address = str(data[2])
                    while True:
                        try:
                            with sqlite3.connect(database) as conn:
                                adminLog(
                                    "unwrapper", "Retrieving user balance")
                                datab = conn.cursor()
                                datab.execute(
                                    "SELECT * FROM Users WHERE username = ?", (username,))
                                # Get current balance
                                balance = float(datab.fetchone()[3])
                                break
                        except Exception:
                            pass
                    print("Balance retrieved")
                    wbalance = float(
                        int(wduco.functions.pendingWithdrawals(tron_address, username)))/10**6
                    if float(amount) <= float(wbalance) and float(amount) > 0:
                        if float(amount) >= 10:
                            if float(amount) <= float(wbalance):
                                adminLog("unwrapper", "Correct amount")
                                balancebackup = balance
                                adminLog("unwrapper", "Updating DUCO Balance")
                                balancebackup = balance
                                balance = str(float(balance)+float(amount))
                                while True:
                                    try:
                                        with sqlite3.connect(database) as conn:
                                            datab = conn.cursor()
                                            datab.execute(
                                                "UPDATE Users set balance = ? where username = ?", (balance, username))
                                            conn.commit()
                                            break
                                    except Exception:
                                        pass
                                try:
                                    adminLog(
                                        "unwrapper", "Sending tron transaction")
                                    txn = wduco.functions.confirmWithdraw(username, tron_address, int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                    adminLog("unwrapper", "Txid: " + txn.txid)
                                    txn = txn.broadcast()
                                    adminLog(
                                        "unwrapper", "Sent confirm tx to tron network")
                                    onchaintx = txn.result()

                                    if onchaintx:
                                        adminLog(
                                            "unwrapper", "Successful unwrapping")
                                        try:
                                            with sqlite3.connect("config/transactions.db", timeout=database_timeout) as tranconn:
                                                datab = tranconn.cursor()
                                                now = datetime.datetime.now()
                                                formatteddatetime = now.strftime(
                                                    "%d/%m/%Y %H:%M:%S")
                                                datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (
                                                    formatteddatetime, str("Wrapper - ")+str(tron_address), username, amount, lastBlockHash))
                                                tranconn.commit()
                                            c.send(
                                                bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        except Exception:
                                            pass
                                    else:
                                        while True:
                                            try:
                                                with sqlite3.connect(database) as conn:
                                                    datab = conn.cursor()
                                                    datab.execute(
                                                        "UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                                    conn.commit()
                                                    break
                                            except Exception:
                                                pass
                                except Exception:
                                    adminLog(
                                        "unwrapper", "Error with Tron blockchain")
                                    try:
                                        c.send(
                                            bytes("NO,error with Tron blockchain", encoding="utf8"))
                                        break
                                    except Exception:
                                        break
                            else:
                                try:
                                    c.send(
                                        bytes("NO,Minimum amount is 10", encoding="utf8"))
                                except Exception:
                                    break
                else:
                    adminLog("unwrapper", "Wrapper disabled")
                    try:
                        c.send(bytes("NO,Wrapper disabled", encoding="utf8"))
                    except Exception:
                        break
        except Exception:
            break

    # These things execute when user disconnects/exits the main loop
    connectedUsers -= 1

    # Decrement connection counter
    try:
        connections[ip] -= 1
        if connections[ip] <= 0:
            connections.pop(ip)
    except KeyError:
        pass

    # Decrement worker counter
    try:
        workers[username] -= 1
        if workers[username] <= 0:
            workers.pop(username)
    except KeyError:
        pass

    # Delete worker from minerapi
    try:
        del minerapi[str(threading.get_ident())]
    except KeyError:
        pass

    # Close thread
    sys.exit()


def unbanip(ip):
    # Unban IP
    try:
        os.system("sudo iptables -D INPUT -s "+str(ip)+" -j DROP")
        adminLog("bans", "Unbanning IP: " + ip)
    except Exception:
        pass


def ban(ip):
    # Ban IP
    try:
        os.system("sudo iptables -I INPUT -s "+str(ip)+" -j DROP")
        # Start auto-unban thread for this IP
        threading.Timer(30.0, unbanip, [ip]).start()
        IPS.pop(ip)
    except Exception:
        pass


def countips():
    # Count connections per IP
    while True:
        for ip in IPS.copy():
            try:
                if IPS[ip] > max_unauthorized_connections and not ip in whitelisted_ip:
                    adminLog("bans", "Banning DDoSing IP: " + ip)
                    ban(ip)
            except Exception:
                pass
        time.sleep(5)


def resetips():
    # Clear IP counter
    while True:
        time.sleep(30)
        IPS.clear()


def shares_per_sec_timer():
    # Reset shares per second values
    global minerapi
    while True:
        for miner in minerapi.copy():
            try:
                minerapi[miner]["Sharerate"] = 0
            except Exception:
                pass
        time.sleep(shares_per_sec_reset)


IPS = {}
workers = {}
bannedIPS = {}
whitelisted = []
if __name__ == '__main__':
    print("Duino-Coin Master Server", serverVersion, "is starting")
    print("wDUCO address:", wrapper_public_key)

    try:
        # Read whitelisted IPs
        with open("config/whitelisted.txt", "r") as whitelistfile:
            whitelisted = whitelistfile.read().splitlines()
        adminLog("system", "Loaded whitelisted IPs file")
        whitelisted_ip = []
        for ip in whitelisted:
            whitelisted_ip.append(socket.gethostbyname(str(ip)))
    except Exception as e:
        adminLog("system", "Error reading whitelisted IPs file: " + str(e))

    try:
        # Read whitelisted usernames
        with open("config/whitelistedUsernames.txt", "r") as whitelistusrfile:
            whitelistedusr = whitelistusrfile.read().splitlines()
            adminLog("system", "Loaded whitelisted usernames file")
            whitelistedUsernames = []
            for username in whitelistedusr:
                whitelistedUsernames.append(username)
    except Exception as e:
        adminLog(
            "system", "Error reading whitelisted usernames file: " + str(e))

    try:
        # Read banned usernames
        with open("config/banned.txt", "r") as bannedusrfile:
            bannedusr = bannedusrfile.read().splitlines()
            adminLog("system", "Loaded banned usernames file")
            banlist = []
            for username in bannedusr:
                banlist.append(username)
    except Exception as e:
        adminLog(
            "system", "Error reading banned usernames file: " + str(e))

    # Create CPU perc measurement
    threading.Thread(target=cpuUsageThread).start()
    # Create duco price calculator
    threading.Thread(target=getDucoPrice).start()
    threading.Thread(target=countips).start()  # Start anti-DDoS thread
    # Start connection counter reseter for the ant-DDoS thread
    threading.Thread(target=resetips).start()
    threading.Thread(target=getBlocks).start()  # Start database updater
    threading.Thread(target=UpdateDatabase).start()  # Start database updater
    threading.Thread(target=API).start()  # Create JSON API thread
    # Start transactions and balance api updater
    threading.Thread(target=UpdateOtherAPIFiles).start()
    # Create Backup generator thread
    threading.Thread(target=createBackup).start()
    # Create Backup generator thread
    threading.Thread(target=shares_per_sec_timer).start()
    threading.Thread(target=createHashes).start()  # Start database updater
    # Admin input management thread
    threading.Thread(target=InputManagement).start()
    print("Background threads started")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
    s.bind((host, port))
    # Put the socket into listening mode; reuse connection after one is closed
    s.listen(socket_listen_num)
    print("TCP Socket binded to port", port)

    try:
        while True:
            # A forever loop until client wants to exit
            c, addr = s.accept()  # Establish connection with client
            try:
                IPS[addr[0]] += 1
            except Exception:
                IPS[addr[0]] = 1

            # Start a new thread
            start_new_thread(handle, (c, addr[0]))

            IPS[addr[0]] -= 1
            if IPS[addr[0]] <= 0:
                IPS.pop(addr[0])
    except Exception as e:
        print("Exiting", str(e))
        s.close()
        os._exit(1)  # Error code 1 so server will autorestart with systemd
