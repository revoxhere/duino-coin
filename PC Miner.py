print("===========================================")
print("    Duino-Coin PC miner version 0.6.4")
print(" https://github.com/revoxhere/duino-coin")
print("   copyright by MrKris7100 & revox 2019")
print("===========================================\n")

import socket, threading, time, random, hashlib, configparser, sys, datetime
from decimal import Decimal
from pathlib import Path

global shares, diff, last_hash_count, khash_count, hash_count, config, VER, connection_counter
shares = [0, 0]
diff = 0
last_hash_count = 0
khash_count = 10
hash_count = 10000
config = configparser.ConfigParser()
connection_counter = 0
VER = "0.6" #big version number

def hush():
	global last_hash_count, hash_count, khash_count
	last_hash_count = hash_count
	khash_count = last_hash_count / 1000
	if khash_count == 0:
		khash_count = 10.0
	hash_count = 0
	threading.Timer(1.0, hush).start()

def loadConfig():
	global pool_address, pool_port, username, password, efficiency
	if not Path("MinerConfig_0.6.4.ini").is_file():
		print("Initial configuration, you can edit 'MinerConfig_0.6.4.ini' file later.")
		print("Don't have an account? Use Wallet to register.\n")
		pool_address = input("Enter pool adddress (official: serveo.net): ")
		pool_port = input("Enter pool port (official: 14808): ")
		username = input("Enter username (the one you used to register): ")
		password = input("Enter password (the one you used to register): ")
		efficiency = input("Enter mining intensity (1-100)%: ")
		config['miner'] = {"address": pool_address,
		"port": pool_port,
		"username": username,
		"password": password,
		"efficiency": efficiency}
		with open("MinerConfig_0.6.4.ini", "w") as configfile:
			config.write(configfile)
	else:
		config.read("MinerConfig_0.6.4.ini")
		pool_address = config["miner"]["address"]
		pool_port = config["miner"]["port"]
		username = config["miner"]["username"]
		password = config["miner"]["password"]
		efficiency = config["miner"]["efficiency"]
	
def connect():
	global soc, connection_counter
	while True:
		soc = socket.socket()
		try:
			if connection_counter > 0:
				now = datetime.datetime.now()
				print(now.strftime("[%H:%M:%S] ") + "SSH tunnel is on but no response from pool. Retrying in 15 seconds...")
				time.sleep(15)
				connection_counter = 0
				connect()
			soc.connect((str(pool_address), int(pool_port)))
			soc.settimeout(1.0)
			now = datetime.datetime.now()
			print(now.strftime("[%H:%M:%S] ") + "Connected to pool on tcp://"+pool_address+":"+pool_port)
			connection_counter = int(connection_counter) + 1
			break
		except:
			now = datetime.datetime.now()
			print(now.strftime("[%H:%M:%S] ") + "Cannot connect to pool server. Outage? Server update? Retrying in 15 seconds...")
			time.sleep(15)
		time.sleep(0.025)

def checkVersion():
	try:
		SERVER_VER = soc.recv(1024).decode()
		if SERVER_VER == VER:
			now = datetime.datetime.now()
			print(now.strftime("[%H:%M:%S] ") + "Successfully checked if miner is up-to-date.")
		else:
			now = datetime.datetime.now()
			print(now.strftime("[%H:%M:%S] ") + "Miner is outdated, please download latest version from https://github.com/revoxhere/duino-coin/releases/")
			print(now.strftime("[%H:%M:%S] ") + "Exiting in 15 seconds.")
			time.sleep(15)
			sys.exit()
	except:
		connect()

def login():
	while True:
		try:
			try:
				soc.send(bytes("LOGI," + username + "," + password, encoding="utf8")) # Send login data
			except:
				connect()
			resp = soc.recv(1024).decode()
			if resp == "OK":
				now = datetime.datetime.now()
				print(now.strftime("[%H:%M:%S] ") + "Successfully logged in.")
				break
			if resp == "NO":
				now = datetime.datetime.now()
				print(now.strftime("[%H:%M:%S] ") + "Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
				soc.close()
				time.sleep(15)
				sys.exit()
		except:
			connect()

		time.sleep(0.025) # Try again if no response

def mine():
	global last_hash_count, hash_count, khash_count, efficiency
	now = datetime.datetime.now()
	print(now.strftime("[%H:%M:%S] ") + "Miner thread started, using 'SHA' algorithm.")
	hush() # Start hash counter thread
	efficiency = 100 - int(efficiency)
	efficiency = efficiency * 0.01
	while True:
		time.sleep(efficiency)
		soc.send(bytes("JOB", encoding="utf8"))
		while True:
			try:
				job = soc.recv(1024).decode() # Get work from pool
			except:
				break
			if job:
				break
			time.sleep(0.025) # Try again if no response
		try:
			job = job.split(",") # Split the job received from pool
			diff = job[2]
		except:
			break
		for iJob in range(100 * int(job[2]) + 1): # Hashing algorithm
			hash = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest()
			hash_count = hash_count + 1
			if job[1] == hash:
				soc.send(bytes(str(iJob) + "," + str(last_hash_count), encoding="utf8")) # Send result of hashing algorithm to pool
				while True:
					try:
					    feedback = soc.recv(1024).decode()
					except:
						connect()
					if feedback == "GOOD":
						now = datetime.datetime.now()
						shares[0] = shares[0] + 1 # Share accepted = increment feedback shares counter by 1
						print(now.strftime("[%H:%M:%S] ") + "accepted: " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), diff: " + str(diff) + ", " + str(khash_count) + " khash/s (yay!!!)")
						break
					elif feedback == "BAD":
						now = datetime.datetime.now()
						shares[1] = shares[1] + 1 # Share rejected = increment bad shares counter by 1
						print(now.strftime("[%H:%M:%S] ") + "rejected: " + str(shares[1]) + "/" + str(shares[1] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), diff: " + str(diff) + ", " + str(khash_count) + " khash/s (boo!!!)")
						break
					time.sleep(0.025) # Try again if no response
				break
while True:
	try:
		loadConfig() #Firstly, load configfile
	except:
		print("There was an error loading the configfile. Try removing it and entering credentials again.")
	try:
		connect() #Connect to pool
	except:
		print("There was an error connecting to pool.")
	try:
		checkVersion() #Check version and display update message if miner isn't updated
	except:
		print("There was an error checking version.")
	try:
		login() #Login, obviously
	except:
		print("There was an error while logging in.")
	try:
		mine() #Start mining
	except:
		print("There was an error while mining.")
	time.sleep(0.025) # Restart loop
