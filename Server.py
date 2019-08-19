#!/usr/bin/env python

###########################################
#   Duino-Coin public-server version 0.4  #
# https://github.com/revoxhere/duino-coin #
#  copyright by MrKris7100 & revox 2019   #
###########################################
# Important: this version of the server is a bit different than one used in "real" duino-coin network.

print("Duino-Coin server version 0.5")
import socket, threading, time, random, hashlib, math
from pathlib import Path

def percentage(part, whole):
  return 100 * float(part)/float(whole)

class ClientThread(threading.Thread): #separate thread for every user
	def __init__(self, ip, port, clientsock):
		thread_id = str(threading.get_ident())
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsock = clientsock
		print("[+] New thread started (" + thread_id + ")")

	def run(self):
		print("Connection from : " + self.ip + ":" + str(self.port))
		while True:
			data = self.clientsock.recv(1024)
			data = data.decode()
			data = data.split(",")
			if data[0] == "REGI": #registration
				username = data[1]
				password = data[2]
				print("Register request")
				print(">Username:", username)
				print(">Password:", password)
				if not Path(username + ".txt").is_file(): #checking if user already exists
					file = open(username + ".txt", "w")
					file.write(password)
					file.close()
					file = open(username + "balance.txt", "w")
					file.write(str(new_users_balance))
					file.close
					self.clientsock.send(bytes("OK", encoding='utf8'))
				else:
					print("Account already exists!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
					break
			elif data[0] == "LOGI": #login
				username = data[1]
				password = data[2]
				print("User logging in")
				print(">Username:", username)
				print(">Password:", password)
				file = open(username + ".txt", "r")
				data = file.readline()
				file.close()
				self.clientsock.send(bytes("OK", encoding='utf8'))
				print("User logged")
			elif data[0] == "JOB": #main, mining section
				print("New job for user: " + username)
				with locker:
					print("Thread(" + thread_id + ") Locking lastblock")
					file = open("blocks", "r")
					blocks = int(file.readline())
					file.close()
					file = open("lastblock", "r+")
					lastblock = file.readline()
					diff = math.ceil(blocks / diff_incrase_per)
					rand = random.randint(0, 100 * diff)
					hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))
					self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest() + "," + str(diff), encoding='utf8'))
					file.seek(0)
					file.write(hashing.hexdigest())
					file.truncate()
					file.close()
					print("Thread(" + thread_id + ") Unlocking lastblock")
				result = self.clientsock.recv(1024)
				result.decode()
				if result == str(rand):
					print("Good result (" + str(result) + ")")
					file = open(username + "balance.txt", "r+")
					balance = float(file.readline())
					balance += reward
					file.seek(0)
					file.write(str(balance))
					file.truncate()
					file.close()
					self.clientsock.send(bytes("GOOD", encoding="utf8"))
					with locker:
						print("Thread(" + thread_id + ") Locking blocks")
						blocks+= 1
						file = open("blocks", "w")
						file.seek(0)
						file.write(str(blocks))
						file.truncate()
						file.close()
						print("Thread(" + thread_id + ") Unlocking blocks")
				else:
					print("Bad result (" + str(result) + ")")
					self.clientsock.send(bytes("BAD", encoding="utf8"))
					
			elif data[0] == "BALA": #check balance section
				print(">>>>>>>>>>>>>> sent balance values")
				file = open(username + "balance.txt", "r")
				balance = file.readline()
				file.close()
				self.clientsock.send(bytes(balance, encoding='utf8'))

			elif data[0] == "SEND": #sending funds section
				username = data[1]
				name = data[2]
				amount = float(data[3])
				print(">>>>>>>>>>>>>> started send funds protocol")
				print("Username:", username)
				print("Receiver username:", name)
				print("Amount", amount)
				#now we have all data needed to transfer money
				#firstly, get current amount of funds in bank
				print("Sent balance values")
				try:
					file = open(username + "balance.txt", "r+")
					balance = float(file.readline())
				except:
					print("Error occured while checking funds!")
				#verify that the balance is higher or equal to transfered amount
				if amount > balance:
					self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
				else: #if ok, check if recipient adress exists
					if Path(name + "balance.txt").is_file():
						#it exists, now -amount from username and +amount to name
						try:
							#remove amount from senders' balance
							balance -= amount
							file.seek(0)
							file.write(str(balance))
							file.truncate()
							file.close
							#get recipients' balance and add amount
							file = open(name+"balance.txt", "r+")
							namebal = float(file.readline())
							namebal += amount
							file.seek(0)
							file.write(str(namebal))
							file.truncate()
							file.close()
							self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
						except:
							self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
					else: #message if recipient doesn't exist
						print("The recepient", name, "doesn't exist!")
						self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))

host = "localhost"
port = 14808
new_users_balance = 0
reward = 0.000005
diff_incrase_per = 100000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
	tcpsock.bind((host,port))
	print("Server started...")
except:
	print("Error during TCP socket...")
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
print("Listening for incoming connections...")
while True:
	try:
		tcpsock.listen(16)
		(conn, (ip, port)) = tcpsock.accept()
		newthread = ClientThread(ip, port, conn)
		newthread.start()
		threads.append(newthread)
	except:
		print("Error in main loop!")

for t in threads:
	t.join()
