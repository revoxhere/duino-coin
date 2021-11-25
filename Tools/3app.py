### Importing section
import random as r            
import socket
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, request, render_template, jsonify
import requests
import json
from flask import Flask
from flask import request
import random
import time
import socket
import urllib.request as urllib2
from flask_xcaptcha import XCaptcha
### Importing section
app = Flask(__name__)
from celery import Celery
from werkzeug.middleware.proxy_fix import ProxyFix
import asyncio
from flask import copy_current_request_context

from threading import Thread

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

### Defining name file as app
### Defining name file as app

### Different system of visiting website
limiter = Limiter(app, key_func=get_remote_address)
### Different system of visiting website

### Defining variables that u see after POST(typing username) request

### Defining variables that u see after POST(typing username) request

### Defining variables that u see after POST(typing username) request

# Variables with faucet wallet details
faucetUsername = 'Faucet_Furimos69'
faucetPassword = 'tranzystor'
msgToSend = 'Furim_Faucet' # Message to send with ducos
#    site_key="c20688f0-f7c7-4605-8510-37f07723bbba",
#     secret_key="0x9Dccd726Ae8AecBdC939A21A6eCE5ad987EEEE0D",
xcaptcha = XCaptcha(
    site_key="c20688f0-f7c7-4605-8510-37f07723bbba",
    secret_key="0x9Dccd726Ae8AecBdC939A21A6eCE5ad987EEEE0D",
    verify_url="https://hcaptcha.com/siteverify",
    api_url="https://hcaptcha.com/1/api.js",
    div_class="h-captcha"
)

class Compute(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.request = request

@app.route("/")
def homepage():
    return render_template("form.html")

response = ""

duco_username = ""
hcaptcha = ""


class Compute(Thread):
    def __init__(self, request):
        Thread.__init__(self)
        self.request = request

    def run(self):
        print("start")
        print(self.request)
        print("Sending duco to {}".format(duco_username))

        time.sleep(30)
        response_balance = requests.get('https://server.duinocoin.com/balances/{}'.format(faucetUsername))
        normalized_response_balance = response_balance.text
        y = json.loads(response_balance.text)
        not_splitted_var = y["result"]["balance"]
        print(not_splitted_var)
        number1 = float(0.01)
        number2 = float(not_splitted_var)
        percent = (number1*number2)/100
        print(percent)  
        response = requests.get('https://server.duinocoin.com/transaction/?username={}&password={}&recipient={}&amount={}&memo={}'.format(faucetUsername, faucetPassword, duco_username, percent, msgToSend))
        print(response.text)
        y = json.loads(response.text)
        not_splitted_var = y["result"]
        splitted_var = not_splitted_var.split(",")
        hash_of_transaction = '''<a style="color:#f5cd79; font-size:40px" href="https://server.duinocoin.com/transactions/{}">🐼</a>'''.format(splitted_var[2])
        print("there is ma boi hash: ", splitted_var[2])
        # return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction) 






@app.route("/giveMeDucos", methods=["POST"])
@limiter.limit("1/hour") 
def submit():
#            CAPTCHA_SECRET_KEY = "0x9Dccd726Ae8AecBdC939A21A6eCE5ad987EEEE0D"
            global duco_username
            CAPTCHA_SECRET_KEY = "0x9Dccd726Ae8AecBdC939A21A6eCE5ad987EEEE0D"
            duco_username = request.form.get("duco_usr")
            hcaptcha = request.form.get("h-captcha-response")


            captcha = request.args.get('captcha', None)
            postdata = {'secret': CAPTCHA_SECRET_KEY,
                        'response': hcaptcha}
            captcha_data = requests.post(
                    'https://hcaptcha.com/siteverify', data=postdata).json()
            if not captcha_data["success"]:
                return ("Incorrect captcha") 
            else:
                thread_a = Compute(request.__copy__())
                thread_a.start()
                return render_template("ducosent.html"), 200

    # #CAPTCHA_SECRET_KEY = "0x9Dccd726Ae8AecBdC939A21A6eCE5ad987EEEE0D"
    # CAPTCHA_SECRET_KEY = "0x0000000000000000000000000000000000000000"
    # duco_username = request.form.get('duco_usr')
    # hcaptcha = request.form.get('h-captcha-response')
    # print(duco_username)
    # captcha = request.args.get('captcha', None)
    # postdata = {'secret': CAPTCHA_SECRET_KEY,
    #             'response': hcaptcha}
    # captcha_data = requests.post(
    #         'https://hcaptcha.com/siteverify', data=postdata).json()
    # if not captcha_data["success"]:
    #     return ("Incorrect captcha") 
    # else:
    #     ip = request.environ.get('REMOTE_ADDR')    
    #     json_ze_strony = requests.get("http://daiman.nl/check.php?ip={}".format(ip)).json()
    #     json_api_username_var = json_ze_strony["code"]
    #     print(json_ze_strony)
    #     print(json_api_username_var)    
    #     str_json_api_username_var = (str(json_api_username_var))
    #     if str_json_api_username_var == "100":    
    #         return render_template("429.html")
    #     else:  
    #         f = open("connect.txt", "r")
    #         connection_var =  f.read()

    #         if connection_var == "json":
    #             response_balance = requests.get('https://server.duinocoin.com/balances/{}'.format(faucetUsername))
    #             normalized_response_balance = response_balance.text
    #             y = json.loads(response_balance.text)
    #             not_splitted_var = y["result"]["balance"]
    #             print(not_splitted_var)
    #             number1 = float(0.01)
    #             number2 = float(not_splitted_var)
    #             percent = (number1*number2)/100
    #             print(percent)
    #             response = requests.get('https://server.duinocoin.com/transaction/?username={}&password={}&recipient={}&amount={}&memo={}'.format(faucetUsername, faucetPassword, duco_username, percent, msgToSend))
    #             print(response.text)
    #             y = json.loads(response.text)
    #             not_splitted_var = y["result"]
    #             splitted_var = not_splitted_var.split(",")
    #             hash_of_transaction = '''<a style="color:#f5cd79; font-size:40px" href="https://server.duinocoin.com/transactions/{}">🐼</a>'''.format(splitted_var[2])
    #             print("there is ma boi hash: ", splitted_var[2])
    #             return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction) 


    #         if connection_var == "port0":
    #             server = ("server.duinocoin.com", 2811)
    #             soc = socket.socket() 
    #             soc.connect(server) 
    #             version = soc.recv(16) 
    #             soc.send(bytes("LOGI,{},{}".format(faucetUsername, faucetPassword),encoding="utf8"))
    #             pong = soc.recv(32) 
    #             soc.send(bytes("BALA,Faucet_Furimos69",encoding="utf8"))
    #             pong0 = soc.recv(32) 
    #             pong0d = pong0.decode('utf-8') 
    #             number1 = float(0.01)
    #             number2 = float(pong0d)
    #             percent = (number1*number2)/100
    #             print(percent)
    #             soc.send(bytes("SEND,Furim_Faucet,{},{}".format(first_name, percent), encoding="utf8")) 
    #             pong1 = soc.recv(256) 
    #             pong1d = pong1.decode('utf-8') 
    #             print(version) 
    #             print(pong)
    #             print(pong0d) 
    #             print(pong1d) 
    #             hash_of_transaction_not_arrayed69 = pong1d.split(",")
    #             hash_of_transaction69 = hash_of_transaction_not_arrayed69[2]
    #             print(hash_of_transaction69)
    #             real_hash_of_transaction = '''{}'''.format(hash_of_transaction69)
    #             print("there is ma boi hash: ", hash_of_transaction69)
    #             return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction69) 

    #         if connection_var == "port1":
    #             server = ("server.duinocoin.com", 2812)
    #             soc = socket.socket() 
    #             soc.connect(server) 
    #             version = soc.recv(16) 
    #             soc.send(bytes("LOGI,{},{}".format(faucetUsername, faucetPassword),encoding="utf8"))
    #             pong = soc.recv(32) 
    #             soc.send(bytes("BALA,Faucet_Furimos69",encoding="utf8"))
    #             pong0 = soc.recv(32) 
    #             pong0d = pong0.decode('utf-8') 
    #             number1 = float(0.01)
    #             number2 = float(pong0d)
    #             percent = (number1*number2)/100
    #             print(percent)
    #             soc.send(bytes("SEND,Furim_Faucet,{},{}".format(first_name, percent), encoding="utf8")) 
    #             pong1 = soc.recv(256) 
    #             pong1d = pong1.decode('utf-8') 
    #             print(version) 
    #             print(pong)
    #             print(pong0d) 
    #             print(pong1d) 
    #             hash_of_transaction_not_arrayed69 = pong1d.split(",")
    #             hash_of_transaction69 = hash_of_transaction_not_arrayed69[2]
    #             print(hash_of_transaction69)
    #             hash_of_transaction = '''<a style="color:#f5cd79; font-size:40px" href="https://server.duinocoin.com/transactions/{}">🐼</a>'''.format(hash_of_transaction69)
    #             real_hash_of_transaction = '''{}'''.format(hash_of_transaction69)
    #             print("there is ma boi hash: ", hash_of_transaction69)
    #             return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction69) 

    #         if connection_var == "port2":
    #             server = ("server.duinocoin.com", 2813)
    #             soc = socket.socket() 
    #             soc.connect(server) 
    #             version = soc.recv(16) 
    #             soc.send(bytes("LOGI,{},{}".format(faucetUsername, faucetPassword),encoding="utf8"))
    #             pong = soc.recv(32) 
    #             soc.send(bytes("BALA,Faucet_Furimos69",encoding="utf8"))
    #             pong0 = soc.recv(32) 
    #             pong0d = pong0.decode('utf-8') 
    #             number1 = float(0.01)
    #             number2 = float(pong0d)
    #             percent = (number1*number2)/100
    #             print(percent)
    #             soc.send(bytes("SEND,Furim_Faucet,{},{}".format(first_name, percent), encoding="utf8")) 
    #             pong1 = soc.recv(256) 
    #             pong1d = pong1.decode('utf-8') 
    #             print(version) 
    #             print(pong)
    #             print(pong0d) 
    #             print(pong1d) 
    #             hash_of_transaction_not_arrayed69 = pong1d.split(",")
    #             hash_of_transaction69 = hash_of_transaction_not_arrayed69[2]
    #             print(hash_of_transaction69)
    #             hash_of_transaction = '''<a style="color:#f5cd79; font-size:40px" href="https://server.duinocoin.com/transactions/{}">🐼</a>'''.format(hash_of_transaction69)
    #             real_hash_of_transaction = '''{}'''.format(hash_of_transaction69)
    #             print("there is ma boi hash: ", hash_of_transaction69)
    #             return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction69) 

    #         if connection_var == "port3":
    #             server = ("server.duinocoin.com", 2814)
    #             soc = socket.socket() 
    #             soc.connect(server) 
    #             version = soc.recv(16) 
    #             soc.send(bytes("LOGI,{},{}".format(faucetUsername, faucetPassword),encoding="utf8"))
    #             pong = soc.recv(32) 
    #             soc.send(bytes("BALA,Faucet_Furimos69",encoding="utf8"))
    #             pong0 = soc.recv(32) 
    #             pong0d = pong0.decode('utf-8') 
    #             number1 = float(0.01)
    #             number2 = float(pong0d)
    #             percent = (number1*number2)/100
    #             print(percent)
    #             soc.send(bytes("SEND,Furim_Faucet,{},{}".format(first_name, percent), encoding="utf8")) 
    #             pong1 = soc.recv(256) 
    #             pong1d = pong1.decode('utf-8') 
    #             print(version) 
    #             print(pong)
    #             print(pong0d) 
    #             print(pong1d) 
    #             hash_of_transaction_not_arrayed69 = pong1d.split(",")
    #             hash_of_transaction69 = hash_of_transaction_not_arrayed69[2]
    #             print(hash_of_transaction69)
    #             hash_of_transaction = '''<a style="color:#f5cd79; font-size:40px" href="https://server.duinocoin.com/transactions/{}">🐼</a>'''.format(hash_of_transaction69)
    #             real_hash_of_transaction = '''{}'''.format(hash_of_transaction69)
    #             print("there is ma boi hash: ", hash_of_transaction69)
    #             return '''<body style="background-color:#212121> <h1 style="color:white">Duco Sent</h1> {}</body>'''.format(hash_of_transaction69) 

@app.errorhandler(429)
def cooldown(e):
    return render_template("429.html"), 429 
# running app function  
if __name__=='__main__':
    app.jinja_env.cache = {}
    app.run()
# running app function

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=6996)
    app.run(threaded=True)

# running app/debuging function
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
# running app/debuging function
 
