import sqlite3
from server_functions import receive_data, send_data

database = 'crypto_database.db'
database_timeout = 10
PoolVersion = 0.1


def PoolList_NO_SEND():
    with sqlite3.connect(database, timeout=database_timeout) as conn:
        c2 = conn.cursor()
        c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT, hidden TEXT, cpu REAL, ram REAL)''')

        c2.execute("SELECT name, ip, port, Status, ram, cpu FROM PoolList WHERE hidden != 'ok'")
        info = c2.fetchall()
        info = (str(info)).replace('\n', '')

        return info


def PoolList(connection):
    send_data(data=PoolList_NO_SEND(), connection=connection)


def PoolLoginAdd(connection, data, PoolPassword):
    try:
        password = str(data[1])
        info = str(data[2])

        info = ast.literal_eval(info)
        poolName = info['name']
        poolHost = info['host']
        poolPort = info['port']
        poolID = info['identifier']
        poolHidden = info['hidden']
    except Exception as e:
        print(e)
        send_data(data=f"NO,Error: {e}", connection=connection)

    if password == PoolPassword:
        print("Debug 3")
        with sqlite3.connect(database, timeout=database_timeout) as conn:
            c2 = conn.cursor()
            print("Debug 4")
            c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT, hidden TEXT, cpu REAL, ram REAL)''')

            c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
            if (c2.fetchall()[0][0]) == 0:
                c2.execute("INSERT INTO PoolList(identifier, name, ip, port, Status, hidden, cpu, ram) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",(poolID, poolName, poolHost, poolPort, "False", poolHidden, 0, 0))

                conn.commit()
                send_data(data="LoginOK", connection=connection)

            else:
                send_data(data="NO,Identifier not found", connection=connection)
    else:
        send_data(data="NO,Password Incorrect", connection=connection)


def PoolLoginRemove(connection, data, PoolPassword):
    try:
        password = str(data[1])
        info = str(data[2])

        info = ast.literal_eval(info)
        poolID = info['identifier']
    except Exception as e:
        print(e)
        send_data(data=f"NO,Error: {e}", connection=connection)

    if password == PoolPassword:
        with sqlite3.connect(database, timeout=database_timeout) as conn:
            c2 = conn.cursor()
            c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT, hidden TEXT, cpu REAL, ram REAL)''')

            c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
            if (c2.fetchall()[0][0]) != 0:
                c2.execute('''DELETE FROM PoolList WHERE identifier=?''',(poolID,))

                conn.commit()
                send_data(data="DeletedOK", connection=connection)

            else:
                send_data(data="NO,Identifier not found", connection=connection)
    else:
        send_data(data="NO,Password Incorrect", connection=connection)


class Pool_Function_class:

    def __init__(connection):
        self.poolID = None
        self.connection = connection

    def login(self, data):
        try:
            info = str(data[1])

            info = ast.literal_eval(info)
            poolHost = info['host']
            poolPort = info['port']
            poolVersion_sent = info['version']
            self.poolID = info['identifier']
        except IndexError:
            send_data(data="NO,Not enough data", connection=self.connection)

        if str(poolVersion_sent) == str(PoolVersion):
            with sqlite3.connect(database, timeout=database_timeout) as conn:
                c2 = conn.cursor()
                c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT, hidden TEXT, cpu REAL, ram REAL)''')

                c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (self.poolID,))
                if (c2.fetchall()[0][0]) == 0:
                    send_data(data="NO,Identifier not found", connection=self.connection)

                c2.execute("UPDATE PoolList SET ip = ?, port = ?, Status = ? WHERE identifier = ?",(poolHost, poolPort, "True", self.poolID))

                conn.commit()

                send_data(data="LoginOK", connection=self.connection)
        else:
            send_data(data="LoginFailed", connection=self.connection)


    def sync(self, data, global_blocks):
        if self.poolID == None:
            send_data(data="No PoolID provided", connection=self.connection)

        try:
            info = str(data[1])
            info = ast.literal_eval(info)
            
            rewards = info['rewards']
            blocks_to_add = int(info['blocks']['blockIncrease'])
            poolCpu = float(info['cpu'])
            poolRam = float(info['ram'])
        except Exception as e:
            print(e)
            send_data(data=f"NO,Error: {e}", connection=self.connection)

        # ============

        global_blocks += blocks_to_add

        with sqlite3.connect(database, timeout=database_timeout) as conn:
            datab = conn.cursor()
            for user in rewards.keys():
                datab.execute("UPDATE Users set balance = balance + ?  where username = ?", (float(rewards[user]), user))
                
            datab.execute("UPDATE PoolList SET cpu = ?, ram = ? WHERE identifier = ?", (poolCpu, poolRam, self.poolID))
            conn.commit()

        # ============
        data_send = {"totalBlocks": global_blocks,
                    "diffIncrease": diff_incrase_per}

        data_send = (str(data_send)).replace("\'", "\"")

        send_data(data=f"SyncOK,{data_send}", connection=self.connection)

        return global_blocks


    def logout(self, data):
        try:
            poolID = str(data[1])
        except IndexError:
            send_data(data="NO,Not enough data", connection=self.connection)


        with sqlite3.connect(database, timeout=database_timeout) as conn:
            c2 = conn.cursor()
            c2.execute('''CREATE TABLE IF NOT EXISTS PoolList(identifier TEXT, name TEXT, ip TEXT, port TEXT, Status TEXT, hidden TEXT, cpu REAL, ram REAL)''')

            c2.execute("SELECT COUNT(identifier) FROM PoolList WHERE identifier = ?", (poolID,))
            if (c2.fetchall()[0][0]) == 0:
                send_data(data="NO,Identifier not found", connection=self.connection)

            c2.execute("UPDATE PoolList SET Status = ? WHERE identifier = ?",("False", poolID))

            conn.commit()

            send_data(data="LogoutOK", connection=self.connection)
