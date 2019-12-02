import socket,threading,time,random,configparser,sys,serial,hashlib,serial.tools.list_ports,datetime,requests
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
from pathlib import Path
O("===========================================")
O("  Duino-Coin Arduino miner version 0.6.7")
O(" https://github.com/revoxhere/duino-coin")
O("        copyright by revox 2019")
O("===========================================\n")
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
                res = requests.get(res, data = None) #Use request to grab data from raw github file
                if res.status_code == 200: #Check for response
                        content = res.content.decode().splitlines() #Read content and split into lines
                        pool_address = content[0] #Line 1 = pool address
                        pool_port = content[1] #Line 2 = pool port
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
if not Path("ArduinoMinerConfig_0.6.7.ini").is_file():
 O("Initial configuration, you can edit 'ArduinoMinerConfig_0.6.7.ini' later\n")
 O("Scanning ports...")
 W=o.list_ports.comports()
 P=[]
 for i in W:
  P.append(i.device)
 O("Found COM ports: "+a(P))
 y=Q("Enter your Arduino port (e.g: COM8): ")
 M=Q("Enter username (the one you used to register): ")
 l=Q("Enter password (the one you used to register): ")
 f['arduinominer']={"arduino":y,"username":M,"password":l}
 with q("ArduinoMinerConfig_0.6.7.ini","w")as configfile:
  f.write(configfile)
else:
 f.read("ArduinoMinerConfig_0.6.7.ini")
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
  O(H.strftime("[%H:%M:%S] ")+"Cannot connect to pool server. Outage? Server update? Retrying in 15 seconds...")
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
O(H.strftime("[%H:%M:%S] ")+"Arduino miner thread started, using 'SHA' algorithm.")
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
     O(H.strftime("[%H:%M:%S] ")+"accepted: "+a(c[0])+"/"+a(c[0]+c[1])+" ("+a(c[0]/(c[0]+c[1])*100)[:5]+"%), diff: "+a(D)+", "+a(z)+" hashes/s (yay!!!)")
     break
    elif V=="BAD":
     H=Y.now()
     c[1]=c[1]+1 
     O(H.strftime("[%H:%M:%S] ")+"rejected: "+a(c[1])+"/"+a(c[1]+c[1])+" ("+a(c[0]/(c[0]+c[1])*100)[:5]+"%), diff: "+a(D)+", "+a(z)+" hashes/s (boo!!!)")
     break
   break
