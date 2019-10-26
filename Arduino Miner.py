import socket,threading,time,random,configparser,sys,serial,hashlib,serial.tools.list_ports,datetime
d=print
B=int
a=float
E=str
y=input
x=open
i=True
U=bytes
k=range
A=hash
g=datetime
D=datetime.datetime
e=hashlib.sha1
Y=serial.Serial
H=serial.tools
n=sys.exit
K=configparser.ConfigParser
m=random.randint
Q=time.sleep
W=threading.Timer
l=socket.socket
from pathlib import Path
d("===========================================")
d("  Duino-Coin Arduino miner version 0.6.4")
d(" https://github.com/revoxhere/duino-coin")
d("        copyright by revox 2019")
d("===========================================\n")
def L():
 global p,r,O
 p=r
 q=m(716,906)
 c=q/100
 O=B(r)*a(c)
 if O<2.7:
  O=a(O)+B(1)*a(c)
 if O>20.0:
  O=a(O)-B(10)
 O=E(O)[:4]
 r=0
 W(1,L).start()
u=[0,0]
p=0
r=0
O=0
b=K()
if not Path("ArduinoMinerConfig_0.6.4.ini").is_file():
 d("Initial configuration, you can edit 'ArduinoMinerConfig_0.6.4.ini' later\n")
 d("Scanning ports...")
 P=H.list_ports.comports()
 R=[]
 for j in P:
  R.append(j.device)
 d("Found COM ports: "+E(R))
 M=y("Enter your Arduino port (e.g: COM8): ")
 J=y("Enter pool adddress (official: serveo.net): ")
 s=y("Enter pool port (official: 14808): ")
 V=y("Enter username: ")
 o=y("Enter password: ")
 b['arduinominer']={"address":J,"arduino":M,"port":s,"username":V,"password":o}
 with x("ArduinoMinerConfig_0.6.4.ini","w")as configfile:
  b.write(configfile)
else:
 b.read("ArduinoMinerConfig_0.6.4.ini")
 M=b["arduinominer"]["arduino"]
 J=b["arduinominer"]["address"]
 s=b["arduinominer"]["port"]
 V=b["arduinominer"]["username"]
 o=b["arduinominer"]["password"]
while i:
 F=l()
 try:
  F.connect((J,B(s)))
  C=D.now()
  d(C.strftime("[%H:%M:%S] ")+"Connected to pool on tcp://"+J+":"+s)
  break
 except:
  d(C.strftime("[%H:%M:%S] ")+"Cannot connect to pool server. Outage? Server update? Retrying in 15 seconds...")
  Q(15)
 Q(0.025)
while i:
 try:
  G=Y(M,115200)
  C=D.now()
  d(C.strftime("[%H:%M:%S] ")+"Connected to Arduino on port "+M)
  break
 except:
  d(C.strftime("[%H:%M:%S] ")+"Cannot connect to Arduino. Check your ArduinoMinerConfig.ini file. Also make sure you have the right permissions to COM port.")
  Q(15)
  n()
 Q(0.025)
F.send(U("LOGI,"+V+","+o,encoding="utf8"))
while i:
 I=F.recv(1024).decode()
 if I=="OK":
  C=D.now()
  d(C.strftime("[%H:%M:%S] ")+"Successfully logged in.")
  break
 if I=="NO":
  C=D.now()
  d(C.strftime("[%H:%M:%S] ")+"Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
  F.close()
 Q(0.025)
C=D.now()
d(C.strftime("[%H:%M:%S] ")+"Arduino miner thread started, using 'SHA' algorithm.")
L()
F.send(U("JOB",encoding="utf8"))
while i:
 F.send(U("JOB",encoding="utf8"))
 while i:
  w=F.recv(1024).decode()
  if w:
   break
  Q(0.025)
 w=w.split(",")
 S=w[2]
 for v in k(100*B(w[2])+1):
  A=e(E(w[0]+E(v)).encode("utf-8")).hexdigest()
  if w[1]==A:
   G.write(U(E(r),encoding="utf8"))
   r=G.readline().decode('utf8').rstrip()
   F.send(U(E(v),encoding="utf8"))
   while i:
    X=F.recv(1024).decode()
    if X=="GOOD":
     C=D.now()
     u[0]=u[0]+1 
     d(C.strftime("[%H:%M:%S] ")+"accepted: "+E(u[0])+"/"+E(u[0]+u[1])+" ("+E(u[0]/(u[0]+u[1])*100)[:5]+"%), diff: "+E(S)+", "+E(O)+" hashes/s (yay!!!)")
     break
    elif X=="BAD":
     C=D.now()
     u[1]=u[1]+1 
     d(C.strftime("[%H:%M:%S] ")+"rejected: "+E(u[1])+"/"+E(u[1]+u[1])+" ("+E(u[0]/(u[0]+u[1])*100)[:5]+"%), diff: "+E(S)+", "+E(O)+" hashes/s (boo!!!)")
     break
   break
# Created by pyminifier (https://github.com/liftoff/pyminifier)
