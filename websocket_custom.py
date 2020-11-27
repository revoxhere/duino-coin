##########################################
# Duino-Coin Api Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
from urllib.request import urlopen, urlretrieve
import socket, sys
import datetime
from base64 import b64encode, b64decode
from requests import get
from json import loads
from threading import Timer

socket.setdefaulttimeout(10)

with urlopen("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt") as content:
    content = content.read().decode().splitlines()
    pool_address = content[0]
    pool_port = content[1]
    server_address = {'address': pool_address, 'port': pool_port}



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


def init_socket():
    global sock
    sock = socket.socket()
    sock.connect((server_address['address'], int(server_address['port'])))
    sock.recv(3)
    return sock





def register(username, password, email, send_email=False):
    try:
        sock.send(bytes(f"REGI,{str(username)},{str(password)},{str(email)}", encoding="utf8"))
        result = decode_soc(sock.recv(128))
    except Exception as e:
        init_socket()
        sock.send(bytes(f"REGI,{str(username)},{str(password)},{str(email)}", encoding="utf8"))
        result = decode_soc(sock.recv(128))
        sock.close()
    return result



def login(username, password):
    try:
        sock.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
        result = decode_soc(sock.recv(64))
    except Exception as e:
        init_socket()
        sock.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
        result = decode_soc(sock.recv(64))
        sock.close()
    return result



def balance():
    try:
        sock.send(bytes("BALA", encoding="utf8"))
        user_balance = sock.recv(1024).decode()
    except Exception as e:
        raise Exception("Socket not initialized please add 'init_socket' to your code")

    return user_balance




def transfer(recipient_username, amount):
    try:
        sock.send(bytes(f"SEND,-,{str(recipient_username)},{str(amount)}", encoding="utf8"))
        response = sock.recv(128).decode()
    except Exception as e:
        raise Exception("Socket not initialized please add 'init_socket' to your code")

    return response



def reset_pass(old_password, new_password):
    try:
        sock.send(bytes(f"CHGP,{str(oldpasswordS)},{str(newpasswordS)}", encoding="utf8"))
        response = sock.recv(128).decode("utf8")
    except Exception as e:
        raise Exception("Socket not initialized please add 'init_socket' to your code")

    return response


# def stat(username):
#     try:
#         sock.send(bytes(f"STAT,{str(username)}", encoding="utf8"))
#         response = sock.recv(1024).decode()
#     except Exception as e:
#         raise Exception("Socket not initialized please add 'init_socket' to your code")

#     return response

