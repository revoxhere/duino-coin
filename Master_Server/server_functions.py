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


def receive_data(connection, limit=256):
    """ Returns received data from the connection,
        raises an exception on error """
    data = connection.recv(limit)

    if not data:
        connection.close()
        raise Exception("Connection closed unexpectedly")
        return None
    else:
        data_pre_split = data
        data = data.decode("utf8").replace("\n", "").split(",")
        if data[0].startswith("Pool"):
            data = pool_info_parser(data, data_pre_split)

        return data


def send_data(data, connection):
    """ Sends data to the connection,
        raises an exception on error """
    try:
        connection.sendall(bytes(str(data), encoding="utf8"))
    except Exception:
        connection.close()
        raise Exception("Connection closed unexpectedly")
        
