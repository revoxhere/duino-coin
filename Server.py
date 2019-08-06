#!/usr/bin/env python

import socket, threading, time
from pathlib import Path

class ClientThread(threading.Thread):

    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        print("[+] New thread started for "+ip+":"+str(port))


    def run(self):    
        print("Connection from : "+ip+":"+str(port))
        while True:
            data = clientsock.recv(4)
            data=data.decode()
            print("Recieved:", data)
            if data == "REGI":
                print("started register")
                username = clientsock.recv(16)
                username=username.decode()
                print("Username:", username)
                password = clientsock.recv(16)
                password=password.decode()
                print("Password:", password)
                regf = Path(username+".txt")
                if not regf.is_file():
                    file = open(username+".txt", "w")
                    file.write(username+":"+password)
                    file.close()
                    clientsock.send(bytes("OK", encoding='utf8'))
                if regf.is_file():
                    print("Account already exists!")
                    clientsock.send(bytes("NO", encoding='utf8'))
            print("Recieved:", data)
            
            if data == "LOGI":
                print("started login")
                username = clientsock.recv(16)
                username=username.decode()
                print("Username:", username)
                password = clientsock.recv(16)
                password=password.decode()
                print("Password:", password)
                try:
                    file = open(username+".txt", "r")
                    data = file.readline()
                    file.close()
                    if data == username+":"+password:
                        clientsock.send(bytes("OK", encoding='utf8'))
                except:
                    clientsock.send(bytes("NO", encoding='utf8'))
                    print("No account like this!")
                    
            if data == "MINE":
                time.sleep(0.3)
                print("Started mine")
                while True:
                    result = clientsock.recv(4)
                    result=result.decode()
                    print("User", username, "has submited share: ", result)
                    time.sleep(0.1)
            time.sleep(0.1)

host = "127.0.0.1"
port = 5000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []


while True:
    tcpsock.listen(4)
    print("\nListening for incoming connections...")
    (clientsock, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
