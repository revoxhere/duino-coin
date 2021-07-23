#!/usr/bin/env python3
##########################################
# Duino-Coin Public Node (v2.5.7)
# This is an early WIP version
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################

from socket import socket
from time import sleep
from hashlib import sha1
from random import randint
from json import dumps
from colorama import init, Fore, Style  # python3 -m pip install colorama
from datetime import datetime
from traceback import format_exc


SOCKET_TIMEOUT = 25
NODE_PORT = 2810
DOCSTRING = """
         Please keep in mind that this 
         an early work in progress version to test the
         concepts. This piece of software will have more
         functionality in the not so far future.

         This node client will connect to one of the master
         ones, request a task, and receive sync data that
         consists of last chain hashes, helping to maintain
         the network.
        """


class Resp:
    """
    Master node response config
    """
    SEPARATOR = ","
    ENDLINE = "\n"
    ENCODING = "utf-8"


class Font:
    """
    Colorama add-ons
    """
    def time():
        return datetime.now().strftime('%H:%M:%S ') + Style.RESET_ALL

    DIM = Fore.WHITE + Style.DIM
    SEP = "-------- "
    BOLD = Fore.YELLOW + Style.BRIGHT


def send_data(data: str, soc) -> None:
    data_b = bytes(data, encoding=Resp.ENCODING)
    try:
        soc.sendall(data_b)
    except Exception:
        pretty_print("Error sending data: "
                     + str(format_exc()))


def recv_data(soc, limit=128) -> str:
    try:
        data = soc.recv(limit).decode(Resp.ENCODING)
    except Exception:
        pretty_print("Error receiving data: "
                     + str(format_exc()))
    return data.rstrip(Resp.ENDLINE)


def pretty_print(*message):
    print(*message)


class Node():
    def __init__(self):
        init(autoreset=True)
        pretty_print(Font.BOLD + Font.SEP + "Duino-Coin Public Node")
        pretty_print(DOCSTRING)

        self.USERNAME = input("Enter your Duino-Coin wallet/username\n> ")

        self.connect()
        while True:
            self.sync()

    def connect(self):
        pretty_print(Font.time() + "Connecting to the master node")
        self.soc = socket()
        self.soc.connect((str("server.duinocoin.com"), int(NODE_PORT)))
        self.soc.settimeout(SOCKET_TIMEOUT)
        pretty_print(Font.time() + "Node is on version", recv_data(self.soc))

    def sync(self):
        pretty_print(Font.time() + "Requesting a task")
        send_data("NODE", self.soc)
        sync_data = recv_data(self.soc).split(Resp.SEPARATOR)

        task = sync_data[0]

        if task == "CREATE_JOBS":
            pretty_print(Font.time() + Fore.GREEN
                         + "Current task: create new jobs for miners")
            last_hash = sync_data[1]
            difficulty = int(sync_data[2])
            pretty_print(Font.time() + Fore.GREEN + "Successfully synced")
            self.create_jobs(last_hash, difficulty)
        else:
            pretty_print(Font.time() + Fore.YELLOW
                         + "There are currently no tasks to be done."
                         + " Checking again in 10s")
            sleep(10)

    def create_jobs(self,
                    last_hash: str,
                    difficulty: int,
                    amount=10):
        self.created_shares = {}

        pretty_print(Font.time()
                     + "Creating "
                     + str(amount)
                     + " share(s) for hash "
                     + Font.BOLD
                     + last_hash[:6])

        for i in range(amount):
            numeric_result = randint(0, 100 * difficulty)
            expected_hash = sha1(
                bytes(last_hash+str(numeric_result),
                      encoding=Resp.ENCODING)
            ).hexdigest()

            self.created_shares[i] = {
                "lhash": last_hash,
                "ehash": expected_hash,
                "res":   numeric_result
            }
        pretty_print(Font.time() + Fore.GREEN + "Finished creating jobs")

        self.output_data = {
            "user": self.USERNAME,
            "jobs": self.created_shares
        }

        pretty_print(Font.time() + Fore.GREEN + "Sending created jobs")
        self.send_jobs(self.output_data)

    def send_jobs(self, jobs):
        pretty_print(Font.time() + "Syncing jobs")
        send_data(dumps(jobs), self.soc)

        feedback = recv_data(self.soc)
        if feedback == "OK":
            pretty_print(Font.time() + Fore.GREEN + "Node accepted new jobs")
        else:
            pretty_print(Font.time() + Fore.RED + "Node rejected new jobs")


if __name__ == "__main__":
    Node()
