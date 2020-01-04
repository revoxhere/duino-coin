#!/usr/bin/env python3
###########################################
#  Duino-Coin wallet version 0.6.8 alpha  #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import time, socket, sys, os, configparser, tkinter, webbrowser, urllib.request, random, requests
import threading
from tkinter import messagebox
from tkinter import *
from pathlib import Path

debug = "Starting debug file of DUCO wallet v0.6.8\n"

try:
        os.mkdir("res") #resources folder
except:
        pass
status = ""
res = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
while True:
        try:
                res = requests.get(res, data = None) #Use request to grab data from raw github file
                if res.status_code == 200: #Check for response
                        content = res.content.decode().splitlines() #Read content and split into lines
                        host = content[0] #Line 1 = pool address
                        port = content[1] #Line 2 = pool port
                        debug = debug + "Received pool IP and port.\n"
                        break
                else:
                        time.sleep(0.025)
        except:
                debug = debug + "Error while receiving pool data.\n"
        time.sleep(0.025)
s = socket.socket()
balanceusd = 0
sending = 0
alt_mode = 0
debug = debug + "Successfully set variables\n"
try:
        config = configparser.ConfigParser()
        debug = debug + "Read configfile\n"
except:
        debug = debug + "Error while loading configfile!!!\n"
# ~10 DUCO = 1 XMG
# 1 XMG = ~0.02 USD
# 1 DUCO = ~0.002 USD
# price is also backed up by some luck during trading, so small randomness is added
# 1.01.2020
rand = random.randint(1000,1090)
rand = rand / 1000
xmgusd = 0.02985
xmgusd = float(xmgusd) * float(rand)
ducousd = float(xmgusd) / float(8)
debug = debug + "Calculated prices\n"
debug = debug + "XMG/USD price is: " + str(xmgusd) + "\n"
debug = debug + "DUCO/USD price is: " + str(ducousd) + "\n"

if not Path("res/bg_0.6.8.gif").is_file():
        try:
                debug = debug + "Downloading latest background file\n"
                url = 'https://i.imgur.com/r6g8eR9.gif'
                urllib.request.urlretrieve(url, 'res/bg_0.6.8.gif')
        except:
                debug = debug + "Couldn't download background file!\n"
else:
        debug = debug + "Background image already downloaded\n"

if not Path("res/bg_0.6.8_alt.gif").is_file():
        try:
                debug = debug + "Downloading latest background file\n"
                url = 'https://i.imgur.com/bUlETdV.gif'
                urllib.request.urlretrieve(url, 'res/bg_0.6.8_alt.gif')
        except:
                debug = debug + "Couldn't download alternate background file!\n"
else:
        debug = debug + "Alternate background image already downloaded\n"
 
def Signup(): #signup definition
        global pwordE
        global pwordconfirm 
        global nameE
        global roots
        window.destroy()
        roots = Tk() #register window
        roots.resizable(False, False)
        roots.title('Register')
        roots.configure(background='white')

        nameL = Label(roots, text='Username: ', bg="white")
        pwordL = Label(roots, text='Password: ', bg="white")
        pwordconfirm = Label(roots, text='Confirm Password: ', bg="white")
        nameL.grid(row=1, column=0, sticky=W) 
        pwordL.grid(row=2, column=0, sticky=W)
        pwordconfirm.grid(row=3, column=0, sticky=W)
         
        nameE = Entry(roots) 
        pwordE = Entry(roots, show='*') 
        pwordconfirm = Entry(roots, show='*')
        nameE.grid(row=1, column=1)
        pwordE.grid(row=2, column=1)
        pwordconfirm.grid(row=3, column=1)
         
        signupButton = Button(roots, text='Register account', command=FSSignup, bg="white")
        signupButton.grid(columnspan=2, sticky=W)
        roots.mainloop()
        SelectScr()
 
def FSSignup(): #signup server communication section
        username = nameE.get()
        passwordconfirm = pwordconfirm.get()
        password = pwordE.get()
        if password == passwordconfirm:
                s.send(bytes("REGI,"+username+","+password, encoding='utf8')) #send register request to server
                key = s.recv(3)
                key=key.decode()
                time.sleep(0.025)
                key = s.recv(2)
                key = key.decode()
                if key == "OK":
                        messagebox.showinfo("Success!", "Successfully registered user "+username+".\nNow you can restart Wallet and login.")
                        roots.destroy()
                        os._exit(0)
                if key == "NO":
                        messagebox.showerror("Error!", "User "+username+" is already registered or you've used non-allowed characters!\nPlease try again!")
                        roots.destroy()
                        Signup()
        else:
                roots.destroy()
                Login()
 
def Login(): #login window
        window.destroy()
        global nameEL
        global pwordEL
        global rootA
 
        rootA = Tk() #login window
        rootA.resizable(False, False)
        rootA.title('Login')
        rootA.configure(background='white')
 
        nameL = Label(rootA, text='Username: ', bg="white")
        pwordL = Label(rootA, text='Password: ', bg="white")
        nameL.grid(row=1, sticky=W)
        pwordL.grid(row=2, sticky=W)
 
        nameEL = Entry(rootA)
        pwordEL = Entry(rootA, show='*')
        nameEL.grid(row=1, column=1)
        pwordEL.grid(row=2, column=1)
 
        loginB = Button(rootA, text='Login to account', command=CheckLogin, bg="white")
        loginB.grid(columnspan=2, sticky=W)
 
        rootA.mainloop()
        SelectScr()

def CheckLogin(): #login server communication section
        username = nameEL.get()
        password = pwordEL.get()
        s.send(bytes("LOGI,"+username+","+password, encoding='utf8')) #send login request to server
        global rootA, window
        key = s.recv(3)
        time.sleep(0.015)
        key = s.recv(2)
        key = key.decode()
        if key == "OK":
                config['wallet'] = {"username": username,
                "password": password}
                with open("res/WalletConfig.ini", "w") as configfile:
                        config.write(configfile)
                rootA.destroy()
                WalletWindow()
                os._exit(0)
                
        if key == "NO":
                messagebox.showerror("Error!", "Incorrect credentials!\n Please try again!")
                rootA.destroy()
                Login()
        else:   
                Login()
                
def SelectScr(): #first-time launch window
        global window
        window = tkinter.Tk()
        window.geometry("355x190")
        window.resizable(False, False)
        window.title("Duino-Coin wallet v0.6.8")
        window.configure(background='white')
        
        label = tkinter.Label(window, text = "", bg="white").pack()       
        label = tkinter.Label(window, text = " Duino-Coin wallet", font=("Arial", 20, "bold"), bg="white", fg="gold").pack()
        label = tkinter.Label(window, text = " It looks like it's your first time launching this program. ", bg="white", font=("Arial", 10)).pack()
        label = tkinter.Label(window, text = " Do you have an Duino-Coin account?", bg="white", font=("Arial", 12)).pack()
        label = tkinter.Label(window, text = "", bg="white").pack()
        tkinter.Button(window, text = "  Yes - login me! ", command = Login, bg="white", font=("Arial", 10)).pack() 
        tkinter.Button(window, text = " No - register me!", command = Signup, bg="white", font=("Arial", 10)).pack()
        label = tkinter.Label(window, text = "", bg="white").pack()
        window.mainloop()
        
def WalletScr():
        global username, password, debug, alt_mode
        config.read("res/WalletConfig.ini")
        username = config["wallet"]["username"]
        password = config["wallet"]["password"]
        try:
                alt_mode = config["wallet"]["alt_mode"]
        except:
                config['wallet'] = {"username": username,
                "password": password,
                "alt_mode": str(0)}
                with open("WalletConfig.ini", "w") as configfile:
                        config.write(configfile)
        debug = debug + "Using pre-defined settings of user " + str(username) + "\n"
        try:
                debug = debug + "Successfully logged-in\n"
                s.send(bytes("LOGI,"+username+","+password, encoding='utf8'))
                
        except:
                debug = debug + "Error while logging-in!\n"
        key = s.recv(64)
        time.sleep(0.025)
        key = s.recv(2)
        key=key.decode()
        debug = debug + "Received server key\n"
        if key == "OK":
                WalletWindow()
        if key == "NO":
                messagebox.showerror("Error!","Error in pre-defined configfile (WalletConfig.ini)!\nRemove it and restart the wallet.")
                os.remove("res/WalletConfig.ini")
                SelectScr()
        else:
                WalletScr()

def num_there(s):
    return any(i.isdigit() for i in s)

def FSSSend():
        global receipent, fsssend, amount, debug, sending, username
        sendit = "OK"
        receipent = receipentA.get()
        amount = amountA.get()
        debug = debug + "Started sending funds protocol\n"
        sending = 1
        if amount.isupper() or amount.islower():
                sendit = "NO"
                debug = debug + "Amount contains letters!\n"
                messagebox.showerror("Error!","Incorrect amount!")
                send.destroy()
        if amount == "0":
                sendit = "NO"
                debug = debug + "Amount is 0!\n"
                messagebox.showerror("Error!","Incorrect amount!")
                send.destroy()
        if receipent == username:
                sendit = "NO"
                debug = debug + "Can't send to yourself!\n"
                messagebox.showerror("Error!","Wrong receipent!")
                send.destroy()
        if sendit =="OK":
                debug = debug + "Sending "+amount+" DUCO from: "+username+" to "+receipent+"\n"
                try:
                        s.send(bytes("SEND,"+username+","+receipent+","+amount, encoding='utf8')) #send sending funds request to server
                except:
                        debug = debug + "Fatal error while sending. Probably timeout.\n"
                        pass
                time.sleep(0.015)
                message = s.recv(128).decode('utf8')
                if num_there(message): #if we receive balance instead of feedback, read message once again
                        message = s.recv(128).decode('utf8')
                debug = debug + "Server returned: "+message+"\n"
                messagebox.showinfo("Server message", message) #print server message
                send.destroy()
        else:
                send.destroy()

def Send():
        global amountA
        global receipentA
        global send
        send = Tk() #sending funds window
        send.resizable(False, False)
        send.title('Send funds')
        send.configure(background='white')
        
        label = tkinter.Label(send, text = "Your balance: "+balance+" DUCO", bg="white")
        receipentA = Label(send, text="Receipents' username: ", bg="white")
        amountA = Label(send, text='Amount: ', bg="white")
        receipentA.grid(row=1, column=0, sticky=W) 
        amountA.grid(row=2, column=0, sticky=W)
        label.grid(row=0, column=0, sticky=W)

        receipentA = Entry(send)
        amountA = Entry(send)
        receipentA.grid(row=1, column=1)
        amountA.grid(row=2, column=1)

         
        signupButton = Button(send, text='Send funds', command=FSSSend, bg="white")
        signupButton.grid(columnspan=2, sticky=W)
        send.mainloop

def Receive(): #receiving funds help dialog
        try:
                messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username ("+username+").")
        except:
                messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username.")
        pass

def alton():
        global username, password, debug, alt_mode
        config['wallet'] = {"username": username,
        "password": password,
        "alt_mode": str(1)}
        with open("res/WalletConfig.ini", "w") as configfile:
                config.write(configfile)
        debug = debug + "Set alternative background.\n"
        messagebox.showinfo("Restart needed!","In order to apply changes, restart your wallet.\nThis months background was made by: niebieskikot")
        
def altoff():
        global username, password, debug, alt_mode
        config['wallet'] = {"username": username,
        "password": password,
        "alt_mode": str(0)}
        with open("res/WalletConfig.ini", "w") as configfile:
                config.write(configfile)
        debug = debug + "Set normal background.\n"
        messagebox.showinfo("Restart needed!","In order to apply changes, restart your wallet.")


def About():
        global about, debug
        
        about = Tk() #about window
        about.resizable(False, False)
        about.geometry("400x400")
        about.title('About')
        about.configure(background='white')

        label = tkinter.Label(about, text = "", bg="white").pack()
        label = tkinter.Label(about, text = "Duino-Coin wallet", font="-weight bold", bg="white").pack()
        label = tkinter.Label(about, text = "Version: 0.6.8 alpha", bg="white").pack()
        label = tkinter.Label(about, text = "Made by revox from Duino-Coin developers", bg="white").pack()
        tkinter.Button(about, text = "Duino-Coin GitHub", command = GitHub, bg="white", width = 46).pack()
        label = tkinter.Label(about, text = "", bg="white").pack()
        
        A = tkinter.Button(about, text = "Use alternative mode", command = alton, bg="white", width = 20)
        A.place(rely=0.3, relx=0.06)
        N = tkinter.Button(about, text = "Use regular mode", command = altoff, bg="white", width = 20)
        N.place(rely=0.3, relx=0.52)

        label = tkinter.Label(about, text = "", bg="white").pack()
     
        label = tkinter.Label(about, text = "Debug output (useful for diagnosing problems):", bg="white").pack()
        S = tkinter.Scrollbar(about)
        T = tkinter.Text(about, height=3, width=50)
        S.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        T.pack(side=tkinter.LEFT, fill=tkinter.Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        T.insert(tkinter.END, debug)

def GitHub():
        webbrowser.open_new_tab("https://github.com/revoxhere/duino-coin")
        pass
      
def Exchange():
        webbrowser.open_new_tab("https://revoxhere.github.io/duco-exchange/")
        pass

def getBalance():
        global balance, wallet, ducousd, balanceusd, sending, debug
        if sending == 1:
                try:
                        threading.Timer(1, getBalance).stop()
                except:
                        pass
        else:
                s.send(bytes("BALA", encoding='utf8'))
                time.sleep(0.025)
                try:
                        balance = s.recv(1024)
                        balance = balance.decode('utf8')
                except:
                        getBalance()

                if "." in str(balance):
                        try:
                                balance = round(float(balance), 8)
                        except:
                                getBalance()

                        label = tkinter.Label(wallet, text = "Your balance: "+str(balance)+" DUCO", bg="white", font=("Arial", 12)).place(relx=.1, rely=.15)
                else:
                        debug = debug + "Error while receiving balance!\n"
                        getBalance()
                balanceusd = float(balance) * float(ducousd)
                balanceusd = str(balanceusd)[:8]
                ducousd = str(ducousd)[:8]
                threading.Timer(1.5, getBalance).start()
        
def WalletWindow():
        global wallet, label, alt_mode
        
        wallet = tkinter.Tk()
        wallet.geometry("500x300")
        wallet.resizable(False, False)
        wallet.title("Duino-Coin wallet v0.6.8")
        if int(alt_mode) == 1:
                filename = PhotoImage(file = "res/bg_0.6.8_alt.gif")
        else:
                filename = PhotoImage(file = "res/bg_0.6.8.gif")
        background_label = Label(wallet, image=filename)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        getBalance()
        
        label = tkinter.Label(wallet, text = "Duino-Coin wallet", bg="white", fg="gold", font=("Arial", 20, "bold")).place(relx=.5, rely=.08, anchor="c")
        label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $", bg="white", font=("Arial", 10)).place(relx=.1, rely=.213)
        label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $", bg="white", font=("Arial", 10)).place(relx=.1, rely=.27)
        
        tkinter.Button(wallet, text = "Send funds", command = Send, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.42)
        tkinter.Button(wallet, text = "Receive funds", command = Receive, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.53)
        tkinter.Button(wallet, text = "Exchange DUCO", command = Exchange, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.64)
        tkinter.Button(wallet, text = "About", command = About, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.75)
        
        label = tkinter.Label(wallet, text = "2019 Duino-Coin developers", bg="white", fg="gray", font=("Arial", 8)).place(relx=0.01, rely=0.93)
        wallet.mainloop()
        
def Start():
        global debug, host, port
        try:
                s.connect((str(host), int(port)))
                s.settimeout(1)
                debug = debug + "Connected to the server\n"
                if not Path("res/WalletConfig.ini").is_file():
                        SelectScr()
                else:
                        WalletScr()
        except SystemExit:
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showerror("Error!","Please try again later.\nServer is under maintenance.")
                sys.exit()
Start()
