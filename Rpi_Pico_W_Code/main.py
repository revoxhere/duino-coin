username = "lucasz228"
mining_key = "None"
avrMinerName = "picoW"
wifiSSID = "wifiSSID"
wifiPassword = "wifiPassword"


import hashlib
import network
from socket import socket
import time
import machine
import binascii

led = machine.Pin("LED", machine.Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifiSSID, wifiPassword)
while wlan.isconnected() == False:
    print(time.time(), 'Waiting for connection...')
    time.sleep(1)
print(time.time(), 'Connection successful')
print(time.time(), 'Network config:', wlan.ifconfig())

soc = socket()


def DUCOS1(last_h: str, exp_h: str, diff: int):
    hashingStartTime = time.time_ns()
    for nonce in range(100 * diff + 1):
        temp_h = hashlib.sha1(last_h.encode('ascii'))
        temp_h.update(str(nonce).encode('ascii'))
        d_res = binascii.hexlify(temp_h.digest()).decode('ascii')

        if d_res == exp_h:
            time_elapsed = time.time_ns() - hashingStartTime
            if time_elapsed > 0:
                hashrate = 1e9 * nonce / time_elapsed
            else:
                return [nonce, 0]

            return [nonce, hashrate]
    return [0, 0]

start_diff = "DUE"

print(time.time(), 'Searching for fastest connection to the server')
NODE_ADDRESS, NODE_PORT = "177.92.44.137", 6403
print(time.time(), 'Connecting to the server',
      NODE_ADDRESS, "on port", NODE_PORT)
soc.connect((str(NODE_ADDRESS), int(NODE_PORT)))
print(time.time(), 'Fastest connection found')
server_version = soc.recv(100).decode()
print(time.time(), 'Server Version: ' + server_version)

# Mining section
while True:
    # Send job request for lower diff
    soc.send(bytes("JOB," + str(username) + "," + start_diff +
             "," + str(mining_key), "utf8"))
    print(time.time(), 'Requested job with diff', start_diff)

    # Receive work
    job = soc.recv(1024).decode().rstrip("\n")
    print(time.time(), 'Received job', job)
    # Split received data to job and difficulty
    job = job.split(",")
    difficulty = job[2]
    result, hashrate = DUCOS1(job[0], job[1], int(difficulty))
    print(time.time(), 'Solved job with diff', difficulty)
    print(time.time(), 'Result is', result)
    # Send numeric result to the server
    soc.send(bytes(str(result) + "," + str(hashrate) + ",Official AVR Miner 4.0," +
             avrMinerName + "," + "DUCOID0000000000000000", "utf8"))

    # Get feedback about the result
    feedback = soc.recv(1024).decode().rstrip("\n")
    # If result was good
    if feedback == "GOOD":
        print(time.time(), 'Accepted share', result, "Hashrate",
              (hashrate/1000), "kH/s", "Difficulty", difficulty)
    # If result was incorrect
    elif feedback == "BAD":
        print(time.time(), 'Rejected share', result, "Hashrate",
              (hashrate/1000), "kH/s", "Difficulty", difficulty)
    else:
        print(time.time(), 'Error:', feedback)
