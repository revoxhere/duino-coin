#!/usr/bin/env python3
"""
Duino-Coin Server module © MIT licensed
https://duinocoin.com
https://github.com/revoxhere/duino-coin-rest-api
Duino-Coin Team & Community 2019-2021
"""

import threading
import requests
import json
from time import sleep

def scaleway_unban(ip, auth_key, instance_id, time=60*45):
    sleep(time)
    api = "https://api.scaleway.com/instance/v1/zones/nl-ams-1/security_groups"
    headers = {
        "X-Auth-Token": auth_key,
        "Content-Type": "application/json"
    }
    pid2 = requests.delete(
        f"{api}/{instance_id}/rules/{pid}",
        headers=headers).text
    if not pid2:
        print("Banned", pid, ip)


def scaleway_ban(ip, auth_key, instance_id, time=60*45):
    api = "https://api.scaleway.com/instance/v1/zones/nl-ams-1/security_groups"

    data = {
        "protocol": "ANY",
        "direction": "inbound",
        "action": "drop",
        "ip_range": f"{ip}",
        "dest_port_from": None, #None for all
        "dest_port_to": None, #None for all
        "editable": True,
        "position": 1
    }

    headers = {
        "X-Auth-Token": auth_key,
        "Content-Type": "application/json"
    }

    pid = requests.post(
        f"{api}/{instance_id}/rules",
        data=json.dumps(data),
        headers=headers).json()

    try:
        pid = pid["rule"]["id"]
        print("Banned", pid, ip)
        threading.Thread(target=scaleway_unban, args=[ip, auth_key, instance_id, time]).start()
    except:
        pass



def pool_info_parser(data, data2):
    if data[0] == "PoolSync":
        length_of_base = 9
        new_data = (data2[length_of_base:])
        data = ['PoolSync', new_data]

    elif data[0] == "PoolLoginAdd":
        length_of_base = 14 + len(data[1])
        new_data = (data2[length_of_base:])
        data = ['PoolLoginAdd', data[1], new_data]

    elif data[0] == "PoolLoginRemove":
        length_of_base = 17 + len(data[1])
        new_data = (data2[length_of_base:])
        data = ['PoolLoginRemove', data[1], new_data]

    elif data[0] == "PoolLogin":
        length_of_base = 10
        new_data = (data2[length_of_base:])
        data = ['PoolLogin', new_data]

    return data


def receive_data(connection, limit=1024):
    """ Returns received data from the connection,
        raises an exception on error """
    try:
        data = connection.recv(limit)

        if not data:
            connection.close()
            return None

        else:
            data_pre_split = data
            data = data.decode("utf-8").replace("\n", "").split(",")
            if data[0].startswith("Pool"):
                data = pool_info_parser(data, data_pre_split)
            return data
    except:
        connection.close()
        return None


def send_data(data, connection):
    """ Sends data to the connection,
        raises an exception on error """
    try:
        connection.sendall(bytes(str(data), encoding="utf-8"))
    except Exception:
        connection.close()
    return
        
