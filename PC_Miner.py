#!/usr/bin/env python3
#############################################
# Duino-Coin PC Miner (Beta v1) © revox 2020
# https://github.com/revoxhere/duino-coin 
#############################################
import socket, statistics, threading, time, random, re, hashlib, configparser, sys, datetime, os, signal # Import libraries
from decimal import Decimal
from pathlib import Path
from signal import signal, SIGINT

try: # Check if colorama is installed
	from colorama import init, Fore, Back, Style
except:
	print("Colorama is not installed. Please install it using pip install colorama. Exiting in 15s.")
	time.sleep(15)
	os._exit()

try: # Check if requests is installed
	import requests
except:
	print("Requests is not installed. Please install it using pip install requests. Exiting in 15s.")
	time.sleep(15)
	os._exit()

# Setting variables
shares = [0, 0]
diff = 0
res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []
config = configparser.ConfigParser()
VER = "0.6" # "Big" version number
timeout = 10 # Socket timeout

def Greeting(): # Greeting message depending on time :)
	global greeting, message
	print(Style.RESET_ALL)
	
	current_hour = time.strptime(time.ctime(time.time())).tm_hour
	
	if current_hour < 12 :
		greeting = "Good morning"
	elif current_hour == 12 :
		greeting = "Good noon"
	elif current_hour > 12 and current_hour < 18 :
		greeting = "Good afternoon"
	elif current_hour >= 18 :
		greeting = "Good evening"
		
	message     ="▋ Duino-Coin PC Miner (Beta v1) © revox 2019-2020\n" # Startup message
	message   += "▋ https://github.com/revoxhere/duino-coin\n"
	message   += "▋ "+str(greeting)+", "+str(username)+"!\n\n"
	
	for char in message:
		sys.stdout.write(char)
		sys.stdout.flush()
		time.sleep(0.01)

def hush(): # Hashes/sec calculation
	global last_hash_count, hash_count, khash_count, hash_mean
	
	last_hash_count = hash_count
	khash_count = last_hash_count / 1000
	if khash_count == 0:
		khash_count = 1.01
		
	hash_mean.append(khash_count) # Calculate average hashrate
	khash_count = statistics.mean(hash_mean)
	khash_count = round(khash_count, 2)
	
	hash_count = 0 # Reset counter
	
	threading.Timer(1.0, hush).start() # Run this def every 1s
	

def loadConfig(): # Config loading section
	global pool_address, pool_port, username, password, efficiency
	
	if not Path("MinerConfig_beta.1.ini").is_file(): # Initial configuration section
		print(Style.BRIGHT + "Initial configuration, you can edit 'MinerConfig_beta.1.ini' file later.")
		print(Style.RESET_ALL + "Don't have an account? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register.\n")

		username = input("Enter username (the one you used to register): ")
		password = input("Enter password (the one you used to register): ")
		efficiency = input("Enter mining intensity " + "(1-100)%: ")
		supporter = input("Do you want to additionally support the network?  (y/n) ")
		
		efficiency = re.sub("\D", "", efficiency)  # Check wheter efficiency is correct
		if int(efficiency) > int(100):
			efficiency = 100
		if int(efficiency) < int(1):
			efficiency = 1
			
		config['miner'] = { # Format data
		"username": username,
		"password": password,
		"efficiency": efficiency,
                "supporter": supporter}
		
		with open("MinerConfig_beta.1.ini", "w") as configfile: # Write data to file
			config.write(configfile)

	else: # If config already exists, load from it
		config.read("MinerConfig_beta.1.ini")
		username = config["miner"]["username"]
		password = config["miner"]["password"]
		efficiency = config["miner"]["efficiency"]
		supporter = config["miner"]["supporter"]


def Connect(): # Connect to pool section
	global soc, connection_counter, res, pool_address, pool_port
	
	while True: # Grab data grom GitHub section
		try:
			try:
				res = requests.get(res, data = None) #Use request to grab data from raw github file
			except:
				pass
			if res.status_code == 200: #Check for response
				content = res.content.decode().splitlines() #Read content and split into lines
				pool_address = content[0] #Line 1 = pool address
				pool_port = content[1] #Line 2 = pool port

				now = datetime.datetime.now()
				print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Successfully received pool address and IP.")
				break # Continue
			else:
				time.sleep(0.025) # Restart if wrong status code
				
		except:
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Cannot receive pool address and IP. Exiting in 15 seconds.")
			time.sleep(15)
			os._exit()
			
		time.sleep(0.025)
		
	while True:
		try: # Shutdown previous connections if any
			soc.shutdown(socket.SHUT_RDWR)
			soc.close()
		except:
			pass
		
		try:
			soc = socket.socket()
		except:
			Connect() # Reconnect if pool down
		
		try: # Try to connect
			soc.connect((str(pool_address), int(pool_port)))
			soc.settimeout(timeout)
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Connected to pool on tcp://"+pool_address+":"+pool_port)
			break # If connection was established, continue
		
		except: # If it wasn't, display a message and exit
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Cannot connect to pool server. There is probably a server update going on. Retrying in 15 seconds...")
			time.sleep(15)
			os._exit()
			
		Connect()	
		time.sleep(0.025)
		

def checkVersion():
	try:
		try:
			SERVER_VER = soc.recv(1024).decode() # Check server version
		except:
			Connect() # Reconnect if pool down
			
		if SERVER_VER == VER: # If miner is up-to-date, display a message and continue
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Successfully checked if miner is up-to-date.")

		else:
			now = datetime.datetime.now()
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Miner is outdated (v"+VER+"), server is on v"+SERVER_VER+" please download latest version from https://github.com/revoxhere/duino-coin/releases/")
			print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Exiting in 15 seconds.")
			time.sleep(15)
			os._exit()
	except:
		Connect() # Reconnect if pool down


def Login():
	while True:
		try:
			try:
				soc.send(bytes("LOGI," + username + "," + password, encoding="utf8")) # Send login data
			except:
				Connect() # Reconnect if pool down
				
			try:
				resp = soc.recv(1024).decode()
			except:
				Connect() # Reconnect if pool down
				
			if resp == "OK": # Check wheter login information was correct
				now = datetime.datetime.now()
				print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Successfully logged in.")
				break # If it was, continue
			
			if resp == "NO":
				now = datetime.datetime.now()
				print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
				soc.close()
				time.sleep(15)
				os._exit() # If it wasn't, display a message and exit
		except:
			Connect() # Reconnect if pool down

		time.sleep(0.025) # Try again if no response


def Mine(): # Mining section
	global last_hash_count, hash_count, khash_count, efficiency
	
	now = datetime.datetime.now()
	print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Miner thread started using SHA1 algorithm.")

	efficiency = 100 - int(efficiency) # Calulate efficiency
	efficiency = efficiency * 0.01
	while True:
		time.sleep(efficiency) # Sleep to achieve lower efficiency
		try:
			soc.send(bytes("JOB", encoding="utf8")) # Send job request
		except:
			Connect() # Reconnect if pool down
		while True:
			try:
				job = soc.recv(1024).decode() # Get work from pool
			except:
				Connect() # Reconnect if pool down
			if job:
				break # If job received, continue to hashing algo
			time.sleep(0.025) # Try again if no response
		try:
			job = job.split(",") # Split received data to job and difficulty
			diff = job[2]
		except:
			Connect() # Reconnect if pool down
			
		for iJob in range(100 * int(job[2]) + 1): # Calculate numbers with difficulty
			hash = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest() # Calculate hash
			hash_count = hash_count + 1 # Increment hash counter
			
			if job[1] == hash: # If result is even with job, send the result
				try:
					soc.send(bytes(str(iJob) + "," + str(last_hash_count), encoding="utf8")) # Send result of hashing algorithm to pool
				except:
					Connect() # Reconnect if pool down
					
				while True:
					try:
						feedback = soc.recv(1024).decode() # Get feedback
					except:
						Connect() # Reconnect if pool down
					if feedback == "GOOD": # If result was good
						now = datetime.datetime.now()
						shares[0] = shares[0] + 1 # Share accepted = increment feedback shares counter by 1
						print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.YELLOW + "Accepted: " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%)," + Style.NORMAL + Fore.WHITE + " diff: " + str(diff) + ", " + Style.BRIGHT + str(khash_count) + " khash/s " + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
						break # Repeat
					elif feedback == "BAD": # If result was bad
						now = datetime.datetime.now()
						shares[1] = shares[1] + 1 # Share rejected = increment bad shares counter by 1
						print(now.strftime(Style.DIM + "[%H:%M:%S] ") + Fore.RED + "Rejected: " + str(shares[1]) + "/" + str(shares[1] + shares[1]) + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%)," + Style.NORMAL + Fore.WHITE + " diff: " + str(diff) + ", " + Style.BRIGHT + str(khash_count) + " khash/s "  + Style.BRIGHT + Fore.RED + "(boo!!!)")
						break # Repeat
					time.sleep(0.025) # Try again if no response
				break # Repeat


def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
    print("\nSIGINT or CTRL-C detected. Exiting gracefully.")
    soc.send(bytes("CLOSE", encoding="utf8"))
    os._exit(0)


init(autoreset=True) # Enable colorama
hush() # Start hash calculator

while True:
    signal(SIGINT, handler) # Enable signal handler
    
    try:
            loadConfig() # Load configfile
    except:
            print(Style.BRIGHT + Fore.RED + "There was an error loading the configfile. Try removing it and re-running configuration."  + Style.RESET_ALL)

    try:
	    Greeting() # Display greeting message
    except:
	    print(Style.BRIGHT + Fore.RED + "You somehow managed to break the greeting message!"  + Style.RESET_ALL)

    try:
            Connect() # Connect to pool
    except:
            print(Style.BRIGHT + Fore.RED + "There was an error connecting to pool. Check your config file." + Style.RESET_ALL)

    try:
            checkVersion() # Check version
    except:
            print(Style.BRIGHT + Fore.RED + "There was an error checking version. Restarting." + Style.RESET_ALL)

    try:
            Login() # Login
    except:
            print(Style.BRIGHT + Fore.RED + "There was an error while logging in. Restarting." + Style.RESET_ALL)

    try:
            Mine() # Mine
    except:
            print(Style.BRIGHT + Fore.RED + "There was an error while mining. Restarting." + Style.RESET_ALL)

    print(Style.RESET_ALL)
    time.sleep(0.025) # Restart if error
    print("Something went wrong! Restarting main program loop!")
