#!/usr/bin/env python3
# ---------- Duino-Coin Multithreaded PC Miner (v1.7) ----------- #
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2020
# --------------------------------------------------------------- #

refresh_time = 3.5 # refresh time in seconds for the output (recommended: 3.5)
autorestart_time = 360 # autorestart time in seconds. 0 = disabled

discord_key = "" # coming soon

# --------------------------------------------------------------- #

import hashlib
import multiprocessing
import os
import random
import socket
import statistics
import sys
import threading
import time
import urllib.request

if sys.platform == "win32":
    try:
        from colorama import Back, Fore, Style, init
        init()
    except:
        print("You don't have colorama installed. Try to install it now?")
        choice = input("(y/n): ")
        if choice == "y":
            os.system("pip install colorama")
            os._exit(1)
        else:
            os._exit(1)
    colorama_choice = True
else:
    colorama_choice = False

class bcolors:
    blue = '\033[36m'
    yellow = '\033[93m'
    endc = '\033[0m'
    back_cyan = '\033[46m'
    red = '\033[31m'
    back_yellow = '\033[43m'
    black = '\033[30m'
    back_red = '\033[41m'

last_hash_count = 0
khash_count = 0
hash_count = 0
hash_mean = []

def hashrateCalculator():
    global last_hash_count, hash_count, khash_count, hash_mean
    
    last_hash_count = hash_count
    khash_count = last_hash_count / 1000
    if khash_count == 0:
        khash_count = random.uniform(0, 1)
    
    hash_mean.append(khash_count)
    khash_count = statistics.mean(hash_mean)
    khash_count = round(khash_count, 2)
  
    hash_count = 0
  
    threading.Timer(1.0, hashrateCalculator).start()

    
def start_thread(arr, i, username, accepted_shares, bad_shares, thread_number):
    global hash_count, khash_count
    soc = socket.socket()

    serverip = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
    with urllib.request.urlopen(serverip) as content:
        content = content.read().decode().splitlines()
    pool_address = content[0]
    pool_port = content[1]

    soc.connect((str(pool_address), int(pool_port)))
    soc.recv(3).decode()

    hashrateCalculator()
    while True:
        try:
            soc.send(bytes("JOB,"+str(username), encoding="utf8"))
            job = soc.recv(1024).decode()
            job = job.split(",")
            try:
                difficulty = job[2]
            except:
                for p in multiprocessing.active_children():
                    p.terminate()
                time.sleep(1)
                sys.argv.append(str(thread_number))
                os.execl(sys.executable, sys.executable, *sys.argv)

            for result in range(100 * int(difficulty) + 1):
                hash_count = hash_count + 1
                ducos1 = hashlib.sha1(str(job[0] + str(result)).encode("utf-8")).hexdigest()
                if job[1] == ducos1:
                    soc.send(bytes(str(result) + "," + str(last_hash_count) + ",Multithreaded Miner v1.7", encoding="utf8"))
                    feedback = soc.recv(1024).decode()
                    arr[i] = khash_count
                    if feedback == "GOOD" or feedback == "BLOCK":
                        accepted_shares[i] += 1
                        break
                    elif feedback == "BAD":
                        bad_shares[i] += 1
                        break
                    elif feedback == "INVU":
                        print("Entered username is incorrect!")
        except (KeyboardInterrupt, SystemExit):
            print("Thread #{}: exiting...".format(i))
            os._exit(0)


def autorestarter():
    time.sleep(autorestart_time)
    
    for p in multiprocessing.active_children():
        p.terminate()
    time.sleep(1)
    sys.argv.append(str(thread_number))
    os.execl(sys.executable, sys.executable, *sys.argv)


def getBalance():
    global pool_address, pool_port
    soc = socket.socket()
    soc.connect((str(pool_address), int(pool_port)))
    soc.recv(3).decode()

    soc.send(bytes("LOGI," + username + "," + password, encoding="utf8"))
    response = soc.recv(2).decode()           
    if response != "OK":
        print("Error logging in - check account credentials!")
        soc.close()
        os._exit(1)
        
    soc.send(bytes("BALA", encoding="utf8"))
    balance = soc.recv(1024).decode()
    soc.close()
    
    return float(balance)


def calculateProfit(start_bal):
    global curr_bal, profit_array
    
    prev_bal = curr_bal

    curr_bal = getBalance()
    session = curr_bal - start_bal
    minute = curr_bal - prev_bal
    hourly = minute * 60

    profit_array = [session, minute, hourly]
    threading.Timer(60, calculateProfit, [start_bal]).start()


def showOutput():
    clear()

    if colorama_choice:
        print(Back.CYAN + Fore.YELLOW + "Duino-Coin Multithreaded PC Miner" + Style.RESET_ALL + "\n")
    else:
        print(bcolors.back_cyan + bcolors.yellow + "Duino-Coin Multithreaded PC Miner" + bcolors.endc + "\n")
    
    
    if colorama_choice:
        print(Back.YELLOW + Fore.BLACK + "Profit: " + str(profit_array[1]) + "/min   " + str(profit_array[2]) + "/h" + "\nTotal session: " + str(profit_array[0]) + Style.RESET_ALL + "\n")
    else:
        print(bcolors.back_yellow + bcolors.black + "Profit: " + str(profit_array[1]) + "/min   " + str(profit_array[2]) + "/h" + "\nTotal session: " + str(profit_array[0]) + bcolors.endc + "\n")
    
    d = {}
    for thread in range(thread_number):
        d[f"#{thread + 1}"] = [f"{hashrate_array[thread]} kH/s", accepted_shares[thread], bad_shares[thread]]

    if colorama_choice:
        print(Fore.YELLOW + Back.CYAN + "{:<9} {:<13} {:<10} {:<10}".format('Thread','Hashrate','Accepted','Rejected') + Style.RESET_ALL)
    else:
        print(bcolors.yellow + bcolors.back_cyan + "{:<9} {:<13} {:<10} {:<10}".format('Thread','Hashrate','Accepted','Rejected') + bcolors.endc)
    for k, v in d.items():
        hashrate, good, bad = v
        if colorama_choice:
            print(Fore.CYAN + "{:<9} {:<13} {:<10} {:<10}".format(k, hashrate, good, bad) + Style.RESET_ALL)
        else:
            print(bcolors.blue + "{:<9} {:<13} {:<10} {:<10}".format(k, hashrate, good, bad) + bcolors.endc)
    
    if colorama_choice:
        print(Back.RED + "{:<9} {:<13} {:<10} {:<10}".format("TOTAL", totalHashrate(sum(hashrate_array)), sum(accepted_shares), sum(bad_shares)) + Style.RESET_ALL)
    else:
        print(bcolors.back_red + "{:<9} {:<13} {:<10} {:<10}".format("TOTAL", totalHashrate(sum(hashrate_array)), sum(accepted_shares), sum(bad_shares)) + bcolors.endc)

    threading.Timer(float(refresh_time), showOutput).start()
        

def clear():
    os.system('cls' if os.name=='nt' else 'clear')


def totalHashrate(khash):
    if khash / 1000 >= 1:
        return str(round(khash / 1000, 2)) + " MH/s"
    else:
        return str(round(khash, 2)) + " kH/s"


if __name__ == '__main__':
    global thread_number, curr_bal

    if os.name == 'nt':
        os.system("title " + "Duino-Coin multithreaded miner")
    else:
        print('\33]0;' + "Duino-Coin multithreaded miner"+'\a', end='')
    clear()

    if colorama_choice:
        print(Fore.RED + "The profit is refreshed every 60 seconds" + Style.RESET_ALL)
    else:
        print(bcolors.red + "The profit is refreshed every 60 seconds" + bcolors.endc)
    
    if (autorestart_time) > 0:
        threading.Thread(target=autorestarter).start()

    with urllib.request.urlopen("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt") as content:
        content = content.read().decode().splitlines() # doing this here because can't access pool_address and pool_port in the threads
    pool_address = content[0]
    pool_port = content[1]
    
    arguments = len(sys.argv)
    if arguments <= 3:
        if colorama_choice:
            print(Fore.RED + "Provide username, password and thread count!" + Style.RESET_ALL)
            print(Fore.YELLOW + "Example: python3 Multithreaded_PC_Miner.py username password 4" + Style.RESET_ALL)
            print(Fore.RED + "Exiting in 15s." + Style.RESET_ALL)
        else:
            print(bcolors.red + "Provide username, password and thread count!" + bcolors.endc)
            print(bcolors.yellow + "Example: python3 Multithreaded_PC_Miner.py username password 4" + bcolors.endc)
            print(bcolors.red + "Exiting in 15s." + bcolors.endc)
        time.sleep(15)
        os._exit(0)

    username = str(sys.argv[1])
    password = str(sys.argv[2])
    thread_number = int(sys.argv[3])
    if thread_number > 8:
        print("Notice: you're launching a miner with 8+ threads, values this high may not add anything to your efficiency but are spamming our small server.\nIf you don't want to contribute in making server go offline then please set this number a bit lower.\nThanks in advance")
    print(f"Miner for user {username} started with {thread_number} threads")

    hashrate_array = multiprocessing.Array("d", thread_number)
    accepted_shares = multiprocessing.Array("i", thread_number)
    bad_shares = multiprocessing.Array("i", thread_number)

    start_balance = getBalance()
    curr_bal = start_balance
    calculateProfit(start_balance)
    showOutput()

    for i in range(thread_number):
        p = multiprocessing.Process(target=start_thread, args=(hashrate_array, i, username, accepted_shares, bad_shares, thread_number))
        p.start()
        time.sleep(0.5)
    time.sleep(1)
    
