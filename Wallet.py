#!/usr/bin/env python

###########################################
#   Duino-Coin wallet version 0.5 alpha   #
# https://github.com/revoxhere/duino-coin #
# copyright by mrkris7100 & revox 2019    #
###########################################

import time, socket, sys, os

users = {}
status = ""
host = 'localhost' #server ip
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
            s.send(bytes('REGI' + ',' + username + ',' + password, encoding='utf8')) #send register request to server
            key = s.recv(2)
            key=key.decode()
            if key == "OK":
                print(" ")
                print("Successfully registered!")
                print("Now you can restart the program and login!")
                time.sleep(10)
                sys.exit()
            elif key == "NO":
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
        time.sleep(0.1)
        s.send(bytes('LOGI' + ',' + username + ',' + password, encoding='utf8')) #send login request to server
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
            print(" ")
            print("Login successful!")
            print(" ")
            break
        elif key == "NO":
            print(" ")
            print("Invalid credentials! There might've been an error. Try again! If you don't have an account, restart and register.")
            time.sleep(10)
            sys.exit()
while True:
    print("\n"*17) #for privacy - move the screen up a bit so password won't be seen
    s.send(bytes('BALA' , encoding='utf8'))
    balance = float(s.recv(32).decode())
    print("*****Official duino-coin WALLET client*****")
    print("\n")
    print(" Your current account balance:", balance)
    print(" To receive funds, instruct sender to send funds to your username (", username, ").")
    print(" You can send funds using option below.")
    print(" Current fee: 0%")
    print("\n"*5)
    chose = input("Do you want to send funds to someone? y/n: ")
    if chose == "y": #info gathering....
        print("Your current account balance is", balance, ". How much funds do you want to send?")
        amount = float(input("Enter a value: "))
        if amount > balance:
            print("You don't have that many funds!")
            time.sleep(3)
        else: 
            print("Enter username of user to who you want to send", amount, "funds.")
            name = input("Enter username: ")
            s.send(bytes('SEND' + ',' + username + ',' + name + ',' + str(amount), encoding='utf8'))
            message = s.recv(48) #get message from the server
            message=message.decode()
            print(message)
            print("\n")
            time.sleep(3)


 
