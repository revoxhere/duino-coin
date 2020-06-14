#!/usr/bin/env python3
# Minimal version of Duino-Coin PC Miner, useful for developing own apps. Created by revox and aSOVIET 2020
import socket, hashlib, os, urllib.request, random, statistics, threading # Only python3 included libraries
soc = socket.socket()
from numba import jit

username = "username"
password = "password"

last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []

def hashrateCalculator(): # Hashes/sec calculation
  global last_hash_count, hash_count, khash_count, hash_mean
  
  last_hash_count = hash_count
  khash_count = last_hash_count / 1000
  if khash_count == 0:
    khash_count = random.uniform(0, 2)
    
  hash_mean.append(khash_count) # Calculate average hashrate
  khash_count = statistics.mean(hash_mean)
  khash_count = round(khash_count, 2)
  
  hash_count = 0 # Reset counter
  
  threading.Timer(1.0, hashrateCalculator).start() # Run this def every 1s


# This sections grabs pool adress and port from Duino-Coin GitHub file
serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
with urllib.request.urlopen(serverip) as content:
    content = content.read().decode().splitlines() #Read content and split into lines
pool_address = content[0] #Line 1 = pool address
pool_port = content[1] #Line 2 = pool port

# This section connects and logs user to the server
soc.connect((str(pool_address), int(pool_port))) # Connect to the server
server_version = soc.recv(3).decode() # Get server version
print("Server is on version", server_version)

soc.send(bytes("LOGI," + username + "," + password, encoding="utf8")) # Send login data
response = soc.recv(2).decode() # Get server feedback about logging in                
if response == "OK":
    print("Loged in")
else:
    print("Error loging in - check account credentials!")
    soc.close()
    os._exit(1)

#@jit()
def doHash(hash, prevHash, diff):
    for result in range(100 * int(diff) + 1): # Calculate hash with difficulty
        ducos1 = hashlib.sha1(str((hash) + str(result)).encode("utf-8")).hexdigest() # Generate hash
        if prevHash == ducos1: # If result is even with job
            return result

hashrateCalculator() # Start hashrate calculator
while True:
    soc.send(bytes("JOB", encoding="utf8")) # Send job request
    job = soc.recv(1024).decode() # Get work from pool
    job = job.split(",") # Split received data to job (job and difficulty)
    difficulty = job[2]
    result = doHash(job[0], job[1], difficulty)
    soc.send(bytes(str(result), encoding="utf8")) # Send result of hashing algorithm to pool
    feedback = soc.recv(1024).decode() # Get feedback about the result
    if feedback == "GOOD": # If result was good
        print("ACCEPTED SHARE • diff", difficulty, "•", str(round(khash_count * 100)), "kH/s")
    elif feedback == "BAD": # If result was bad
        print("Rejected share", result, "Difficulty", difficulty)
