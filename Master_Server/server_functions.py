
def Comma_Seperator_filter(data, data2):
    if data[0] == "PoolSync":
        leng_of_base = 9
        new_data = (data2[leng_of_base:])
        data = ['PoolSync', new_data]

    elif data[0] == "PoolLoginAdd":
        leng_of_base = 14 + len(data[1])
        new_data = (data2[leng_of_base:])
        data = ['PoolLoginAdd', data[1], new_data]

    elif data[0] == "PoolLoginRemove":
        leng_of_base = 17 + len(data[1])
        new_data = (data2[leng_of_base:])
        data = ['PoolLoginRemove', data[1], new_data]

    elif data[0] == "PoolLogin":
        leng_of_base = 10
        new_data = (data2[leng_of_base:])
        data = ['PoolLogin', new_data]

    return data


def receive_data(connection):
    """ Returns received data from the connection,
        raises an exception on error """
    data = connection.recv(128)
    if not data:
        connection.close()
        raise Exception("Connection closed unexpectedly")
        return None
    else:
        data_pre_split = data
        data = data.decode("utf8").replace("\n", "").split(",")
        data = Comma_Seperator_filter(data, data_pre_split)

        return data


def send_data(data, connection):
    """ Sends data to the connection,
        raises an exception on error """
    try:
        connection.sendall(bytes(str(data), encoding="utf8"))
    except Exception:
        raise Exception("Connection closed unexpectedly")
        connection.close()
