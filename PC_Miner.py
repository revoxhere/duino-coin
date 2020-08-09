#!/usr/bin/env python3
##########################################
# Duino-Coin PC Miner (v1.6) 
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © revox, MrKris7100 2020
##########################################
import socket, statistics, threading, time, random, re, subprocess, hashlib, platform, getpass, configparser, sys, datetime, os, signal # Import libraries
from pathlib import Path
from signal import signal, SIGINT

try: # Check if cpuinfo is installed
  import cpuinfo
  from multiprocessing import freeze_support
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Cpuinfo is not installed. Please install it using: python3 -m pip install py-cpuinfo.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if colorama is installed
  from colorama import init, Fore, Back, Style
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Colorama is not installed. Please install it using: python3 -m pip install colorama.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

try: # Check if requests is installed
  import requests
except:
  now = datetime.datetime.now()
  print(now.strftime("%H:%M:%S ") + "Requests is not installed. Please install it using: python3 -m pip install requests.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
  time.sleep(15)
  os._exit(1)

# Global variables
VER = "1.6" # Version number
timeout = 1 # Socket timeout
resources = "PCMiner_"+str(VER)+"_resources"

shares = [0, 0]
diff = 0
last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []
st = "A1"
donatorrunning = False
bytereturn = 0
balance = 0

res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
config = configparser.ConfigParser()
autorestart = 0
donationlevel = 0

pcusername = getpass.getuser() # Username
platform = str(platform.system()) + " " + str(platform.release()) # Platform information
publicip = requests.get("https://api.ipify.org").text # Public IP
freeze_support() # If not used, pyinstaller hangs when checking cpuinfo
cpu = cpuinfo.get_cpu_info() # Processor info

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
  global greeting, message, autorestart, st, bytereturn
  print(Style.RESET_ALL)

  if float(autorestart) <= 0:
    autorestart = 0
    autorestartmessage = "disabled"
  if float(autorestart) > 0:
    autorestartmessage = "restarting every " + str(autorestart) + "s"

  miningmethodlabel = "DUCO-S1"
    
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
  
  print(" * " + Fore.YELLOW + Style.BRIGHT + "Duino-Coin © Single-threaded PC Miner " + Style.RESET_ALL + Fore.YELLOW+ "(v" + str(VER) + ") 2019-2020") # Startup message
  print(" * " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
  try:
    print(" * " + Fore.YELLOW + "CPU: " + Style.BRIGHT + str(cpu["brand_raw"]))
  except:
    pass
  if os.name == 'nt':
    print(" * " + Fore.YELLOW + "Donation level: " +  Style.BRIGHT + str(donationlevel))
  print(" * " + Fore.YELLOW + "Algorithm: " + Style.BRIGHT + str(miningmethodlabel))
  print(" * " + Fore.YELLOW + "Autorestarter: " + Style.BRIGHT + str(autorestartmessage))
  print(" * " + Fore.YELLOW + str(greeting) + ", " + Style.BRIGHT +  str(username) + "\n")
  
  if os.name == 'nt':
    if not Path(str(resources) + "/Miner_executable.exe").is_file(): # Initial miner executable section
      url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
      r = requests.get(url)
      with open(str(resources) + '/Miner_executable.exe', 'wb') as f:
        f.write(r.content)

def hashrateCalculator(): # Hashes/sec calculation
  global last_hash_count, hash_count, khash_count, hash_mean
  
  last_hash_count = hash_count
  khash_count = last_hash_count / 1000
  if khash_count == 0:
    khash_count = random.uniform(0, 1)
    
  hash_mean.append(khash_count) # Calculate average hashrate
  khash_count = statistics.mean(hash_mean)
  khash_count = round(khash_count, 2)
  
  hash_count = 0 # Reset counter
  
  threading.Timer(1.0, hashrateCalculator).start() # Run this def every 1s

def autorestarter(): # Autorestarter
  time.sleep(float(autorestart))

  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Restarting the miner")

  os.execl(sys.executable, sys.executable, *sys.argv)


def loadConfig(): # Config loading section
  global pool_address, pool_port, username, efficiency, autorestart, donationlevel, st, bytereturn, temp_print_time
  
  if not Path(str(resources) + "/Miner_config.cfg").is_file(): # Initial configuration section
    print(Style.BRIGHT + "Duino-Coin basic configuration tool.\nEdit "+str(resources) + "/Miner_config.cfg file later if you want to change it.")
    print(Style.RESET_ALL + "Don't have an Duino-Coin account yet? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register on server.\n")

    username = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
    efficiency = input(Style.RESET_ALL + Fore.YELLOW + "Set mining intensity (1-100)% (recommended: 100): " + Style.BRIGHT)
    autorestart = input(Style.RESET_ALL + Fore.YELLOW + "Set after how many seconds miner will restart (recommended: 600): " + Style.BRIGHT)
    donationlevel = "0"
    if os.name == 'nt':
      donationlevel = input(Style.RESET_ALL + Fore.YELLOW + "Set developer donation level (0-5) (recommended: 1), this will not reduce your earnings: " + Style.BRIGHT)
    
    efficiency = re.sub("\D", "", efficiency)  # Check wheter efficiency is correct
    if float(efficiency) > int(100):
      efficiency = 100
    if float(efficiency) < int(1):
      efficiency = 1

    donationlevel = re.sub("\D", "", donationlevel)  # Check wheter donationlevel is correct
    if float(donationlevel) > int(5):
      donationlevel = 5
    if float(donationlevel) < int(0):
      donationlevel = 0
      
    config['miner'] = { # Format data
    "username": username,
    "efficiency": efficiency,
    "autorestart": autorestart,
    "donate": donationlevel,
    "st": "A1",
    "bytereturn": "0"}
    
    with open(str(resources) + "/Miner_config.cfg", "w") as configfile: # Write data to file
      config.write(configfile)
    print(Style.RESET_ALL + "Config saved! Launching...")

  else: # If config already exists, load from it
    config.read(str(resources) + "/Miner_config.cfg")
    username = config["miner"]["username"]
    efficiency = config["miner"]["efficiency"]
    autorestart = config["miner"]["autorestart"]
    donationlevel = config["miner"]["donate"]
    st = config["miner"]["st"]
    bytereturn = config["miner"]["bytereturn"]

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
    
    except: # If it wasn't, display a message
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " Cannot connect to the server. It is probably under maintenance or temporarily down.\nRetrying in 15 seconds.")
      time.sleep(15)
      os.execl(sys.executable, sys.executable, *sys.argv)
      
    Connect()  

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
      soc.send(bytes("FROM," + "PC Miner," + str(username) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send metrics to server about client
    
    else:
      now = datetime.datetime.now()
      cont = input(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Miner is outdated (v"+VER+")," + Style.RESET_ALL + Fore.RED + " server is on v"+SERVER_VER+", please download latest version from https://github.com/revoxhere/duino-coin/releases/ or type \'continue\' if you wish to continue anyway.\n")
      if cont != "continue": 
        os._exit(1)
    
  except:
    Connect() # Reconnect if pool down

def Mine(): # Mining section
  global last_hash_count, hash_count, khash_count, donationlevel, donatorrunning, efficiency

  if os.name == 'nt':
    if int(donationlevel) > 0:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.RED + " Thank You for being an awesome donator! <3")
    else:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Duino-Coin network is a completely free service and will always be." + Style.BRIGHT + Fore.YELLOW + "\n  You can help us maintain the server and low-fee payouts by donating.\n  Visit " + Style.RESET_ALL + Fore.GREEN + "https://revoxhere.github.io/duino-coin/donate" + Style.BRIGHT + Fore.YELLOW + " to learn more.")

    if not donatorrunning: # Check wheter donation was already started
      if int(donationlevel) == int(5):  # Check donationlevel and if it's more than 0 launch Magi Miner as donation
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_pcminer -p x -e 100 -s 4"
      if int(donationlevel) == int(4):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_pcminer -p x -e 70 -s 4"
      if int(donationlevel) == int(3):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_pcminer -p x -e 50 -s 4"
      if int(donationlevel) == int(2):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_pcminer -p x -e 30 -s 4"
      if int(donationlevel) == int(1):
          cmd = "cd " + str(resources) + " & Miner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_pcminer -p x -e 10 -s 4"
      if int(donationlevel) == int(0):
          cmd = ""
      try:  # Start cmd set above
        subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
        donatorrunning = True
      except:
        pass

  efficiency = 100 - float(efficiency) # Calulate efficiency
  efficiency = efficiency * 0.01

  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.GREEN + Fore.WHITE + " sys " + Back.RESET + Fore.YELLOW + " Mining thread started" + Style.RESET_ALL + Fore.YELLOW + " using DUCO-S1 algorithm")
  
  while True:
    time.sleep(float(efficiency)) # Sleep to achieve lower efficiency
    try:
      soc.send(bytes("JOB," + str(username), encoding="utf8")) # Send job request
    except:
      Connect() # Reconnect if pool down
    while True:
      try:
        job = soc.recv(1024).decode() # Get work from pool
      except:
        os.execl(sys.executable, sys.executable, *sys.argv)
      if job:
        break # If job received, continue to hashing algo
      time.sleep(0.025) # Try again if no response
    try:
      job = job.split(",") # Split received data to job and difficulty
      diff = job[2]
    except:
      os.execl(sys.executable, sys.executable, *sys.argv)
    
    computestart = datetime.datetime.now()
    for iJob in range(100 * int(job[2]) + 1): # Calculate hash with difficulty
      ducos1 = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest() # Generate hash
      hash_count = hash_count + 1 # Increment hash counter
      
      if job[1] == ducos1: # If result is even with job, send the result
        computestop = datetime.datetime.now()
        try:
          soc.send(bytes(str(iJob) + "," + str(last_hash_count) + "," + str(st) + "," + str(bytereturn), encoding="utf8")) # Send result of hashing algorithm to pool
        except:
          os.execl(sys.executable, sys.executable, *sys.argv) # Reconnect if pool down
          
        while True:
          try:
            feedback = soc.recv(1024).decode() # Get feedback
          except:
            os.execl(sys.executable, sys.executable, *sys.argv) # Reconnect if pool down
          if feedback == "GOOD": # If result was good
            now = datetime.datetime.now()
            computetime = computestop - computestart # Time from start of hash computing to finding the result
            computetime = str(int(computetime.microseconds / 1000)) # Convert to ms

            shares[0] = shares[0] + 1 # Share accepted = increment feedback shares counter by 1
            title("Duino-Coin PC Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
            print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " cpu " + Back.RESET + Fore.GREEN + " Accepted " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(diff) + " • " + Style.BRIGHT + Fore.WHITE + str(khash_count) + " kH/s " + Style.BRIGHT + Fore.YELLOW + "(yay!!!) " + Style.DIM + Fore.BLUE + "[" + computetime + "ms]")
            break # Repeat

          elif feedback == "BLOCK": # If big block was found
            now = datetime.datetime.now()
            computetime = now - computestart # Time from start of hash computing to finding the result
            computetime = str(int(computetime.microseconds / 1000)) # Convert to ms

            shares[0] = shares[0] + 1 # Share accepted = increment feedback shares counter by 1
            title("Duino-Coin PC Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
            print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " cpu " + Back.RESET + Fore.GREEN + " Block accepted ("+str(job[0])[:8]+") " + Fore.YELLOW + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(diff) + " • " + Style.BRIGHT + Fore.WHITE + str(khash_count) + " kH/s " + Style.BRIGHT + Fore.YELLOW + "(yay!!!) " + Style.DIM + Fore.BLUE + "[" + computetime + "ms]")
            break # Repeat

          elif feedback == "BAD": # If result was bad
            now = datetime.datetime.now()
            computetime = now - computestart # Time from start of hash computing to finding the result
            computetime = str(int(computetime.microseconds / 1000)) # Convert to ms
            
            shares[1] = shares[1] + 1 # Share rejected = increment bad shares counter by 1
            title("Duino-Coin PC Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
            print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + " cpu " + Back.RESET + Fore.RED + " Rejected " + Fore.YELLOW + str(shares[1]) + "/" + str(shares[1] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff " + str(diff) + " • " + Style.BRIGHT + Fore.WHITE + str(khash_count) + " kH/s "  + Style.BRIGHT + Fore.RED + "(boo!!!) " + Style.DIM + Fore.BLUE + "[" + computetime + "ms]")
            break # Repeat

          elif feedback == "INVU": # If this user doesn't exist server will forward earnings to developer account
            now = datetime.datetime.now()
            print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.BLUE + Fore.WHITE + " net " + Back.RESET + Fore.RED + " User "+str(username)+" doesn't exist." + Style.RESET_ALL + Fore.RED + " Make sure you've entered the username correctly. Please check your config file. Exiting in 15s.")
            time.sleep(15)
            os._exit(1)
        break # Repeat

init(autoreset=True) # Enable colorama
hashrateCalculator() # Start hashrate calculator

while True:
  title("Duino-Coin PC Miner (v"+str(VER)+")")

  try:
    loadConfig() # Load configfile
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error loading the config file (Miner_config.cfg). Try removing it and re-running configuration. Exiting in 15s."  + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)

  try: # Setup autorestarter
    if float(autorestart) > 0:
      threading.Thread(target=autorestarter).start()
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error in while autorestarting. Check configuration file (Miner_config.cfg). Exiting in 15s." + Style.RESET_ALL)    
    time.sleep(15)
    os._exit(1)

  try:
    Greeting() # Display greeting message
  except:
    pass

  try:
    Connect() # Connect to pool
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error connecting to pool. Check your config file (Miner_config.cfg). Exiting in 15s." + Style.RESET_ALL)
    time.sleep(15)
    os._exit(1)

  try:
    checkVersion() # Check version
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error checking server version. Restarting." + Style.RESET_ALL)
    os.execl(sys.executable, sys.executable, *sys.argv)

  try:
    Mine() # Launch mining thread
  except:
    print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + " There was an error while mining. Restarting." + Style.RESET_ALL)
    os.execl(sys.executable, sys.executable, *sys.argv)

  print(Style.RESET_ALL + Style.RESET_ALL)
  time.sleep(0.025) # Restart
