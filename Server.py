#!/usr/bin/env python

###########################################
#        Duino-Coin miner version 0.4     #
# https://github.com/revoxhere/duino-coin #
#  copyright by MrKris7100 & revox 2019   #
###########################################

import socket, threading, time, random, hashlib, configparser, sys
from pathlib import Path

def hush():
	global last_hash_count, hash_count
	last_hash_count = hash_count
	hash_count = 0
	threading.Timer(1.0, hush).start()
shares = [0, 0]
last_hash_count = 0
hash_count = 0
config = configparser.ConfigParser()
if not Path("config.ini").is_file():
	print("Initial configuration, you can edit 'config.ini' later\n")
	pool_address = input("Enter pool adddress (official: serveo.net): ")
	pool_port = input("Enter pool port (official: 14808): ")
	username = input("Enter username: ")
	password = input("Enter password: ")
	config['pool'] = {"address": pool_address,
	"port": pool_port,
	"username": username,
	"password": password}
	with open("config.ini", "w") as configfile:
		config.write(configfile)
else:
	config.read("config.ini")
	pool_address = config["pool"]["address"]
	pool_port = config["pool"]["port"]
	username = config["pool"]["username"]
	password = config["pool"]["password"]

while True:
	print("Connecting to pool...")
	soc = socket.socket()
	try:
		soc.connect((pool_address, int(pool_port)))
		print("Connected!")
		break
	except:
		print("Cannot connect to pool server. Retrying in 30 seconds...")
		time.sleep(30)
	time.sleep(0.025)
print("Logging in...")
soc.send(bytes("LOGI," + username + "," + password, encoding="utf8"))
while True:
	resp = soc.recv(1024).decode()
	if resp == "OK":
		print("Logged in!")
		break
	if resp == "NO":
		print("Error, closing in 5 seconds...")
		soc.close()
		time.sleep(5)
		sys.exit()
	time.sleep(0.025)

print("Start mining...")
hush()
while True:
	soc.send(bytes("JOB", encoding="utf8"))
	while True:
		job = soc.recv(1024).decode()
		if job:
			break
		time.sleep(0.025)

	print("Recived new job from pool.")
	job = job.split(",")
	print("Recived new job from pool. Diff: " + job[2])
	for iJob in range(2 ** int(job[2]) + 1):
		hash = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest()
		hash_count = hash_count + 1
		if job[1] == hash:
			soc.send(bytes(str(iJob), encoding="utf8"))
			while True:
				good = soc.recv(1024).decode()
				if good == "GOOD":
					shares[0] = shares[0] + 1 # Share accepted
					print("Share accepted " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), " + str(last_hash_count) + " H/s")
					break
				elif good == "BAD":
					shares[1] = shares[1] + 1 # SHare rejected
					print("Share rejected " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%), " + str(last_hash_count) + " H/s")
					break
				time.sleep(0.025)
			break
