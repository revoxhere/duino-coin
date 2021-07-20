#!/usr/bin/env python3
##########################################
# Duino-Coin Node (v2.5.7)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2021
##########################################

from socket import socket
from time import sleep
from hashlib import sha1
from random import randint
from json import dumps


class Resp:
    SEPARATOR = ","
    ENDLINE = "\n"
    ENCODING = "utf-8"


def send_data(data: str, soc) -> None:
    data_b = bytes(data, encoding=Resp.ENCODING)
    soc.sendall(data_b)


def recv_data(soc, limit=128) -> str:
    data = soc.recv(limit).decode(Resp.ENCODING)
    return data.rstrip(Resp.ENDLINE)


def pretty_print(*message):
    print(*message)


class Node():
    def __init__(self):
        self.soc = socket()
        self.soc.connect((str("server.duinocoin.com"), int(2810)))
        self.soc.settimeout(15)
        pretty_print("Server is on version", recv_data(self.soc))
        self.sync()

    def sync(self):
        pretty_print("Syncing with the server...")

        send_data("NODE", self.soc)
        sync_data = recv_data(self.soc).split(Resp.SEPARATOR)

        last_hash = sync_data[0]
        difficulty = int(sync_data[1])

        self.create_jobs(last_hash, difficulty)

    def create_jobs(self,
                    last_hash: str,
                    difficulty: int,
                    amount=10):
        self.created_shares = {}

        pretty_print("Creating",
                     amount,
                     "share(s) for hash",
                     last_hash[:6])

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

        pretty_print("Finished creating jobs")

        self.send_jobs(self.created_shares)

    def send_jobs(self, jobs):
        pretty_print("Sending jobs back to the server")
        send_data(dumps(jobs), self.soc)

        pretty_print("Feedback:", recv_data(self.soc))


if __name__ == "__main__":
    Node()
