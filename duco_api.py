##########################################
# Duino-Coin Api Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
from urllib.request import urlopen
import socket
from requests import get
from json import loads
from threading import Timer

socket.setdefaulttimeout(10)
ducofiat = .003


def decode_soc(rec):
    response = rec.decode("utf8")
    response = response.split(",")
    return response


def decode_soc_no_utf(rec):
    response = rec.decode()
    response = response.split(",")
    return response


def GetDucoPrice():
    global ducofiat
    jsonapi = get("http://163.172.179.54/api.json", data = None)
    if jsonapi.status_code == 200:
        content = jsonapi.content.decode()
        contentjson = loads(content)
        ducofiat = round(float(contentjson["Duco price"]), 6)
    else:
        ducofiat = .003
    Timer(15, GetDucoPrice).start()


class api_actions():

    def __init__(self):
        """initiate connection with socket server"""
        with urlopen("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt") as self.content:
            self.content = self.content.read().decode().splitlines()
            self.pool_address = self.content[0]
            self.pool_port = int(self.content[1])

        socket.setdefaulttimeout(10)
        self.sock = socket.socket()
        self.sock.connect((self.pool_address, self.pool_port))
        self.sock.recv(3)
        self.username = None
        self.password = None


    def register(self, username, password, email, send_email=False):
        """Register User"""
        self.sock.send(bytes(f"REGI,{str(username)},{str(password)},{str(email)}", encoding="utf8"))
        self.register_result = decode_soc(self.sock.recv(128))
        if 'NO' in self.register_result:
            raise Exception(self.register_result[1])
        return self.register_result

    def login(self, username, password):
        """Login User"""
        self.username = username
        self.password = password

        self.sock.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
        self.login_result = decode_soc(self.sock.recv(64))

        if 'NO' in self.login_result:
            raise Exception(self.login_result[1])

        return self.login_result

    def logout(self):
        """Logout user/close connection"""
        self.sock.close()

    def balance(self):
        """Get user balance"""
        if self.password == None or self.username == None:
            raise Exception("User not logged in")
        self.sock.send(bytes("BALA", encoding="utf8"))
        self.user_balance = self.sock.recv(1024).decode()
        return self.user_balance


    def transfer(self, recipient_username, amount):
        """transfer duco from current user to target user"""
        if self.password == None or self.username == None:
            raise Exception("User not logged in")
        self.sock.send(bytes(f"SEND,-,{str(recipient_username)},{str(amount)}", encoding="utf8"))
        self.transfer_response = self.sock.recv(128).decode()
        return self.transfer_response

    def reset_pass(self, old_password, new_password):
        """resets current user's password"""
        if self.password == None or self.username == None:
            raise Exception("User not logged in")
        self.sock.send(bytes(f"CHGP,{str(old_password)},{str(new_password)}", encoding="utf8"))
        self.reset_password_response = self.sock.recv(128).decode("utf8")
        return self.reset_password_response

    def close(self):
        """closes the connection"""
        self.sock.close()

