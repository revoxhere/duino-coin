#!/usr/bin/env python3
##########################################
# Duino-Coin Tkinter GUI Wallet (v2.52)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
import sys
from base64 import b64decode, b64encode
from configparser import ConfigParser
from datetime import datetime
from json import loads
from json import loads as jsonloads
from locale import getdefaultlocale
from os import _exit, execl, mkdir
from os import name as osname
from os import path, system
from pathlib import Path
from socket import socket
from sqlite3 import connect as sqlconn
import subprocess
from threading import Thread, Timer
from time import sleep, time
from tkinter import (BOTH, END, LEFT, RIGHT, Button, Checkbutton, E, Entry,
                     Frame, IntVar, Label, Listbox, N, PhotoImage, S,
                     Scrollbar, StringVar, Tk, Toplevel, W, messagebox, ttk)
from tkinter.font import Font
from urllib.request import urlopen, urlretrieve
from webbrowser import open_new_tab

from requests import get

# Version number
VERSION = 2.52
# Colors
BACKGROUND_COLOR = "#121212"
FONT_COLOR = "#fffdee"
FOREGROUND_COLOR = "#ff9f43"
FOREGROUND_COLOR_SECONDARY = "#fdcb6e"
# Minimum transaction amount to be saved
MIN_TRANSACTION_VALUE = 0.00000000001
# Minimum transaction amount to show a notification
MIN_TRANSACTION_VALUE_NOTIFY = 0.5
# Resources folder location
resources = "Wallet_" + str(VERSION) + "_resources/"
ENCRYPTION_ITERATIONS = 100_000
config = ConfigParser()
wrong_passphrase = False
global_balance = 0
oldbalance = 0
balance = 0
unpaid_balance = 0
profitCheck = 0
curr_bal = 0
WS_URI = "ws://server.duinocoin.com:15808"


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    execl(sys.executable, sys.executable, *sys.argv)


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
        except Exception:
            duco_fiat_value = 0.003
    else:
        duco_fiat_value = 0.003
    Timer(30, get_duco_price).start()


def title(title):
    if osname == "nt":
        system("title " + title)
    else:
        print("\33]0;" + title + "\a", end="")
        sys.stdout.flush()


def _derive_key(
        password: bytes,
        salt: bytes,
        iterations: int = ENCRYPTION_ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ENCRYPTION_ITERATIONS,
        backend=backend)
    return b64e(kdf.derive(password))


def password_encrypt(
        message: bytes,
        password: str,
        iterations: int = ENCRYPTION_ITERATIONS) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(
        password.encode(),
        salt,
        ENCRYPTION_ITERATIONS)
    return b64e(
        b"%b%b%b" % (
            salt,
            ENCRYPTION_ITERATIONS.to_bytes(4, "big"),
            b64d(Fernet(key).encrypt(message))))


def password_decrypt(
        token: bytes,
        password: str) -> bytes:
    decoded = b64d(token)
    salt, ENCRYPTION_ITERATIONS, token = decoded[:16], decoded[16:20], b64e(
        decoded[20:])
    ENCRYPTION_ITERATIONS = int.from_bytes(ENCRYPTION_ITERATIONS, "big")
    key = _derive_key(
        password.encode(),
        salt,
        ENCRYPTION_ITERATIONS)
    return Fernet(key).decrypt(token)


def get_string(string_name):
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name


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


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        messagebox.showerror(title="Warning",
                             message=("CLI and GUI wallets are being deprecated in favor of the Web Wallet. "
                                      + "This app may not run properly."))

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
            pady=(5, 1))

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
        self.master.bind(
            "<Return>",
            self._login_btn_clicked_bind)
        self.pack()

    def _login_btn_clicked_bind(self, event):
        self._login_btn_clicked()

    def _login_btn_clicked(self):
        global username, password
        username = self.entry_username.get()
        password = self.entry_password.get()

        if username and password:
            soc = websocket.create_connection(WS_URI)
            soc.recv().decode()
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password),
                encoding="utf8"))
            response = soc.recv().decode()
            response = response.rstrip("\n").split(",")

            if response[0] == "OK":
                passwordEnc = b64encode(bytes(password, encoding="utf8"))
                with sqlconn(resources + "wallet.db") as con:
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
                soc = websocket.create_connection(WS_URI)
                soc.recv().decode()
                soc.send(
                    bytes(
                        "REGI,"
                        + str(usernameS)
                        + ","
                        + str(passwordS)
                        + ","
                        + str(emailS),
                        encoding="utf8"))
                response = soc.recv().decode().rstrip("\n")
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
        tos_warning = "\n".join(l for line in tos_warning.splitlines()
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


def loading_window():
    global loading, status
    loading = Tk()
    loading.resizable(False, False)
    loading.configure(background=BACKGROUND_COLOR)
    loading.title(get_string("loading"))
    try:
        loading.iconphoto(True,
                          PhotoImage(file=resources + "duco_color.png"))
    except Exception:
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


def transactions_window(handler):
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
        listbox.insert(END, gtxl[i]["Sender"] + " to " + gtxl[i]
                       ["Recipient"] + ": " + str(gtxl[i]["Amount"]) + " DUCO")

    def get_selection(event):
        try:
            selection = listbox.curselection()[0]
            openTransaction(gtxl[str(selection)]["Hash"])
        except IndexError:
            pass

    listbox.bind("<Button-1>", get_selection)
    listbox.config(yscrollcommand=scrollbar.set, font=TEXT_FONT)
    scrollbar.config(command=listbox.yview)


def currency_converter_calc():
    fromcurrency = fromCurrencyInput.get(fromCurrencyInput.curselection())
    tocurrency = toCurrencyInput.get(toCurrencyInput.curselection())
    amount = amountInput.get()

    # TODO
    value = duco_fiat_value * float(amount)

    result = get_string("result") + ": " + str(round(value, 6))
    conversionresulttext.set(str(result))
    calculatorWindow.update()


def currency_converter_window(handler):
    global conversionresulttext
    global fromCurrencyInput
    global toCurrencyInput
    global amountInput
    global calculatorWindow

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
    fromCurrencyInput.insert(0, "DUCO")

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

    fromCurrencyInput.select_set(0)
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
    toCurrencyInput.insert(0, "USD")

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
        command=currency_converter_calc,
    ).grid(row=3,
           columnspan=2,
           column=2,
           sticky=N + S + W + E,
           pady=(5, 0),
           padx=5)

    conversionresulttext = StringVar(calculatorWindow)
    conversionresulttext.set(get_string("result") + ": 0.0")
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


def statistics_window(handler):
    statsApi = get(
        "https://server.duinocoin.com"
        + "/api.json",
        data=None)
    if statsApi.status_code == 200:  # Check for reponse
        statsApi = statsApi.json()

    miner_api = get(
        "https://server.duinocoin.com"
        + "/miners.json",
        data=None)
    if miner_api.status_code == 200:  # Check for reponse
        miner_api = miner_api.json()

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

    for threadid in miner_api:
        if username in miner_api[threadid]["User"]:
            rigId = miner_api[threadid]["Identifier"]
            if rigId == "None":
                rigId = ""
            else:
                rigId += ": "
            software = miner_api[threadid]["Software"]
            hashrate = str(round(miner_api[threadid]["Hashrate"], 2))
            totalHashrate += float(hashrate)
            difficulty = str(miner_api[threadid]["Diff"])
            shares = (
                str(miner_api[threadid]["Accepted"])
                + "/"
                + str(
                    miner_api[threadid]["Accepted"]
                    + miner_api[threadid]["Rejected"]))

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
        Active_workers_listbox.insert(
            i, get_string("statistics_miner_warning"))

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
        text=get_string("your_miners") + " - " + totalHashrateString,
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

    num = 0
    for i in statsApi["Top 10 richest miners"]:
        Top_10_listbox.insert(num, i)
        num += 1

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
        text=get_string("difficulty")
        + ": "
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
        text=get_string("mined_blocks")
        + ": "
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
        text=get_string("network_hashrate")
        + ": "
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
        text=get_string("active_miners")
        + ": "
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
        text="1 DUCO "
        + get_string("estimated_price")
        + ": $"
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
        text=get_string("registered_users")
        + ": "
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
        text=get_string("mined_duco")
        + ": "
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


def wrapper_window(handler):
    def Wrap():
        amount = amountWrap.get()
        print("Got amount:", amount)
        print("pub key:", pub_key)
        soc = websocket.create_connection(WS_URI)
        soc.recv().decode()
        try:
            float(amount)
        except Exception:
            pass
        else:
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password),
                encoding="utf8"))
            _ = soc.recv().decode()
            soc.send(
                bytes(
                    "WRAP,"
                    + str(amount)
                    + ","
                    + str(pub_key)
                    + str(",placeholder"),
                    encoding="utf8"))
            soc.close()
            sleep(2)
            wrapperWindow.quit()

    try:
        pubkeyfile = open(str(resources + "DUCOPubKey.pub"), "r")
    except Exception:
        messagebox.showerror(
            title=get_string("wrapper_error_title"),
            message=get_string("wrapper_error"))
    else:
        if TRONPY_ENABLED:
            pub_key = pubkeyfile.read()
            pubkeyfile.close()

            wrapperWindow = Toplevel()
            wrapperWindow.resizable(False, False)
            wrapperWindow.title(get_string("wrapper_title"))
            wrapperWindow.transient([root])

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


def unwrapper_window(handler):
    def UnWrap():
        pubkeyfile = open(str(resources + "DUCOPubKey.pub"), "r")
        pub_key = pubkeyfile.read()
        pubkeyfile.close()

        passphrase = passphraseEntry.get()
        privkeyfile = open(str(resources + "DUCOPrivKey.encrypt"), "r")
        privKeyEnc = privkeyfile.read()
        privkeyfile.close()

        try:
            priv_key = password_decrypt(privKeyEnc, passphrase).decode()
            use_wrapper = True
        except InvalidToken:
            print(get_string("invalid_passphrase"))
            use_wrapper = False

        amount = amountUnWrap.get()
        print("Got amount:", amount)
        soc = websocket.create_connection(WS_URI)
        soc.recv().decode()
        try:
            float(amount)
        except Exception:
            pass
        else:
            soc.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password), encoding="utf8"))
            _ = soc.recv().decode()
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
                                + str(pub_key)
                                + str(",placeholder"),
                                encoding="utf8"))

                soc.close()
                sleep(2)
                unWrapperWindow.quit()

    try:
        pubkeyfile = open(str(resources + "DUCOPubKey.pub"), "r")
        pubkeyfile.read()
        pubkeyfile.close()
    except Exception:
        messagebox.showerror(
            title=get_string("wrapper_error_title"),
            message=get_string("wrapper_error"))
    else:
        if TRONPY_ENABLED:
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


def settings_window(handler):
    def _wrapperconf():
        if TRONPY_ENABLED:
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
                    except Exception:
                        pass
                    else:
                        print("Saving data")

                        privkeyfile = open(
                            str(resources + "DUCOPrivKey.encrypt"), "w")
                        privkeyfile.write(
                            str(password_encrypt(
                                priv_key.encode(), passphrase
                            ).decode()))
                        privkeyfile.close()

                        pubkeyfile = open(
                            str(resources + "DUCOPubKey.pub"), "w")
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
            with sqlconn(resources + "wallet.db") as con:
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
        with sqlconn(resources + "wallet.db") as con:
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
                        soc = websocket.create_connection(WS_URI)
                        soc.recv().decode()
                        soc.send(
                            bytes(
                                "LOGI,"
                                + str(username)
                                + ","
                                + str(password), encoding="utf8"))
                        soc.recv().decode()
                        soc.send(
                            bytes(
                                "CHGP,"
                                + str(oldpasswordS)
                                + ","
                                + str(newpasswordS),
                                encoding="utf8"))
                        response = soc.recv().decode().rstrip("\n").split(",")
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
                                        resources + "wallet.db"
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
        text=get_string("logged_in_as")
        + ": "
        + str(username),
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
        text=get_string("wallet_version")
        + ": "
        + str(VERSION),
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


def get_balance():
    global oldbalance
    global balance
    global unpaid_balance
    global global_balance
    global gtxl
    try:
        soc = websocket.create_connection(WS_URI)
        soc.recv().decode()
        soc.send(bytes(
            "LOGI,"
            + str(username)
            + ","
            + str(password), encoding="utf8"))
        _ = soc.recv().decode()
        soc.send(bytes(
            "BALA",
            encoding="utf8"))
        oldbalance = balance
        balance = float(soc.recv().decode().rstrip("\n"))
        global_balance = round(float(balance), 8)

        try:
            gtxl = {}
            soc.send(bytes(
                "GTXL," + str(username) + ",7",
                encoding="utf8"))
            gtxl = str(soc.recv().decode().rstrip(
                "\n").replace("\'", "\""))
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
                        notification.icon = resources + "duco_color.png"
                        notification.send(block=False)
                    with sqlconn(resources + "wallet.db") as con:
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
    Timer(3, get_balance).start()


def get_wbalance():
    if TRONPY_ENABLED:
        try:
            pubkeyfile = open(str(resources + "DUCOPubKey.pub"), "r")
            pub_key = pubkeyfile.read()
            pubkeyfile.close()
            wBalance = float(wduco.functions.balanceOf(pub_key)) / (10 ** 6)
            return wBalance
        except Exception:
            return 0.0
    else:
        return 0.0


def update_balance_labels():
    global profit_array, profitCheck
    try:
        balancetext.set(str(round(global_balance, 7)) + " ᕲ")
        wbalancetext.set(str(get_wbalance()) + " wᕲ")
        balanceusdtext.set(
            "$" + str(round(global_balance * duco_fiat_value, 4)))

        with sqlconn(resources + "wallet.db") as con:
            cur = con.cursor()
            cur.execute("SELECT rowid,* FROM Transactions ORDER BY rowid DESC")
            Transactions = cur.fetchall()
        transactionstext_format = ""
        for i, row in enumerate(Transactions, start=1):
            transactionstext_format += str(row[1]) + \
                " " + str(row[2]) + " DUCO\n"
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
    except Exception:
        _exit(0)
    Timer(1, update_balance_labels).start()


def profit_calculator(start_bal):
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
    except Exception:
        _exit(0)
    Timer(10, profit_calculator, [start_bal]).start()


def send_funds_protocol(handler):
    recipientStr = recipient.get()
    amountStr = amount.get()

    MsgBox = messagebox.askquestion(
        get_string("warning"),
        get_string("send_funds_warning")
        + " "
        + str(amountStr)
        + " DUCO "
        + get_string("send_funds_to")
        + " "
        + str(recipientStr)
        + "?",
        icon="warning",)
    if MsgBox == "yes":
        soc = websocket.create_connection(WS_URI)
        soc.recv().decode()

        soc.send(bytes(
            "LOGI,"
            + str(username)
            + ","
            + str(password),
            encoding="utf8"))
        response = soc.recv().decode()
        soc.send(
            bytes(
                "SEND,"
                + "-"
                + ","
                + str(recipientStr)
                + ","
                + str(amountStr),
                encoding="utf8"))
        response = soc.recv().decode().rstrip("\n").split(",")
        soc.close()

        if "OK" in str(response[0]):
            MsgBox = messagebox.showinfo(response[0],
                                         response[1]
                                         + "\nTXID:"
                                         + response[2])
        else:
            MsgBox = messagebox.showwarning(response[0], response[1])
    root.update()


def init_rich_presence():
    global RPC
    try:
        RPC = Presence(806985845320056884)
        RPC.connect()
    except Exception:  # Discord not launched
        pass


def update_rich_presence():
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
        except Exception:  # Discord not launched
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
        except Exception:
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
            text=get_string("uppercase_duino_coin_wallet")
            + ": "
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
        if TRONPY_ENABLED:
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
        sendLabel.bind("<Button-1>", send_funds_protocol)

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
        wrapLabel.bind("<Button-1>", wrapper_window)

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
        wrapLabel.bind("<Button-1>", unwrapper_window)

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
        transactionsLabel.bind("<Button>", transactions_window)

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
        calculatorLabel.bind("<Button>", currency_converter_window)

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
        statsLabel.bind("<Button>", statistics_window)

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
        settingsLabel.bind("<Button>", settings_window)

        root.iconphoto(True, PhotoImage(file=resources + "duco_color.png"))
        start_balance = global_balance
        curr_bal = start_balance
        profit_calculator(start_balance)
        update_balance_labels()

        root.mainloop()


try:
    from pypresence import Presence
except ModuleNotFoundError:
    print("Pypresence is not installed."
          + "Wallet will try to install it. "
          + "If it fails, please manually install \"pypresence\".")
    install("pypresence")

try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    print("Pillow is not installed. "
          + "Wallet will try to install it. "
          + "If it fails, please manually install \"Pillow\".")
    install("Pillow")

try:
    from notifypy import Notify
except ModuleNotFoundError:
    print("Notify-py is not installed. "
          + "Continuing without notification system.")
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
    print("Cryptography is not installed. "
          + "Please manually install \"cryptography\"."
          + "\nExiting in 15s.")
    sleep(15)
    _exit(1)

try:
    import secrets
except ModuleNotFoundError:
    print("Secrets is not installed. "
          + "Please manually install \"secrets\"."
          + "\nExiting in 15s.")
    sleep(15)
    _exit(1)

try:
    from base64 import urlsafe_b64decode as b64d
    from base64 import urlsafe_b64encode as b64e
except ModuleNotFoundError:
    print("Base64 is not installed. "
          + "Please manually install \"base64\""
          + "\nExiting in 15s.")
    sleep(15)
    _exit(1)

try:
    import websocket
except ModuleNotFoundError:
    print("websocket-client is not installed. "
          + "Wallet will try to install it. "
          + "If it fails, please manually install \"websocket-client\".")
    install("websocket-client")

try:
    import tronpy
    from tronpy.keys import PrivateKey
    TRONPY_ENABLED = True
except ModuleNotFoundError:
    TRONPY_ENABLED = False
    print("Tronpy is not installed. "
          + "Please manually install \"tronpy\" "
          + "if you intend on using wDUCO wrapper.")
else:
    try:
        tron = tronpy.Tron()
        wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U")
    except:
        TRONPY_ENABLED = False
        print("Tron-side error, disabling wrapper for this session")

if not path.exists(resources):
    mkdir(resources)

with sqlconn(resources + "/wallet.db") as con:
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
with open(resources + "langs.json", "r", encoding="utf-8") as lang_file:
    lang_file = jsonloads(lang_file.read())
try:
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
    elif locale.startswith("it"):
        lang = "italian"
    elif locale.startswith("zh"):
        lang = "chinese_simplified"
    elif locale.startswith("th"):
        lang = "thai"
    else:
        lang = "english"
except IndexError:
    lang = "english"

if __name__ == "__main__":
    with sqlconn(resources + "wallet.db") as con:
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
            loading_window()
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
                get_balance()
                init_rich_presence()
                Thread(target=update_rich_presence).start()
                try:
                    # Destroy loading dialog and start the main wallet window
                    loading.destroy()
                except Exception:
                    pass
                root = Tk()
                my_gui = Wallet(root)
            except Exception as e:
                print(e)
                _exit(0)
