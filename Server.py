#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server Remastered (v2.3)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################
import requests, ast, smtplib, sys, ssl, socket, re, math, random, hashlib, datetime,  requests, smtplib, ssl, sqlite3, bcrypt, time, os.path, json, logging, threading, configparser, fastrand, os, psutil, statistics
from _thread import *
from shutil import copyfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import OrderedDict
import quickemailverification

host = "" # Server will use this as hostname to bind to (localhost on Windows, 0.0.0.0 on Linux in most cases)
port = 2811 # Server will listen on this port (official server uses 2811)
serverVersion = 2.2 # Server version which will be sent to the clients (official server uses latest release version number)
diff_incrase_per = 5000 # Difficulty will increase every x blocks (official server uses 5k)
max_mining_connections = 24 # Maximum number of clients using mining protocol per IP 
max_login_connections = 28 # Maximum number of logged-in clients per IP 
max_unauthorized_connections = 28 # Maximum number of connections that haven't sent any data yet 
hashes_num = 3000 # Number of pregenerated jobs for every difficulty in mining section; used to massively reduce load on the server (official server uses 3000)
database_timeout = 5 # Database access times out after this many seconds (default: 5)
max_rejected_shares = 50
big_block_reward = 7.77
reward_multiplier = 0.77
socket_listen_num = 4
use_wrapper = True # wDUCO wrapper usage
wrapper_permission = False # Set to false for declaration, will be updated when checking smart contract
config = configparser.ConfigParser()
lock = threading.Lock()

try: # Read sensitive data from config file
    config.read('AdminData.ini')
    duco_email = config["main"]["duco_email"]
    duco_password = config["main"]["duco_password"]
    NodeS_Overide = config["main"]["NodeS_Overide"]
    wrapper_private_key = config["main"]["wrapper_private_key"]
    NodeS_Username = config["main"]["NodeS_Username"]
    emailchecker_private_key = config["main"]["emailchecker_private_key"]
except:
    print("""Please create AdminData.ini config file first:
        [main]
        duco_email = ???
        duco_password = ???
        NodeS_Overide = ???
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
Duino-Coin Team"""

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
       <italic>Duino-Coin Team</italic>
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
readyHashesMedium = {}
readyHashesNet = {}
readyHashesAVR = {}
readyHashesESP = {}
readyHashesESP32 = {}
readyHashesEXTREME = {}
readyHashesLow = {}

database = 'crypto_database.db' # User data database location
if not os.path.isfile(database):
    # Create it if it doesn't exist
    with sqlite3.connect(database, timeout = database_timeout) as conn:
        datab = conn.cursor()
        datab.execute('''CREATE TABLE IF NOT EXISTS Users(username TEXT, password TEXT, email TEXT, balance REAL)''')
        conn.commit()

blockchain = 'duino_blockchain.db' # Blockchain database location
if not os.path.isfile(blockchain):
    # Create it if it doesn't exist
    with sqlite3.connect(blockchain, timeout = database_timeout) as blockconn:
        try:
            with open("config/lastblock", "r+") as lastblockfile:
                lastBlockHash = lastblockfile.readline() # If old database is found, read lastBlockHash from it
        except:
            lastBlockHash = "ba29a15896fd2d792d5c4b60668bf2b9feebc51d" # First block - SHA1 of "duino-coin"
        try:
            with open("config/blocks", "r+") as blockfile:
                blocks = blockfile.readline() # If old database is found, read mined blocks amount from it
        except:
            blocks = 1 # Start from 1
        blockdatab = blockconn.cursor()
        blockdatab.execute('''CREATE TABLE IF NOT EXISTS Server(blocks REAL, lastBlockHash TEXT)''')
        blockdatab.execute("INSERT INTO Server(blocks, lastBlockHash) VALUES(?, ?)", (blocks, lastBlockHash))
        blockconn.commit()
else:
    with sqlite3.connect(blockchain, timeout = database_timeout) as blockconn:
        blockdatab = blockconn.cursor()
        blockdatab.execute("SELECT blocks FROM Server")
        # Read amount of mined blocks
        blocks = int(blockdatab.fetchone()[0])
        blockdatab.execute("SELECT lastBlockHash FROM Server")
        # Read lastblock's hash
        lastBlockHash = str(blockdatab.fetchone()[0])

if not os.path.isfile("config/transactions.db"):
    # Create transactions database if it doesn't exist
    with sqlite3.connect("config/transactions.db", timeout = database_timeout) as conn:
        datab = conn.cursor()
        datab.execute('''CREATE TABLE IF NOT EXISTS Transactions(timestamp TEXT, username TEXT, recipient TEXT, amount REAL, hash TEXT)''')
        conn.commit()

if not os.path.isfile("config/foundBlocks.db"):
    # Create transactions database if it doesn't exist
    with sqlite3.connect("config/foundBlocks.db", timeout = database_timeout) as conn:
        datab = conn.cursor()
        datab.execute('''CREATE TABLE IF NOT EXISTS Blocks(timestamp TEXT, finder TEXT, amount REAL, hash TEXT)''')
        conn.commit()
        
if use_wrapper:
    import tronpy # Tronpy isn't default installed, install it with "python3 -m pip install tronpy"
    from tronpy.keys import PrivateKey, PublicKey
    # Wrapper public key
    wrapper_public_key = PrivateKey(bytes.fromhex(wrapper_private_key)).public_key.to_base58check_address()
    tron = tronpy.Tron(network="mainnet")
    # wDUCO contract
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U") 
    wrapper_permission = wduco.functions.checkWrapperStatus(wrapper_public_key)
    
def adminLog(messagetype, message):
    # TODO
    if messagetype != "bans":
        print(message)
    
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
                pricesNodeSfile.write("," + str(getDucoPriceNodeS()).rstrip("\n"))
            with open("pricesJustSwap.txt", "a") as pricesJustSwapfile:
                pricesJustSwapfile.write("," + str(getDucoPriceJustSwap()).rstrip("\n"))
        # Run every 6h
        time.sleep(3600*6) 
        adminLog("system", "Backup finished")
        
def getDucoPrice():
    # Calcualte DUCO price price from coingecko
    global ducoPrice
    while True:
        coingecko = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=magi&vs_currencies=usd", data=None)
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
    nodeS = requests.get("http://www.node-s.co.za/api/v1/duco/exchange_rate", data=None)
    if nodeS.status_code == 200:
        nodeScontent = nodeS.content.decode()
        nodeScontentjson = json.loads(nodeScontent)
        ducousd = float(nodeScontentjson["value"])
    else:
        ducousd = .015
    return ducousd

def getDucoPriceJustSwap():
    # Get DUCO price from JustSwap exchange
    justswap = requests.get("https://api.justswap.io/v2/allpairs?page_size=9000&page_num=2", data=None)
    if justswap.status_code == 200:
        justswapcontent = justswap.content.decode()
        justswapcontentjson = json.loads(justswapcontent)
        ducotrx = float(justswapcontentjson["data"]["0_TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U"]["price"])
    else:
        ducotrx = .25
    coingecko = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd", data=None)
    if coingecko.status_code == 200:
        geckocontent = coingecko.content.decode()
        geckocontentjson = json.loads(geckocontent)
        trxusd = float(geckocontentjson["tron"]["usd"])
    else:
        trxusd = .05
    ducousd = round(ducotrx * trxusd, 8);
    return ducousd

def getRegisteredUsers():
    # Count all registered users
    while True:
        try:
            with sqlite3.connect(database, timeout = database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT COUNT(username) FROM Users")
                registeredUsers = datab.fetchone()[0]
                break
        except:
            pass
    return registeredUsers

def getMinedDuco():
    # Count all mined DUCO
    while True:
        try:
            with sqlite3.connect(database, timeout = database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT SUM(balance) FROM Users")
                allMinedDuco = datab.fetchone()[0]
                break
        except:
            pass
    return allMinedDuco

def getLeaders():
    # Get leaderboard of 10 DUCO holders
    while True:
        try:
            leadersdata = []
            with sqlite3.connect(database, timeout = database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Users ORDER BY balance DESC")
                i = 0
                for row in datab.fetchall():
                    leadersdata.append(f"{round((float(row[3])), 4)} DUCO - {row[0]}")
                    i += 1
                    if i > 10:
                        break
                break
        except:
            pass
    return(leadersdata[:10])

def getAllBalances():
    # Get all balances list
    while True:
        try:
            leadersdata = {}
            with sqlite3.connect(database, timeout = database_timeout) as conn:
                datab = conn.cursor()
                datab.execute("SELECT * FROM Users ORDER BY balance DESC")
                for row in datab.fetchall():
                    if float(row[3]) > 0:
                        leadersdata[str(row[0])] = str(round((float(row[3])), 4)) + " DUCO"
                break
        except:
            pass
    return(leadersdata)

def getTransactions():
    # Get transactions
    while True:
        try:
            transactiondata = {}
            with sqlite3.connect("config/transactions.db", timeout = database_timeout) as conn:
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
        except:
            pass
    return transactiondata

def getBlocks():
    # Get big blocks
    while True:
        try:
            transactiondata = {}
            with sqlite3.connect("config/foundBlocks.db", timeout = database_timeout) as conn:
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
        with open('foundBlocks.json', 'w') as outfile: # Write JSON big blocks to file
            json.dump(transactiondata, outfile, indent=4, ensure_ascii=False)
        #adminLog("system", "Updated block JSON data")
        time.sleep(120)
        
def cpuUsageThread():
    # CPU usage %
    while True:
        percarray.append(round(psutil.cpu_percent(interval=None)))
        process = psutil.Process(os.getpid())
        memarray.append(round(process.memory_percent()))
        time.sleep(3)

def API():
    # Update main server info and miner API file
    while True:
        try:
            now = datetime.datetime.now()
            diff = int(blocks / diff_incrase_per)
            minerList = []
            usernameMinerCounter = {}
            serverHashrate = 0
            hashrate = 0
            for x in minerapi.copy():
                lastsharetimestamp = datetime.datetime.strptime(minerapi[x]["Last share timestamp"], "%d/%m/%Y %H:%M:%S") # Convert string back to datetime format
                timedelta = now - lastsharetimestamp # Get time delta
                if int(timedelta.total_seconds()) > 30: # Remove workers inactive for more than 30 seconds from the API
                    minerapi.pop(x)
                serverHashrate += float(minerapi[x]["Hashrate"]) # Add user hashrate to the server hashrate

            if serverHashrate >= 1000000000:
                prefix = " GH/s"
                serverHashrate = serverHashrate / 1000000000
            elif serverHashrate >= 1000000:
                prefix = " MH/s"
                serverHashrate = serverHashrate / 1000000
            elif serverHashrate >= 1000:
                prefix = " kH/s"
                serverHashrate = serverHashrate / 1000
            else:
                prefix = " H/s"

            minerapipublic = {}
            for miner in minerapi.copy():
                minerapipublic[miner] = {
                    "User":         str(minerapi[miner]["User"]),
                    "Hashrate":     minerapi[miner]["Hashrate"],
                    "Is estimated": str(minerapi[miner]["Is estimated"]),
                    "Sharetime":    minerapi[miner]["Sharetime"],
                    "Accepted":     minerapi[miner]["Accepted"],
                    "Rejected":     minerapi[miner]["Rejected"],
                    "Diff":         minerapi[miner]["Diff"],
                    "Software":     str(minerapi[miner]["Software"]),
                    "Identifier":   str(minerapi[miner]["Identifier"]),
                    "Last share timestamp": str(minerapi[miner]["Last share timestamp"])}

            formattedMinerApi = { # Prepare server API data
                "_Duino-Coin Public master server JSON API": "https://github.com/revoxhere/duino-coin",
                "Server version":        float(serverVersion),
                "Active connections":    int(connectedUsers),
                "Open threads":          int(threading.active_count()),
                "Server CPU usage":      float(round(statistics.mean(percarray[-100:]), 2)),
                "Server RAM usage":      float(round(statistics.mean(memarray[-100:]), 2)),
                "Last update":           str(now.strftime("%d/%m/%Y %H:%M (UTC)")),
                "Pool hashrate":         str(round(serverHashrate, 2))+prefix,
                "Duco price":            float(round(ducoPrice, 6)), # Get price from global
                "Registered users":      int(getRegisteredUsers()), # Call getRegisteredUsers function
                "All-time mined DUCO":   float(round(getMinedDuco(), 2)), # Call getMinedDuco function
                "Current difficulty":    int(diff),
                "Mined blocks":          int(blocks),
                "Full last block hash":  str(lastBlockHash),
                "Last block hash":       str(lastBlockHash)[:10]+"...",
                "Top 10 richest miners": getLeaders(), # Call getLeaders function
                "Active workers":        usernameMinerCounter,
                "Miners":                minerapipublic}
            
            for thread in formattedMinerApi["Miners"].copy():
                # Append miners to formattedMinerApi["Miners"][id of thread]
                minerList.append(formattedMinerApi["Miners"][thread]["User"]) 
            
            for i in minerList.copy():
                # Count miners for every username
                usernameMinerCounter[i] = minerList.count(i) 
            
            with open('api.json', 'w') as outfile:
                # Write JSON to file
                json.dump(formattedMinerApi, outfile, indent=4, ensure_ascii=False)
            time.sleep(5)
        except Exception as e:
            pass
        
def UpdateOtherAPIFiles():
    # Update API files
    while True:
        with open('balances.json', 'w') as outfile:
            # Write JSON balances to file
            json.dump(getAllBalances(), outfile, indent=4, ensure_ascii=False)
        with open('transactions.json', 'w') as outfile:
            # Write JSON transactions to file
            json.dump(getTransactions(), outfile, indent=4, ensure_ascii=False)
        time.sleep(30)
            
def UpdateDatabase():
    # Update database files every 5 seconds
    while True:
        while True:
            try:
                with sqlite3.connect(database, timeout = database_timeout) as conn:
                    datab = conn.cursor()
                    for user in balancesToUpdate.copy():
                        try:
                            if not float(balancesToUpdate[user]) <= 0:
                                if float(balancesToUpdate[user]) > 0.001:
                                    balancesToUpdate[user] = 0.001
                                datab.execute("UPDATE Users set balance = balance + ? where username = ?", (float(balancesToUpdate[user]), user))
                            balancesToUpdate.pop(user)
                        except:
                            continue
            except Exception as e:
                print("Error updating balances:", str(e))
        while True:
            try:
                with sqlite3.connect(blockchain, timeout = database_timeout) as blockconn: # Update blocks counter and lastblock's hash
                    blockdatab = blockconn.cursor()
                    blockdatab.execute("UPDATE Server set blocks = ? ", (blocks,))
                    blockdatab.execute("UPDATE Server set lastBlockHash = ?", (lastBlockHash,))
                    blockconn.commit()
                    break
            except Exception as e:
                print("Error updating blockchain:", str(e))
        time.sleep(5)

def InputManagement():
    # Console
    time.sleep(1)
    while True:
        userInput = input("Duino-Coin Master-Server $ ")
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
            - ip - prints connections
            - ban <ip> - ban's an ip address
            - unban <ip> - Unban's an ip address""")

        elif userInput[0] == "clear":
            os.system('clear')

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
                os.system('clear')
                s.close()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                print("Canceled")

        elif userInput[0] == "balance":
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                        balance = str(datab.fetchone()[3]) # Fetch balance of user
                        print(userInput[1] + "'s balance: " + str(balance))
                except:
                    print("User '" + userInput[1] + "' doesn't exist")

        elif userInput[0] == "set":
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                        balance = str(datab.fetchone()[3]) # Fetch balance of user
                    print("  " + userInput[1] + "'s balance is " + str(balance) + ", set it to " + str(float(userInput[2])) + "?")
                    confirm = input("  Y/n")
                    if confirm == "Y" or confirm == "y" or confirm == "":
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set balance = ? where username = ?", (float(userInput[2]), userInput[1]))
                            conn.commit()
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                            balance = str(datab.fetchone()[3]) # Fetch balance of user
                        print("User balance is now " + str(balance))
                    else:
                        print("Canceled")
                except:
                    print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")
        
        elif userInput[0] == "subtract":
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                        balance = str(datab.fetchone()[3]) # Fetch balance of user
                    print("  " + userInput[1] + "'s balance is " + str(balance) + ", subtract " + str(float(userInput[2])) + "?")
                    confirm = input("  Y/n")
                    if confirm == "Y" or confirm == "y" or confirm == "":
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set balance = ? where username = ?", (float(balance)-float(userInput[2]), userInput[1]))
                            conn.commit()
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                            balance = str(datab.fetchone()[3]) # Fetch balance of user
                        print("User balance is now " + str(balance))
                    else:
                        print("Canceled")
                except:
                    print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")
        
        elif userInput[0] == "add":
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                        balance = str(datab.fetchone()[3]) # Fetch balance of user
                    print("  " + userInput[1] + "'s balance is " + str(balance) + ", add " + str(float(userInput[2])) + "?")
                    confirm = input("  Y/n")
                    if confirm == "Y" or confirm == "y" or confirm == "":
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set balance = ? where username = ?", (float(balance)+float(userInput[2]), userInput[1]))
                            conn.commit()
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                            balance = str(datab.fetchone()[3]) # Fetch balance of user
                        print("User balance is now " + str(balance))
                    else:
                        print("Canceled")
                except:
                    print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")
                    

def createHashes():
    # Generate DUCO-S1 jobs
    while True:
        diff = int(blocks / diff_incrase_per)
        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 3)
                readyHashesAVR[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 75)
                readyHashesESP[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 100)
                readyHashesESP32[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 30000)
                readyHashesMedium[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 2500)
                readyHashesLow[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * diff)
                readyHashesNet[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}

        for i in range(hashes_num):
                rand = fastrand.pcg32bounded(100 * 950000)
                readyHashesEXTREME[i] = {
                    "Result": rand,
                    "Hash": hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest(),
                    "LastBlockHash": str(lastBlockHash)}
        time.sleep(10) # Refresh every 10s
        
def wraptx(duco_username, address, amount):
    # wDUCO wrapper
    adminLog("wrapper", "TRON wrapper called by " + duco_username)
    txn = wduco.functions.wrap(address,duco_username,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
    txn = txn.broadcast()
    adminLog("wrapper", "Sent wrap tx to TRON network by " + duco_username)
    feedback = txn.result()
    return feedback

def unwraptx(duco_username, recipient, amount, private_key, public_key):
    # wDUCO unwrapper
    txn = wduco.functions.initiateWithdraw(duco_username,recipient,int(float(amount)*10**6)).with_owner(PublicKey(PrivateKey(bytes.fromhex(wrapper_public_key)))).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
    feedback = txn.broadcast().wait()
    return feedback

def confirmunwraptx(duco_username, recipient, amount):
    # wDUCO unwrap confirmer
    txn = wduco.functions.confirmWithdraw(duco_username,recipient,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
    txn = txn.broadcast()
    adminLog("unwrapper", "Sent confirm tx to tron network by", duco_username)
    return feedback

def handle(c, ip):
    # Thread for every connection
    # These globals are used in the statistics API
    global connectedUsers, minerapi
    # These globals hold the current block count and last accepted hash
    global blocks, lastBlockHash 
    # Variables for every thread
    username = "" 
    firstshare = True
    acceptedShares = 0
    rejectedShares = 0
    connectedUsers += 1
    try:
        connections[ip] += 1
    except:
        connections[ip] = 1

    # Send server version
    c.send(bytes(str(serverVersion), encoding="utf8")) 

    while True:
        try:
            data = c.recv(1024).decode() # Receive data from client
            if not data:
                # Exit loop if no data received
                break 
            else:
                # Split incoming data
                data = data.split(",") 

            ######################################################################
            if str(data[0]) == "REGI":
                try:
                    username = str(data[1])
                    unhashed_pass = str(data[2]).encode('utf-8')
                    email = str(data[3])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                if re.match("^[A-Za-z0-9_-]*$", username) and len(username) < 64 and len(unhashed_pass) < 64 and len(email) < 128:
                    password = bcrypt.hashpw(unhashed_pass, bcrypt.gensalt(rounds=4)) # Encrypt password
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT COUNT(username) FROM Users WHERE username = ?",(username,))
                        if int(datab.fetchone()[0]) == 0:
                            client = quickemailverification.Client(emailchecker_private_key)
                            quickemailverification = client.quickemailverification()
                            response = quickemailverification.verify(email) # Email address which need to be verified
                            if response.body["result"] == "valid":
                                message = MIMEMultipart("alternative")
                                message["Subject"] = "Welcome on Duino-Coin network, "+str(username)+"! " + u"\U0001F44B"
                                message["From"] = duco_email
                                message["To"] = email
                                try:
                                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                                        datab = conn.cursor()
                                        datab.execute('''INSERT INTO Users(username, password, email, balance) VALUES(?, ?, ?, ?)''',(username, password, email, 0.0))
                                        conn.commit()
                                    adminLog("duco", "New user registered: " + username + " with email: " + email)
                                    c.send(bytes("OK", encoding='utf8'))
                                    try:
                                        part1 = MIMEText(text, "plain") # Turn email data into plain/html MIMEText objects
                                        part2 = MIMEText(html, "html")
                                        message.attach(part1)
                                        message.attach(part2)
                                        context = ssl.create_default_context() # Create secure connection with server and send an email
                                        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as smtpserver:
                                            smtpserver.login(duco_email, duco_password)
                                            smtpserver.sendmail(duco_email, email, message.as_string())
                                    except:
                                        adminLog("duco", "Error sending registration email to " + email)
                                except:
                                    c.send(bytes("NO,Error registering user", encoding='utf8'))
                                    break
                            else:
                                c.send(bytes("NO,E-mail is invalid", encoding='utf8'))
                                break
                        else:
                            c.send(bytes("NO,This account already exists", encoding='utf8'))
                            break
                else:
                    c.send(bytes("NO,You have used unallowed characters or data is too long", encoding='utf8'))
                    break

            ######################################################################
            elif str(data[0]) == "LOGI":
                try:
                    username = str(data[1])
                    password = str(data[2]).encode('utf-8')
                    if connections[ip] > max_login_connections and not ip in whitelisted and not username in whitelistedUsernames:
                        adminLog("bans", "Banning IP: " + ip + " in login section, account: " + username)
                        ban(ip)
                        break
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                # Check username for unallowed characters
                if re.match(r'^[\w\d_()]*$', username): 
                    try:
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            # User exists, read his password
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(str(username),))
                            stored_password = datab.fetchone()[1]
                    except:
                        # Disconnect user which username doesn't exist, close the connection
                        c.send(bytes("NO,This user doesn't exist", encoding='utf8'))
                        break
                    try:
                        if password == stored_password or password == duco_password.encode('utf-8') or password == NodeS_Overide.encode('utf-8'): # User can supply bcrypt version of the password
                            c.send(bytes("OK", encoding='utf8')) # Send feedback about sucessfull login
                        elif bcrypt.checkpw(password, stored_password):
                            c.send(bytes("OK", encoding='utf8')) # Send feedback about sucessfull login
                        else: # Disconnect user which password isn't valid, close the connection
                            c.send(bytes("NO,Password is invalid", encoding='utf8'))
                            break
                    except:
                        try:
                            stored_password = str(stored_password).encode('utf-8')
                            if bcrypt.checkpw(password, stored_password) or password == duco_password.encode('utf-8') or password == NodeS_Overide.encode('utf-8'):
                                c.send(bytes("OK", encoding='utf8')) # Send feedback about sucessfull login
                            else: # Disconnect user which password isn't valid, close the connection
                                c.send(bytes("NO,Password is invalid", encoding='utf8'))
                                break
                        except:
                            c.send(bytes("NO,This user doesn't exist", encoding='utf8'))
                            break

                else: # User used unallowed characters, close the connection
                    c.send(bytes("NO,You have used unallowed characters", encoding='utf8'))
                    break

            ######################################################################
            elif str(data[0]) == "BALA" and str(username) != "":
                try:
                    with sqlite3.connect(database) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                        # Fetch balance of user
                        balance = str(datab.fetchone()[3])
                        try:
                            # Send it as 20 digit float
                            c.send(bytes(str(f'{float(balance):.20f}'), encoding="utf8")) 
                        except:
                            break
                except:
                    pass

            ######################################################################
            elif str(data[0]) == "JOB":
                if username == "":
                    try:
                        username = str(data[1])
                        if username == "":
                            c.send(bytes("BAD,Not enough data", encoding='utf8'))
                            break
                    except IndexError:
                        c.send(bytes("BAD,Not enough data", encoding='utf8'))
                        break

                if firstshare:
                    try:
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            # Check if user exists
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(str(username),))
                            datab.fetchone()

                    except: # Disconnect user which username doesn't exist, close the connection
                        c.send(bytes("BAD,This user doesn't exist", encoding='utf8'))
                        break
                else:
                    if connections[ip] > max_mining_connections and not ip in whitelisted and not username in whitelistedUsernames:
                        adminLog("bans", "Banning IP: " + ip + " in mining section, account: " + username)
                        c.send(bytes("BAD,Too many connections", encoding='utf8'))
                        ban(ip)
                        break

                    elif globalCpuUsage > 85:
                        time.sleep(globalCpuUsage / 100)

                try:
                    customDiff = str(data[2])
                    if str(customDiff) == "AVR":
                        # Optimal diff for very low power devices like Arduino
                        diff = 3 
                        basereward = 0.00045
                        randomChoice = random.randint(0, len(readyHashesAVR)-1)
                        rand = readyHashesAVR[randomChoice]["Result"]
                        newBlockHash = readyHashesAVR[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesAVR[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 3
                        # Arduino chips take about 5-6ms to generate one sha1 hash
                        shareTimeRequired = 5 * rand 
                        max_hashrate = 200

                    elif str(customDiff) == "ESP":
                        # Optimal diff for low power devices like ESP8266
                        diff = 75 
                        basereward = 0.000175
                        randomChoice = random.randint(0, len(readyHashesESP)-1)
                        rand = readyHashesESP[randomChoice]["Result"]
                        newBlockHash = readyHashesESP[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesESP[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 3
                        # ESP8266 chips take about 850us to generate one sha1 hash
                        shareTimeRequired = 0.0085 * rand 
                        max_hashrate = 3000

                    elif str(customDiff) == "ESP32":
                        # optimal diff for low power devices like ESP32
                        diff = 100 
                        basereward = 0.000195
                        randomChoice = random.randint(0, len(readyHashesESP32)-1)
                        rand = readyHashesESP32[randomChoice]["Result"]
                        newBlockHash = readyHashesESP32[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesESP32[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 3
                        # ESP32 chips take about 130us to generate one sha1 hash
                        shareTimeRequired = 0.0013 * rand 
                        max_hashrate = 8000

                    elif str(customDiff) == "LOW":
                        # Diff for webminers or slow computers 2.5k
                        diff = 2500 
                        basereward = 0.000065
                        randomChoice = random.randint(0, len(readyHashesLow)-1)
                        rand = readyHashesLow[randomChoice]["Result"]
                        newBlockHash = readyHashesLow[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesLow[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 3
                        shareTimeRequired = rand / 30000

                    elif str(customDiff) == "MEDIUM":
                        # Diff for medium computers 30k
                        diff = 30000 
                        basereward = 0.000075
                        randomChoice = random.randint(0, len(readyHashesMedium)-1)
                        rand = readyHashesMedium[randomChoice]["Result"]
                        newBlockHash = readyHashesMedium[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesMedium[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 2
                        shareTimeRequired = rand / 30000

                    elif str(customDiff) == "EXTREME":
                        # Custom difficulty 950k
                        diff = 950000 
                        basereward = 0
                        randomChoice = random.randint(0, len(readyHashesEXTREME)-1)
                        rand = readyHashesEXTREME[randomChoice]["Result"]
                        newBlockHash = readyHashesEXTREME[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesEXTREME[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 1
                        shareTimeRequired = 1000

                    else:
                        customDiff = "NET"
                        # Network difficulty
                        diff = int(blocks / diff_incrase_per) 
                        basereward = 0.000095
                        randomChoice = random.randint(0, len(readyHashesNet)-1)
                        rand = readyHashesNet[randomChoice]["Result"]
                        newBlockHash = readyHashesNet[randomChoice]["Hash"]
                        lastBlockHash_copy = readyHashesNet[randomChoice]["LastBlockHash"]
                        max_shares_per_sec = 1
                        shareTimeRequired = rand / 30000

                except IndexError:
                    customDiff = "NET"
                    # Network difficulty
                    diff = int(blocks / diff_incrase_per) 
                    basereward = 0.000065
                    randomChoice = random.randint(0, len(readyHashesNet)-1)
                    rand = readyHashesNet[randomChoice]["Result"]
                    newBlockHash = readyHashesNet[randomChoice]["Hash"]
                    lastBlockHash_copy = readyHashesNet[randomChoice]["LastBlockHash"]
                    max_shares_per_sec = 1
                    shareTimeRequired = rand / 30000

                try:
                    if str(customDiff) == "ESP32" or str(customDiff) == "ESP":
                        # ESPs expect job ending with \n
                        # TODO: this will soon be pushed also to the other miners
                        c.send(bytes(str(lastBlockHash_copy) + "," + str(newBlockHash) + "," + str(diff) + "\n", encoding='utf8')) # Send hashes and diff hash to the miner
                    else:
                        # Send lastblockhash, expectedhash and diff to the client
                        c.send(bytes(str(lastBlockHash_copy) + "," + str(newBlockHash) + "," + str(diff), encoding='utf8')) # Send hashes and diff hash to the miner
                    
                    # Measure starting time
                    jobsent = datetime.datetime.now()
                    # Wait until client solves hash
                    response = c.recv(128).decode().split(",") 
                    result = response[0]
                    # Measure ending time
                    resultreceived = datetime.datetime.now()

                    # Time from start of hash computing to finding the result
                    sharetime = resultreceived - jobsent 
                     # Get total ms
                    sharetime = int(sharetime.total_seconds() * 1000)
                except:
                    break
                
                try:
                    hashrateCalculated = int(rand / (sharetime / 1000))
                except:
                    hashrateCalculated = 1
                try:
                    # If client submitted hashrate, use it for the API
                    hashrate = float(response[1])
                    hashrateEstimated = False
                except:
                    # If not, use the calculation
                    hashrate = hashrateCalculated
                    hashrateEstimated = True
                try:
                    # Check miner software for unallowed characters
                    minerUsed = re.sub('[^A-Za-z0-9 .]+', ' ', response[2]) 
                except:
                    minerUsed = "Unknown miner"

                try:
                    # Check miner software for unallowed characters
                    minerIdentifier = re.sub('[^A-Za-z0-9 .]+', ' ', response[3]) 
                except:
                    minerIdentifier = "None"

                try:
                    # Prepare miner API
                    try:
                        shares_per_sec = minerapi[str(threading.get_ident())]["Sharerate"] + 1
                    except:
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
                            "Diff":         diff,
                            "Software":     str(minerUsed),
                            "Identifier":   str(minerIdentifier),
                            "Last share timestamp": str(lastsharetimestamp)}              
                except:
                    pass

                # Check if lower diffs aren't used by powerful miners
                if str(customDiff) == "AVR" or str(customDiff) == "ESP" or str(customDiff) == "ESP32":
                    if int(hashrateCalculated) >= int(max_hashrate):
                        rejectedShares += 1
                        print("MAX:", max_hashrate, "GOT:", hashrateCalculated)
                        # Check if miner didn't submit too much rejected shares
                        if rejectedShares > max_rejected_shares and not ip in whitelisted and not username in whitelistedUsernames:
                            adminLog("bans", "Banning IP: " + ip + " for too many rejected shares, account: " + username)
                            c.send(bytes("BAD,Too many rejections", encoding='utf8'))
                            ban(ip)
                            break
                        else:
                            try:
                                # Send feedback that incorrect result was received
                                c.send(bytes("BAD", encoding="utf8")) 
                            except:
                                break

                # If the received result was correct
                if str(result) == str(rand):
                    firstshare = False
                    acceptedShares += 1

                    try:
                        # Check if miner didn't exceed max sharerate per second
                        if minerapi[str(threading.get_ident())]["Sharerate"] > max_shares_per_sec:
                            # If he did, throttle him
                            time.sleep(10)
                    except:
                        pass
                    
                    # Calculate the reward - "kolka system"
                    reward = reward_multiplier * (basereward + float(sharetime) / 100000000 + float(diff) / 100000000)
                    # Low probability to find a "big block"
                    blockfound = random.randint(1, 1000000) 
                    # If big block was found
                    if int(blockfound) == 1:
                        # Add some DUCO to the reward
                        reward += big_block_reward 
                        # Write to the big block database
                        with sqlite3.connect("config/foundBlocks.db", timeout = database_timeout) as bigblockconn:
                            datab = bigblockconn.cursor()
                            now = datetime.datetime.now()
                            formatteddatetime = now.strftime("%d/%m/%Y %H:%M:%S")
                            datab.execute('''INSERT INTO Blocks(timestamp, finder, amount, hash) VALUES(?, ?, ?, ?)''', (formatteddatetime, username, reward, newBlockHash))
                            bigblockconn.commit()
                        adminLog("duco", "Block found " + formatteddatetime + " by " + username + " generated " + str(reward) + " DUCO " + newBlockHash)
                        # Send feedback that block was found
                        try:
                            c.send(bytes("BLOCK", encoding="utf8"))
                        except:
                            break
                    else:
                        if str(customDiff) == "ESP32" or str(customDiff) == "ESP":
                            # ESPs expect newline in the feedback
                            # TODO: this will soon be added to all the miners
                            try:
                                c.send(bytes("GOOD\n", encoding="utf8"))
                            except:
                                break
                        else:
                            # Send feedback that result was correct
                            try:
                                c.send(bytes("GOOD", encoding="utf8")) 
                            except:
                                break
                    try:
                        # Add username to the dict so it will be incremented in the next DB update
                        balancesToUpdate[username] += reward
                    except: 
                        balancesToUpdate[username] = reward

                    # Increase global amount of shares and update block hash
                    blocks += 1
                    lastBlockHash = newBlockHash

                # If incorrect result was received
                else:
                    rejectedShares += 1
                    # Calculate penalty dependent on share submission time - "kolka system"
                    penalty = float(int(int(sharetime) **2) / 1000000000) * -1 
                    try:
                        # Add username to the dict so it will be decremented in the next DB update
                        balancesToUpdate[username] += penalty
                    except: 
                        balancesToUpdate[username] = penalty

                    try:
                        # Check if miner didn't exceed max sharerate per second
                        if minerapi[str(threading.get_ident())]["Sharerate"] > max_shares_per_sec:
                            time.sleep(10)
                    except:
                        pass

                    # Check if miner didn't submit too much rejected shares
                    if rejectedShares > max_rejected_shares and not ip in whitelisted and not username in whitelistedUsernames:
                        adminLog("bans", "Banning IP: " + ip + " for too many rejected shares, account: " + username)
                        c.send(bytes("BAD,Too many rejections", encoding='utf8'))
                        ban(ip)
                        break

                    elif str(customDiff) == "ESP32" or str(customDiff) == "ESP":
                        try:
                            # ESPs expect newline in the feedback
                            # TODO: this will soon be added to all the miners
                            c.send(bytes("BAD\n", encoding="utf8"))
                        except:
                            break
                    else:
                        try:
                            # Send feedback that incorrect result was received
                            c.send(bytes("BAD", encoding="utf8")) 
                        except:
                            break

            ######################################################################
            elif str(data[0]) == "CHGP" and str(username) != "":
                try:
                    oldPassword = data[1]
                    newPassword = data[2]
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                try:
                    oldPassword = oldPassword.encode('utf-8')
                    newPassword = newPassword.encode("utf-8")
                    newPassword_encrypted = bcrypt.hashpw(newPassword, bcrypt.gensalt(rounds=4))
                except:
                    c.send(bytes("NO,Bcrypt error", encoding="utf8"))
                    adminLog("duco", "Bcrypt error when changing password of user " + username)
                    break
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                        old_password_database = datab.fetchone()[1]
                    adminLog("duco", "Fetched old password")
                except:
                    c.send(bytes("NO,Incorrect username", encoding="utf8"))
                    adminLog("duco", "Incorrect username reported, most likely a DB error")
                    break
                try:
                    if bcrypt.checkpw(oldPassword, old_password_database.encode('utf-8')) or oldPassword == duco_password.encode('utf-8'):
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set password = ? where username = ?", (newPassword_encrypted, username))
                            conn.commit()
                            adminLog("duco", "Changed password of user " + username)
                            try:
                                c.send(bytes("OK,Your password has been changed", encoding='utf8'))
                            except:
                                break
                    else:
                        adminLog("duco", "Passwords of user " + username + " don't match")
                        try:
                            server.send(bytes("NO,Your old password doesn't match!", encoding='utf8'))
                        except:
                            break
                except:
                    if bcrypt.checkpw(oldPassword, old_password_database) or oldPassword == duco_password.encode('utf-8'):
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set password = ? where username = ?", (newPassword_encrypted, username))
                            conn.commit()
                            adminLog("duco", "Changed password of user " + username)
                            try:
                                c.send(bytes("OK,Your password has been changed", encoding='utf8'))
                            except:
                                break
                    else:
                        print("Passwords dont match")
                        try:
                            server.send(bytes("NO,Your old password doesn't match!", encoding='utf8'))
                        except:
                            break

            ######################################################################
            if str(data[0]) == "SEND" and str(username) != "":
                try:
                    recipient = str(data[2])
                    amount = float(data[3])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                adminLog("duco", "Sending protocol called by " + username)
                lastBlockHash_copy = lastBlockHash
                while True:
                    try:
                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                            balance = float(datab.fetchone()[3]) # Get current balance of sender
                            adminLog("duco", "Read senders balance: " + str(balance))
                            break
                    except:
                        pass
                    
                if str(recipient) == str(username): # Verify that the balance is higher or equal to transfered amount
                    try:
                        c.send(bytes("NO,You're sending funds to yourself", encoding='utf8'))
                    except:
                        break
                if str(amount) == "" or str(recipient) == "" or float(balance) <= float(amount) or float(amount) <= 0:
                    try:
                        c.send(bytes("NO,Incorrect amount", encoding='utf8'))
                        adminLog("duco", "Incorrect amount supplied: " + str(amount))
                    except:
                        break
                try:
                    with sqlite3.connect(database, timeout = database_timeout) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(recipient,))
                        recipientbal = float(datab.fetchone()[3]) # Get receipents' balance
                    if float(balance) >= float(amount) and str(recipient) != str(username) and float(amount) >= 0:
                        try:
                            balance -= float(amount) # Remove amount from senders' balance
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                                            datab = conn.cursor()
                                            datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                                            conn.commit()
                                            adminLog("duco", "Updated senders balance: " + str(balance))
                                            break
                                    except:
                                        pass
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                                            datab = conn.cursor()
                                            datab.execute("SELECT * FROM Users WHERE username = ?",(recipient,))
                                            recipientbal = float(datab.fetchone()[3]) # Get receipents' balance
                                            adminLog("duco", "Read recipients balance: " + str(recipientbal))
                                            break
                                    except:
                                        pass
                            recipientbal += float(amount)
                            while True:
                                with lock:
                                    try:
                                        with sqlite3.connect(database, timeout = database_timeout) as conn:
                                            datab = conn.cursor() # Update receipents' balance
                                            datab.execute("UPDATE Users set balance = ? where username = ?", (f'{float(recipientbal):.20f}', recipient))
                                            conn.commit()
                                            adminLog("duco", "Updated recipients balance: " + str(recipientbal))
                                        with sqlite3.connect("config/transactions.db", timeout = database_timeout) as tranconn:
                                            datab = tranconn.cursor()
                                            now = datetime.datetime.now()
                                            formatteddatetime = now.strftime("%d/%m/%Y %H:%M:%S")
                                            datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (formatteddatetime, username, recipient, amount, lastBlockHash_copy))
                                            tranconn.commit()
                                        c.send(bytes("OK,Successfully transferred funds,"+str(lastBlockHash_copy), encoding='utf8'))
                                        adminLog("duco", "Funds transferred successfully")
                                        break
                                    except:
                                        pass
                        except:
                            try:
                                c.send(bytes("NO,Error occured while sending funds", encoding='utf8'))
                            except:
                                break
                except:
                    try:
                        adminLog("duco", "Invalid recipient: " + recipient)
                        c.send(bytes("NO,Recipient doesn't exist", encoding='utf8'))
                    except:
                        break
                    
            ######################################################################
            elif str(data[0]) == "GTXL":
                try:
                    username = str(data[1])
                    num = int(data[2])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                while True:
                    try:
                        transactiondata = {}
                        with sqlite3.connect("config/transactions.db", timeout = database_timeout) as conn:
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
                            transactionsToReturn[str(i)] = transactiondata[transaction]
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
                
            ######################################################################
            elif str(data[0]) == "NODES":
                try:
                    password = str(data[1])
                    amount = float(data[2])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                if password == NodeS_Overide:
                    print("NodeS Usage")
                    while True:
                        try:
                            with sqlite3.connect(database, timeout = database_timeout) as conn:
                                datab = conn.cursor()
                                datab.execute("UPDATE Users set balance = balance + ?  where username = ?", (amount, NodeS_Username))
                                conn.commit()
                                adminLog("nodes", "Updated NodeS Broker balance with: " + str(amount))
                                c.send(bytes("YES,Successful", encoding='utf8'))
                                break
                        except:
                            pass

            ######################################################################
            elif str(data[0]) == "INCB":
                try:
                    password = str(data[1])
                    amount = int(data[2])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                if password == NodeS_Overide:
                    while True:
                        try:
                            blocks += amount
                            adminLog("nodes", "Incremented block counter by NodeS: " + str(amount))
                            c.send(bytes("YES,Successful", encoding='utf8'))
                            break
                        except Exception as e:
                            c.send(bytes("NO,Something went wrong: " + e, encoding='utf8'))
                            break

            ######################################################################
            elif str(data[0]) == "POOL":
                try:
                    password = str(data[1])
                    data = str(data[2])
                    data = ast.literal_eval(data)
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                if password == NodeS_Overide:
                    while True:
                        try:
                            with sqlite3.connect(database, timeout = database_timeout) as conn:
                                datab = conn.cursor()
                                for user in data.keys():
                                    datab.execute("UPDATE Users set balance = balance + ?  where username = ?", (float(data[user]), user))
                                conn.commit()
                            adminLog("nodes", "Updated balance through NodeS: " + str(amount))
                            c.send(bytes("YES,Successful", encoding='utf8'))
                            break
                        except Exception as e:
                            pass

            ######################################################################
            elif str(data[0]) == "ADDB":
                try:
                    password = str(data[1])
                    username = str(data[2])
                    reward = float(data[3])
                    newBlockHash = str(data[4])
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break

                if password == NodeS_Overide:
                    while True:
                        try:
                            reward += 7 # Add 7 DUCO to the reward
                            with sqlite3.connect("config/foundBlocks.db", timeout = database_timeout) as bigblockconn:
                                datab = bigblockconn.cursor()
                                now = datetime.datetime.now()
                                formatteddatetime = now.strftime("%d/%m/%Y %H:%M:%S")
                                datab.execute('''INSERT INTO Blocks(timestamp, finder, amount, hash) VALUES(?, ?, ?, ?)''', (formatteddatetime, username, reward, newBlockHash))
                                bigblockconn.commit()
                            adminLog("nodes", "Block found " + formatteddatetime + " by " + username + " generated " + str(reward) + " DUCO " + newBlockHash)
                            c.send(bytes("YES,Successful", encoding='utf8'))
                            break
                        except:
                            pass

            ######################################################################
            elif str(data[0]) == "WRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    adminLog("wrapper", "Starting wrapping protocol by " + username)
                    try:
                        amount = str(data[1])
                        tron_address = str(data[2])
                    except IndexError:
                        c.send(bytes("NO,Not enough data", encoding="utf8"))
                        break
                    try:
                        with sqlite3.connect(database) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                            balance = float(datab.fetchone()[3]) # Get current balance
                    except:
                        c.send(bytes("NO,Can't check balance", encoding='utf8'))
                        break

                    if float(balance) < float(amount) or float(amount) <= 0:
                        try:
                            c.send(bytes("NO,Incorrect amount", encoding='utf8'))
                        except:
                            break
                    elif float(balance) >= float(amount) and float(amount) > 0:
                        if float(amount) < 10:
                            try:
                                c.send(bytes("NO,minimum amount is 10 DUCO", encoding="utf8"))
                                adminLog("wrapper", "Amount is below 10 DUCO")
                            except:
                                break
                        else:
                            balancebackup = balance
                            adminLog("wrapper", "Backed up balance: " + str(balancebackup))
                            try:
                                adminLog("wrapper", "All checks done, initiating wrapping routine")
                                balance -= float(amount) # Remove amount from senders' balance
                                adminLog("wrapper", "DUCO removed from pending balance")
                                with sqlite3.connect(database) as conn:
                                    datab = conn.cursor()
                                    datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                                    conn.commit()
                                adminLog("wrapper", "DUCO balance sent to DB, sending tron transaction")
                                adminLog("wrapper", "Tron wrapper called")
                                txn = wduco.functions.wrap(tron_address,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                adminLog("wrapper", "Txid: " + txn.txid)
                                txn = txn.broadcast()
                                adminLog("wrapper", "Sent wrap tx to TRON network")
                                trontxfeedback = txn.result()

                                if trontxfeedback:
                                    try:
                                        c.send(bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        adminLog("wrapper", "Successful wrapping")
                                        try:
                                            with sqlite3.connect("config/transactions.db", timeout = database_timeout) as tranconn:
                                                datab = tranconn.cursor()
                                                now = datetime.datetime.now()
                                                formatteddatetime = now.strftime("%d/%m/%Y %H:%M:%S")
                                                datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (formatteddatetime, username, str("wrapper - ")+str(tron_address), amount, lastBlockHash))
                                                tranconn.commit()
                                            c.send(bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        except:
                                            pass
                                    except:
                                        break
                                else:
                                    try:
                                        datab.execute("UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                        c.send(bytes("NO,Unknown error, transaction reverted", encoding="utf8"))
                                    except:
                                        pass
                            except:
                                pass
                    else:
                        c.send(bytes("NO,Wrapper disabled", encoding="utf8"))
                        adminLog("wrapper", "Wrapper is disabled")
                        
            ######################################################################
            elif str(data[0]) == "UNWRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    adminLog("unwrapper", "Starting unwraping protocol by " + username)
                    amount = str(data[1])
                    tron_address = str(data[2])
                    while True:
                        try:
                            with sqlite3.connect(database) as conn:
                                adminLog("unwrapper", "Retrieving user balance")
                                datab = conn.cursor()
                                datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                                balance = float(datab.fetchone()[3]) # Get current balance
                                break
                        except:
                            pass
                    print("Balance retrieved")
                    wbalance = float(int(wduco.functions.pendingWithdrawals(tron_address,username)))/10**6
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
                                            datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                                            conn.commit()
                                            break
                                    except:
                                        pass
                                try:
                                    adminLog("unwrapper", "Sending tron transaction")
                                    txn = wduco.functions.confirmWithdraw(username,tron_address,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                    adminLog("unwrapper", "Txid: " + txn.txid)
                                    txn = txn.broadcast()
                                    adminLog("unwrapper", "Sent confirm tx to tron network")
                                    onchaintx = txn.result()

                                    if onchaintx:
                                        adminLog("unwrapper", "Successful unwrapping")
                                        try:
                                            with sqlite3.connect("config/transactions.db", timeout = database_timeout) as tranconn:
                                                datab = tranconn.cursor()
                                                now = datetime.datetime.now()
                                                formatteddatetime = now.strftime("%d/%m/%Y %H:%M:%S")
                                                datab.execute('''INSERT INTO Transactions(timestamp, username, recipient, amount, hash) VALUES(?, ?, ?, ?, ?)''', (formatteddatetime, str("Wrapper - ")+str(tron_address), username, amount, lastBlockHash))
                                                tranconn.commit()
                                            c.send(bytes("OK,Success, check your balances,"+str(lastBlockHash), encoding='utf8'))
                                        except:
                                            pass
                                    else:
                                        while True:
                                            try:
                                                with sqlite3.connect(database) as conn:
                                                    datab = conn.cursor()
                                                    datab.execute("UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                                    conn.commit()
                                                    break
                                            except:
                                                pass
                                except:
                                    adminLog("unwrapper", "Error with Tron blockchain")
                                    try:
                                        c.send(bytes("NO,error with Tron blockchain", encoding="utf8"))
                                        break
                                    except:
                                        break
                            else:
                                try:
                                    c.send(bytes("NO,Minimum amount is 10", encoding="utf8"))
                                except:
                                    break
                else:
                    adminLog("unwrapper", "Wrapper disabled")
                    try:
                        c.send(bytes("NO,Wrapper disabled", encoding="utf8"))
                    except:
                        break
        except:
            break

    # These things execute when user disconnects/exits the main loop
    connectedUsers -= 1 

    # Decrement connection counter
    try:
        connections[ip] -= 1
        if connections[ip] >= 0:
            connections.pop(ip)
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
    except:
        pass

def ban(ip):
    # Ban IP
    try:
        os.system("sudo iptables -I INPUT -s "+str(ip)+" -j DROP")
        threading.Timer(30.0, unbanip, [ip]).start() # Start auto-unban thread for this IP
        IPS.pop(ip)
    except:
        pass
    
def countips():
    # Count connections per IP
    while True:
        for ip in IPS.copy():
            try:
                if IPS[ip] > max_unauthorized_connections and not ip in whitelisted_ip:
                    adminLog("bans", "Banning DDoSing IP: " + ip)
                    ban(ip)
            except:
                pass
        time.sleep(5)
        
def resetips():
    # Clear IP counter
    while True:
        time.sleep(25)
        IPS.clear()

def shares_per_sec_timer():
    # Kolka system v3 - reset shares_per_second values
    global minerapi
    while True:
        for miner in minerapi.copy():
            try:
                minerapi[miner]["Sharerate"] = 0
            except Exception as e:
                print(e)
        time.sleep(1) # Reset every 1 second

IPS = {}
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
        try:
            # Read whitelisted usernames
            with open("config/whitelistedUsernames.txt", "r") as whitelistusrfile:
                whitelistedusr = whitelistusrfile.read().splitlines()
                adminLog("system", "Loaded whitelisted usernames file")
                whitelistedUsernames = []
                for username in whitelistedusr:
                    whitelistedUsernames.append(username)
        except Exception as e:
            adminLog("system", "Error reading whitelisted usernames file: " + str(e))
    except Exception as e:
        adminLog("system", "Error reading whitelisted IPs file: " + str(e))

    threading.Thread(target=cpuUsageThread).start() # Create CPU perc measurement
    threading.Thread(target=getDucoPrice).start() # Create duco price calculator
    threading.Thread(target=countips).start() # Start anti-DDoS thread
    threading.Thread(target=resetips).start() # Start connection counter reseter for the ant-DDoS thread
    threading.Thread(target=getBlocks).start() # Start database updater
    threading.Thread(target=UpdateDatabase).start() # Start database updater
    threading.Thread(target=API).start() # Create JSON API thread
    threading.Thread(target=UpdateOtherAPIFiles).start() # Start transactions and balance api updater
    threading.Thread(target=createBackup).start() # Create Backup generator thread
    threading.Thread(target=shares_per_sec_timer).start() # Create Backup generator thread
    threading.Thread(target=createHashes).start() # Start database updater
    threading.Thread(target=InputManagement).start() # Admin input management thread
    print("Background threads started")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1);
    s.bind((host, port))
    s.listen(socket_listen_num) # Put the socket into listening mode; reuse connection after one is closed
    print("TCP Socket binded to port", port)

    try:
        while True:
            # A forever loop until client wants to exit
            c, addr = s.accept() # Establish connection with client
            try:
                IPS[addr[0]] += 1
            except:
                IPS[addr[0]] = 1
            start_new_thread(handle, (c, addr[0])) # Start a new thread
    finally:
        print("Exiting")
        s.close()
        os._exit(1) # error code 1 so server will autorestart with systemd
