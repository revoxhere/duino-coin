#!/usr/bin/env python3
#############################################
# Duino-Coin Server (v1.337) © revox 2020
# https://github.com/revoxhere/duino-coin
#############################################
import socket, threading, time, random, hashlib, math, datetime, re, configparser, sys, errno, os, psutil, string, json
from pathlib import Path
from collections import OrderedDict
from github import Github

def ServerLog(whattolog):  # Serverlog section for debugging. Not used in proper pool to reduce disk usage. 
  #logfile = open(now.strftime("logs/%Y-%m-%d.txt"), "a")
  now = datetime.datetime.now()
  now = now.strftime("%H:%M:%S")
  #logfile.write(now + whattolog + "\n")
  #logfile.close()
  print(now, whattolog)

def ServerLogHash(whattolog): # Separate serverlog section for mining section debugging. Not used in proper pool to reduce disk usage. 
  #logfile = open(now.strftime("logs/%Y-%m-%d.txt"), "a")
  #now = datetime.datetime.now()
  #now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
  #logfile.write(now + whattolog + "\n")
  #logfile.close()
  #print(now, whattolog)
  pass

def search(myDict, search1):
    search.a=[]
    for key, value in myDict.items():
        if search1 in value:
            search.a.append(key)

def prepend_line(file_name, line):
    dummy_file = file_name + '.bak'
    with open(file_name, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        write_obj.write(line + '\n')
        for line in read_obj:
            write_obj.write(line)
    os.remove(file_name)
    os.rename(dummy_file, file_name)
  
def UpdateServerInfo(): ######################## API PROTOCOL ########################
  global server_info, hashrates, xmgusd, threads, diff, update_count, gitrepo, miners, gitusername, rewardap, blocks, userinfo
  now = datetime.datetime.now()
  now = now.strftime("%H:%M")
  lastUpdate = str(now)

  miners = []
  server_info['pool_hashrate'] = 0
  server_info['users'] = len(os.listdir('users'))


  for hashrate in hashrates:
    server_info['pool_hashrate'] += hashrates[hashrate]["hashrate"]

  data = {"pool_miners" : server_info["miners"], "pool_hashrate" : server_info["pool_hashrate"], "users" : server_info["users"], "miners" : {}}
  for hashrate in hashrates:
    data["miners"][hashrate] = hashrates[hashrate]

  file = open("config/api.html", "w")
  jsonfile = open("config/api.json", "w")

  for x in hashrates:
    miners.append(hashrates[x]["username"])
  res = []
  for i in miners: 
    if i not in res: 
        res.append(i)

  poolHashrate = int((server_info['pool_hashrate']) / 1000)
  workersNumber = str(len(res))
  workersList = str(" (") + str(', '.join(map(str, res))) + str(")")
  usersNumber = str(server_info["users"])

  blok = open("config/blocks", "r")
  minedBlocks = blok.readline()
  blok.close()

  lastblok = open("config/lastblock", "r+")
  lastblokid = lastblok.readline().rstrip("\n\r ")[:10] + (lastblok.readline().rstrip("\n\r ")[10:] and '..')
  lastblockHash = str(lastblokid)
  lastblok.close()

  difficulty = math.ceil(int(minedBlocks) / diff_incrase_per)

  if workersList == " ()":
    workersList = " (No active workers right now :c)"

  rand = random.randint(1000,1090)
  rand = rand / 1000
  ducousdLong = float(xmgusd) * float(rand)
  ducoPrice = round(float(ducousdLong) / float(8), 8)
    
  ########## JSON #########
  jsonapi = json.dumps(
    {'Pool hashrate': str(poolHashrate),
     'Last update': str(lastUpdate),
     'Duco price': str(ducoPrice),
     'Current difficulty': str(difficulty),
     'Registered users': str(usersNumber),
     'Mined blocks': str(minedBlocks),
     'Active workers': str(workersNumber) + str(workersList)}
     , sort_keys=True, indent=4)

  ########## HTML #########
  htmlapi = """<!DOCTYPE html>
  <html>
	<head>
		<link href="https://fonts.googleapis.com/css?family=Open+Sans&display=swap" rel="stylesheet">
		<style>
			body {
			   font-family: 'Open Sans', sans-serif;
			}

			img {
				margin-top: 20px;
			}

			h1 {
				color: #0d52bf;
				font-size: 20px;
			}
			h2 {

				font-size: 16px;
				margin-top: 5px;
			}
			.statisticsDiv {
			  display: inline-block;
			  width: 150px;
			}
		</style>
	</head>
	<body>
		<div style="text-align:center;">
			<div class="statisticsDiv" align="center">
				<img src="hashrate.png" width="64px" height="64px">
				<h2>Pool hashrate:</h2>
				<h1>"""+str(poolHashrate)+""" kH/s</h1>
			</div>

			<div class="statisticsDiv" align="center">
				<img src="users.png" width="64px" height="64px">
				<h2>Registered users:</h2>
				<h1>"""+str(usersNumber)+"""</h1>
			</div>

			<div class="statisticsDiv" align="center">
				<img src="blocks.png" width="64px" height="64px">
				<h2>Mined blocks:</h2>
				<h1>"""+str(minedBlocks)+"""</h1>
			</div>

			<br>

			<div class="statisticsDiv" align="center">
				<img src="hash.png" width="64px" height="64px">
				<h2>Last block hash:</h2>
				<h1>"""+str(lastblockHash)+"""...</h1>
			</div>

			<div class="statisticsDiv" align="center">
				<img src="difficulty.png" width="64px" height="64px">
				<h2>Current difficulty:</h2>
				<h1>"""+str(difficulty)+"""</h1>
			</div>

			<div class="statisticsDiv" align="center">
				<img src="clock.png" width="64px" height="64px">
				<h2>Last API update</h2>
				<h1>"""+str(lastUpdate)+""" GMT+1</h1>
			</div>

			<br>

			<div align="center">
				<img src="workers.png" width="64px" height="64px">
				<h2>Active workers:</h2>
				<h1>"""+str(workersNumber)+str(workersList)+"""</h1>
			</div>
		</div>
	</body>
  </html>"""
  file.write(str(htmlapi))
  file.close()
  jsonfile.write(str(jsonapi))
  jsonfile.close()
  threading.Timer(5, UpdateServerInfo).start()


  ######################## UPDATE API FILE ########################
def UpdateAPIfiles():
  global update_count
  ######################## GITHUB API ########################
  try:
    g = Github(gitusername, gitpassword)
    ServerLog("Logged in to GitHub...")
  except:
    UpdateAPIfiles()

  try:
    repo = g.get_repo("revoxhere/"+gitrepo)
  except:
    UpdateAPIfiles()
  try:
    htmlfile_contents = Path("config/api.html").read_text() # Get api file contents
    htmlcontents = repo.get_contents("api.html") # Get contents of previous file for SHA verification
  except:
    UpdateAPIfiles()

  try:
    repo.update_file(htmlcontents.path, "Statistics update #"+str(update_count), str(htmlfile_contents), htmlcontents.sha, branch="master") #Post statistics file into github
    update_count = update_count + 1 # Increment update counter by 1
  except:
    UpdateAPIfiles()

  try:
    jsonfile_contents = Path("config/api.json").read_text() # Get api file contents
    jsoncontents = repo.get_contents("api.json") # Get contents of previous file for SHA verification
  except:
    UpdateAPIfiles()

  try:
    repo.update_file(jsoncontents.path, "Statistics update #"+str(update_count), str(jsonfile_contents), jsoncontents.sha, branch="master") #Post statistics file into github
    ServerLog("Updated API files on GitHub. Update count:"+str(update_count))
  except:
    UpdateAPIfiles()
  # Run every 200s
  threading.Timer(200, UpdateAPIfiles).start()
  
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
  
class InputProc(threading.Thread): ######################## SERVER CONSOLE ########################
  def run(self):
    proc = psutil.Process()
    while True:
      cmd = input(">")
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
    global server_info, hashrates, kicklist, thread_id, diff, data, users, miners
    conn.settimeout(60)
    err = False
    username = ""
    thread_id = str(threading.current_thread().ident)

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
        ServerLog("Client "+str(username)+" requested account registration.")

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
          ServerLog("Unallowed characters!")
          self.clientsock.send(bytes("NO", encoding='utf8'))
          break

      ######################## LOGIN PROTOCOL ########################
      elif data[0] == "LOGI":
        username = data[1]
        password = data[2]
        server_info['miners'] += 1
        hashrates[int(thread_id)] = {"username" : username, "hashrate" : 0}
        ServerLog("Client "+str(username)+" requested account login.")

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
            ServerLog("Incorrect password!")
            self.clientsock.send(bytes("NO", encoding='utf8'))
            break
        else:
          # User doesn't exist, disconnect
          ServerLog("User doesn't exist!")
          self.clientsock.send(bytes("NO", encoding='utf8'))
          break

      ######################## MINING PROTOCOL ########################
      elif username != "" and data[0] == "JOB":
        time.sleep(0.01)
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

        # Add miner hashrate to statistics
        try:
          if response.find(",") != -1:
            try:
              response = response.split(",")
              result = response[0]
              hashrate = response[1]
              hashrates[int(thread_id)]["hashrate"] = float(hashrate)
            except:
              pass
          else: # Arduino Miner compatibility
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
              if float(balance) < 50:
                reward = float(0.00008219)
              else:
                if float(balance) < 80:
                  reward = float(0.00001200)
                else:
                  if float(balance) < 100:
                    reward = float(0.0000014439)
                  else:
                    reward = float(0.000000719)
              
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
        ServerLogHash("Received PoTr request")

        with locker: # Using locker to fix problems when mining on many devices with one account
          bal = open("balances/" + username + ".txt", "r")
          balance = str(float(bal.readline())).rstrip("\n\r ")\

          if float(balance) < 60: # New users will mine a bit faster
              reward = float(0.025219)
          else:
              if float(balance) < 70:
                reward = float(0.0122)
              else:
                if float(balance) < 90:
                  reward = float(0.01)
                else:
                  if float(balance) < 100:
                    reward = float(0.005)
                  else:
                    reward = float(0.002)

          balance = float(balance) + float(reward)
          bal = open("balances/" + username + ".txt", "w")
          bal.seek(0)
          bal.write(str(balance))
          bal.truncate()
          bal.close()
        ServerLogHash("Added balance using PoTr")

      ######################## CHECK USER STATUS PROTOCOL ########################
      elif username != "" and data[0] == "STAT":
        file = open("users/" + username + ".txt", "r")
        filecont = file.readlines()
        file.close()

        try:
                userstatus = filecont[1]
                self.clientsock.send(bytes(userstatus, encoding='utf8'))
        except:
                self.clientsock.send(bytes("Regular Member", encoding='utf8'))
        
      ######################## CLIENT INFO PROTOCOL ########################
      elif username != "" and data[0] == "FROM":
        ServerLog("Client "+str(username)+" sent informations")
        if data[1]:
          client = data[1]
        if data[2]:
          pcusername = data[2]
        if data[3]:
          ip = data[3]
        if data[4]:
          platform = data[4]
        if data:
          ServerLog("Uname: " + str(username) + " Client: " + str(client) + " PC: " + str(pcusername) + " IP: " + str(ip) + " Platform: " + str(platform))
        time.sleep(0.1)

      ######################## CLOSE PROTOCOL ########################
      elif username != "" and data[0] == "CLOSE":
        try:
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
          break
	
      ######################## PASSWORD CHANGE PROTOCOL ########################
      elif username != "" and data[0] == "CHGP":
        time.sleep(0.2)
        oldPassword = data[2]
        newPassword = data[3]
        print(data)
        ServerLog("Client request changing password")
        
        try:
          file = open("users/" + username + ".txt", "r")
          lines = file.readlines()
          serverOldPassword = lines[0]
          serverOldPassword = serverOldPassword.replace("\n", "")
          file.close()
        except:
          ServerLog("Can't check clients' username")

        if str(serverOldPassword) == str(oldPassword):
          file = open("users/" + username + ".txt", "r")
          lines = file.readlines()
          file.close
          print(lines)

          file = open("users/" + username + ".txt", "w")
          lines[0] = str(newPassword+"\n")
          print(lines)
          file.writelines(lines)
          file.close()
          
          try:
            self.clientsock.send(bytes("Success! Your password has been changed.", encoding='utf8'))
          except:
            break
        else:
          try:
            self.clientsock.send(bytes("Error! Your old password doesn't match!", encoding='utf8'))
          except:
            break
          
      ######################## SENDING PROTOCOL ########################
      elif username != "" and data[0] == "SEND":
        time.sleep(0.001)
        sender = username
        receiver = data[2]
        amount = float(data[3])
        ServerLog("Client request transfer funds")

        # Get current amount of funds
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
              file.close()

              # Get receipents' balance and add transferred amount
              file = open("balances/" + receiver + ".txt", "r+")
              receiverbal = float(file.readline())
              receiverbal += amount
              file.seek(0)
              file.write(str(receiverbal))
              file.close()

              try:
                self.clientsock.send(bytes("Successfully transfered funds!", encoding='utf8'))
              except:
                break
              ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + receiver)

            except:
              try:
                self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
              except:
                break

          else: # Send message if receipent doesn't exist
            ServerLog("The recepient "+receiver+" doesn't exist!")
            try:
              self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
            except:
              break
            
      ######################## BALANCE CHECK PROTOCOL ########################
      elif username != "" and data[0] == "BALA":
        time.sleep(0.1)

        file = open("balances/" + username + ".txt", "r")
        balance = file.readline()
        file.close()

        try:
          self.clientsock.send(bytes(balance, encoding='utf8'))
        except:
          break

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
    try:
      users = users.replace(" "+str(username), "")
      server_info['miners'] -= 1
    except:
      pass
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
xmgusd = 0.014541
VER = "1.337" # Version number

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
  

######################## MAIN LOOP ########################
ServerLog("Listening for incoming connections...")
# Start thread for updating server info api
UpdateServerInfo()
UpdateAPIfiles()
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
