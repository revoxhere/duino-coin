#!/usr/bin/env python

###########################################
#   Duino-Coin miner version 0.1 alpha    #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import serial, time, random, socket, datetime, sys

users = {}
status = ""
ser = serial.Serial('COM8') #COM on windows, /dev/... on linux... i presume? this needs testing
host = '0.tcp.ngrok.io' #server ip
port = 14808 #server port
s = socket.socket()
try: #establish connection
    s.connect((host, port))
    print("Successfully connected to the mining server!")
except:
    print("Server communication failed! Can't reach mining servers!")
    time.sleep(10)
    sys.exit()

print("*****Official duino-coin miner*****")
welcome = input("Do you have an duino-coin acount? y/n: ")
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
            s.send(bytes('REGI' , encoding='utf8')) #send register request to server
            time.sleep(0.1)
            s.send(bytes(username , encoding='utf8'))
            time.sleep(0.1)
            s.send(bytes(password , encoding='utf8'))
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
        time.sleep(0.1)
        s.send(bytes('LOGI' , encoding='utf8')) #send login request to server
        time.sleep(0.1)
        s.send(bytes(username , encoding='utf8'))
        time.sleep(0.1)
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
            print("Invalid credentials! There might've been an error. Try again! If you don't have an account, restart and register.")
            time.sleep(10)
            sys.exit()
 

def mine(): #mining section
    s.send(bytes("MINE", encoding='utf8')) #send mine request to server
    time.sleep(0.1)
    while True:
        now = datetime.datetime.now()
        work = random.randint(0,9)
        work2 = random.randint(0,9)

        ser.write(b'1') #establish connection to arduino
        connection = ser.readline()
        connection=connection.decode('utf-8')
    
        ser.write(str(work).encode()) #give work to arduino
        ser.write(str(work2).encode())
    
        result = ser.readline() #get and hash the result
        result=result.decode('utf-8')
        print(now.strftime("[%Y-%m-%d %H:%M:%S]"), "Share found (yay!!!) at", result,) #some spicy messages
        s.send(bytes(result, encoding='utf8')) #send result to server which will take care of rest
        time.sleep(0.1)

mine() #JUST... MINE :D


