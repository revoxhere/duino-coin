#!/usr/bin/env python

###########################################
#   Duino-Coin wallet version 0.4 alpha   #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

# Wallet will be updated (ability to auto-login and send funds) in the future

import time, socket, sys, os

users = {}
status = ""
host = 'serveo.net' #server ip
port = 14808 #server port
s = socket.socket()

print("*****Official duino-coin wallet*****")
print("*************version 3**************")
print("\n")

try: #try to establish connection
    s.connect((host, port))
    print("Successfully connected to the wallet server!")
except:
    print("Server communication failed! A server update is probably underway. Please try again in a couple of hours.")
    time.sleep(10)
    sys.exit()
welcome = input("Do you have an duino-coin pool acount? y/n: ")
print(" ")
if welcome == "n": #login system
    while True:
        print("***Please register on pool:***")
        username = input("Enter a username:")
        password = input("Enter a password:")
        password1 = input("Confirm password:")
        print("Sent registration request...")
        print("If registration takes more than 5 seconds, please restart and try again!")
        if password == password1:
            s.send(bytes("REGI,"+username+","+password, encoding='utf8')) #send register request to server
            key = s.recv(2)
            key=key.decode()
            if key == "OK":
                print(" ")
                print("Successfully registered!")
                print("Now you can restart the program and login!")
                time.sleep(10)
                sys.exit()
            if key == "NO":
                print(" ")
                print("That user is already registered!")
                time.sleep(10)
                sys.exit()
        
if welcome == "y":
    while True:
        print("***Please login to pool:***")
        username = input("Username:")
        password = input("Password:")
        print("Sent login request...")
        print("If login takes more than 5 seconds, please restart and try again!")
        s.send(bytes("LOGI,"+username+","+password, encoding='utf8')) #send login request to server
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
            print(" ")
            print("Login successful!")
            print(" ")
            break
        if key == "NO":
            print(" ")
            print("Invalid credentials! If you don't have an account, restart and register.")
            time.sleep(10)
            sys.exit()
menu=True
while menu:
    print("\n"*17) #for privacy - move the screen up a bit so password won't be seen
    time.sleep(0.1)
    s.send(bytes("BALA", encoding='utf8'))
    balance = s.recv(32)
    balance=balance.decode()
    print("*****Official duino-coin WALLET client*****")
    print("\n")
    print(" Your current account balance:", balance)
    print(" To receive funds, instruct sender to send funds to your username (", username, ").")
    print(" You can send funds using option below.")
    print(" Current fee: 0%")
    print("\n"*5)
    print(" Sending funds is currenty DISABLED. Try again later.")



 
