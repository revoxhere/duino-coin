#!/usr/bin/env python3
#############################################
# Duino-Coin PC Miner (Beta v1) © revox 2020
# https://github.com/revoxhere/duino-coin 
#############################################
import socket,threading,time,random,configparser,sys,serial,hashlib,serial.tools.list_ports,datetime,requests
from pathlib import Path

O=print
h=int
E=float
a=str
Q=input
q=open
J=True
r=bytes
u=range
U=hash
j=datetime
Y=datetime.datetime
K=hashlib.sha1
C=serial.Serial
o=serial.tools
I=sys.exit
R=configparser.ConfigParser
e=random.randint
X=time.sleep
res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
B=threading.Timer
A=socket.socket

O("\n▋ Duino-Coin Arduino Miner (Beta v1) © revox 2019-2020")
O("▋ https://github.com/revoxhere/duino-coin\n")

def L():
 global S,b,z
 S=b
 s=e(716,906)
 n=s/100
 z=h(b)*E(n)
 if z<2.7:
  z=E(z)+h(1)*E(n)
 if z>20.0:
  z=E(z)-h(10)
 z=a(z)[:4]
 b=0
 B(1,L).start()
c=[0,0]
S=0
b=0
z=0
f=R()
while True:
 try:
  res = requests.get(res, data = None)
  if res.status_code == 200:
   content = res.content.decode().splitlines()
   pool_address = content[0]
   pool_port = content[1]
   H=Y.now()
   O(H.strftime("[%H:%M:%S] ")+"Successfully received pool IP and port.")
   break
  else:
   X(0.025)
 except:
  H=Y.now()
  O(H.strftime("[%H:%M:%S] ")+"Couldn't receive pool IP and port. Exiting in 15 seconds.")
  X(15)
 X(0.025)
if not Path("ArduinoMinerConfig_beta.1.ini").is_file():
 O("Initial configuration, you can edit 'ArduinoMinerConfig_beta.1.ini' later\n")
 O("Scanning ports...")
 W=o.list_ports.comports()
 P=[]
 for i in W:
  P.append(i.device)
 O("Found COM ports: "+a(P))
 y=Q("Enter your Arduino COM port (e.g: COM8): ")
 M=Q("Enter username (the one you used to register): ")
 l=Q("Enter password (the one you used to register): ")
 f['arduinominer']={"arduino":y,"username":M,"password":l}
 with q("ArduinoMinerConfig_beta.1.ini","w")as configfile:
  f.write(configfile)
else:
 f.read("ArduinoMinerConfig_beta.1.ini")
 y=f["arduinominer"]["arduino"]
 p=pool_address
 x=pool_port
 M=f["arduinominer"]["username"]
 l=f["arduinominer"]["password"]
while J:
 v=A()
 try:
  v.connect((p,h(x)))
  H=Y.now()
  O(H.strftime("[%H:%M:%S] ")+"Connected to pool on tcp://"+p+":"+x)
  break
 except:
  O(H.strftime("[%H:%M:%S] ")+"Cannot connect to pool server. It is probably under maintenance. Retrying in 15 seconds...")
  X(15)
 X(0.025)
while J:
 try:
  w=C(y,115200)
  H=Y.now()
  O(H.strftime("[%H:%M:%S] ")+"Connected to Arduino on port "+y)
  break
 except:
  O(H.strftime("[%H:%M:%S] ")+"Cannot connect to Arduino. Check your ArduinoMinerConfig.ini file. Also make sure you have the right permissions to COM port.")
  X(15)
  I()
 X(0.025)
v.send(r("LOGI,"+M+","+l,encoding="utf8"))
while J:
 F=v.recv(1024).decode()
 if F=="OK":
  H=Y.now()
  O(H.strftime("[%H:%M:%S] ")+"Successfully logged in.")
  break
 if F=="NO":
  H=Y.now()
  O(H.strftime("[%H:%M:%S] ")+"Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
  v.close()
 X(0.025)
H=Y.now()
O(H.strftime("[%H:%M:%S] ")+"Arduino miner thread started, using SHA1 algorithm.")
O("\nDuino-Coin network is a completely free service and will always be. You can really help us maintain the server and low-fee payouts by donating - visit https://revoxhere.github.io/duino-coin/donate to learn more.\n")

L()
v.send(r("JOB",encoding="utf8"))
while J:
 v.send(r("JOB",encoding="utf8"))
 while J:
  g=v.recv(1024).decode()
  if g:
   break
  X(0.025)
 g=g.split(",")
 D=g[2]
 for G in u(100*h(g[2])+1):
  U=K(a(g[0]+a(G)).encode("utf-8")).hexdigest()
  if g[1]==U:
   w.write(r(a(b),encoding="utf8"))
   b=w.readline().decode('utf8').rstrip()
   v.send(r(a(G)+","+a(S),encoding="utf8"))
   while J:
    V=v.recv(1024).decode()
    if V=="GOOD":
     H=Y.now()
     c[0]=c[0]+1 
     O(H.strftime("[%H:%M:%S] ")+"Accepted: "+a(c[0])+"/"+a(c[0]+c[1])+" ("+a(c[0]/(c[0]+c[1])*100)[:5]+"%), diff: "+a(D)+", "+a(z)+" hashes/s (yay!!!)")
     break
    elif V=="BAD":
     H=Y.now()
     c[1]=c[1]+1 
     O(H.strftime("[%H:%M:%S] ")+"Rejected: "+a(c[1])+"/"+a(c[1]+c[1])+" ("+a(c[0]/(c[0]+c[1])*100)[:5]+"%), diff: "+a(D)+", "+a(z)+" hashes/s (boo!!!)")
     break
   break
