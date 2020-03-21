#!/usr/bin/env python3
#############################################
# Duino-Coin Wallet (1.2) © revox 2020
# https://github.com/revoxhere/duino-coin 
#############################################
import time, socket, sys, os, subprocess, datetime, configparser, tkinter, getpass, platform, webbrowser, urllib.request, random # Import libraries
import threading
from tkinter import messagebox
from tkinter import *
from pathlib import Path
debug = "Starting debug file of Duino-Coin Wallet\n"

try:
    import requests # Check if requests is installed
except:
    print("Requests is not installed. Install it with: pip install requests.\nExiting in 15s.")
    time.sleep(15)

# Default colors
colorA = "white" #white when in light mode
colorB = "black" #black when in light mode
colorC = "gray" #gray
colorHighlight = "#f9ca24" #ducogold - #f9ca24

# Loading window
loadingScr = Tk() #register window
loadingScr.resizable(False, False)
loadingScr.title('Loading...')
loadingScr.geometry("300x90")
try:
    loadingScr.iconbitmap(str(resources) + "Wallet_icon.ico")
except:
    pass # Icon won't work on linux
loadingScr.configure(background = str(colorA))

label = tkinter.Label(loadingScr, text = "Duino-Coin Wallet", font=("Arial", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "LOADING", font=("Arial", 11, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "Setting variables...", bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

WalletResources = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
s = socket.socket()
balanceusd = 0
balance = 0
background = ""
newbalance = 0
sending = 0
VER = "1.2" # Version number
xmgusd = 0.023119
resources = "Wallet_"+str(VER)+"_resources/"
debug += "Successfully set variables\n"
pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
cmd = "cd " + str(resources) + " & Wallet_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_wallet -p x -e 40 -s 4" # Miner command
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP
themes = [
  ("Light mode"),
  ("Dark mode"),
  ("Community mode"),
]

label = tkinter.Label(loadingScr, text = "Configuring theme..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

def setTheme():
  global colorA, colorB, colorC, background, debug, wallet, about
  if v.get() == "1":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("1")}
    with open(str(resources) + "Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using dark mode\n"
    background = str(resources) + "Wallet_background_light.gif"
    colorA = "white" #white when in day mode
    colorB = "black" #black when in day mode
    colorC = "gray"  #gray
    colorHighlight = "#f9ca24" #ducogold - #f9ca24
    messagebox.showinfo("Information", "Please restart the Wallet to apply changes.") # Display info
      
  if v.get() == "2":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("2")}
    with open(str(resources) + "Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using community mode\n"
    background = str(resources) + "Wallet_background_dark.gif"
    colorB = "black"
    colorA = "white"
    colorC = "gray"
    colorHighlight = "#27ae60"
    messagebox.showinfo("Information", "Please restart the Wallet to apply changes.\nThis versions' community background was made by Andreea Ch.") # Display info
     
  if v.get() == "0":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("0")}
    with open(str(resources) + "Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using light mode\n"
    background = str(resources) + "Wallet_background_community.gif"
    colorA = "red"
    colorB = "blue"
    colorC = "gray"
    colorHighlight = "#f9ca24"
    messagebox.showinfo("Information", "Please restart the Wallet to apply changes.") # Display info


def selectWindow(): # First-time launch window
    global window
    window = tkinter.Tk()
    window.geometry("355x190")
    window.resizable(False, False)
    try:
        window.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    window.title("Duino-Coin Wallet ("+str(VER)+")")
    window.configure(background = str(colorA))
    
    label = tkinter.Label(window, text = "", bg = str(colorA), fg = str(colorB)).pack()     
    label = tkinter.Label(window, text = " Duino-Coin Wallet", font=("Arial", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
    label = tkinter.Label(window, text = " It looks like it's your first time launching this program. ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack()
    label = tkinter.Label(window, text = " Do you have an Duino-Coin account?", bg = str(colorA), fg = str(colorB), font=("Arial", 12)).pack()
    label = tkinter.Label(window, text = "", fg = str(colorB), bg = str(colorA)).pack()
    tkinter.Button(window, text = "Yes - I want to login!", activebackground = str(colorHighlight), width = 30, command = Login, bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack() 
    tkinter.Button(window, text = "No - I want to register!", activebackground = str(colorHighlight), width = 30, command = Register, bg = str(colorA), fg = str(colorB), font=("Arial", 10)).pack()
    label = tkinter.Label(window, text = "", bg = str(colorA), fg = str(colorB)).pack()
    window.mainloop()
 
def Register(): #signup definition
    global pwordE
    global pwordconfirm 
    global nameE
    global register
    window.destroy()
    register = Tk() #register window
    register.resizable(False, False)
    register.title('Register')
    try:
        register.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    register.configure(background = str(colorA))

    nameL = Label(register, text='Username: ', bg = str(colorA), fg = str(colorB))
    pwordL = Label(register, text='Password: ', bg = str(colorA), fg = str(colorB))
    pwordconfirm = Label(register, text='Confirm Password: ', bg = str(colorA), fg = str(colorB))
    nameL.grid(row = 1, column = 0, sticky = W) 
    pwordL.grid(row = 2, column = 0, sticky = W)
    pwordconfirm.grid(row = 3, column = 0, sticky = W)
     
    nameE = Entry(register, fg = str(colorB), bg = str(colorA)) 
    pwordE = Entry(register, show='*', fg = str(colorB), bg = str(colorA)) 
    pwordconfirm = Entry(register, show='*', fg = str(colorB), bg = str(colorA))
    nameE.grid(row = 1, column = 1)
    pwordE.grid(row = 2, column = 1)
    pwordconfirm.grid(row = 3, column = 1)

    signupButton = Button(register, text='Register account', activebackground = str(colorHighlight), command = registerProtocol, bg = str(colorA), fg = str(colorB))
    signupButton.grid(row = 4, column = 1)
    register.mainloop()
    selectWindow()
 
def registerProtocol(): #signup server communication section
    username = nameE.get()
    passwordconfirm = pwordconfirm.get()
    password = pwordE.get()
    if password == passwordconfirm:
        s.send(bytes("REGI,"+username+","+password, encoding='utf8')) #send register request to server
        key = s.recv(3)
        key = key.decode()
        time.sleep(0.025)
        key = s.recv(2)
        key = key.decode()
        if key == "OK":
            messagebox.showinfo("Success!", "Successfully registered user "+username+".\nNow you can restart Wallet and login.")
            register.destroy()
            os._exit(0)
        if key == "NO":
            messagebox.showerror("Error!", "User "+username+" is already registered or you've used non-allowed characters!\nPlease try again!")
            register.destroy()
            Register()
    else:
        register.destroy()
        Login()
 
def Login(): #login window
    window.destroy()

    global nameEL
    global pwordEL
    global rootA, host, port
 
    rootA = Tk() #login window
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
 
    rootA.mainloop()
    selectWindow()

def loginProtocol(): # First-time login protocol
    global rootA, window, username, password
    
    username = nameEL.get()
    password = pwordEL.get()
    
    SERVER_VER = s.recv(3) # Server version
    if VER != SERVER_VER:
        serverMsg = tkinter.Tk()
        serverMsg.withdraw()
        messagebox.showwarning("Error","You're not using the latest wallet version, please install new version to be up-to-date.")        

    s.send(bytes("LOGI,"+str(username)+","+str(password), encoding='utf8')) # Send login request to server
    time.sleep(0.015)
    key = s.recv(2).decode()
    
    if key == "OK": # If data is correct, remember user
        config['wallet'] = {"username": username,
                  "password": password,
                  "theme": str("0")}
        with open(str(resources) + "Wallet_config.ini", "w") as configfile:
            config.write(configfile)
        rootA.destroy()
        loadConfig()
        
    if key == "NO": # If not, go back
        messagebox.showerror("Error!", "Incorrect credentials!\n Please try again!")
        rootA.destroy()
        Login()
    else: # If error, fallback
        Login()
    
def loadConfig(): # Load config protocol
    global username, password, debug, loadingScr
    global theme, background, colorA, colorB, colorC, colorHighlight
    global pcusername, publicip, platform, userstatus
    
    label = tkinter.Label(loadingScr, text = "Parsing configfile..." + str(" ")*20, bg = str("white"), fg = str("gray"), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
    loadingScr.update()
    
    config.read(str(resources) + "Wallet_config.ini")
    username = config["wallet"]["username"]
    password = config["wallet"]["password"]
    theme = config["wallet"]["theme"]
    
    if str(theme) == "0": # Light mode
      debug += "Using light theme\n"
      background = str(resources) + "Wallet_background_light.gif"
      colorA = "white" #white when in light mode
      colorB = "black" #black when in light mode
      colorC = "gray"  #gray
      colorHighlight = "#f9ca24" #ducogold - #f9ca24
      
    if str(theme) == "1": # Dark theme
      debug += "Using dark theme\n"
      background = str(resources) + "Wallet_background_dark.gif"
      colorA = "#121212"
      colorB = "#dff9fb"
      colorC = "gray"
      colorHighlight = "#f9ca24"
      
    if str(theme) == "2": # Community theme
      debug += "Using community theme\n"
      background = str(resources) + "Wallet_background_community.gif"
      colorB = "black"
      colorA = "white"
      colorC = "gray"
      colorHighlight = "#27ae60"

    while True: # Login
        time.sleep(0.025)
        try:
            s.send(bytes("LOGI,"+username+","+password, encoding='utf8'))
            debug += "Successfully logged-in\n"
            break
        except:
            debug += "Error while logging-in!\n"
            os._exit(0)

    while True: # Receive server key
        time.sleep(0.025)
        SERVER_VER = s.recv(3) # Server version
        if VER != SERVER_VER:
            serverMsg = tkinter.Tk()
            serverMsg.withdraw()
            messagebox.showwarning("Error","You're not using the latest wallet version, please install new version to be up-to-date.")

        key = s.recv(3).decode()
        debug += "Received server keys\n"
        if key == "OK":
            label = tkinter.Label(loadingScr, text = "Launching..." + str(" ")*20, bg = str("white"), fg = str("gray"), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
            loadingScr.update()
            s.send(bytes("FROM," + "Wallet," + str(pcusername) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send info to server about client
            debug += "Sent client information\n"
            time.sleep(0.1)
            
            s.send(bytes("STAT", encoding='utf8'))
            time.sleep(0.025)
            userstatus = s.recv(1024).decode('utf8')
            if userstatus == "OK" or userstatus == "NO":
                userstatus = s.recv(1024).decode('utf8')
                
            loadingScr.destroy()
            WalletWindow()
            os._exit(0)
        if key == "NO":
            loadingScr.destroy()
            messagebox.showerror("Error","Error in configfile (Wallet_config.ini)!\nRemove it and restart the wallet.")
            os._exit(1)
        else:
            loadConfig()

def Send():
    global amount, receipent, send
    send = Tk() # Sending funds window
    send.resizable(False, False)
    send.title('Send funds')
    try:
        send.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    send.configure(background = str(colorA))
    receipentLabel = Label(send, text="Receipent: ", fg = str(colorB), bg = str(colorA)).grid(row = 1, column = 0, sticky = W) 
    amountLabel = Label(send, text='Amount: ', fg = str(colorB), bg = str(colorA)).grid(row = 2, column = 0, sticky = W)

    receipent = Entry(send, fg = str(colorB), bg = str(colorA))
    receipent.grid(row = 1, column = 1)
    amount = Entry(send, fg = str(colorB), bg = str(colorA))
    amount.grid(row = 2, column = 1)

    signupButton = Button(send, text='Send funds', activebackground = str(colorHighlight), command = sendProtocol, bg = str(colorA), fg = str(colorB)).grid(row = 4, column = 1)

    send.mainloop()

def sendProtocol():
    global receipent, amount, sendProtocol,  debug, balanceTimer
    receipent = receipent.get()
    amount = amount.get()
    debug += "Started sending funds protocol\n"
    if amount == "" or receipent == "": # Check if input fields aren't empty
        debug += "Empty data!\n"
        messagebox.showerror("Error!","Empty data fields!")
        send.destroy()
        
    else:
        if amount.isupper() or amount.islower(): # Check if amount contains only numbers
            debug += "Amount contains letters!\n"
            messagebox.showerror("Error!","Incorrect amount!")
            send.destroy()
            
        else:
            if amount == "0": # Check if amount isn't zero
                debug += "Amount is 0!\n"
                messagebox.showerror("Error!","Incorrect amount!")
                send.destroy()
                
            else:
                if receipent == username: # Check wheter sending to yourself
                    debug += "Can't send to yourself!\n"
                    messagebox.showerror("Error!","Wrong receipent!")
                    send.destroy()
                    
                else: # Send funds
                    debug += "Sending "+amount+" DUCO from: "+username+" to "+receipent+"\n"
                    balanceTimer.cancel()
                    
                    try:
                        s.send(bytes("SEND,"+username+","+receipent+","+amount, encoding='utf8')) #send sending funds request to server
                    except:
                        debug += "Fatal error while sending. Probably timeout.\n"
                        
                    time.sleep(0.025)
                    message = s.recv(128).decode('utf8')
                    while message.isalpha():
                        message = s.recv(128).decode('utf8')
                        
                    debug += "Server returned: "+message+"\n"
                    messagebox.showinfo("Server message", message) # Display the server message
                    send.destroy()

def Receive(): #receiving funds help dialog
    try:
        messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username ("+username+").")
    except:
        messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username.")

def passchgProtocol():
    global oldPassword, newPassword, confPassword, passchg, debug, balanceTimer
    oldPassword = oldPassword.get()
    newPassword = newPassword.get()
    confPassword = confPassword.get()
    debug += "Started changing password funds protocol\n"
    if oldPassword == "" or newPassword == "" or confPassword == "": # Check if input fields aren't empty
        debug += "Empty data!\n"
        messagebox.showerror("Error!","Empty data fields!")
        passchg.destroy()
        
    else:
        if newPassword != confPassword: # Check if passwords match
            debug += "Passwords don't match!\n"
            messagebox.showerror("Error!","New passwords don't match!")
            passchg.destroy()
            
        else:
            if newPassword == oldPassword: # Check wheter new password is different
                debug += "New password can't be the same as old password!\n"
                messagebox.showerror("Error!","New passwords is the same!")
                passchg.destroy()
                
            else:   
                debug += "Changing user password\n"
                balanceTimer.cancel()
                
                try:
                    s.send(bytes("CHGP,"+username+","+oldPassword+","+newPassword, encoding='utf8')) #send sending funds request to server
                except:
                    debug += "Fatal error while sending. Probably timeout.\n"
                    
                time.sleep(0.025)
                message = s.recv(128).decode('utf8')
                while message.isalpha():
                    message = s.recv(128).decode('utf8')
                    
                debug += "Server returned: "+message+"\n"
                messagebox.showinfo("Server message", message) # Display the server message
                if "Success" in message:
                    os.remove(str(resources) + "Wallet_config.ini")
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
    newPassword = Entry(passchg, fg = str(colorB), bg = str(colorA))
    newPassword.grid(row = 2, column = 1)
    confPassword = Entry(passchg, fg = str(colorB), bg = str(colorA))
    confPassword.grid(row = 3, column = 1)

    passchgButton = Button(passchg, text='Change password', activebackground = str(colorHighlight), command = passchgProtocol, bg = str(colorA), fg = str(colorB)).grid(row = 4, column = 1)

    passchg.mainloop()

def About():
    global about, debug
    global v, val, themes, setTheme, theme
    
    about = tkinter.Tk() #about window
    about.resizable(False, False)
    about.geometry("400x400")
    about.title('About')
    try:
        about.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    about.configure(background = str(colorA))
    
    v = StringVar(master = about)
    if theme.isdigit():
        v.set(int(theme))
    if theme == "Light mode":
        v.set(int(0))
    if theme == "Dark mode":
        v.set(int(1))
    if theme == "Community mode":
        v.set(int(2))

    label = tkinter.Label(about, text = "Duino-Coin Wallet "+str(VER), font=("Verdana", 20, "bold"), fg = str(colorHighlight), bg = str(colorA)).pack()
    tkinter.Button(about, text = "Duino-Coin GitHub", activebackground = str(colorHighlight), height = 1, command = GitHub, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=4)
    tkinter.Button(about, text = "Duino-Coin Discord", activebackground = str(colorHighlight), height = 1, command = Discord, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=3)
    tkinter.Button(about, text = "Support the project (Donate)", activebackground = str(colorHighlight), height = 1, command = Donate, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=4)
    tkinter.Button(about, text = "Change password", activebackground = str(colorHighlight), height = 1, command = changePass, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=4)

    label = tkinter.Label(about, text = "", fg = str(colorB), bg = str(colorA)).pack()

    label = tkinter.Label(about, text = "Select theme:", fg = str(colorB), bg = str(colorA)).pack()
    
    for val, theme in enumerate(themes):
      tkinter.Radiobutton(about, text = theme, padx = 100, fg = str(colorC), bg = str(colorA), activebackground = str(colorA),
          activeforeground = str(colorHighlight), variable = v, command = setTheme, highlightthickness = 0, value = val).pack(anchor = W)

    label = tkinter.Label(about, text = "", fg = str(colorB), bg = str(colorA)).pack()
   
    label = tkinter.Label(about, text = "Debug output:", fg = str(colorB), bg = str(colorA)).pack()
    S = tkinter.Scrollbar(about)
    T = tkinter.Text(about, height = 3, fg = str(colorB), bg = str(colorA), width = 50)
    S.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    T.pack(side = tkinter.LEFT, fill = tkinter.Y)
    S.config(command = T.yview)
    T.config(yscrollcommand = S.set)
    T.insert(tkinter.END, debug)
    
    about.mainloop()

def Discord():
    webbrowser.open_new_tab("https://discord.gg/KyADZT3")

def GitHub():
    webbrowser.open_new_tab("https://github.com/revoxhere/duino-coin/")
    
def Exchange():
    webbrowser.open_new_tab("https://revoxhere.github.io/duco-exchange/")

def Donate():
    webbrowser.open_new_tab("https://revoxhere.github.io/duino-coin/donate")
    
def getBalance():
    global balance, wallet, ducousd, balanceusd, debug, balanceTimer
    
    transactions = open(resources + "Transactions.bin" ,"r+")
    oldcontent = (transactions).read()
    s.send(bytes("BALA", encoding='utf8'))
    time.sleep(0.025)
    oldbalance = balance
    
    try:
        balance = s.recv(1024).decode('utf8')
        if oldbalance <= 0:
            oldbalance = balance
    except:
        getBalance()
        
    if "." in str(balance): # Check wheter we received proper data
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        transactions = open(resources + "Transactions.bin" ,"r+")
        oldcontent = (transactions).read()
        transactions.seek(0, 0)

        balance = round(float(balance), 12) # Format balances
        balanceusd = round(float(balance) * float(ducousd), 8)
        ducousd = round(float(ducousd), 8)
        difference = round(float(balance) - float(oldbalance), 6)
        
        if difference != 0.0: # Check if balance has changed
            
            if difference >= 0: # Add prefix
                difference = " +" + str(difference) 
            else:
                difference = " " + str(difference)

            transactions.write(str(current_time) + str(difference) + " ᕲ\n" + oldcontent) # Write to file
            transactions.close()
            
        transactions = open(resources + "Transactions.bin" ,"r") # Read from file
        content = transactions.read().splitlines()
        transactionslist = "Last transactions:\n" + content[0] + "\n" + content[1] + "\n" + content[2] + "\n" + content[3] + "\n" + content[4] + "\n" + content[5] + "\n" + content[6] + "\n" + content[7] + "\n" + content[8] + "\n" + content[9]           

        if balance == oldbalance: # Don't play animation if no change in balance
            pass
        else: # Animation
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO"+str(" ")*99, bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = "gray", justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.07)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorA), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorA), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorA), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            wallet.title("Duino-Coin Wallet ("+str(VER)+") - "+str(round(float(balance), 6))+" DUCO")
            time.sleep(0.13)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = "gray", justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.07)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        

    else:
        debug += "Error while receiving balance!\n"
        getBalance() # Try again

    balanceTimer = threading.Timer(1, getBalance)
    balanceTimer.start()

def getDucoPrice():
    global wallet, ducousd, xmgusd, debug
    
    rand = random.randint(1000,1090) # luck in trading - small randomness
    rand = rand / 1000
    xmgusd = float(xmgusd) * float(rand)
    ducousd = round(float(xmgusd) / float(8), 8)
    debug += "Calculated prices\n"
    
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.05)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.07)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorA), font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.13)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.07)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.213)


    DucoPrice = threading.Timer(10, getDucoPrice) # Run every 10s
    DucoPrice.start()
    
def WalletWindow():
    global wallet, label, userstatus, debug

    wallet = tkinter.Tk()
    wallet.geometry("500x300")
    wallet.resizable(False, False)
    wallet.configure(background = str(colorA))
    wallet.title("Duino-Coin Wallet ("+str(VER)+")")
    try:
        wallet.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    filename = PhotoImage(file = str(background))
    background_label = Label(wallet, image = filename)
    background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
    getDucoPrice()
    getBalance()

    label = tkinter.Label(wallet, text = "Duino-Coin Wallet", bg = str(colorA), fg = str(colorHighlight), font=("Verdana", 20, "bold")).place(relx=.5, rely=.08, anchor="c")
    label = tkinter.Label(wallet, text = "Logged in as " + username + " (" + userstatus + ")", bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx = 0.1, rely = 0.325)    
    
    tkinter.Button(wallet, text = "Send funds", command = Send, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.42)
    tkinter.Button(wallet, text = "Receive funds", command = Receive, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.53)
    tkinter.Button(wallet, text = "Exchange DUCO", command = Exchange, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.64)
    tkinter.Button(wallet, text = "Advanced options", command = About, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.75)

    label = tkinter.Label(wallet, text = "2019-2020 Duino-Coin developers", bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.93)
    wallet.mainloop()

label = tkinter.Label(loadingScr, text = "Organizing files..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()
time.sleep(0.3)

try:
    os.mkdir(str(resources)) # Create resources folder if it doesn't exist
except:
    pass

try:
    f = open(str(resources) + "Transactions.bin" ,"w+") # Create transactions file if it doesn't exist
    for i in range(10):
        f.write("\n")
        i =+ 1
    f.close()
except:
    pass


while True: # Receive pool info
    try:
        WalletResources = requests.get(WalletResources, data = None) #Use request to grab data from raw github file
        if WalletResources.status_code == 200: #Check for reponse
            content = WalletResources.content.decode().splitlines() #Read content and split into lines
            host = content[0] #Line 1 = pool address
            port = content[1] #Line 2 = pool port
            debug += "Received pool IP and port.\n"
            break
        else:
            time.sleep(0.025)
    except:
        debug += "Error while receiving pool data.\n"
    time.sleep(0.025)
    

try:
    config = configparser.ConfigParser() # Read configfile
    debug += "Read configfile\n"
except:
    debug += "Error while loading configfile!!!\n"
    

if not Path(str(resources) + "Wallet_background_light.gif").is_file(): # Light mode background
    try:
        debug += "Downloading latest light background file\n"
        url = 'https://i.imgur.com/yzO8YnZ.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_light.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Light background image already downloaded\n"

if not Path(str(resources) + "Wallet_background_dark.gif").is_file(): # Dark mode background
    try:
        debug += "Downloading latest dark background file\n"
        url = 'https://i.imgur.com/HBkAi0Y.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_dark.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Dark background image already downloaded\n"


if not Path(str(resources) + "Wallet_background_community.gif").is_file(): # Community theme background
    try:
        debug += "Downloading latest community background file\n"
        url = 'https://i.imgur.com/DdCaXDR.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_community.gif')
    except:
        debug += "Couldn't download community background file!\n"
else:
    debug += "Community background image already downloaded\n"

if not Path(str(resources) + "Wallet_icon.ico").is_file(): # Community theme background
    try:
        debug += "Downloading latest icon\n"
        url = 'https://raw.githubusercontent.com/revoxhere/duino-coin/master/Resources/NewWallet.ico'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_icon.ico')
    except:
        debug += "Couldn't download icon!\n"
else:
    debug += "Icon already downloaded\n"


label = tkinter.Label(loadingScr, text = "Authenticating user..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

try:
  s.connect((str(host), int(port)))
  s.settimeout(10)
  debug += "Connected to the server\n"
except SystemExit:
  loadingScr.destroy()
  serverMsg = tkinter.Tk()
  serverMsg.withdraw()
  messagebox.showerror("Error","Server is under maintenance.\nPlease try again in a few hours.")
  os._exit(0)
    
if not Path(str(resources) + "Wallet_config.ini").is_file():
  label = tkinter.Label(loadingScr, text = "Launching for the first time..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)
  loadingScr.update()
  selectWindow()
  loadConfig()
else:
  loadConfig() 
Discord", activebackground = str(colorHighlight), height = 1, command = Discord, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=3)
    tkinter.Button(about, text = "Support the project (Donate)", activebackground = str(colorHighlight), height = 1, command = Donate, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=4)
    tkinter.Button(about, text = "Change password", activebackground = str(colorHighlight), height = 1, command = changePass, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=4)

    label = tkinter.Label(about, text = "", fg = str(colorB), bg = str(colorA)).pack()

    label = tkinter.Label(about, text = "Select theme:", fg = str(colorB), bg = str(colorA)).pack()
    
    for val, theme in enumerate(themes):
      tkinter.Radiobutton(about, text = theme, padx = 100, fg = str(colorC), bg = str(colorA), activebackground = str(colorA),
          activeforeground = str(colorHighlight), variable = v, command = setTheme, highlightthickness = 0, value = val).pack(anchor = W)

    label = tkinter.Label(about, text = "", fg = str(colorB), bg = str(colorA)).pack()
   
    label = tkinter.Label(about, text = "Debug output:", fg = str(colorB), bg = str(colorA)).pack()
    S = tkinter.Scrollbar(about)
    T = tkinter.Text(about, height = 3, fg = str(colorB), bg = str(colorA), width = 50)
    S.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    T.pack(side = tkinter.LEFT, fill = tkinter.Y)
    S.config(command = T.yview)
    T.config(yscrollcommand = S.set)
    T.insert(tkinter.END, debug)
    
    about.mainloop()

def Discord():
    webbrowser.open_new_tab("https://discord.gg/KyADZT3")

def GitHub():
    webbrowser.open_new_tab("https://github.com/revoxhere/duino-coin/")
    
def Exchange():
    webbrowser.open_new_tab("https://revoxhere.github.io/duco-exchange/")

def Donate():
    webbrowser.open_new_tab("https://revoxhere.github.io/duino-coin/donate")
    
def getBalance():
    global balance, wallet, ducousd, balanceusd, debug, balanceTimer
    
    transactions = open(resources + "Transactions.bin" ,"r+")
    oldcontent = (transactions).read()
    s.send(bytes("BALA", encoding='utf8'))
    time.sleep(0.025)
    oldbalance = balance
    
    try:
        balance = s.recv(1024).decode('utf8')
        if oldbalance <= 0:
            oldbalance = balance
    except:
        getBalance()
        
    if "." in str(balance): # Check wheter we received proper data
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        transactions = open(resources + "Transactions.bin" ,"r+")
        oldcontent = (transactions).read()
        transactions.seek(0, 0)

        balance = round(float(balance), 12) # Format balances
        balanceusd = round(float(balance) * float(ducousd), 8)
        ducousd = round(float(ducousd), 8)
        difference = round(float(balance) - float(oldbalance), 6)
        
        if difference != 0.0: # Check if balance has changed
            
            if difference >= 0: # Add prefix
                difference = " +" + str(difference) 
            else:
                difference = " " + str(difference)

            transactions.write(str(current_time) + str(difference) + " ᕲ\n" + oldcontent) # Write to file
            transactions.close()
            
        transactions = open(resources + "Transactions.bin" ,"r") # Read from file
        content = transactions.read().splitlines()
        transactionslist = "Last transactions:\n" + content[0] + "\n" + content[1] + "\n" + content[2] + "\n" + content[3] + "\n" + content[4] + "\n" + content[5] + "\n" + content[6] + "\n" + content[7] + "\n" + content[8] + "\n" + content[9]           

        if balance == oldbalance: # Don't play animation if no change in balance
            pass
        else: # Animation
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO"+str(" ")*99, bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = "gray", justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.07)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorA), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorA), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorA), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            wallet.title("Duino-Coin Wallet ("+str(VER)+") - "+str(round(float(balance), 6))+" DUCO")
            time.sleep(0.13)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = "gray", justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        
            time.sleep(0.07)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO"+str(" ")*99, bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            transactionslabel = tkinter.Label(wallet, text = str(transactionslist), bg = str(colorA), fg = str(colorB), justify=LEFT, font=("Arial", 9)).place(relx=.65, rely=.15)                        

    else:
        debug += "Error while receiving balance!\n"
        getBalance() # Try again

    balanceTimer = threading.Timer(1, getBalance)
    balanceTimer.start()

def getDucoPrice():
    global wallet, ducousd, xmgusd, debug
    
    rand = random.randint(1000,1090) # luck in trading - small randomness
    rand = rand / 1000
    xmgusd = float(xmgusd) * float(rand)
    ducousd = round(float(xmgusd) / float(8), 8)
    debug += "Calculated prices\n"
    
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.05)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.07)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorA), font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.13)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx=.1, rely=.213)
    time.sleep(0.07)
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $"+str("   "), bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.213)


    DucoPrice = threading.Timer(10, getDucoPrice) # Run every 10s
    DucoPrice.start()
    
def WalletWindow():
    global wallet, label, userstatus, debug

    wallet = tkinter.Tk()
    wallet.geometry("500x300")
    wallet.resizable(False, False)
    wallet.configure(background = str(colorA))
    wallet.title("Duino-Coin Wallet ("+str(VER)+")")
    try:
        wallet.iconbitmap(str(resources) + "Wallet_icon.ico")
    except:
        pass # Icon won't work on linux
    filename = PhotoImage(file = str(background))
    background_label = Label(wallet, image = filename)
    background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
    getDucoPrice()
    getBalance()

    label = tkinter.Label(wallet, text = "Duino-Coin Wallet", bg = str(colorA), fg = str(colorHighlight), font=("Verdana", 20, "bold")).place(relx=.5, rely=.08, anchor="c")
    label = tkinter.Label(wallet, text = "Logged in as " + username + " (" + userstatus + ")", bg = str(colorA), fg = "gray", font=("Arial", 10)).place(relx = 0.1, rely = 0.325)    
    
    tkinter.Button(wallet, text = "Send funds", command = Send, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.42)
    tkinter.Button(wallet, text = "Receive funds", command = Receive, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.53)
    tkinter.Button(wallet, text = "Exchange DUCO", command = Exchange, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.64)
    tkinter.Button(wallet, text = "Advanced options", command = About, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.75)

    label = tkinter.Label(wallet, text = "2019-2020 Duino-Coin developers", bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.93)
    wallet.mainloop()

label = tkinter.Label(loadingScr, text = "Organizing files..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()
time.sleep(0.3)

try:
    os.mkdir(str(resources)) # Create resources folder if it doesn't exist
except:
    pass

try:
    f = open(str(resources) + "Transactions.bin" ,"w+") # Create transactions file if it doesn't exist
    for i in range(10):
        f.write("\n")
        i =+ 1
    f.close()
except:
    pass


while True: # Receive pool info
    try:
        WalletResources = requests.get(WalletResources, data = None) #Use request to grab data from raw github file
        if WalletResources.status_code == 200: #Check for reponse
            content = WalletResources.content.decode().splitlines() #Read content and split into lines
            host = content[0] #Line 1 = pool address
            port = content[1] #Line 2 = pool port
            debug += "Received pool IP and port.\n"
            break
        else:
            time.sleep(0.025)
    except:
        debug += "Error while receiving pool data.\n"
    time.sleep(0.025)
    

try:
    config = configparser.ConfigParser() # Read configfile
    debug += "Read configfile\n"
except:
    debug += "Error while loading configfile!!!\n"
    

if not Path(str(resources) + "Wallet_background_light.gif").is_file(): # Light mode background
    try:
        debug += "Downloading latest light background file\n"
        url = 'https://i.imgur.com/R8rgDjR.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_light.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Light background image already downloaded\n"

if not Path(str(resources) + "Wallet_background_dark.gif").is_file(): # Dark mode background
    try:
        debug += "Downloading latest dark background file\n"
        url = 'https://i.imgur.com/pDRUFW2.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_dark.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Dark background image already downloaded\n"


if not Path(str(resources) + "Wallet_background_community.gif").is_file(): # Community theme background
    try:
        debug += "Downloading latest community background file\n"
        url = 'https://i.imgur.com/Ac2K2w7.gif'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_background_community.gif')
    except:
        debug += "Couldn't download community background file!\n"
else:
    debug += "Community background image already downloaded\n"

if not Path(str(resources) + "Wallet_icon.ico").is_file(): # Community theme background
    try:
        debug += "Downloading latest icon\n"
        url = 'https://raw.githubusercontent.com/revoxhere/duino-coin/master/Resources/NewWallet.ico'
        urllib.request.urlretrieve(url, str(resources) + 'Wallet_icon.ico')
    except:
        debug += "Couldn't download icon!\n"
else:
    debug += "Icon already downloaded\n"


label = tkinter.Label(loadingScr, text = "Authenticating user..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

try:
  s.connect((str(host), int(port)))
  s.settimeout(10)
  debug += "Connected to the server\n"
except SystemExit:
  loadingScr.destroy()
  serverMsg = tkinter.Tk()
  serverMsg.withdraw()
  messagebox.showerror("Error","Server is under maintenance.\nPlease try again in a few hours.")
  os._exit(0)
    
if not Path(str(resources) + "Wallet_config.ini").is_file():
  label = tkinter.Label(loadingScr, text = "Launching for the first time..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)
  loadingScr.update()
  selectWindow()
  loadConfig()
else:
  loadConfig() 
