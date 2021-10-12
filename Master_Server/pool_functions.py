#!/usr/bin/env python3
"""
Duino-Coin Pool sync module © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin-rest-api
Duino-Coin Team & Community 2019-2021
"""

import sqlite3
from server_functions import receive_data, send_data
from Server import DIFF_INCREASES_PER, CONFIG_BLOCKS, DB_TIMEOUT
import ast
import json
import datetime
import requests

POOL_DATABASE = 'config/pools_database.db'
POOL_VER = 0.1


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def floatmap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def generate_block(username, reward, new_block_hash, algo):
    with sqlite3.connect(CONFIG_BLOCKS, timeout=DB_TIMEOUT) as conn:
        datab = conn.cursor()
        timestamp = now().strftime("%d/%m/%Y %H:%M:%S")
        datab.execute(
            """INSERT INTO
            Blocks(
            timestamp,
            finder,
            amount,
            hash)
            VALUES(?, ?, ?, ?)""",
            (timestamp, username + " (" + algo + ")",
                reward, new_block_hash))
        conn.commit()
    print("Pool block found by " + username)


def _pool_list():
    with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
        conn.row_factory = dict_factory
        c2 = conn.cursor()
        c2.execute("""CREATE TABLE
            IF NOT EXISTS
            PoolList(
            identifier TEXT,
            name TEXT,
            ip TEXT,
            port TEXT,
            Status TEXT,
            hidden TEXT,
            cpu REAL,
            ram REAL,
            connections INT)""")

        c2.execute(
            """SELECT name, ip, port, Status, ram, cpu
            FROM PoolList
            WHERE hidden != 'True'""")
        info = c2.fetchall()
        info = str(info).replace("'", '"')

        return info


def pool_list(connection):
    send_data(data=_pool_list(), connection=connection)


def pool_login_add(connection, data, PoolPassword):
    try:
        password = str(data[1])

        info = str(data[2])
        info = ast.literal_eval(info)
        info = json.loads(info)

        poolHost = info['host']
        poolPort = info['port']

        poolID = info['identifier']
        poolName = info['name']

        poolHidden = info['hidden']
    except Exception as e:
        print(e)
        send_data(data=f"NO,Error: {e}", connection=connection)

    if password == PoolPassword:
        with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
            c2 = conn.cursor()
            print("Debug 4")
            c2.execute("""CREATE TABLE
                IF NOT EXISTS
                PoolList(
                identifier TEXT,
                name TEXT,
                ip TEXT,
                port TEXT,
                Status TEXT,
                hidden TEXT,
                cpu REAL,
                ram REAL,
                connections INT)""")

            c2.execute(
                """SELECT
                COUNT(identifier)
                FROM PoolList
                WHERE identifier = ?""",
                (poolID,))
            if (c2.fetchall()[0][0]) == 0:
                c2.execute("""INSERT INTO PoolList(
                    identifier,
                    name,
                    ip,
                    port,
                    Status,
                    hidden,
                    cpu,
                    ram,
                    connections)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (poolID,
                            poolName,
                            poolHost,
                            poolPort,
                            "False",
                            poolHidden,
                            0, 0, 0))

                conn.commit()
                send_data(data="LoginOK", connection=connection)

            else:
                send_data(data="NO,Identifier not found",
                          connection=connection)
    else:
        send_data(data="NO,Password Incorrect", connection=connection)


def pool_login_remove(connection, data, PoolPassword):
    try:
        password = str(data[1])
        poolID = str(data[2])
    except Exception as e:
        print(e)
        send_data(data=f"NO,Error: {e}", connection=connection)

    if password == PoolPassword:
        with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
            c2 = conn.cursor()
            c2.execute("""CREATE TABLE
                IF NOT EXISTS
                PoolList(
                identifier TEXT,
                name TEXT,
                ip TEXT,
                port TEXT,
                Status TEXT,
                hidden TEXT,
                cpu REAL,
                ram REAL,
                connections INT)""")

            c2.execute(
                """SELECT
                COUNT(identifier)
                FROM PoolList
                WHERE identifier = ?""",
                (poolID,))
            if (c2.fetchall()[0][0]) != 0:
                c2.execute(
                    """DELETE
                    FROM PoolList
                    WHERE identifier=?""",
                    (poolID,))

                conn.commit()
                send_data(data="DeletedOK", connection=connection)

            else:
                send_data(data="NO,Identifier not found",
                          connection=connection)
    else:
        send_data(data="NO,Password Incorrect", connection=connection)


class Pool:
    def __init__(self, connection):
        self.poolID = None
        self.poolIP = None
        self.connection = connection
        self.session = requests.Session()

    def login(self, data):
        try:
            info = str(data[1])
            info = ast.literal_eval(info)
            info = json.loads(info)

            self.poolIP = info['host']
            self.poolID = info['identifier']
            self.poolName = info['name']
            poolPort = info['port']
            poolVersion_sent = info['version']
        except IndexError:
            send_data(data="NO,Not enough data", connection=self.connection)

        if str(poolVersion_sent) == str(POOL_VER):
            with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
                c2 = conn.cursor()
                c2.execute(
                    """CREATE TABLE
                    IF NOT EXISTS
                    PoolList(
                    identifier TEXT,
                    name TEXT,
                    ip TEXT,
                    port TEXT,
                    Status TEXT,
                    hidden TEXT,
                    cpu REAL,
                    ram REAL,
                    connections INT)""")

                c2.execute(
                    """SELECT COUNT(identifier)
                    FROM PoolList
                    WHERE identifier = ?""",
                    (self.poolID,))

                if (c2.fetchall()[0][0]) == 0:
                    send_data(data="NO,Identifier not found",
                              connection=self.connection)

                c2.execute("""UPDATE PoolList
                    SET ip = ?,
                    port = ?,
                    connections = ?,
                    Status = ?
                    WHERE identifier = ?""",
                           (self.poolIP,
                            poolPort, 0,
                            "True",
                            self.poolID))

                conn.commit()

            send_data(data="LoginOK", connection=self.connection)
        else:
            send_data(data="LoginFailed", connection=self.connection)

    def sync(self, data):
        blocks_to_add = 0
        poolConnections = 0
        poolWorkers = {}
        rewards = {}
        poolCpu = 0
        poolRam = 0
        self.connection.settimeout(45)

        if not self.poolID or not self.poolName:
            send_data(data="No PoolID provided", connection=self.connection)
            return blocks_to_add, poolConnections, poolWorkers, rewards, 0

        try:
            info = str(data[1].decode())
            info = ast.literal_eval(info)

            blocks_to_add = int(info['blocks']['blockIncrease'])
            big_blocks_to_add = info['blocks']['bigBlocks']
            poolCpu = float(info['cpu'])
            poolRam = float(info['ram'])
            poolConnections = int(info['connections'])
            hide_this_pool = "False"

            # if poolConnections > 7000:
            #    hide_this_pool = "True"
        except Exception as e:
            send_data(data=f"NO,Error: {e}", connection=self.connection)
            return 0, 0, {}, {}, 1

        try:
            with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
                datab = conn.cursor()
                datab.execute("""UPDATE PoolList
                    SET cpu = ?,
                    ram = ?,
                    connections = ?,
                    hidden = ?
                    WHERE identifier = ?""",
                              (poolCpu,
                               poolRam,
                               poolConnections,
                               hide_this_pool,
                               self.poolID))
                conn.commit()
        except Exception as e:
            print(e)

        i = 0
        while i < 2:
            try:
                # print(f"Attempting to download http://{self.poolIP}/rewards_{self.poolName}.json")
                rewards = self.session.get(
                    f"http://{self.poolIP}/rewards_{self.poolName}.json").json()
                # print(f"Downloaded http://{self.poolIP}/rewards_{self.poolName}.json OK")
                break
            except Exception as e:
                i += 1
        else:
            print(f"Gave up retrying http://{self.poolIP}/rewards_{self.poolName}.json")

        i = 0
        while i < 2:
            try:
                # print(f"Attempting to download http://{self.poolIP}/workers_{self.poolName}.json")
                poolWorkers = self.session.get(
                    f"http://{self.poolIP}/workers_{self.poolName}.json").json()
                # print(f"Downloaded http://{self.poolIP}/workers_{self.poolName}.json OK")
                break
            except Exception as e:
                i += 1
        else:
            print(f"Gave up retrying http://{self.poolIP}/workers_{self.poolName}.json")

        return blocks_to_add, poolConnections, poolWorkers, rewards, 0

    def logout(self, data):
        try:
            poolID = str(data[1])
        except IndexError:
            send_data(data="NO,Not enough data", connection=self.connection)

        with sqlite3.connect(POOL_DATABASE, timeout=DB_TIMEOUT) as conn:
            c2 = conn.cursor()
            c2.execute("""CREATE TABLE
                IF NOT EXISTS
                PoolList(
                identifier TEXT,
                name TEXT,
                ip TEXT,
                port TEXT,
                Status TEXT,
                hidden TEXT,
                cpu REAL,
                ram REAL,
                connections INT)""")

            c2.execute(
                """SELECT
                COUNT(identifier)
                FROM PoolList
                WHERE identifier = ?""",
                (poolID,))
            if (c2.fetchall()[0][0]) == 0:
                send_data(data="NO,Identifier not found",
                          connection=self.connection)

            c2.execute(
                """UPDATE PoolList
                SET Status = ?
                WHERE identifier = ?""",
                ("False", poolID))

            conn.commit()

            send_data(data="LogoutOK", connection=self.connection)
