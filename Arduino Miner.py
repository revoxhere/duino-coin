#!/usr/bin/env python
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ=print
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹=str
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ=input
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅힉=open
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳=True
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𤴰=int
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐢈=bytes
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅께=range
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤍=hash
import socket, threading, time, random, configparser, sys, serial, hashlib, serial.tools.list_ports
from pathlib import Path
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𣎹=hashlib.sha1
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𗒙=serial.Serial
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𢡹=serial.tools
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﻧ=sys.exit
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࢢ=configparser.ConfigParser
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂=time.sleep
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ܗ=threading.Timer
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ꏑ=socket.socket
from pathlib import Path
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞠼="0.6"
def 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩱘():
 global 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅筲,𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅筲=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌=0
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ܗ(1.0,𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩱘).start()
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃=[0,0]
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅筲=0
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌=0
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࢢ()
if not Path("ArduinoMinerConfig.ini").is_file():
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Initial configuration, you can edit 'ArduinoMinerConfig.ini' later\n")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Scanning ports...")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𫕐=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𢡹.list_ports.comports()
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅폳=[]
 for 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𤚶 in 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𫕐:
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅폳.append(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𤚶.device)
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Found COM ports: "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅폳))
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ޅ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ("Enter your Arduino port (e.g: COM8): ")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࡀ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ("Enter pool adddress (official: serveo.net): ")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩺁=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ("Enter pool port (official: 14808): ")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﴢ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ("Enter username: ")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐦲=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﶎ("Enter password: ")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ['pool']={"address":𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࡀ,"arduino":𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ޅ,"port":𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩺁,"username":𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﴢ,"password":𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐦲}
 with 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅힉("ArduinoMinerConfig.ini","w")as configfile:
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ.write(configfile)
else:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ.read("ArduinoMinerConfig.ini")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ޅ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ["pool"]["arduino"]
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࡀ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ["pool"]["address"]
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩺁=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ["pool"]["port"]
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﴢ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ["pool"]["username"]
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐦲=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﱌ["pool"]["password"]
while 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Connecting to pool...")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ꏑ()
 try:
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.connect((𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࡀ,𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𤴰(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩺁)))
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Connected!")
  break
 except:
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Cannot connect to pool server. Retrying in 30 seconds...")
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(30)
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(0.025)
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Connecting to Arduino...")
try:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࢴ=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𗒙(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ޅ,9600)
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Connected to Arduino!")
except:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Cannot connect to Arduino. Check your ArduinoMinerConfig.ini file.")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﻧ()
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Checking version...")
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𬸉=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.recv(1024).decode()
if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𬸉==𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞠼:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Miner is up-to-date.")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(0.1)
else:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Miner is outdated, please download latest version from https://github.com/revoxhere/duino-coin/releases/")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Exiting in 5s.")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(5)
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﻧ()
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Logging in...")
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.send(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐢈("LOGI,"+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﴢ+","+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐦲,encoding="utf8"))
while 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤲=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.recv(1024).decode()
 if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤲=="OK":
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Logged in!")
  break
 if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤲=="NO":
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Error, closing in 5 seconds...")
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.close()
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(5)
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﻧ()
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(0.025)
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Started arduino mining thread...")
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(1)
𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𩱘()
while 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳:
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.send(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐢈("JOB",encoding="utf8"))
 while 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳:
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.recv(1024).decode()
  if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠:
   break
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(0.025)
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠.split(",")
 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Recived new job from pool, difficulty: "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠[2])
 for 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐬇 in 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅께(100*𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𤴰(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠[2])+1):
  𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤍=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𣎹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠[0]+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐬇)).encode("utf-8")).hexdigest()
  if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𘂠[1]==𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐤍:
   𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.send(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐢈(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐬇)+","+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌),encoding="utf8"))
   while 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅崳:
    𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࢴ.write(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𐢈(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌),encoding="utf8"))
    𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅裌=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ࢴ.readline().decode('utf8').rstrip()
    𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𧗨=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𦈏.recv(1024).decode()
    if 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𧗨=="GOOD":
     𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]+1 
     𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Share accepted "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0])+"/"+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1])+" ("+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]/(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1])*100)+"%), "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅筲)+" H/s")
     break
    elif 𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𧗨=="BAD":
     𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1]=𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1]+1 
     𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅ﲠ("Share rejected "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0])+"/"+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1])+" ("+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]/(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[0]+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𞥃[1])*100)+"%), "+𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅䊹(𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅筲)+" H/s")
     break
    𞹭ᐤ𐡆ﭡ𪑈𞡱ꝩ𐮇𣮍𖤛鹅𪕂(0.025)
   break
# Created by pyminifier (https://github.com/liftoff/pyminifier)
