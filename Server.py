#!/usr/bin/env python

###########################################
#   Duino-Coin public-server version 0.4  #
# https://github.com/revoxhere/duino-coin #
#  copyright by MrKris7100 & revox 2019   #
###########################################
# Important: this version of the server is a bit different than one used in "real" duino-coin network.

print("Duino-Coin server version 0.4")
import socket, threading, time, random, hashlib
from pathlib import Path

def percentage(part, whole):
  return 100 * float(part)/float(whole)

class ClientThread(threading.Thread): #separate thread for every user
	def __init__(self,ip,port,clientsock):
		print(clientsock)
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.clientsock = clientsock
		print("[+] New thread started for "+ip+":"+str(port))

	def run(self):
		thread_id = threading.get_ident()
		print("Connection from : "+ip+":"+str(port))
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
				regf = Path(username+".txt")
				if not regf.is_file(): #checking if user already exists
					file = open(username+".txt", "w")
					file.write(password)
					file.close()
					file = open(username+"balance.txt", "w")
					file.write(str(new_users_balance))
					file.close
					self.clientsock.send(bytes("OK", encoding='utf8'))
				if regf.is_file():
					print("Account already exists!")
					self.clientsock.send(bytes("NO", encoding='utf8'))
					break

			if data[0] == "LOGI": #login
				username = data[1]
				password = data[2]
				print("User logging in")
				print(">Username:", username)
				print(">Password:", password)
				file = open(username+".txt", "r")
				data = file.readline()
				file.close()
				self.clientsock.send(bytes("OK", encoding='utf8'))
				print("User logged")
   
			if data[0] == "JOB": #main, mining section
				print("New job for user: " + username)
				with locker:
					print("Thread(" + str(thread_id) + ") Locking resources")
					file = open("lastblock", "r+")
					lastblock = file.readline()
					rand = random.randint(0, 100)
					hashing = hashlib.sha1(str(lastblock + str(rand)).encode("utf-8"))
					self.clientsock.send(bytes(lastblock + "," + hashing.hexdigest(), encoding='utf8'))
					file.seek(0)
					file.write(hashing.hexdigest())
					file.truncate()
					file.close()
					print("Thread(" + str(thread_id) + ") Unlocking resources")
				result = self.clientsock.recv(1024)
				if result.decode() == str(rand):
					print("Good result (" + str(result.decode()) + ")")
					file = open(username+"balance.txt", "r+")
					balance = float(file.readline())
					balance = balance + reward
					file.seek(0)
					file.write(str(balance))
					file.truncate()
					file.close()
					self.clientsock.send(bytes("GOOD", encoding="utf8"))
				else:
					print("Bad result (" + str(result.decode()) + ")")
					self.clientsock.send(bytes("BAD", encoding="utf8"))
					
			if data[0] == "BALA": #check balance section
				print(">>>>>>>>>>>>>> sent balance values")
				file = open(username+"balance.txt", "r")
				balance = file.readline()
				file.close()
				self.clientsock.send(bytes(balance, encoding='utf8'))

			if data[0] == "SEND": #sending funds section
				username = data[1]
				name = data[2]
				amount = data[3]
				print(">>>>>>>>>>>>>> started send funds protocol")
				print("Username:", username)
				print("Receiver username:", name)
				print("Amount", amount)
				#now we have all data needed to transfer money
				#firstly, get current amount of funds in bank
				print("Sent balance values")
				try:
					file = open(username+"balance.txt", "r")
					balance = file.readline()
					file.close()
				except:
					print("Error occured while checking funds!")
				#verify that the balance is higher or equal to transfered amount
				if amount >= balance:
					self.clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
				if amount <= balance: #if ok, check if recipient adress exists
					bankf = Path(name+"balance.txt")
					if bankf.is_file():
						#it exists, now -amount from username and +amount to name
						try:
							print("Amount after 0.1% fee:", recieveramount)
							#get senders' balance
							file = open(username+"balance.txt", "r")
							balance = file.readline()
							file.close()
							#remove amount from senders' balance
							balance = float(balance) - float(amount)
							file = open(username+"balance.txt", "w")
							file.write(str(balance))
							file.close()
							#get recipients' balance
							file = open(name+"balance.txt", "r")
							namebal = file.readline()
							file.close()
							#add amount to recipients' balance
							namebal = float(namebal) + float(recieveramount)
							file = open(name+"balance.txt", "w")
							file.write(str(namebal))
							file.close()
							self.clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
						except:
							self.clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
					if not bankf.is_file(): #message if recipient doesn't exist
						print("The recepient", name, "doesn't exist!")
						self.clientsock.send(bytes("Error! The recipient doesn't exist!", encoding='utf8'))

host = "localhost"
port = 14808
new_users_balance = 0
reward = 0.000005

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []

locker = threading.Lock()

regf = Path("lastblock")
if not regf.is_file():
	file = open("lastblock", "w")
	file.write(hashlib.sha1(str("revox.heremrkris7100").encode("utf-8")).hexdigest())
	file.close()

while True:
	try:
		tcpsock.listen(16)
		print("\nListening for incoming connections...")
		(conn, (ip, port)) = tcpsock.accept()
		newthread = ClientThread(ip, port, conn)
		newthread.start()
		threads.append(newthread)
	except:
		print("Error in main loop!")

for t in threads:
	t.join()
