import socket,threading,time,random,configparser,sys,serial,hashlib,serial.tools.list_ports,datetime
Q=print
m=int
u=float
X=str
J=input
F=open
i=True
t=bytes
c=range
v=hash
U=datetime
P=datetime.datetime
b=hashlib.sha1
L=serial.Serial
D=serial.tools
a=sys.exit
H=configparser.ConfigParser
o=random.randint
O=time.sleep
z=threading.Timer
y=socket.socket
from pathlib import Path
Q("===========================================")
Q("  Duino-Coin Arduino miner version 0.6.4")
Q(" https://github.com/revoxhere/duino-coin")
Q("        copyright by revox 2019")
Q("===========================================\n")
def l():
 global f,d,e
 f=d
 K=o(716,906)
 B=K/100
 e=m(d)*u(B)
 if e<2.7:
  e=u(e)+m(1)*u(B)
 if e>20.0:
  e=u(e)-m(10)
 e=X(e)[:4]
 d=0
 z(1,l).start()
E=[0,0]
f=0
d=0
e=0
q=H()
if not Path("ArduinoMinerConfig_0.6.4.ini").is_file():
 Q("Initial configuration, you can edit 'ArduinoMinerConfig_0.6.4.ini' later\n")
 Q("Scanning ports...")
 I=D.list_ports.comports()
 V=[]
 for T in I:
  V.append(T.device)
 Q("Found COM ports: "+X(V))
 S=J("Enter your Arduino port (e.g: COM8): ")
 s=J("Enter pool adddress (official: serveo.net): ")
 n=J("Enter pool port (official: 14808): ")
 N=J("Enter username (the one you used to register): ")
 W=J("Enter password (the one you used to register): ")
 q['arduinominer']={"address":s,"arduino":S,"port":n,"username":N,"password":W}
 with F("ArduinoMinerConfig_0.6.4.ini","w")as configfile:
  q.write(configfile)
else:
 q.read("ArduinoMinerConfig_0.6.4.ini")
 S=q["arduinominer"]["arduino"]
 s=q["arduinominer"]["address"]
 n=q["arduinominer"]["port"]
 N=q["arduinominer"]["username"]
 W=q["arduinominer"]["password"]
while i:
 h=y()
 try:
  h.connect((s,m(n)))
  x=P.now()
  Q(x.strftime("[%H:%M:%S] ")+"Connected to pool on tcp://"+s+":"+n)
  break
 except:
  Q(x.strftime("[%H:%M:%S] ")+"Cannot connect to pool server. Outage? Server update? Retrying in 15 seconds...")
  O(15)
 O(0.025)
while i:
 try:
  r=L(S,115200)
  x=P.now()
  Q(x.strftime("[%H:%M:%S] ")+"Connected to Arduino on port "+S)
  break
 except:
  Q(x.strftime("[%H:%M:%S] ")+"Cannot connect to Arduino. Check your ArduinoMinerConfig.ini file. Also make sure you have the right permissions to COM port.")
  O(15)
  a()
 O(0.025)
h.send(t("LOGI,"+N+","+W,encoding="utf8"))
while i:
 w=h.recv(1024).decode()
 if w=="OK":
  x=P.now()
  Q(x.strftime("[%H:%M:%S] ")+"Successfully logged in.")
  break
 if w=="NO":
  x=P.now()
  Q(x.strftime("[%H:%M:%S] ")+"Error! Wrong credentials or account doesn't exist!\nIf you don't have an account, register using Wallet!\nExiting in 15 seconds.")
  h.close()
 O(0.025)
x=P.now()
Q(x.strftime("[%H:%M:%S] ")+"Arduino miner thread started, using 'SHA' algorithm.")
l()
h.send(t("JOB",encoding="utf8"))
while i:
 h.send(t("JOB",encoding="utf8"))
 while i:
  g=h.recv(1024).decode()
  if g:
   break
  O(0.025)
 g=g.split(",")
 A=g[2]
 for G in c(100*m(g[2])+1):
  v=b(X(g[0]+X(G)).encode("utf-8")).hexdigest()
  if g[1]==v:
   r.write(t(X(d),encoding="utf8"))
   d=r.readline().decode('utf8').rstrip()
   h.send(t(X(G)+","+X(e)+" (Arduino)",encoding="utf8"))
   while i:
    k=h.recv(1024).decode()
    if k=="GOOD":
     x=P.now()
     E[0]=E[0]+1 
     Q(x.strftime("[%H:%M:%S] ")+"accepted: "+X(E[0])+"/"+X(E[0]+E[1])+" ("+X(E[0]/(E[0]+E[1])*100)[:5]+"%), diff: "+X(A)+", "+X(e)+" hashes/s (yay!!!)")
     break
    elif k=="BAD":
     x=P.now()
     E[1]=E[1]+1 
     Q(x.strftime("[%H:%M:%S] ")+"rejected: "+X(E[1])+"/"+X(E[1]+E[1])+" ("+X(E[0]/(E[0]+E[1])*100)[:5]+"%), diff: "+X(A)+", "+X(e)+" hashes/s (boo!!!)")
     break
   break
# Created by pyminifier (https://github.com/liftoff/pyminifier)
