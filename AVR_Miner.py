#!/usr/bin/env python3
##########################################
# Duino-Coin AVR Miner (v1.8)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
import socket, threading, time, re, subprocess, platform, configparser, sys, datetime, os # Import libraries
from pathlib import Path
from signal import signal, SIGINT

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try: # Check if colorama is installed
  from colorama import init, Fore, Back, Style
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Colorama is not installed. Miner will try to install it. If it fails, please install it using: python3 -m pip install colorama.")
  install("colorama")
  os.execl(sys.executable, sys.executable, *sys.argv)

try: # Check if requests is installed
  import requests
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Requests is not installed. Miner will try to install it. If it fails, please install it using: python3 -m pip install requests.")
  install("requests")
  os.execl(sys.executable, sys.executable, *sys.argv)

try:
  import serial
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Pyserial is not installed. Miner will try to install it. If it fails, please install it using: python3 -m pip install pyserial.")
  install("pyserial")
  os.execl(sys.executable, sys.executable, *sys.argv)

try:
  import serial.tools.list_ports
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Serial tools is not installed. Please install it using: pip install -r requirements.txt.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

# Global variables
minerVersion = "1.8" # Version number
timeout = 5 # Socket timeout
resources = "AVRMiner_"+str(minerVersion)+"_resources"
shares = [0, 0]
diff = 0
donatorrunning = False
balance = 0
job = ""
debug = False
platform = str(platform.system()) + " " + str(platform.release()) # Platform information
serveripfile = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
config = configparser.ConfigParser()
autorestart = 0
donationlevel = 0

try:
    os.mkdir(str(resources)) # Create resources folder if it doesn't exist
except:
    pass

def debugOutput(text):
  if debug == "True":
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "%H:%M:%S.%f ") + "DEBUG: " + text)

def title(title):
  if os.name == 'nt':
    os.system("title "+title)
  else:
    print('\33]0;'+title+'\a', end='')
    sys.stdout.flush()

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "\n%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " SIGINT detected - Exiting gracefully." + Style.NORMAL + Fore.WHITE + " See you soon!")
  try:
    soc.send(bytes("CLOSE", encoding="utf8")) # Try sending a close connection request to the server
  except:
    if debug == "True": raise
  os._exit(0)

signal(SIGINT, handler) # Enable signal handler

def Greeting(): # Greeting message depending on time
  global greeting, autorestart
  print(Style.RESET_ALL)

  if float(autorestart) <= 0:
    autorestart = 0
    autorestartmessage = "disabled"
  if float(autorestart) > 0:
    autorestartmessage = "every " + str(autorestart) + " minutes"
    
  current_hour = time.strptime(time.ctime(time.time())).tm_hour
  
  if current_hour < 12 :
    greeting = "Have a wonderful morning"
  elif current_hour == 12 :
    greeting = "Have a tasty noon"
  elif current_hour > 12 and current_hour < 18 :
    greeting = "Have a peaceful afternoon"
  elif current_hour >= 18 :
    greeting = "Have a cozy evening"
  else:
    greeting = "Welcome back"
  
  print(" > " + Fore.YELLOW + Style.BRIGHT + "Official Duino-Coin © AVR Miner" + Style.RESET_ALL + Fore.WHITE + " (v" + str(minerVersion) + ") 2019-2020") # Startup message  print(" * " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
  print(" > " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
  print(" > " + Fore.WHITE + "AVR board on port: " + Style.BRIGHT + Fore.YELLOW + str(avrport))
  if os.name == 'nt':
    print(" > " + Fore.WHITE + "Donation level: " +  Style.BRIGHT + Fore.YELLOW + str(donationlevel))
  print(" > " + Fore.WHITE + "Algorithm: " + Style.BRIGHT + Fore.YELLOW + "DUCO-S1A")
  print(" > " + Fore.WHITE + "Autorestarter: " + Style.BRIGHT + Fore.YELLOW + str(autorestartmessage))
  print(" > " + Fore.WHITE + str(greeting) + ", " + Style.BRIGHT + Fore.YELLOW + str(username) + "!\n")
  
  if os.name == 'nt':
    if not Path(str(resources) + "/Donate_executable.exe").is_file(): # Initial miner executable section
      debugOutput("OS is Windows, downloading developer donation executable")
      url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
      r = requests.get(url)
      with open(str(resources) + '/Donate_executable.exe', 'wb') as f:
        f.write(r.content)

def autorestarter(): # Autorestarter
  time.sleep(float(autorestart)*60)

  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Restarting the miner")

  os.execl(sys.executable, sys.executable, *sys.argv)

def loadConfig(): # Config loading section
  global pool_address, pool_port, username, autorestart, donationlevel, avrport, debug
  
  if not Path(str(resources) + "/Miner_config.cfg").is_file(): # Initial configuration section
    print(Style.BRIGHT + "Duino-Coin basic configuration tool\nEdit "+str(resources) + "/Miner_config.cfg file later if you want to change it.")
    print(Style.RESET_ALL + "Don't have an Duino-Coin account yet? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register on server.\n")

    username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)

    print(Style.RESET_ALL + Fore.YELLOW + "Configuration tool has found the following ports:")
    print(Style.RESET_ALL + Fore.YELLOW + "----")
    portlist = serial.tools.list_ports.comports()
    for port in portlist:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "  " + str(port))
    print(Style.RESET_ALL + Fore.YELLOW + "----")
    print(Style.RESET_ALL + Fore.YELLOW + "If you can't see your board here, make sure the it is properly connected and the program has access to it (admin/sudo rights).")

    avrport = input(Style.RESET_ALL + Fore.YELLOW + "Enter your board serial port (e.g. COM1 or /dev/ttyUSB1): " + Style.BRIGHT)
    autorestart = input(Style.RESET_ALL + Fore.YELLOW + "If you want, set after how many minutes miner will restart (recommended: 30): " + Style.BRIGHT)
    donationlevel = "0"
    if os.name == 'nt':
      donationlevel = input(Style.RESET_ALL + Fore.YELLOW + "Set developer donation level (0-5) (recommended: 1), this will not reduce your earnings: " + Style.BRIGHT)

    donationlevel = re.sub("\D", "", donationlevel)  # Check wheter donationlevel is correct
    if float(donationlevel) > int(5):
      donationlevel = 5
    if float(donationlevel) < int(0):
      donationlevel = 0

    config['arduminer'] = { # Format data
    "username": username,
    "avrport": avrport,
    "autorestart": autorestart,
    "donate": donationlevel,
    "debug": False}
    
    with open(str(resources) + "/Miner_config.cfg", "w") as configfile: # Write data to file
      config.write(configfile)
    print(Style.RESET_ALL + "Config saved! Launching...")

  else: # If config already exists, load from it
    config.read(str(resources) + "/Miner_config.cfg")
    username = config["arduminer"]["username"]
    avrport = config["arduminer"]["avrport"]
    autorestart = config["arduminer"]["autorestart"]
    donationlevel = config["arduminer"]["donate"]
    debug = config["arduminer"]["debug"]

def Connect(): # Connect to pool section
  global soc, pool_address, pool_port
  
  res = requests.get(serveripfile, data = None) #Use request to grab data from raw github file
  if res.status_code == 200: #Check for response
    content = res.content.decode().splitlines() #Read content and split into lines
    pool_address = content[0] #Line 1 = pool address
    pool_port = content[1] #Line 2 = pool port
    debugOutput("Retrieved pool IP: " + pool_address + ":" + str(pool_port))

  try: # Shutdown previous connections if any
    soc.shutdown(socket.SHUT_RDWR)
    soc.close()
  except:
    debugOutput("No previous connections to close")

  try: # Try to connect
    soc = socket.socket()
    soc.connect((str(pool_address), int(pool_port)))
    soc.settimeout(timeout)
  except: # If it wasn't, display a message
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Connection error! Retrying in 15s.")
    if debug == "True": raise
    time.sleep(15)
    Connect()

def checkVersion():
  serverVersion = soc.recv(1024).decode() # Check server version
  debugOutput("Server version: " + serverVersion)
  if float(serverVersion) <= float(minerVersion) and len(serverVersion) == 3: # If miner is up-to-date, display a message and continue
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.YELLOW + " Connected" + Style.RESET_ALL + Fore.WHITE + " to master Duino-Coin server (v"+str(serverVersion)+")")
  else:
    now = datetime.datetime.now()
    cont = input(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Miner is outdated (v"+minerVersion+")," + Style.RESET_ALL + Fore.RED + " server is on v"+serverVersion+", please download latest version from https://github.com/revoxhere/duino-coin/releases/ or type \'continue\' if you wish to continue anyway.\n")
    if cont != "continue":
      os._exit(1)

def ConnectToAVR():
  global com
  try:
    com = serial.Serial(avrport, 115200, timeout=5)
  except:
    if debug == "True": raise
    Connect()

def AVRMine(): # Mining section
  global donationlevel, donatorrunning
  if os.name == 'nt' and donatorrunning == False:
    cmd = str(resources) + "/Donate_executable.exe -o stratum+tcp://xmg.minerclaim.net:3333 -o revox.donate -p x -e "
    if int(donationlevel) == 5: cmd += "100"
    elif int(donationlevel) == 4: cmd += "75"
    elif int(donationlevel) == 3: cmd += "50"
    elif int(donationlevel) == 2: cmd += "25"
    elif int(donationlevel) == 1: cmd += "10"
    if int(donationlevel) > 0: # Launch CMD as subprocess
      debugOutput("Starting donation process")
      donatorrunning = True
      subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL)
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Thank You for being an awesome donator! <3")
    else:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Duino-Coin network is a completely free service and will always be." + Style.BRIGHT + Fore.YELLOW + "\n  You can help us maintain the server and low-fee payouts by donating.\n  Visit " + Style.RESET_ALL + Fore.GREEN + "https://duinocoin.com/donate" + Style.BRIGHT + Fore.YELLOW + " to learn more.")
  
  try:
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " AVR mining thread is starting" + Style.RESET_ALL + Fore.WHITE + " using DUCO-S1A algorithm, please wait...")
    debugOutput("Sending start word")
    ready = com.readline().decode().rstrip().lstrip() # AVR will send ready signal
    debugOutput("Received start word ("+str(ready)+")")
  except:
    if debug == "True": raise
    Connect()

  while True:
    while True:
      try:
        soc.send(bytes("JOB,"+str(username)+",AVR",encoding="utf8")) # Send job request
        job = soc.recv(1024).decode() # Get work from pool
        job = job.split(",") # Split received data to job and difficulty
        diff = job[2]
        if job[0] and job[1] and job[2]:
          debugOutput("Job received: " +str(job))
          break # If job received, continue 
      except:
        if debug == "True": raise
        Connect()
    try:
      com.write(bytes("start\n", encoding="utf8")) # start
      debugOutput("Written start word")
      com.write(bytes(str(job[0])+"\n", encoding="utf8")) # hash
      debugOutput("Written hash")
      com.write(bytes(str(job[1])+"\n", encoding="utf8")) # job
      debugOutput("Written job")
      com.write(bytes(str(job[2])+"\n", encoding="utf8")) # diff
      debugOutput("Written diff")
      result = com.readline().decode().rstrip().lstrip() # Send hash, job and difficulty to the board using serial
      result = result.split(",")
      debugOutput("Received result ("+str(result[0])+")")
      debugOutput("Received time ("+str(result[1])+")")
      soc.send(bytes(str(result[0])+",150,Official AVR Miner v"+str(minerVersion), encoding="utf8")) # Send result back to the server
    except:
      if debug == "True": raise
      Connect()

    while True:
      try:
        feedback = soc.recv(1024).decode() # Get feedback
      except socket.timeout:
        if debug == "True": raise
        Connect()
      now = datetime.datetime.now()
      computetime = str(round(int(result[1]) / 1000000, 2)) # Convert to s

      if feedback == "GOOD": # If result was good
        shares[0] = shares[0] + 1 # Share accepted  = increment correct shares counter by 1
        title("Duino-Coin AVR Miner (v"+str(minerVersion)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.GREEN + " Accepted " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(job[2]) + " • " + Style.BRIGHT + Fore.BLUE + computetime + "s avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "(yay!)")
        break # Repeat

      elif feedback == "BLOCK": # If result was good
        shares[0] = shares[0] + 1 # Share rejected = increment incorrect shares counter by 1
        title("Duino-Coin AVR Miner (v"+str(minerVersion)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.GREEN + " Block accepted ("+str(job[0])[:8]+") " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(job[2]) + " • " + Style.BRIGHT + Fore.BLUE + computetime + "s avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
        break # Repeat

      elif feedback == "INVU": # If user doesn't exist 
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " User "+str(username)+" doesn't exist." + Style.RESET_ALL + Fore.RED + " Make sure you've entered the username correctly. Please check your config file. Exiting in 15s.")
        time.sleep(15)
        os._exit(1)

      elif feedback == "ERR": # If server says that it encountered an error
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Internal server error." + Style.RESET_ALL + Fore.RED + " Retrying in 15s.")
        time.sleep(15)
        Connect()

      else: # If result was bad
        shares[1] += 1 # Share rejected = increment bad shares counter by 1
        title("Duino-Coin Python Miner (v"+str(minerVersion)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.RED + " Rejected " + Fore.YELLOW + str(shares[1]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(diff) + " • " + Style.BRIGHT + Fore.BLUE + computetime + "s avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "(boo!) ")
        break # Repeat

if __name__ == '__main__':
  init(autoreset=True) # Enable colorama
  title("Duino-Coin AVR Miner (v"+str(minerVersion)+")")
  try:
    loadConfig() # Load configfile
    debugOutput("Config file loaded")
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error loading the configfile (Miner_config.cfg). Try removing it and re-running configuration. Exiting in 15s."  + Style.RESET_ALL)
    if debug == "True": raise
    time.sleep(15)
    os._exit(1)
  try:
    Greeting() # Display greeting message
    debugOutput("Greeting displayed")
  except:
    if debug == "True": raise

  while True:
    try: # Setup autorestarter
      if float(autorestart) > 0:
        debugOutput("Enabled autorestarter for " + str(autorestart) + " minutes")
        threading.Thread(target=autorestarter).start()
      else:
        debugOutput("Autorestarted is disabled")
    except:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error in autorestarter. Check configuration file (Miner_config.cfg). Exiting in 15s." + Style.RESET_ALL)
      if debug == "True": raise
      time.sleep(15)
      os._exit(1)

    try:
      Connect() # Connect to pool
      debugOutput("Connected to master server")
    except:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error connecting to the server. Retrying in 15s." + Style.RESET_ALL)
      if debug == "True": raise
      time.sleep(15)
      Connect()

    try:
      checkVersion() # Check version
      debugOutput("Version check complete")
    except:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error checking server version. Restarting." + Style.RESET_ALL)
      if debug == "True": raise
      Connect()

    try:
      ConnectToAVR() # Connect to AVR board
      debugOutput("Connected to AVR board")
    except:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error connecting to AVR board. Restarting." + Style.RESET_ALL)
      if debug == "True": raise
      Connect()

    try:
      debugOutput("Mining started")
      AVRMine() # Launch mining thread
      debugOutput("Mining ended")
    except:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while mining. Restarting." + Style.RESET_ALL)
      if debug == "True": raise
      Connect()
    time.sleep(0.025) # Restart
    debugOutput("Restarting")
