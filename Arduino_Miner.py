#!/usr/bin/env python3
##########################################
# Duino-Coin Arduino Miner (v1.6) 
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
import socket, statistics, threading, time, random, re, subprocess, hashlib, platform, getpass, configparser, sys, datetime, os # Import libraries
from pathlib import Path
from signal import signal, SIGINT

try: # Check if colorama is installed
  from colorama import init, Fore, Back, Style
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Colorama is not installed. Please install it using: python3 -m pip install colorama.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if requests is installed
  import requests
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Requests is not installed. Please install it using: python3 -m pip install requests.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try:
  import serial
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Pyserial is not installed. Please install it using: python3 -m pip install pyserial.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try:
  import serial.tools.list_ports
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Serial tools is not installed. Please install it using: python3 -m pip install serial.tools.list_ports.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

# Global variables
VER = "1.6" # Version number
timeout = 5 # Socket timeout
resources = "ArduinoMiner_"+str(VER)+"_resources"

shares = [0, 0]
diff = 0
donatorrunning = False
balance = 0
job = ""

res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
config = configparser.ConfigParser()
autorestart = 0
donationlevel = 0

pcusername = getpass.getuser() # Username
platform = str(platform.system()) + " " + str(platform.release()) # Platform information
publicip = requests.get("https://api.ipify.org").text # Public IP

try:
    os.mkdir(str(resources)) # Create resources folder if it doesn't exist
except:
    pass


def title(title):
  if os.name == 'nt':
    os.system("title "+title)
  else:
    print('\33]0;'+title+'\a', end='')
    sys.stdout.flush()
        
def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "\n%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " SIGINT detected - Exiting gracefully." + Style.NORMAL + " See you soon!")
  try:
    soc.send(bytes("CLOSE", encoding="utf8"))
  except:
    pass
  os._exit(0)

signal(SIGINT, handler) # Enable signal handler

def Greeting(): # Greeting message depending on time
  global greeting, message, autorestart, st, bytereturn, miningmethod
  print(Style.RESET_ALL)

  if float(autorestart) <= 0:
    autorestart = 0
    autorestartmessage = "disabled"
  if float(autorestart) > 0:
    autorestartmessage = "restarting every " + str(autorestart) + "s"
    
  current_hour = time.strptime(time.ctime(time.time())).tm_hour
  
  if current_hour < 12 :
    greeting = "We hope you're having a great morning"
  elif current_hour == 12 :
    greeting = "We hope you're having a great noon"
  elif current_hour > 12 and current_hour < 18 :
    greeting = "We hope you're having a great afternoon"
  elif current_hour >= 18 :
    greeting = "We hope you're having a great evening"
  else:
    greeting = "Welcome back"
  
  print(" * " + Fore.YELLOW + Style.BRIGHT + "Duino-Coin © Arduino Miner " + Style.RESET_ALL + Fore.YELLOW+ "(v" + str(VER) + ") 2019-2020") # Startup message  print(" * " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
  print(" * " + Fore.YELLOW + "AVR board on port: " + Style.BRIGHT + str(arduinoport))
  if os.name == 'nt':
    print(" * " + Fore.YELLOW + "Donation level: " +  Style.BRIGHT + str(donationlevel))
  print(" * " + Fore.YELLOW + "Algorithm: " + Style.BRIGHT + "DUCO-S1A")
  print(" * " + Fore.YELLOW + "Autorestarter: " + Style.BRIGHT + str(autorestartmessage))
  print(" * " + Fore.YELLOW + str(greeting) + ", " + Style.BRIGHT +  str(username) + "\n")
  
  if os.name == 'nt':
    if not Path(str(resources) + "/Miner_executable.exe").is_file(): # Initial miner executable section
      url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
      r = requests.get(url)
      with open(str(resources) + '/Miner_executable.exe', 'wb') as f:
        f.write(r.content)

def autorestarter(): # Autorestarter
  time.sleep(float(autorestart))

  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Restarting the miner")

  os.execl(sys.executable, sys.executable, *sys.argv)

def loadConfig(): # Config loading section
  global pool_address, pool_port, username, password, autorestart, donationlevel, arduinoport
  
  if not Path(str(resources) + "/Miner_config.cfg").is_file(): # Initial configuration section
    print(Style.BRIGHT + "Duino-Coin basic configuration tool.\nEdit "+str(resources) + "/Miner_config.cfg file later if you want to change it.")
    print(Style.RESET_ALL + "Don't have an Duino-Coin account yet? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register on server.\n")

    username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
    password = input(Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT)

    print(Style.RESET_ALL + Fore.YELLOW + "Configuration tool has found the following ports:")
    print(Style.RESET_ALL + Fore.YELLOW + "----")
    portlist = serial.tools.list_ports.comports()
    for port in portlist:
      print(Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "  " + str(port))
    print(Style.RESET_ALL + Fore.YELLOW + "----")
    print(Style.RESET_ALL + Fore.YELLOW + "If you can't see your board here, make sure the it is properly connected and the program has access to it (admin/sudo rights).")

    arduinoport = input(Style.RESET_ALL + Fore.YELLOW + "Enter your board serial port (e.g. COM1 or /dev/ttyUSB1): " + Style.BRIGHT)
    autorestart = input(Style.RESET_ALL + Fore.YELLOW + "Set after how many seconds miner will restart (recommended: 360): " + Style.BRIGHT)
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
    "password": password,
    "arduinoport": arduinoport,
    "autorestart": autorestart,
    "donate": donationlevel}
    
    with open(str(resources) + "/Miner_config.cfg", "w") as configfile: # Write data to file
      config.write(configfile)

  else: # If config already exists, load from it
    config.read(str(resources) + "/Miner_config.cfg")
    username = config["arduminer"]["username"]
    password = config["arduminer"]["password"]
    arduinoport = config["arduminer"]["arduinoport"]
    autorestart = config["arduminer"]["autorestart"]
    donationlevel = config["arduminer"]["donate"]

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
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Cannot receive pool address and IP.\nExiting in 15 seconds.")
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
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Cannot connect to the server. It is probably under maintenance or temporarily down.\nRetrying in 15 seconds.")
      time.sleep(15)
      os.execl(sys.executable, sys.executable, *sys.argv)
      
    Connect()  
    time.sleep(0.025)
    

def checkVersion():
  try:
    try:
      SERVER_VER = soc.recv(1024).decode() # Check server version
    except:
      Connect() # Reconnect if pool down

    if len(SERVER_VER) != 3:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Cannot connect to the server." + Style.RESET_ALL + Fore.RED + " It is probably under maintenance or temporarily down.\nRetrying in 15 seconds.")
      time.sleep(15)
      os.execl(sys.executable, sys.executable, *sys.argv)                     
      
    if float(SERVER_VER) <= float(VER) and len(SERVER_VER) == 3: # If miner is up-to-date, display a message and continue
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.YELLOW + " Connected" + Style.RESET_ALL + Fore.YELLOW + " to master Duino-Coin server (v"+str(SERVER_VER)+")")
    
    else:
      now = datetime.datetime.now()
      cont = input(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Miner is outdated (v"+VER+")," + Style.RESET_ALL + Fore.RED + " server is on v"+SERVER_VER+", please download latest version from https://github.com/revoxhere/duino-coin/releases/ or type \'continue\' if you wish to continue anyway.\n")
      if cont != "continue": 
        os._exit(1)
    
  except:
    Connect() # Reconnect if pool down

def ConnectToArduino():
  global com
  com = serial.Serial(arduinoport, 115200)

def Login():
  global autorestart
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
        soc.send(bytes("FROM," + "Arduino Miner," + str(username) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send metrics to server about client

        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.YELLOW + " Logged in successfully " + Style.RESET_ALL + Fore.YELLOW + "as " + str(username))

        soc.send(bytes("BALA", encoding="utf8")) # Get and round balance from the server
        balance = round(float(soc.recv(1024).decode()), 6)

        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Style.NORMAL + Fore.YELLOW + " Your account balance is " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + str(balance) + " DUCO")

        break # If it was, continue
      
      if resp == "NO":
        now = datetime.datetime.now()
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Error! Wrong credentials or account doesn't exist!" + Style.RESET_ALL + Fore.RED + "\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")

        soc.close()
        time.sleep(15)
        os._exit(1) # If it wasn't, display a message and exit
      else:
        os.execl(sys.executable, sys.executable, *sys.argv)

    except:
      os.execl(sys.executable, sys.executable, *sys.argv) # Reconnect if pool down

    time.sleep(0.025) # Try again if no response 

def ArduinoMine(): # Mining section
  global donationlevel, donatorrunning
  
  if os.name == 'nt':
    if int(donationlevel) > 0:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Thank You for being an awesome donator! <3")
    else:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Duino-Coin network is a completely free service and will always be." + Style.BRIGHT + Fore.YELLOW + "\n  You can help us maintain the server and low-fee payouts by donating.\n  Visit " + Style.RESET_ALL + Fore.GREEN + "https://revoxhere.github.io/duino-coin/donate" + Style.BRIGHT + Fore.YELLOW + " to learn more.")

    if not donatorrunning: # Check wheter donation was already started
      if int(donationlevel) == int(5):  # Check donationlevel and if it's more than 0 launch Magi Miner as donation
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 100 -s 4"
      if int(donationlevel) == int(4):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 70 -s 4"
      if int(donationlevel) == int(3):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 50 -s 4"
      if int(donationlevel) == int(2):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 30 -s 4"
      if int(donationlevel) == int(1):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 10 -s 4"
      if int(donationlevel) == int(0):
          cmd = ""
      try:  # Start cmd set above
        subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
        donatorrunning = True
      except:
        pass

  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Arduino mining thread started" + Style.RESET_ALL + Fore.YELLOW + " using DUCO-S1A algorithm, please wait until Arduino will create a stable connection with the miner")
  
  ready = com.readline().decode().rstrip().lstrip() # Arduino will send ready signal
  while True:
    com.write(bytes("start\n", encoding="utf8")) # hash

    soc.send(bytes("Job",encoding="utf8")) # Send job request to server
    job = soc.recv(1024).decode().split(",") # Split received job
    
    com.write(bytes(str(job[0])+"\n", encoding="utf8")) # hash
    time.sleep(0.025)
    com.write(bytes(str(job[1])+"\n", encoding="utf8")) # job
    time.sleep(0.025)
    com.write(bytes(str(job[2])+"\n", encoding="utf8")) # diff

    computestart = datetime.datetime.now() # Get timestamp of start of the computing
    result = com.readline().decode().rstrip().lstrip() # Send hash, job and difficulty to the board using serial
    soc.send(bytes(str(result), encoding="utf8")) # Send result of hashing algorithm to pool

    while True:
      feedback = soc.recv(1024).decode() # Get feedback
      time.sleep(0.025)
      if feedback == "GOOD": # If result was good
        now = datetime.datetime.now()
        computetime = now - computestart # Time from start of hash computing to finding the result
        computetime = str(int(computetime.microseconds / 1000)) # Convert to ms

        shares[0] = shares[0] + 1 # Share rejected = increment correct shares counter by 1
        title("Duino-Coin Arduino Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.GREEN + " Accepted " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(job[2]) + " • " + Style.BRIGHT + Fore.BLUE + computetime + "ms avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
        break # Repeat

      elif feedback == "BLOCK": # If result was good
        now = datetime.datetime.now()
        computetime = now - computestart # Time from start of hash computing to finding the result
        computetime = str(int(computetime.microseconds / 1000)) # Convert to ms

        shares[0] = shares[0] + 1 # Share rejected = increment correct shares counter by 1
        title("Duino-Coin Arduino Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.GREEN + " Block accepted ("+str(job[0])[:8]+") " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(job[2]) + " • " + Style.BRIGHT + Fore.BLUE + computetime + "ms avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
        break # Repeat

      elif feedback == "BAD": # If result was bad
        now = datetime.datetime.now()
        computetime = now - computestart # Time from start of hash computing to finding the result
        computetime = str(int(computetime.microseconds / 1000)) # Convert to ms
                                                                                                                       
        shares[1] = shares[1] + 1 # Share rejected = increment rejected shares counter by 1
        title("Duino-Coin Arduino Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " avr " + Back.RESET + Fore.RED + " Rejected " + Fore.YELLOW + str(shares[1]) + "/" + str(shares[1] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) "  + Style.NORMAL + Fore.WHITE + "• diff " + str(job[2]) + " • "  + Style.BRIGHT + Fore.BLUE + computetime + "ms avr time " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "(boo!!!)")
        break # Repeat


init(autoreset=True) # Enable colorama

while True:
  title("Duino-Coin Arduino Miner (v"+str(VER)+")")

  try:
    loadConfig() # Load configfile
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error loading the configfile. Try removing it and re-running configuration. Exiting in 15s."  + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)

  try: # Setup autorestarter
    if float(autorestart) > 0:
      threading.Thread(target=autorestarter).start()
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error in autorestarter. Check configuration file. Exiting in 15s." + Style.RESET_ALL)    
    time.sleep(15)
    os._exit(1)

  try:
    Greeting() # Display greeting message
  except:
    pass
  
  try:
    Connect() # Connect to pool
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while connecting to the server. Restarting in 15 seconds." + Style.RESET_ALL)
    time.sleep(15)
    os.execl(sys.executable, sys.executable, *sys.argv)
    
  try:
    checkVersion() # Check version
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while connecting to the server. Restarting in 15 seconds." + Style.RESET_ALL)
    time.sleep(15)
    os.execl(sys.executable, sys.executable, *sys.argv)

  try:
    Login() # Login
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while logging-in. Restarting." + Style.RESET_ALL)
    os.execl(sys.executable, sys.executable, *sys.argv)

  ConnectToArduino() # Connect to AVR board

  try:
    ArduinoMine()
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while mining. Restarting." + Style.RESET_ALL)
    os.execl(sys.executable, sys.executable, *sys.argv)

  print(Style.RESET_ALL + Style.RESET_ALL)
  time.sleep(0.025) # Restart
