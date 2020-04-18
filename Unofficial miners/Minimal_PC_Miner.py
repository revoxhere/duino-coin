#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020
import socket, hashlib, os, urllib.request, time # Only python3 included libraries

username = "enter your username here"
password = "enter your password here"

soc = socket.socket()

# This sections grabs pool adress and port from Duino-Coin GitHub file
while True: # Grab data grom GitHub section
    serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
    with urllib.request.urlopen(serverip) as content:
        content = content.read().decode().splitlines() #Read content and split into lines
    pool_address = content[0] #Line 1 = pool address
    pool_port = content[1] #Line 2 = pool port
    break # Continue

# This section connects and logs user to the server
soc.connect((str(pool_address), int(pool_port))) # Connect to the server
while True:
    soc.send(bytes("LOGI," + username + "," + password, encoding="utf8")) # Send login data
    
    server_version = soc.recv(3).decode() # Get server version
    print("Server is on version", server_version)
    
    response = soc.recv(2).decode() # Get server feedback about logging in                
    if response == "NO":
        print("Error loging in - check account credentials!")
        soc.close()
        time.sleep(15)
        os._exit(1)
    if response == "OK":
        print("Loged in")
        break

# Mining section
while True:
    soc.send(bytes("JOB", encoding="utf8")) # Send job request
    while True:
        job = soc.recv(1024).decode() # Get work from pool
        if job:
            break # If job received, continue to hashing it
        time.sleep(0.025)
    job = job.split(",") # Split received data to job (job and difficulty)
    difficulty = job[2]
    for result in range(100 * int(difficulty) + 1): # Calculate hash with difficulty
            ducos1 = hashlib.sha1(str(job[0] + str(result)).encode("utf-8")).hexdigest() # Generate hash
            if job[1] == ducos1: # If result is even with job
                soc.send(bytes(str(result), encoding="utf8")) # Send result of hashing algorithm to pool
                while True:
                    feedback = soc.recv(1024).decode() # Get feedback about the result
                    if feedback == "GOOD": # If result was good
                        print("Accepted share", result, "Difficulty", difficulty)
                        break
                    elif feedback == "BAD": # If result was bad
                        print("Rejected share", result, "Difficulty", difficulty)
                        break
                    time.sleep(0.025)
                break
