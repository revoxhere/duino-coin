#!/usr/bin/env python

###########################################
# Duino-Coin public-server version 0.6    #
# https://github.com/revoxhere/duino-coin #
#  copyright by MrKris7100 & revox 2019   #
###########################################
# Important: this version of the server is a bit different than one used in official duino-coin network.
# !!! If you want to host pool/server yourself, you need to firstly install 'psutil' using pip install psutil !!!
VER = "0.6"

import socket, threading, time, random, hashlib, math, datetime, re, configparser, sys, errno, json, os, psutil, string
from pathlib import Path

def ServerLog(whattolog):
	#Getting actual date and time
	now = datetime.datetime.now()
	#Creating and opening today's log file
	logfile = open(now.strftime("logs/%Y-%m-%d.txt"), "a")
	#Time formating
	now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
	#Writing message and closing file
	logfile.write(now + whattolog + "\n")
	logfile.close()
	
def UpdateServerInfo():
	global server_info, hashrates
	#Nulling pool hashrate stat
	server_info['pool_hashrate'] = 0
	#Counting registered users
	server_info['users'] = len(os.listdir('users'))
	#Addition miners hashrate and update pool's hashrate
	for hashrate in hashrates:
		server_info['pool_hashrate'] += hashrates[hashrate]["hashrate"]
	#Preparing json data for API
	data = {"pool_miners" : server_info["miners"], "pool_hashrate" : server_info["pool_hashrate"], "users" : server_info["users"], "miners" : {}}
	#Adding mining users to API's json
	for hashrate in hashrates:
		data["miners"][hashrate] = hashrates[hashrate]
	#Writing json data to API
	with open("config/api.json", "w") as fJson:
		json.dump(data, fJson, indent=4)
	#Wait 5 seconds and repeat
	threading.Timer(5, UpdateServerInfo).start()
	
def randomString(stringLength=10):
	#Generating random string with specified length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
	
class InputProc(threading.Thread):
	def run(self):
		proc = psutil.Process()
		while True:
			#Waiting for input command in server console
			cmd = input(">")
			#Parsing commands
			if cmd.find(" ") != -1:
				cmd = cmd.split(" ")
				if cmd[0] == "list":
					#Listing all registered users on screen
					if cmd[1] == "users":
						print(' '.join([os.path.splitext(x)[0] for x in os.listdir('users')]))
					#Listing all connected users on screen
					elif cmd[1] == "miners":
						print(' '.join([hashrates[x]["username"] for x in hashrates]))
				if cmd[0] == "kick":
					#Kick (disconnect) specified user
					kicklist.append(cmd[1])
				if cmd[0] == "ban":
					#Ban and kick specified user
					kicklist.append(cmd[1])
					#Just changing user's password to random string
					file = open("users/" + cmd[1] + ".txt", "w")
					file.write(randomString(32))
					file.close()
			else:
				if cmd == "kickall"
					#Kicking (disconnecting) all connected users
					kicklist.append(-1)
				if cmd == "serverinfo":
					#Displaying server's info like version, resource usage, etc.
					print("Duino-coin server, version: " + VER)
					print("\nServer resources usage:")
					print("CPU: " + str(proc.cpu_percent()) + "%")
					print("MEM: " + "{:.1f}".format(proc.memory_info()[0] / 2 ** 20) + "MB")
					print("\nConnected miners: " + str(server_info["miners"]))
					print("Server hashrate: " + str(server_info["pool_hashrate"]) + " H/s")
					print("Registered users: " + str(server_info["users"]))
					with locker:
						file = open("config/blocks", "r")
						print("\nMined blocks: " + file.readline())
						file.close()
						file = open("config/lastblock", "r+")
						print("Last block: " + file.readline())
						file.close()
				if cmd == "stop":
					#Shutting down server
					with locker:
						sys.exit()

class ClientThread(threading.Thread): #separate thread for every user
	def __init__(self, ip, port, clientsock):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsock = clientsock

	def run(self):
		global server_info, hashrates, kicklist
		#New user connected
		username = ""
		#Getting thread id for this connection
		thread_id = str(threading.current_thread().ident)
		ServerLog("New thread (" + thread_id + ") started, connection: " + self.ip + ":" + str(self.port))
		#Increasing number of connected users
		server_info['miners'] += 1
		#Adding hashrate statistic for connected user
		hashrates[thread_id] = {"username" : username, "hashrate" : 0}
		while True:
			try:
				#Sending server version to client
				self.clientsock.send(bytes(VER, encoding='utf8'))
			except socket.error as err:
				if err.errno == errno.ECONNRESET:
					break
			#Checking "kicklist" for "kickall" command
			if -1 in kicklist:
				del kicklist[:]
				break
			#Checking "kicklist" for this user "kick" command
			elif username in kicklist:
				kicklist.remove(username)
				break
			try:
				#Listening for requests from client
				data = self.clientsock.recv(1024)
			except socket.error as err:
				if err.errno == errno.ECONNRESET:
					break
			data = data.decode()
			data = data.split(",")
			#Recived register request
			if data[0] == "REGI":
				username = data[1]
				password = data[2]
				ServerLog("Client request account registration.")
				#Checking username for unallowed characters
				if re.match(regex,username):
					#Checking if user already exists
					if not Path("users/" + username + ".txt").is_file():
						#If user dosen't exist, saving his password and setting up balance
						file = open("users/" + username + ".txt", "w")
						file.write(password)
						file.close()
						file = open("balances/" + username + ".txt", "w")
						file.write(str(new_user_balance))
						file.close
						self.clientsock.send(bytes("OK", encoding='utf8'))
						ServerLog("New user (" + username + ") registered")
					else:
						#User arleady exists
						ServerLog("Account already exists!")
						self.clientsock.send(bytes("NO", encoding='utf8'))
						break
				else:
					#User used unallowed characters, disconnecting
					ServerLog("Unallowed characters!!!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
					break
			#Recived login request
			elif data[0] == "LOGI": #login
				username = data[1]
				password = data[2]
				ServerLog("Client request logging in to account " + username)
				#Checking username for unallowed characters
				if re.match(regex,username):
					#Checking that user exists
					try:
						#User exists, reading his password
						file = open("users/" + username + ".txt", "r")
						data = file.readline()
						file.close()
					except:
						#Doesnt exist, disconnect
						ServerLog("User doesn't exist!")
						self.clientsock.send(bytes("NO", encoding='utf8'))
						break
					#Comparing saved password with recived password
					if password == data:
						#Password matches
						self.clientsock.send(bytes("OK", encoding='utf8'))
						ServerLog("Password matches, user logged")
						#Updating statistics username
						hashrates[thread_id]["username"] = username
					else:
						#Bad password, disconneting
						ServerLog("Incorrect password")
						self.clientsock.send(bytes("NO", encoding='utf8'))
						break
				else:
					#User doesn't exists
					ServerLog("User doesn't exist!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
					break
			#Client requested new job for him
			elif username != "" and data[0] == "JOB": #main, mining section
				ServerLog("New job for user: " + username)
				#Waiting for unlocked files then locking them
				with locker:
					#Reading blocks amount
					file = open("config/blocks", "r")
					blocks = int(file.readline())
					file.close()
					#Reading lastblock's hash
					file = open("config/lastblock", "r+")
					lastblock = file.readline()
					#Calculating difficulty
					diff = math.ceil(blocks / diff_incrase_per)
					rand = random.randint(0, 100 * diff)
					#Generating next block hash
					hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))
					ServerLog("Sending target hash: " + hashing.hexdigest())
					try:
						#Sending target hash to miner
						self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
					except socket.error as err:
						if err.errno == errno.ECONNRESET:
							break
					#Updating lastblock's hash
					file.seek(0)
					file.write(hashing.hexdigest())
					file.truncate()
					file.close()
				try:
					#Waiting until client solves hash
					response = self.clientsock.recv(1024).decode()
				except socket.error as err:
					if err.errno == errno.ECONNRESET:
						break
				#Old 0.5.1 version compatibility
				if response.find(",") != -1:
					response = response.split(",")
					result = response[0]
					hashrates[thread_id]["hashrate"] = int(response[1])
				else:
					result = response
					hashrates[thread_id]["hashrate"] = 0
				#Checking recived result is good hash
				if result == str(rand):
					ServerLog("Recived good result (" + str(result) + ")")
					#Rewarding user for good hash
					file = open("balances/" + username + ".txt", "r+")
					balance = float(file.readline())
					balance += reward
					file.seek(0)
					file.write(str(balance))
					file.truncate()
					file.close()
					try:
						self.clientsock.send(bytes("GOOD", encoding="utf8"))
					except socket.error as err:
						if err.errno == errno.ECONNRESET:
							break
					#Waiting fo unlocked files then lock them
					with locker:
						#Update amount of blocks
						blocks+= 1
						file = open("config/blocks", "w")
						file.seek(0)
						file.write(str(blocks))
						file.truncate()
						file.close()
				else:
					#Recived hash is bad
					ServerLog("Recived bad result (" + str(result[0]) + ")")
					try:
						self.clientsock.send(bytes("BAD", encoding="utf8"))
					except socket.error as err:
						if err.errno == errno.ECONNRESET:
							break
			#Client requested account balance checking
			elif username != "" and data[0] == "BALA": #check balance section
				ServerLog("Client request balance check")
				file = open("balances/" + username + ".txt", "r")
				balance = file.readline()
				file.close()
				try:
					self.clientsock.send(bytes(balance, encoding='utf8'))
				except socket.error as err:
					if err.errno == errno.ECONNRESET:
						break
			elif username != "" and data[0] == "SEND": #sending funds section
				sender = data[1]
				reciver = data[2]
				amount = float(data[3])
				ServerLog("Client request transfer funds")
				#now we have all data needed to transfer money
				#firstly, get current amount of funds in bank
				try:
					file = open("balances/" + sender + ".txt", "r+")
					balance = float(file.readline())
				except:
					ServerLog("Can't checks sender's (" + sender + ") balance")
				#verify that the balance is higher or equal to transfered amount
				if amount > balance:
					try:
						self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
					except socket.error as err:
						if err.errno == errno.ECONNRESET:
							break
				else: #if ok, check if recipient adress exists
					if Path("balances/" + reciver + ".txt").is_file():
						#it exists, now -amount from sender and +amount to reciver
						try:
							#remove amount from senders' balance
							balance -= amount
							file.seek(0)
							file.write(str(balance))
							file.truncate()
							file.close
							#get recipients' balance and add amount
							file = open("balances/" + reciver + ".txt", "r+")
							reciverbal = float(file.readline())
							reciverbal += amount
							file.seek(0)
							file.write(str(reciverbal))
							file.truncate()
							file.close()
							try:
								self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
							except socket.error as err:
								if err.errno == errno.ECONNRESET:
									break
							ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + reciver)
						except:
							try:
								self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
							except socket.error as err:
								if err.errno == errno.ECONNRESET:
									break
					else: #message if recipient doesn't exist
						ServerLog("The recepient", reciver, "doesn't exist!")
						try:
							self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))
						except socket.error as err:
							if err.errno == errno.ECONNRESET:
								break
		ServerLog("Thread (" + thread_id + ") and connection closed")
		#Closing socket connection
		self.clientsock.close()
		#Decrasing number of connected miners
		server_info['miners'] -= 1
		#Delete this miner from statistics
		del hashrates[thread_id]

regex = r'^[\w\d_()]*$'
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
threads = []
kicklist = []
server_info = {'miners' : 0, 'pool_hashrate' : 0, 'users' : 0}
hashrates = {}
config = configparser.ConfigParser()
locker = threading.Lock()

#Initial files and folders checking and creating
if not Path("logs").is_dir():
	mkdir("logs")
if not Path("config").is_dir():
	mkdir("config")
if not Path("users").is_dir():
	mkdir("users")
if not Path("balances").is_dir():
	mkdir("balances")
if not Path("config/lastblock").is_file():
	file = open("config/lastblock", "w")
	file.write(hashlib.sha1(str("revox.heremrkris7100").encode("utf-8")).hexdigest())
	file.close()
if not Path("config/blocks").is_file():
	file = open("config/blocks", "w")
	file.write("0")
	file.close()
#Initial configuration
if not Path("config/ServerConfig.ini").is_file():
	print("Initial configuration, you can edit 'ServerConfig.ini' in 'config' folder later\n")
	host = input("Enter server host adddress: ")
	port = input("Enter server port: ")
	new_user_balance = input("Enter default balance for new users: ")
	reward = input("Enter block reward: ")
	diff_incrase_per = input("Enter how many blocks are needed for incrase difficulty: ")
	config['server'] = {"host": host,
	"port": port,
	"new_user_bal": new_user_balance,
	"reward": reward,
	"diff_incrase_per": diff_incrase_per}
	with open("config/ServerConfig.ini", "w") as configfile:
		config.write(configfile)
#Loading server config from INI if exists
else:
	config.read("config/ServerConfig.ini")
	host = config['server']['host']
	port = config['server']['port']
	new_user_balance = config['server']['new_user_bal']
	reward = config['server']['reward']
	diff_incrase_per = config['server']['diff_incrase_per']
	ServerLog("Loaded server config: " + host + ", " + port + ", " + new_user_balance + ", " + reward + ", " + diff_incrase_per)
#Converting some variables to numbers
port = int(port)
reward = float(reward)
diff_incrase_per = int(diff_incrase_per)
#Binding socket
try:
	tcpsock.bind((host, port))
	ServerLog("Server started...")
except:
	ServerLog("Error during TCP socket...")
	time.sleep(5)
	sys.exit()

#Thread for updating server info
UpdateServerInfo()
#Main server loop
ServerLog("Listening for incoming connections...")
while True:
	#Starting thread for input procesing
	newthread = InputProc()
	newthread.start()
	try:
		#Listening for new connections
		tcpsock.listen(16)
		(conn, (ip, port)) = tcpsock.accept()
		#Starting thread for new connection
		newthread = ClientThread(ip, port, conn)
		newthread.start()
		threads.append(newthread)
	except:
		ServerLog("Error in main loop!")

for t in threads:
	t.join()
