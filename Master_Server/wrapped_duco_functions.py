## wDUCO 2.0 functions by yanis (@ygboucherk), 2020-2021
import sqlite3
import traceback
from hashlib import sha1
from Server import DATABASE as database
from Server import DB_TIMEOUT as database_timeout
from Server import CONFIG_TRANSACTIONS as config_db_transactions
from Server import WRAPPER_KEY as wrapper_private_key

use_wrapper = True
wrapper_permission = False

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
    print("Sent confirm tx to tron network by" + duco_username)
    return feedback


def protocol_wrap_wduco(username, tron_address, amount):
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

    if float(balance) < float(amount) or float(amount) <= 0:
        return "NO,Incorrect amount"

    elif float(balance) >= float(amount) and float(amount) > 0:
        balancebackup = balance
        print("Backed up balance: " + str(balancebackup))
        try:
            print("All checks done, initiating wrapping routine")
            balance -= float(amount)
            print("DUCO removed from pending balance")

            with sqlite3.connect(database) as conn:
                datab = conn.cursor()
                datab.execute(
                    """UPDATE Users
                    set balance = ?
                    where username = ?""",
                    (balance, username))
                conn.commit()
            print("DUCO balance sent to DB, sending tron transaction")

            print("Tron wrapper called")
            txn = wduco.functions.wrap(
                tron_address,
                int(float(amount)*10**6)
            ).with_owner(wrapper_public_key
                         ).fee_limit(20_000_000
                                     ).build().sign(
                PrivateKey(
                    bytes.fromhex(wrapper_private_key)))

            print("Txid: " + txn.txid)
            txn = txn.broadcast()

            print("Sent wrap tx to TRON network")
            txnsucceeded = txn.wait()
            if txnsucceeded:
                trontxfeedback = txn.result()
            else:
                trontxfeedback = False

            if trontxfeedback:
                print("Successful wrapping")
                try:
                    with sqlite3.connect(config_db_transactions,
                                         timeout=database_timeout) as tranconn:
                        datab = tranconn.cursor()
                        now = datetime.datetime.now()
                        lastBlockHash = sha1(
                            tron_address+str(amount)).hexdigest()
                        formatteddatetime = now.strftime(
                            "%d/%m/%Y %H:%M:%S")
                        datab.execute("""INSERT INTO 
                            Transactions(
                            timestamp, 
                            username, 
                            recipient, 
                            amount, 
                            hash) 
                            VALUES(?, ?, ?, ?, ?)""",
                                      (formatteddatetime,
                                       username,
                                       str("wrapper - ")+str(tron_address),
                                          amount,
                                          lastBlockHash))
                        tranconn.commit()
                        return "OK,Sucessfull wrapping,"+str(lastBlockHash)
                except Exception:
                    pass
            else:
                try:
                    datab.execute(
                        """UPDATE Users 
                        set balance = ? 
                        where username = ?""",
                        (balancebackup, username))
                    return "NO,Unknown error, transaction reverted"
                except Exception:
                    pass
        except Exception as e:
            print("Error with Tron blockchain:")
            print(traceback.format_exc())
            return "NO,error with Tron blockchain"+str(e)

    else:
        return "NO,Wrapper disabled"


def protocol_unwrap_wduco(username, tron_address, amount):
    while True:
        try:
            with sqlite3.connect(database) as conn:
                print("Retrieving user balance")
                datab = conn.cursor()
                datab.execute(
                    "SELECT * FROM Users WHERE username = ?", (username,))
                # Get current balance
                balance = float(datab.fetchone()[3])
                break
        except Exception:
            pass

    print("Balance retrieved")
    wbalance = float(
        int(wduco.functions.pendingWithdrawals(tron_address, username)))/10**6

    if float(amount) <= float(wbalance) and float(amount) > 0:

        if float(amount) <= float(wbalance):
            print("Correct amount")
            balancebackup = balance
            print("Updating DUCO Balance")
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
                print("Sending tron transaction")
                txn = wduco.functions.confirmWithdraw(
                    username,
                    tron_address,
                    int(float(amount)*10**6)
                ).with_owner(wrapper_public_key
                             ).fee_limit(20_000_000
                                         ).build().sign(
                    PrivateKey(bytes.fromhex(wrapper_private_key)))

                print("Txid: " + txn.txid)
                txn = txn.broadcast()

                print("Sent confirm tx to tron network")
                txnsucceeded = txn.wait()
                if txnsucceeded:
                    trontxfeedback = txn.result()
                else:
                    trontxfeedback = False

                if trontxfeedback:
                    print("Successful unwrapping")
                    with sqlite3.connect(config_db_transactions,
                                         timeout=database_timeout) as tranconn:
                        datab = tranconn.cursor()
                        now = datetime.datetime.now()
                        formatteddatetime = now.strftime(
                            "%d/%m/%Y %H:%M:%S")
                        lastBlockHash = sha1(
                            tron_address+str(amount)).hexdigest()
                        datab.execute("""INSERT INTO 
                                Transactions(
                                timestamp, 
                                username, 
                                recipient, 
                                amount, 
                                hash) 
                                VALUES(?, ?, ?, ?, ?)""",
                                      (formatteddatetime,
                                       str("Wrapper - ")+str(tron_address),
                                          username,
                                          amount,
                                          lastBlockHash))
                        tranconn.commit()
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
                print("Error with Tron blockchain:")
                print(traceback.format_exc())
                return "NO,error with Tron blockchain"+str(e)
