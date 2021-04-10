#!/usr/bin/env python3
##########################################
# Duino-Coin Tkinter GUI Wallet (v2.4)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
from tkinter import Tk, Label, Frame, Entry, Button
from tkinter import StringVar, IntVar, PhotoImage
from tkinter import Listbox, Scrollbar, Checkbutton
from tkinter import Toplevel, ttk
from tkinter.font import Font
from tkinter import LEFT, BOTH, RIGHT, END, N, S, W, E
from webbrowser import open_new_tab
from urllib.request import urlopen, urlretrieve
from pathlib import Path
from threading import Timer, Thread
from configparser import ConfigParser
from time import sleep, time
from os import _exit, mkdir, execl
from tkinter import messagebox
from base64 import b64encode, b64decode
from requests import get
from json import loads
from datetime import datetime
from json import loads as jsonloads
from subprocess import check_call
from os import execl, system, _exit
from os import name as osname
from locale import getdefaultlocale
from socket import socket
from sqlite3 import connect as sqlconn
import sys


# VERSION number
VERSION = 2.4
# Colors
BACKGROUND_COLOR = "#121212"
FONT_COLOR = "#FAFAFA"
FOREGROUND_COLOR = "#f0932b"
FOREGROUND_COLOR_SECONDARY = "#ffbe76"
# Minimum transaction amount to be saved
MIN_TRANSACTION_VALUE = 0.00000000001
# Minimum transaction amount to show a notification
MIN_TRANSACTION_VALUE_NOTIFY = 0.5
# Resources folder location
resources = "Wallet_" + str(VERSION) + "_resources/"
config = ConfigParser()
wrong_passphrase = False
iterations = 100_000
global_balance = 0


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    execl(sys.executable, sys.executable, *sys.argv)


try:
    from pypresence import Presence
except:
    print(
        'Pypresence is not installed.'
        + 'Wallet will try to install it. '
        + 'If it fails, please manually install "pypresence" python3 package.')
    install("pypresence")

try:
    from PIL import Image, ImageTk
except:
    print(
        'Pillow is not installed. '
        + 'Wallet will try to install it. '
        + 'If it fails, please manually install "Pillow" python3 package.')
    install("Pillow")

try:
    import pystray
except:
    print("Pystray is not installed. "
          + "Continuing without system tray support")
    disableTray = True
else:
    disableTray = Falsename

try:
    from notifypy import Notify
except:
    print("Notify-py is not installed. "
          + "Continuing without notification system")
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
    now = datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + 'Cryptography is not installed. '
        + 'Please install it using: python3 - m pip install cryptography.'
        + '\nExiting in 15s.')
    sleep(15)
    _exit(1)


try:
    import secrets
except ModuleNotFoundError:
    now = datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + 'Secrets is not installed. '
        + 'Please install it using: python3 - m pip install secrets.'
        + '\nExiting in 15s.')
    sleep(15)
    _exit(1)

try:
    from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
except:
    now = datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + 'Base64 is not installed. '
        + 'Please install it using: python3 -m pip install base64.'
        + '\nExiting in 15s.')
    sleep(15)
    _exit(1)

try:
    import tronpy
    from tronpy.keys import PrivateKey

    tronpy_installed = True
except ModuleNotFoundError:
    tronpy_installed = False
    now = datetime.now()
    print(
        now.strftime("%H:%M:%S ")
        + 'Tronpy is not installed. '
        + 'Please install it using: python3 -m pip install tronpy.'
        + '\nwDUCO Wrapper was disabled because Tronpy is missing')
else:
    tron = tronpy.Tron()
    tron = tronpy.Tron()
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U")


def get_duco_price():
    global duco_fiat_value
    jsonapi = get(
        "https://raw.githubusercontent.com/"
        + "revoxhere/"
        + "duco-statistics/master/"
        + "api.json",
        data=None)
    if jsonapi.status_code == 200:
        try:
            content = jsonapi.content.decode()
            contentjson = loads(content)
            duco_fiat_value = round(float(contentjson["Duco price"]), 4)
        except:
            duco_fiat_value = 0.003
    else:
        duco_fiat_value = 0.003
    Timer(30, GetDucoPrice).start()


def title(title):
    if osname == "nt":
        system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def _derive_key(
        password: bytes,
        salt: bytes,
        iterations: int = iterations) -> bytes:

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=backend)
    return b64e(kdf.derive(password))


def password_encrypt(
        message: bytes,
        password: str,
        iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(
        password.encode(),
        salt,
        iterations)
    return b64e(
        b"%b%b%b" % (
            salt,
            iterations.to_bytes(4, "big"),
            b64d(Fernet(key).encrypt(message))))


def password_decrypt(
        token: bytes,
        password: str) -> bytes:
    decoded = b64d(token)
    salt, iterations, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iterations, "big")
    key = _derive_key(
        password.encode(),
        salt,
        iterations)
    return Fernet(key).decrypt(token)


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("Login")
        master.resizable(False, False)

        TEXT_FONT_BOLD = Font(size=12, weight="bold")
        TEXT_FONT = Font(size=12, weight="normal")

        self.duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
        self.duco.image = self.duco
        self.ducoLabel = Label(
            self, background=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            image=self.duco)
        self.ducoLabel2 = Label(
            self,
            background=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            text=get_string("welcome_message"),
            font=TEXT_FONT_BOLD)
        self.spacer = Label(self)

        self.label_username = Label(
            self,
            text=get_string("username"),
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            padx=5)
        self.label_password = Label(
            self,
            text=get_string("passwd"),
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            padx=5)
        self.entry_username = Entry(
            self,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)
        self.entry_password = Entry(
            self,
            show="*",
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)

        self.ducoLabel.grid(
            row=0,
            sticky="nswe",
            pady=(5, 0),
            padx=(5))
        self.ducoLabel2.grid(
            row=1,
            sticky="nswe",
            padx=(5))
        self.label_username.grid(
            row=4,
            sticky=W,
            pady=(5, 0))
        self.entry_username.grid(
            row=5,
            sticky=N,
            padx=(5))
        self.label_password.grid(
            row=6,
            sticky=W)
        self.entry_password.grid(
            row=7,
            sticky=N)

        self.var = IntVar()
        self.checkbox = Checkbutton(
            self,
            text=get_string("keep_me_logged_in"),
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR,
            selectcolor=BACKGROUND_COLOR,
            activeforeground=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            variable=self.var,
            font=TEXT_FONT,
            borderwidth="0",
            highlightthickness="0")
        self.checkbox.grid(
            columnspan=2,
            sticky=W,
            pady=(5),
            padx=5)

        self.logbtn = Button(
            self,
            text=get_string("login"),
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR,
            command=self._login_btn_clicked,
            font=TEXT_FONT_BOLD)
        self.logbtn.grid(
            columnspan=2,
            sticky="nswe",
            padx=(5),
            pady=(0, 1))

        self.regbtn = Button(
            self,
            text=get_string("register"),
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR,
            command=self._register_btn_clicked,
            font=TEXT_FONT_BOLD)
        self.regbtn.grid(
            columnspan=2,
            sticky="nswe",
            padx=(5),
            pady=(0, 5))

        self.configure(background=BACKGROUND_COLOR)
        self.pack()

    def _login_btn_clicked(self):
        global username, password
        username = self.entry_username.get()
        password = self.entry_password.get()
        keeplogedin = self.var.get()

        if username and password:
            soc = socket()
            soc.connect((pool_address, int(pool_port)))
            soc.recv(3)
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password),
                encoding="utf8"))
            response = soc.recv(64).decode("utf8").rstrip("\n")
            response = response.split(",")

            if response[0] == "OK":
                if keeplogedin >= 1:
                    passwordEnc = b64encode(bytes(password, encoding="utf8"))
                    with sqlconn(f"{resources}/wallet.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            """INSERT INTO
                            UserData(username, password, useWrapper)
                            VALUES(?, ?, ?)""",
                            (username, passwordEnc, "False"))
                        con.commit()
                root.destroy()
            else:
                messagebox.showerror(
                    title=get_string("login_error"),
                    message=response[1])
        else:
            messagebox.showerror(
                title=get_string("login_error"),
                message=get_string("fill_the_blanks_warning"))

    def _registerprotocol(self):
        emailS = email.get()
        usernameS = username.get()
        passwordS = password.get()
        confpasswordS = confpassword.get()

        if emailS and usernameS and passwordS and confpasswordS:
            if passwordS == confpasswordS:
                soc = socket()
                soc.connect((pool_address, int(pool_port)))
                soc.recv(3)
                soc.send(
                    bytes(
                        "REGI,"
                        + str(usernameS)
                        + ","
                        + str(passwordS)
                        + ","
                        + str(emailS),
                        encoding="utf8"))
                response = soc.recv(128).decode("utf8").rstrip("\n")
                response = response.split(",")

                if response[0] == "OK":
                    messagebox.showinfo(
                        title=get_string("registration_success"),
                        message=get_string("registration_success_msg"))
                    register.destroy()
                    execl(sys.executable, sys.executable, *sys.argv)
                else:
                    messagebox.showerror(
                        title=get_string("register_error"),
                        message=response[1])
            else:
                messagebox.showerror(
                    title=get_string("register_error"),
                    message=get_string("error_passwd_dont_match"))
        else:
            messagebox.showerror(
                title=get_string("register_error"),
                message=get_string("fill_the_blanks_warning"))

    def _register_btn_clicked(self):
        global username, password, confpassword, email, register
        root.destroy()
        register = Tk()
        register.title(get_string("register"))
        register.resizable(False, False)

        TEXT_FONT_BOLD = Font(
            register,
            size=12,
            weight="bold")
        TEXT_FONT = Font(
            register,
            size=12,
            weight="normal")

        tos_warning = get_string("register_tos_warning")
        import textwrap
        tos_warning = textwrap.dedent(tos_warning)
        tos_warning = '\n'.join(l for line in tos_warning.splitlines()
                                for l in textwrap.wrap(line, width=20))

        duco = ImageTk.PhotoImage(Image.open(resources + "duco.png"))
        duco.image = duco
        ducoLabel = Label(
            register,
            background=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            image=duco)
        ducoLabel.grid(
            row=0,
            padx=5,
            pady=(5, 0),
            sticky="nswe")

        ducoLabel2 = Label(
            register,
            background=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            text=get_string("register_on_network"),
            font=TEXT_FONT_BOLD)
        ducoLabel2.grid(row=1,
                        padx=5,
                        sticky="nswe")

        def colorLabelBlue(handler):
            ducoLabel3.configure(foreground="#6c5ce7")

        def colorLabelNormal(handler):
            ducoLabel3.configure(foreground=FONT_COLOR)

        ducoLabel3 = Label(
            register,
            background=FOREGROUND_COLOR,
            foreground=FONT_COLOR,
            text=tos_warning,
            font=TEXT_FONT)
        ducoLabel3.grid(
            row=2,
            padx=5,
            sticky="nswe")
        ducoLabel3.bind("<Button-1>", openTos)
        ducoLabel3.bind("<Enter>", colorLabelBlue)
        ducoLabel3.bind("<Leave>", colorLabelNormal)

        Label(
            register,
            text=get_string("username").upper(),
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            font=TEXT_FONT_BOLD,
        ).grid(
            row=3,
            sticky=W,
            padx=5,
            pady=(5, 0))
        username = Entry(
            register,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)
        username.grid(
            row=4,
            padx=5)

        Label(
            register,
            text=get_string("passwd").upper(),
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            font=TEXT_FONT_BOLD,
        ).grid(
            row=5,
            sticky=W,
            padx=5)
        password = Entry(
            register,
            show="*",
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)
        password.grid(
            row=6,
            padx=5)

        Label(
            register,
            text=get_string("confirm_passwd").upper(),
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            font=TEXT_FONT_BOLD,
        ).grid(
            row=7,
            sticky=W,
            padx=5)
        confpassword = Entry(
            register,
            show="*",
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)
        confpassword.grid(
            row=8,
            padx=5)

        Label(
            register,
            text=get_string("email").upper(),
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
            font=TEXT_FONT_BOLD,
        ).grid(
            row=9,
            sticky=W,
            padx=5)
        email = Entry(
            register,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR_SECONDARY)
        email.grid(
            row=10,
            padx=5)

        self.logbtn = Button(
            register,
            text=get_string("register"),
            activebackground=BACKGROUND_COLOR,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            command=self._registerprotocol,
            font=TEXT_FONT_BOLD)
        self.logbtn.grid(
            columnspan=2,
            sticky="nswe",
            padx=(5, 5),
            pady=(5, 5))
        register.configure(background=BACKGROUND_COLOR)


def LoadingWindow():
    global loading, status
    loading = Tk()
    loading.resizable(False, False)
    loading.configure(background=BACKGROUND_COLOR)
    loading.title(get_string("loading"))
    try:
        loading.iconphoto(True,
                          PhotoImage(file=resources + "duco_color.png"))
    except:
        pass
    TEXT_FONT = Font(loading,
                    size=10,
                    weight="bold")
    TEXT_FONT_BOLD = Font(loading,
                     size=14,
                     weight="bold")

    original = Image.open(resources + "duco_color.png")
    resized = original.resize((128, 128), Image.ANTIALIAS)
    github = ImageTk.PhotoImage(resized)
    github.image = github
    githubLabel = Label(loading,
                        image=github,
                        background=BACKGROUND_COLOR,
                        foreground=FONT_COLOR)
    githubLabel.grid(row=0,
                     column=0,
                     sticky=N + S + E + W,
                     pady=(5, 0),
                     padx=(5))

    Label(
        loading,
        text=get_string("duino_coin_wallet"),
        font=TEXT_FONT_BOLD,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(
        row=1,
        column=0,
        sticky=S + W,
        pady=(5, 0),
        padx=5)
    loading.update()

    status = Label(
        loading,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
        text=get_string("loading_database"),
        font=TEXT_FONT)
    status.grid(
        row=2,
        column=0,
        sticky=S + W,
        pady=(0, 5),
        padx=5)
    loading.update()


def get_string(string_name):
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name


with urlopen(
    "https://raw.githubusercontent.com/"
    + "revoxhere/"
    + "duino-coin/gh-pages/"
        + "serverip.txt") as content:
    content = content.read().decode().splitlines()
    pool_address = content[0]
    pool_port = content[1]

try:
    mkdir(resources)
except FileExistsError:
    pass

with sqlconn(f"{resources}/wallet.db") as con:
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS
        Transactions(Date TEXT, amount REAL)""")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS
        UserData(username TEXT, password TEXT, useWrapper TEXT)""")
    con.commit()

if not Path(resources + "duco.png").is_file():
    urlretrieve("https://i.imgur.com/9JzxR0B.png", resources + "duco.png")
if not Path(resources + "duco_color.png").is_file():
    urlretrieve(
        "https://github.com/"
        + "revoxhere/"
        + "duino-coin/blob/master/"
        + "Resources/duco.png?raw=true",
        resources + "duco_color.png")
if not Path(resources + "calculator.png").is_file():
    urlretrieve("https://i.imgur.com/iqE28Ej.png",
                resources + "calculator.png")
if not Path(resources + "exchange.png").is_file():
    urlretrieve("https://i.imgur.com/0qMtoZ7.png",
                resources + "exchange.png")
if not Path(resources + "discord.png").is_file():
    urlretrieve("https://i.imgur.com/LoctALa.png",
                resources + "discord.png")
if not Path(resources + "github.png").is_file():
    urlretrieve("https://i.imgur.com/PHEfWbl.png",
                resources + "github.png")
if not Path(resources + "settings.png").is_file():
    urlretrieve("https://i.imgur.com/NNEI4WL.png",
                resources + "settings.png")
if not Path(resources + "transactions.png").is_file():
    urlretrieve("https://i.imgur.com/nbVPlKk.png",
                resources + "transactions.png")
if not Path(resources + "stats.png").is_file():
    urlretrieve("https://i.imgur.com/KRfHZUM.png",
                resources + "stats.png")
if not Path(resources + "langs.json").is_file():
    urlretrieve(
        "https://raw.githubusercontent.com/"
        + "revoxhere/"
        + "duino-coin/master/Resources/"
        + "Wallet_langs.json",
        resources + "langs.json")

# Load language strings depending on system locale
with open(f"{resources}langs.json", "r", encoding="utf-8") as lang_file:
    lang_file = jsonload(lang_file)

locale = getdefaultlocale()[0]
if locale.startswith("es"):
    lang = "spanish"
elif locale.startswith("pl"):
    lang = "polish"
elif locale.startswith("fr"):
    lang = "french"
elif locale.startswith("bg"):
    lang = "bulgarian"
elif locale.startswith("nl"):
    lang = "dutch"
elif locale.startswith("ru"):
    lang = "russian"
elif locale.startswith("de"):
    lang = "german"
elif locale.startswith("tr"):
    lang = "turkish"
else:
    lang = "english"


def openTos(handler):
    open_new_tab("https://github.com/revoxhere/duino-coin#terms-of-usage")


def openGitHub(handler):
    open_new_tab("https://github.com/revoxhere/duino-coin")


def openWebsite(handler):
    open_new_tab("https://duinocoin.com")


def openExchange(handler):
    open_new_tab("https://revoxhere.github.io/duco-exchange/")


def openDiscord(handler):
    open_new_tab("https://discord.com/invite/kvBkccy")


def openTransaction(hashToOpen):
    open_new_tab("https://explorer.duinocoin.com/?search="+str(hashToOpen))


def openTransactions(handler):
    transactionsWindow = Toplevel()
    transactionsWindow.resizable(False, False)
    transactionsWindow.title(get_string("wallet_transactions"))
    transactionsWindow.transient([root])
    transactionsWindow.configure(background=BACKGROUND_COLOR)

    TEXT_FONT_BOLD_LARGE = Font(
        transactionsWindow,
        size=14,
        weight="bold")
    TEXT_FONT = Font(
        transactionsWindow,
        size=12,
        weight="normal")

    Label(
        transactionsWindow,
        text=get_string("transaction_list"),
        font=TEXT_FONT_BOLD_LARGE,
        background=BACKGROUND_COLOR,
        foreground=FOREGROUND_COLOR,
    ).grid(row=0,
           column=0,
           columnspan=2,
           sticky=S + W,
           pady=(5, 0),
           padx=5)

    Label(
        transactionsWindow,
        text=get_string("transaction_list_notice"),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=1,
           column=0,
           columnspan=2,
           sticky=S + W,
           pady=(5, 0),
           padx=5)

    listbox = Listbox(
        transactionsWindow,
        width="35",
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    listbox.grid(
        row=2,
        column=0,
        sticky=S + W + N + E,
        padx=(5, 0),
        pady=(0, 5))
    scrollbar = Scrollbar(transactionsWindow,
                          background=BACKGROUND_COLOR)
    scrollbar.grid(
        row=2,
        column=1,
        sticky=N + S,
        padx=(0, 5),
        pady=(0, 5))

    for i in gtxl:
        listbox.insert(END, gtxl[i]["Sender"] + " to " + gtxl[i]["Recipient"] + ": " + str(gtxl[i]["Amount"]) + " DUCO")
        
    def getSelection(event):
        try:
            selection = listbox.curselection()[0]
            openTransaction(gtxl[str(selection)]["Hash"])
        except IndexError:
            pass

    listbox.bind("<Button-1>", getSelection)
    listbox.config(yscrollcommand=scrollbar.set, font=TEXT_FONT)
    scrollbar.config(command=listbox.yview)


def currencyConvert():
    fromcurrency = fromCurrencyInput.get(fromCurrencyInput.curselection())
    tocurrency = toCurrencyInput.get(toCurrencyInput.curselection())
    amount = amountInput.get()
    try:
        if fromcurrency != "DUCO":
            currencyapi = get(
                "https://api.exchangeratesapi.io/latest?base=" +
                str(fromcurrency),
                data=None)
            exchangerates = loads(currencyapi.content.decode())
        else:
            currencyapi = get(
                "https://api.exchangeratesapi.io/latest?base=USD",
                data=None)
            exchangerates = loads(currencyapi.content.decode())

        if currencyapi.status_code == 200:  # Check for reponse
            if fromcurrency == "DUCO" and tocurrency != "DUCO":
                exchangerates = loads(currencyapi.content.decode())
                result = (
                    str(
                        round(
                            float(amount)
                            * float(duco_fiat_value)
                            * float(exchangerates["rates"][tocurrency]),
                            6))
                    + " "
                    + str(tocurrency))
            else:
                if tocurrency == "DUCO":
                    currencyapisss = get(
                        "https://api.exchangeratesapi.io/latest?symbols="
                        + str(fromcurrency)
                        + ",USD",
                        data=None)
                    if currencyapi.status_code == 200:  # Check for reponse
                        ratesjson = loads(
                            currencyapisss.content.decode())
                        result = str(
                            str(round(
                                float(amount)
                                * float(1 / duco_fiat_value)
                                / float(ratesjson["rates"][fromcurrency]),
                                6))
                            + " "
                            + str(tocurrency))
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
                        + str(tocurrency))
    except:
        result = get_string("calculate_error")

    result = get_string("result") + ": " + result
    conversionresulttext.set(str(result))
    calculatorWindow.update()


def openCalculator(handler):
    global conversionresulttext
    global fromCurrencyInput
    global toCurrencyInput
    global amountInput
    global calculatorWindow

    currencyapi = get(
        "https://api.exchangeratesapi.io/latest",
        data=None)
    if currencyapi.status_code == 200:  # Check for reponse
        exchangerates = loads(currencyapi.content.decode())
        exchangerates["rates"]["DUCO"] = float(duco_fiat_value)

    calculatorWindow = Toplevel()
    calculatorWindow.resizable(False, False)
    calculatorWindow.title(get_string("wallet_calculator"))
    calculatorWindow.transient([root])
    calculatorWindow.configure(background=BACKGROUND_COLOR)

    TEXT_FONT_BOLD = Font(
        calculatorWindow,
        size=12,
        weight="bold")
    TEXT_FONT_BOLD_LARGE = Font(
        calculatorWindow,
        size=14,
        weight="bold")
    TEXT_FONT = Font(
        calculatorWindow,
        size=12,
        weight="normal")

    Label(
        calculatorWindow,
        text=get_string("currency_converter"),
        font=TEXT_FONT_BOLD_LARGE,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=0,
           columnspan=2,
           column=0,
           sticky=S + W,
           pady=5,
           padx=5)

    Label(
        calculatorWindow,
        text=get_string("from"),
        font=TEXT_FONT_BOLD,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=1,
           column=0,
           sticky=S + W,
           padx=5)
    fromCurrencyInput = Listbox(
        calculatorWindow,
        exportselection=False,
        background=BACKGROUND_COLOR,
        selectbackground=FOREGROUND_COLOR,
        border="0",
        font=TEXT_FONT,
        foreground=FONT_COLOR,
        width="20",
        height="13",
    )
    fromCurrencyInput.grid(row=2,
                           column=0,
                           sticky=S + W,
                           padx=(5, 0))
    i = 0
    for currency in exchangerates["rates"]:
        fromCurrencyInput.insert(i, currency)
        i = i + 1
    vsb = Scrollbar(
        calculatorWindow,
        orient="vertical",
        command=fromCurrencyInput.yview,
        background=BACKGROUND_COLOR,
    )
    vsb.grid(row=2,
             column=1,
             sticky="ns",
             padx=(0, 5))
    fromCurrencyInput.configure(yscrollcommand=vsb.set)

    fromCurrencyInput.select_set(32)
    fromCurrencyInput.event_generate("<<ListboxSelect>>")

    Label(
        calculatorWindow,
        text=get_string("to"),
        font=TEXT_FONT_BOLD,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=1,
           column=3,
           columnspan=2,
           sticky=S + W,
           padx=5)
    toCurrencyInput = Listbox(
        calculatorWindow,
        exportselection=False,
        background=BACKGROUND_COLOR,
        selectbackground=FOREGROUND_COLOR,
        border="0",
        foreground=FONT_COLOR,
        font=TEXT_FONT,
        width="20",
        height="13")
    toCurrencyInput.grid(
        row=2,
        column=3,
        sticky=S + W,
        padx=(5, 0))
    i = 0
    for currency in exchangerates["rates"]:
        toCurrencyInput.insert(i, currency)
        i = i + 1
    vsb2 = Scrollbar(
        calculatorWindow,
        orient="vertical",
        command=toCurrencyInput.yview,
        background=BACKGROUND_COLOR,)
    vsb2.grid(
        row=2,
        column=4,
        sticky="ns",
        padx=(0, 5))
    toCurrencyInput.configure(yscrollcommand=vsb2.set)

    toCurrencyInput.select_set(0)
    toCurrencyInput.event_generate("<<ListboxSelect>>")

    Label(
        calculatorWindow,
        text=get_string("input_amount"),
        font=TEXT_FONT_BOLD,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=3,
           columnspan=2,
           column=0,
           sticky=S + W,
           padx=5)

    def clear_ccamount_placeholder(self):
        amountInput.delete("0", "100")

    amountInput = Entry(
        calculatorWindow,
        foreground=FOREGROUND_COLOR_SECONDARY,
        border="0",
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,)
    amountInput.grid(
        row=4,
        column=0,
        sticky=N + S + W + E,
        padx=5,
        columnspan=2,
        pady=(0, 5))
    amountInput.insert("0", str(global_balance))
    amountInput.bind("<FocusIn>", clear_ccamount_placeholder)

    Button(
        calculatorWindow,
        text=get_string("calculate"),
        font=TEXT_FONT_BOLD,
        foreground=FOREGROUND_COLOR,
        activebackground=BACKGROUND_COLOR,
        background=BACKGROUND_COLOR,
        command=currencyConvert,
    ).grid(row=3,
           columnspan=2,
           column=2,
           sticky=N + S + W + E,
           pady=(5, 0),
           padx=5)

    conversionresulttext = StringVar(calculatorWindow)
    conversionresulttext.set(f'{get_string("result")}: 0.0')
    conversionresultLabel = Label(
        calculatorWindow,
        textvariable=conversionresulttext,
        font=TEXT_FONT_BOLD,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,)
    conversionresultLabel.grid(
        row=4,
        columnspan=2,
        column=2,
        pady=(0, 5))

    calculatorWindow.mainloop()


def openStats(handler):
    statsApi = get(
        "https://raw.githubusercontent.com/"
        + "revoxhere/"
        + "duco-statistics/master/"
        + "api.json",
        data=None)
    if statsApi.status_code == 200:  # Check for reponse
        statsApi = statsApi.json()

    statsWindow = Toplevel()
    statsWindow.resizable(False, False)
    statsWindow.title(get_string("statistics_title"))
    statsWindow.transient([root])
    statsWindow.configure(background=BACKGROUND_COLOR)

    TEXT_FONT_BOLD_LARGE = Font(
        statsWindow,
        size=14,
        weight="bold")
    TEXT_FONT = Font(
        statsWindow,
        size=12,
        weight="normal")

    Active_workers_listbox = Listbox(
        statsWindow,
        exportselection=False,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
        border="0",
        font=TEXT_FONT,
        width="65",
        height="8",)
    Active_workers_listbox.grid(
        row=1,
        columnspan=2,
        sticky=N + E + S + W,
        pady=(0, 5),
        padx=5)
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
                    + statsApi["Miners"][threadid]["Rejected"]))

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
                + shares)
            i += 1
    if i == 0:
        Active_workers_listbox.insert(i, get_string("statistics_miner_warning"))

    totalHashrateString = str(int(totalHashrate)) + " H/s"
    if totalHashrate > 1000000000:
        totalHashrateString = str(
            round(totalHashrate / 1000000000, 2)) + " GH/s"
    elif totalHashrate > 1000000:
        totalHashrateString = str(round(totalHashrate / 1000000, 2)) + " MH/s"
    elif totalHashrate > 1000:
        totalHashrateString = str(round(totalHashrate / 1000, 2)) + " kH/s"

    Active_workers_listbox.configure(height=i)
    Active_workers_listbox.select_set(32)
    Active_workers_listbox.event_generate("<<ListboxSelect>>")

    Label(
        statsWindow,
        text=f'{get_string("your_miners")} - ' + totalHashrateString,
        font=TEXT_FONT_BOLD_LARGE,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(
        row=0,
        column=0,
        columnspan=2,
        sticky=S + W,
        pady=5,
        padx=5)

    Label(
        statsWindow,
        text=get_string("richlist"),
        font=TEXT_FONT_BOLD_LARGE,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(
        row=2,
        column=0,
        sticky=S + W,
        pady=5,
        padx=5)
    Top_10_listbox = Listbox(
        statsWindow,
        exportselection=False,
        border="0",
        font=TEXT_FONT,
        width="30",
        height="10",
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    Top_10_listbox.grid(
        row=3,
        column=0,
        rowspan=10,
        sticky=N + E + S + W,
        pady=(0, 5),
        padx=5)

    for i in statsApi["Top 10 richest miners"]:
        Top_10_listbox.insert(i, statsApi["Top 10 richest miners"][i])

    Top_10_listbox.select_set(32)
    Top_10_listbox.event_generate("<<ListboxSelect>>")

    Label(
        statsWindow,
        text=get_string("network_info"),
        font=TEXT_FONT_BOLD_LARGE,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=2,
           column=1,
           sticky=S + W,
           padx=5,
           pady=5)
    Label(
        statsWindow,
        text=f'{get_string("difficulty")}: '
        + str(statsApi["Current difficulty"]),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=3,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'{get_string("mined_blocks")}: '
        + str(statsApi["Mined blocks"]),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=4,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'{get_string("network_hashrate")}: '
        + str(statsApi["Pool hashrate"]),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=5,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'{get_string("active_miners")}: '
        + str(len(statsApi["Miners"])),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=6,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'1 DUCO {get_string("estimated_price")}: $'
        + str(statsApi["Duco price"]),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=7,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'{get_string("registered_users")}: '
        + str(statsApi["Registered users"]),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=8,
           column=1,
           sticky=S + W,
           padx=5)
    Label(
        statsWindow,
        text=f'{get_string("mined_duco")}: '
        + str(statsApi["All-time mined DUCO"])
        + " ᕲ",
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(row=9,
           column=1,
           sticky=S + W,
           padx=5)

    statsWindow.mainloop()


def openWrapper(handler):
    def Wrap():
        amount = amountWrap.get()
        print("Got amount: ", amount)
        soc = socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)
        try:
            float(amount)
        except:
            pass
        else:
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password),
                encoding="utf8"))
            _ = soc.recv(10)
            soc.send(
                bytes(
                    "WRAP,"
                    + str(amount)
                    + ","
                    + str(pub_key),
                    encoding="utf8"))
            soc.close()
            sleep(2)
            wrapperWindow.quit()

    try:
        pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
    except:
        messagebox.showerror(
            title=get_string("wrapper_error_title"),
            message=get_string("wrapper_error"))
    else:
        if tronpy_installed:
            pub_key = pubkeyfile.read()
            pubkeyfile.close()

            wrapperWindow = Toplevel()
            wrapperWindow.resizable(False, False)
            wrapperWindow.title(get_string("wrapper_title"))
            wrapperWindow.transient([root])
            wrapperWindow.configure()

            askWrapAmount = Label(
                wrapperWindow,
                text=get_string("wrapper_amount_to_wrap") + ":")
            askWrapAmount.grid(row=0,
                               column=0,
                               sticky=N + W)
            amountWrap = Entry(wrapperWindow,
                               border="0",
                               font=Font(size=15))
            amountWrap.grid(row=1,
                            column=0,
                            sticky=N + W)
            wrapButton = Button(wrapperWindow,
                                text="Wrap",
                                command=Wrap)
            wrapButton.grid(row=2,
                            column=0,
                            sticky=N + W)
        else:
            messagebox.showerror(
                title=get_string("wrapper_error_title"),
                message=get_string("wrapper_error_tronpy"))


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
            use_wrapper = True
        except InvalidToken:
            print(get_string("invalid_passphrase"))
            use_wrapper = False

        amount = amountUnWrap.get()
        print("Got amount:", amount)
        soc = socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)
        try:
            float(amount)
        except:
            pass
        else:
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password), encoding="utf8"))
            _ = soc.recv(10)
            if use_wrapper:
                pendingvalues = wduco.functions.pendingWithdrawals(
                    pub_key, username)
                # transaction wasn't initiated, but variable should be declared
                txn_success = False
                try:
                    amount = float(amount)
                except ValueError:
                    print("Value should be numeric - aborting")
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
                            .sign(PrivateKey(bytes.fromhex(priv_key))))
                        txn = txn.broadcast()
                        txnfeedback = txn.result()
                        if txnfeedback:
                            txn_success = True
                        else:
                            txn_success = False
                    if txn_success or amount <= pendingvalues:
                        soc.send(
                            bytes(
                                "UNWRAP,"
                                + str(amount)
                                + ","
                                + str(pub_key),
                                encoding="utf8"))

                soc.close()
                sleep(2)
                unWrapperWindow.quit()

    try:
        pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
        pubkeyfile.read()
        pubkeyfile.close()
    except:
        messagebox.showerror(
            title=get_string("wrapper_error_title"),
            message=get_string("wrapper_error"))
    else:
        if tronpy_installed:
            unWrapperWindow = Toplevel()
            unWrapperWindow.resizable(False, False)
            unWrapperWindow.title(get_string("unwrapper_title"))
            unWrapperWindow.transient([root])
            unWrapperWindow.configure()
            askAmount = Label(
                unWrapperWindow,
                text=get_string("unwrap_amount"))
            askAmount.grid(row=1,
                           column=0,
                           sticky=N + W)

            amountUnWrap = Entry(
                unWrapperWindow,
                border="0",
                font=Font(size=15))
            amountUnWrap.grid(row=2,
                              column=0,
                              sticky=N + W)

            askPassphrase = Label(
                unWrapperWindow,
                text=get_string("ask_passphrase"))
            askPassphrase.grid(row=4,
                               column=0,
                               sticky=N + W)

            passphraseEntry = Entry(
                unWrapperWindow,
                border="0",
                font=Font(size=15))
            passphraseEntry.grid(
                row=5,
                column=0,
                sticky=N + W)

            wrapButton = Button(
                unWrapperWindow,
                text=get_string("unwrap_duco"),
                command=UnWrap)
            wrapButton.grid(
                row=7,
                column=0,
                sticky=N + W)
        else:
            messagebox.showerror(
                title=get_string("wrapper_error"),
                message=get_string("wrapper_error_tronpy"))


def openSettings(handler):
    def _wrapperconf():
        if tronpy_installed:
            privkey_input = StringVar()
            passphrase_input = StringVar()
            wrapconfWindow = Toplevel()
            wrapconfWindow.resizable(False, False)
            wrapconfWindow.title(get_string("wrapper_title"))
            wrapconfWindow.transient([root])
            wrapconfWindow.configure()

            def setwrapper():
                if privkey_input and passphrase_input:
                    priv_key = privkey_entry.get()
                    print("Got priv key:", priv_key)
                    passphrase = passphrase_entry.get()
                    print("Got passphrase:", passphrase)
                    try:
                        pub_key = PrivateKey(
                            bytes.fromhex(priv_key)
                        ).public_key.to_base58check_address()
                    except:
                        pass
                    else:
                        print("Saving data")

                        privkeyfile = open(
                            str(f"{resources}/DUCOPrivKey.encrypt"), "w")
                        privkeyfile.write(
                            str(password_encrypt(
                                priv_key.encode(), passphrase
                            ).decode()))
                        privkeyfile.close()

                        pubkeyfile = open(
                            str(f"{resources}/DUCOPubKey.pub"), "w")
                        pubkeyfile.write(pub_key)
                        pubkeyfile.close()

                        Label(wrapconfWindow, text=get_string(
                            "wrapper_success")).pack()
                        wrapconfWindow.quit()

            title = Label(
                wrapconfWindow,
                text=get_string("wrapper_config_title"),
                font=Font(size=20))
            title.grid(row=0,
                       column=0,
                       sticky=N + W,
                       padx=5)

            askprivkey = Label(
                wrapconfWindow,
                text=get_string("ask_private_key"))
            askprivkey.grid(row=1,
                            column=0,
                            sticky=N + W)

            privkey_entry = Entry(
                wrapconfWindow,
                font=TEXT_FONT,
                textvariable=privkey_input)
            privkey_entry.grid(row=2,
                               column=0,
                               sticky=N + W)

            askpassphrase = Label(wrapconfWindow,
                                  text=get_string("passphrase"))
            askpassphrase.grid(row=3,
                               column=0,
                               sticky=N + W)

            passphrase_entry = Entry(
                wrapconfWindow,
                font=TEXT_FONT,
                textvariable=passphrase_input)
            passphrase_entry.grid(row=4,
                                  column=0,
                                  sticky=N + W)

            wrapConfigButton = Button(
                wrapconfWindow,
                text=get_string("configure_wrapper_lowercase"),
                command=setwrapper)
            wrapConfigButton.grid(row=5,
                                  column=0,
                                  sticky=N + W)

            wrapconfWindow.mainloop()

        else:
            messagebox.showerror(
                title=get_string("wrapper_error"),
                message=get_string("wrapper_error_tronpy"))

    def _logout():
        try:
            with sqlconn(f"{resources}/wallet.db") as con:
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
        with sqlconn(f"{resources}/wallet.db") as con:
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
                        soc = socket()
                        soc.connect((pool_address, int(pool_port)))
                        soc.recv(3)
                        soc.send(
                            bytes(
                                "LOGI,"
                                + str(username)
                                + ","
                                + str(password), encoding="utf8"))
                        soc.recv(2)
                        soc.send(
                            bytes(
                                "CHGP,"
                                + str(oldpasswordS)
                                + ","
                                + str(newpasswordS),
                                encoding="utf8"))
                        response = soc.recv(128).decode(
                            "utf8").rstrip("\n").split(",")
                        soc.close()

                        if not "OK" in response[0]:
                            messagebox.showerror(
                                title=get_string("change_passwd_error"),
                                message=response[1])
                        else:
                            messagebox.showinfo(
                                title=get_string("change_passwd_ok"),
                                message=response[1])
                            try:
                                try:
                                    with sqlconn(
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
                            title=get_string("change_passwd_error"),
                            message=get_string("error_passwd_dont_match"))
                else:
                    messagebox.showerror(
                        title=get_string("change_passwd_error"),
                        message=get_string("fill_the_blanks_warning"))
            else:
                messagebox.showerror(
                    title=get_string("change_passwd_error"),
                    message=get_string("same_passwd_error"))

        settingsWindow.destroy()
        changepassWindow = Toplevel()
        changepassWindow.title(get_string("change_passwd_lowercase"))
        changepassWindow.resizable(False, False)
        changepassWindow.transient([root])
        changepassWindow.configure(background=BACKGROUND_COLOR)

        TEXT_FONT_BOLD = Font(changepassWindow, size=12, weight="bold")
        TEXT_FONT = Font(changepassWindow, size=12, weight="normal")

        Label(
            changepassWindow,
            text=get_string("old_passwd"),
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=0,
               sticky=W,
               padx=5)
        oldpassword = Entry(
            changepassWindow,
            show="*",
            font=TEXT_FONT,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        oldpassword.grid(row=1,
                         sticky="nswe",
                         padx=5)

        Label(
            changepassWindow,
            text=get_string("new_passwd"),
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=2,
               sticky=W,
               padx=5)
        newpassword = Entry(
            changepassWindow,
            show="*",
            font=TEXT_FONT,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        newpassword.grid(row=3,
                         sticky="nswe",
                         padx=5)

        Label(
            changepassWindow,
            text=get_string("confirm_new_passwd"),
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=4,
               sticky=W,
               padx=5)
        confpassword = Entry(
            changepassWindow,
            show="*",
            font=TEXT_FONT,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        confpassword.grid(row=5,
                          sticky="nswe",
                          padx=5)

        chgpbtn = Button(
            changepassWindow,
            text=get_string("change_passwd"),
            command=_changepassprotocol,
            foreground=FOREGROUND_COLOR,
            font=TEXT_FONT_BOLD,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR)
        chgpbtn.grid(columnspan=2,
                     sticky="nswe",
                     pady=5,
                     padx=5)

    settingsWindow = Toplevel()
    settingsWindow.resizable(False, False)
    settingsWindow.title(get_string("settings_title"))
    settingsWindow.transient([root])
    settingsWindow.configure(background=BACKGROUND_COLOR)
    TEXT_FONT = Font(
        settingsWindow,
        size=12,
        weight="normal")
    TEXT_FONT_BOLD_LARGE = Font(
        settingsWindow,
        size=12,
        weight="bold")

    Label(
        settingsWindow,
        text=get_string("uppercase_settings"),
        font=TEXT_FONT_BOLD_LARGE,
        foreground=FOREGROUND_COLOR,
        background=BACKGROUND_COLOR,
    ).grid(row=0,
           column=0,
           columnspan=4,
           sticky=S + W,
           pady=(5, 5),
           padx=(5, 0))

    logoutbtn = Button(
        settingsWindow,
        text=get_string("logout"),
        command=_logout,
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        activebackground=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    logoutbtn.grid(row=1,
                   column=0,
                   columnspan=4,
                   sticky="nswe",
                   padx=5)

    chgpassbtn = Button(
        settingsWindow,
        text=get_string("change_passwd"),
        command=_chgpass,
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        activebackground=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    chgpassbtn.grid(row=2,
                    column=0,
                    columnspan=4,
                    sticky="nswe",
                    padx=5)

    wrapperconfbtn = Button(
        settingsWindow,
        text=get_string("configure_wrapper"),
        command=_wrapperconf,
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        activebackground=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    wrapperconfbtn.grid(row=3,
                        column=0,
                        columnspan=4,
                        sticky="nswe",
                        padx=5)

    cleartransbtn = Button(
        settingsWindow,
        text=get_string("clear_transactions"),
        command=_cleartrs,
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        activebackground=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    cleartransbtn.grid(row=4,
                       column=0,
                       columnspan=4,
                       sticky="nswe",
                       padx=5)

    separator = ttk.Separator(settingsWindow, orient="horizontal")
    separator.grid(
        row=5,
        column=0,
        columnspan=4,
        sticky=N + S + E + W,
        padx=(5, 5),
        pady=5)

    Label(
        settingsWindow,
        text=f'{get_string("logged_in_as")}: ' + str(username),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(
        row=6,
        column=0,
        columnspan=4,
        padx=5,
        sticky=S + W)
    Label(
        settingsWindow,
        text=f'{get_string("wallet_version")}: ' + str(VERSION),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(
        row=7,
        column=0,
        columnspan=4,
        padx=5,
        sticky=S + W)
    Label(
        settingsWindow,
        text=get_string("translation_author_message")
        + " "
        + get_string("translation_author"),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(
        row=8,
        column=0,
        columnspan=4,
        padx=5,
        sticky=S + W)
    Label(
        settingsWindow,
        text=get_string("config_dev_warning"),
        font=TEXT_FONT,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR,
    ).grid(
        row=9,
        column=0,
        columnspan=4,
        padx=5,
        sticky=S + W)

    separator = ttk.Separator(settingsWindow, orient="horizontal")
    separator.grid(
        row=10,
        column=0,
        columnspan=4,
        sticky=N + S + E + W,
        padx=(5, 5),
        pady=5)

    original = Image.open(resources + "duco.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    website = ImageTk.PhotoImage(resized)
    website.image = website
    websiteLabel = Label(
        settingsWindow,
        image=website,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    websiteLabel.grid(
        row=11,
        column=0,
        sticky=N + S + E + W,
        padx=(5, 0),
        pady=(0, 5))
    websiteLabel.bind("<Button-1>", openWebsite)

    original = Image.open(resources + "github.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    github = ImageTk.PhotoImage(resized)
    github.image = github
    githubLabel = Label(
        settingsWindow,
        image=github,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    githubLabel.grid(
        row=11,
        column=1,
        sticky=N + S + E + W,
        pady=(0, 5))
    githubLabel.bind("<Button-1>", openGitHub)

    original = Image.open(resources + "exchange.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    exchange = ImageTk.PhotoImage(resized)
    exchange.image = exchange
    exchangeLabel = Label(
        settingsWindow,
        image=exchange,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    exchangeLabel.grid(
        row=11,
        column=2,
        sticky=N + S + E + W,
        pady=(0, 5))
    exchangeLabel.bind("<Button-1>", openExchange)

    original = Image.open(resources + "discord.png")
    resized = original.resize((48, 48), Image.ANTIALIAS)
    discord = ImageTk.PhotoImage(resized)
    discord.image = discord
    discordLabel = Label(
        settingsWindow,
        image=discord,
        background=BACKGROUND_COLOR,
        foreground=FONT_COLOR)
    discordLabel.grid(
        row=11,
        column=3,
        sticky=N + S + E + W,
        padx=(0, 5),
        pady=(0, 5))
    discordLabel.bind("<Button-1>", openDiscord)


oldbalance = 0
balance = 0
unpaid_balance = 0


def getBalance():
    global oldbalance
    global balance
    global unpaid_balance
    global global_balance
    global gtxl
    try:
        soc = socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)
        soc.send(bytes(
            "LOGI,"
            + str(username)
            + ","
            + str(password), encoding="utf8"))
        _ = soc.recv(2)
        soc.send(bytes(
            "BALA",
            encoding="utf8"))
        oldbalance = balance
        balance = float(soc.recv(64).decode().rstrip("\n"))
        global_balance = round(float(balance), 8)

        try:
            gtxl = {}
            soc.send(bytes(
                "GTXL," + str(username) + ",7",
                encoding="utf8"))
            gtxl = str(soc.recv(8096).decode().rstrip("\n").replace("\'", "\""))
            print(gtxl)
            gtxl = jsonloads(gtxl)
        except Exception as e:
            print("Error getting transaction list: " + str(e))

        if oldbalance != balance:
            difference = float(balance) - float(oldbalance)
            dif_with_unpaid = (
                float(balance) - float(oldbalance)) + unpaid_balance
            if float(balance) != float(difference):
                if (dif_with_unpaid >= MIN_TRANSACTION_VALUE
                        or dif_with_unpaid < 0
                        ):
                    now = datetime.now()
                    difference = round(dif_with_unpaid, 8)
                    if (
                        difference >= MIN_TRANSACTION_VALUE_NOTIFY
                        or difference < 0
                        and notificationsEnabled
                    ):
                        notification = Notify()
                        notification.title = get_string("duino_coin_wallet")
                        notification.message = (
                            get_string("notification_new_transaction")
                            + "\n"
                            + now.strftime("%d.%m.%Y %H:%M:%S\n")
                            + str(round(difference, 6))
                            + " DUCO")
                        notification.icon = f"{resources}/duco_color.png"
                        notification.send(block=False)
                    with sqlconn(f"{resources}/wallet.db") as con:
                        cur = con.cursor()
                        cur.execute(
                            """INSERT INTO Transactions(Date, amount)
                                VALUES(?, ?)""", (
                                now.strftime("%d.%m.%Y %H:%M:%S"),
                                round(difference, 8)))
                        con.commit()
                        unpaid_balance = 0
                else:
                    unpaid_balance += float(balance) - float(oldbalance)
    except Exception as e:
        print("Retrying in 3s. (" + str(e) + ")")
    Timer(3, getBalance).start()


def getwbalance():
    if tronpy_installed:
        try:
            pubkeyfile = open(str(f"{resources}/DUCOPubKey.pub"), "r")
            pub_key = pubkeyfile.read()
            pubkeyfile.close()
            wBalance = float(wduco.functions.balanceOf(pub_key)) / (10 ** 6)
            return wBalance
        except:
            return 0.0
    else:
        return 0.0


profitCheck = 0


def updateBalanceLabel():
    global profit_array, profitCheck
    try:
        balancetext.set(str(round(global_balance, 7)) + " ᕲ")
        wbalancetext.set(str(getwbalance()) + " wᕲ")
        balanceusdtext.set("$" + str(round(global_balance * duco_fiat_value, 4)))

        with sqlconn(f"{resources}/wallet.db") as con:
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
            sessionprofittext.set(
                get_string("session") + ": "
                + str(profit_array[0]) + " ᕲ")
            minuteprofittext.set(
                "≈" + str(profit_array[1]) + " ᕲ/"
                + get_string("minute"))
            hourlyprofittext.set(
                "≈" + str(profit_array[2]) + " ᕲ/"
                + get_string("hour"))
            dailyprofittext.set(
                "≈"
                + str(profit_array[3])
                + " ᕲ/"
                + get_string("day")
                + " ($"
                + str(round(profit_array[3] * duco_fiat_value, 4))
                + ")")
        else:
            if profitCheck > 10:
                sessionprofittext.set(get_string("sessionprofit_unavailable1"))
                minuteprofittext.set(get_string("sessionprofit_unavailable2"))
                hourlyprofittext.set("")
                dailyprofittext.set("")
            profitCheck += 1
    except:
        _exit(0)
    Timer(1, updateBalanceLabel).start()

curr_bal = 0
def calculateProfit(start_bal):
    try:  # Thanks Bilaboz for the code!
        global curr_bal, profit_array

        prev_bal = curr_bal
        curr_bal = global_balance
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
                round(daily, 2)]
    except:
        _exit(0)
    Timer(10, calculateProfit, [start_bal]).start()


def sendFunds(handler):
    recipientStr = recipient.get()
    amountStr = amount.get()

    MsgBox = messagebox.askquestion(
        get_string("warning"),
        get_string("send_funds_warning")
        + str(amountStr)
        + " DUCO "
        + get_string("send_funds_to")
        + " "
        + str(recipientStr),
        icon="warning",)
    if MsgBox == "yes":
        soc = socket()
        soc.connect((pool_address, int(pool_port)))
        soc.recv(3)

        soc.send(bytes(
            "LOGI,"
            + str(username)
            + ","
            + str(password),
            encoding="utf8"))
        response = soc.recv(2)
        soc.send(
            bytes(
                "SEND,"
                + "-"
                + ","
                + str(recipientStr)
                + ","
                + str(amountStr),
                encoding="utf8"))
        response = soc.recv(128).decode().rstrip("\n").split(",")
        soc.close()

        if "OK" in str(response[0]):
            MsgBox = messagebox.showinfo(response[0],
                                         response[1]
                                         + "\nTXID:"
                                         + response[2])
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
    startTime = int(time())
    while True:
        try:
            balance = round(global_balance, 4)
            RPC.update(
                details=str(balance)
                + " ᕲ ($"
                + str(round(duco_fiat_value * balance, 2))
                + ")",
                start=startTime,
                large_image="duco",
                large_text="Duino-Coin, "
                + "a coin that can be mined with almost everything, "
                + "including AVR boards",
                buttons=[
                    {"label": "Learn more",
                     "url": "https://duinocoin.com"},
                    {"label": "Discord Server",
                     "url": "https://discord.gg/k48Ht5y"}])
        except:  # Discord not launched
            pass
        sleep(15)


class Wallet:
    def __init__(self, master):
        global recipient
        global amount
        global balancetext
        global wbalancetext
        global sessionprofittext
        global minuteprofittext
        global hourlyprofittext
        global dailyprofittext
        global balanceusdtext
        global transactionstext
        global curr_bal
        global profit_array
        try:
            loading.destroy()
        except:
            pass

        textFont4 = Font(
            size=14,
            weight="bold")
        TEXT_FONT_BOLD_LARGE = Font(
            size=12,
            weight="bold")
        TEXT_FONT_BOLD = Font(
            size=18,
            weight="bold")
        TEXT_FONT = Font(
            size=12,
            weight="normal")

        self.master = master
        master.resizable(False, False)
        master.configure(background=BACKGROUND_COLOR)
        master.title(get_string("duino_coin_wallet"))

        Label(
            master,
            text=f'{get_string("uppercase_duino_coin_wallet")}: '
            + str(username),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
        ).grid(
            row=0,
            column=0,
            sticky=S + W,
            columnspan=4,
            pady=(5, 0),
            padx=(5, 0))

        balancetext = StringVar()
        wbalancetext = StringVar()
        balancetext.set(get_string("please_wait"))
        if tronpy_installed:
            wbalancetext.set(get_string("please_wait"))
        else:
            wbalancetext.set("0.00")
        balanceLabel = Label(
            master,
            textvariable=balancetext,
            font=TEXT_FONT_BOLD,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        balanceLabel.grid(row=1,
                          column=0,
                          columnspan=3,
                          sticky=S + W,
                          padx=(5, 0))

        wbalanceLabel = Label(
            master,
            textvariable=wbalancetext,
            font=textFont4,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        wbalanceLabel.grid(row=2,
                           column=0,
                           columnspan=3,
                           sticky=S + W,
                           padx=(5, 0))

        balanceusdtext = StringVar()
        balanceusdtext.set(get_string("please_wait"))

        Label(
            master,
            textvariable=balanceusdtext,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=1,
               column=3,
               sticky=S + E,
               pady=(0, 1.5),
               padx=(0, 5))

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(
            row=4,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=(5, 5),
            pady=(0, 5))

        def clear_recipient_placeholder(self):
            recipient.delete("0", "100")

        def clear_amount_placeholder(self):
            amount.delete("0", "100")

        Label(
            master,
            text=get_string("recipient"),
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=5,
               column=0,
               sticky=W + S,
               padx=(5, 0))

        recipient = Entry(
            master,
            border="0",
            font=TEXT_FONT,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        recipient.grid(row=5,
                       column=1,
                       sticky=N + W + S + E,
                       columnspan=3,
                       padx=(0, 5))
        recipient.insert("0", "revox")
        recipient.bind("<FocusIn>", clear_recipient_placeholder)

        Label(
            master,
            text=get_string("amount"),
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR,
        ).grid(row=6,
               column=0,
               sticky=W + S,
               padx=(5, 0))

        amount = Entry(
            master,
            border="0",
            font=TEXT_FONT,
            foreground=FOREGROUND_COLOR_SECONDARY,
            background=BACKGROUND_COLOR)
        amount.grid(row=6,
                    column=1,
                    sticky=N + W + S + E,
                    columnspan=3,
                    padx=(0, 5))
        amount.insert("0", str(VERSION))
        amount.bind("<FocusIn>", clear_amount_placeholder)

        sendLabel = Button(
            master,
            text=get_string("send_funds"),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR)
        sendLabel.grid(
            row=8,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=(5),
            pady=(1, 2))
        sendLabel.bind("<Button-1>", sendFunds)

        wrapLabel = Button(
            master,
            text=get_string("wrap_duco"),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR)
        wrapLabel.grid(
            row=9,
            column=0,
            sticky=N + S + E + W,
            columnspan=2,
            padx=(5, 1),
            pady=(1, 5))
        wrapLabel.bind("<Button-1>", openWrapper)

        wrapLabel = Button(
            master,
            text=get_string("unwrap_duco"),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
            activebackground=BACKGROUND_COLOR)
        wrapLabel.grid(
            row=9,
            column=2,
            sticky=N + S + E + W,
            columnspan=2,
            padx=(1, 5),
            pady=(1, 5))
        wrapLabel.bind("<Button-1>", openUnWrapper)

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(
            row=10,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=(5, 5))

        Label(
            master,
            text=get_string("estimated_profit"),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
        ).grid(row=11,
               column=0,
               sticky=S + W,
               columnspan=4,
               pady=(5, 0),
               padx=(5, 0))

        sessionprofittext = StringVar()
        sessionprofittext.set(get_string("please_wait_calculating"))
        sessionProfitLabel = Label(
            master,
            textvariable=sessionprofittext,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        sessionProfitLabel.grid(
            row=12,
            column=0,
            sticky=W,
            columnspan=4,
            padx=5)

        minuteprofittext = StringVar()
        minuteProfitLabel = Label(
            master,
            textvariable=minuteprofittext,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        minuteProfitLabel.grid(
            row=13,
            column=0,
            sticky=W,
            columnspan=4,
            padx=5)

        hourlyprofittext = StringVar()
        hourlyProfitLabel = Label(
            master,
            textvariable=hourlyprofittext,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        hourlyProfitLabel.grid(
            row=14,
            column=0,
            sticky=W,
            columnspan=4,
            padx=5)

        dailyprofittext = StringVar()
        dailyprofittext.set("")
        dailyProfitLabel = Label(
            master,
            textvariable=dailyprofittext,
            font=TEXT_FONT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        dailyProfitLabel.grid(
            row=15,
            column=0,
            sticky=W,
            columnspan=4,
            padx=5)

        separator = ttk.Separator(master, orient="horizontal")
        separator.grid(
            row=16,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=5)

        Label(
            master,
            text=get_string("local_transactions"),
            font=TEXT_FONT_BOLD_LARGE,
            foreground=FOREGROUND_COLOR,
            background=BACKGROUND_COLOR,
        ).grid(row=17,
               column=0,
               sticky=S + W,
               columnspan=4,
               pady=(5, 0),
               padx=(5, 0))

        transactionstext = StringVar()
        transactionstext.set("")
        transactionstextLabel = Label(
            master,
            textvariable=transactionstext,
            font=TEXT_FONT,
            justify=LEFT,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        transactionstextLabel.grid(
            row=18,
            column=0,
            sticky=W,
            columnspan=4,
            padx=5,
            pady=(0, 5))

        separator = ttk.Separator(master,
                                  orient="horizontal")
        separator.grid(
            row=19,
            column=0,
            sticky=N + S + E + W,
            columnspan=4,
            padx=5,
            pady=(0, 10))

        original = Image.open(resources + "transactions.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        transactions = ImageTk.PhotoImage(resized)
        transactions.image = transactions
        transactionsLabel = Label(
            master,
            image=transactions,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        transactionsLabel.grid(
            row=20,
            column=0,
            sticky=N + S + W + E,
            pady=(0, 5))
        transactionsLabel.bind("<Button>", openTransactions)

        original = Image.open(resources + "calculator.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        calculator = ImageTk.PhotoImage(resized)
        calculator.image = calculator
        calculatorLabel = Label(
            master,
            image=calculator,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        calculatorLabel.grid(
            row=20,
            column=1,
            sticky=N + S + W + E,
            padx=(0, 5),
            pady=(0, 5))
        calculatorLabel.bind("<Button>", openCalculator)

        original = Image.open(resources + "stats.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        stats = ImageTk.PhotoImage(resized)
        stats.image = stats
        statsLabel = Label(
            master,
            image=stats,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        statsLabel.grid(
            row=20,
            column=2,
            sticky=N + S + W + E,
            padx=(0, 5),
            pady=(0, 5))
        statsLabel.bind("<Button>", openStats)

        original = Image.open(resources + "settings.png")
        resized = original.resize((58, 58), Image.ANTIALIAS)
        settings = ImageTk.PhotoImage(resized)
        settings.image = settings
        settingsLabel = Label(
            master,
            image=settings,
            background=BACKGROUND_COLOR,
            foreground=FONT_COLOR)
        settingsLabel.grid(
            row=20,
            column=3,
            sticky=N + S + W + E,
            padx=(0, 10),
            pady=(0, 5))
        settingsLabel.bind("<Button>", openSettings)

        root.iconphoto(True, PhotoImage(file=resources + "duco_color.png"))
        start_balance = global_balance
        curr_bal = start_balance
        calculateProfit(start_balance)
        updateBalanceLabel()

        if not disableTray:
            try:
                def quit_window(icon, item):
                    master.destroy()

                def show_window(icon, item):
                    master.after(0, root.deiconify)

                def withdraw_window():
                    image = Image.open(resources + "duco.png")
                    menu = (
                        pystray.MenuItem(get_string("tray_show"), show_window),
                        pystray.MenuItem(get_string("tray_exit"), quit_window))
                    icon = pystray.Icon(
                        get_string("duino_coin_wallet"),
                        image,
                        get_string("duino_coin_wallet"),
                        menu)
                    icon.run()

                t = Thread(target=withdraw_window)
                t.setDaemon(True)
                t.start()
            except:
                pass

        root.mainloop()


with sqlconn(f"{resources}/wallet.db") as con:
    cur = con.cursor()
    cur.execute("SELECT COUNT(username) FROM UserData")
    userdata_count = cur.fetchall()[0][0]
    if userdata_count < 1:
        root = Tk()
        lf = LoginFrame(root)
        root.mainloop()
        cur = con.cursor()
        cur.execute("SELECT COUNT(username) FROM UserData")
        userdata_count = cur.fetchall()[0][0]
    if userdata_count >= 1:
        LoadingWindow()
        with sqlconn(f"{resources}/wallet.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM UserData")
            userdata_query = cur.fetchone()
            username = userdata_query[0]
            passwordEnc = (userdata_query[1]).decode("utf-8")
            password = b64decode(passwordEnc).decode("utf8")
        status.config(text=get_string("preparing_wallet_window"))
        loading.update()
        try:
            # Start duco price updater
            get_duco_price()
            getBalance()
            initRichPresence()
            Thread(target=updateRichPresence).start()
            try:
                # Destroy loading dialog and start the main wallet window
                loading.destroy()
            except:
                pass
            root = Tk()
            my_gui = Wallet(root)
        except ValueError:
            print("ValueError")
            _exit(0)
_exit(0)
