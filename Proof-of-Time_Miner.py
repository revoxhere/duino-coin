#!/usr/bin/env python3
###############################################
# Duino-Coin PoT Miner (Beta 3) © revox 2020
# https://github.com/revoxhere/duino-coin 
###############################################
import socket, statistics, threading, time, re, configparser, sys, getpass, platform, datetime, os, signal, subprocess # Import libraries
from decimal import Decimal
from pathlib import Path
from signal import signal, SIGINT

try: # Check if colorama is installed
  from colorama import init, Fore, Back, Style
  init(autoreset=True) # Enable colorama
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "✗ Colorama is not installed. Please install it using pip install colorama.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if requests is installed
  import requests
except:
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Requests is not installed. Please install it using pip install requests.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if numpy is installed
  import numpy
except:
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Numpy is not installed. Please install it using pip install numpy.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if tendo is installed
	from tendo import singleton
except:
	now = datetime.datetime.now()
	print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Tendo is not installed. Please install it using pip install tendo.\nExiting in 15s.")
	time.sleep(15)
	os._exit(1)

if not Path("PoT_b3_resources").is_dir(): # Check if resources folder exists
  try:
    os.mkdir("PoT_b3_resources") # Create resources folder
  except:
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Couldn't create resources directory.\nExiting in 15s.")

if not os.name == 'nt': # Check if running on Windows
  now = datetime.datetime.now()
  win = input(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ You can use Proof-Of-Time Miner only on Windows. Continue anyway? [y/n] ")
  if win != "y":
    os._exit(0)

# Set variables
res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Server IP file
income = 0
timer = 45
reward = 0.0252195 # Default PoT reward
config = configparser.ConfigParser()
VER = "0.9" # "Big" version number  (0.9 = Beta 3)
timeout = 10 # Socket timeout
pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP

try: # Check if another pcminer instance is already running
        potminer = singleton.SingleInstance()
except:
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Only one instance can be running at once.\nExiting in 15 seconds.")
        time.sleep(15)
        os._exit(1)

def handler(signal_received, frame): # If SIGINT received, do as much cleanup as possible
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "\n%H:%M:%S ") + Fore.YELLOW + "✓ SIGINT detected - exiting gracefully. See you soon!")
  try:
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=process.pid), shell=True, stderr=subprocess.DEVNULL) # Exit Magi Miner
  except:
        pass
  try:
        soc.send(bytes("CLOSE", encoding="utf8")) # Let the server niecely close the connection
  except:
        pass
  os._exit(0)

signal(SIGINT, handler) # Enable signal handler

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
  else:
    greeting = "Hello"
    
  message  = "║ Duino-Coin Proof-of-Time Miner (Beta 3) © revox 2019-2020\n" # Startup message
  message += "║ https://github.com/revoxhere/duino-coin\n"
  message += "║ "+str(greeting)+", "+str(username)+" \U0001F44B\n\n"
  
  for char in message:
    sys.stdout.write(char)
    sys.stdout.flush()
    time.sleep(0.01)


def loadConfig(): # Config loading section
  global pool_address, pool_port, username, password, efficiency, cmd
  cmd = "cd PoT_b3_resources & PoT_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_potminer -p x -e 10 -s 4" # Miner command

  if not Path("PoT_b3_resources/PoT_executable.exe").is_file(): # Initial configuration section
    now = datetime.datetime.now()
    print(now.strftime(Style.RESET_ALL + Style.DIM + "%H:%M:%S ") + Fore.YELLOW + "ⓘ　Downloading required PoT executable")

    url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
    r = requests.get(url)

    with open('PoT_b3_resources/PoT_executable.exe', 'wb') as f:
        f.write(r.content)


  if not Path("PoT_b3_resources/PoT_config.ini").is_file(): # Initial configuration section
    print(Style.RESET_ALL + Style.BRIGHT + "Initial configuration, you can edit 'PoT_b3_resources/PoT_config.ini' file later.")
    print(Style.RESET_ALL + "Don't have an account? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register.\n")

    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    config['pot'] = { # Format data
    "username": username,
    "password": password}
    
    with open("PoT_b3_resources/PoT_config.ini", "w") as configfile: # Write data to file
      config.write(configfile)

  else: # If config already exists, load from it
    config.read("PoT_b3_resources/PoT_config.ini")
    username = config["pot"]["username"]
    password = config["pot"]["password"]
    

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
        break # Continue
      else:
        time.sleep(0.025) # Restart if wrong status code
        
    except:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Cannot receive pool address and IP.\nExiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)
      
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
      break # If connection was established, continue
    
    except: # If it wasn't, display a message and exit
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Cannot connect to the server. It is probably under maintenance.\nRetrying in 15 seconds...")
      time.sleep(15)
      os._exit(1)
      
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
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.YELLOW + "✓ Connected to the Duino-Coin server (v"+str(SERVER_VER)+")")
    else:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Miner is outdated (v"+VER+"), server is on v"+SERVER_VER+" please download latest version from https://github.com/revoxhere/duino-coin/releases/\nExiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)
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
        soc.send(bytes("FROM," + "PoT_Miner," + str(pcusername) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send info to server about client

        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.YELLOW + "✓ Logged in successfully")

        break # If it was, continue
      
      if resp == "NO":
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Error! Wrong credentials, account doesn't exist or you are already connected!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")

        soc.close()
        time.sleep(15)
        os._exit(1) # If it wasn't, display a message and exit

    except:
      Connect() # Reconnect if pool down

    time.sleep(0.025) # Try again if no response


def Mine(): # "Mining" section
    global process, timer, reward, income
    try: # Start Magi Miner
        process = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.YELLOW + "✓ Proof of Time thread started")
    except:
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Fore.RED + "✗ Error while launching PoT executable!\nExiting in 15s.")
        time.sleep(15)
        os._exit(1)

    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "\n") + Fore.YELLOW + "ⓘ　Duino-Coin network is a completely free service and will always be. You can really help us maintain the server and low-fee payouts by donating - visit " + Fore.GREEN + "https://revoxhere.github.io/duino-coin/donate" + Fore.YELLOW + " to learn more.\n")

    while True:
        print("", end = Style.DIM + Fore.YELLOW + "\r⏲　Next reward in " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f"{timer:02}"  + Style.RESET_ALL + Style.DIM + Fore.YELLOW + " seconds " + Style.RESET_ALL + Style.DIM + "▰"*timer + " ")
        timer -= 1
        time.sleep(1)
        if timer <= 0: # Ask for reward every 45s; server won't allow faster submission
            income += reward
            income = round(float(income), 8)
            timer = 45 # Reset the timer
            soc.send(bytes("PoTr", encoding="utf8")) # Send Proof-of-Time-reward request
            now = datetime.datetime.now()
            print("", end=f"\r" + now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "» You've been rewarded • This session estimated income is " + str(income) + " DUCO\n")


while True:
  try:
    loadConfig() # Load configfile
  except:
    print(Style.BRIGHT + Fore.RED + "✗ There was an error loading the configfile. Try removing it and re-running configuration."  + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)

  try:
    Greeting() # Display greeting message
  except:
    print(Style.BRIGHT + Fore.RED + "✗ You somehow managed to break the greeting message!"  + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)
    
  try:
    Connect() # Connect to pool
  except:
    print(Style.BRIGHT + Fore.RED + "✗ There was an error connecting to pool. Check your configfile." + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)
    
  try:
    checkVersion() # Check version
  except:
    print(Style.BRIGHT + Fore.RED + "✗ There was an error checking version. Restarting." + Style.RESET_ALL)

  try:
    Login() # Login
  except:
    print(Style.BRIGHT + Fore.RED + "✗ There was an error while logging in. Restarting." + Style.RESET_ALL)

  try:
    Mine() # "Mine"
  except:
    print(Style.BRIGHT + Fore.RED + "✗ There was an error in PoT section. Restarting." + Style.RESET_ALL)

  print(Style.RESET_ALL)
  time.sleep(0.025) # Restart if error
