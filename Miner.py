#!/usr/bin/env python

print("===========================================")
print("    Duino-Coin PC miner version 0.6.1")
print(" https://github.com/revoxhere/duino-coin")
print("   copyright by MrKris7100 & revox 2019")
print("===========================================\n")

import socket, threading, time, random, hashlib, configparser, sys, datetime
from decimal import Decimal
from pathlib import Path

VER = "0.6" #it's really 0.6.1 but we set it as 0.6 because server is still 0.6.1

def hush():
	global last_hash_count, hash_count, khash_count
	last_hash_count = hash_count
	khash_count = last_hash_count / 1000
	hash_count = 0
	threading.Timer(1.0, hush).start()
	
shares = [0, 0]
diff = 0
last_hash_count = 0
khash_count = 0
hash_count = 0
config = configparser.ConfigParser()

if not Path("MinerConfig.ini").is_file():
	print("Initial configuration, you can edit 'MinerConfig.ini' file later.")
	print("Don't have an account? Use Wallet first to register.\n")
	pool_address = input("Enter pool adddress (official: serveo.net): ")
	pool_port = input("Enter pool port (official: 14808): ")
	username = input("Enter username (the one you used to register): ")
	password = input("Enter password (the one you used to register): ")
	config['pool'] = {"address": pool_address,
	"port": pool_port,
	"username": username,
	"password": password}
	with open("MinerConfig.ini", "w") as configfile:
		config.write(configfile)
else:
	config.read("MinerConfig.ini")
	pool_address = config["pool"]["address"]
	pool_port = config["pool"]["port"]
	username = config["pool"]["username"]
	password = config["pool"]["password"]

while True:
	soc = socket.socket()
	try:
		soc.connect((pool_address, int(pool_port)))
		time.sleep(1)
		now = datetime.datetime.now()
		print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Successfully connected to pool on tcp://"+pool_address+":"+pool_port)
		break
	except:
		now = datetime.datetime.now()
		print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Cannot connect to pool server. Retrying in 30 seconds...")
		time.sleep(30)
	time.sleep(0.025)
	
SERVER_VER = soc.recv(1024).decode()
if SERVER_VER == VER:
	now = datetime.datetime.now()
	print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Successfully checked if miner is up-to-date.")
else:
	now = datetime.datetime.now()
	print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Miner is outdated, please download latest version from https://github.com/revoxhere/duino-coin/releases/")
	print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Exiting in 5 seconds.")
	time.sleep(5)
	sys.exit()
	
soc.send(bytes("LOGI," + username + "," + password, encoding="utf8")) # Send login data
while True:
	resp = soc.recv(1024).decode()
	if resp == "OK":
		now = datetime.datetime.now()
		print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Successfully logged in.")
		break
	if resp == "NO":
		now = datetime.datetime.now()
		print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Error! Wrong credentials or account doesn't exist! If you don't have an account, register using Wallet!\nExiting in 5 seconds.")
		soc.close()
		time.sleep(5)
		sys.exit()
	time.sleep(0.025) # Try again if no response after 0.025 seconds

now = datetime.datetime.now()
print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Miner thread started, using 'SHA' algorithm.")
time.sleep(3)
hush() # Start hash counter thread
while True:
	soc.send(bytes("JOB", encoding="utf8"))
	while True:
		job = soc.recv(1024).decode() # Get work from pool
		if job:
			break
		time.sleep(0.025) # Try again if no response after 0.025 seconds
	job = job.split(",") # Split the job received from pool
	diff = job[2]
	for iJob in range(100 * int(job[2]) + 1): # Hashing algorithm
		hash = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest()
		hash_count = hash_count + 1
		if job[1] == hash:
			soc.send(bytes(str(iJob) + "," + str(last_hash_count), encoding="utf8")) # Send result of hashing algorithm to pool
			while True:
				feedback = soc.recv(1024).decode()
				if feedback == "GOOD":
					now = datetime.datetime.now()
					shares[0] = shares[0] + 1 # Share accepted = increment feedback shares counter by 1
					print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "accepted: " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " shares (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), diff: " + str(diff) + ", " + str(khash_count) + " khash/s (yay!!!)")
					break
				elif feedback == "BAD":
					now = datetime.datetime.now()
					shares[1] = shares[1] + 1 # Share rejected = increment bad shares counter by 1
					print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "rejected: " + str(shares[1]) + "/" + str(shares[1] + shares[1]) + " shares (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), diff: " + str(diff) + ", " + str(khash_count) + " khash/s (boo!!!)")
					break
				time.sleep(0.025) # Try again if no response after 0.025 seconds
			break

