#!/usr/bin/env python3
##########################################
# Duino-Coin CLI Wallet (v2.1)
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
import socket, configparser, getpass, os, platform, sys, time, json, datetime
from signal import signal, SIGINT
from pathlib import Path

try:
	from cryptography.fernet import Fernet, InvalidToken
	from cryptography.hazmat.backends import default_backend
	from cryptography.hazmat.primitives import hashes
	from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ModuleNotFoundError:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Cryptography is not installed. Please install it using: python3 -m pip install cryptography.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)


try:
	import secrets
except ModuleNotFoundError:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Secrets is not installed. Please install it using: python3 -m pip install secrets.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)

try:
	from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
except:
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Base64 is not installed. Please install it using: python3 -m pip install base64.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)

wrong_passphrase = False
backend = default_backend()
iterations = 100_000


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

try:
	import tronpy
	from tronpy.keys import PrivateKey
	tronpy_installed = True
except ModuleNotFoundError:
	tronpy_installed = False
	now = datetime.datetime.now()
	print(now.strftime("%H:%M:%S ") + "Tronpy is not installed. Please install it using: python3 -m pip install tronpy.\nWrapper was disabled because of tronpy is needed for !")

timeout = 30 # Socket timeout
VER = 2.1
use_wrapper = False # default value for preventing error
ipfile = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
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

def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(), length=32, salt=salt,
		iterations=iterations, backend=backend)
	return b64e(kdf.derive(password))

def password_encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
	salt = secrets.token_bytes(16)
	key = _derive_key(password.encode(), salt, iterations)
	return b64e(
		b'%b%b%b' % (
			salt,
			iterations.to_bytes(4, 'big'),
			b64d(Fernet(key).encrypt(message)),
		)
	)

def password_decrypt(token: bytes, password: str) -> bytes:
	decoded = b64d(token)
	salt, iterations, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
	iterations = int.from_bytes(iterations, 'big')
	key = _derive_key(password.encode(), salt, iterations)
	return Fernet(key).decrypt(token)


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
		res = requests.get(ipfile, data = None) #Use request to grab data from raw github file
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
					ducofiat = 0.0025 # If json api request fails, wallet will use this value
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




def reconnect():
	while True: # Grab data grom GitHub section
		try:
			res = requests.get(ipfile, data = None) #Use request to grab data from raw github file
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
						ducofiat = 0.0025 # If json api request fails, wallet will use this value
	
				except: # If it wasn't, display a message
					print(Style.RESET_ALL + Fore.RED + "Cannot connect to the server. It is probably under maintenance or temporarily down.\nRetrying in 15 seconds.")
					time.sleep(15)
					os.execl(sys.executable, sys.executable, *sys.argv)
				else:
					return s
			else:
				print("Retrying connection...")
				time.sleep(0.025) # Restart if wrong status code
		except:
			print(Style.RESET_ALL + Fore.RED + " Cannot receive pool address and IP.\nExiting in 15 seconds .")
			time.sleep(15)
			os._exit(1)



while True:
	title("Duino-Coin CLI Wallet")
	if not Path("CLIWallet_config.cfg").is_file(): # Initial configuration section
		print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "Duino-Coin CLI Wallet first-run\n")
		print(Style.RESET_ALL + "Select an option")

		choice = input("  1 - Login\n  2 - Register\n  3 - Exit\n")
		try:
			int(choice)
		except ValueError:
			print("Error, value must be numeric")
		if int(choice) <= 1:
			username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
			password = getpass.getpass(prompt=Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT, stream=None)
			server_timeout = True
			while server_timeout:
				try:
					s.send(bytes("LOGI," + str(username) + "," + str(password) + str(",placeholder"), encoding="utf8"))
					loginFeedback = s.recv(64).decode().split(",")
					server_timeout = False
					if loginFeedback[0] == "OK":
						print(Style.RESET_ALL + Fore.YELLOW + "Successfull login")

						config['wallet'] = {"username": username, "password": password}
						config['wrapper'] = {"use_wrapper": "false"}
			
						with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
							config.write(configfile)
					else:
						print(Style.RESET_ALL + Fore.RED + "Couldn't login, reason: " + Style.BRIGHT + str(loginFeedback[1]))
						time.sleep(15)
						os._exit(1)
				except socket.timeout:
					server_timeout = True

		if int(choice) == 2:
			username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
			password = getpass.getpass(prompt=Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT, stream=None)
			pconfirm = getpass.getpass(prompt=Style.RESET_ALL + Fore.YELLOW + "Confirm your password: " + Style.BRIGHT, stream=None)
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
	else:
		config.read("CLIWallet_config.cfg")
		if config["wrapper"]["use_wrapper"] == "true" and tronpy_installed:
			use_wrapper = True
			if config["wrapper"]["use_custom_passphrase"] == "true":
				passphrase = getpass.getpass(prompt=Style.RESET_ALL + Fore.YELLOW + "Passphrase for decrypting private key : " + Style.BRIGHT, stream=None)
				try:
					priv_key = str(password_decrypt(config["wrapper"]["priv_key"], passphrase))[2:66]
				except InvalidToken:
					print("Invalid passphrase, disabling wrapper for this session")
					use_wrapper = False
					wrong_passphrase = True
			else:
				priv_key = str(password_decrypt(config["wrapper"]["priv_key"], config["wallet"]["password"]))[2:66]
			pub_key = config["wrapper"]["pub_key"]
			tron = tronpy.Tron()
			wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U") # wDUCO contract
			wbalance = wduco.functions.balanceOf(config["wrapper"]["pub_key"])
			try:
				trx_balance = tron.get_account_balance(config["wrapper"]["pub_key"])
			except:
				trx_balance = 0
		while True:
			config.read("CLIWallet_config.cfg")
			username = config["wallet"]["username"]
			password = config["wallet"]["password"]
			s.send(bytes("LOGI," + str(username) + "," + str(password) + str(",placeholder"), encoding="utf8"))
			loginFeedback = s.recv(128).decode().split(",")
			if loginFeedback[0] == "OK":
				break
			else:
				print(Style.RESET_ALL + Fore.RED + "Couldn't login, reason: " + Style.BRIGHT + str(loginFeedback[1]))
				time.sleep(15)
				os._exit(1)

		while True:
			while True:
				try:
					s.send(bytes("BALA", encoding="utf8"))
				except:
					s = reconnect()
				if use_wrapper:
					wbalance = float(wduco.functions.balanceOf(pub_key))/10**6
					try:
						trx_balance = tron.get_account_balance(pub_key)
					except:
						trx_balance = 0
				try:
					balance = round(float(s.recv(256).decode()), 8)
					balanceusd = round(float(balance) * float(ducofiat), 6)
					break
				except:
					pass
			print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "\nDuino-Coin CLI Wallet")
			print(Style.RESET_ALL + Fore.YELLOW + "You have " + Style.BRIGHT + str(balance) + " DUCO")
			print(Style.RESET_ALL + Fore.YELLOW + "Which is about " + Style.BRIGHT + str(balanceusd) + " USD")
			print(Style.RESET_ALL + Fore.YELLOW + "DUCO price : " + Style.BRIGHT + str(ducofiat) + " USD")
			if use_wrapper:
				print(Style.RESET_ALL + Fore.YELLOW + "And also " + Style.BRIGHT + str(wbalance) + " wDUCO")
				pendingbalance = float(wduco.functions.pendingWithdrawals(pub_key, username))/(10**6)
				if pendingbalance > 0:
					print(Style.RESET_ALL + Fore.YELLOW + "Pending unwraps " + Style.BRIGHT + str(pendingbalance) + " wDUCO")
				print(Style.RESET_ALL + Fore.YELLOW + "Tron address for receiving : " + Style.BRIGHT + str(pub_key))
				print(Style.RESET_ALL + Fore.YELLOW + "TRX balance (useful for fees) : " + Style.BRIGHT + str(trx_balance))
			print(Style.RESET_ALL + Fore.YELLOW + "Type `help` to list available commands")
			command = input(Style.RESET_ALL + Fore.WHITE + "DUCO Console $ " + Style.BRIGHT)
			if command == "refresh":
				continue

			elif command == "send":
				recipient = input(Style.RESET_ALL + Fore.WHITE + "Enter recipients' username: " + Style.BRIGHT)
				try:
					amount = float(input(Style.RESET_ALL + Fore.WHITE + "Enter amount to transfer: " + Style.BRIGHT))
				except ValueError:
					print("NO, Amount should be numeric... aborting")
					continue
				
				
				
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
				try:
					message = s.recv(1024).decode()
				except:
					s = reconnect()
				print(Style.RESET_ALL + Fore.BLUE + "Server message: " + Style.BRIGHT + str(message))

			elif command == "wrapperconf": # wrapper config
				config.read("CLIWallet_config.cfg")
				if not config["wrapper"]["use_wrapper"] == "true" and tronpy_installed:
					print(Style.RESET_ALL + Fore.WHITE + "Select an option")
					try:
						choice = int(input("1 - Generate a new key\n2 - Import a key \n3 - Cancel\n"))
						if choice <= 1:
							priv_key = str(PrivateKey.random())
							pub_key = PrivateKey(bytes.fromhex(priv_key)).public_key.to_base58check_address()
							print("How do you want to encrypt private keey within config file ?")
							incorrect_value = True
							while incorrect_value:
								try:
									encryption_choice = int(input("1 - encrypt it using DUCO password\n2 - use your custom passphrase (more secure)"))
									incorrect_value = False
								except ValueError:
									print("Error, should be numeric")
									incorrect_value = True
								if encryption_choice <= 1:
									config['wrapper'] = {"use_wrapper" : "true", "priv_key" : str(password_encrypt(priv_key.encode(), password).decode()), "pub_key" : pub_key, "use_custom_passphrase" : "false"}
									with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
										config.write(configfile)
										print("Success !")
								elif encryption_choice >= 2:
									print("Input your passphrase for encrypting private key !")
									passphrase = input("passphrase : ")
									config['wrapper'] = {"use_wrapper" : "true", "priv_key" : str(password_encrypt(priv_key.encode(), passphrase).decode()), "pub_key" : pub_key, "use_custom_passphrase" : "true"}
									with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
										config.write(configfile)
										print("Success !")
						elif choice == 2:
							priv_key = input("Input your own private key : ")
							try:
								pub_key = PrivateKey(bytes.fromhex(priv_key)).public_key.to_base58check_address()
								print("How do you want to encrypt private keey within config file ?")
								incorrect_value = True
								while incorrect_value:
									try:
										encryption_choice = int(input("1 - encrypt it using DUCO password (low security)\n2 - use your custom passphrase (more secure)\n"))
										incorrect_value = False
									except ValueError:
										print("Error, should be numeric")
										incorrect_value = True
									if encryption_choice <= 1:
										config['wrapper'] = {"use_wrapper" : "true", "priv_key" : str(password_encrypt(priv_key.encode(), password).decode()), "pub_key" : pub_key, "use_custom_passphrase" : "false"}
										with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
											config.write(configfile)
											print("Success !")
									elif encryption_choice >= 2:
										print("Input your passphrase for encrypting private key !")
										passphrase = input("passphrase : ")
										config['wrapper'] = {"use_wrapper" : "true", "priv_key" : str(password_encrypt(priv_key.encode(), passphrase).decode()), "pub_key" : pub_key, "use_custom_passphrase" : "true"}
										with open("CLIWallet_config.cfg", "w") as configfile: # Write data to file
											config.write(configfile)
											print("Success !")
							except ValueError:
								print("Incorrect key was provided")
						else:
							print("Cancelled...")
							
					except ValueError:
						print(Style.RESET_ALL + Fore.WHITE + "Incorrect value was provided" + Style.bright)
				elif not tronpy_installed:
					print(now.strftime("%H:%M:%S ") + "Tronpy is not installed. Please install it using: python3 -m pip install tronpy")

			elif command == "wrap":
				if use_wrapper:
					try:
						amount = float(input(Style.RESET_ALL + Fore.WHITE + "Enter amount to wrap (minimum is 10): " + Style.BRIGHT))
					except ValueError:
						print("NO, Amount should be numeric... aborting")
						continue
						
					try:
						s.send(bytes("BALA", encoding="utf8"))
						balance = round(float(s.recv(256).decode()), 8)
					except:
						s = reconnect()
					if float(amount) >= 10 and float(amount) <= balance:
						tron_address = input(Style.RESET_ALL + Fore.WHITE + "Enter tron address, or leave blank to choose local wallet: " +Style.BRIGHT)
						if tron_address == "":
							tron_address = pub_key
						s.send(bytes(str("WRAP,")+str(amount)+str(",")+str(tron_address), encoding='utf8'))
					elif float(amount) < 10 and not float(amount) > balance:
						print("Error, minimum amount is 10 DUCO")
					else:
						print("Error, unsufficient balance")
				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")
				
			elif command == "unwrap":
				if use_wrapper:
					pendingvalues = wduco.functions.pendingWithdrawals(pub_key, username)
					txn_success = False # transaction wasn't initiated, but variable should be declared
					try:
						amount = float(input(Style.RESET_ALL + Fore.WHITE + "Enter amount to unwrap: " + Style.BRIGHT))
					except ValueError:
						print("NO, Value should be numeric... aborting")
						continue
					if int(float(amount)*10**6) >= pendingvalues:
						toInit = int(float(amount)*10**6)-pendingvalues
					else:
						toInit = amount*10**6
					if toInit > 0:
						txn = wduco.functions.initiateWithdraw(username,toInit).with_owner(pub_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(priv_key)))
						print("Initiating unwrap...\nTXid :", txn.txid)
						txn = txn.broadcast()
						txnfeedback = txn.result()
						if txnfeedback:
							txn_success = True
						else:
							txn_success = False
							
					if amount <= pendingvalues:
						print("Amount is over pending values, using pending values in order to save txn fees")
						
					if txn_success or amount <= pendingvalues:
						s.send(bytes(str("UNWRAP,")+str(amount)+str(",")+str(pub_key), encoding='utf8'))
					else:
						print("There was an error while initiating unwrap, aborting")

					if amount <= pendingvalues:
						print("Amount is over pending values, using pending values in order to save txn fees")

				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")

			elif command == "cancelunwraps":
				if use_wrapper:
					txn = wduco.functions.cancelWithdrawals(pub_key,username).with_owner(pub_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(priv_key)))
					print("Transaction sent, txid :", txn.txid)
					txn = txn.broadcast()
					if txn.result():
						print("Success")
					else:
						print("Failed, you should have enough energy or trx")
				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")
					
					
					
			elif command == "finishunwraps":
				if use_wrapper:
					pendingvalues = float(wduco.functions.pendingWithdrawals(pub_key, username))/(10**6)
					s.send(bytes(str("UNWRAP,")+str(pendingvalues)+str(",")+str(pub_key), encoding='utf8'))
					print("Finished unwrapping", str(pendingvalues), "DUCOs")
				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")
					
			
			elif command == "exportwrapkey":
				if use_wrapper:
					confirmation = input("Type YES for confirming export of private key : ")
					if confirmation == "YES":
						print("Private key :", priv_key)
					else:
						print("Cancelled, invalid confirmation")
				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")

			elif command == "wsend":
				if use_wrapper:
					recipient = input(Style.RESET_ALL + Fore.WHITE + "Enter recipients' TRON address: " + Style.BRIGHT)
					try:
						amount = float(input(Style.RESET_ALL + Fore.WHITE + "Enter amount to transfer: " + Style.BRIGHT))
					except ValueError:
						print("NO, Amount should be numeric... aborting")
						continue
					wbalance = float(wduco.functions.balanceOf(pub_key))/10**6
					if float(amount) <= wbalance:
						txn = wduco.functions.transfer(recipient,int(float(amount)*10**6)).with_owner(pub_key).fee_limit(5_000_000).build().sign(PrivateKey(bytes.fromhex(priv_key)))
						txn = txn.broadcast()
						print("Transaction submitted to TRON network\nTXid :", txn.txid)
						trontxresult = txn.wait()
						if trontxresult:
							print("Successful transaction")
						else:
							print("Error while confirming transaction")
				elif wrong_passphrase:
					print("Wrapper disabled, you entered a wrong passphrase")
				else:
					print("Wrapper disabled, configure it using `wrapperconf`")

			elif command == "about":
				print(Style.RESET_ALL + Fore.WHITE + "Duino-Coin CLI Wallet is made with <3 by Duino-Coin community")
				print(Style.RESET_ALL + Fore.WHITE + "This is version "+str(VER))
				print(Style.RESET_ALL + Fore.WHITE + "And is distributed under MIT license")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "https://duinocoin.com")
				print(Style.RESET_ALL + Fore.WHITE + "Stay safe everyone!")
				print(Style.RESET_ALL + Fore.WHITE + "Server version : " + Style.BRIGHT + SERVER_VER + Style.RESET_ALL)
				if float(SERVER_VER) > VER:
					print(Style.RESET_ALL + Fore.YELLOW + "Server is " + Fore.WHITE + Style.BRIGHT + SERVER_VER + Fore.YELLOW +Style.RESET_ALL + ", but client is " + Style.BRIGHT + Fore.WHITE + VER + Style.RESET_ALL + Fore.YELLOW + ", you should consider downloading last release")
				else:
					print(Style.RESET_ALL + Fore.WHITE + "Client is up-to-date :D")

			elif command == "logout":
				os.remove("CLIWallet_config.cfg")
				os.execl(sys.executable, sys.executable, *sys.argv)

			elif command == "donate":
				print(Style.RESET_ALL + Fore.BLUE + Style.BRIGHT + "Feel free of donating for helping to maintain DUCO and wDUCO (wrapping/unwrapping involves fees for maintainers) ?")
				print(Style.RESET_ALL + Fore.YELLOW + "TRON and tokens : " + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "TY5wfM6JsYKEEMfQR3RBQBPKfetTpf7nyM" + Style.RESET_ALL + Fore.YELLOW + " (wrapper's address)")
				print("Duino-Coin : " + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "revox"  + Style.RESET_ALL + Fore.YELLOW + " (revox, DUCO lead developer)")
				print("Duino-Coin : " + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "acridkiller"  + Style.RESET_ALL + Fore.YELLOW + " (Acrid, duco faucet maintainer)")
				print("Duino-Coin : " + Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + "Yanis"  + Style.RESET_ALL + Fore.YELLOW + " (wDUCO developer)")

			else:
				print(Style.RESET_ALL + Fore.YELLOW + " DUCO commands:")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " help" + Style.RESET_ALL + " - shows this help message")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " refresh" + Style.RESET_ALL + " - refresh balance")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " send" + Style.RESET_ALL + " - send funds")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " userinfo" + Style.RESET_ALL + " - displays account informations")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " changepass" + Style.RESET_ALL + " - changes account password")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " exit" + Style.RESET_ALL + " - exit Duino-Coin wallet")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " about" + Style.RESET_ALL + " - displays about message")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " donate" + Style.RESET_ALL + " - donate to developpers/maintainers of the program")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " logout" + Style.RESET_ALL + " - logs off the user\n")
				print(Style.RESET_ALL + Fore.YELLOW + " Wrapper-related commands:")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " wsend" + Style.RESET_ALL + " - sends wDUCO via tron - you should have some TRX or tron energy for txn fees")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " wrapperconf" + Style.RESET_ALL + " - set wrapper config")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " wrap" + Style.RESET_ALL + " - wrap DUCO on tron")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " unwrap" + Style.RESET_ALL + " - unwrap wDUCO - you should have some TRX or tron energy for txn fees")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " cancelunwrap" + Style.RESET_ALL + " - sends back pending unwrap values to wallet - you should have some trx or tron energy for txn fees")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " finishunwraps" + Style.RESET_ALL + " - completes pending unwraps")
				print(Style.RESET_ALL + Fore.WHITE + Style.BRIGHT + " exportwrapkey" + Style.RESET_ALL + " - exports wrapper private key")
