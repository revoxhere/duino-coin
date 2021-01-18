#!/usr/bin/env python3
#############################################
# Duino-Coin Master Server Remastered (v1.9)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
#############################################
import requests, smtplib, sys, ssl, socket, re, math, random, hashlib, datetime,  requests, smtplib, ssl, sqlite3, bcrypt, time, os.path, json, logging, threading
from _thread import *
from shutil import copyfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

host = "" # Server will use this as hostname to bind to (localhost on Windows, 0.0.0.0 on Linux in most cases)
port = 2811 # Server will listen on this port - 2811 for official Duino-Coin server (14808 for old one)
serverVersion = 1.9 # Server version which will be sent to the clients
diff_incrase_per = 2000 # Difficulty will increase every x blocks (official server uses 2k)
duco_email = "xxx" # E-mail and password to send registration mail from
duco_password = "xxx" # E-mail password and admin override password
NodeS_Overide = "xxx" # Node-S override key
wrapper_private_key = "xxx" # private key used for interacting with blockchain
use_wrapper = True # Choosing if you want to use wrapper or not
wrapper_permission = False # set to false for declaration, will be updated by checking smart contract
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
connectedUsers = 0
database = 'crypto_database.db' # User data database location
if not os.path.isfile(database): # Create it if it doesn't exist
    with sqlite3.connect(database, timeout = 15) as conn:
        datab = conn.cursor()
        datab.execute('''CREATE TABLE IF NOT EXISTS Users(username TEXT, password TEXT, email TEXT, balance REAL)''')
blockchain = 'duino_blockchain.db' # Blockchain database location
if not os.path.isfile(blockchain): # Create it if it doesn't exist
    with sqlite3.connect(blockchain, timeout = 15) as blockconn:
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
if use_wrapper:
    import tronpy # tronpy isn't default installed, install it with "pip install tronpy"
    from tronpy.keys import PrivateKey, PublicKey
    wrapper_public_key = PrivateKey(bytes.fromhex(wrapper_private_key)).public_key.to_base58check_address() # wrapper's public key
    tron = tronpy.Tron(network="mainnet")
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U") # wDUCO contract
    wrapper_permission = wduco.functions.checkWrapperStatus(wrapper_public_key)
def createBackup():
    if not os.path.isdir('backups/'):
        os.mkdir('backups/')
    while True:
        today = datetime.date.today()
        if not os.path.isdir('backups/'+str(today)+'/'):
            os.mkdir('backups/'+str(today))
            copyfile(blockchain, "backups/"+str(today)+"/"+blockchain)
            copyfile(database, "backups/"+str(today)+"/"+database)
            with open("prices.txt", "a") as pricesfile:
                pricesfile.write("," + str(round(getDucoPrice(), 4)).rstrip("\n"))
        time.sleep(3600*6) # Run every 6h
def getDucoPrice():
    coingecko = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=magi&vs_currencies=usd", data=None)
    if coingecko.status_code == 200:
        geckocontent = coingecko.content.decode()
        geckocontentjson = json.loads(geckocontent)
        xmgusd = float(geckocontentjson["magi"]["usd"])
    else:
        xmgusd = .015
    ducousdLong = float(xmgusd) * 3.5 * random.randint(97,103) / 100
    ducoPrice = round(float(ducousdLong) / 10, 8) * 0.8
    return ducoPrice
def getRegisteredUsers():
    with sqlite3.connect(database, timeout = 15) as conn:
        datab = conn.cursor()
        datab.execute("SELECT COUNT(username) FROM Users")
        registeredUsers = datab.fetchone()[0]
    return registeredUsers
def getMinedDuco():
    with sqlite3.connect(database, timeout = 15) as conn:
        datab = conn.cursor()
        datab.execute("SELECT SUM(balance) FROM Users")
        allMinedDuco = datab.fetchone()[0]
    return allMinedDuco
def getLeaders():
    leadersdata = []
    with sqlite3.connect(database, timeout = 15) as conn:
        datab = conn.cursor()
        datab.execute("SELECT * FROM Users ORDER BY balance DESC")
        for row in datab.fetchall():
            leadersdata.append(f"{round((float(row[3])), 4)} DUCO - {row[0]}")
    return(leadersdata[:10])
def getCpuUsage():
    import psutil
    while True:
        try:
            cpuperc = psutil.cpu_percent() / 4
            break
        except:
            pass
    return(cpuperc)
def API():
    while True:
        try:
            l = threading.Lock()
            with l:
                with sqlite3.connect(blockchain, timeout = 15) as blockconn:
                    blockdatab = blockconn.cursor()
                    blockdatab.execute("SELECT blocks FROM Server") # Read amount of mined blocks
                    blocks = int(blockdatab.fetchone()[0])
                    blockdatab.execute("SELECT lastBlockHash FROM Server") # Read lastblock's hash
                    lastBlockHash = str(blockdatab.fetchone()[0])
                    diff = math.ceil(blocks / diff_incrase_per) # Calculate difficulty
                now = datetime.datetime.now()
                minerList = []
                usernameMinerCounter = {}
                serverHashrate = 0
                hashrate = 0
                for x in minerapi.copy():
                    lista = minerapi[x] # Convert list to strings
                    hashrate = lista[1]
                    serverHashrate += float(hashrate) # Add user hashrate to the server hashrate
                if serverHashrate >= 1000000:
                    prefix = " MH/s"
                    serverHashrate = serverHashrate / 1000000
                elif serverHashrate >= 1000:
                    prefix = " kH/s"
                    serverHashrate = serverHashrate / 1000
                else:
                    prefix = " H/s"
                formattedMinerApi = { # Prepare server API data
                        "Server version":        float(serverVersion),
                        "Active connections":    int(connectedUsers),
                        "Server CPU usage":      float(getCpuUsage()),
                        "Last update":           str(now.strftime("%d/%m/%Y %H:%M (UTC)")),
                        "Pool hashrate":         str(round(serverHashrate, 2))+prefix,
                        "Duco price":            float(round(getDucoPrice(), 6)), # Call getDucoPrice function
                        "Registered users":      int(getRegisteredUsers()), # Call getRegisteredUsers function
                        "All-time mined DUCO":   float(round(getMinedDuco(), 2)), # Call getMinedDuco function
                        "Current difficulty":    int(diff),
                        "Mined blocks":          int(blocks),
                        "Full last block hash":  str(lastBlockHash),
                        "Last block hash":       str(lastBlockHash)[:10]+"...",
                        "Top 10 richest miners": getLeaders(), # Call getLeaders function
                        "Active workers":        usernameMinerCounter,
                        "Miners": {}}
                for x in minerapi.copy(): # Get data from every miner
                    lista = minerapi[x] # Convert list to strings
                    formattedMinerApi["Miners"][x] = { # Format data
                    "User":          str(lista[0]),
                    "Hashrate":      float(lista[1]),
                    "Is estimated":  str(lista[6]),
                    "Sharetime":     float(lista[2]),
                    "Accepted":      int(lista[3]),
                    "Rejected":      int(lista[4]),
                    "Diff":          int(lista[5]),
                    "Software":      str(lista[7])}
                for thread in formattedMinerApi["Miners"]:
                    minerList.append(formattedMinerApi["Miners"][thread]["User"]) # Append miners to formattedMinerApi["Miners"][id of thread]
                for i in minerList:
                    usernameMinerCounter[i]=minerList.count(i) # Count miners for every username
                with open('api.json', 'w') as outfile: # Write JSON to file
                    json.dump(formattedMinerApi, outfile, indent=4, ensure_ascii=False)
        except:
            pass
        time.sleep(3)

def InputManagement():
    while True:
        userInput = input("DUCO Server ᕲ ")
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
            - restart - restarts DUCO server""")
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
                with sqlite3.connect(database, timeout = 15) as conn:
                    datab = conn.cursor()
                    datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                    balance = str(datab.fetchone()[3]) # Fetch balance of user
                print(userInput[1] + "'s balance: " + str(balance))
            except:
                print("User '" + userInput[1] + "' doesn't exist")
        elif userInput[0] == "set":
            try:
                with sqlite3.connect(database, timeout = 15) as conn:
                    datab = conn.cursor()
                    datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                    balance = str(datab.fetchone()[3]) # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " + str(balance) + ", set it to " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout = 15) as conn:
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
                with sqlite3.connect(database, timeout = 15) as conn:
                    datab = conn.cursor()
                    datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                    balance = str(datab.fetchone()[3]) # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " + str(balance) + ", subtract " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(balance)-float(userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout = 15) as conn:
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
                with sqlite3.connect(database, timeout = 15) as conn:
                    datab = conn.cursor()
                    datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                    balance = str(datab.fetchone()[3]) # Fetch balance of user
                print("  " + userInput[1] + "'s balance is " + str(balance) + ", add " + str(float(userInput[2])) + "?")
                confirm = input("  Y/n")
                if confirm == "Y" or confirm == "y" or confirm == "":
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set balance = ? where username = ?", (float(balance)+float(userInput[2]), userInput[1]))
                        conn.commit()
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(userInput[1],))
                        balance = str(datab.fetchone()[3]) # Fetch balance of user
                    print("User balance is now " + str(balance))
                else:
                    print("Canceled")
            except:
                print("User '" + str(userInput[1]) + "' doesn't exist or you've entered wrong number ("+str(userInput[2])+")")

def handle(c):
    global connectedUsers, minerapi # These globals are used in the statistics API
    c.send(bytes(str(serverVersion), encoding="utf8")) # Send server version
    connectedUsers += 1 # Count new opened connection
    username = "" # Variables for every thread
    lastBlockHash = ""
    acceptedShares = 0
    rejectedShares = 0
    blocks = 0
    blockFound = False

    def wraptx(duco_username, address, amount):
        print("Tron wrapper called !")
        txn = wduco.functions.wrap(address,duco_username,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
        txn = txn.broadcast()
        print("Sent wrap tx to TRON network")
        feedback = txn.wait()
        return feedback

    def unwraptx(duco_username, recipient, amount, private_key, public_key):
        txn = wduco.functions.initiateWithdraw(duco_username,recipient,int(float(amount)*10**6)).with_owner(PublicKey(PrivateKey(bytes.fromhex(wrapper_public_key)))).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
        feedback = txn.broadcast().wait()
        return feedback

    def confirmunwraptx(duco_username, recipient, amount):
        txn = wduco.functions.confirmWithdraw(duco_username,recipient,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
        txn = txn.broadcast()
        print("Sent confirm tx to tron network")
        return feedback

    while True:
        try:
            data = c.recv(1024).decode() # Receive data from client
            if not data:
                break
            else:
                data = data.split(",") # Split incoming data

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
                    password = bcrypt.hashpw(unhashed_pass, bcrypt.gensalt()) # Encrypt password
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT COUNT(username) FROM Users WHERE username = ?",(username,))
                        if int(datab.fetchone()[0]) == 0:
                            if "@" in email and "." in email:
                                message = MIMEMultipart("alternative")
                                message["Subject"] = "Welcome on Duino-Coin network, "+str(username)+"! " + u"\U0001F44B"
                                message["From"] = duco_email
                                message["To"] = email
                                try:
                                    with sqlite3.connect(database, timeout = 15) as conn:
                                        datab = conn.cursor()
                                        datab.execute('''INSERT INTO Users(username, password, email, balance) VALUES(?, ?, ?, ?)''',(username, password, email, 0.0))
                                        conn.commit()
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
                                        print("Error sending registration email")
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
            if str(data[0]) == "LOGI":
                try:
                    username = str(data[1])
                    password = str(data[2]).encode('utf-8')
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                if re.match(r'^[\w\d_()]*$', username): # Check username for unallowed characters
                    try:
                        with sqlite3.connect(database) as conn: # User exists, read his password
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(str(username),))
                            stored_password = datab.fetchone()[1]
                    except: # Disconnect user which username doesn't exist, close the connection
                        c.send(bytes("NO,This user doesn't exist", encoding='utf8'))
                        break
                    try:
                        if bcrypt.checkpw(password, stored_password) or password == duco_password.encode('utf-8') or password == NodeS_Overide:
                            c.send(bytes("OK", encoding='utf8')) # Send feedback about sucessfull login
                        else: # Disconnect user which password isn't valid, close the connection
                            c.send(bytes("NO,Password is invalid", encoding='utf8'))
                            break
                    except:
                        try:
                            stored_password = str(stored_password).encode('utf-8')
                            if bcrypt.checkpw(password, stored_password) or password == duco_password.encode('utf-8'):
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
            if str(data[0]) == "JOB":
                if username == "":
                    try:
                        username = str(data[1])
                    except IndexError:
                        c.send(bytes("NO,Not enough data", encoding='utf8'))
                        break
                try:
                    with sqlite3.connect(blockchain, timeout=20) as blockconn:
                        blockdatab = blockconn.cursor()
                        blockdatab.execute("SELECT blocks FROM Server") # Read amount of mined blocks
                        blocks = int(blockdatab.fetchone()[0])
                        blockdatab.execute("SELECT lastBlockHash FROM Server") # Read lastblock's hash
                        lastBlockHash = str(blockdatab.fetchone()[0])
                except:
                    break
                # Calculate difficulty and create new block hash
                try:
                    customDiff = str(data[2])
                    if str(customDiff) == "AVR":
                        diff = 300 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR200":
                        diff = 200 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 80
                    if str(customDiff) == "AVR400":
                        diff = 300 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR500":
                        diff = 500 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR600":
                        diff = 600 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR700":
                        diff = 700 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR800":
                        diff = 800 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    if str(customDiff) == "AVR900":
                        diff = 900 # Use 300 - optimal diff for very low power devices like arduino
                        shareTimeRequired = 100
                    elif str(customDiff) == "ESP":
                        diff = 1500 # Use 1500 - optimal diff for low power devices like ESP
                        shareTimeRequired = 200
                    elif str(customDiff) == "MEDIUM":
                        diff = 5000 # Use 5000 - optimal diff for low power computers
                        shareTimeRequired = 170
                except:
                    diff = math.ceil(blocks / diff_incrase_per) # Use "standard" difficulty
                if diff < 1000:
                    rand = random.randint(1, diff)
                else:
                    rand = random.randint(1, 100 * diff)
                    shareTimeRequired = rand / 10000
                try:
                    newBlockHash = hashlib.sha1(str(lastBlockHash + str(rand)).encode("utf-8")).hexdigest()
                    c.send(bytes(str(lastBlockHash) + "," + str(newBlockHash) + "," + str(diff), encoding='utf8')) # Send hashes and diff hash to the miner
                    jobsent = datetime.datetime.now()
                    response = c.recv(128).decode().split(",") # Wait until client solves hash
                    result = response[0]
                    # Kolka system - reward dependent on share submission time and rejection of very fast shares
                    resultreceived = datetime.datetime.now()
                except:
                    break
                sharetime = resultreceived - jobsent # Time from start of hash computing to finding the result
                sharetime = sharetime.total_seconds() * 1000 # Get total ms
                reward = int(int(sharetime) **2) / 750000000 # Calculate reward dependent on share submission time
                try: # If client submitted hashrate, use it
                    hashrate = float(response[1])
                    hashrateEstimated = False
                except: # If not, estimate it ourselves
                    try:
                        hashrate = int(rand) / int(sharetime) * 2000000 / int(diff) # This formula gives a rough estimation of the hashrate
                    except ZeroDivisionError:
                        hashrate = 1000
                    hashrateEstimated = True
                try:
                    minerUsed = str(response[2])
                except:
                    minerUsed = "Unknown"
                try:
                    minerapi.update({str(threading.get_ident()): [str(username), str(hashrate), str(sharetime), str(acceptedShares), str(rejectedShares), str(diff), str(hashrateEstimated), str(minerUsed)]})
                except:
                    pass
                if result == str(rand) and int(sharetime) > int(shareTimeRequired) and int(sharetime) < 999:
                    try:
                        acceptedShares += 1
                        c.send(bytes("GOOD", encoding="utf8")) # Send feedback that result was correct
                        while True:
                            try:
                                with sqlite3.connect(database, timeout=15) as conn: # Get users balance and check if it exists
                                    datab = conn.cursor()
                                    datab.execute("SELECT * FROM Users WHERE username = ?", (username,))
                                    balance = float(datab.fetchone()[3])
                                    balance += float(reward) # Reward user
                                    datab = conn.cursor()
                                    datab.execute("UPDATE Users set balance = ? where username = ?", (f'{balance:.20f}', username))
                                    conn.commit()
                                    break
                            except:
                                pass
                    except:
                        c.send(bytes("INVU", encoding="utf8")) # Send feedback that this user doesn't exist
                        break
                    while True:
                        try:
                            with sqlite3.connect(blockchain, timeout=20) as blockconn: # Update blocks counter and lastblock's hash
                                blocks += 1
                                blockdatab = blockconn.cursor()
                                blockdatab.execute("UPDATE Server set blocks = ? ", (blocks,))
                                blockdatab.execute("UPDATE Server set lastBlockHash = ?", (newBlockHash,))
                                blockconn.commit()
                                break
                        except:
                            pass
                else: # Incorrect result received
                    try:
                        rejectedShares += 1
                        c.send(bytes("BAD", encoding="utf8")) # Send feedback that incorrect result was received
                    except:
                        break

                    while True:
                        try:
                            with sqlite3.connect(database, timeout=15) as conn:
                                datab = conn.cursor()
                                datab.execute("SELECT * FROM Users WHERE username = ?", (username,))
                                balance = str(datab.fetchone()[3]) # Get miner balance
                                if float(balance) > .00005:
                                    balance = float(balance) - int(int(sharetime) *2) / 750000000 # Calculate penalty dependent on share submission time
                                    while True:
                                        try:
                                            with sqlite3.connect(database) as conn:
                                                datab = conn.cursor() # Update his the balance
                                                datab.execute("UPDATE Users set balance = ? where username = ?", (f'{balance:.20f}', username))
                                                conn.commit()
                                                break
                                        except:
                                            pass
                                break
                        except:
                            pass

            ######################################################################
            if str(data[0]) == "CHGP" and str(username) != "":
                try:
                    oldPassword = data[1]
                    newPassword = data[2]
                except IndexError:
                    c.send(bytes("NO,Not enough data", encoding='utf8'))
                    break
                try:
                    oldPassword = oldPassword.encode('utf-8')
                    newPassword = newPassword.encode("utf-8")
                    newPassword_encrypted = bcrypt.hashpw(newPassword, bcrypt.gensalt())
                except:
                    c.send(bytes("NO,Bcrypt error", encoding="utf8"))
                    break
                try:
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                        old_password_database = datab.fetchone()[1]
                except:
                    c.send(bytes("NO,Incorrect username", encoding="utf8"))
                    break

                if bcrypt.checkpw(oldPassword, old_password_database) or oldPassword == duco_password.encode('utf-8'):
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("UPDATE Users set password = ? where username = ?", (newPassword_encrypted, username))
                        conn.commit()
                        try:
                            c.send(bytes("OK,Your password has been changed", encoding='utf8'))
                        except:
                            break
                else:
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
                try:
                    with sqlite3.connect(database, timeout = 15) as conn:
                        datab = conn.cursor()
                        datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                        balance = float(datab.fetchone()[3]) # Get current balance of sender
                except:
                    c.send(bytes("NO,Can't check sender balance", encoding='utf8'))
                    break
                if str(recipient) == str(username): # Verify that the balance is higher or equal to transfered amount
                    try:
                        c.send(bytes("NO,You're sending funds to yourself", encoding='utf8'))
                    except:
                        break
                if float(balance) <= float(amount) or float(amount) <= 0:
                    try:
                        c.send(bytes("NO,Incorrect amount", encoding='utf8'))
                        print("NO,Incorrect amount")
                    except:
                        break
                elif float(balance) >= float(amount) and str(recipient) != str(username) and float(amount) >= 0:
                    try:
                        balance -= float(amount) # Remove amount from senders' balance
                        with sqlite3.connect(database, timeout = 15) as conn:
                            datab = conn.cursor()
                            datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                            conn.commit()
                        with sqlite3.connect(database, timeout = 15) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(recipient,))
                            recipientbal = float(datab.fetchone()[3]) # Get receipents' balance
                        recipientbal += float(amount)
                        with sqlite3.connect(database, timeout = 15) as conn:
                            datab = conn.cursor() # Update receipents' balance
                            datab.execute("UPDATE Users set balance = ? where username = ?", (f'{float(recipientbal):.20f}', recipient))
                            conn.commit()
                        c.send(bytes("OK,Successfully transferred funds!", encoding='utf8'))
                    except:
                        c.send(bytes("NO,Error occured while sending funds", encoding='utf8'))
                        break

            ######################################################################
            elif str(data[0]) == "BALA" and str(username) != "":
                while True:
                    try:
                        with sqlite3.connect(database, timeout = 15) as conn:
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                            balance = str(datab.fetchone()[3]) # Fetch balance of user
                            try:
                                c.send(bytes(str(f'{float(balance):.20f}'), encoding="utf8")) # Send it as 20 digit float
                            except:
                                break
                            break
                    except:
                        pass

            ######################################################################
            elif str(data[0]) == "WRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    print("Starting Wrapping protocol")
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
                                print("NO, minimum amount is 10 DUCO")
                            except:
                                break
                        else:
                            balancebackup = balance
                            print("Backed up balance")
                            try:
                                print("All checks done, initiating wrapping routine")
                                balance -= float(amount) # Remove amount from senders' balance
                                print("DUCO removed from pending balance")
                                with sqlite3.connect(database) as conn:
                                    datab = conn.cursor()
                                    datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                                    conn.commit()
                                print("DUCO balance sent to DB, sending tron transaction")
                                print("Tron wrapper called !")
                                txn = wduco.functions.wrap(tron_address,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                print("txid :", txn.txid)
                                txn = txn.broadcast()
                                print("Sent wrap tx to TRON network")
                                trontxfeedback = txn.wait()

                                if trontxfeedback:
                                    try:
                                        c.send(bytes("OK,Success, check your balances !", encoding="utf8"))
                                        print("Successful wrapping")
                                    except:
                                        break
                                else:
                                    try:
                                        datab.execute("UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                        c.send(bytes("NO,Unknown error, transaction reverted", encoding="utf8"))
                                    except:
                                        break
                            except:
                                break
                    else:
                        c.send(bytes("NO,Wrapper disabled", emcoding="utf8"))
                        print("NO,Wrapper disabled")

            ######################################################################
            elif str(data[0]) == "UNWRAP" and str(username) != "":
                if use_wrapper and wrapper_permission:
                    print("Starting unwraping protocol")
                    amount = str(data[1])
                    tron_address = str(data[2])
                    try:
                        with sqlite3.connect(database) as conn:
                            print("Retrieving user balance...")
                            datab = conn.cursor()
                            datab.execute("SELECT * FROM Users WHERE username = ?",(username,))
                            balance = float(datab.fetchone()[3]) # Get current balance
                    except:
                        print("Error retrieving user balance")
                        try:
                            c.send(bytes("NO,Error retrieving balance", encoding="utf8"))
                            break
                        except:
                            break
                    print("Balance retrieved")
                    wbalance = float(int(wduco.functions.pendingWithdrawals(tron_address)))/10*6
                    if float(amount) <= float(wbalance) and float(amount) > 0:
                        if float(amount) >= 10:
                            if float(amount) <= float(wbalance):
                                print("Correct amount")
                                balancebackup = balance
                                print("Updating DUCO Balance")
                                balancebackup = balance
                                balance = str(float(balance)+float(amount))
                                try:
                                    with sqlite3.connect(database) as conn:
                                        datab = conn.cursor()
                                        datab.execute("UPDATE Users set balance = ? where username = ?", (balance, username))
                                        conn.commit()
                                except:
                                    print("Error with DUCO DB")
                                    c.send(bytes("NO,Error with DUCO DB", encoding="utf8"))
                                    break
                                try:
                                    print("Sending tron transaction !")
                                    txn = wduco.functions.confirmWithdraw(username,tron_address,int(float(amount)*10**6)).with_owner(wrapper_public_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(wrapper_private_key)))
                                    print("txid :", txn.txid)
                                    txn = txn.broadcast()
                                    print("Sent confirm tx to tron network")
                                    onchaintx = txn.wait()

                                    if onchaintx:
                                        try:
                                            c.send(bytes("OK,Success !", encoding="utf8"))
                                        except:
                                            break
                                    else:
                                        with sqlite3.connect(database) as conn:
                                            datab = conn.cursor()
                                            datab.execute("UPDATE Users set balance = ? where username = ?", (balancebackup, username))
                                            conn.commit()
                                except:
                                    print("NO,Error with tron blockchain")
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
                    print("Wrapper disabled")
                    try:
                        c.send(bytes("NO,Wrapper disabled", encoding="utf8"))
                    except:
                        break
        except:
            break
    #User disconnected, exiting loop
    connectedUsers -= 1 # Subtract connected miners amount
    try: # Delete miner from minerapi if it was used
        del minerapi[str(threading.get_ident())]
    except KeyError:
        pass
    sys.exit() # Close thread

def unbanip(ip):
    os.system("sudo iptables -D INPUT -s "+str(ip)+" -j DROP")
    print("Unbanning IP:", ip)

IPS = {}
bannedIPS = {}
def countips():
    while True:
        for ip in IPS.copy():
            if IPS[ip] > 50 and not ip == "51.15.127.80":
                print("Banning IP:", ip)
                os.system("sudo iptables -I INPUT -s "+str(ip)+" -j DROP")
                IPS.pop(ip)
                threading.Timer(60.0, unbanip, [ip]).start() # Start auto-unban thread for this IP
        time.sleep(2)
def resetips():
    while True:
        time.sleep(30)
        IPS.clear()

if __name__ == '__main__':
    print("Duino-Coin Master Server", serverVersion, "is starting...")
    threading.Thread(target=API).start() # Create JSON API thread
    threading.Thread(target=createBackup).start() # Create Backup generator thread
    threading.Thread(target=InputManagement).start() # Admin input management thread
    threading.Thread(target=countips).start() # Start anti-DDoS thread
    threading.Thread(target=resetips).start() # Start connection counter reseter for the ant-DDoS thread
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("Socket binded to port", port)
    # Put the socket into listening mode
    s.listen(5) # Queue of 5 connections
    print("Socket is listening")
    print("Wrapper's tron address :", wrapper_public_key)
    # a forever loop until client wants to exit
    try:
        while True:
            # Establish connection with client
            c, addr = s.accept()
            try:
                IPS[addr[0]] += 1
            except:
                IPS[addr[0]] = 1
            #print('Connected to :', addr[0], ':', addr[1])
            # Start a new thread and return its identifier
            start_new_thread(handle, (c,))
    finally:
        print("exiting")
        s.close()
        import os
        os._exit(1) # error code 1 so it will autorestart with systemd
