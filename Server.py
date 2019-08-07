#!/usr/bin/env python

###########################################
#   Duino-Coin server version 0.1 alpha   #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import socket, threading, time
from pathlib import Path


class ClientThread(threading.Thread): #separate thread for every user

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
            if data == "REGI": #registration
                #time.sleep(0.3)
                print("started register")
                username = clientsock.recv(16)
                username=username.decode()
                print("Username:", username)
                password = clientsock.recv(16)
                password=password.decode()
                print("Password:", password)
                regf = Path(username+".txt")
                if not regf.is_file(): #checking if user already exists
                    file = open(username+".txt", "w")
                    file.write(username+":"+password)
                    file.close()
                    clientsock.send(bytes("OK", encoding='utf8'))
                if regf.is_file():
                    print("Account already exists!")
                    clientsock.send(bytes("NO", encoding='utf8'))
            if data == "LOGI": #login
                #time.sleep(0.1)
                print("started login")
                username = clientsock.recv(16)
                username=username.decode()
                #time.sleep(0.1)
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
                    
            if data == "MINE": #main, mining section
                time.sleep(0.3)
                print("Started mining")
                try:
                    file = open(username+"balance.txt", "r")
                    balance = file.readline()
                    file.close()
                except:
                    file = open(username+"balance.txt", "w")
                    file.write(str(0))
                    file.close()
                while True:
                    result = clientsock.recv(4)
                    result=result.decode()
                    print("User", username, "has submited share: ", result)

                    balance = float(balance) + 0.000000000013
                    try:
                        file = open(username+"balance.txt", "w")
                        file.write(str(balance))
                        file.close()
                    except:
                        print("Error occured while adding funds!")
                    print(username,"'s Balance:", balance)

            if data == "BALA": #check balance section
                time.sleep(0.3)
                print("Sent balance values")
                try:
                    file = open(username+"balance.txt", "r")
                    balance = file.readline()
                    file.close()
                except:
                    file = open(username+"balance.txt", "w")
                    file.write(str(0))
                    file.close()
                    print("Had to set", username, "balance to 0!")
                    file = open(username+"balance.txt", "r")
                    balance = file.readline()
                    file.close()
                clientsock.send(bytes(balance, encoding='utf8'))

            if data == "SEND": #sending funds section
                time.sleep(0.3)
                print("Started send funds protocol")
                username = clientsock.recv(16)
                username=username.decode()
                print("Username:", username)
                name = clientsock.recv(16)
                name=name.decode()
                print("Receiver username:", name)
                amount = clientsock.recv(16)
                amount=amount.decode()
                print("Amount", amount)
                #now we have all data needed to transfer money
                #firstly, get current amount of funds in bank
                print("Sent balance values")
                try:
                    file = open(username+"balance.txt", "r")
                    balance = file.readline()
                    file.close()
                except:
                    print("Error occured while checking funds!")
                #verify that the balance is higher or equal to transfered amount
                if amount >= balance:
                    clientsock.send(bytes("Error! Your balance is lower than amount you want to transfer!", encoding='utf8'))
                if amount <= balance: #if ok, check if recipient adress exists
                    bankf = Path(name+"balance.txt")
                    if bankf.is_file():
                        #it exists, now -amount from username and +amount to name
                        try:
                            #get senders' balance
                            file = open(username+"balance.txt", "r")
                            balance = file.readline()
                            file.close()
                            #remove amount from senders' balance
                            balance = float(balance) - float(amount)
                            file = open(username+"balance.txt", "w")
                            file.write(str(balance))
                            file.close()
                            #get recipients' balance
                            file = open(name+"balance.txt", "r")
                            namebal = file.readline()
                            file.close()
                            #add amount to recipients' balance
                            namebal = float(namebal) + float(amount)
                            file = open(name+"balance.txt", "w")
                            file.write(str(namebal))
                            file.close()
                            
                            clientsock.send(bytes("Successfully transfered funds!!!", encoding='utf8'))
                        except:
                            clientsock.send(bytes("Unknown error occured while sending funds.", encoding='utf8'))
                    if not bankf.is_file(): #message if recipient doesn't exist
                        print("The recepient", name, "doesn't exist!")
                        clientsock.send(bytes("Error! The recipient doesn't exist! Make sure he submited at least one share!", encoding='utf8'))
            #time.sleep(0.1)

host = "localhost"
port = 5000

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []


while True:
    try:
        tcpsock.listen(16)
        print("\nListening for incoming connections...")
        (clientsock, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port)
        newthread.start()
        threads.append(newthread)
    except:
        print("Error in main loop!")

for t in threads:
    t.join()
