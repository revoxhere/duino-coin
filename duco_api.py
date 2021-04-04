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
            # Checks whether the token is the one that's being searched
            if item == str(token):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def time(self, time):
        """Searches by time"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the 'Time' is equal to the one searched
            if info['Time'] == str(time):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def sender(self, sender):
        """Searches by sender"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the sender's the one being searched
            if info['Sender'] == str(sender):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def recipient(self, recipient):
        """Searches by recipient"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the recipient's the one being searched
            if info['Recipient'] == str(recipient):
                # It is, so return the transaction data of it
                return transaction_data(info, item)


    def amount(self, amount):
        """Searches by amount"""
        for item in self.data.keys():
            info = self.data[item]
            # Checks whether the amount is the one being searched
            if info['Amount'] == str(amount):
                # It is, so return the transaction data of it
                return transaction_data(info, item)



class read_data:

    def __init__(self):
        # Gets response from transactions.json on the masterserver
        response = requests.get(TRANSACTIONS_URL, data=None)
        # Checks whether data has been sent (http-code = ok)
        if response.status_code == 200:
            # The response was "ok" so get data from response body (content)
            data1 = (response.content.decode())
        else:
            # The response was anything als than "ok", so report the error
            raise ConnectionError("Could not connect to server")

        try:
            # Tries to convert the received data into a dictionary.
            self.data = ast.literal_eval(data1)
        except:
            # The convertion failed, so report the error
            raise Exception("Data cant be converted into a dict. please retry")
        # No username has been specified up until this point, so set it to "None"
        self.username = None


    def total_transactions(self):
        # Returns the amount of transactions
        return len(self.data)


    def print(self):
        # Iterates through every transactions
        for trans in self.data.keys():
            # and prints it
            print(self.data[trans])


    def all(self):
        # Creates a userdata-instance based on the data provided
        return user_data(data=self.data)


    def user_transactions(self, username=None):
        # Checks whether a 'valid' username was specified.
        if username != None:
            # It was, so set the class-variable to it
            self.username = username
        elif self.username == None:
            # The username was None, so print an 'error'
            raise ValueError("Please provide a username")

        sent = {}
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores the details of a transaction
            info = (self.data[trans])
            # And checks whether the 'Sender' was the specified user
            if info['Sender'] == self.username:
                # It was, so the info gets pushed to the 'sent' variable
                sent.update({trans: info})


        # return sent
        return user_data(data=sent)


    def user_transaction_qty(self, username=None):
        """Gets total amount of user sends"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Counts the transactions sent by the user
        count = 0
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores the details in this variable
            info = (self.data[trans])
            # And then checks whether the 'Sender' is the user specified
            if info['Sender'] == self.username:
                # It is the user specified, so add 1 to the transaction-counter
                count += 1

        return count


    def user_reciepts(self, username=None):
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores the received transactions
        sent = {}
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores their details in this variable
            info = (self.data[trans])
            # Checks whether the 'Recipient' is the user specified
            if info['Recipient'] == self.username:
                # It is the user, so push the info to the variable
                sent.update({trans: info})

        # Returns userdata based on received transactions
        return user_data(data=sent)


    def user_reciept_qty(self, username=None):
        """Gets total amount of user reciepts"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Counts how many transactions have been received
        count = 0
        # Iterates through every transaction available
        for trans in self.data.keys():
            # Stores their details in this variable
            info = (self.data[trans])
            # Checks whether the 'Recipient' is the user specified
            if info['Recipient'] == self.username:
                # It is the user, so add 1 to the receive-counter
                count += 1

        # Return the amount of received transactions.
        return count


    def total_duco_sent(self, username=None):
        """Gets total amount of duco sent by user"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores how many ducos the user has sent
        total = 0

        # Gets the transactions the user has sent
        transactions = self.user_transactions()
        # Iterates through the sent transactions
        for token in transactions.tokens():
            # Gets the transaction details
            info = transactions.token(token=token)
            # Adds the sent amount to the total
            total += float(info.amount)

        # Returns the total duco sent
        return total


    def total_duco_received(self, username=None):
        """Gets total amount of duco recieved by user"""
        # Checks whether there's a valid username provided
        if username != None:
            # It is, so the class-variable gets set
            self.username = username
        elif self.username == None:
            # The username can't be valid, so print an 'error'/warning
            raise ValueError("Please provide a username")

        # Stores how many ducos the user has received
        total = 0

        # Gets every transaction the user has received
        transactions = self.user_reciepts()
        # Iterates through the received transactions
        for token in transactions.tokens():
            # Gets the transaction details
            info = transactions.token(token=token)
            # Adds the received amount to the total
            total += float(info.amount)

        # Returns the total amount of ducos received
        return total
