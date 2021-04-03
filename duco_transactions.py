##########################################
# Duino-Coin Transactions Module
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# Creator: Connor2
# © Duino-Coin Community 2021
##########################################
import ast
import requests


TRANSACTIONS_URL = "http://51.15.127.80/transactions.json"


class transaction_data:

    def __init__(self, data, token):
        self.data = data
        self.token = token

        self.obj = (self.token, self.data)
        self.all = (self.token, self.data)

        self.time = self.data["Time"]
        self.amount = self.data["Amount"]
        self.recipient = self.data["Recipient"]
        self.sender = self.data["Sender"]


class user_data:

    def __init__(self, data):
        self.data = data


    def diction(self):
        """Returns all transactions"""
        return self.data


    def tokens(self):
        """Returns all tokens"""
        return self.data.keys()


    def token(self, token):
        """Searches by token"""
        for item in self.data.keys():
            info = self.data[item]
            if item == str(token):
                return transaction_data(info, item)


    def time(self, time):
        """Searches by time"""
        for item in self.data.keys():
            info = self.data[item]
            if info['Time'] == str(time):
                return transaction_data(info, item)


    def sender(self, sender):
        """Searches by sender"""
        for item in self.data.keys():
            info = self.data[item]
            if info['Sender'] == str(sender):
                return transaction_data(info, item)


    def recipient(self, recipient):
        """Searches by recipient"""
        for item in self.data.keys():
            info = self.data[item]
            if info['Recipient'] == str(recipient):
                return transaction_data(info, item)


    def amount(self, amount):
        """Searches by amount"""
        for item in self.data.keys():
            info = self.data[item]
            if info['Amount'] == str(amount):
                return transaction_data(info, item)



class read_data:

    def __init__(self):
        response = requests.get(TRANSACTIONS_URL, data=None)
        if response.status_code == 200:
            data1 = (response.content.decode())
        else:
            raise ConnectionError("Could not connect to server")

        try:
            self.data = ast.literal_eval(data1)
        except:
            raise Exception("Data cant be converted into a dict. please retry")

        self.username = None


    def total_transactions(self):
        return len(self.data)


    def print(self):
        for trans in self.data.keys():
            print(self.data[trans])


    def all(self):
        return user_data(data=self.data)


    def user_transactions(self, username=None):
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        sent = {}
        for trans in self.data.keys():
            info = (self.data[trans])
            if info['Sender'] == self.username:
                sent.update({trans: info})


        # return sent
        return user_data(data=sent)


    def user_transaction_qty(self, username=None):
        """Gets total amount of user sends"""
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        count = 0
        for trans in self.data.keys():
            info = (self.data[trans])
            if info['Sender'] == self.username:
                count += 1

        return count


    def user_reciepts(self, username=None):
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        sent = {}
        for trans in self.data.keys():
            info = (self.data[trans])
            if info['Recipient'] == self.username:
                sent.update({trans: info})

        return user_data(data=sent)


    def user_reciept_qty(self, username=None):
        """Gets total amount of user reciepts"""
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        count = 0
        for trans in self.data.keys():
            info = (self.data[trans])
            if info['Recipient'] == self.username:
                count += 1

        return count


    def total_duco_sent(self, username=None):
        """Gets total amount of duco sent by user"""
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        total = 0

        transactions = self.user_transactions()
        for token in transactions.tokens():
            info = transactions.token(token=token)

            total += float(info.amount)

        return total


    def total_duco_received(self, username=None):
        """Gets total amount of duco recieved by user"""
        if username != None:
            self.username = username
        elif self.username == None:
            raise ValueError("Please provide a username")

        total = 0

        transactions = self.user_reciepts()
        for token in transactions.tokens():
            info = transactions.token(token=token)

            total += float(info.amount)

        return total


