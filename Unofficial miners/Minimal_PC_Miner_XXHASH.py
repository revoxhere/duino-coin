#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner
# Using the XXHASH algorithm
# Created by revox 2020-2021
import os
import socket
import sys  # Only python3 included libraries
import time
import urllib.request

import xxhash  # use python3 -m pip install xxhash to install xxhash

soc = socket.socket()
soc.settimeout(10)

username = "revox"  # Edit this to your username, mind the quotes


def retrieve_server_ip():
    print("> Retrieving Pool Address and Port")
    pool_obtained = False
    while not pool_obtained:
        try:
            serverip = ("https://raw.githubusercontent.com/"
                            + "revoxhere/"
                            + "duino-coin/gh-pages/"
                            + "serverip.txt")
            with urllib.request.urlopen(serverip) as content:
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
            # Send job request
            soc.send(bytes(
                "JOBXX,"
                + str(username)
                + ",NET",
                encoding="utf8"))
            # Receive work
            job = soc.recv(1024).decode().rstrip("\n")
            # Split received data to job and difficulty
            job = job.split(",")
            difficulty = job[2]

            hashingStartTime = time.time()
            for ducos1xxres in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                ducos1xx = xxhash.xxh64(
                    str(job[0])
                    + str(ducos1xxres),
                    seed=2811).hexdigest()

                # If hash is even with expected hash result
                if job[1] == ducos1xx:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = ducos1xxres / timeDifference

                    # Send numeric result to the server
                    soc.send(bytes(
                        str(ducos1xxres)
                        + ","
                        + str(hashrate) +
                        ",Minimal PC Miner (XXHASH)",
                        encoding="utf8"))

                    # Get feedback about the result
                    feedback = soc.recv(1024).decode().rstrip("\n")
                    # If result was good
                    if feedback == "GOOD":
                        print("Accepted share",
                              ducos1xxres,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break
                    # If result was incorrect
                    elif feedback == "BAD":
                        print("Rejected share",
                              ducos1xxres,
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
        os.execv(sys.argv[0], sys.argv)
