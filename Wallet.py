#!/usr/bin/env python

###########################################
#   Duino-Coin wallet version 0.5 alpha   #
# https://github.com/revoxhere/duino-coin #
#       copyright by revox 2019           #
###########################################

import time, socket, sys, os, configparser, tkinter
from tkinter import messagebox
from tkinter import *
from pathlib import Path

users = {}
status = ""
host = 'serveo.net' #official server ip
port = 14808 #official server port
s = socket.socket()
config = configparser.ConfigParser()
 
def Signup(): #signup definition
        window.destroy()
        global pwordE
        global pwordconfirm 
        global nameE
        global roots
        
        roots = Tk() #register window
        roots.resizable(False, False)
        roots.title('Register')

        nameL = Label(roots, text='Username: ')
        pwordL = Label(roots, text='Password: ')
        pwordconfirm = Label(roots, text='Confirm Password: ')
        nameL.grid(row=1, column=0, sticky=W) 
        pwordL.grid(row=2, column=0, sticky=W)
        pwordconfirm.grid(row=3, column=0, sticky=W)
         
        nameE = Entry(roots) 
        pwordE = Entry(roots, show='*') 
        pwordconfirm = Entry(roots, show='*')
        nameE.grid(row=1, column=1)
        pwordE.grid(row=2, column=1)
        pwordconfirm.grid(row=3, column=1)
         
        signupButton = Button(roots, text='Register me', command=FSSignup)
        signupButton.grid(columnspan=2, sticky=W)
        roots.mainloop()
        SelectScr()
 
def FSSignup():
        username = nameE.get()
        passwordconfirm = pwordconfirm.get()
        password = pwordE.get()
        if password == passwordconfirm:
                s.send(bytes("REGI,"+username+","+password, encoding='utf8')) #send register request to server
                key = s.recv(2)
                key=key.decode()
                if key == "OK":
                        messagebox.showinfo("Title", "Successfully registered user "+username+".\nNow you can login!")
                        roots.destroy()
                        Login()
                if key == "NO":
                        messagebox.showerror("Error!", "User "+username+" is already registered!\nPlease try again!")
                        roots.destroy()
                        Signup()
        else:
                roots.destroy()
                Signup()
 
def Login():
        window.destroy()
        global nameEL
        global pwordEL
        global rootA
 
        rootA = Tk() #login window
        rootA.resizable(False, False)
        rootA.title('Login')
 
        nameL = Label(rootA, text='Username: ')
        pwordL = Label(rootA, text='Password: ')
        nameL.grid(row=1, sticky=W)
        pwordL.grid(row=2, sticky=W)
 
        nameEL = Entry(rootA)
        pwordEL = Entry(rootA, show='*')
        nameEL.grid(row=1, column=1)
        pwordEL.grid(row=2, column=1)
 
        loginB = Button(rootA, text='Login', command=CheckLogin)
        loginB.grid(columnspan=2, sticky=W)
 
        rootA.mainloop()
        SelectScr()
 
def CheckLogin():
        username = nameEL.get()
        password = pwordEL.get()
        s.send(bytes("LOGI,"+username+","+password, encoding='utf8')) #send login request to server
        
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
                messagebox.showinfo("Title", "Successfully logged in!\nYour login data will be automatically remembered!")
                config['pool'] = {"username": username,
                "password": password}
                with open("config.ini", "w") as configfile:
                        config.write(configfile)
                rootA.destroy()
                WalletScr()
                
        if key == "NO":
                messagebox.showerror("Error!", "Incorrect credentials!\n Please try again!")
                rootA.destroy()
                Login()
                
        Login()
                
def SelectScr():
        global window
        window = tkinter.Tk()
        window.geometry("330x200")
        window.resizable(False, False)
        window.title("Duino-Coin wallet")
        
        label = tkinter.Label(window, text = "").pack()       
        label = tkinter.Label(window, text = " Welcome to the Duino-Coin wallet!", font="-weight bold").pack()
        label = tkinter.Label(window, text = " It looks like it's your first time launching this program. ").pack()
        label = tkinter.Label(window, text = " Do you have an Duino-Coin account?").pack()
        label = tkinter.Label(window, text = "").pack()
        tkinter.Button(window, text = "  Yes, login me! ", command = Login).pack() 
        tkinter.Button(window, text = " No, register me!", command = Signup).pack()
        label = tkinter.Label(window, text = "").pack() 
        label = tkinter.Label(window, text = "                                        2019 Duino-Coin developers").pack()

        window.mainloop()
        
def WalletScr():
        global username
        print("Using pre-defined settings")
        config.read("config.ini")
        username = config["pool"]["username"]
        password = config["pool"]["password"]
        print("Pre-defined settings:", username, password)
        
        s.send(bytes("LOGI,"+username+","+password, encoding='utf8')) #send login request to server
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
                WalletWindow()
        if key == "NO":
                messagebox.showerror("Error!","Error in pre-defined credentials!\nRemoving them and again starting login select window")
                os.remove("config.ini")
                SelectScr()

def FSSSend():
        global receipent 
        global amount
        receipent = receipentA.get()
        amount = amountA.get()
        
        if amount.isupper() or amount.islower():
                print("Amount contains letters!")
                messagebox.showerror("Error!","Incorrect amount!")
                send.destroy()

        print("Sending ", amount, " funds from:", username, "to", receipent)
        s.send(bytes("SEND,"+username+","+receipent+","+amount, encoding='utf8')) #send sending funds request to server
        time.sleep(0.1)
        message = s.recv(1024).decode('utf8')
        message = ''.join([i for i in message if not i.isdigit()]) #sometimes crappy numbers happen, idk why so remove them
        messagebox.showinfo("Server message", message) #print server message
        send.destroy()
        WalletWindow()

def Send():
        global amountA
        global receipentA
        global send
        wallet.destroy()
        send = Tk() #sending funds window
        send.resizable(False, False)
        send.title('Send funds')
        
        label = tkinter.Label(send, text = "Your balance: "+balance+" DUCO")
        receipentA = Label(send, text="Receipents' username: ")
        amountA = Label(send, text='Amount: ')
        receipentA.grid(row=1, column=0, sticky=W) 
        amountA.grid(row=2, column=0, sticky=W)
        label.grid(row=0, column=0, sticky=W)

        receipentA = Entry(send)
        amountA = Entry(send)
        receipentA.grid(row=1, column=1)
        amountA.grid(row=2, column=1)

         
        signupButton = Button(send, text='Send funds', command=FSSSend)
        signupButton.grid(columnspan=2, sticky=W)
        send.mainloop()

def Receive(): #receiving funds help dialog
        messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username ("+username+").")
        pass

def About():
        global about
        
        about = Tk() #about window
        about.resizable(False, False)
        about.geometry("300x90")
        about.title('About')

        label = tkinter.Label(about, text = "Official Duino-Coin wallet", font="-weight bold").pack()
        label = tkinter.Label(about, text = "Wallet version: 0.5 alpha").pack()
        label = tkinter.Label(about, text = "Made by revox from Duino-Coin developers").pack()
        label = tkinter.Label(about, text = "Learn more at: github.com/revoxhere/duino-coin").pack()


def getBalance():
        global balance
        s.send(bytes("BALA", encoding='utf8'))
        time.sleep(0.025)
        balance = s.recv(6)
        balance = balance.decode('utf8')
        print("Got balance from server:", balance)

def WalletWindow():
        getBalance()
        global wallet
        
        print("Displaying main wallet window")
        wallet = tkinter.Tk()
        wallet.geometry("320x250")
        wallet.resizable(False, False)
        wallet.title("Duino-Coin wallet")

        
        photo = PhotoImage(file = "bg.gif")
        w = Label(wallet, image=photo)
        w.grid()
        
        label = tkinter.Label(wallet, text = "Official Duino-Coin wallet", font="-weight bold", background='white').place(relx=.5, rely=.09, anchor="c")
        label = tkinter.Label(wallet, text = "").grid()
        label = tkinter.Label(wallet, text = "Balance: "+balance+" DUCO", background='white').place(relx=.5, rely=.2, anchor="c")
        
        tkinter.Button(wallet, text = "    Send funds    ", command = Send).place(relx=0.3, rely=0.40)
        tkinter.Button(wallet, text = "  Receive funds  ", command = Receive).place(relx=0.3, rely=0.55)
        tkinter.Button(wallet, text = "        About        ", command = About).place(relx=0.3, rely=0.70)
        
        label = tkinter.Label(wallet, text = "2019 Duino-Coin developers", background='white').place(relx=0.46, rely=0.91)
        
        wallet.mainloop()
        
def Start():
        try:
                s.connect((host, port))
                print("Connected to the server")
                if not Path("config.ini").is_file():
                        SelectScr()
                else:
                        WalletScr()
        except:
                root = tkinter.Tk()
                root.withdraw()
                messagebox.showerror("Error!","Server communication failed!\nA server update is probably underway.\nPlease try again in a couple of hours.")
                sys.exit()

Start()


 
