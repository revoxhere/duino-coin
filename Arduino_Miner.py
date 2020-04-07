#!/usr/bin/env python3
###################################################
# Duino-Coin Arduino Miner (v1.337) © revox 2020
# https://github.com/revoxhere/duino-coin 
###################################################
import socket, subprocess, statistics, re, threading, time, random, configparser, getpass, sys, os, hashlib, datetime, signal, platform
from pathlib import Path
from signal import signal, SIGINT

try:
    import requests
except:
    print("✗ Requests is not installed. Please install it with pip install requests")
    time.sleep(15)
    os._exit(0)

try:
    from colorama import init, Fore, Back, Style
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + "✗ Colorama is not installed. Please install it using: python3 -m pip install colorama.\nIf you can't install it, use Minimal-PC_Miner.\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

try:
    import serial
except:
    print("✗ pySerial is not installed. Please install it with pip install pyserial")
    time.sleep(15)
    os._exit(0)

try:
    import serial.tools.list_ports
except:
    print("✗ Serial.tools.list_ports is not installed. Please install it with pip install serial.tools.list_ports")
    time.sleep(15)
    os._exit(0)

# Global variables
VER = 1.337 # Version number
timeout = 5 # Socket timeout
resources = "ArduinoMiner_"+str(VER)+"_resources"
init(autoreset=True) # Enable colorama

shares = [0, 0]
diff = 0
last_hash_count = 0
khash_count = 0
hash_count = 0
Ardu = True
hash_mean = []

res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
config = configparser.ConfigParser()

pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
cmd = "cd "+str(resources)+" & ArduinoMiner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 10 -s 4" # Miner command
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP

try:
    os.mkdir(str(resources))
except:
    pass

def title(title):
  if os.name == 'nt':
    os.system("title "+title)
  else:
    print('\33]0;'+title+'\a', end='')
    sys.stdout.flush()

title("Duino-Coin PC Miner (v"+str(VER)+")")

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
    now = datetime.datetime.now()
    print(now.strftime(Style.DIM + "\n%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "✓" + Style.RESET_ALL + Fore.YELLOW + " SIGINT detected - Exiting gracefully." + Style.BRIGHT + Fore.YELLOW +  " See you soon!")
    try:
        soc.send(bytes("CLOSE", encoding="utf8"))
    except:
        pass
    os._exit(0)

signal(SIGINT, handler) # Enable signal handler

if not Path(str(resources)+"/Arduino_config.ini").is_file():
 print(Style.BRIGHT + "Duino-Coin basic configuration tool. Edit "+str(resources) + "/Miner_config.ini file later if you want to change it.")
 print(Style.RESET_ALL + "Don't have an Duino-Coin account yet? Use " + Fore.YELLOW + "Wallet" + Fore.WHITE + " to register on server.\n")
 print(Style.RESET_ALL + "Scanning ports...")
 W = serial.tools.list_ports.comports()
 devices=[]
 for i in W:
  devices.append(i.device)
 devices = str(devices).replace('[', '')
 devices = str(devices).replace(']', '')
 devices = str(devices).replace('\'', '')
 print(Style.RESET_ALL + Fore.YELLOW + "Found ports: " + Style.BRIGHT + str(devices))
 y = input(Style.RESET_ALL + Fore.YELLOW + "Enter your Arduino port (e.g: COM8 or /dev/ttyUSB0): " + Style.BRIGHT)
 M = input(Style.RESET_ALL + Fore.YELLOW + "Enter your username: " + Style.BRIGHT)
 l = input(Style.RESET_ALL + Fore.YELLOW + "Enter your password: " + Style.BRIGHT)
 autorestart = input(Style.RESET_ALL + Fore.YELLOW + "Set after how many seconds miner will restart (0 = disable autorestarter): " + Style.BRIGHT)
 donationlevel = input(Style.RESET_ALL + Fore.YELLOW + "Set donation level (0-5): " + Style.BRIGHT)

 donationlevel = re.sub("\D", "", donationlevel)  # Check wheter donationlevel is correct
 if float(donationlevel) > int(5):
   donationlevel = 5
 if float(donationlevel) < int(0):
   donationlevel = 0

 config['arduinominer']={
    "arduino":str(y),
    "username":str(M),
    "password":str(l),
    "autorestart": autorestart,
    "donate": donationlevel}
 
 with open(str(resources)+"/Arduino_config.ini","w") as configfile:
  config.write(configfile)
  
else:
 config.read(str(resources)+"/Arduino_config.ini")
 y = config["arduinominer"]["arduino"]
 M = config["arduinominer"]["username"]
 l = config["arduinominer"]["password"]
 autorestart = config["arduinominer"]["autorestart"]
 donationlevel = config["arduinominer"]["donate"]

if float(autorestart) <= 0:
    autorestart = 0
    autorestartmessage = "disabled"
if float(autorestart) > 0:
    autorestartmessage = "restarting every " + str(autorestart) + "s"

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
    greeting = "Welcome back"

print(" * " + Fore.YELLOW + Style.BRIGHT + "Duino-Coin © Arduino Miner " + Style.RESET_ALL + Fore.YELLOW + "(v" + str(VER) + ") 2019-2020") # Startup message
time.sleep(0.15)
print(" * " + Fore.YELLOW + "https://github.com/revoxhere/duino-coin")
time.sleep(0.15)
print(" * " + Fore.YELLOW + "Board on port: " + Style.BRIGHT + str(y))
time.sleep(0.15)
print(" * " + Fore.YELLOW + "Donation level: " +  Style.BRIGHT + str(donationlevel))
time.sleep(0.15)
print(" * " + Fore.YELLOW + "Autorestarter: " + Style.BRIGHT + str(autorestartmessage))
time.sleep(0.15)
print(" * " + Fore.YELLOW + str(greeting) + ", " + Style.BRIGHT +  str(M) + "\n")

if not Path(str(resources) + "/Miner_executable.exe").is_file(): # Initial miner executable section
    url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
    r = requests.get(url)
    with open(str(resources) + '/Miner_executable.exe', 'wb') as f:
      f.write(r.content)

def restart(): # Hashes/sec calculation
  time.sleep(float(autorestart))
  print(Style.BRIGHT + "ⓘ　Restarting the miner")
  os.execl(sys.executable, sys.executable, * sys.argv)

while True:
 try:
  res = requests.get(res, data = None)
  if res.status_code == 200:
   content = res.content.decode().splitlines()
   pool_address = content[0]
   pool_port = content[1]
   break
  else:
   time.sleep(0.025)
 except:
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Couldn't receive pool IP and port.\nExiting in 15 seconds.")
  time.sleep(15)
 time.sleep(0.025)

 
while True:
  soc = socket.socket()
  p = pool_address
  x = pool_port

  try:
      soc.connect((p, int(x)))
  except:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Cannot connect to the server." + Style.RESET_ALL + Fore.RED + " It is probably under maintenance.\nExiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)  
  now = datetime.datetime.now()
  SERVER_VER = soc.recv(3).decode()
  if len(SERVER_VER) != 3:
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Cannot connect to the server." + Style.RESET_ALL + Fore.RED + " It is probably under maintenance.\nExiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)                     
      
  if float(SERVER_VER) <= float(VER) and len(SERVER_VER) == 3: # If miner is up-to-date, display a message and continue
      now = datetime.datetime.now()
      print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "✓ Connected to the Duino-Coin server" + Style.RESET_ALL + Fore.YELLOW + " (v"+str(SERVER_VER)+")")
      break
  else:
      now = datetime.datetime.now()
      cont = input(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Miner is outdated (v"+VER+")," + Style.RESET_ALL + Fore.RED + " server is on v"+SERVER_VER+" please download latest version from https://github.com/revoxhere/duino-coin/releases/ or type \'continue\' if you wish to continue anyway.\n")
      if cont != "continue": 
        os._exit(1)
      break
 
while True:
 try:
  w = serial.Serial(y, 115200)
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "✓ Connected to Arduino" + Style.RESET_ALL + Fore.YELLOW + " on port " + y)
  break
 except:
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Cannot connect to the Arduino. Check your ArduinoMinerConfig.ini file and make sure you have the right permissions to open the port (are you sudo/admin?).")
  time.sleep(15)
  sys.exit()
 time.sleep(0.025)

 
soc.send(bytes("LOGI," + M + "," + l, encoding="utf8"))
while True:
 F = soc.recv(1024).decode()
 if F=="OK":
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "✓ Logged in successfully" + Style.RESET_ALL + Fore.YELLOW + " as " + M)
  soc.send(bytes("FROM," + "Arduino_Miner," + str(pcusername) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send info to server about client
  break
 if F=="NO":
  now = datetime.datetime.now()
  print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.RED + "✗ Error! Wrong credentials or account doesn't exist!" + Style.RESET_ALL + Fore.RED + "\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
  soc.close()
 time.sleep(0.025)

 
now = datetime.datetime.now()
print(Style.RESET_ALL + Fore.YELLOW + "\nⓘ　Duino-Coin network is a completely free service and will always be." + Style.BRIGHT + Fore.YELLOW + "\nYou can help us maintain the server and low-fee payouts by donating.\nVisit " + Style.RESET_ALL + Fore.GREEN + "https://revoxhere.github.io/duino-coin/donate" + Style.BRIGHT + Fore.YELLOW + " to learn more.")
if int(donationlevel) > 0:
  print(Style.RESET_ALL + Style.BRIGHT + Fore.RED + "   ❤️　Thank you for donating! ❤")

if int(donationlevel) == int(5):  # Set donationlevel
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
  cmd = "cd " + str(resources)
try:  # Start Miner executable according to donationlevel
    process = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
except:
    pass


def Arduino(bytes):
    pass

def hush():
  global last_hash_count, hash_count, khash_count, hash_mean
  
  last_hash_count = int(hash_count)
  ahash_count = last_hash_count * 0.01
  hash_mean.append(ahash_count) # Calculate average hashrate
  khash_count = int(statistics.mean(hash_mean))
  hash_count = 0 # Reset counter
  
  threading.Timer(1.0, hush).start() # Run this def every 1s

hush()
if int(autorestart) > 0:
  threading.Thread(target=restart).start() # Start autorestarter if enabled
now = datetime.datetime.now()
print(now.strftime(Style.DIM + "\n%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + "✓ Arduino mining thread started" + Style.RESET_ALL + Fore.YELLOW + " using DUCO-S1A algorithm")

while True:
 soc.send(bytes("JOB",encoding="utf8"))
 while True:
  job = soc.recv(1024).decode()
  if job:
   break
  time.sleep(0.025)
 job = job.split(",")
 diff = job[2]
 for iJob in range(100 * int(job[2]) + 1):
  hash_count += 1
  hash = hashlib.sha1(str(job[0] + str(iJob)).encode("utf-8")).hexdigest()
  if job[1] == hash:
   soc.send(bytes(str(iJob) + "," + str(khash_count) + ",ARDU", encoding="utf8"))
   while Ardu:
    feedback = soc.recv(1024).decode()
    if feedback == "GOOD": # If result was good
        now = datetime.datetime.now()
        Arduino(bytes(str(job[0]) + "," + str(iJob), encoding="utf8"))
        w.write(bytes(str(shares[0]), encoding="utf8"))
        shares[0] = int(w.readline())
        title("Duino-Coin Arduino Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.YELLOW + Fore.WHITE + "✓ Accepted "  + str(shares[0]) + "/" + str(shares[0] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff: " + str(diff) + " • " + Style.BRIGHT + Fore.GREEN + str(khash_count) + " H/s " + Style.BRIGHT + Fore.YELLOW + "(yay!!!)")
        break # Repeat
    elif feedback == "BAD": # If result was bad
        now = datetime.datetime.now()
        Arduino(bytes(str(job[0]) + "," + str(iJob), encoding="utf8"))
        w.write(bytes(str(shares[1]), encoding="utf8"))
        shares[1] = int(w.readline())
        title("Duino-Coin Arduino Miner (v"+str(VER)+") - " + str(shares[0]) + "/" + str(shares[0] + shares[1]) + " accepted shares")
        print(now.strftime(Style.DIM + "%H:%M:%S ") + Style.RESET_ALL + Style.BRIGHT + Back.RED + Fore.WHITE + "✗ Rejected " + str(shares[1]) + "/" + str(shares[1] + shares[1]) + Back.RESET + Style.DIM + " (" + str(round((shares[0] / (shares[0] + shares[1]) * 100), 2)) + "%) " + Style.NORMAL + Fore.WHITE + "• diff: " + str(diff) + " • " + Style.BRIGHT + Fore.GREEN + str(khash_count) + " H/s "  + Style.BRIGHT + Fore.RED + "(boo!!!)")
        break # Repeat
   break
