#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020-2021
# Modifications made by Robert Furr (robtech21)

import hashlib
import os
import socket
import sys  # Only python3 included libraries
import time
import urllib.request
import ssl

soc = socket.socket()
soc.settimeout(10)

username = input('Username?\n> ') 

DiffChoice = input('User lower difficulty? (Y/N) [Leave empty for default of True]\n> ')
if DiffChoice.lower == "n":
    UseLowerDiff = False
else:
    UseLowerDiff = True

def retrieve_server_ip():
    print("> Retrieving Pool Address And Port")
    pool_obtained = False
    while not pool_obtained:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            serverip = ("https://raw.githubusercontent.com/"
                            + "revoxhere/"
                            + "duino-coin/gh-pages/"
                            + "serverip.txt")
            with urllib.request.urlopen(serverip, context=ctx) as content:
                # Read content and split into lines
                content = content.read().decode().splitlines()
            global pool_address, pool_port
            # Line 1 = IP
            pool_address = content[0]
            # Line 2 = port
            pool_port = content[1]
            pool_obtained =  True
        except:
            print("> Failed to retrieve Pool Address and Port, Retrying.")
            continue

retrieve_server_ip()
while True:
    try:
        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)

        # Mining section
        while True:
            if UseLowerDiff:
                # Send job request for lower diff
                soc.send(bytes(
                    "JOB,"
                    + str(username)
                    + ",MEDIUM",
                    encoding="utf8"))
            else:
                # Send job request
                soc.send(bytes(
                    "JOB,"
                    + str(username),
                    encoding="utf8"))

            # Receive work
            job = soc.recv(1024).decode().rstrip("\n")
            # Split received data to job and difficulty
            job = job.split(",")
            difficulty = job[2]
            
            hashingStartTime = time.time()
            base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
            temp_hash = None
            
            for result in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                temp_hash =  base_hash.copy()
                temp_hash.update(str(result).encode('ascii'))
                ducos1 = temp_hash.hexdigest()

                # If hash is even with expected hash result
                if job[1] == ducos1:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = result / timeDifference

                    # Send numeric result to the server
                    soc.send(bytes(
                        str(result)
                        + ","
                        + str(hashrate)
                        + ",Minimal_PC_Miner",
                        encoding="utf8"))

                    # Get feedback about the result
                    feedback = soc.recv(1024).decode().rstrip("\n")
                    # If result was good
                    if feedback == "GOOD":
                        print("Accepted share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break
                    # If result was incorrect
                    elif feedback == "BAD":
                        print("Rejected share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break

    except Exception as e:
        print("Error occured: " + str(e) + ", restarting in 5s.")
        retrieve_server_ip()
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
