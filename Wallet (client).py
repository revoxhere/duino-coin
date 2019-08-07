#!/usr/bin/env python

###########################################
#   Duino-Coin wallet version 0.1 alpha   #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import time, socket, sys, os

users = {}
status = ""
host = '0.tcp.ngrok.io' #server ip
port = 14808 #server port
s = socket.socket()
try: #try to establish connection
    s.connect((host, port))
    print("Successfully connected to the wallet server!")
except:
    print("Server communication failed! Can't reach wallet servers!")
    time.sleep(10)
    sys.exit()

print("*****Official duino-coin WALLET client*****")
welcome = input("Do you have an duino-coin pool acount? y/n: ")
print(" ")
if welcome == "n": #login system, same as in miner
    while True:
        print("***Please register on pool:***")
        username = input("Enter a username:")
        password = input("Enter a password:")
        password1 = input("Confirm password:")
        print("Sent registration request...")
        print("If registration takes more than 5 seconds, please restart and try again!")
        if password == password1:
            s.send(bytes('REGI' , encoding='utf8'))
            time.sleep(0.2)
            s.send(bytes(username , encoding='utf8'))
            time.sleep(0.2)
            s.send(bytes(password , encoding='utf8'))
            key = s.recv(2)
            key=key.decode()
            if key == "OK":
                print(" ")
                print("Successfully registered!")
                print("Now you can restart program and login!")
                time.sleep(10)
                sys.exit()
            if key == "NO":
                print(" ")
                print("That user is already registered!")
                time.sleep(10)
                sys.exit()
        
if welcome == "y":
    while True:
        print("***Please login to wallet:***")
        username = input("Username:")
        password = input("Password:")
        print("Sent login request...")
        print("If login takes more than 5 seconds, please restart and try again!")
        s.send(bytes('LOGI' , encoding='utf8'))
        time.sleep(0.2)
        s.send(bytes(username , encoding='utf8'))
        time.sleep(0.2)
        s.send(bytes(password , encoding='utf8'))
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
            print(" ")
            print("Login successful!")
            print(" ")
            break
        if key == "NO":
            print(" ")
            print("Invalid credentials! There might've been an error! If you don't have an account, restart and register.")
            time.sleep(10)
            sys.exit()

ans=True
while ans:
    time.sleep(0.1)
    s.send(bytes('BALA' , encoding='utf8'))
    time.sleep(0.1)
    balance = s.recv(32)
    balance=balance.decode()
    print("*****Official duino-coin WALLET client*****")
    print("\n")
    print(" Your current account balance:", balance)
    print(" To receive funds, instruct sender to send funds to your username (", username, ").")
    print(" You can send funds using option below. Be aware that recipients' acount has to be activated")
    print("                             (in other words: the recipient has submited at least one share)")
    print("\n")
    chose = input("Do you want to send funds to someone? y/n: ")
    if chose == "y": #info gathering....
        print("Your current account balance is", balance, ". How much funds do you want to send?")
        amount = input("Enter a value: ")
        if amount >= balance:
            print("You don't have that many funds!")
            time.sleep(3)
            sys.exit()
        if amount <= balance: 
            print("Enter username of user to who you want to send", amount, "funds.")
            name = input("Enter username: ")
            s.send(bytes('SEND', encoding='utf8'))
            time.sleep(0.2)
            s.send(bytes(username, encoding='utf8'))
            time.sleep(0.2)
            s.send(bytes(name, encoding='utf8'))
            time.sleep(0.2)
            s.send(bytes(amount, encoding='utf8'))
            time.sleep(0.2)
            message = s.recv(48) #get message from the server
            message=message.decode()
            print(message)
            print("\n")


 
