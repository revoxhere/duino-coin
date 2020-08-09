#!/usr/bin/env python3
##########################################
# Duino-Coin GUI Wallet (v1.6)
# https://github.com/revoxhere/duino-coin 
# Distributed under MIT license
# © Duino-Coin Community 2020
##########################################
import time, socket, sys, os, datetime, random, configparser, tkinter, getpass, platform, webbrowser, urllib.request, json, threading # Import libraries
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as st 
from pathlib import Path

try:
    import requests # Check if requests is installed
except:
    print("Requests is not installed. Install it with: python3 -m pip install requests.\nExiting in 15s.")
    time.sleep(15)
    os.exit(1)

# Default colors
colorA = "#23272a" #background
colorB = "#fafafa" #foreground
colorC = "#EEEEEE"
colorHighlight = "#FBC531" #ducogold - #FBC531
colorHighlight = "#FBC531" #ducogold - #FBC531
WalletResources = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
s = socket.socket()
balancecurrency = 0
balance = 0
background = ""
newbalance = 0
Updated = False
sending = 0
VER = "1.6" # Version number
resources = "Wallet_"+str(VER)+"_resources/"
pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP
themes = [
  ("Light"),
  ("Dark"),
]
currencies = [
  ("USD"),
  ("PLN"),
  ("RUB"),
  ("EUR"),
]

# Loading window
loadingScr = tkinter.Tk() #register window
loadingScr.resizable(False, False)
loadingScr.title('Loading...')
loadingScr.geometry("300x90")
try:
    loadingScr.iconbitmap(str(resources) + "Wallet_icon.ico")
except:
    pass # Icon won't work on linux
loadingScr.configure(background = str(colorA))

label = tkinter.Label(loadingScr, text = "Duino-Coin GUI Wallet", font=("Arial", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "LOADING", font=("Arial", 10, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "Configuring theme..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)
loadingScr.update()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def setTheme(event):
  global colorA, colorB, colorC, background, wallet

  config.read(str(resources) + "Wallet_config.cfg")
  username = config["wallet"]["username"]
  password = config["wallet"]["password"]
  currency = config["wallet"]["currency"]

  if event == "Light":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("0"),
              "currency": str(currency)}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    background = str(resources) + "Wallet_background_light.gif"
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)
    
  if event == "Dark":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("1"),
              "currency": str(currency)}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    background = str(resources) + "Wallet_background_dark.gif"
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)

def setCurrency(event):
  global currency, currencies, SETTINGS
  
  config.read(str(resources) + "Wallet_config.cfg")
  username = config["wallet"]["username"]
  password = config["wallet"]["password"]
  theme = config["wallet"]["theme"]

  if event == "USD":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str(theme),
              "currency": str("USD")}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)
    
  if event == "PLN":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str(theme),
              "currency": str("PLN")}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)
      
  if event == "RUB":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str(theme),
              "currency": str("RUB")}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.\n") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)

  if event == "EUR":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str(theme),
              "currency": str("EUR")}
    with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
      config.write(configfile)
    messagebox.showinfo("Information", "Wallet will be restarted to apply changes.\n") # Display info
    os.execl(sys.executable, sys.executable, *sys.argv)


def selectWindow(): # First-time launch window
    global window
    window = tkinter.Tk()
    window.geometry("355x190")
    window.resizable(False, False)
    try:
        window.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    window.title("Duino-Coin GUI Wallet ("+str(VER)+")")
    window.configure(background = str(colorA))
    
    tkinter.Label(window, text = "", bg = str(colorA), fg = str(colorB)).pack()     
    tkinter.Label(window, text = " Duino-Coin GUI Wallet", font=("Verdana", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
    tkinter.Label(window, text = " It looks like it's your first time launching this program. ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack()
    tkinter.Label(window, text = " Do you have an Duino-Coin account?", bg = str(colorA), fg = str(colorB), font=("Arial", 12)).pack()
    tkinter.Label(window, text = "", fg = str(colorB), bg = str(colorA)).pack()
    tkinter.Button(window, text = "Yes - I want to login!", activebackground = str(colorHighlight), width = 30, command = Login, bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack() 
    tkinter.Button(window, text = "No - I want to register!", activebackground = str(colorHighlight), width = 30, command = Register, bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack()
    tkinter.Label(window, text = "", bg = str(colorA), fg = str(colorB)).pack()
    window.bind('<Return>', LoginCallback)
    window.mainloop()
 
def Register(): #signup definition
    global pwordE, pwordconfirm, nameE, register, emailE
    
    register = tkinter.Tk() #register window
    register.resizable(False, False)
    register.title('Register')
    try:
        register.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    register.configure(background = str(colorA))

    nameL = tkinter.Label(register, text='Username: ', bg = str(colorA), fg = str(colorB))
    emailL =tkinter.Label(register, text='E-mail: ', bg = str(colorA), fg = str(colorB))
    pwordL =tkinter.Label(register, text='Password: ', bg = str(colorA), fg = str(colorB))
    pwordconfirm = tkinter.Label(register, text='Confirm Password: ', bg = str(colorA), fg = str(colorB))

    nameL.grid(row = 1, column = 0, sticky = W)
    emailL.grid(row = 2, column = 0, sticky = W)
    pwordL.grid(row = 3, column = 0, sticky = W)
    pwordconfirm.grid(row = 4, column = 0, sticky = W)
     
    nameE = Entry(register, fg = str(colorB), bg = str(colorA)) 
    emailE = Entry(register, fg=str(colorB), bg = str(colorA))
    pwordE = Entry(register, show='*', fg = str(colorB), bg = str(colorA)) 
    pwordconfirm = Entry(register, show='*', fg = str(colorB), bg = str(colorA))

    nameE.grid(row = 1, column = 1)
    emailE.grid(row=2, column = 1)
    pwordE.grid(row = 3, column = 1)
    pwordconfirm.grid(row = 4, column = 1)

    signupButton = tkinter.Button(register, text='Register account', activebackground = str(colorHighlight), command = registerProtocol, bg = str(colorA), fg = str(colorB))
    signupButton.grid(row = 5, column = 1)
    register.bind('<Return>', registerCallback)
    register.mainloop()
    selectWindow()

def registerCallback(event):
    registerProtocol()
 
def registerProtocol(): #signup server communication section
    username = nameE.get()
    email = emailE.get()
    passwordconfirm = pwordconfirm.get()
    password = pwordE.get()
    if password == passwordconfirm:
        while True:
            s.send(bytes("REGI,"+str(username)+","+str(password)+","+str(email), encoding='utf8')) #send register request to server
            key = s.recv(32).decode()
            key = key.split(",")
            if key[0] == "OK":
                messagebox.showinfo("Success!", "Registered user "+username+".\nCheck your e-mail for welcome message.")
                window.destroy()
                register.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)
            if key[0] == "NO":
                messagebox.showerror("Error!", str(key[1]))
                register.destroy()
                os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        register.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)
        
def LoginCallback(event):
    Login()

def loginProCallback(event):
    loginProtocol()
 
def Login(): #login window
    global nameEL, pwordEL, rootA, host, port
 
    rootA = tkinter.Tk() #login window
    rootA.resizable(False, False)
    rootA.title('Login')
    try:
        rootA.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    rootA.configure(background = str(colorA))
 
    nameL = Label(rootA, text='Username: ', bg = str(colorA), fg = str(colorB))
    pwordL = Label(rootA, text='Password: ', bg = str(colorA), fg = str(colorB))
    nameL.grid(row = 1, sticky = W)
    pwordL.grid(row = 2, sticky = W)
 
    nameEL = Entry(rootA, fg = str(colorB), bg = str(colorA))
    pwordEL = Entry(rootA, show='*', fg = str(colorB), bg = str(colorA))
    nameEL.grid(row = 1, column = 1)
    pwordEL.grid(row = 2, column = 1)
 
    loginB = Button(rootA, text='Login to account', activebackground = str(colorHighlight), command = loginProtocol, bg = str(colorA), fg = str(colorB))
    loginB.grid(row = 4, column = 1)
    rootA.bind('<Return>', loginProCallback)
 
    rootA.mainloop()
    selectWindow()

def loginProtocol(): # First-time login protocol
    global rootA, window, username, password
    
    username = nameEL.get()
    password = pwordEL.get()
    
    while True:

        s.send(bytes("LOGI,"+str(username)+","+str(password), encoding='utf8')) # Send login request to server
        key = s.recv(64).decode()
        key = key.split(',')
        if key[0] == "OK": # If data is correct, remember user
            config['wallet'] = {"username": username,
                      "password": password,
                      "theme": str("1"),
                      "currency": str("USD")}
            with open(str(resources) + "Wallet_config.cfg", "w") as configfile:
                config.write(configfile)
            window.destroy()
            rootA.destroy()
            loadConfig()
            
        if key[0] == "NO": # If not, go back
            messagebox.showerror("Error!", str(key[1]))
            rootA.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        else: # If error, fallback
            os.execl(sys.executable, sys.executable, *sys.argv)

def sendEmailProtocol():
  email = emailE.get()
  balanceTimer.cancel()
  s.send(bytes("ADDEMAIL,"+str(username)+","+str(password)+","+str(email), encoding='utf8')) # Send login request to server
  time.sleep(0.025)
  resp = s.recv(1024).decode()
  messagebox.showinfo("Server message", str(resp))
  emailWindow.destroy()

def addEmail():
  global emailE, emailWindow

  emailWindow = tkinter.Tk() #email window
  emailWindow.resizable(False, False)
  emailWindow.title('Add e-mail to account')
  try:
      rootA.iconbitmap(str(resources) + "Wallet_icon.ico")
  except:
      pass # Icon won't work on linux
  emailWindow.configure(background = str(colorA))

  nameL = Label(emailWindow, text="There is no e-mail associated with your account.\nWithout it you won\'t be able to exchange funds.\nWe won't send spam.\nPlease add e-mail to your account:", bg = str(colorA), fg = str(colorB))
  nameL.pack()

  emailE = Entry(emailWindow, fg = str(colorB), bg = str(colorA), width=30)
  emailE.pack()

  emailB = Button(emailWindow, text='Add e-mail', activebackground = str(colorHighlight), command = sendEmailProtocol, bg = str(colorA), fg = str(colorB))
  emailB.pack()
    
def loadConfig(): # Load config protocol
    global username, password, loadingScr, currency, rate
    global theme, background, colorA, colorB, colorC, colorHighlight
    global pcusername, publicip, platform, userstatus
    
    label = tkinter.Label(loadingScr, text = "Parsing configfile..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
    loadingScr.update()
    
    config.read(str(resources) + "Wallet_config.cfg")
    username = config["wallet"]["username"]
    password = config["wallet"]["password"]
    theme = config["wallet"]["theme"]
    currency = config["wallet"]["currency"]
    
    if str(theme) == "0": # Light mode
      background = str(resources) + "Wallet_background_light.gif"
      colorA = "#fafafa" #white when in light mode #background
      colorB = "black" #black when in light mode #foreground
      colorC = "gray"
      colorHighlight = "#FBC531" #ducogold - #FBC531
      
    if str(theme) == "1": # Dark theme
      background = str(resources) + "Wallet_background_dark.gif"
      colorA = "#23272a" #background
      colorB = "#fafafa" #foreground
      colorC = "#EEEEEE"
      colorHighlight = "#FBC531" #ducogold - #FBC531

    if str(currency) == "USD": # Fiat currency exchange rates
      rate = 1 # API is in USD

    if str(currency) == "PLN":
      rate = 4.25 # One USD is 4.75 PLN

    if str(currency) == "RUB":
      rate = 76.40 # And so on...
      
    if str(currency) == "EUR":
      rate = 0.93

    while True: # Login
        time.sleep(0.025)
        try:
            s.send(bytes("LOGI,"+username+","+password, encoding='utf8'))
            break
        except:
            os._exit(1)

    while True: # Receive server key
        key = s.recv(64).decode()
        key = key.split(',')
        if key[0] == "OK":
            label = tkinter.Label(loadingScr, text = "Launching..." + str(" ")*20, bg = "#23272a", fg = "#EEEEEE", font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
            loadingScr.update()

            s.send(bytes("FROM," + "Wallet," + str(pcusername).rstrip() + "," + str(publicip).rstrip() + "," + str(platform).rstrip(), encoding="utf8")) # Send info to server settings client
            time.sleep(0.045)
            
            while True:   
                s.send(bytes("STAT", encoding='utf8'))
                try:
                    userstatus = s.recv(1024).decode('utf8')
                    userstatus = userstatus.split(',')

                    if userstatus[1] == "NoEmail":
                      addEmail()
                      s.send(bytes("STAT", encoding='utf8'))
                      userstatus = s.recv(1024).decode('utf8')
                      userstatus = userstatus.split(',')
                    break

                except:
                    pass

            loadingScr.destroy()
            WalletWindow()
            os._exit(0)
        if key[0] == "NO":
            loadingScr.destroy()
            messagebox.showerror("Error",str(key[1]))
            os._exit(0)
        else:
            loadConfig()

def passchgProtocol():
    global oldPassword, newPassword, confPassword, passchg, balanceTimer
    oldPassword = oldPassword.get()
    newPassword = newPassword.get()
    confPassword = confPassword.get()
    if oldPassword == "" or newPassword == "" or confPassword == "": # Check if input fields aren't empty
        messagebox.showerror("Error!","Empty data fields!")
        passchg.destroy()
        
    else:
        if newPassword != confPassword: # Check if passwords match
            messagebox.showerror("Error!","New passwords don't match!")
            passchg.destroy()
            
        else:
            if newPassword == oldPassword: # Check wheter new password is different
                messagebox.showerror("Error!","New password is the same as the old one!")
                passchg.destroy()
                
            else:   
                balanceTimer.cancel()
                time.sleep(0.1)

                s.send(bytes("CHGP,"+str(oldPassword) + "," + str(newPassword), encoding='utf8')) #send sending funds request to server
                time.sleep(0.025)
                message = s.recv(128).decode('utf8')
                if hasNumbers(message):
                    message = s.recv(128).decode('utf8')
                    
                messagebox.showinfo("Server message", message) # Display the server message
                if "Success" in message:
                    s.send(bytes("CLOSE", encoding='utf8'))
                    os.remove(str(resources) + "Wallet_config.cfg")
                    os.execl(sys.executable, sys.executable, *sys.argv)
                passchg.destroy()

def changePass():
    global oldPassword, newPassword, confPassword, passchg
    passchg = Tk() # Changing password window
    passchg.resizable(False, False)
    passchg.title('Change password')
    try:
        passchg.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    
    passchg.configure(background = str(colorA))
    oldPassword = Label(passchg, text="Current password: ", fg = str(colorB), bg = str(colorA)).grid(row = 1, column = 0, sticky = W) 
    newPassword = Label(passchg, text='New password: ', fg = str(colorB), bg = str(colorA)).grid(row = 2, column = 0, sticky = W)
    confPassword = Label(passchg, text='Confirm new password: ', fg = str(colorB), bg = str(colorA)).grid(row = 3, column = 0, sticky = W)

    oldPassword = Entry(passchg, fg = str(colorB), bg = str(colorA))
    oldPassword.grid(row = 1, column = 1)
    newPassword = Entry(passchg, fg = str(colorB), bg = str(colorA), show='*')
    newPassword.grid(row = 2, column = 1)
    confPassword = Entry(passchg, fg = str(colorB), bg = str(colorA), show='*')
    confPassword.grid(row = 3, column = 1)

    passchgButton = Button(passchg, text='Change password', activebackground = str(colorHighlight), command = passchgProtocol, bg = str(colorA), fg = str(colorB)).grid(row = 4, column = 1)

    passchg.mainloop()

def Logout():
    s.send(bytes("CLOSE", encoding='utf8'))
    os.remove(str(resources) + "Wallet_config.cfg")
    os.remove(str(resources) + "Transactions.bin")
    os.execl(sys.executable, sys.executable, *sys.argv)

def Discord():
    webbrowser.open_new_tab("https://discord.gg/kvBkccy")

def GitHub():
    webbrowser.open_new_tab("https://github.com/revoxhere/duino-coin/")
    
def Exchange():
    webbrowser.open_new_tab("https://revoxhere.github.io/duco-exchange/")

def Website():
    webbrowser.open_new_tab("https://revoxhere.github.io/duino-coin/")
    
def getBalance():
    global balance, wallet, ducofiat, balancecurrency, balanceTimer
    
    transactions = open(resources + "Transactions.bin" ,"r+")
    oldcontent = (transactions).read()

    try:
      s.send(bytes("BALA", encoding='utf8'))
      
      oldbalance = balance
      balance = s.recv(1024).decode('utf8')
      if oldbalance <= 0:
        oldbalance = balance
    except:
      messagebox.showerror("Error","Connection to master server closed.\nWallet will be restarted.")
      os.execl(sys.executable, sys.executable, *sys.argv)
        
    if "." in str(balance): # Check wheter we received proper data
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        transactions = open(resources + "Transactions.bin" ,"r+")
        oldcontent = (transactions).read()
        transactions.seek(0, 0)

        balance = round(float(balance), 8) # Format balances
        balancecurrency = round(float(oldbalance) * float(ducofiat) * float(rate), 6)
        difference = round(float(balance) - float(oldbalance), 8)
        
        if difference != 0.0: # Check if balance has changed
            
            if difference >= 0: # Add prefix
                difference = " +" + str(difference)
            else:
                difference = " " + str(difference)
            transactions.write(str(current_time) + str(difference) + "\n" + oldcontent) # Write to file
            transactions.close()
            
        transactions = open(resources + "Transactions.bin" ,"r") # Read from file
        content = transactions.read().splitlines()

        if content[0] == "":
            singletransaction = "No local transactions yet\n\n\n\n\n\n"
            transactionslist = "No local transactions yet\n"

        else:
            singletransaction = content[0] + "        \n\n\n\n\n\n"
            transactionslist = "Local transaction list\n" + content[0] + " DUCO \n" + content[1] + " DUCO \n" + content[2] + " DUCO \n" + content[3] + " DUCO \n" + content[4] + " DUCO \n" + content[5] + " DUCO \n" + content[6] + " DUCO \n" + content[7] + " DUCO \n" + content[8] + " DUCO \n" + content[9] + " DUCO \n"

        if balance == oldbalance: # Don't play animation if no change in balance
            pass
        else: # Animation
            wallet.title("Duino-Coin GUI Wallet ("+str(VER)+") - "+str(round(float(balance), 6))+" DUCO")
            label = tkinter.Label(OVERVIEW, text = str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorHighlight), font=("Arial", 18)).place(relx=.2, rely=.13)
            label = tkinter.Label(OVERVIEW, text = str(balancecurrency)+" "+str(currency)+"          ", bg = str(colorA), fg = str(colorHighlight), font=("Arial", 17)).place(relx=.2, rely=.35)
            transactionslabel = tkinter.Label(OVERVIEW, text = str(singletransaction), bg = str(colorA), fg = str(colorHighlight), justify=LEFT, font=("Arial", 15)).place(relx=.2, rely=.82)                        
            time.sleep(0.1)
            label = tkinter.Label(OVERVIEW, text = str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorB), font=("Arial", 18)).place(relx=.2, rely=.13)
            label = tkinter.Label(OVERVIEW, text = str(balancecurrency)+" "+str(currency)+"          ", bg = str(colorA), fg = str(colorB), font=("Arial", 17)).place(relx=.2, rely=.35)
            transactionslabel = tkinter.Label(OVERVIEW, text = str(singletransaction), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 15)).place(relx=.2, rely=.82)
            transactionslistlabel =  tkinter.Label(TRANSACTIONS, text = str(transactionslist), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 15)).place(relx=.03, rely=.03)

    else:
        getBalance() # Try again

    balanceTimer = threading.Timer(0.3, getBalance)
    balanceTimer.start()

def getDucoPrice():
    global ducofiat, rate, Updated
    try:
      jsonapi = requests.get("https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json", data = None) #Use request to grab data from raw github file
      if jsonapi.status_code == 200: #Check for reponse
          content = jsonapi.content.decode() #Read content and split into lines
          contentjson = json.loads(content)
          ducofiat = float(contentjson["Duco price"]) * float(rate)
          ducofiat = round(ducofiat, 8)
          bigblocks = contentjson["Big blocks and finders"]
          bigblocks = bigblocks.split(",")
          workers = contentjson["Active workers"]
          richestMiners = contentjson["Top 10 richest miners"]
          richestMiners = richestMiners.split(",")
          if Updated == False:
            for bigblock in bigblocks:
              if username in bigblock:
                ownblocks.configure(state ='normal')
                bigblock = bigblock.lstrip(" ")
                ownblocks.insert(INSERT, bigblock + "\n-----------------\n")
                ownblocks.configure(state ='disabled')
            Label(STATISTICS, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 9)).pack()
            Label(STATISTICS, text="Active workers: "+str(workers), fg = str(colorB), bg = str(colorA), font=("Arial", 13), wraplength=600).pack()
            Label(STATISTICS, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 9)).pack()
            Label(STATISTICS, text="Rich list (Top 5): "+str(richestMiners[0])+", "+str(richestMiners[1])+", "+str(richestMiners[2])+", "+str(richestMiners[3])+", "+str(richestMiners[4]), fg = str(colorB), bg = str(colorA), font=("Arial", 13), wraplength=600).pack()
            Updated = True

      else:
          ducofiat = 0.0015 * rate # If json api request fails, wallet will use this value
          ducofiat = round(ducofiat, 8)
          Label(STATISTICS, text="Error fetching data", fg = str(colorB), bg = str(colorA), font=("Arial", 9)).pack()
    except:
        ducofiat = 0.0015 * rate # If json api request fails, wallet will use this value
        Label(STATISTICS, text="Error fetching data", fg = str(colorB), bg = str(colorA), font=("Arial", 9)).pack()

    
    label = tkinter.Label(OVERVIEW, text = str(ducofiat)+" "+str(currency)+str("           "), bg = str(colorA), fg = str(colorB), font=("Arial", 16)).place(relx=.2, rely=.58)
    time.sleep(0.03)
    label = tkinter.Label(OVERVIEW, text = str(ducofiat)+" "+str(currency)+str("           "), bg = str(colorA), fg = "gray", font=("Arial", 16)).place(relx=.2, rely=.58)
    time.sleep(0.05)
    label = tkinter.Label(OVERVIEW, text = str(ducofiat)+" "+str(currency)+str("           "), bg = str(colorA), fg = str(colorA), font=("Arial", 16)).place(relx=.2, rely=.58)
    time.sleep(0.10)
    label = tkinter.Label(OVERVIEW, text = str(ducofiat)+" "+str(currency)+str("           "), bg = str(colorA), fg = "gray", font=("Arial", 16)).place(relx=.2, rely=.58)
    time.sleep(0.05)
    label = tkinter.Label(OVERVIEW, text = str(ducofiat)+" "+str(currency)+str("           "), bg = str(colorA), fg = str(colorB), font=("Arial", 16)).place(relx=.2, rely=.58)

    DucoPrice = threading.Timer(15, getDucoPrice) # Run every 30s
    DucoPrice.start()

def FooterUpdate():
  textlist = ["Your funds are always securely stored on Duino-Coin master server",
              "Duino-Coin is and will always be a completely free service",
              "Unlike others, you don't need to keep your Duino wallet open 24/7",
              "Have you tried the Duino-Coin online wallet yet? If not, visit revoxhere.ct8.pl",
              "Have you seen Bitcoin transaction fees? Good that DUCO doesn't have any"]
  randomtext = random.choice(textlist)
  lbl = Label(footer, text = str(randomtext), background=str(colorA), foreground="#27ae60", font=("Arial", 9), padx=5).pack(anchor=E)

def sendCallback(event):
  sendProtocol()

def sendProtocol():
    global receipent, amount, sendProtocol,  balanceTimer, message

    receipentStr = receipent.get()
    amountStr = amount.get()

    if amountStr == "" or receipentStr == "": # Check if input fields aren't empty
        messagebox.showerror("Error!","Empty data fields!")
        
    else:
        if amountStr.isupper() or amountStr.islower(): # Check if amount contains only numbers
            messagebox.showerror("Error!","Amount can only contain numbers!")

            amount.delete(0, 'end')
            
        else:
            if amountStr == "0": # Check if amount isn't zero
                messagebox.showerror("Error!","Amount must be higher than zero!")

                amount.delete(0, 'end')
                
            else:
                if receipentStr == username: # Check wheter sending to yourself
                    messagebox.showerror("Error!","You can't send funds to yourself!")

                    receipent.delete(0, 'end')
                    
                else: # Send funds
                    balanceTimer.cancel()
                    
                    s.send(bytes("SEND,deprecated,"+receipentStr+","+amountStr, encoding='utf8')) # Sending funds request to server
                    time.sleep(0.025)
                    message = s.recv(128).decode('utf8')

                    while hasNumbers(message):
                        message = s.recv(128).decode('utf8')

                    messagebox.showinfo("Server message", message) # Display the server message

                    receipent.delete(0, 'end')
                    amount.delete(0, 'end')
                    getBalance()

def EditFile():
    webbrowser.open(str(resources)+"Wallet_config.cfg")
    
def WalletWindow():
    global wallet, label, userstatus, OVERVIEW, receipent, amount, TRANSACTIONS, footer

    wallet = tkinter.Tk()	
    wallet.geometry("610x360")
    wallet.resizable(False, False)
    wallet.configure(background = str(colorA))
    wallet.title("Duino-Coin GUI Wallet ("+str(VER)+")")

    style = ttk.Style()

    style.theme_create( "coloredTabs", parent="alt", settings={
        "TNotebook": {
            "configure": {
                "tabmargins": [2, 5, 2, 0],
                "background": str(colorA)}},
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": str(colorA), "foreground": str(colorB)},
            "map":       {"background": [("selected", str(colorHighlight))],
                          "expand": [("selected", [1, 1, 1, 0])] } } } )

    style.theme_use("coloredTabs")
    TAB_CONTROL = ttk.Notebook(wallet)
    Label(wallet, text = "Duino-Coin GUI Wallet "+str(VER), bg = str(colorA), fg = str(colorHighlight), font=("Arial", 13, "bold"), padx=5).pack(anchor = W)

    footer = tkinter.Frame(wallet, bg=str(colorA), height=20)
    footer.pack(fill='both', side='bottom')
    FooterUpdate()

    #OVERVIEW
    OVERVIEW = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(OVERVIEW, text='Overview')
    filename = PhotoImage(file = str(background))
    Label(OVERVIEW, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    duco = PhotoImage(file = str(resources) + '/icons/duco.png') 
    Label(OVERVIEW, image = duco, compound = CENTER, bg=str(colorA)).place(relx=0.03, rely=0.02)
    label = tkinter.Label(OVERVIEW, text = str(username)+"'s balance", bg = str(colorA), fg = str(colorC), font=("Arial", 13)).place(relx = 0.17, rely = 0.03)

    money = PhotoImage(file = str(resources) + '/icons/money.png') 
    Label(OVERVIEW, image = money, compound = CENTER, bg=str(colorA)).place(relx=0.03, rely=0.25)
    label = tkinter.Label(OVERVIEW, text = str(username)+"'s estimated fiat balance", bg = str(colorA), fg = str(colorC), font=("Arial", 13)).place(relx = 0.17, rely = 0.27)
    
    exchange = PhotoImage(file = str(resources) + '/icons/exchange.png') 
    Label(OVERVIEW, image = exchange, compound = CENTER, bg=str(colorA)).place(relx=0.03, rely=0.48)
    label = tkinter.Label(OVERVIEW, text = "Estimated DUCO/"+str(currency)+" price ", bg = str(colorA), fg = str(colorC), font=("Arial", 13)).place(relx = 0.17, rely = 0.5)

    time = PhotoImage(file = str(resources) + '/icons/clock.png') 
    Label(OVERVIEW, image = time, compound = CENTER, bg=str(colorA)).place(relx=0.038, rely=0.75)
    label = tkinter.Label(OVERVIEW, text = "Last transaction", bg = str(colorA), fg = str(colorC), font=("Arial", 13)).place(relx = 0.17, rely = 0.74)
   


    #SEND
    SEND = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(SEND, text='Send')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(SEND, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    receipentLabel = Label(SEND, text="Recipient's address ", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).place(relx=.03, rely=.03)
    
    amountLabel = Label(SEND, text='Amount to transfer ', fg = str(colorB), bg = str(colorA), font=("Arial", 13)).place(relx=.03, rely=.25)

    receipent = Entry(SEND, fg = str(colorB), bg = str(colorA), font=("Arial", 13), width=47)
    receipent.place(relx=.1, rely=.11)
    amount = Entry(SEND, fg = str(colorB), bg = str(colorA), font=("Arial", 13), width=47)
    amount.place(relx=.1, rely=.35)

    send = PhotoImage(file = str(resources) + '/icons/send.png') 
    sendButton = Button(SEND, image = send, compound = LEFT, text='Send funds', activebackground = str(colorHighlight), command = sendProtocol, bg = str(colorA), fg = str(colorB), font=("Arial", 13)).place(relx=.5, rely=.7, anchor="c")
    
    SEND.bind('<Return>', sendCallback)



    #RECEIVE
    RECEIVE = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(RECEIVE, text='Receive')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(RECEIVE, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    Label(RECEIVE, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 3)).pack()
    Label(RECEIVE, text="To receive funds from someone instruct them\nto send funds to your username ("+str(username)+").\n\nSuccessfull transaction will result\nin immediate money transfer.\nCheck your transaction list to see\nif you've received your funds\n(you need to have the wallet open,\ntransaction list is stored locally).", fg = str(colorB), bg = str(colorA), font=("Arial", 18)).pack()



    #TRANSACTIONS
    TRANSACTIONS = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(TRANSACTIONS, text='Transactions')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(TRANSACTIONS, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)



    #STATISTICS
    global ownblocks, networkhashrate, STATISTICS
    STATISTICS = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(STATISTICS, text='Statistics')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(STATISTICS, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    Label(STATISTICS, text="Blocks found by you", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack()
    ownblocks = st.ScrolledText(STATISTICS,  height = 5, background=str(colorA), foreground=str(colorB), font = ("Arial", 10)) 
    ownblocks.pack()

    
    
    #SHORTCUTS
    SHORTCUTS = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(SHORTCUTS, text='Shortcuts')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(SHORTCUTS, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    Label(SHORTCUTS, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 9)).pack()
    tkinter.Button(SHORTCUTS, text = "Visit Duino-Coin GitHub", activebackground = str(colorHighlight), height = 1, command = GitHub, width=47, fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack(pady=2)
    tkinter.Button(SHORTCUTS, text = "Browse Duino-Coin Website", activebackground = str(colorHighlight), height = 1, command = Website, width=47, fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack(pady=2)
    tkinter.Button(SHORTCUTS, text = "Join Duino-Coin Discord", activebackground = str(colorHighlight), height = 1, command = Discord, width=47, fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack(pady=2)
    tkinter.Button(SHORTCUTS, text = "Open Duino-Coin Exchange", activebackground = str(colorHighlight), height = 1, command = Exchange, width=47, fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack(pady=2)
    Label(SHORTCUTS, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack()
    tkinter.Button(SHORTCUTS, text = "Edit Wallet configuration file", activebackground = str(colorHighlight), height = 1, command = EditFile, width=47, fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack(pady=2)
    Label(SHORTCUTS, text="", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack()
    Label(SHORTCUTS, text = "Duino-Coin GUI Wallet is brought to you by revox from Duino-Coin developers", fg = str(colorB), bg = str(colorA), font=("Arial", 10)).pack()



    #SETTINGS
    global SETTINGS
    global v, val, themes, setTheme, theme
    global c, cal, setCurrency, currencies

    SETTINGS = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(SETTINGS, text='Settings')
    TAB_CONTROL.pack(expand=1, fill="both")
    Label(SETTINGS, image = filename).place(x = 0, y = 0, relwidth = 1, relheight = 1)

    tvariable = StringVar(SETTINGS)
    if theme == "0":
        tvariable.set(themes[0])
    if theme == "1":
        tvariable.set(themes[1])
    if theme == "2":
        tvariable.set(themes[2])

    cvariable = StringVar(SETTINGS)
    if currency == "USD":
        cvariable.set(currencies[0])
    if currency == "PLN":
        cvariable.set(currencies[1])
    if currency == "RUB":
        cvariable.set(currencies[2])
    if currency == "EUR":
        cvariable.set(currencies[3])

    tkinter.Button(SETTINGS, text = "Change password", activebackground = str(colorHighlight), height = 1, command = changePass, width=23, font=("Arial", 13), fg = str(colorB), bg = str(colorA)).place(relx=0.03, rely=0.03)
    tkinter.Button(SETTINGS, text = "Logout", activebackground = str(colorHighlight), height = 1, command = Logout, width=23, font=("Arial", 13), fg = str(colorB), bg = str(colorA)).place(relx=0.53, rely=0.03)

    tkinter.Label(SETTINGS, text = "Select theme", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).place(relx=0.03, rely=0.20)
    th = OptionMenu(SETTINGS, tvariable, *themes, command = setTheme)
    th.config(bg = str(colorA), fg = str(colorB), activebackground = str(colorHighlight), width=23, height=1)
    th.place(relx=0.03, rely=0.3)

    tkinter.Label(SETTINGS, text = "Select currency", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).place(relx=0.53, rely=0.20)
    w = OptionMenu(SETTINGS, cvariable, *currencies, command = setCurrency)
    w.config(bg = str(colorA), fg = str(colorB), activebackground = str(colorHighlight), width=23, height=1)
    w.place(relx=0.53, rely=0.3)

    tkinter.Label(SETTINGS, text = "\n\n\n\n\n\n\n", fg = str(colorB), bg = str(colorA), font=("Arial", 13)).pack()
    tkinter.Label(SETTINGS, text = "Remember that you don't need to have your wallet open 24/7 to receive funds. Duino-Coin master server takes care of all transactions and your wallet data is securely stored on the main server.", fg = str(colorB), bg = str(colorA), wraplength=600, font=("Arial", 13)).pack()



    getDucoPrice()
    getBalance()
    wallet.mainloop()

label = tkinter.Label(loadingScr, text = "Organizing files..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()
config = configparser.ConfigParser() # Read configfile

try:
    os.mkdir(str(resources)) # Create resources folder if it doesn't exist
except:
    pass
try:
    os.mkdir(str(resources) + "/icons") # Create icons folder if it doesn't exist
except:
    pass
if not os.path.isfile(str(resources) + "Transactions.bin"):
    f = open(str(resources) + "Transactions.bin" ,"w+") # Create transactions file if it doesn't exist
    for i in range(10):
        f.write("\n")
        i =+ 1
    f.close()
while True: # Receive pool info
    WalletResources = requests.get(WalletResources, data = None) #Use request to grab data from raw github file
    if WalletResources.status_code == 200: #Check for reponse
        content = WalletResources.content.decode().splitlines() #Read content and split into lines
        host = content[0] #Line 1 = pool address
        port = content[1] #Line 2 = pool port
        break
    else:
        time.sleep(0.025)
    

if not Path(str(resources) + "Wallet_background_light.gif").is_file(): # Light mode background
  url = 'https://i.imgur.com/lbQbVzx.gif'
  urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_light.gif')

if not Path(str(resources) + "Wallet_background_dark.gif").is_file(): # Dark mode background
  url = 'https://i.imgur.com/nISni6J.gif'
  urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_dark.gif')

if not Path(str(resources) + "Wallet_icon.ico").is_file():
  url = 'https://raw.githubusercontent.com/revoxhere/duino-coin/master/Resources/NewWallet.ico'
  urllib.request.urlretrieve(url, str(resources) + 'Wallet_icon.ico')

if not Path(str(resources) + "/icons/exchange.png").is_file():
  url = 'https://i.imgur.com/ujKAjLh.png'
  urllib.request.urlretrieve(url, str(resources) + '/icons/exchange.png')

if not Path(str(resources) + "/icons/duco.png").is_file():
  url = 'https://i.imgur.com/wFZX2Fq.png'
  urllib.request.urlretrieve(url, str(resources) + '/icons/duco.png')

if not Path(str(resources) + "/icons/send.png").is_file():
  url = 'https://i.imgur.com/7pNAz2M.png'
  urllib.request.urlretrieve(url, str(resources) + '/icons/send.png')

if not Path(str(resources) + "/icons/money.png").is_file():
  url = 'https://i.imgur.com/iMuz8PM.png'
  urllib.request.urlretrieve(url, str(resources) + '/icons/money.png')

if not Path(str(resources) + "/icons/clock.png").is_file():
  url = 'https://i.imgur.com/s72e9Mb.png'
  urllib.request.urlretrieve(url, str(resources) + '/icons/clock.png')

label = tkinter.Label(loadingScr, text = "Authenticating user..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

try:
  s.connect((str(host), int(port)))
  SERVER_VER = s.recv(3).decode() # Server version
  if float(VER) < float(SERVER_VER):
    serverMsg = tkinter.Tk()
    serverMsg.withdraw()
    messagebox.showwarning("Warning","Your wallet is outdated, please install latest version to be up-to-date.")
    serverMsg.destroy()

except:
  loadingScr.destroy()
  serverMsg = tkinter.Tk()
  serverMsg.withdraw()
  messagebox.showerror("Error","Server is under maintenance or offline.\nPlease try again in a few hours.")
  serverMsg.destroy()
  os._exit(0)
    
if not Path(str(resources) + "Wallet_config.cfg").is_file():
  label = tkinter.Label(loadingScr, text = "Launching for the first time..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)
  loadingScr.update()
  selectWindow()
  loadConfig()
else:
  loadConfig() 
