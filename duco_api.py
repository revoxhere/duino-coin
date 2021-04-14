##########################################
# Duino-Coin API Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################
import ast
import hashlib
import json
import os
import queue
import socket
import sys
import threading
import time
import urllib.request
from threading import Timer

import requests
from requests import get

miner_q = queue.Queue()


#====================================# Vars #====================================#


TRANSACTIONS_URL = "http://51.15.127.80/transactions.json"

API_URL = "http://51.15.127.80/api.json"
SERVER_URL = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"

duco_price = 0.003
socket.setdefaulttimeout(10)


#====================================# common functions #====================================#


def decode_response(rec):
    return rec.decode().split(",")


#====================================# Duco Transactions #====================================#

class transaction_data:

    def __init__(self, data, token):
        self.data = data
        self.token = token

        self.obj = (self.token, self.data)
        self.all = (self.token, self.data)

        self.time = self.data["Time"]
        self.amount = self.data["Amount"]
        self.recipient = self.data["Recipient"]
        self.sender = self.data["Sender"]


class user_data:

    def __init__(self, data):
        self.data = data


    def diction(self):
        """Returns all transactions"""
        return self.data


    def tokens(self):
        """Returns all tokens"""
        return self.data.keys()


    def token(self, token):
        """Searches by token"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the token is the one that's being searched
            if item == str(token):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def time(self, time):
        """Searches by time"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the 'Time' is equal to the one searched
            if info['Time'] == str(time):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def sender(self, sender):
        """Searches by sender"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the sender's the one being searched
            if info['Sender'] == str(sender):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def recipient(self, recipient):
        """Searches by recipient"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the recipient's the one being searched
            if info['Recipient'] == str(recipient):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def amount(self, amount):
        """Searches by amount"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the amount is the one being searched
            if info['Amount'] == str(amount):
                # It is, so return the transaction data of it
                return transaction_data(info, item)



class transactions:

    def __init__(self):
        # Gets response from transactions.json on the masterserver
        response = requests.get(TRANSACTIONS_URL, data=None)
        # Checks whether data has been sent (http-code = ok)
        if response.status_code == 200:
            # The response was "ok" so get data from response body (content)
            data1 = (response.content.decode())
        else:
            # The response was anything als than "ok", so report the error
            raise ConnectionError("Could not connect to server")

        try:
            # Tries to convert the received data into a dictionary.
            self.data = ast.literal_eval(data1)
        except:
            # The convertion failed, so report the error
            raise Exception("Data cant be converted into a dict. please retry")
        # No username has been specified up until this point, so set it to "None"
        self.username = None


    def total_transactions(self):
        # Returns the amount of transactions
        return len(self.data)


    def print(self):
        # Iterates through every transactions
        for trans in self.data.keys():
            # and prints it
            print(self.data[trans])


    def all(self):
        # Creates a userdata-instance based on the data provided
        return user_data(data=self.data)

    def all_time_transacted(self):
        # returnes the all time transacted amount

        transactions = self.all()

        transactions_token = list(transactions.tokens())

        total = 0

        for trans_token in transactions_token:
            total += float(transactions.token(trans_token).amount)

        return total


    def user_transactions(self, username=None):
        # Checks whether a 'valid' username was specified.
        if username != None:
            # It was, so set the class-variable to it
            self.username = username
        elif self.username == None:
            # The username was None, so print an 'error'
            raise ValueError("Please provide a username")

        sent = {}
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores the details of a transaction
            info = (self.data[trans])
            # And checks whether the 'Sender' was the specified user
            if info['Sender'] == self.username:
                # It was, so the info gets pushed to the 'sent' variable
                sent.update({trans: info})


        # return sent
        return user_data(data=sent)


    def user_transaction_qty(self, username=None):
        """Gets total amount of user sends"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Counts the transactions sent by the user
        count = 0
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores the details in this variable
            info = (self.data[trans])
            # And then checks whether the 'Sender' is the user specified
            if info['Sender'] == self.username:
                # It is the user specified, so add 1 to the transaction-counter
                count += 1

        return count


    def user_reciepts(self, username=None):
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores the received transactions
        sent = {}
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores their details in this variable
            info = (self.data[trans])
            # Checks whether the 'Recipient' is the user specified
            if info['Recipient'] == self.username:
                # It is the user, so push the info to the variable
                sent.update({trans: info})

        # Returns userdata based on received transactions
        return user_data(data=sent)


    def user_reciept_qty(self, username=None):
        """Gets total amount of user reciepts"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Counts how many transactions have been received
        count = 0
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores their details in this variable
            info = (self.data[trans])
            # Checks whether the 'Recipient' is the user specified
            if info['Recipient'] == self.username:
                # It is the user, so add 1 to the receive-counter
                count += 1

        # Return the amount of received transactions.
        return count


    def total_duco_sent(self, username=None):
        """Gets total amount of duco sent by user"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores how many ducos the user has sent
        total = 0

        # Gets the transactions the user has sent
        transactions = self.user_transactions()
        # Iterates through the sent transactions
        for token in transactions.tokens():
            # Gets the transaction details
            info = transactions.token(token=token)
            # Adds the sent amount to the total
            total += float(info.amount)

        # Returns the total duco sent
        return total


    def total_duco_received(self, username=None):
        """Gets total amount of duco recieved by user"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores how many ducos the user has received
        total = 0

        # Gets every transaction the user has received
        transactions = self.user_reciepts()
        # Iterates through the received transactions
        for token in transactions.tokens():
            # Gets the transaction details
            info = transactions.token(token=token)
            # Adds the received amount to the total
            total += float(info.amount)

        # Returns the total amount of ducos received
        return total



#====================================# Duco Api #====================================#

def get_duco_price():
    """
    A function for getting the current price of DUCO
    """
    api_response = get(API_URL)
    if api_response.status_code == 200:
        duco_price = round(api_response.json()["Duco price"], 6)
    else:
        duco_price = .003
    return duco_price


def start_duco_price_timer(tkinter_label=None, interval=15):
    """
    A function that starts a timer with a specified interval and updates duco_price variable with the current price.
    Arguments:
        tkinter_label: Tkinter label that will be updated with the price (optional)
        interval: Interval between price updates (default: 15)
    """
    global duco_price
    api_response = get(API_URL)
    if api_response.status_code == 200:
        duco_price = round(api_response.json()["Duco price"], 6)
    else:
        duco_price = .003
    if tkinter_label:
        tkinter_label.set(f"1 Duco = ${duco_price}")
    Timer(interval, start_duco_price_timer, args=(tkinter_label, interval)).start()


class api_actions:
    """
    A class that provides an interface for interacting with the DUCO server
    """
    def __init__(self):
        """
        A class constructor that initiates the connection with the server.
        """
        serverinfo = get(SERVER_URL).text.splitlines()
        self.pool_address = serverinfo[0]
        self.pool_port = int(serverinfo[1])
        self.sock = socket.socket()
        self.sock.connect((self.pool_address, self.pool_port))
        self.sock.recv(3)
        self.username = None
        self.password = None

    def register(self, username, password, email):
        """
        A function for registering an account
        """
        self.sock.send(f"REGI,{username},{password},{email}".encode())
        register_result = decode_response(self.sock.recv(128))
        if 'NO' in register_result:
            raise Exception(register_result[1])
        return register_result

    def Pools(self):
        """
        A function for getting a list of pools
        """
        self.sock.send("POOLList".encode())
        register_result = decode_response(self.sock.recv(1024))
        return register_result

    def login(self, username, password):
        """
        A function for logging into an account
        """
        self.username = username
        self.password = password

        self.sock.send(f"LOGI,{username},{password}".encode())
        login_result = decode_response(self.sock.recv(64))

        if 'NO' in login_result:
            raise Exception(login_result[1])

        return login_result

    def logout(self):
        """
        A function for disconnecting from the server
        """
        self.sock.close()

    def balance(self):
        """
        A function for getting account balance
        """
        if not self.password or not self.username:
            raise Exception("User not logged in")
        self.sock.send("BALA".encode())
        user_balance = self.sock.recv(1024).decode()
        return user_balance

    def transfer(self, recipient_username, amount):
        """
        A function for transfering balance between two accounts
        """
        if not self.password or not self.username:
            raise Exception("User not logged in")
        self.sock.send(f"SEND,-,{recipient_username},{amount}".encode())
        transfer_response = self.sock.recv(128).decode()
        return transfer_response

    def getTransactions(self, amount):
        """
        A function for get last (amount) of transactions
        """
        if not self.password or not self.username:
            raise Exception("User not logged in")
        self.sock.send(f"GTXL,{self.username},{amount}".encode())
        transactions = self.sock.recv(1024).decode()
        return json.loads(json.dumps(transactions))

    def reset_pass(self, old_password, new_password):
        """
        A function for resetting the password of an account
        """
        if not self.password or not self.username:
            raise Exception("User not logged in")
        self.sock.send(f"CHGP,{old_password},{new_password}".encode())
        reset_password_response = self.sock.recv(128).decode()
        return reset_password_response

    def close(self):
        """
        A function for disconnecting from the server
        """
        self.sock.close()


#====================================# Duco Miner #====================================#

class miner:

    def __init__(self):
        self.username = None
        self.UseLowerDiff = True
        self.stopVar = False
        self.workers = 1
        self.last_job = {}



    def start(self, username=None, workers=None):
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        if workers != None:
            self.workers = int(workers)

        for worker in range(self.workers):
            x = threading.Thread(target=self.worker)
            x.start()


    def stop(self):
        self.stopVar = True


    def worker(self): # Mining section\
        soc = socket.socket()
        with urllib.request.urlopen(SERVER_URL) as content:
            # Read content and split into lines
            content = content.read().decode().splitlines()

        # Line 1 = IP
        pool_address = content[0]
        # Line 2 = port
        pool_port = content[1]

        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)

        while True:
            if self.stopVar == True:
                print("Stopping Worker")
                break
            if self.UseLowerDiff:
                # Send job request for lower diff
                soc.send(bytes(
                    "JOB,"
                    + str(self.username)
                    + ",MEDIUM",
                    encoding="utf8"))
            else:
                # Send job request
                soc.send(bytes(
                    "JOB,"
                    + str(self.username),
                    encoding="utf8"))

            # Receive work
            job = soc.recv(1024).decode().rstrip("\n")
            # Split received data to job and difficulty
            job = job.split(",")
            difficulty = job[2]

            hashingStartTime = time.time()
            for result in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                ducos1 = hashlib.sha1(
                    str(
                        job[0]
                        + str(result)
                    ).encode("utf-8")).hexdigest()

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
                        miner_q.put({'Status': "Accepted share",
                                        'Result': result,
                                        "Hashrate": int(hashrate/1000),
                                        "Difficulty": difficulty})
                        # print("Accepted share",
                        #       result,
                        #       "Hashrate",
                        #       int(hashrate/1000),
                        #       "kH/s",
                        #       "Difficulty",
                        #       difficulty)
                        break
                    # If result was incorrect
                    elif feedback == "BAD":
                        miner_q.put({'Status': "Rejected share",
                                        'Result': result,
                                        "Hashrate": int(hashrate/1000),
                                        "Difficulty": difficulty})
                        # print("Rejected share",
                        #       result,
                        #       "Hashrate",
                        #       int(hashrate/1000),
                        #       "kH/s",
                        #       "Difficulty",
                        #       difficulty)
                        break


if __name__ == '__main__':
    print(transactions().all_time_transacted())
    # miner_class = miner()

    # miner_class.start(username="connorhess")

    # for i in range(10):
    #     print(miner_q.get())
    #     time.sleep(1)

    # miner_class.stop()
