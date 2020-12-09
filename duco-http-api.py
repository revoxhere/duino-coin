import flask, requests

# user  variables
faucetuser = "username"
faucetpasswd = "password"
claimamount = int(10)
enable_faucet = False
api_port = 5000


#only a program variable
users = [faucetuser]


def login(username, password): 
    #gets server ip
    import requests, socket
    server = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt").text # requests IP and port
    splitted = str.splitlines(server) # treats response
    ip = splitted[0] # isolates IP
    port = splitted[1] # isolates port
    ipport = str(ip)+str(":")+str(port) # ip:port, useful for debugging

    #opens socket
    global s
    s = socket.socket() # creates socket
    s.connect((str(ip), int(port))) # connects socket
    print("DUCO server is running", s.recv(64).decode(), "version") # prints version
    tosend = str("LOGI,") + str(username) + str(",") + str(password) # fetches credentials
    s.send(bytes(tosend, encoding="utf8")) # sends credentials
    loginfeedback = s.recv(64).decode()
    print("Server response :", loginfeedback)
    global loggedin
    if loginfeedback == "OK":
        loggedin = True
        print("Successfully logged in ! ")
    else :
        loggedin = False
        print("Login failed")


def sendfunds(recipient, amount):
    log_all = True
    if loggedin:
        if log_all:
            print("Sent", amount, "DUCO to", recipient)
        s.send(bytes("BALA", encoding="utf8"))
        balance = s.recv(64).decode()
        if float(balance) >= float(amount):
            s.send(bytes(f"SEND,-,{str(recipient)},{str(amount)}", encoding="utf8"))
            global sendfundsfeedback
            sendfundsfeedback = s.recv(128).decode()
            print(sendfundsfeedback)
        else :
            print("Didn't send", amount, "DUCO to", recipient, "\nCause : not enough balance")
    else :
        print("Didn't send", amount, "DUCO to", recipient, "\nCause : not logged in")

def getbalance():
    if loggedin:
        s.send(bytes("BALA", encoding="utf8"))
        global balance
        balance = s.recv(64).decode()
        print("You has", balance, "DUCO")


def register(username, password, email):
    global s
    import requests, socket
    #gets server ip
    server = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt").text # requests IP and port
    splitted = str.splitlines(server) # treats response
    ip = splitted[0] # isolates IP
    port = splitted[1] # isolates port
    ipport = str(ip)+str(":")+str(port) # ip:port, useful for debugging

    #opens socket
    s = socket.socket() # creates socket
    s.connect((str(ip), int(port))) # connects socket
    print("DUCO server is running", s.recv(64).decode(), "version") # prints version
    
    #sends register informations
    s.send(bytes(f"REGI,{str(username)},{str(password)},{str(email)}", encoding="utf8")) # sends register details to server
    registerfeedback = s.recv(64).decode() # receives register feedback
    global loggedin
    if registerfeedback == "OK":
        loggedin = True
    else:
        loggedin = False
        print(registerfeedback) # prints it on screen


def logout():
    s.close()

print("DUCO functions successfully loaded ! ")

app = flask.Flask(__name__)
app.config["DEBUG"] = True





@app.route('/faucet/<user>', methods=['GET'])
def faucet(user):
    if enable_faucet:
        login(faucetuser, faucetpasswd)
        print("")
        if loggedin:
            getbalance()
            if float(balance) < float(claimamount):
                return "Unsufficient faucet balance"
            else:
                if user in users:
                    return "Already claimed ! "
                else:
                    getbalance()
                    users.append(user)
                    sendfunds(user, claimamount)
                    toreturn = str("Sent ") +str(claimamount) +str(" DUCO to ") +str(user)
                    getbalance()
                    return toreturn
    logout()



@app.route("/wallet/login/<user>/<password>")
def httplogin(user, password):
    login(user, password)
    if loggedin:
        return "OK"
    else:
        return "error"
    logout()

@app.route("/faucetinfo")
def faucetinfo():
    if enable_faucet:
        login(faucetuser, faucetpasswd)
        if loggedin:
            getbalance()
            toreturn = str("Faucet balance : ") +str(balance)
            return toreturn
        else:
            return "error"
    else:
        return "Faucet isn't enabled"
    

@app.route("/wallet/getbalance/<user>/<password>")
def httpgetbalance(user, password):
    login(user, password)
    if loggedin:
        getbalance()
        return balance
    else:
        return "error"
    logout()

@app.route("/wallet/sendtx/<user>/<password>/<recipient>/<amount>")
def sendtx(user, password, recipient, amount):
    login(user, password)
    if loggedin:
        sendfunds(recipient, amount)
        return sendfundsfeedback
    else:
        return "error"

@app.route("/wallet/register/<name>/<passwd>/<email>")
def httpregister(name, passwd, email):
    register(name, passwd, email)
    if loggedin:
        return "OK"
    else:
        return registerfeedback
    


app.run(host='0.0.0.0', port=api_port)