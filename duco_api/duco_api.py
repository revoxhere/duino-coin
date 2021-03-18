##########################################
# Duino-Coin API Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################
import socket
from requests import get
from threading import Timer
import json

API_URL = "http://51.15.127.80/api.json"
SERVER_URL = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
duco_price = 0.003
socket.setdefaulttimeout(10)


def decode_response(rec):
    """
    Decodes a response from the server
    """
    return rec.decode().split(",")

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
