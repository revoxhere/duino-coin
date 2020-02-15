#!/usr/bin/env python3
#############################################
# Duino-Coin Server (Beta 3) © revox 2020
# https://github.com/revoxhere/duino-coin 
#############################################
import socket, threading, time, random, hashlib, math, datetime, re, configparser, sys, errno, os, psutil, string, json
from pathlib import Path
from collections import OrderedDict
from github import Github

def ServerLog(whattolog):  # Serverlog section for debugging. Not used in proper pool to reduce disk usage. 
  #Getting actual date and time
  #now = datetime.datetime.now()
  #Creating and opening today's log file
  #logfile = open(now.strftime("logs/%Y-%m-%d.txt"), "a")
  #Time formating
  #now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
  #Writing message and closing file
  #logfile.write(now + whattolog + "\n")
  #logfile.close()
  print(whattolog)

def ServerLogHash(whattolog): # Separate serverlog section for mining section debugging. Not used in proper pool to reduce disk usage. 
  #Getting actual date and time
  #now = datetime.datetime.now()
  #Creating and opening today's log file
  #logfile = open(now.strftime("logs/%Y-%m-%d.txt"), "a")
  #Time formating
  #now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
  #Writing message and closing file
  #logfile.write(now + whattolog + "\n")
  #logfile.close()
  #print(whattolog+"\n")
  pass

def search(myDict, search1):
    search.a=[]
    for key, value in myDict.items():
        if search1 in value:
            search.a.append(key)
  
def UpdateServerInfo(): ######################## API PROTOCOL ########################
  global server_info, hashrates, threads, diff, update_count, gitrepo, miners, gitusername, rewardap, blocks, userinfo
  now = datetime.datetime.now()
  now = now.strftime("%H:%M:%S")
  # Null pool hashrate stat
  server_info['pool_hashrate'] = 0
  # Count registered users
  server_info['users'] = len(os.listdir('users'))
  # Add miners hashrate and update pool's hashrate
  for hashrate in hashrates:
    server_info['pool_hashrate'] += hashrates[hashrate]["hashrate"]
  # Prepare json data for API
  data = {"pool_miners" : server_info["miners"], "pool_hashrate" : server_info["pool_hashrate"], "users" : server_info["users"], "miners" : {}}
  # Add users to API's output
  for hashrate in hashrates:
    data["miners"][hashrate] = hashrates[hashrate]
  # Write data to text API
  file = open("config/api.txt", "w")
  file.write(str("Pool hashrate: "))
  file.write(str(int((server_info['pool_hashrate']) / 1000)))
  file.write(str(" kH/s\n"))
  file.write(str("Active workers: "))
  file.write(str(server_info["miners"]))
  file.write(str(" ("))
  miners = []
  for x in hashrates:
    miners.append(hashrates[x]["username"])
  res = []
  for i in miners: 
    if i not in res: 
        res.append(i)
  file.write(str(', '.join(map(str, res))))
  file.write(str(")"))
  file.write(str("\nRegistered users: "))
  file.write(str(server_info["users"]))
  blok = open("config/blocks", "r")
  bloki = blok.readline()
  blok.close()
  file.write(str("\nMined blocks: " + bloki))
  file.write(str("\nLast block #: "))
  lastblok = open("config/lastblock", "r+")
  lastblokid = lastblok.readline().rstrip("\n\r ")[:10] + (lastblok.readline().rstrip("\n\r ")[10:] and '..')
  file.write(str(lastblokid))
  lastblok.close()
  file.write(str(" [...]"))
  file.write(str("\nCurrent difficulty: "))
  diff = math.ceil(int(bloki) / diff_incrase_per)
  file.write(str(diff))
  reward = round(float(0.000025219) * int(diff), 10)
  file.write(str("\nReward: "))
  file.write(str(reward))
  file.write(str(" DUCO/block"))
  file.write(str("\nLast updated: "))
  file.write(str(now))
  file.write(str(" (GMT+1) (updated every 90s)"))
  file.close() # End of API file writing
  threading.Timer(5, UpdateServerInfo).start()

  ######################## UPDATE API FILE ########################
def UpdateAPIfile():
  global update_count
  try: # Create new file if it doesn't exist
    repo.create_file("api.txt", "test", "test", branch="master")
    ServerLog("File didn't exist on GitHub repo, created it!")
  except:
    pass
  file_contents = Path("config/api.txt").read_text() # Get api file contents
  update_count = update_count + 1 # Increment update counter by 1
  repo = g.get_repo("revoxhere/"+gitrepo)
  contents = repo.get_contents("api.txt") # Get contents of previous file for SHA verification
  try:
    repo.update_file(contents.path, "Statistics update #"+str(update_count), str(file_contents), contents.sha, branch="master") #Post statistics file into github
    ServerLog("Updated statistics file on GitHub. Update count:"+str(update_count))
  except:
    ServerLog("Failed to update statistics file!")
  # Run every 90s
  threading.Timer(90, UpdateAPIfile).start()
  
def randomString(stringLength=10):
    # Generate random string with specified length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
  
class InputProc(threading.Thread): ######################## SERVER CONSOLE ########################
  def run(self):
    proc = psutil.Process()
    while True:
      # Wait for input command in server console
      cmd = input(">")
      # Parse commands
      if cmd.find(" ") != -1:
        cmd = cmd.split(" ")
        if cmd[0] == "list":
          # List all registered users
          if cmd[1] == "users":
            print(' '.join([os.path.splitext(x)[0] for x in os.listdir('users')]))
          # List all connected users
          elif cmd[1] == "miners":
            print(' '.join([hashrates[x]["username"] for x in hashrates]))
        if cmd[0] == "kick":
          # Kick (disconnect) specified user
          kicklist.append(cmd[1])
        if cmd[0] == "ban":
          # Ban and kick specified user
          kicklist.append(cmd[1])
          # Changing user's password to random string
          file = open("users/" + cmd[1] + ".txt", "w")
          file.write(randomString(32))
          file.close()
      else:
        if cmd == "hashrates":
          print(hashrates)
        if cmd == "hash":
          print(str(' '.join(map(str, [hashrates[x]["hashrate"] for x in hashrates]))))
        if cmd == "kickall":
          # Kick (disconnect) all connected users
          kicklist.append(-1)
        if cmd == "serverinfo":
          # Display server info
          print("Duino-Coin server by revox & MrKris7100 from DUCO developers")
          print("Server version: " + VER)
          print("\nConnected GitHub account: "+str(gitusername)+", publishing on: "+str(gitrepo))
          print("  GitHub update count: "+str(update_count))
          print("\nServer resources usage:")
          print("  CPU usage: " + str(proc.cpu_percent()) + "%")
          print("  Memory usage: " + "{:.1f}".format(proc.memory_info()[0] / 2 ** 20) + "MB")
          print("\nConnected miners: " + str(server_info["miners"]))
          print("Server hashrate: " + str(server_info["pool_hashrate"]) + " H/s")
          print("Registered users count: " + str(server_info["users"]))
          with locker:
            file = open("config/blocks", "r")
            print("\nMined blocks count: " + file.readline())
            file.close()
            file = open("config/lastblock", "r+")
            print("Last block hash: " + file.readline())
            file.close()
        if cmd == "stop":
          # Shutting down server
          with locker:
            os._exit(0)
    time.sleep(1)

class ClientThread(threading.Thread): ######################## USER THREAD ########################
  def __init__(self, ip, port, clientsock):
    threading.Thread.__init__(self)
    self.ip = ip
    self.port = port
    self.clientsock = clientsock
    try:
      # Send server version to client
      clientsock.send(bytes(VER, encoding='utf8'))
    except socket.error as err:
      if err.errno == errno.ECONNRESET:
        err = True
  def run(self):
    conn.settimeout(60)
    err = False
    global server_info, hashrates, kicklist, thread_id, diff, data, users, miners
    # New user connected
    username = ""
    # Get thread id for this connection
    thread_id = str(threading.current_thread().ident)
    ServerLog("New thread (" + thread_id + ") started, connection: " + self.ip + ":" + str(self.port))
    while True:
      # Check "kicklist" for "kickall" command
      if -1 in kicklist:
        del kicklist[:]
        break
      # Check "kicklist" for this user "kick" command
      elif username in kicklist:
        kicklist.remove(username)
        break
      try:
        # Listen for requests from clients
        data = self.clientsock.recv(1024)
      except socket.error as err:
        if err.errno == errno.ECONNRESET:
          break
      if data:
        try:
          data = data.decode()
          data = data.split(",")
        except:
          break
      else:
        break

      ######################## REGISTRATION PROTOCOL ########################
      if data[0] == "REGI":
        username = data[1]
        password = data[2]
        server_info['miners'] += 1
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        ServerLog("Client "+str(username)+" has requested account registration.")
        # Check username for unallowed characters
        if re.match(regex,username):
          # Check if user already exists
          if not Path("users/" + username + ".txt").is_file():
            # If user dosen't exist, save his password and balance
            file = open("users/" + username + ".txt", "w")
            file.write(password)
            file.close()
            file = open("balances/" + username + ".txt", "w")
            file.write(str("0.5"))
            file.close()
            self.clientsock.send(bytes("OK", encoding='utf8'))
            ServerLog("New user (" + username + ") registered")
          else:
            # User arleady exists, disconnect
            ServerLog("Account already exists!")
            self.clientsock.send(bytes("NO", encoding='utf8'))
            break
        else:
          # User used unallowed characters, disconnect
          ServerLog("Unallowed characters!!!")
          self.clientsock.send(bytes("NO", encoding='utf8'))
          break

      ######################## LOGIN PROTOCOL ########################
      elif data[0] == "LOGI":
        username = data[1]
        password = data[2]
        server_info['miners'] += 1
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        ServerLog("Client request logging in to account " + username)
        # Check username for unallowed characters (regex)
        if re.match(regex,username):
          # Check if that user exists
          try:
            # User exists, read his password
            file = open("users/" + username + ".txt", "r")
            file = file.read()
            filecont = file.splitlines()
          except:
            # Doesnt exist, disconnect
            ServerLog("User doesn't exist!")
            self.clientsock.send(bytes("NO", encoding='utf8'))
            break
          # Compare saved password with received password
          if password == filecont[0]:
            # Password matches
            ServerLog("Password matches, user logged")
            self.clientsock.send(bytes("OK", encoding='utf8'))
            # Update statistics username
            try:
              hashrates[int(thread_id)]["username"] = username
            except:
              pass
          else:
            # Bad password, disconnect
            ServerLog("Incorrect password")
            self.clientsock.send(bytes("NO", encoding='utf8'))
            break
        else:
          # User doesn't exist, disconnect
          ServerLog("User doesn't exist!")
          self.clientsock.send(bytes("NO", encoding='utf8'))
          break

      ######################## MINING PROTOCOL ########################
      elif username != "" and data[0] == "JOB":
        time.sleep(0.2)
        # Wait for unlocked files then lock them
        with locker:
          # Read blocks amount
          file = open("config/blocks", "r")
          blocks = int(file.readline())
          file.close()
          # Read lastblock's hash
          file = open("config/lastblock", "r+")
          lastblock = file.readline()
          # Calculate difficulty
          diff = math.ceil(blocks / diff_incrase_per)
          rand = random.randint(0, 100 * diff)
          # Generate next block hash
          hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))
          ServerLogHash("Sending target hash: " + hashing.hexdigest())
          try:
            # Send target hash to miner
            self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
          except socket.error as err:
            if err.errno == errno.ECONNRESET:
              break
          # Update lastblock's hash
          file.seek(0)
          file.write(hashing.hexdigest())
          file.truncate()
          file.close()
        try:
          # Wait until client solves hash
          response = self.clientsock.recv(1024).decode()
        except socket.error as err:
          if err.errno == errno.ECONNRESET:
            break
        # Ad miner hashrate to statistics
        try:
          if response.find(",") != -1:
            try:
              response = response.split(",")
              result = response[0]
              hashrate = response[1]
              hashrates[int(thread_id)]["hashrate"] = float(hashrate)
            except:
              pass
          else: # Alpha 5 compatibility
            try:
              result = response
              hashrates[int(thread_id)]["hashrate"] = 1000 #1kH/s
            except:
              pass
        except:
          pass
        # Checking received result
        if result == str(rand):
          ServerLogHash("Received good result (" + str(result) + ")")
          # Rewarding user for good hash
          with locker: # Using locker to fix problems when mining on many devices with one account
            global reward
            
            bal = open("balances/" + username + ".txt", "r")
            balance = str(float(bal.readline())).rstrip("\n\r ")
            
            if float(balance) < 30: # New users will mine a bit faster
              reward = float(0.00025219)
            else:
              if float(balance) < 50: # Lower than 50
                reward = float(0.000050219)
              else:
                if float(balance) < 80: # Lower than 80
                  reward = float(0.000003200)
                else:
                  if float(balance) < 150: # Lower than 150
                    reward = float(0.000000024439)
                  else: # Higher than 150
                    reward = float(0.000000001519)
              
            balance = float(balance) + float(reward)
            bal = open("balances/" + username + ".txt", "w")
            bal.seek(0)
            bal.write(str(balance))
            bal.truncate()
            bal.close()
          try:
            self.clientsock.send(bytes("GOOD", encoding="utf8"))
          except socket.error as err:
            if err.errno == errno.ECONNRESET:
              break
          # Waiting fo unlocked files then lock them
          with locker:
            # Update amount of blocks
            blocks+= 1
            blo = open("config/blocks", "w")
            blo.seek(0)
            blo.write(str(blocks))
            blo.truncate()
            blo.close()
        else:
          # If result is bad send "BAD"
          ServerLogHash("Recived bad result!"+result)
          try:
            self.clientsock.send(bytes("BAD", encoding="utf8"))
          except:
            break
          
      ######################## PROOF OF TIME PROTOCOL ########################
      elif username != "" and data[0] == "PoTr":
        time.sleep(44)
        ServerLog("Received PoTr request")
        with locker: # Using locker to fix problems when mining on many devices with one account
          bal = open("balances/" + username + ".txt", "r")
          balance = str(float(bal.readline())).rstrip("\n\r ")\

          if float(balance) < 30: # New users will mine a bit faster
            reward = float(0.025219)
          else:
            if float(balance) < 50: # lower than 50
              reward = float(0.0025219)
            else:
              if float(balance) < 80: # lower than 80
                reward = float(0.00025219)
              else:
                if float(balance) < 150:
                  reward = float(0.000025219)
                else:
                  reward = float(0.0000006519)
                  
          balance = float(balance) + float(reward)
          bal = open("balances/" + username + ".txt", "w")
          bal.seek(0)
          bal.write(str(balance))
          bal.truncate()
          bal.close()
        ServerLog("Added balance using PoTr")

      ######################## BALANCE CHECK PROTOCOL ########################
      elif username != "" and data[0] == "BALA":
        time.sleep(0.2)
        ServerLog("Client request balance check")
        file = open("balances/" + username + ".txt", "r")
        balance = file.readline()
        file.close()
        try:
          self.clientsock.send(bytes(balance, encoding='utf8'))
        except:
          break

      ######################## CHECK USER STATUS PROTOCOL ########################
      elif username != "" and data[0] == "STAT":
        ServerLog("Client requested user status check")
        file = open("users/" + username + ".txt", "r")
        file = file.read()
        filecont = file.splitlines()
        try:
                userstatus = filecont[1]
                print(userstatus)
                self.clientsock.send(bytes(userstatus, encoding='utf8'))
        except:
                self.clientsock.send(bytes("Regular Member", encoding='utf8'))
        print("sentuserinfo")
      ######################## CLIENT INFO PROTOCOL ########################
      elif username != "" and data[0] == "FROM":
        if data[1]:
          client = data[1]
        if data[2]:
          pcusername = data[2]
        if data[3]:
          ip = data[3]
        if data[4]:
          platform = data[4]
        if data:
          print(str(client), str(pcusername), str(ip), str(platform))
        time.sleep(0.1)

      ######################## CLOSE PROTOCOL ########################
      elif username != "" and data[0] == "CLOSE":
        try:
          ServerLog("Client requested thread (" + thread_id + ") closing")
          # Close socket connection
          self.clientsock.close()
          # Decrease number of connected miners
          server_info['miners'] -= 1
          # Delete this miner from statistics
          users = users.replace(" "+str(username), "")
          try:
            del hashrates[int(thread_id)]
          except:
            try:
              del hashrates[str(thread_id)]
            except:
              try:
                del hashrates[thread_id]
              except:
                hashrates.pop(thread_id, None)
          print(hashrates)
          time.sleep(1)
        except:
          ServerLog("Error closing connection (" + thread_id + ")!")
          time.sleep(1)
          
      ######################## SENDING PROTOCOL ########################
      elif username != "" and data[0] == "SEND":
        time.sleep(0.2)
        sender = username
        receiver = data[2]
        amount = float(data[3])
        ServerLog("Client request transfer funds")
        # Get current amount of funds in bank
        try:
          file = open("balances/" + sender + ".txt", "r+")
          balance = float(file.readline())
        except:
          ServerLog("Can't checks senders' (" + sender + ") balance")
        # Verify that the balance is higher or equal to transfered amount
        if amount > balance:
          try:
            self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
          except:
            break
        else: # Check if recipient adress exists
          if Path("balances/" + receiver + ".txt").is_file():
            try:
              # Remove amount from senders' balance
              balance -= amount
              file.seek(0)
              file.write(str(balance))
              file.truncate()
              file.close()
              # Get receipents' balance and add transferred amount
              file = open("balances/" + receiver + ".txt", "r+")
              receiverbal = float(file.readline())
              receiverbal += amount
              file.seek(0)
              file.write(str(receiverbal))
              file.truncate()
              file.close()
              try:
                self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
              except socket.error as err:
                break
              ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + receiver)
            except:
              try:
                self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
              except socket.error as err:
                break
          else: # Send message if receipent doesn't exist
            ServerLog("The recepient "+receiver+" doesn't exist!")
            try:
              self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
            except socket.error as err:
              break
    ServerLog("Thread (" + thread_id + ") and connection closed")
    # Close socket connection
    self.clientsock.close()
    
    # Delete this miner from statistics
    try:
      del hashrates[int(thread_id)]
    except:
      try:
        del hashrates[str(thread_id)]
      except:
        try:
          del hashrates[thread_id]
        except:
          hashrates.pop(thread_id, None)
    print(hashrates)
    try:
      users = users.replace(" "+str(username), "")
      server_info['miners'] -= 1
      ServerLog("Del passed!")
    except:
      ServerLog("Error removing from dict " + str(thread_id))
    time.sleep(1)
      
######################## VARIABLES ########################
regex = r'^[\w\d_()]*$'
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
threads = []
kicklist = []
server_info = {'miners' : 0, 'pool_hashrate' : 0, 'users' : 0}
userinfo = ""
hashrates = {}
config = configparser.ConfigParser()
locker = threading.Lock()
update_count = 0
users = ""
VER = "0.9" # "Big" version number  (0.9 = Beta 3)

######################## INITIAL FILE CREATION ########################
if not Path("config").is_dir():
  os.mkdir("config")
if not Path("users").is_dir():
  os.mkdir("users")
if not Path("balances").is_dir():
  os.mkdir("balances")
if not Path("config/lastblock").is_file():
  file = open("config/lastblock", "w")
  file.write(hashlib.sha1(str("revox.heremrkris7100").encode("utf-8")).hexdigest()) #First block
  file.close()
if not Path("config/blocks").is_file():
  file = open("config/blocks", "w")
  file.write("1")
  file.close()

######################## INITIAL CONFIGURATION ########################
if not Path("config/config.ini").is_file():
  print("Initial server configuration\n")
  host = input("Enter server host adddress: ")
  port = input("Enter server port: ")
  new_user_balance = input("Default balance for new users: ")
  diff_incrase_per = input("How many blocks are needed for incrase difficulty: ")
  gitusername = input("GitHub username to push api to: ")
  gitpassword = input("GitHub password to push api to: ")
  gitrepo = input("GitHub repository name to push api to: ")
  config['server'] = {"host": host,
  "port": port,
  "new_user_bal": new_user_balance,
  "diff_incrase_per": diff_incrase_per,
  "gitusername": gitusername,
  "gitpassword": gitpassword,
  "gitrepo": gitrepo}
  with open("config/config.ini", "w") as configfile:
    config.write(configfile)
    
######################## LOAD CONFIGFILE ########################
else:
  config.read("config/config.ini")
  host = config['server']['host']
  port = config['server']['port']
  new_user_balance = config['server']['new_user_bal']
  diff_incrase_per = config['server']['diff_incrase_per']
  gitusername = config['server']['gitusername']
  gitpassword = config['server']['gitpassword']
  gitrepo = config['server']['gitrepo']
  port = int(port)
  diff_incrase_per = int(diff_incrase_per)

######################## BIND SOCKETS ########################
try:
  tcpsock.bind((host, port))
  ServerLog("TCP server started...")
except:
  ServerLog("Error during TCP socket!")
  time.sleep(5)
  sys.exit()
  
######################## GITHUB API ########################
try:
  g = Github(gitusername, gitpassword)
  ServerLog("Logged in to GitHub...")
except:
  ServerLog("Error logging in to GitHub!")
  time.sleep(5)
  sys.exit()

######################## MAIN LOOP ########################
ServerLog("Listening for incoming connections...")
# Start thread for updating server info api
UpdateServerInfo()
UpdateAPIfile()
while True:
  # Start thread for input procesing
  newthread = InputProc()
  newthread.start()
  try:
    # Listen for new connections
    tcpsock.listen(1)
    (conn, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, conn)
    newthread.start()
    threads.append(newthread)
  except:
    ServerLog("Error in main loop!")
  time.sleep(0.025)

for t in threads:
  t.join()
