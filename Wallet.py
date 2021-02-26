#!/usr/bin/env python3
##########################################
# Duino-Coin Tkinter GUI Wallet (v2.2)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
from tkinter import (
    Tk,
    Label,
    Frame,
    Entry,
    StringVar,
    IntVar,
    Button,
    PhotoImage,
    Listbox,
    Scrollbar,
    Checkbutton,
    Toplevel,
    ttk,
)
from tkinter.font import Font
from tkinter import LEFT, BOTH, RIGHT, END, N, E, S, W
from webbrowser import open_new_tab
from urllib.request import urlopen, urlretrieve
from pathlib import Path
import socket, sys
import sqlite3
from threading import Timer
import threading
from time import sleep, time
from os import _exit, mkdir, execl
import datetime
from tkinter import messagebox
from base64 import b64encode, b64decode
from requests import get
from json import loads
from configparser import ConfigParser
import json
import subprocess, os


version = 2.2
config = ConfigParser()
resources = "Wallet_" + str(version) + "_resources/"
backgroundColor = "#121212"
fontColor = "#FAFAFA"
foregroundColor = "#f0932b"
foregroundColorSecondary = "#ffbe76"
min_trans_difference = 0.00000000001  # Minimum transaction amount to be saved
min_trans_difference_notify = 0.5  # Minimum transaction amount to show a notification
wrong_passphrase = False
iterations = 100_000
globalBalance = 0


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    os.execl(sys.executable, sys.executable, *sys.argv)


try:
    from pypresence import Presence
except:
    print(
        'Pypresence is not installed. Wallet will try to install it. If it fails, please manually install "pypresence" python3 package.'
    )
    install("pypresence")

try:
    from PIL import Image, ImageTk
except:
    print(
        'Pillow is not installed. Wallet will try to install it. If it fails, please manually install "Pillow" python3 package.'
    )
    install("Pillow")

try:
    import pystray
except:
    print("Pystray is not installed. Continuing without using tray support")
    disableTray = True
else:
    disableTray = False

try:
    from notifypy import Notify
except:
    print("Notifypy is not installed. Continuing without notification system")
    notificationsEnabled = False
else:
    notificationsEnabled = True

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    backend = default_backend()
except ModuleNotFoundError:
    now = datetime.datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + "Cryptography is not installed. Please install it using: python3 -m pip install cryptography.\nExiting in 15s."
    )
    sleep(15)
    os._exit(1)


try:
    import secrets
except ModuleNotFoundError:
    now = datetime.datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + "Secrets is not installed. Please install it using: python3 -m pip install secrets.\nExiting in 15s."
    )
    sleep(15)
    os._exit(1)

try:
    from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
except:
    now = datetime.datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + "Base64 is not installed. Please install it using: python3 -m pip install base64.\nExiting in 15s."
    )
    sleep(15)
    os._exit(1)

try:
    import tronpy
    from tronpy.keys import PrivateKey

    tronpy_installed = True
except ModuleNotFoundError:
    tronpy_installed = False
    now = datetime.datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + "Tronpy is not installed. Please install it using: python3 -m pip install tronpy.\nWrapper was disabled because of tronpy is needed for !"
    )
else:
    tron = tronpy.Tron()
    tron = tronpy.Tron()
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U")


def GetDucoPrice():
    global ducofiat
    jsonapi = get(
        "https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json",
        data=None,
    )
    if jsonapi.status_code == 200:
        try:
            content = jsonapi.content.decode()
            contentjson = loads(content)
            ducofiat = round(float(contentjson["Duco price"]), 4)
        except:
            ducofiat = 0.003
    else:
        ducofiat = 0.003
    Timer(30, GetDucoPrice).start()


def title(title):
    if os.name == "nt":
        os.system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend,
    )
    return b64e(kdf.derive(password))


def password_encrypt(
    message: bytes, password: str, iterations: int = iterations
) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b"%b%b%b"
        % (
            salt,
            iterations.to_bytes(4, "big"),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def password_decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iterations, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iterations, "big")
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Login")
        master.resizable(False, False)

        textFont2 = Font(size=12, weight="bold")
        textFont = Font(size=12, weight="normal")

        self.duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
        self.duco.image = self.duco
        self.ducoLabel = Label(
            self, background=foregroundColor, foreground=fontColor, image=self.duco
        )
        self.ducoLabel2 = Label(
            self,
            background=foregroundColor,
            foreground=fontColor,
            text="Welcome to the\nDuino-Coin\nTkinter GUI Wallet",
            font=textFont2,
        )
        self.spacer = Label(self)

        self.label_username = Label(
            self,
            text="USERNAME",
            font=textFont2,
            background=backgroundColor,
            foreground=fontColor,
            padx=5,
        )
        self.label_password = Label(
            self,
            text="PASSWORD",
            font=textFont2,
            background=backgroundColor,
            foreground=fontColor,
            padx=5,
        )
        self.entry_username = Entry(
            self,
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )
        self.entry_password = Entry(
            self,
            show="*",
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )

        self.ducoLabel.grid(row=0, sticky="nswe", pady=(5, 0), padx=(5))
        self.ducoLabel2.grid(row=1, sticky="nswe", padx=(5))
        self.label_username.grid(row=4, sticky=W, pady=(5, 0))
        self.entry_username.grid(row=5, sticky=N, padx=(5))
        self.label_password.grid(row=6, sticky=W)
        self.entry_password.grid(row=7, sticky=N)

        self.var = IntVar()
        self.checkbox = Checkbutton(
            self,
            text="Keep me logged in",
            background=backgroundColor,
            activebackground=backgroundColor,
            selectcolor=backgroundColor,
            activeforeground=foregroundColor,
            foreground=fontColor,
            variable=self.var,
            font=textFont,
            borderwidth="0",
            highlightthickness="0",
        )
        self.checkbox.grid(columnspan=2, sticky=W, pady=(5))

        self.logbtn = Button(
            self,
            text="LOGIN",
            foreground=foregroundColor,
            background=backgroundColor,
            activebackground=backgroundColor,
            command=self._login_btn_clicked,
            font=textFont2,
        )
        self.logbtn.grid(columnspan=2, sticky="nswe", padx=(5), pady=(0, 1))

        self.regbtn = Button(
            self,
            text="REGISTER",
            foreground=foregroundColor,
            background=backgroundColor,
            activebackground=backgroundColor,
            command=self._register_btn_clicked,
            font=textFont2,
        )
        self.regbtn.grid(columnspan=2, sticky="nswe", padx=(5), pady=(0, 5))

        self.configure(background=backgroundColor)
        self.pack()

    def _login_btn_clicked(self):
        global username, password
        username = self.entry_username.get()
        password = self.entry_password.get()
        keeplogedin = self.var.get()

        if username and password:
            soc = socket.socket()
            soc.connect((pool_address, int(pool_port)))
            soc.recv(3)
            soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
            response = soc.recv(64).decode("utf8")
            response = response.split(",")

            if response[0] == "OK":
                if keeplogedin >= 1:
                    passwordEnc = b64encode(bytes(password, encoding="utf8"))
                    with sqlite3.connect(f"{resources}/wallet.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            """INSERT INTO UserData(username, password, useWrapper) VALUES(?, ?, ?)""",
                            (username, passwordEnc, "False"),
                        )
                        con.commit()
                root.destroy()
            else:
                messagebox.showerror(title="Error loging-in", message=response[1])
        else:
            messagebox.showerror(
                title="Error loging-in", message="Fill in the blanks first"
            )

    def _registerprotocol(self):
        emailS = email.get()
        usernameS = username.get()
        passwordS = password.get()
        confpasswordS = confpassword.get()

        if emailS and usernameS and passwordS and confpasswordS:
            if passwordS == confpasswordS:
                soc = socket.socket()
                soc.connect((pool_address, int(pool_port)))
                soc.recv(3)
                soc.send(
                    bytes(
                        f"REGI,{str(usernameS)},{str(passwordS)},{str(emailS)}",
                        encoding="utf8",
                    )
                )
                response = soc.recv(128).decode("utf8")
                response = response.split(",")

                if response[0] == "OK":
                    messagebox.showinfo(
                        title="Registration successfull",
                        message="New user has been registered sucessfully. You can now login",
                    )
                    register.destroy()
                    execl(sys.executable, sys.executable, *sys.argv)
                else:
                    messagebox.showerror(
                        title="Error registering user", message=response[1]
                    )
            else:
                messagebox.showerror(
                    title="Error registering user", message="Passwords don't match"
                )
        else:
            messagebox.showerror(
                title="Error registering user", message="Fill in the blanks first"
            )

    def _register_btn_clicked(self):
        global username, password, confpassword, email, register
        root.destroy()
        register = Tk()
        register.title("Register")
        register.resizable(False, False)

        textFont2 = Font(register, size=12, weight="bold")
        textFont = Font(register, size=12, weight="normal")

        duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
        duco.image = duco
        ducoLabel = Label(
            register, background=foregroundColor, foreground=fontColor, image=duco
        )
        ducoLabel2 = Label(
            register,
            background=foregroundColor,
            foreground=fontColor,
            text="Register on network",
            font=textFont2,
        )
        ducoLabel.grid(row=0, padx=5, pady=(5, 0), sticky="nswe")
        ducoLabel2.grid(row=1, padx=5, sticky="nswe")

        Label(
            register,
            text="USERNAME",
            background=backgroundColor,
            foreground=fontColor,
            font=textFont2,
        ).grid(row=3, sticky=W, padx=5, pady=(5, 0))
        username = Entry(
            register,
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )
        username.grid(row=4, padx=5)

        Label(
            register,
            text="PASSWORD",
            background=backgroundColor,
            foreground=fontColor,
            font=textFont2,
        ).grid(row=5, sticky=W, padx=5)
        password = Entry(
            register,
            show="*",
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )
        password.grid(row=6, padx=5)

        Label(
            register,
            text="CONFIRM PASSWORD",
            background=backgroundColor,
            foreground=fontColor,
            font=textFont2,
        ).grid(row=7, sticky=W, padx=5)
        confpassword = Entry(
            register,
            show="*",
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )
        confpassword.grid(row=8, padx=5)

        Label(
            register,
            text="E-MAIL",
            background=backgroundColor,
            foreground=fontColor,
            font=textFont2,
        ).grid(row=9, sticky=W)
        email = Entry(
            register,
            font=textFont,
            background=backgroundColor,
            foreground=foregroundColorSecondary,
        )
        email.grid(row=10, padx=5)

        self.logbtn = Button(
            register,
            text="REGISTER",
            activebackground=backgroundColor,
            foreground=foregroundColor,
            background=backgroundColor,
            command=self._registerprotocol,
            font=textFont2,
        )
        self.logbtn.grid(columnspan=2, sticky="nswe", padx=(5, 5), pady=(5, 5))
        register.configure(background=backgroundColor)


def LoadingWindow():
    global loading, status
    loading = Tk()
    loading.resizable(False, False)
    loading.configure(background=backgroundColor)
    loading.title("Loading")
    try:
        loading.iconphoto(True, PhotoImage(file=resources + "duco.png"))
    except:
        pass
    textFont = Font(loading, size=10, weight="bold")
    textFont2 = Font(loading, size=14, weight="bold")

    Label(
        loading,
        text="DUINO-COIN WALLET",
        font=textFont2,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=0, column=0, sticky=S + W, pady=5, padx=5)
    loading.update()

    status = Label(
        loading,
        background=backgroundColor,
        foreground=fontColor,
        text="Loading database...",
        font=textFont,
    )
    status.grid(row=1, column=0, sticky=S + W, pady=(0, 5), padx=5)
    loading.update()


if not Path(resources + "duco.png").is_file():
    urlretrieve("https://i.imgur.com/9JzxR0B.png", resources + "duco.png")
if not Path(resources + "calculator.png").is_file():
    urlretrieve("https://i.imgur.com/iqE28Ej.png", resources + "calculator.png")
if not Path(resources + "exchange.png").is_file():
    urlretrieve("https://i.imgur.com/0qMtoZ7.png", resources + "exchange.png")
if not Path(resources + "discord.png").is_file():
    urlretrieve("https://i.imgur.com/LoctALa.png", resources + "discord.png")
if not Path(resources + "github.png").is_file():
    urlretrieve("https://i.imgur.com/PHEfWbl.png", resources + "github.png")
if not Path(resources + "settings.png").is_file():
    urlretrieve("https://i.imgur.com/NNEI4WL.png", resources + "settings.png")
if not Path(resources + "transactions.png").is_file():
    urlretrieve("https://i.imgur.com/nbVPlKk.png", resources + "transactions.png")
if not Path(resources + "stats.png").is_file():
    urlretrieve("https://i.imgur.com/KRfHZUM.png", resources + "stats.png")

with sqlite3.connect(f"{resources}/wallet.db") as con:
    cur = con.cursor()
    cur.execute("SELECT COUNT(username) FROM UserData")
    userdata_count = cur.fetchall()[0][0]
if userdata_count != 1:
    root = Tk()
    lf = LoginFrame(root)
    root.mainloop()
else:
    LoadingWindow()
    with sqlite3.connect(f"{resources}/wallet.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM UserData")
        userdata_query = cur.fetchone()
        username = userdata_query[0]
        passwordEnc = (userdata_query[1]).decode("utf-8")
        password = b64decode(passwordEnc).decode("utf8")
    status.config(text="Preparing wallet window...")
    loading.update()


def openGitHub(handler):
    open_new_tab("https://github.com/revoxhere/duino-coin")


def openWebsite(handler):
    open_new_tab("https://duinocoin.com")


def openExchange(handler):
    open_new_tab("https://revoxhere.github.io/duco-exchange/")


def openDiscord(handler):
    open_new_tab("https://discord.com/invite/kvBkccy")


def openTransactions(handler):
    transactionsWindow = Toplevel()
    transactionsWindow.resizable(False, False)
    transactionsWindow.title("Duino-Coin Wallet - Transactions")
    transactionsWindow.transient([root])
    transactionsWindow.configure(background=backgroundColor)

    textFont3 = Font(transactionsWindow, size=14, weight="bold")
    textFont = Font(transactionsWindow, size=12, weight="normal")

    Label(
        transactionsWindow,
        text="LOCAL TRANSACTION LIST",
        font=textFont3,
        background=backgroundColor,
        foreground=foregroundColor,
    ).grid(row=0, column=0, columnspan=2, sticky=S + W, pady=(5, 0), padx=5)
    Label(
        transactionsWindow,
        text="Still a work in progress version",
        font=textFont,
        foreground=fontColor,
        background=backgroundColor,
    ).grid(row=1, column=0, columnspan=2, sticky=S + W, padx=5)

    listbox = Listbox(
        transactionsWindow, width="35", background=backgroundColor, foreground=fontColor
    )
    listbox.grid(row=2, column=0, sticky=S + W + N + E, padx=(5, 0), pady=(0, 5))
    scrollbar = Scrollbar(transactionsWindow, background=backgroundColor)
    scrollbar.grid(row=2, column=1, sticky=N + S, padx=(0, 5), pady=(0, 5))

    with sqlite3.connect(f"{resources}/wallet.db") as con:
        cur = con.cursor()
        cur.execute("SELECT rowid,* FROM Transactions ORDER BY rowid DESC")
        Transactions = cur.fetchall()
    for i, row in enumerate(Transactions, start=1):
        listbox.insert(END, f"{str(row[1])}  {row[2]} DUCO")

    listbox.config(yscrollcommand=scrollbar.set, font=textFont)
    scrollbar.config(command=listbox.yview)


def currencyConvert():
    fromcurrency = fromCurrencyInput.get(fromCurrencyInput.curselection())
    tocurrency = toCurrencyInput.get(toCurrencyInput.curselection())
    amount = amountInput.get()
    try:
        if fromcurrency != "DUCO":
            currencyapi = get(
                "https://api.exchangeratesapi.io/latest?base=" + str(fromcurrency),
                data=None,
            )
            exchangerates = loads(currencyapi.content.decode())
        else:
            currencyapi = get(
                "https://api.exchangeratesapi.io/latest?base=USD", data=None
            )
            exchangerates = loads(currencyapi.content.decode())

        if currencyapi.status_code == 200:  # Check for reponse
            if fromcurrency == "DUCO" and tocurrency != "DUCO":
                exchangerates = loads(currencyapi.content.decode())
                result = (
                    str(
                        round(
                            float(amount)
                            * float(ducofiat)
                            * float(exchangerates["rates"][tocurrency]),
                            6,
                        )
                    )
                    + " "
                    + str(tocurrency)
                )
            else:
                if tocurrency == "DUCO":
                    currencyapisss = get(
                        "https://api.exchangeratesapi.io/latest?symbols="
                        + str(fromcurrency)
                        + ",USD",
                        data=None,
                    )
                    if currencyapi.status_code == 200:  # Check for reponse
                        exchangeratesss = loads(currencyapisss.content.decode())
                        result = (
                            str(
                                round(
                                    float(amount)
                                    * float(1 / ducofiat)
                                    / float(exchangeratesss["rates"][fromcurrency]),
                                    6,
                                )
                            )
                            + " "
                            + str(tocurrency)
                        )
                else:
                    result = (
                        str(
                            round(
                                float(amount)
                                * float(exchangerates["rates"][tocurrency]),
                                6,
                            )
                        )
                        + " "
                        + str(tocurrency)
                    )
    except:
        result = "Incorrect calculation"
    result = "RESULT: " + result
    conversionresulttext.set(str(result))
    calculatorWindow.update()


def openCalculator(handler):
    global conversionresulttext, fromCurrencyInput, toCurrencyInput, amountInput, calculatorWindow

    currencyapi = get("https://api.exchangeratesapi.io/latest", data=None)
    if currencyapi.status_code == 200:  # Check for reponse
        exchangerates = loads(currencyapi.content.decode())
        exchangerates["rates"]["DUCO"] = float(ducofiat)

    calculatorWindow = Toplevel()
    calculatorWindow.resizable(False, False)
    calculatorWindow.title("Duino-Coin Wallet - Calculator")
    calculatorWindow.transient([root])
    calculatorWindow.configure(background=backgroundColor)

    textFont2 = Font(calculatorWindow, size=12, weight="bold")
    textFont3 = Font(calculatorWindow, size=14, weight="bold")
    textFont = Font(calculatorWindow, size=12, weight="normal")

    Label(
        calculatorWindow,
        text="CURRENCY CONVERTER",
        font=textFont3,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=0, columnspan=2, column=0, sticky=S + W, pady=5, padx=5)

    Label(
        calculatorWindow,
        text="FROM",
        font=textFont2,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=1, column=0, sticky=S + W, padx=5)
    fromCurrencyInput = Listbox(
        calculatorWindow,
        exportselection=False,
        background=backgroundColor,
        selectbackground=foregroundColor,
        border="0",
        font=textFont,
        foreground=fontColor,
        width="20",
        height="13",
    )
    fromCurrencyInput.grid(row=2, column=0, sticky=S + W, padx=(5, 0))
    i = 0
    for currency in exchangerates["rates"]:
        fromCurrencyInput.insert(i, currency)
        i = i + 1
    vsb = Scrollbar(
        calculatorWindow,
        orient="vertical",
        command=fromCurrencyInput.yview,
        background=backgroundColor,
    )
    vsb.grid(row=2, column=1, sticky="ns", padx=(0, 5))
    fromCurrencyInput.configure(yscrollcommand=vsb.set)

    fromCurrencyInput.select_set(32)
    fromCurrencyInput.event_generate("<<ListboxSelect>>")

    Label(
        calculatorWindow,
        text="TO",
        font=textFont2,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=1, column=3, columnspan=2, sticky=S + W, padx=5)
    toCurrencyInput = Listbox(
        calculatorWindow,
        exportselection=False,
        background=backgroundColor,
        selectbackground=foregroundColor,
        border="0",
        foreground=fontColor,
        font=textFont,
        width="20",
        height="13",
    )
    toCurrencyInput.grid(row=2, column=3, sticky=S + W, padx=(5, 0))
    i = 0
    for currency in exchangerates["rates"]:
        toCurrencyInput.insert(i, currency)
        i = i + 1
    vsb2 = Scrollbar(
        calculatorWindow,
        orient="vertical",
        command=toCurrencyInput.yview,
        background=backgroundColor,
    )
    vsb2.grid(row=2, column=4, sticky="ns", padx=(0, 5))
    toCurrencyInput.configure(yscrollcommand=vsb2.set)

    toCurrencyInput.select_set(0)
    toCurrencyInput.event_generate("<<ListboxSelect>>")

    Label(
        calculatorWindow,
        text="INPUT AMOUNT",
        font=textFont2,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=3, columnspan=2, column=0, sticky=S + W, padx=5)

    def clear_ccamount_placeholder(self):
        amountInput.delete("0", "100")

    amountInput = Entry(
        calculatorWindow,
        foreground=foregroundColorSecondary,
        border="0",
        font=textFont,
        background=backgroundColor,
    )
    amountInput.grid(
        row=4, column=0, sticky=N + S + W + E, padx=5, columnspan=2, pady=(0, 5)
    )
    amountInput.insert("0", str(globalBalance))
    amountInput.bind("<FocusIn>", clear_ccamount_placeholder)

    Button(
        calculatorWindow,
        text="CALCULATE",
        font=textFont2,
        foreground=foregroundColor,
        activebackground=backgroundColor,
        background=backgroundColor,
        command=currencyConvert,
    ).grid(row=3, columnspan=2, column=2, sticky=N + S + W + E, pady=(5, 0), padx=5)

    conversionresulttext = StringVar(calculatorWindow)
    conversionresulttext.set("RESULT: 0.0")
    conversionresultLabel = Label(
        calculatorWindow,
        textvariable=conversionresulttext,
        font=textFont2,
        background=backgroundColor,
        foreground=fontColor,
    )
    conversionresultLabel.grid(row=4, columnspan=2, column=2, pady=(0, 5))

    calculatorWindow.mainloop()


def openStats(handler):
    statsApi = get(
        "https://raw.githubusercontent.com/revoxhere/duco-statistics/master/api.json",
        data=None,
    )
    if statsApi.status_code == 200:  # Check for reponse
        statsApi = statsApi.json()

    statsWindow = Toplevel()
    statsWindow.resizable(False, False)
    statsWindow.title("Duino-Coin Wallet - Statistics")
    statsWindow.transient([root])
    statsWindow.configure(background=backgroundColor)

    textFont3 = Font(statsWindow, size=14, weight="bold")
    textFont = Font(statsWindow, size=12, weight="normal")

    Active_workers_listbox = Listbox(
        statsWindow,
        exportselection=False,
        background=backgroundColor,
        foreground=fontColor,
        border="0",
        font=textFont,
        width="65",
        height="8",
    )
    Active_workers_listbox.grid(
        row=1, columnspan=2, sticky=N + E + S + W, pady=(0, 5), padx=5
    )
    i = 0
    totalHashrate = 0
    for threadid in statsApi["Miners"]:
        if username in statsApi["Miners"][threadid]["User"]:
            rigId = statsApi["Miners"][threadid]["Identifier"]
            if rigId == "None":
                rigId = ""
            else:
                rigId += ": "
            software = statsApi["Miners"][threadid]["Software"]
            hashrate = str(round(statsApi["Miners"][threadid]["Hashrate"], 2))
            totalHashrate += float(hashrate)
            difficulty = str(statsApi["Miners"][threadid]["Diff"])
            shares = (
                str(statsApi["Miners"][threadid]["Accepted"])
                + "/"
                + str(
                    statsApi["Miners"][threadid]["Accepted"]
                    + statsApi["Miners"][threadid]["Rejected"]
                )
            )
            Active_workers_listbox.insert(
                i,
                "#"
                + str(i + 1)
                + ": "
                + rigId
                + software
                + " "
                + str(round(float(hashrate) / 1000, 2))
                + " kH/s @ diff "
                + difficulty
                + ", "
                + shares
                + " acc.",
            )
            i += 1
    if i == 0:
        Active_workers_listbox.insert(
            i, "Couldn't detect any miners mining on your account"
        )

    totalHashrateString = str(int(totalHashrate)) + " H/s"
    if totalHashrate > 1000000000:
        totalHashrateString = str(round(totalHashrate / 1000000000, 2)) + " GH/s"
    elif totalHashrate > 1000000:
        totalHashrateString = str(round(totalHashrate / 1000000, 2)) + " MH/s"
    elif totalHashrate > 1000:
        totalHashrateString = str(round(totalHashrate / 1000, 2)) + " kH/s"

    Active_workers_listbox.configure(height=i)
    Active_workers_listbox.select_set(32)
    Active_workers_listbox.event_generate("<<ListboxSelect>>")

    Label(
        statsWindow,
        text="YOUR MINERS - " + totalHashrateString,
        font=textFont3,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=0, column=0, columnspan=2, sticky=S + W, pady=5, padx=5)

    Label(
        statsWindow,
        text="RICHLIST",
        font=textFont3,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=2, column=0, sticky=S + W, pady=5, padx=5)
    Top_10_listbox = Listbox(
        statsWindow,
        exportselection=False,
        border="0",
        font=textFont,
        width="30",
        height="10",
        background=backgroundColor,
        foreground=fontColor,
    )
    Top_10_listbox.grid(
        row=3, column=0, rowspan=10, sticky=N + E + S + W, pady=(0, 5), padx=5
    )
    i = 0
    for rich in statsApi["Top 10 richest miners"]:
        Top_10_listbox.insert(i, statsApi["Top 10 richest miners"][i])
        i += 1
    Top_10_listbox.select_set(32)
    Top_10_listbox.event_generate("<<ListboxSelect>>")

    Label(
        statsWindow,
        text="NETWORK INFO",
        font=textFont3,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=2, column=1, sticky=S + W, padx=5, pady=5)
    Label(
        statsWindow,
        text="Difficulty: " + str(statsApi["Current difficulty"]),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=3, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="Mined blocks: " + str(statsApi["Mined blocks"]),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=4, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="Network hashrate: " + str(statsApi["Pool hashrate"]),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=5, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="Active miners: " + str(len(statsApi["Miners"])),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=6, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="1 DUCO est. price: $" + str(statsApi["Duco price"]),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=7, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="Registered users: " + str(statsApi["Registered users"]),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=8, column=1, sticky=S + W, padx=5)
    Label(
        statsWindow,
        text="All-time mined DUCO: " + str(statsApi["All-time mined DUCO"]) + " ᕲ",
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=9, column=1, sticky=S + W, padx=5)

    statsWindow.mainloop()


def openWrapper(handler):
    def Wrap():
        amount = amountWrap.get()
        print("Got amount :", amount)
        soc = socket.socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)
        try:
            float(amount)
        except:
            pass
        else:
            soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
            _ = soc.recv(10)
            soc.send(
                bytes(
                    str("WRAP,") + str(amount) + str(",") + str(pub_key),
                    encoding="utf8",
                )
            )
            soc.close()
            sleep(2)
            wrapperWindow.quit()

    try:
        pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
    except:
        messagebox.showerror(
            title="Wrapper error",
            message="Wrapper is not configured. Please configure it in settings !",
        )
    else:
        if tronpy_installed:
            pub_key = pubkeyfile.read()
            pubkeyfile.close()

            wrapperWindow = Toplevel()
            wrapperWindow.resizable(False, False)
            wrapperWindow.title("Duino-Coin Wallet - Wrapper")
            wrapperWindow.transient([root])
            wrapperWindow.configure()

            askWrapAmount = Label(wrapperWindow, text="Amount to wrap :")
            askWrapAmount.grid(row=0, column=0, sticky=N + W)
            amountWrap = Entry(wrapperWindow, border="0", font=Font(size=15))
            amountWrap.grid(row=1, column=0, sticky=N + W)
            wrapButton = Button(wrapperWindow, text="Wrap", command=Wrap)
            wrapButton.grid(row=2, column=0, sticky=N + W)
        else:
            messagebox.showerror(
                title="Wrapper error",
                message="Tronpy is not installed, please install it using `pip install tronpy`",
            )


def openUnWrapper(handler):
    def UnWrap():
        pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
        pub_key = pubkeyfile.read()
        pubkeyfile.close()

        passphrase = passphraseEntry.get()
        privkeyfile = open(str(f"{resources}/DUCOPrivKey.encrypt"), "r")
        privKeyEnc = privkeyfile.read()
        privkeyfile.close()

        try:
            priv_key = str(password_decrypt(privKeyEnc, passphrase))[2:66]
            wrong_passphrase = False
            use_wrapper = True
        except InvalidToken:
            print("Invalid passphrase, disabling wrapper for this session")
            use_wrapper = False
            wrong_passphrase = True

        amount = amountUnWrap.get()
        print("Got amount :", amount)
        soc = socket.socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)
        try:
            float(amount)
        except:
            pass
        else:
            soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
            _ = soc.recv(10)
            if use_wrapper:
                pendingvalues = wduco.functions.pendingWithdrawals(pub_key, username)
                txn_success = False  # transaction wasn't initiated, but variable should be declared
                try:
                    amount = float(amount)
                except ValueError:
                    print("NO, Value should be numeric... aborting")
                else:
                    if int(float(amount) * 10 ** 6) >= pendingvalues:
                        toInit = int(float(amount) * 10 ** 6) - pendingvalues
                    else:
                        toInit = amount * 10 ** 6
                    if toInit > 0:
                        txn = (
                            wduco.functions.initiateWithdraw(username, toInit)
                            .with_owner(pub_key)
                            .fee_limit(5_000_000)
                            .build()
                            .sign(PrivateKey(bytes.fromhex(priv_key)))
                        )
                        txn = txn.broadcast()
                        txnfeedback = txn.result()
                        if txnfeedback:
                            txn_success = True
                        else:
                            txn_success = False
                    if txn_success or amount <= pendingvalues:
                        soc.send(
                            bytes(
                                str("UNWRAP,") + str(amount) + str(",") + str(pub_key),
                                encoding="utf8",
                            )
                        )

                soc.close()
                sleep(2)
                unWrapperWindow.quit()

    try:
        pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
        pub_key = pubkeyfile.read()
        pubkeyfile.close()
    except:
        messagebox.showerror(
            title="Wrapper error",
            message="Wrapper is not configured. Please configure it in settings !",
        )
    else:
        if tronpy_installed:
            unWrapperWindow = Toplevel()
            unWrapperWindow.resizable(False, False)
            unWrapperWindow.title("Duino-Coin Wallet - Unwrapper")
            unWrapperWindow.transient([root])
            unWrapperWindow.configure()
            askAmount = Label(unWrapperWindow, text="Amount to unwrap : ")
            askAmount.grid(row=1, column=0, sticky=N + W)

            amountUnWrap = Entry(unWrapperWindow, border="0", font=Font(size=15))
            amountUnWrap.grid(row=2, column=0, sticky=N + W)

            askPassphrase = Label(
                unWrapperWindow, text="Passphrase (for accessing private key) :"
            )
            askPassphrase.grid(row=4, column=0, sticky=N + W)

            passphraseEntry = Entry(unWrapperWindow, border="0", font=Font(size=15))
            passphraseEntry.grid(row=5, column=0, sticky=N + W)

            wrapButton = Button(unWrapperWindow, text="Unwrap", command=UnWrap)
            wrapButton.grid(row=7, column=0, sticky=N + W)
        else:
            messagebox.showerror(
                title="Wrapper error",
                message="Tronpy is not installed, please install it using : `pip install tronpy`",
            )


def openSettings(handler):
    def _wrapperconf():
        if tronpy_installed:
            privkey_input = StringVar()
            passphrase_input = StringVar()
            wrapconfWindow = Toplevel()
            wrapconfWindow.resizable(False, False)
            wrapconfWindow.title("Duino-Coin Wallet - Wrapper")
            wrapconfWindow.transient([root])
            wrapconfWindow.configure()

            def setwrapper():
                if privkey_input and passphrase_input:
                    priv_key = privkey_entry.get()
                    print("Got priv key :", priv_key)
                    passphrase = passphrase_entry.get()
                    print("Got passphrase :", passphrase)
                    try:
                        pub_key = PrivateKey(
                            bytes.fromhex(priv_key)
                        ).public_key.to_base58check_address()
                    except:
                        pass
                    else:
                        with sqlite3.connect(f"{resources}/wallet.db") as con:
                            print("Saving data")

                            privkeyfile = open(
                                str(f"{resources}/DUCOPrivKey.encrypt"), "w"
                            )
                            privkeyfile.write(
                                str(
                                    password_encrypt(
                                        priv_key.encode(), passphrase
                                    ).decode()
                                )
                            )
                            privkeyfile.close()

                            pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "w")
                            pubkeyfile.write(pub_key)
                            pubkeyfile.close()

                        Label(wrapconfWindow, text="Success !").pack()
                        wrapconfWindow.quit()

            title = Label(
                wrapconfWindow, text="DUCO Wrapper config", font=Font(size=20)
            )
            title.grid(row=0, column=0, sticky=N + W, padx=5)

            askprivkey = Label(wrapconfWindow, text="Private key : ")
            askprivkey.grid(row=1, column=0, sticky=N + W)

            privkey_entry = Entry(
                wrapconfWindow, font=textFont, textvariable=privkey_input
            )
            privkey_entry.grid(row=2, column=0, sticky=N + W)

            askpassphrase = Label(wrapconfWindow, text="Passphrase : ")
            askpassphrase.grid(row=3, column=0, sticky=N + W)

            passphrase_entry = Entry(
                wrapconfWindow, font=textFont, textvariable=passphrase_input
            )
            passphrase_entry.grid(row=4, column=0, sticky=N + W)

            wrapConfigButton = Button(
                wrapconfWindow, text="Configure wrapper", command=setwrapper
            )
            wrapConfigButton.grid(row=5, column=0, sticky=N + W)

            wrapconfWindow.mainloop()

        else:
            messagebox.showerror(
                title="Wrapper error",
                message="Tronpy is not installed, please install it using `pip install tronpy`",
            )

    def _logout():
        try:
            with sqlite3.connect(f"{resources}/wallet.db") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM UserData")
                con.commit()
        except Exception as e:
            print(e)
        try:
            execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(e)

    def _cleartrs():
        with sqlite3.connect(f"{resources}/wallet.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM transactions")
            con.commit()

    def _chgpass():
        def _changepassprotocol():
            oldpasswordS = oldpassword.get()
            newpasswordS = newpassword.get()
            confpasswordS = confpassword.get()

            if oldpasswordS != newpasswordS:
                if oldpasswordS and newpasswordS and confpasswordS:
                    if newpasswordS == confpasswordS:
                        soc = socket.socket()
                        soc.connect((pool_address, int(pool_port)))
                        soc.recv(3)
                        soc.send(
                            bytes(
                                f"LOGI,{str(username)},{str(password)}", encoding="utf8"
                            )
                        )
                        soc.recv(2)
                        soc.send(
                            bytes(
                                f"CHGP,{str(oldpasswordS)},{str(newpasswordS)}",
                                encoding="utf8",
                            )
                        )
                        response = soc.recv(128).decode("utf8").split(",")
                        soc.close()

                        if not "OK" in response[0]:
                            messagebox.showerror(
                                title="Error changing password", message=response[1]
                            )
                        else:
                            messagebox.showinfo(
                                title="Password changed", message=response[1]
                            )
                            try:
                                try:
                                    with sqlite3.connect(
                                        f"{resources}/wallet.db"
                                    ) as con:
                                        cur = con.cursor()
                                        cur.execute("DELETE FROM UserData")
                                        con.commit()
                                except Exception as e:
                                    print(e)
                            except FileNotFoundError:
                                pass
                            execl(sys.executable, sys.executable, *sys.argv)
                    else:
                        messagebox.showerror(
                            title="Error changing password",
                            message="New passwords don't match",
                        )
                else:
                    messagebox.showerror(
                        title="Error changing password",
                        message="Fill in the blanks first",
                    )
            else:
                messagebox.showerror(
                    title="Error changing password",
                    message="New password is the same as the old one",
                )

        settingsWindow.destroy()
        changepassWindow = Toplevel()
        changepassWindow.title("Change password")
        changepassWindow.resizable(False, False)
        changepassWindow.transient([root])
        changepassWindow.configure(background=backgroundColor)

        textFont2 = Font(changepassWindow, size=12, weight="bold")
        textFont = Font(changepassWindow, size=12, weight="normal")

        Label(
            changepassWindow,
            text="OLD PASSWORD",
            font=textFont2,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=0, sticky=W, padx=5)
        oldpassword = Entry(
            changepassWindow,
            show="*",
            font=textFont,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        oldpassword.grid(row=1, sticky="nswe", padx=5)

        Label(
            changepassWindow,
            text="NEW PASSWORD",
            font=textFont2,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=2, sticky=W, padx=5)
        newpassword = Entry(
            changepassWindow,
            show="*",
            font=textFont,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        newpassword.grid(row=3, sticky="nswe", padx=5)

        Label(
            changepassWindow,
            text="CONFIRM NEW PASSWORD",
            font=textFont2,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=4, sticky=W, padx=5)
        confpassword = Entry(
            changepassWindow,
            show="*",
            font=textFont,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        confpassword.grid(row=5, sticky="nswe", padx=5)

        chgpbtn = Button(
            changepassWindow,
            text="CHANGE PASSWORD",
            command=_changepassprotocol,
            foreground=foregroundColor,
            font=textFont2,
            background=backgroundColor,
            activebackground=backgroundColor,
        )
        chgpbtn.grid(columnspan=2, sticky="nswe", pady=5, padx=5)

    settingsWindow = Toplevel()
    settingsWindow.resizable(False, False)
    settingsWindow.title("Duino-Coin Wallet - Settings")
    settingsWindow.transient([root])
    settingsWindow.configure(background=backgroundColor)
    textFont = Font(settingsWindow, size=12, weight="normal")
    textFont3 = Font(settingsWindow, size=12, weight="bold")

    Label(
        settingsWindow,
        text="SETTINGS",
        font=textFont3,
        foreground=foregroundColor,
        background=backgroundColor,
    ).grid(row=0, column=0, columnspan=4, sticky=S + W, pady=(5, 5), padx=(5, 0))

    logoutbtn = Button(
        settingsWindow,
        text="LOGOUT",
        command=_logout,
        font=textFont,
        background=backgroundColor,
        activebackground=backgroundColor,
        foreground=fontColor,
    )
    logoutbtn.grid(row=1, column=0, columnspan=4, sticky="nswe", padx=5)

    chgpassbtn = Button(
        settingsWindow,
        text="CHANGE PASSWORD",
        command=_chgpass,
        font=textFont,
        background=backgroundColor,
        activebackground=backgroundColor,
        foreground=fontColor,
    )
    chgpassbtn.grid(row=2, column=0, columnspan=4, sticky="nswe", padx=5)

    wrapperconfbtn = Button(
        settingsWindow,
        text="CONFIGURE WRAPPER",
        command=_wrapperconf,
        font=textFont,
        background=backgroundColor,
        activebackground=backgroundColor,
        foreground=fontColor,
    )
    wrapperconfbtn.grid(row=3, column=0, columnspan=4, sticky="nswe", padx=5)

    cleartransbtn = Button(
        settingsWindow,
        text="CLEAR TRANSACTIONS",
        command=_cleartrs,
        font=textFont,
        background=backgroundColor,
        activebackground=backgroundColor,
        foreground=fontColor,
    )
    cleartransbtn.grid(row=4, column=0, columnspan=4, sticky="nswe", padx=5)

    separator = ttk.Separator(settingsWindow, orient="horizontal")
    separator.grid(
        row=5, column=0, columnspan=4, sticky=N + S + E + W, padx=(5, 5), pady=5
    )

    Label(
        settingsWindow,
        text="Logged-in as user: " + str(username),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=6, column=0, columnspan=4, padx=5, sticky=S + W)
    Label(
        settingsWindow,
        text="Wallet version: " + str(version),
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=7, column=0, columnspan=4, padx=5, sticky=S + W)
    Label(
        settingsWindow,
        text="More options will come in the future",
        font=textFont,
        background=backgroundColor,
        foreground=fontColor,
    ).grid(row=8, column=0, columnspan=4, padx=5, sticky=S + W)

    separator = ttk.Separator(settingsWindow, orient="horizontal")
    separator.grid(
        row=9, column=0, columnspan=4, sticky=N + S + E + W, padx=(5, 5), pady=5
    )

    original = Image.open(resources + "duco.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    website = ImageTk.PhotoImage(resized)
    website.image = website
    websiteLabel = Label(
        settingsWindow, image=website, background=backgroundColor, foreground=fontColor
    )
    websiteLabel.grid(row=10, column=0, sticky=N + S + E + W, padx=(5, 0), pady=(0, 5))
    websiteLabel.bind("<Button-1>", openWebsite)

    original = Image.open(resources + "github.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    github = ImageTk.PhotoImage(resized)
    github.image = github
    githubLabel = Label(
        settingsWindow, image=github, background=backgroundColor, foreground=fontColor
    )
    githubLabel.grid(row=10, column=1, sticky=N + S + E + W, pady=(0, 5))
    githubLabel.bind("<Button-1>", openGitHub)

    original = Image.open(resources + "exchange.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    exchange = ImageTk.PhotoImage(resized)
    exchange.image = exchange
    exchangeLabel = Label(
        settingsWindow, image=exchange, background=backgroundColor, foreground=fontColor
    )
    exchangeLabel.grid(row=10, column=2, sticky=N + S + E + W, pady=(0, 5))
    exchangeLabel.bind("<Button-1>", openExchange)

    original = Image.open(resources + "discord.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    discord = ImageTk.PhotoImage(resized)
    discord.image = discord
    discordLabel = Label(
        settingsWindow, image=discord, background=backgroundColor, foreground=fontColor
    )
    discordLabel.grid(row=10, column=3, sticky=N + S + E + W, padx=(0, 5), pady=(0, 5))
    discordLabel.bind("<Button-1>", openDiscord)


oldbalance = 0
balance = 0
unpaid_balance = 0


def getBalance():
    global oldbalance, balance, unpaid_balance, globalBalance
    while True:
        try:
            soc = socket.socket()
            soc.connect((pool_address, int(pool_port)))
            soc.recv(3)
            soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
            _ = soc.recv(2)
            while True:
                while True:
                    try:
                        soc.send(bytes("BALA", encoding="utf8"))
                        oldbalance = balance
                        balance = soc.recv(1024).decode()
                        try:
                            balance = float(balance)
                            break
                        except ValueError:
                            pass
                    except Exception as e:
                        print("Retrying in 5s.")
                        sleep(5)

                try:
                    if oldbalance != balance:
                        difference = float(balance) - float(oldbalance)
                        dif_with_unpaid = (
                            float(balance) - float(oldbalance)
                        ) + unpaid_balance
                        if float(balance) != float(difference):
                            if (
                                dif_with_unpaid >= min_trans_difference
                                or dif_with_unpaid < 0
                            ):
                                now = datetime.datetime.now()
                                difference = round(dif_with_unpaid, 8)
                                if (
                                    difference >= min_trans_difference_notify
                                    or difference < 0
                                    and notificationsEnabled
                                ):
                                    notification = Notify()
                                    notification.title = "Duino-Coin Wallet"
                                    notification.message = (
                                        "New transaction\n"
                                        + now.strftime("%d.%m.%Y %H:%M:%S\n")
                                        + str(round(difference, 6))
                                        + " DUCO"
                                    )
                                    notification.icon = f"{resources}/duco.png"
                                    notification.send(block=False)
                                with sqlite3.connect(f"{resources}/wallet.db") as con:
                                    cur = con.cursor()
                                    cur.execute(
                                        """INSERT INTO Transactions(Transaction_Date, amount) VALUES(?, ?)""",
                                        (
                                            now.strftime("%d.%m.%Y %H:%M:%S"),
                                            round(difference, 8),
                                        ),
                                    )
                                    con.commit()
                                    unpaid_balance = 0
                            else:
                                unpaid_balance += float(balance) - float(oldbalance)
                except Exception as e:
                    print(e)

                globalBalance = round(float(balance), 8)
                sleep(3)
        except:
            print("Retrying in 5s.")
            sleep(5)


def getwbalance():
    if tronpy_installed:
        try:
            pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
            pub_key = pubkeyfile.read()
            pubkeyfile.close()
        except:
            return 0
        else:
            wBalance = float(wduco.functions.balanceOf(pub_key)) / (10 ** 6)
            return wBalance


profitCheck = 0


def updateBalanceLabel():
    global profit_array, profitCheck
    try:
        balancetext.set(str(round(globalBalance, 7)) + " ᕲ")
        wbalancetext.set(str(getwbalance()) + " wᕲ")
        balanceusdtext.set("$" + str(round(globalBalance * ducofiat, 4)))

        with sqlite3.connect(f"{resources}/wallet.db") as con:
            cur = con.cursor()
            cur.execute("SELECT rowid,* FROM Transactions ORDER BY rowid DESC")
            Transactions = cur.fetchall()
        transactionstext_format = ""
        for i, row in enumerate(Transactions, start=1):
            transactionstext_format += f"{str(row[1])}  {row[2]} DUCO\n"
            if i == 6:
                transactionstext_format = transactionstext_format.rstrip("\n")
                break
        transactionstext.set(transactionstext_format)

        if profit_array[2] != 0:
            sessionprofittext.set("SESSION: " + str(profit_array[0]) + " ᕲ")
            minuteprofittext.set("≈" + str(profit_array[1]) + " ᕲ/MINUTE")
            hourlyprofittext.set("≈" + str(profit_array[2]) + " ᕲ/HOUR")
            dailyprofittext.set(
                "≈"
                + str(profit_array[3])
                + " ᕲ/DAY ($"
                + str(round(profit_array[3] * ducofiat, 4))
                + ")"
            )
        else:
            if profitCheck > 10:
                sessionprofittext.set("Launch your miners")
                minuteprofittext.set("first to see estimated profit.")
                hourlyprofittext.set("")
                dailyprofittext.set("")
            profitCheck += 1
    except:
        _exit(0)
    Timer(1, updateBalanceLabel).start()


def calculateProfit(start_bal):
    try:  # Thanks Bilaboz for the code!
        global curr_bal, profit_array

        prev_bal = curr_bal
        curr_bal = globalBalance
        session = curr_bal - start_bal
        tensec = curr_bal - prev_bal
        minute = tensec * 6
        hourly = minute * 60
        daily = hourly * 24

        if tensec >= 0:
            profit_array = [
                round(session, 8),
                round(minute, 6),
                round(hourly, 4),
                round(daily, 2),
            ]
    except:
        _exit(0)
    Timer(10, calculateProfit, [start_bal]).start()


def sendFunds(handler):
    recipientStr = recipient.get()
    amountStr = amount.get()

    MsgBox = messagebox.askquestion(
        "Warning",
        f"Are you sure you want to send {amountStr} DUCO to {recipientStr}",
        icon="warning",
    )
    if MsgBox == "yes":
        soc = socket.socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)

        soc.send(bytes(f"LOGI,{str(username)},{str(password)}", encoding="utf8"))
        response = soc.recv(2)
        soc.send(bytes(f"SEND,-,{str(recipientStr)},{str(amountStr)}", encoding="utf8"))
        response = soc.recv(128).decode().split(",")
        soc.close()

        if "OK" in str(response[0]):
            MsgBox = messagebox.showinfo(
                response[0], response[1] + "\nTXID:" + response[2]
            )
        else:
            MsgBox = messagebox.showwarning(response[0], response[1])
    root.update()


def initRichPresence():
    global RPC
    try:
        RPC = Presence(806985845320056884)
        RPC.connect()
    except:  # Discord not launched
        pass


def updateRichPresence():
    try:
        balance = round(globalBalance, 4)
        RPC.update(
            details=str(balance) + " ᕲ ($" + str(round(ducofiat * balance, 2)) + ")",
            large_image="duco",
            large_text="Duino-Coin, a cryptocurrency that can be mined with Arduino boards",
            buttons=[
                {"label": "Learn more", "url": "https://duinocoin.com"},
                {"label": "Discord Server", "url": "https://discord.gg/k48Ht5y"},
            ],
        )
    except:  # Discord not launched
        pass

    Timer(15, updateRichPresence).start()


class Wallet:
    def __init__(self, master):
        global recipient, amount, balancetext, wbalancetext
        global sessionprofittext, minuteprofittext, hourlyprofittext, dailyprofittext
        global balanceusdtext, ducopricetext
        global transactionstext
        global curr_bal, profit_array
        try:
            loading.destroy()
        except:
            pass

        textFont4 = Font(size=14, weight="bold")
        textFont3 = Font(size=12, weight="bold")
        textFont2 = Font(size=18, weight="bold")
        textFont = Font(size=12, weight="normal")

        self.master = master
        master.resizable(False, False)
        master.configure(background=backgroundColor)
        master.title("Duino-Coin Wallet")

        Label(
            master,
            text="DUINO-COIN WALLET: " + str(username),
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
        ).grid(row=0, column=0, sticky=S + W, columnspan=4, pady=(5, 0), padx=(5, 0))

        balancetext = StringVar()
        wbalancetext = StringVar()
        balancetext.set("Please wait...")
        if tronpy_installed:
            wbalancetext.set("Please wait...")
        else:
            wbalancetext.set("0.00")
        balanceLabel = Label(
            master,
            textvariable=balancetext,
            font=textFont2,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        balanceLabel.grid(row=1, column=0, columnspan=3, sticky=S + W, padx=(5, 0))

        wbalanceLabel = Label(
            master,
            textvariable=wbalancetext,
            font=textFont4,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        wbalanceLabel.grid(row=2, column=0, columnspan=3, sticky=S + W, padx=(5, 0))

        balanceusdtext = StringVar()
        balanceusdtext.set("Please wait...")

        Label(
            master,
            textvariable=balanceusdtext,
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=1, column=3, sticky=S + E, pady=(0, 1.5), padx=(0, 5))

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(
            row=4,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=(5, 5),
            pady=(0, 5),
        )

        def clear_recipient_placeholder(self):
            recipient.delete("0", "100")

        def clear_amount_placeholder(self):
            amount.delete("0", "100")

        Label(
            master,
            text="RECIPIENT",
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=5, column=0, sticky=W + S, padx=(5, 0))

        recipient = Entry(
            master,
            border="0",
            font=textFont,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        recipient.grid(row=5, column=1, sticky=N + W + S + E, columnspan=3, padx=(0, 5))
        recipient.insert("0", "revox")
        recipient.bind("<FocusIn>", clear_recipient_placeholder)

        Label(
            master,
            text="AMOUNT",
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        ).grid(row=6, column=0, sticky=W + S, padx=(5, 0))

        amount = Entry(
            master,
            border="0",
            font=textFont,
            foreground=foregroundColorSecondary,
            background=backgroundColor,
        )
        amount.grid(row=6, column=1, sticky=N + W + S + E, columnspan=3, padx=(0, 5))
        amount.insert("0", "2.2")
        amount.bind("<FocusIn>", clear_amount_placeholder)

        sendLabel = Button(
            master,
            text="SEND FUNDS",
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
            activebackground=backgroundColor,
        )
        sendLabel.grid(
            row=7,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=(5),
            pady=(1, 2),
        )
        sendLabel.bind("<Button-1>", sendFunds)

        wrapLabel = Button(
            master,
            text="WRAP DUCO",
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
            activebackground=backgroundColor,
        )
        wrapLabel.grid(
            row=8,
            column=0,
            sticky=N + S + E + W,
            columnspan=2,
            padx=(5, 1),
            pady=(1, 5),
        )
        wrapLabel.bind("<Button-1>", openWrapper)

        wrapLabel = Button(
            master,
            text="UNWRAP DUCO",
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
            activebackground=backgroundColor,
        )
        wrapLabel.grid(
            row=8,
            column=2,
            sticky=N + S + E + W,
            columnspan=2,
            padx=(1, 5),
            pady=(1, 5),
        )
        wrapLabel.bind("<Button-1>", openUnWrapper)

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(row=9, column=0, sticky=N + S + E + W, columnspan=4, padx=(5, 5))

        Label(
            master,
            text="ESTIMATED PROFIT",
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
        ).grid(row=10, column=0, sticky=S + W, columnspan=4, pady=(5, 0), padx=(5, 0))

        sessionprofittext = StringVar()
        sessionprofittext.set("Please wait - calculating...")
        sessionProfitLabel = Label(
            master,
            textvariable=sessionprofittext,
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        )
        sessionProfitLabel.grid(row=11, column=0, sticky=W, columnspan=4, padx=5)

        minuteprofittext = StringVar()
        minuteProfitLabel = Label(
            master,
            textvariable=minuteprofittext,
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        )
        minuteProfitLabel.grid(row=12, column=0, sticky=W, columnspan=4, padx=5)

        hourlyprofittext = StringVar()
        hourlyProfitLabel = Label(
            master,
            textvariable=hourlyprofittext,
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        )
        hourlyProfitLabel.grid(row=13, column=0, sticky=W, columnspan=4, padx=5)

        dailyprofittext = StringVar()
        dailyprofittext.set("")
        dailyProfitLabel = Label(
            master,
            textvariable=dailyprofittext,
            font=textFont,
            background=backgroundColor,
            foreground=fontColor,
        )
        dailyProfitLabel.grid(row=14, column=0, sticky=W, columnspan=4, padx=5)

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(row=15, column=0, sticky=N + S + E + W, columnspan=4, padx=5)

        Label(
            master,
            text="LOCAL TRANSACTIONS",
            font=textFont3,
            foreground=foregroundColor,
            background=backgroundColor,
        ).grid(row=16, column=0, sticky=S + W, columnspan=4, pady=(5, 0), padx=(5, 0))

        transactionstext = StringVar()
        transactionstext.set("")
        transactionstextLabel = Label(
            master,
            textvariable=transactionstext,
            font=textFont,
            justify=LEFT,
            background=backgroundColor,
            foreground=fontColor,
        )
        transactionstextLabel.grid(
            row=17, column=0, sticky=W, columnspan=4, padx=5, pady=(0, 5)
        )

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(
            row=18, column=0, sticky=N + S + E + W, columnspan=4, padx=5, pady=(0, 10)
        )

        original = Image.open(resources + "transactions.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        transactions = ImageTk.PhotoImage(resized)
        transactions.image = transactions
        transactionsLabel = Label(
            master, image=transactions, background=backgroundColor, foreground=fontColor
        )
        transactionsLabel.grid(row=19, column=0, sticky=N + S + W + E, pady=(0, 5))
        transactionsLabel.bind("<Button>", openTransactions)

        original = Image.open(resources + "calculator.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        calculator = ImageTk.PhotoImage(resized)
        calculator.image = calculator
        calculatorLabel = Label(
            master, image=calculator, background=backgroundColor, foreground=fontColor
        )
        calculatorLabel.grid(
            row=19, column=1, sticky=N + S + W + E, padx=(0, 5), pady=(0, 5)
        )
        calculatorLabel.bind("<Button>", openCalculator)

        original = Image.open(resources + "stats.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        stats = ImageTk.PhotoImage(resized)
        stats.image = stats
        statsLabel = Label(
            master, image=stats, background=backgroundColor, foreground=fontColor
        )
        statsLabel.grid(
            row=19, column=2, sticky=N + S + W + E, padx=(0, 5), pady=(0, 5)
        )
        statsLabel.bind("<Button>", openStats)

        original = Image.open(resources + "settings.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        settings = ImageTk.PhotoImage(resized)
        settings.image = settings
        settingsLabel = Label(
            master, image=settings, background=backgroundColor, foreground=fontColor
        )
        settingsLabel.grid(
            row=19, column=3, sticky=N + S + W + E, padx=(0, 10), pady=(0, 5)
        )
        settingsLabel.bind("<Button>", openSettings)

        root.iconphoto(True, PhotoImage(file=resources + "duco.png"))
        start_balance = globalBalance
        curr_bal = start_balance
        calculateProfit(start_balance)
        updateBalanceLabel()

        if not disableTray:

            def quit_window(icon, item):
                master.destroy()

            def show_window(icon, item):
                master.after(0, root.deiconify)

            def withdraw_window():
                image = Image.open(resources + "duco.png")
                menu = (
                    pystray.MenuItem("Show", show_window),
                    pystray.MenuItem("Quit", quit_window),
                )
                icon = pystray.Icon(
                    "Duino-coin GUI Wallet", image, "Duino-coin GUI Wallet", menu
                )
                icon.run()

            t = threading.Thread(target=withdraw_window)
            t.setDaemon(True)
            t.start()

        root.mainloop()


try:
    mkdir(resources)
except FileExistsError:
    pass

with sqlite3.connect(f"{resources}/wallet.db") as con:
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS Transactions(Transaction_Date TEXT, amount REAL)"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS UserData(username TEXT, password TEXT, useWrapper TEXT)"""
    )
    con.commit()

with urlopen(
    "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt"
) as content:
    content = content.read().decode().splitlines()
    pool_address = content[0]
    pool_port = content[1]

try:
    GetDucoPrice()  # Start duco price updater
    threading.Thread(target=getBalance).start()
    initRichPresence()
    updateRichPresence()
    try:
        loading.destroy()  # Destroy loading dialog and start the main wallet window
    except:
        pass
    root = Tk()
    my_gui = Wallet(root)
except ValueError:
    print("ValueError")
    _exit(0)
