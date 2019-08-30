#!/usr/bin/env python

###########################################
#   Duino-Coin public-server version 0.5  #
# https://github.com/revoxhere/duino-coin #
#  copyright by MrKris7100 & revox 2019   #
###########################################
# Important: this version of the server is a bit different than one used in "real" duino-coin network.

VER = "0.5"

import socket, threading, time, random, hashlib, math, datetime, re
from pathlib import Path

def ServerLog(whattolog):
	now = datetime.datetime.now()
	now = now.strftime("[%Y-%m-%d %H:%M:%S] ")
	print(now + whattolog)
	
class ClientThread(threading.Thread): #separate thread for every user
	def __init__(self, ip, port, clientsock):
		self.thread_id = str(threading.get_ident())
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsock = clientsock
		ServerLog("New thread started (" + self.thread_id + ")")

	def run(self):
		ServerLog("Connection from : " + self.ip + ":" + str(self.port))
		while True:
			data = self.clientsock.recv(1024)
			data = data.decode()
			data = data.split(",")
			if data[0] == "REGI": #registration
				username = data[1]
				password = data[2]
				ServerLog("Client request account registration.")
				file = open("log.txt", "w")
				file.write("Tried to register user:"+username+" using "+password)
				file.close()
				if re.match(regex,username):
					if not Path(username + ".txt").is_file(): #checking if user already exists
						file = open(username + ".txt", "w")
						file.write(password)
						file.close()
						file = open(username + "balance.txt", "w")
						file.write(str(new_users_balance))
						file.close
						self.clientsock.send(bytes("OK", encoding='utf8'))
						ServerLog("New user (" + username + ") registered")
						file = open("log.txt", "w")
						file.write("Registered: "+username+" using "+password)
						file.close()
					else:
						ServerLog("Account already exists!")
						self.clientsock.send(bytes("NO", encoding='utf8'))
						break
				else:
					ServerLog("Unallowed characters!!!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
					break
			elif data[0] == "LOGI": #login
				username = data[1]
				password = data[2]
				ServerLog("Client request logging in to account " + username)
				if re.match(regex,username):
					try:
						file = open(username + ".txt", "r")
						data = file.readline()
						file.close()
					except:
						ServerLog("User doesn't exist!")
						self.clientsock.send(bytes("NO", encoding='utf8'))
					if password == data:
						self.clientsock.send(bytes("OK", encoding='utf8'))
						ServerLog("Password matches, user logged")
					else:
						ServerLog("Incorrect password")
						self.clientsock.send(bytes("NO", encoding='utf8'))
				else:
					ServerLog("User doesn't exist!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
			elif data[0] == "JOB": #main, mining section
				ServerLog("New job for user: " + username)
				with locker:
					file = open("blocks", "r")
					blocks = int(file.readline())
					file.close()
					file = open("lastblock", "r+")
					lastblock = file.readline()
					diff = math.ceil(blocks / diff_incrase_per)
					rand = random.randint(0, 100 * diff)
					hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))
					ServerLog("Sending target hash: " + hashing.hexdigest())
					self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
					file.seek(0)
					file.write(hashing.hexdigest())
					file.truncate()
					file.close()
				result = self.clientsock.recv(1024).decode()
				if result == str(rand):
					ServerLog("Recived good result (" + str(result) + ")")
					file = open(username + "balance.txt", "r+")
					balance = float(file.readline())
					balance += reward
					file.seek(0)
					file.write(str(balance))
					file.truncate()
					file.close()
					self.clientsock.send(bytes("GOOD", encoding="utf8"))
					with locker:
						blocks+= 1
						file = open("blocks", "w")
						file.seek(0)
						file.write(str(blocks))
						file.truncate()
						file.close()
				else:
					ServerLog("Recived bad result (" + str(result) + ")")
					self.clientsock.send(bytes("BAD", encoding="utf8"))
					
			elif data[0] == "BALA": #check balance section
				ServerLog("Client request balance check")
				file = open(username + "balance.txt", "r")
				balance = file.readline()
				file.close()
				self.clientsock.send(bytes(balance, encoding='utf8'))

			elif data[0] == "SEND": #sending funds section
				sender = data[1]
				reciver = data[2]
				amount = float(data[3])
				ServerLog("Client request transfer funds")
				#now we have all data needed to transfer money
				#firstly, get current amount of funds in bank
				try:
					file = open(sender + "balance.txt", "r+")
					balance = float(file.readline())
				except:
					ServerLog("Can't checks sender's (" + sender + ") balance")
				#verify that the balance is higher or equal to transfered amount
				if amount > balance:
					self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
				else: #if ok, check if recipient adress exists
					if Path(reciver + "balance.txt").is_file():
						#it exists, now -amount from sender and +amount to reciver
						try:
							#remove amount from senders' balance
							balance -= amount
							file.seek(0)
							file.write(str(balance))
							file.truncate()
							file.close
							#get recipients' balance and add amount
							file = open(reciver+"balance.txt", "r+")
							reciverbal = float(file.readline())
							reciverbal += amount
							file.seek(0)
							file.write(str(reciverbal))
							file.truncate()
							file.close()
							self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
							ServerLog("Transferred " + str(amount) + " DUCO from " + sender + " to " + reciver)
						except:
							self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
					else: #message if recipient doesn't exist
						ServerLog("The recepient", reciver, "doesn't exist!")
						self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))

ServerLog("duino-coin Server v" + VER)
host = "localhost"
port = 14808
new_users_balance = 0
reward = 0.000005
regex = r'^[\w\d_()]*$'
diff_incrase_per = 500000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
	tcpsock.bind((host,port))
	ServerLog("Server started...")
except:
	ServerLog("Error during TCP socket...")
	time.sleep(5)
	sys.exit()
threads = []

locker = threading.Lock()

if not Path("lastblock").is_file():
	file = open("lastblock", "w")
	file.write(hashlib.sha1(str("revox.heremrkris7100").encode("utf-8")).hexdigest())
	file.close()
if not Path("blocks").is_file():
	file = open("blocks", "w")
	file.write("0")
	file.close()
ServerLog("Listening for incoming connections...")
while True:
	try:
		tcpsock.listen(16)
		(conn, (ip, port)) = tcpsock.accept()
		newthread = ClientThread(ip, port, conn)
		newthread.start()
		threads.append(newthread)
	except:
		ServerLog("Error in main loop!")

for t in threads:
	t.join()
