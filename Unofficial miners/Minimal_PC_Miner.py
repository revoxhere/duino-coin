#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox 2020-2021
import socket, hashlib, urllib.request, time, os, sys  # Only python3 included libraries

soc = socket.socket()
soc.settimeout(10)

username = "enter your username here"  # Edit this to your username, mind the quotes
UseLowerDiff = True  # Set it to True to mine with lower difficulty

while True:
    try:
        # This sections grabs pool adress and port from Duino-Coin GitHub file
        serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"  # Serverip file
        with urllib.request.urlopen(serverip) as content:
            content = (
                content.read().decode().splitlines()
            )  # Read content and split into lines
        pool_address = content[0]  # Line 1 = pool address
        pool_port = content[1]  # Line 2 = pool port

        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))  # Connect to the server
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)
        # Mining section
        while True:
            if UseLowerDiff:
                soc.send(
                    bytes("JOB," + str(username) + ",MEDIUM", encoding="utf8")
                )  # Send job request
            else:
                soc.send(
                    bytes("JOB," + str(username), encoding="utf8")
                )  # Send job request
            job = soc.recv(1024).decode()  # Get work from pool
            job = job.split(",")  # Split received data to job (job and difficulty)
            difficulty = job[2]

            hashingStartTime = time.time()
            for result in range(
                100 * int(difficulty) + 1
            ):  # Calculate hash with difficulty
                ducos1 = hashlib.sha1(
                    str(job[0] + str(result)).encode("utf-8")
                ).hexdigest()  # Generate hash
                if job[1] == ducos1:  # If result is even with job
                    hashingStopTime = time.time()
                    difference = hashingStopTime - hashingStartTime
                    hashrate = result / difference
                    soc.send(
                        bytes(str(result) + "," + str(hashrate) + ",Minimal_PC_Miner", encoding="utf8")
                    )  # Send result of hashing algorithm to pool
                    feedback = soc.recv(1024).decode()  # Get feedback about the result
                    if feedback == "GOOD":  # If result was good
                        print("Accepted share", result, "Hashrate", int(hashrate/1000), "kH/s", "Difficulty", difficulty)
                        break
                    elif feedback == "BAD":  # If result was bad
                        print("Rejected share", result, "Hashrate", int(hashrate/1000), "kH/s", "Difficulty", difficulty)
                        break
    except Exception as e:
        print("Error occured: " + str(e) + ", restarting in 5s.")
        time.sleep(5)
        os.execv(sys.argv[0], sys.argv)
