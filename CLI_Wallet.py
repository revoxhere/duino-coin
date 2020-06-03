#!/usr/bin/env python3
##########################################
# Duino-Coin Console Wallet (v1.5) 
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © revox 2020
##########################################

import socket, configparser, getpass, os, platform, sys, time, json
from signal import signal, SIGINT
from pathlib import Path

try: # Check if requests is installed
	import requests
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Requests is not installed. Please install it using: python3 -m pip install requests.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)

try: # Check if colorama is installed
	from colorama import init, Fore, Back, Style
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Colorama is not installed. Please install it using: python3 -m pip install colorama.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)

timeout = 5 # Socket timeout
VER = 1.5
res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
config = configparser.ConfigParser()
pcusername = getpass.getuser() # Username
platform = str(platform.system()) + " " + str(platform.release()) # Platform information
publicip = requests.get("https://api.ipify.org").text # Public IP
s = socket.socket()

def title(title):
	if os.name == 'nt':
		os.system("title "+title)
	else:
		print('\33]0;'+title+'\a', end='')
		sys.stdout.flush()

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
	print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "See you soon!")
	try:
		s.send(bytes("CLOSE", encoding="utf8"))
	except:
		pass
	os._exit(0)
signal(SIGINT, handler) # Enable signal handler

while True: # Grab data grom GitHub section
	try:
		res = requests.get(res, data = None) #Use request to grab data from raw github file
		if res.status_code == 200: #Check for response
			content = res.content.decode().splitlines() #Read content and split into lines
			pool_address = content[0] #Line 1 = pool address
			pool_port = content[1] #Line 2 = pool port
			try: # Try to connect
				s.connect((str(pool_address), int(pool_port)))
				s.settimeout(timeout)
				SERVER_VER = s.recv(3).decode()

				jsonapi = requests.get("https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json", data = None) # Use request to grab data from raw github file
				if jsonapi.status_code == 200: # Check for reponse
					content = jsonapi.content.decode() # Read content and split into lines
					contentjson = json.loads(content)
					ducofiat = float(contentjson["Duco price"])
				else:
					ducofiat = 0.0024847 * rate # If json api request fails, wallet will use this value
				break # If connection was established, continue
    
			except: # If it wasn't, display a message
				print(Style.RESET_ALL + Fore.RED + "Cannot connect to the server. It is probably under maintenance or temporarily down.\nRetrying in 15 seconds.")
				time.sleep(15)
				os.execl(sys.executable, sys.executable, *sys.argv)
		else:
			print("Retrying connection...")
			time.sleep(0.025) # Restart if wrong status code
    
	except:
		print(Style.RESET_ALL + Fore.RED + " Cannot receive pool address and IP.\nExiting in 15 seconds.")
		time.sleep(15)
		os._exit(1)

while True:
	title("Duino-Coin CLI Wallet")
	if not Path("WalletCLI_config.ini").is_file(): # Initial configuration section
		print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "Duino-Coin CLI Wallet first-run\n")
		print(Style.RESET_ALL + "Select an option")

		choice = input("  1 - Login\n  2 - Register\n  3 - Exit\n")
		if int(choice) <= 1:
			username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
			password = input(Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT)

			s.send(bytes("LOGI," + str(username) + "," + str(password), encoding="utf8"))
			loginFeedback = s.recv(64).decode().split(",")
			if loginFeedback[0] == "OK":
				print(Style.RESET_ALL + Fore.YELLOW + "Successfull login")

				config['wallet'] = {"username": username, "password": password}
	
				with open("WalletCLI_config.ini", "w") as configfile: # Write data to file
					config.write(configfile)
			else:
				print(Style.RESET_ALL + Fore.RED + "Couldn't login, reason: " + Style.BRIGHT + str(loginFeedback[1]))
				time.sleep(15)
				os._exit(1)

		if int(choice) == 2:
			username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
			password = input(Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT)
			pconfirm = input(Style.RESET_ALL + Fore.YELLOW + "Confirm your password: " + Style.BRIGHT)
			email = input(Style.RESET_ALL + Fore.YELLOW + "Enter your e-mail address (used for exchange and support): " + Style.BRIGHT)
			if password == pconfirm:
				while True:
					s.send(bytes("REGI," + str(username) + "," + str(password) + "," + str(email), encoding="utf8"))
					regiFeedback = s.recv(256).decode().split(",")

					if regiFeedback[0] == "OK":
						print(Style.RESET_ALL + Fore.YELLOW + Style.BRIGHT + "Successfully registered new account")
						break
					elif regiFeedback[0] == "NO":
						print(Style.RESET_ALL + Fore.RED + 
							"\nCouldn't register new user, reason: " + Style.BRIGHT + str(regiFeedback[1]))
						time.sleep(15)
						os._exit(1)

		if int(choice) >= 3:
			os._exit(0)

	else: # If config already exists, load from it
		while True:
			config.read("WalletCLI_config.ini")
			username = config["wallet"]["username"]
			password = config["wallet"]["password"]

			s.send(bytes("LOGI," + str(username) + "," + str(password), encoding="utf8"))
			loginFeedback = s.recv(128).decode().split(",")
			if loginFeedback[0] == "OK":
				break
			else:
				print(Style.RESET_ALL + Fore.RED + "Couldn't login, reason: " + Style.BRIGHT + str(loginFeedback[1]))
				time.sleep(15)
				os._exit(1)

		while True:
			while True:
				s.send(bytes("BALA", encoding="utf8"))
				try:
					balance = round(float(s.recv(256).decode()), 8)
					balanceusd = round(float(balance) * float(ducofiat), 4)
					break
				except:
					pass
			print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "\nDuino-Coin CLI Wallet")
			print(Style.RESET_ALL + Fore.YELLOW + "You have " + Style.BRIGHT + str(balance) + " DUCO")
			print(Style.RESET_ALL + Fore.YELLOW + "Which is about " + Style.BRIGHT + str(balanceusd) + " USD")
			print(Style.RESET_ALL + Fore.YELLOW + "Type `help` to list available commands")
			command = input(Style.RESET_ALL + Fore.WHITE + "DUCO Console $ " + Style.BRIGHT)
			if command == "refresh":
				continue

			elif command == "send":
				recipient = input(Style.RESET_ALL + Fore.WHITE + "Enter recipients' username: " + Style.BRIGHT)
				amount = input(Style.RESET_ALL + Fore.WHITE + "Enter amount to transfer: " + Style.BRIGHT)
				s.send(bytes("SEND,deprecated,"+str(recipient)+","+str(amount), encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					print(Style.RESET_ALL + Fore.BLUE + "Server message: " + Style.BRIGHT + str(message))
					break

			elif command == "changepass":
				oldpassword = input(Style.RESET_ALL + Fore.WHITE + "Enter your current password: " + Style.BRIGHT)
				newpassword = input(Style.RESET_ALL + Fore.WHITE + "Enter new password: " + Style.BRIGHT)
				s.send(bytes("CHGP,"+  str(oldpassword) + "," + str(newpassword), encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					print(Style.RESET_ALL + Fore.BLUE + "Server message: " + Style.BRIGHT + str(message))
					break

			elif command == "exit":
				print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "\nSIGINT detected - Exiting gracefully." + Style.NORMAL + " See you soon!")
				try:
					s.send(bytes("CLOSE", encoding="utf8"))
				except:
					pass
				os._exit(0)

			elif command == "userinfo":
				s.send(bytes("STAT", encoding="utf8"))
				while True:
					message = s.recv(1024).decode()
					break
				print(Style.RESET_ALL + Fore.BLUE + "Server message: " + Style.BRIGHT + str(message))

			elif command == "about":
				print(Style.RESET_ALL + Fore.WHITE + "Duino-Coin CLI Wallet is made with <3 by Duino-Coin community")
				print(Style.RESET_ALL + Fore.WHITE + "This is version "+str(VER))
				print(Style.RESET_ALL + Fore.WHITE + "And is distributed under MIT license")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "https://duinocoin.com")
				print(Style.RESET_ALL + Fore.WHITE + "Stay safe everyone!")

			elif command == "logout":
				os.remove("WalletCLI_config.ini")
				os.execl(sys.executable, sys.executable, *sys.argv)

			else:
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "Available commands:")
				print(Style.RESET_ALL + Fore.WHITE + " help - shows this help message")
				print(Style.RESET_ALL + Fore.WHITE + " refresh - refreshes balance")
				print(Style.RESET_ALL + Fore.WHITE + " send - sends funds")
				print(Style.RESET_ALL + Fore.WHITE + " userinfo - displays account informations")
				print(Style.RESET_ALL + Fore.WHITE + " changepass - changes account password")
				print(Style.RESET_ALL + Fore.WHITE + " exit - exits Duino-Coin wallet")
				print(Style.RESET_ALL + Fore.WHITE + " about - displays about message")
				print(Style.RESET_ALL + Fore.WHITE + " logout - logs off the user")
