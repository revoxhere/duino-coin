##########################################
# Duino-Coin API Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################
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

#====================================# Endpoints #====================================#

class Endpoints:
    api = 'https://server.duinocoin.com/api.json'
    transactions = 'https://server.duinocoin.com/transactions.json'
    server = 'https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt'


#====================================# Duco Transactions #====================================#

class Transaction:
    """
    The individual data representing a transaction
    """

    def __init__(self, **kwargs):
        self.date = kwargs['Date']
        self.time = kwargs['Time']
        self.recipient = kwargs['Recipient']
        self.sender = kwargs['Sender']
        self.amount = kwargs['Amount']
        self.hash = kwargs['Hash']
        self.memo = kwargs['Memo']


class Transactions:

    def __init__(self):
        self.data = None
        self.username = None
        self._get()

    def _get(self):
        try:
            response = requests.get(Endpoints.transactions)
        except Exception as e:
            raise ConnectionError(f'Could not get transactions: {e}')

        try:
            self.data = json.loads(response.text)
        except Exception as e:
            raise e

        return self.data

    def update(self):
        self.data = None
        return self.all()

    def all(self):
        if not self.data:
            self._get()

        # Creates a userdata-instance based on the data provided
        return [Transaction(**data) for data in self.data.values()]

    def total_transactions(self):
        # Returns the amount of transactions
        return len(self.all())

    def all_time_transacted(self):
        # returnes the all time transacted amount
        return sum([t.amount for t in self.all()])

    def user_transactions_sent(self, username=None):
        # Checks whether a 'valid' username was specified.
        if username != None:
            # It was, so set the class-variable to it
            self.username = username
        elif self.username == None:
            # The username was None, so print an 'error'
            raise ValueError('Please provide a username')

        return [t for t in self.all() if t.sender == self.username]

    def total_user_transactions_sent(self, username=None):
        '''Gets total amount of user sends'''
        return len(self.user_transactions_sent(username=username))

    def user_transactions_received(self, username=None):
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError('Please provide a username')

        return [t for t in self.all() if t.recipient == self.username]

    def total_user_transactions_received(self, username=None):
        '''Gets total amount of user reciepts'''
        return len(self.user_transactions_received(username=username))


    def total_duco_sent(self, username=None):
        '''Gets total amount of duco sent by user'''
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError('Please provide a username')

        return sum([t.amount for t in self.user_transactions_sent((username))])


    def total_duco_received(self, username=None):
        '''Gets total amount of duco recieved by user'''
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError('Please provide a username')

        return sum([t.amount for t in self.user_transactions_received((username))])


#====================================# Duco Api #====================================#
class Wallet:
    '''
    A class that provides an interface for interacting with the DUCO server
    '''
    def __init__(self):
        '''
        A class constructor that initiates the connection with the server.
        '''
        self.username = None
        self.password = None
        self.transactions = None

        serverinfo = requests.get(Endpoints.server).text.splitlines()
        self.pool_address = serverinfo[0]
        self.pool_port = int(serverinfo[1])

        socket.setdefaulttimeout(10)
        self._connect_socket()

    def _connect_socket(self):
        self.sock = socket.socket()
        self.sock.connect((self.pool_address, self.pool_port))
        self.sock.recv(3)

        if self.username and self.password:
            self.login(self.username, self.password)

    def _decode_response(self, rec):
        return rec.decode().split(',')

    def register(self, username, password, email):
        '''
        A function for registering an account
        '''
        self.sock.send(f'REGI,{username},{password},{email}'.encode())
        register_result = self._decode_response(self.sock.recv(128))
        if 'NO' in register_result:
            raise Exception(register_result[1])
        return register_result

    def login(self, username, password):
        '''
        A function for logging into an account
        '''
        self.username = username
        self.password = password

        self.sock.send(f'LOGI,{username},{password}'.encode())
        login_result = self._decode_response(self.sock.recv(64))

        if 'NO' in login_result:
            raise Exception(login_result[1])

        return login_result

    def logout(self):
        '''
        A function for disconnecting from the server
        '''
        self.close()

    def get_duco_price(self):
        '''
        A function for getting the current price of DUCO
        '''
        try:
            api_response = requests.get(Endpoints.api)
        except Exception as e:
            raise Exception(f'Error getting duco price: {e}')
        
        price_json = json.loads(api_response.text)
        return round(price_json.get('Duco price', 0.0), 6)

    def get_balance(self):
        '''
        A function for getting account balance
        '''
        self._connect_socket()

        self.sock.send('BALA'.encode())
        user_balance = self.sock.recv(1024).decode()
        return user_balance

    def transfer(self, recipient_username, amount):
        '''
        A function for transfering balance between two accounts
        '''
        self._connect_socket()

        self.sock.send(f'SEND,-,{recipient_username},{amount}'.encode())
        transfer_response = self.sock.recv(128).decode()
        return transfer_response

    def get_transactions(self):
        '''
        A function for get last (amount) of transactions
        '''
        self.transactions = Transactions()
        return self.transactions

    def reset_pass(self, old_password, new_password):
        '''
        A function for resetting the password of an account
        '''
        self._connect_socket()

        self.sock.send(f'CHGP,{old_password},{new_password}'.encode())
        reset_password_response = self.sock.recv(128).decode()
        return reset_password_response

    def close(self):
        '''
        A function for disconnecting from the server
        '''
        self.sock.close()


#====================================# Duco Miner #====================================#

class Miner:

    def __init__(self, username, num_workers, diff):
        self.username = username
        self.num_workers = num_workers
        self.diff = diff
        self.use_lower_diff = True
        self.should_stop = False
        self.last_job = {}
        self.miner_q = queue.Queue()

    def start(self):
        for _ in range(self.num_workers):
            x = threading.Thread(target=self.worker)
            x.start()

    def stop(self):
        self.should_stop = True

    def get_q(self):
        return self.miner_q.get()

    def worker(self): # Mining section\
        soc = socket.socket()
        
        try:
            serverinfo = requests.get(Endpoints.server).text.splitlines()
        except Exception as e:
            print(f'Cannot get server details: {e}')

        pool_address = serverinfo[0]
        pool_port = int(serverinfo[1])

        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print('Server is on version', server_version)

        while True:
            
            if self.should_stop == True:
                print('Stopping Worker')
                break
            
            # Send job request
            soc.sendall(bytes(
                'JOB,'
                + str(self.username)
                +','
                + self.diff,
                encoding='utf8'))

            # Receive work
            job = soc.recv(1024).decode().rstrip('\n')
            # Split received data to job and difficulty
            job = job.split(',')
            difficulty = job[2]

            hashingStartTime = time.time()
            for result in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                ducos1 = hashlib.sha1(
                    str(
                        job[0]
                        + str(result)
                    ).encode('utf-8')).hexdigest()

                # If hash is even with expected hash result
                if job[1] == ducos1:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = result / timeDifference

                    # Send numeric result to the server
                    soc.send(bytes(
                        str(result)
                        + ','
                        + str(hashrate)
                        + ',Minimal_PC_Miner',
                        encoding='utf8'))

                    # Get feedback about the result
                    feedback = soc.recv(1024).decode().rstrip('\n')
                    # If result was good
                    if feedback == 'GOOD':
                        self.miner_q.put({'Status': 'Accepted share',
                                        'Result': result,
                                        'Hashrate': int(hashrate/1000),
                                        'Difficulty': difficulty})
                        print('Accepted share',
                              result,
                              'Hashrate',
                              int(hashrate/1000),
                              'kH/s',
                              'Difficulty',
                              difficulty)
                        break
                    # If result was incorrect
                    elif feedback == 'BAD':
                        self.miner_q.put({'Status': 'Rejected share',
                                        'Result': result,
                                        'Hashrate': int(hashrate/1000),
                                        'Difficulty': difficulty})
                        print('Rejected share',
                              result,
                              'Hashrate',
                              int(hashrate/1000),
                              'kH/s',
                              'Difficulty',
                              difficulty)
                        break

        soc.close()
        return

if __name__ == '__main__':
    # print(Transactions().all_time_transacted())
    miner = Miner('dansinclair25', 10, 'LOW')

    miner.start()
    # miner.start(username='connorhess')

    while True:
        try:
            print(miner.get_q())
        except KeyboardInterrupt:
            miner.stop()
