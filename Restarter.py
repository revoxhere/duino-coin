import socket, time, datetime, subprocess
pool_address = "serveo.net"
pool_port = "14808"


while True:
    soc = socket.socket()
    try:
        soc.connect((pool_address, int(pool_port)))
        try:
            soc.settimeout(1.0)
            resp = soc.recv(1024).decode()
            soc.settimeout(None)
            if resp == "0.6":
                now = datetime.datetime.now()
                print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "Server is up and running [OK] on tcp://"+pool_address+":"+pool_port)
            else:
                now = datetime.datetime.now()
                print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + "> Server is running but SSH not! [ERROR] Restarting!")
                subprocess.call([r'C:\Users\revox.lola\Desktop\Server\autorestart.bat'])
        except:
            now = datetime.datetime.now()
            print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + ">>>>> Server is running but SSH not! [ERROR] Restarting!")
            subprocess.call([r'C:\Users\revox.lola\Desktop\Server\autorestart.bat'])
    except:
        now = datetime.datetime.now()
        print(now.strftime("[%Y-%m-%d %H:%M:%S] ") + ">>> Server is down! [ERROR] Restarting!")
        subprocess.call([r'C:\Users\revox.lola\Desktop\Server\autorestart.bat'])

    time.sleep(10)
    
