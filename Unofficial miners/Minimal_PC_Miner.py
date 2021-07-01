#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps.
# Created by revox 2020-2021
# Modifications made by Robert Furr (robtech21) and YeahNotSewerSide

import hashlib
import os
import socket
import sys  # Only python3 included libraries
import time
import ssl
import select

AVAILABLE_PORTS = [2812, 2813, 2814, 2815, 2816]
soc = None

username = input('Username?\n> ')
diff_choice = input(
    'Use lower difficulty? (Y/N) [Leave empty for default of True]\n> ')
if diff_choice.lower == "n":
    UseLowerDiff = False
else:
    UseLowerDiff = True


def get_fastest_connection(server_ip: str):
    connection_pool = []
    available_connections = []
    for i in range(len(AVAILABLE_PORTS)):
        connection_pool.append(socket.socket())
        connection_pool[i].setblocking(0)
        try:
            connection_pool[i].connect((server_ip,
                                        AVAILABLE_PORTS[i]))
        except BlockingIOError as e:
            pass

    ready_connections, _, __ = select.select(connection_pool, [], [])

    while True:
        for connection in ready_connections:
            try:
                server_version = connection.recv(100)
            except:
                continue
            if server_version == b'':
                continue

            available_connections.append(connection)
            connection.send(b'PING')

        ready_connections, _, __ = select.select(available_connections, [], [])
        ready_connections[0].recv(100)
        ready_connections[0].settimeout(10)
        return ready_connections[0]


while True:
    try:
        print('Searching for fastest connection to the server')
        soc = get_fastest_connection(str("server.duinocoin.com"))
        print('Fastest connection found')

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
                temp_hash = base_hash.copy()
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
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
