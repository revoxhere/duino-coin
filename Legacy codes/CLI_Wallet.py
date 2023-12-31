#!/usr/bin/env python3
##########################################
# Duino-Coin CLI Wallet (v2.7.1)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2022
##########################################
import configparser
import datetime
import getpass
import json
import os
from os import _exit, execl, mkdir
from os import path
import platform
import socket
import sys
import time
from pathlib import Path
from signal import SIGINT, signal
from base64 import b64decode, b64encode
from platform import system as plsystem
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
from json import load as jsonload

try:
    import requests
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") +
          "Requests is not installed. "
          + "Please install it using: python3 -m pip install requests."
          + "\nExiting in 15s.")
    time.sleep(15)
    os._exit(1)

wrong_passphrase = False
iterations = 100_000
timeout = 30  # Socket timeout
VER = 2.71
RESOURCES_DIR = 'CLI_Wallet_' + str(VER) + '_resources'
use_wrapper = False
WS_URI = "ws://server.duinocoin.com:15808"
config = configparser.ConfigParser()

# Check if the resources folder exists, and makes one if not
if not path.exists(RESOURCES_DIR):
    mkdir(RESOURCES_DIR)

# Check if commands file exists
if not Path(RESOURCES_DIR + "/cli_wallet_commands.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/master/Resources/"
           + "cli_wallet_commands.json")
    r = requests.get(url)
    with open(RESOURCES_DIR + "/cli_wallet_commands.json", "wb") as f:
        f.write(r.content)

# Check if languages file exists
if not Path(RESOURCES_DIR + "/langs.json").is_file():
    url = ("https://raw.githubusercontent.com/"
           + "revoxhere/"
           + "duino-coin/master/Resources/"
           + "CLI_Wallet_langs.json")
    r = requests.get(url)
    with open(RESOURCES_DIR + "/langs.json", "wb") as f:
        f.write(r.content)

# Load language file
with open(RESOURCES_DIR + "/langs.json", "r", encoding="utf8") as lang_file:
    lang_file = jsonload(lang_file)

# OS X invalid locale hack
if plsystem() == "Darwin":
    if getlocale()[0] is None:
        setlocale(LC_ALL, "en_US.UTF-8")

# Check if wallet is configured, if it isn't, autodetect language
try:
    if not Path(RESOURCES_DIR + "/CLIWallet_config.cfg").is_file():
        locale = getdefaultlocale()[0]
        if locale.startswith("nl"):
            lang = "dutch"
        elif locale.startswith("th"):
            lang = "thai"
        elif locale.startswith("sk"):
            lang = "slovak"
        elif locale.startswith("ko"):
            lang = "korean"
        else:
            lang = "english"
    else:
        # Read language variable from configfile
        try:
            config.read(RESOURCES_DIR + "/CLIWallet_config.cfg")
            lang = config["wallet"]["language"]
        except Exception:
            # If it fails, fallback to english
            lang = "english"
except Exception as error:
    lang = "english"


def getString(string_name):
    # Get string form language file
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file["english"]:
        return lang_file["english"][string_name]
    else:
        return "String not found: " + string_name


try:
    from base64 import urlsafe_b64decode as b64d
    from base64 import urlsafe_b64encode as b64e
except ModuleNotFoundError:
    print(getString("base64_not_installed"))
    time.sleep(15)
    _exit(1)

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("cryptography_not_installed"))
    time.sleep(15)
    os._exit(1)

try:
    import secrets
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("secrets_not_installed"))
    time.sleep(15)
    os._exit(1)

try:
    import websocket
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("websocket_not_installed"))
    time.sleep(15)
    os._exit(1)

try:  # Check if colorama is installed
    from colorama import Back, Fore, Style, init
except:
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("colorama_not_installed"))
    time.sleep(15)
    os._exit(1)

try:
    import tronpy
    from tronpy.keys import PrivateKey
    tronpy_installed = True
except:
    tronpy_installed = False
    now = datetime.datetime.now()
    print(now.strftime("%H:%M:%S ") + getString("tronpy_not_installed"))

backend = default_backend()


def title(title):
    if os.name == 'nt':
        os.system(
            "title "
            + title)
    else:
        print(
            '\33]0;'
            + title
            + '\a',
            end='')
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


def print_command(name, desc):
    print(" " + Style.RESET_ALL + Fore.WHITE +
          Style.BRIGHT + name + Style.RESET_ALL + desc)


# Print the command names and description using a json file
def print_commands_norm():
    with open(RESOURCES_DIR + '/cli_wallet_commands.json') as f:
        data = json.load(f)
        for key, value in data.items():
            if key == "wrapper_commands":
                break
            print_command(key, value)


def print_commands_wrapper():
    with open(RESOURCES_DIR + '/cli_wallet_commands.json') as f:
        data = json.load(f)
        for key in data["wrapper_commands"]:
            print_command(key, data["wrapper_commands"][key])


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
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message))))


def password_decrypt(
        token: bytes,
        password: str) -> bytes:
    decoded = b64d(token)
    salt, iterations, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iterations, 'big')
    key = _derive_key(
        password.encode(),
        salt,
        iterations)
    return Fernet(key).decrypt(token)


def handler(signal_received, frame):
    print(Style.RESET_ALL
          + Style.BRIGHT
          + Fore.YELLOW
          + getString("see_you_soon"))
    try:
        wss_conn.send(bytes("CLOSE", encoding="utf8"))
    except:
        pass
    os._exit(0)


signal(SIGINT, handler)  # Enable signal handler


while True:
    print(("Warning: CLI and GUI wallets are being deprecated "
           + "in favor of the Web Wallet. "
           + "This app may not run properly."))
    try:
        wss_conn = websocket.create_connection(WS_URI)
        SERVER_VER = wss_conn.recv().decode()

        jsonapi = requests.get(
            "https://raw.githubusercontent.com/"
            + "revoxhere/"
            + "duco-statistics/master/api.json",
            data=None)
        if jsonapi.status_code == 200:
            content = jsonapi.content.decode()
            contentjson = json.loads(content)
            ducofiat = float(contentjson["Duco price"])
        else:
            ducofiat = 0.0025
        break

    except Exception as e:
        print(e)
        print(Style.RESET_ALL
              + Fore.RED
              + getString("cant_connect_to_server"))
        time.sleep(15)
        os._exit(1)

    except:
        print(Style.RESET_ALL
              + Fore.RED
              + getString("cant_recieve_pool_ip_and_port"))
        time.sleep(15)
        os._exit(1)


def reconnect():
    while True:
        try:
            # Try to connect
            wss_conn = websocket.create_connection(WS_URI)
            wss_conn.settimeout(timeout)
            SERVER_VER = wss_conn.recv().decode().rstrip("\n")

            jsonapi = requests.get(
                "https://raw.githubusercontent.com/"
                + "revoxhere/"
                + "duco-statistics/master/api.json",
                data=None)
            if jsonapi.status_code == 200:
                content = jsonapi.content.decode()
                contentjson = json.loads(content)
                ducofiat = float(contentjson["Duco price"])
            else:
                ducofiat = 0.0025

        except:
            print(Style.RESET_ALL + Fore.RED
                  + getString("cant_connect_to_server"))
            time.sleep(15)
            os.system("python " + __file__)
        else:
            return wss_conn


while True:
    title("Duino-Coin CLI Wallet")
    if not Path(RESOURCES_DIR + "/CLIWallet_config.cfg").is_file():
        # Initial configuration section
        print(Style.RESET_ALL
              + Style.BRIGHT
              + Fore.YELLOW
              + getString("first_run"))
        print(Style.RESET_ALL + getString("select_option"))

        choice = input(getString("choice_input"))
        try:
            int(choice)
        except ValueError:
            print(getString("value_not_numeric"))

        if int(choice) <= 1:
            username = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("enter_username")
                + Style.BRIGHT)

            password = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + getString("enter_password")
                                       + Style.BRIGHT,
                                       stream=None)

            server_timeout = True
            while server_timeout:
                try:
                    wss_conn.send(bytes(
                        "LOGI,"
                        + str(username)
                        + ","
                        + str(password)
                        + str(",placeholder"),
                        encoding="utf8"))
                    loginFeedback = wss_conn.recv().decode()
                    loginFeedback = loginFeedback.rstrip("\n").split(",")
                    server_timeout = False

                    if loginFeedback[0] == "OK":
                        print(Style.RESET_ALL
                              + Fore.YELLOW
                              + getString("login_success"))

                        config['wallet'] = {
                            "username": username,
                            "password": b64encode(
                                bytes(password, encoding="utf8")
                            ).decode("utf-8"),
                            "language": lang}
                        config['wrapper'] = {"use_wrapper": "false"}

                        # Write data to file
                        with open(RESOURCES_DIR
                                  + "/CLIWallet_config.cfg",
                                  "w") as configfile:
                            config.write(configfile)
                    else:
                        print(Style.RESET_ALL
                              + Fore.RED
                              + getString("login_failed")
                              + Style.BRIGHT
                              + str(loginFeedback[1]))
                        time.sleep(15)
                        os._exit(1)
                except socket.timeout:
                    server_timeout = True

        if int(choice) == 2:
            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + getString("agree_requirments")
                  + Fore.WHITE
                  + "https://github.com/revoxhere/duino-coin#terms-of-usage"
                  + Fore.YELLOW)

            username = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("enter_username")
                + Style.BRIGHT)

            password = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + getString("enter_password")
                                       + Style.BRIGHT,
                                       stream=None)

            pconfirm = getpass.getpass(prompt=Style.RESET_ALL
                                       + Fore.YELLOW
                                       + getString("confirm_password")
                                       + Style.BRIGHT,
                                       stream=None)

            email = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + getString("enter_email")
                + Style.BRIGHT)

            if password == pconfirm:
                while True:
                    wss_conn.send(bytes(
                        "REGI,"
                        + str(username)
                        + ","
                        + str(password)
                        + ","
                        + str(email),
                        encoding="utf8"))

                    regiFeedback = wss_conn.recv().decode()
                    regiFeedback = regiFeedback.rstrip("\n").split(",")

                    if regiFeedback[0] == "OK":
                        print(Style.RESET_ALL
                              + Fore.YELLOW
                              + Style.BRIGHT
                              + getString("register_success"))
                        break

                    elif regiFeedback[0] == "NO":
                        print(Style.RESET_ALL
                              + Fore.RED
                              + getString("register_failed")
                              + Style.BRIGHT
                              + str(regiFeedback[1]))
                        time.sleep(15)
                        os._exit(1)

        if int(choice) >= 3:
            os._exit(0)

    else:
        config.read(RESOURCES_DIR + "/CLIWallet_config.cfg")
        if config["wrapper"]["use_wrapper"] == "true" and tronpy_installed:
            use_wrapper = True

            if config["wrapper"]["use_custom_passphrase"] == "true":
                passphrase = getpass.getpass(
                    prompt=Style.RESET_ALL
                    + Fore.YELLOW
                    + getString("decrypt_private_key")
                    + Style.BRIGHT,
                    stream=None)

                try:
                    priv_key = password_decrypt(
                        config["wrapper"]["priv_key"],
                        passphrase).decode("utf8")
                except InvalidToken:
                    print(getString("invalid_passphrase_wrapper"))
                    use_wrapper = False
                    wrong_passphrase = True
            else:
                try:
                    priv_key = password_decrypt(
                        config["wrapper"]["priv_key"],
                        b64decode(
                            config["wallet"]["password"]
                        ).decode("utf8")
                    ).decode("utf8")
                except InvalidToken:
                    print(getString("invalid_passphrase_wrapper"))
                    use_wrapper = False
                    wrong_passphrase = True

            pub_key = config["wrapper"]["pub_key"]

            while True:
                try:
                    tron = tronpy.Tron()
                    # wDUCO contract
                    wduco = tron.get_contract(
                        "TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U"
                    )
                    break
                except:
                    print("Retrying wDUCO contract fetch")
                    pass

            while True:
                try:
                    wbalance = wduco.functions.balanceOf(
                        config["wrapper"]["pub_key"])
                    break
                except:
                    print("Retrying wDUCO balance fetch")

            try:
                trx_balance = tron.get_account_balance(
                    config["wrapper"]["pub_key"]
                )
            except:
                trx_balance = 0

        while True:
            config.read(RESOURCES_DIR + "/CLIWallet_config.cfg")
            username = config["wallet"]["username"]
            password = b64decode(config["wallet"]["password"]).decode("utf8")

            print("Authenticating...")
            wss_conn.send(bytes(
                "LOGI,"
                + str(username)
                + ","
                + str(password)
                + str(",placeholder"),
                encoding="utf8"))

            loginFeedback = wss_conn.recv().decode().rstrip("\n").split(",")
            if loginFeedback[0] == "OK":
                break
            else:
                print(Style.RESET_ALL
                      + Fore.RED
                      + getString("login_failed")
                      + Style.BRIGHT
                      + str(loginFeedback[1]))
                time.sleep(15)
                os._exit(1)

        while True:
            while True:
                try:
                    wss_conn.send(bytes(
                        "BALA",
                        encoding="utf8"))
                except:
                    wss_conn = reconnect()
                try:
                    balance = round(
                        float(wss_conn.recv().decode().rstrip("\n")), 8)
                    balanceusd = round(
                        float(balance) * float(ducofiat), 6)
                    break
                except:
                    pass

            if use_wrapper:
                while True:
                    try:
                        wbalance = float(
                            wduco.functions.balanceOf(pub_key)
                        )/10**6
                        break
                    except:
                        pass

                try:
                    trx_balance = tron.get_account_balance(pub_key)
                except:
                    trx_balance = 0

            print(Style.RESET_ALL
                  + Style.BRIGHT
                  + Fore.YELLOW
                  + getString("cli_wallet_text"))

            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + getString("you_have")
                  + Style.BRIGHT
                  + str(balance)
                  + " DUCO")

            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + getString("which_is_about")
                  + Style.BRIGHT
                  + str(balanceusd)
                  + " USD")

            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + getString("duco_price")
                  + Style.BRIGHT
                  + str(ducofiat)
                  + " USD")

            if use_wrapper:
                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("you_have")
                      + Style.BRIGHT
                      + str(wbalance)
                      + " wDUCO")

                while True:
                    try:
                        pendingbalance = float(
                            wduco.functions.pendingWithdrawals(
                                pub_key,
                                username)
                        )/(10**6)
                        break
                    except:
                        pass

                if pendingbalance > 0:
                    print(Style.RESET_ALL
                          + Fore.YELLOW
                          + getString("pending_unwraps")
                          + Style.BRIGHT
                          + str(pendingbalance)
                          + " wDUCO")

                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("tron_address")
                      + Style.BRIGHT
                      + str(pub_key))

                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("trx_balance")
                      + Style.BRIGHT
                      + str(trx_balance))

            print(Style.RESET_ALL
                  + Fore.YELLOW
                  + getString("help_list_command"))

            command = input(Style.RESET_ALL
                            + Fore.WHITE
                            + getString("duco_console")
                            + Style.BRIGHT)

            if command == "refresh":
                continue

            elif command == "clear":
                if os.name == "nt":
                    os.system("cls")
                    continue
                else:
                    os.system("clear")
                    continue

            elif command == "send":
                recipient = input(Style.RESET_ALL
                                  + Fore.WHITE
                                  + getString("enter_recipients_name")
                                  + Style.BRIGHT)
                try:
                    amount = float(input(
                        Style.RESET_ALL
                        + Fore.WHITE
                        + getString("enter_amount_transfer")
                        + Style.BRIGHT))
                except ValueError:
                    print(getString("amount_numeric"))
                    continue

                wss_conn.send(bytes(
                    "SEND,-,"
                    + str(recipient)
                    + ","
                    + str(amount),
                    encoding="utf8"))
                while True:
                    message = wss_conn.recv().decode().rstrip("\n")
                    print(Style.RESET_ALL
                          + Fore.BLUE
                          + getString("server_message")
                          + Style.BRIGHT
                          + str(message))
                    break

            elif command == "changepass":
                oldpassword = input(
                    Style.RESET_ALL
                    + Fore.WHITE
                    + getString("enter_current_password")
                    + Style.BRIGHT)

                newpassword = input(
                    Style.RESET_ALL
                    + Fore.WHITE
                    + getString("enter_new_password")
                    + Style.BRIGHT)

                wss_conn.send(bytes(
                    "CHGP,"
                    + str(oldpassword)
                    + ","
                    + str(newpassword),
                    encoding="utf8"))

                while True:
                    message = wss_conn.recv().decode().rstrip("\n")
                    print(Style.RESET_ALL
                          + Fore.BLUE
                          + getString("server_message")
                          + Style.BRIGHT
                          + str(message))
                    break

            elif command == "exit":
                print(Style.RESET_ALL
                      + Style.BRIGHT
                      + Fore.YELLOW
                      + getString("sigint_detected")
                      + Style.NORMAL
                      + getString("see_you_soon")
                      + Style.RESET_ALL)
                try:
                    wss_conn.send(bytes("CLOSE", encoding="utf8"))
                except:
                    pass
                os._exit(0)

            elif command == "wrapperconf":  # wrapper config
                config.read(RESOURCES_DIR + "/CLIWallet_config.cfg")
                if (not config["wrapper"]["use_wrapper"] == "true"
                        and tronpy_installed):
                    print(Style.RESET_ALL
                          + Fore.WHITE
                          + getString("select_option"))
                    try:
                        choice = int(
                            input(getString("choice_input_wrapper")))

                        if choice <= 1:
                            priv_key = str(PrivateKey.random())
                            pub_key = PrivateKey(bytes.fromhex(
                                priv_key)).public_key.to_base58check_address()
                            print(getString("how_encrypt_private_key"))

                            incorrect_value = True
                            while incorrect_value:
                                try:
                                    encryption_choice = int(
                                        input(getString("encryption_choice")))
                                    incorrect_value = False
                                except ValueError:
                                    print(getString("value_not_numeric"))
                                    incorrect_value = True

                                if encryption_choice <= 1:
                                    config['wrapper'] = {
                                        "use_wrapper": "true",
                                        "priv_key": str(password_encrypt(
                                            priv_key.encode(),
                                            password).decode()),
                                        "pub_key": pub_key,
                                        "use_custom_passphrase": "false"}

                                    # Write data to file
                                    with open(RESOURCES_DIR
                                              + "/CLIWallet_config.cfg",
                                              "w") as configfile:
                                        config.write(configfile)
                                        print(getString("success"))

                                elif encryption_choice >= 2:
                                    passphrase = input(
                                        getString("encrypt_private_key"))
                                    config['wrapper'] = {
                                        "use_wrapper": "true",
                                        "priv_key": str(password_encrypt(
                                            priv_key.encode(),
                                            passphrase).decode()),
                                        "pub_key": pub_key,
                                        "use_custom_passphrase": "true"}

                                    # Write data to file
                                    with open(RESOURCES_DIR
                                              + "/CLIWallet_config.cfg",
                                              "w") as configfile:
                                        config.write(configfile)
                                        print(getString("success"))

                                print("Restart the wallet to use the wrapper")

                        elif choice == 2:
                            priv_key = input(getString("input_private_key"))
                            try:
                                pub_key = PrivateKey(
                                    bytes.fromhex(
                                        priv_key)
                                ).public_key.to_base58check_address()
                                print(getString("how_encrypt_private_key"))

                                incorrect_value = True
                                while incorrect_value:
                                    try:
                                        encryption_choice = int(
                                            input(
                                                getString("encryption_choice")
                                            )
                                        )
                                        incorrect_value = False
                                    except ValueError:
                                        print(getString("value_not_numeric"))
                                        incorrect_value = True

                                    if encryption_choice <= 1:
                                        config['wrapper'] = {
                                            "use_wrapper": "true",
                                            "priv_key": str(password_encrypt(
                                                priv_key.encode(),
                                                password).decode()),
                                            "pub_key": pub_key,
                                            "use_custom_passphrase": "false"}

                                        # Write data to file
                                        with open(RESOURCES_DIR
                                                  + "/CLIWallet_config.cfg",
                                                  "w") as configfile:
                                            config.write(configfile)
                                            print(getString("success"))

                                    elif encryption_choice >= 2:
                                        passphrase = input(
                                            getString("encrypt_private_key"))
                                        config['wrapper'] = {
                                            "use_wrapper": "true",
                                            "priv_key": str(password_encrypt(
                                                priv_key.encode(),
                                                passphrase).decode()),
                                            "pub_key": pub_key,
                                            "use_custom_passphrase": "true"}

                                        # Write data to file
                                        with open(RESOURCES_DIR
                                                  + "/CLIWallet_config.cfg",
                                                  "w") as configfile:
                                            config.write(configfile)
                                            print(getString("success"))
                            except ValueError:
                                print(getString("incorrect_key"))
                        else:
                            print(getString("cancelled"))

                    except ValueError:
                        print(Style.RESET_ALL
                              + Fore.WHITE
                              + getString("incorrect_value")
                              + Style.BRIGHT)

                elif not tronpy_installed:
                    print(now.strftime(
                        "%H:%M:%S ")
                        + getString("tronpy_not_installed_2"))

            elif command == "wrap":
                if use_wrapper:
                    try:
                        amount = float(input(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + getString("amount_to_wrap")
                            + Style.BRIGHT))
                    except ValueError:
                        print(getString("no_amount_numeric"))
                        continue

                    try:
                        wss_conn.send(bytes("BALA", encoding="utf8"))
                        balance = round(
                            float(wss_conn.recv().decode().rstrip("\n")), 8)
                    except:
                        wss_conn = reconnect()
                    if float(amount) >= 10 and float(amount) <= balance:
                        tron_address = input(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + getString("enter_tron_address_or_local")
                            + Style.BRIGHT)
                        if tron_address == "":
                            tron_address = pub_key

                        wss_conn.send(bytes(
                            "WRAP,"
                            + str(amount)
                            + ","
                            + str(tron_address)
                            + str(",placeholder"),
                            encoding='utf8'))

                    elif float(amount) < 10 and not float(amount) > balance:
                        print(getString("error_min_10_duco"))
                    else:
                        print(getString("error_unsufficient_balance"))
                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "unwrap":
                if use_wrapper:
                    pendingvalues = wduco.functions.pendingWithdrawals(
                        pub_key, username
                    )
                    # Transaction wasn't initiated
                    # but variable should be declared
                    txn_success = False
                    try:
                        amount = float(
                            input(Style.RESET_ALL
                                  + Fore.WHITE
                                  + getString("enter_amount_unwrap")
                                  + Style.BRIGHT))
                    except ValueError:
                        print(getString("value_not_numeric"))
                        continue
                    if int(float(amount)*10**6) >= pendingvalues:
                        toInit = int(float(amount)*10**6)-pendingvalues
                    else:
                        toInit = amount*10**6
                    if toInit > 0:
                        txn = wduco.functions.initiateWithdraw(
                            username, toInit
                        ).with_owner(
                            pub_key
                        ).fee_limit(
                            5_000_000
                        ).build().sign(
                            PrivateKey(
                                bytes.fromhex(priv_key)
                            )
                        )
                        print(getString("initiating_unwrap"), txn.txid)
                        txn = txn.broadcast()
                        txnfeedback = txn.result()
                        if txnfeedback:
                            txn_success = True
                        else:
                            txn_success = False

                    if amount <= pendingvalues:
                        print(getString("amount_over_pending_values"))

                    if txn_success or amount <= pendingvalues:
                        wss_conn.send(bytes(
                            "UNWRAP,"
                            + str(amount)
                            + ","
                            + str(pub_key),
                            encoding='utf8'))
                    else:
                        print(getString("error_initiating_unwrap"))

                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "cancelunwraps":
                if use_wrapper:
                    txn = wduco.functions.cancelWithdrawals(
                        pub_key, username
                    ).with_owner(
                        pub_key
                    ).fee_limit(
                        5_000_000
                    ).build().sign(
                        PrivateKey(
                            bytes.fromhex(priv_key)
                        )
                    )
                    print(getString("transaction_send_txid"), txn.txid)
                    txn = txn.broadcast()
                    if txn.result():
                        print(getString("success"))
                    else:
                        print(getString("error_not_enough_energy_or_trx"))
                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "finishunwraps":
                if use_wrapper:
                    pendingvalues = float(
                        wduco.functions.pendingWithdrawals(
                            pub_key,
                            username))/(10**6)
                    wss_conn.send(bytes(
                        "UNWRAP,"
                        + str(pendingvalues)
                        + ","
                        + str(pub_key)
                        + str(",placeholder"),
                        encoding='utf8'))
                    print(getString("finished_unwrapping"),
                          str(pendingvalues), "DUCO")
                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "exportwrapkey":
                if use_wrapper:
                    confirmation = input(
                        getString("confirm_export_private_key"))
                    if confirmation == "YES":
                        print(getString("private_key"), priv_key)
                    else:
                        print(getString("cancelled_invalid_confirmation"))
                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "wsend":
                if use_wrapper:
                    recipient = input(
                        Style.RESET_ALL
                        + Fore.WHITE
                        + getString("enter_tron_recipients_name")
                        + Style.BRIGHT)
                    try:
                        amount = float(input(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + getString("enter_amount_transfer")
                            + Style.BRIGHT))
                    except ValueError:
                        print(getString("amount_numeric"))
                        continue
                    wbalance = float(wduco.functions.balanceOf(pub_key))/10**6
                    if float(amount) <= wbalance:
                        txn = wduco.functions.transfer(
                            recipient,
                            int(float(amount)*10**6)
                        ).with_owner(
                            pub_key
                        ).fee_limit(
                            5_000_000
                        ).build().sign(
                            PrivateKey(
                                bytes.fromhex(priv_key)
                            )
                        )
                        txn = txn.broadcast()
                        print(getString("tron_transaction_submitted"),
                              txn.txid)
                        trontxresult = txn.wait()
                        if trontxresult:
                            print(getString("tron_successful_transaction"))
                        else:
                            print(getString("tron_error_transaction"))
                elif wrong_passphrase:
                    print(getString("error_wrong_passphrase"))
                else:
                    print(getString("error_configure_wrapperconf"))

            elif command == "about":
                print(Style.RESET_ALL
                      + Fore.WHITE
                      + getString("about_1"))
                print(Style.RESET_ALL
                      + Fore.WHITE
                      + getString("about_2")
                      + str(VER))
                print(Style.RESET_ALL
                      + Fore.WHITE
                      + getString("about_3"))
                print(Style.RESET_ALL
                      + Fore.WHITE
                      + Style.BRIGHT
                      + "https://duinocoin.com")
                print(Style.RESET_ALL
                      + Fore.WHITE
                      + getString("about_4")
                      + Style.BRIGHT
                      + str(SERVER_VER)
                      + Style.RESET_ALL)
                if float(SERVER_VER) > VER:
                    print(Style.RESET_ALL
                          + Fore.YELLOW
                          + getString("about_5")
                          + Fore.WHITE
                          + Style.BRIGHT
                          + SERVER_VER
                          + Fore.YELLOW
                          + Style.RESET_ALL
                          + getString("about_6")
                          + Style.BRIGHT
                          + Fore.WHITE
                          + str(VER)
                          + Style.RESET_ALL
                          + Fore.YELLOW
                          + getString("about_7"))
                else:
                    print(Style.RESET_ALL
                          + Fore.WHITE
                          + getString("about_8"))

            elif command == "logout":
                os.remove(RESOURCES_DIR + "/CLIWallet_config.cfg")
                os.system("python " + __file__)

            elif command == "donate":
                print(Style.RESET_ALL
                      + Fore.BLUE
                      + Style.BRIGHT
                      + getString("donate_1"))
                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("donate_2")
                      + Style.RESET_ALL
                      + Fore.WHITE
                      + Style.BRIGHT
                      + "TY5wfM6JsYKEEMfQR3RBQBPKfetTpf7nyM"
                      + Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("donate_3"))
                print("Duino-Coin: "
                      + Style.RESET_ALL
                      + Fore.WHITE
                      + Style.BRIGHT
                      + "revox"
                      + Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("donate_4"))
                print("Duino-Coin: "
                      + Style.RESET_ALL
                      + Fore.WHITE
                      + Style.BRIGHT
                      + "Yanis"
                      + Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("donate_5"))

            else:
                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("duco_commands"))
                print_commands_norm()

                print(Style.RESET_ALL
                      + Fore.YELLOW
                      + getString("wrapper_commands"))
                print_commands_wrapper()
