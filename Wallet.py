#!/usr/bin/env python

###########################################
#  Duino-Coin wallet version 0.6.5 alpha  #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import time, socket, sys, os, configparser, tkinter, webbrowser, urllib.request, random
import threading
from tkinter import messagebox
from tkinter import *
from pathlib import Path

#setting variables
debug = "Starting debug file of DUCO wallet v0.6.5\n"
users = {}
status = ""
host = "0.tcp.ngrok.io" #official server ip
port = 19921 #official server port
s = socket.socket()

balanceusd = 0
sending = 0
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
# 9.11.2019
rand = random.randint(1000,1090)
rand = rand / 1000
xmgusd = 0.02985
xmgusd = float(xmgusd) * float(rand)
ducousd = float(xmgusd) / float(8)
debug = debug + "Calculated prices\n"
debug = debug + "XMG/USD price is: " + str(xmgusd) + "\n"
debug = debug + "DUCO/USD price is: " + str(ducousd) + "\n"

if not Path("bg_0.6.5.gif").is_file():
        try:
                debug = debug + "Downloading latest background file\n"
                url = 'https://i.imgur.com/4bvAxvA.gif'
                urllib.request.urlretrieve(url, 'bg_0.6.5.gif')
        except:
                debug = debug + "Couldn't download background file!\n"
else:
        debug = debug + "Background image already downloaded\n"
 
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
                with open("WalletConfig.ini", "w") as configfile:
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
        window.title("Duino-Coin wallet v0.6.5")
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
        global username, password, debug
        config.read("WalletConfig.ini")
        username = config["wallet"]["username"]
        password = config["wallet"]["password"]
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
                os.remove("WalletConfig.ini")
                SelectScr()
        else:
                WalletScr()

def num_there(s):
    return any(i.isdigit() for i in s)

def FSSSend():
        global receipent, fsssend, amount, debug, sending
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
        
        label = tkinter.Label(send, text = "Your balance: "+balancegood+" DUCO", bg="white")
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

def About():
        global about, debug
        
        about = Tk() #about window
        about.resizable(False, False)
        about.geometry("400x300")
        about.title('About')
        about.configure(background='white')

        label = tkinter.Label(about, text = "", bg="white").pack()
        label = tkinter.Label(about, text = "Duino-Coin wallet", font="-weight bold", bg="white").pack()
        label = tkinter.Label(about, text = "Version: 0.6.5 alpha", bg="white").pack()
        label = tkinter.Label(about, text = "Made by revox from Duino-Coin developers", bg="white").pack()
        tkinter.Button(about, text = "Duino-Coin GitHub", command = GitHub, bg="white").pack()
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
        global balancegood, wallet, ducousd, balanceusd, sending
        if sending == 1:
                try:
                        threading.Timer(1, getBalance).stop()
                except:
                        pass
        else:
                s.send(bytes("BALA", encoding='utf8'))
                time.sleep(0.025)
                balance = s.recv(1024)
                balance = balance.decode('utf8')
                balance = balance[:10]
                if "." in balance:
                        balancegood = balance
                        try:
                                label = tkinter.Label(wallet, text = "Your balance: "+balancegood+" (DUCO)", bg="white", font=("Arial", 12)).place(relx=.1, rely=.15)
                        except:
                                pass
                balanceusd = float(balance) * float(ducousd)
                balanceusd = str(balanceusd)[:8]
                ducousd = str(ducousd)[:8]
                threading.Timer(1, getBalance).start()
        
def WalletWindow():
        getBalance()
        global wallet, label
        
        wallet = tkinter.Tk()
        wallet.geometry("500x300")
        wallet.resizable(False, False)
        wallet.title("Duino-Coin wallet v0.6.5")

        filename = PhotoImage(file = "bg_0.6.5.gif")
        background_label = Label(wallet, image=filename)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        label = tkinter.Label(wallet, text = "Duino-Coin wallet", bg="white", fg="gold", font=("Arial", 20, "bold")).place(relx=.5, rely=.06, anchor="c")
        label = tkinter.Label(wallet, text = "", bg="white").place()
        label = tkinter.Label(wallet, text = "Your balance: "+balancegood+" (DUCO)", bg="white", font=("Arial", 12)).place(relx=.1, rely=.15)
        label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd), bg="white", font=("Arial", 10)).place(relx=.1, rely=.213)
        label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd), bg="white", font=("Arial", 10)).place(relx=.1, rely=.27)
        
        tkinter.Button(wallet, text = "Send funds", command = Send, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.42)
        tkinter.Button(wallet, text = "Receive funds", command = Receive, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.53)
        tkinter.Button(wallet, text = "Exchange DUCO", command = Exchange, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.64)
        tkinter.Button(wallet, text = "About", command = About, bg="white", font=("Arial", 10), height = 1, width = 30).place(relx=0.1, rely=0.75)
        
        label = tkinter.Label(wallet, text = "2019 Duino-Coin developers", bg="white", fg="gray", font=("Arial", 8)).place(relx=0.01, rely=0.93)
        wallet.mainloop()
        
def Start():
        global debug
        try:
                s.connect((host, port))
                s.settimeout(30)
                debug = debug + "Connected to the server\n"
                if not Path("WalletConfig.ini").is_file():
                        SelectScr()
                else:
                        WalletScr()
        except:
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showerror("Error!","A server update is probably underway.\nPlease try again later.")
                sys.exit()
Start()
