#!/usr/bin/env python3
"""
Duino-Coin wDUCO API © MIT licensed
developed by yanis (@ygboucherk) 
https://duinocoin.com
https://github.com/revoxhere/duino-coin-rest-api
Duino-Coin Team & Community 2019-2021
"""

import sqlite3
import traceback
import datetime
from hashlib import sha1
from Server import DATABASE as database
from Server import DB_TIMEOUT as database_timeout
from Server import CONFIG_TRANSACTIONS as config_db_transactions
from Server import WRAPPER_KEY as wrapper_private_key
from Server import admin_print

use_wrapper = True
wrapper_permission = False
wrap_enabled = True
unwrap_enabled = True

if use_wrapper:
    import tronpy  # python3 -m pip install tronpy
    from tronpy.keys import PrivateKey, PublicKey
    # Wrapper public key
    wrapper_public_key = PrivateKey(bytes.fromhex(
        wrapper_private_key)).public_key.to_base58check_address()
    tron = tronpy.Tron(network="mainnet")
    # wDUCO contract
    wduco = tron.get_contract("TWYaXdxA12JywrUdou3PFD1fvx2PWjqK9U")
    wrapper_permission = wduco.functions.checkWrapperStatus(wrapper_public_key)


def unwraptx(duco_username, recipient, amount, private_key, public_key):
    # wDUCO unwrapper
    txn = wduco.functions.initiateWithdraw(
        duco_username,
        recipient,
        int(float(amount)*10**6)
    ).with_owner(
        PublicKey(PrivateKey(
            bytes.fromhex(wrapper_public_key)))
    ).fee_limit(5_000_000).build().sign(
        PrivateKey(
            bytes.fromhex(wrapper_private_key)))
    feedback = txn.broadcast().wait()
    return feedback


def confirmunwraptx(duco_username, recipient, amount):
    # wDUCO unwrap confirmer
    txn = wduco.functions.confirmWithdraw(
        duco_username,
        recipient,
        int(float(amount)*10**6)
    ).with_owner(
        wrapper_public_key
    ).fee_limit(5_000_000
                ).build().sign(
        PrivateKey(
            bytes.fromhex(wrapper_private_key)))
    txn = txn.broadcast()
    admin_print("Sent confirm tx to tron network by " + duco_username)
    return feedback


def protocol_wrap_wduco(username, tron_address, amount):
    if use_wrapper and wrapper_permission and wrap_enabled:
        try:
            with sqlite3.connect(database) as conn:
                datab = conn.cursor()
                datab.execute(
                    """SELECT *
                    FROM Users
                    WHERE username = ?""",
                    (username,))
                balance = float(datab.fetchone()[3])
        except Exception:
            return "NO,Can't check balance"

        if float(balance) <= float(amount) or float(amount) <= 0:
            return "NO,Incorrect amount"

        elif float(balance) >= float(amount) and float(amount) > 0:
            balancebackup = balance
            # admin_print("Backed up balance: " + str(balancebackup))
            try:
                balance -= float(amount)
                while True:
                    try:
                        with sqlite3.connect(database,
                                             timeout=database_timeout) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                """UPDATE Users
                                set balance = ?
                                where username = ?""",
                                (balance, username))
                            conn.commit()
                        break
                    except:
                        # print("Retrying")
                        pass
                # print("DUCO balance sent to DB, sending tron transaction")

                # print("Tron wrapper called")
                try:
                    txn = wduco.functions.wrap(
                        tron_address,
                        int(float(amount)*10**6)
                    ).with_owner(wrapper_public_key
                                 ).fee_limit(20_000_000
                                             ).build().sign(
                        PrivateKey(
                            bytes.fromhex(wrapper_private_key)))

                    admin_print("Wrap TXID: " + txn.txid)
                    txn = txn.broadcast()

                    admin_print("Sent wrap tx to TRON network")
                    txnsucceeded = txn.wait()
                    if txnsucceeded:
                        trontxfeedback = txn.result()
                    else:
                        trontxfeedback = False
                except:
                    trontxfeedback = False

                if trontxfeedback:
                    admin_print("Successful wrap")
                    now = datetime.datetime.now()
                    lastBlockHash = sha1(bytes(
                        str(tron_address)+str(now), encoding='utf8')
                    ).hexdigest()
                    try:
                        with sqlite3.connect(config_db_transactions,
                                             timeout=database_timeout
                                             ) as tranconn:
                            datab = tranconn.cursor()

                            formatteddatetime = now.strftime(
                                "%d/%m/%Y %H:%M:%S")
                            memo = str(tron_address)
                            datab.execute("""INSERT INTO 
                                Transactions(
                                timestamp, 
                                username, 
                                recipient, 
                                amount, 
                                hash,
                                memo) 
                                VALUES(?, ?, ?, ?, ?, ?)""",
                                          (formatteddatetime,
                                           username,
                                           "wDUCO",
                                              amount,
                                              lastBlockHash,
                                              memo))
                            tranconn.commit()
                    except Exception as e:
                        print(e)
                    return "OK,Sucessfull wrapping,"+str(lastBlockHash)
                else:
                    with sqlite3.connect(database,
                                         timeout=database_timeout
                                         ) as tranconn:
                        datab = tranconn.cursor()
                        datab.execute(
                            """UPDATE Users 
                            set balance = ? 
                            where username = ?""",
                            (balancebackup, username))
                        tranconn.commit()
                    #print("Error with Tron blockchain")
                    return "NO,Wrapper was unable to broadcast the transaction. Try again later"
            except Exception as e:
                with sqlite3.connect(database,
                                     timeout=database_timeout
                                     ) as tranconn:
                    datab = tranconn.cursor()
                    datab.execute(
                        """UPDATE Users 
                        set balance = ? 
                        where username = ?""",
                        (balancebackup, username))
                    tranconn.commit()
                #print("Error with Tron blockchain:", traceback.format_exc())
                return "NO,Error with Tron blockchain: "+str(e)
    else:
        return "NO,Wrapper is disabled"


def protocol_unwrap_wduco(username, tron_address, amount):
    if use_wrapper and wrapper_permission and unwrap_enabled:
        while True:
            try:
                with sqlite3.connect(database) as conn:
                    #print("Retrieving user balance")
                    datab = conn.cursor()
                    datab.execute(
                        "SELECT * FROM Users WHERE username = ?", (username,))
                    # Get current balance
                    balance = float(datab.fetchone()[3])
                    break
            except Exception:
                pass

        #print("Balance retrieved")
        i = 0
        while i < 3:
            try:
                wbalance = float(
                    int(wduco.functions.pendingWithdrawals(
                        tron_address, username)
                        )
                )/10**6
                break
            except:
                i += 1
        if i >= 3:
            return "NO,error with Tron blockchain"

        if float(amount) <= float(wbalance) and float(amount) > 0:

            if float(amount) <= float(wbalance):
                #print("Correct amount")
                balancebackup = balance
                #print("Updating DUCO Balance")
                balancebackup = balance
                balance = str(float(balance)+float(amount))
                while True:
                    try:
                        with sqlite3.connect(database) as conn:
                            datab = conn.cursor()
                            datab.execute(
                                """UPDATE 
                                    Users set balance = ? 
                                    where username = ?""",
                                (balance, username))
                            conn.commit()
                            break
                    except Exception:
                        pass
                try:
                    admin_print("Sending tron transaction")
                    txn = wduco.functions.confirmWithdraw(
                        username,
                        tron_address,
                        int(float(amount)*10**6)
                    ).with_owner(wrapper_public_key
                                 ).fee_limit(20_000_000
                                             ).build().sign(
                        PrivateKey(bytes.fromhex(wrapper_private_key)))

                    admin_print("Unwrap TXID: " + txn.txid)
                    txn = txn.broadcast()

                    #print("Sent confirm tx to tron network")
                    txnsucceeded = txn.wait()
                    if txnsucceeded:
                        trontxfeedback = txn.result()
                    else:
                        trontxfeedback = False

                    if trontxfeedback:
                        admin_print("Successful unwrap")
                        try:
                            with sqlite3.connect(config_db_transactions,
                                                 timeout=database_timeout
                                                 ) as tranconn:
                                datab = tranconn.cursor()
                                now = datetime.datetime.now()
                                formatteddatetime = now.strftime(
                                    "%d/%m/%Y %H:%M:%S")
                                lastBlockHash = sha1(
                                    bytes(str(tron_address)+str(now),
                                          encoding='utf8')
                                ).hexdigest()
                                memo = str(tron_address)
                                datab.execute("""INSERT INTO 
                                        Transactions(
                                        timestamp, 
                                        username, 
                                        recipient, 
                                        amount, 
                                        hash,
                                        memo) 
                                        VALUES(?, ?, ?, ?, ?, ?)""",
                                              (formatteddatetime,
                                               "wDUCO",
                                                  username,
                                                  amount,
                                                  lastBlockHash,
                                                  memo))
                                tranconn.commit()
                        except Exception as e:
                            print(e)
                        return "OK,Sucessfull unwrap,"+str(lastBlockHash)
                    else:
                        while True:
                            try:
                                with sqlite3.connect(database) as conn:
                                    datab = conn.cursor()
                                    datab.execute(
                                        """UPDATE Users 
                                            set balance = ? 
                                            where username = ?""",
                                        (balancebackup, username))
                                    conn.commit()
                                    break
                            except Exception:
                                pass
                except Exception as e:
                    while True:
                        try:
                            with sqlite3.connect(database) as conn:
                                datab = conn.cursor()
                                datab.execute(
                                    """UPDATE Users 
                                        set balance = ? 
                                        where username = ?""",
                                    (balancebackup, username))
                                conn.commit()
                                break
                        except Exception:
                            pass
                    #print("Error with Tron blockchain:")
                    # print(traceback.format_exc())
                    return "NO,error with Tron blockchain"+str(e)
    else:
        return "NO,Wrapper disabled"
