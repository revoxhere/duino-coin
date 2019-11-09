print("===========================================")
print("    Duino-Coin PC miner version 0.6.5")
print(" https://github.com/revoxhere/duino-coin")
print("   copyright by MrKris7100 & revox 2019")
print("===========================================\n")

import socket, threading, time, random, hashlib, configparser, sys, datetime, os, pip, signal, time
from decimal import Decimal
from pathlib import Path
from signal import signal, SIGINT

try:
    from colorama import init, Fore, Back, Style
except:
    print("Colorama is not installed. Installing it...")
    pip.main(['install', '--user', 'colorama'])
    print("\n")

global shares, diff, last_hash_count, khash_count, hash_count, config, VER, connection_counter
shares = [0, 0]
diff = 0
last_hash_count = 0
khash_count = 1 #1kh/s if 0 (impossible number)
hash_count = 10000
config = configparser.ConfigParser()
VER = "0.6" #big version number
timeout = 15 #timeout after n seconds
catch = 0

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
	if not Path("MinerConfig_0.6.5.ini").is_file():
		print(Style.BRIGHT + "Initial configuration, you can edit 'MinerConfig_0.6.5.ini' file later.")
		print(Style.RESET_ALL + "Don't have an account? Use " + Fore.YELLOW + "Wallet" + Style.RESET_ALL + " to register.\n")
		pool_address = input(Style.RESET_ALL + "Enter pool adddress " + Fore.YELLOW + "(official: serveo.net): ")
		pool_port = input(Style.RESET_ALL + "Enter pool port " + Fore.YELLOW + "(official: 14808): ")
		username = input(Style.RESET_ALL + "Enter username (the one you used to register): " + Fore.YELLOW)
		password = input(Style.RESET_ALL + "Enter password (the one you used to register): " + Fore.YELLOW)
		efficiency = input(Style.RESET_ALL + "Enter mining intensity " + Fore.YELLOW + "(1-100)%: ")
		config['miner'] = {"address": pool_address,
		"port": pool_port,
		"username": username,
		"password": password,
		"efficiency": efficiency}
		with open("MinerConfig_0.6.5.ini", "w") as configfile:
			config.write(configfile)
	else:
		config.read("MinerConfig_0.6.5.ini")
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
			soc.connect((str(pool_address), int(pool_port)))
			soc.settimeout(timeout)
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.GREEN + "Connected to pool on tcp://"+pool_address+":"+pool_port)
			break
		except:
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.RED + "Cannot connect to pool server. There is probably a server update going on. Retrying in 15 seconds...")
			time.sleep(15)
		time.sleep(0.025)

def checkVersion():
	try:
		SERVER_VER = soc.recv(1024).decode()
		if SERVER_VER == VER:
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.GREEN + "Successfully checked if miner is up-to-date.")
		else:
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.RED + "Miner is outdated, please download latest version from https://github.com/revoxhere/duino-coin/releases/")
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.RED + "Exiting in 15 seconds.")
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
				print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.GREEN + "Successfully logged in.")
				break
			if resp == "NO":
				now = datetime.datetime.now()
				print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.RED + "Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
				soc.close()
				time.sleep(15)
				sys.exit()
		except:
			connect()

		time.sleep(0.025) # Try again if no response

def mine():
	global last_hash_count, hash_count, khash_count, efficiency
	now = datetime.datetime.now()
	print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.GREEN + "Miner thread started, using 'SHA' algorithm.")
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
						print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.GREEN + "accepted: " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Style.DIM + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%)," + Style.NORMAL + Fore.WHITE + " diff: " + str(diff) + ", " + Style.BRIGHT + str(khash_count) + " khash/s " + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
						break
					elif feedback == "BAD":
						now = datetime.datetime.now()
						shares[1] = shares[1] + 1 # Share rejected = increment bad shares counter by 1
						print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Style.RESET_ALL + Fore.RED + "rejected: " + str(shares[1]) + "/" + str(shares[1] + shares[1]) + Style.DIM + " (" + str(shares[0] / (shares[0] + shares[1]) * 100) + "%)," + Style.NORMAL + Fore.WHITE + " diff: " + str(diff) + ", " + Style.BRIGHT + str(khash_count) + " khash/s "  + Style.BRIGHT + Fore.RED + "(boo!!!)")
						break
					time.sleep(0.025) # Try again if no response
				break
	time.sleep(1) # Restart loop

def handler(signal_received, frame):
    # Handle any cleanup here
    print("SIGINT or CTRL-C detected. Exiting gracefully.")
    soc.send(bytes("CLOSE", encoding="utf8"))
    os._exit(0)


init(autoreset=True)
hush()
while True:
    signal(SIGINT, handler)
    try:
            loadConfig() #Firstly, load configfile
    except:
            print(Style.BIRGHT + Fore.RED + "There was an error loading the configfile. Try removing it and re-running configuration."  + Style.RESET_ALL)
    try:
            connect() #Connect to pool
    except:
            print(Style.BIRGHT + Fore.RED + "There was an error connecting to pool. Check your config file." + Style.RESET_ALL)
    try:
            checkVersion() #Check version and display update message if miner isn't updated
    except:
            print(Style.BIRGHT + Fore.RED + "There was an error checking version. Restarting." + Style.RESET_ALL)
    try:
            login() #Login, obviously
    except:
            print(Style.BIRGHT + Fore.RED + "There was an error while logging in. Restarting." + Style.RESET_ALL)
    try:
            mine() #Start mining
    except:
            print(Style.BIRGHT + Fore.RED + "There was an error while mining. Restarting." + Style.RESET_ALL)
    print(Style.RESET_ALL)
    time.sleep(1)

