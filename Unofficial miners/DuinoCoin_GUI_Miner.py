# Based on Minimal PC Miner by Revox
# https://github.com/revoxhere/duino-coin-miner
# Created by rsoda (ilnarildarovuch)

import hashlib
import os
import socket
import sys
import time
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import requests

class Ui_GUI(object):
    def setupUi(self, GUI):
        GUI.setObjectName("GUI")
        GUI.setFixedSize(462, 323)
        self.graphics = pg.PlotWidget(GUI)
        self.graphics.setGeometry(QtCore.QRect(10, 10, 256, 192))
        self.graphics.setObjectName("graphics")
        self.graphics.setBackground("w")
        self.graphics.setAutoVisible(x=True, y=True)
        self.low = QtWidgets.QRadioButton(GUI)
        self.low.setGeometry(QtCore.QRect(310, 50, 82, 17))
        self.low.setObjectName("low")
        self.medium = QtWidgets.QRadioButton(GUI)
        self.medium.setGeometry(QtCore.QRect(310, 70, 82, 17))
        self.medium.setObjectName("medium")
        self.high = QtWidgets.QRadioButton(GUI)
        self.high.setGeometry(QtCore.QRect(310, 90, 82, 17))
        self.high.setObjectName("high")
        self.user = QtWidgets.QLineEdit(GUI)
        self.user.setGeometry(QtCore.QRect(300, 120, 141, 20))
        self.user.setInputMask("")
        self.user.setText("Username")
        self.user.setMaxLength(32767)
        self.user.setObjectName("user")
        self.key = QtWidgets.QLineEdit(GUI)
        self.key.setGeometry(QtCore.QRect(300, 150, 141, 20))
        self.key.setObjectName("key")
        self.miner_id = QtWidgets.QLineEdit(GUI)
        self.miner_id.setGeometry(QtCore.QRect(300, 180, 141, 20))
        self.miner_id.setObjectName("miner_id")
        self.log = QtWidgets.QTextBrowser(GUI)
        self.log.setGeometry(QtCore.QRect(10, 220, 441, 51))
        self.log.setObjectName("log")
        self.start = QtWidgets.QPushButton(GUI)
        self.start.setGeometry(QtCore.QRect(270, 290, 75, 23))
        self.start.setObjectName("start")
        self.stop = QtWidgets.QPushButton(GUI)
        self.stop.setGeometry(QtCore.QRect(370, 290, 75, 23))
        self.stop.setObjectName("stop")
        self.threads_len = QtWidgets.QLineEdit(GUI)
        self.threads_len.setGeometry(QtCore.QRect(20, 290, 61, 20))
        self.threads_len.setInputMask("")
        self.threads_len.setValidator(QtGui.QIntValidator(1, 999, self))
        self.threads_len.setObjectName("threads_len")

        self.retranslateUi(GUI)
        QtCore.QMetaObject.connectSlotsByName(GUI)

    def retranslateUi(self, GUI):
        self.pref_hashes = 0
        self.wased_hashes = []
        self.threads = []
        _translate = QtCore.QCoreApplication.translate
        GUI.setWindowTitle(_translate("GUI", "GUI Duino Coin Miner"))
        self.low.setText(_translate("GUI", "LOW"))
        self.low.setChecked(True)
        self.medium.setText(_translate("GUI", "MEDIUM"))
        self.high.setText(_translate("GUI", "HIGH"))
        self.key.setText(_translate("GUI", "Mining key ( Or empty )"))
        self.miner_id.setText(_translate("GUI", "Minimal_PC_Miner"))
        self.start.setText(_translate("GUI", "Start"))
        self.stop.setText(_translate("GUI", "Stop"))
        self.threads_len.setText(_translate("GUI", "Threads"))

class GUI(QtWidgets.QWidget, Ui_GUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.setupUi(self)
        self.start.clicked.connect(self.start_mining)
        self.stop.clicked.connect(self.stop_mining)

    def start_mining(self):
        username = self.user.text()
        mining_key = self.key.text()
        miner_id = self.miner_id.text()
        diff_choice = ""  # default value

        try:
            power = int(self.threads_len.text())
        except ValueError:
            power = 1
            self.threads_len.setText("1")
        
        if self.low.isChecked():
            diff_choice = "l"
        elif self.medium.isChecked():
            diff_choice = "m"
        elif self.high.isChecked():
            diff_choice = "h"
        for i in range(power):
            self.threads.append(MiningThread(username, mining_key, diff_choice, miner_id))
            self.threads[i].log_signal.connect(self.log.append)
            self.threads[i].hashrate_signal.connect(self.hash_counter)
            self.threads[i].start()

    def stop_mining(self):
        for i in self.threads:
            i.stop()
        self.threads.clear()

    def hash_counter(self, hashrate):
        self.wased_hashes.append(hashrate)
        self.pref_hashes += 1
        self.graphics.plot(list(range(1, self.pref_hashes + 1)), self.wased_hashes)


class MiningThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    hashrate_signal = QtCore.pyqtSignal(int)

    def __init__(self, username, mining_key, diff_choice, miner_id):
        super(MiningThread, self).__init__()
        self.username = username
        self.mining_key = mining_key
        self.miner_id = miner_id
        self.diff_choice = diff_choice
        self.running = True

    def run(self):
        soc = socket.socket()
        def current_time():
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            return current_time
        def fetch_pools():
            while True:
                try:
                    response = requests.get(
                        "https://server.duinocoin.com/getPool"
                    ).json()
                    NODE_ADDRESS = response["ip"]
                    NODE_PORT = response["port"]
                    return NODE_ADDRESS, NODE_PORT
                except Exception as e:
                    self.log_signal.emit(f'{current_time()} : Error retrieving mining node, retrying in 15s')
                    time.sleep(15)
        while self.running:
            try:
                self.log_signal.emit(f'{current_time()} : Searching for fastest connection to the server')
                try:
                    NODE_ADDRESS, NODE_PORT = fetch_pools()
                except Exception as e:
                    NODE_ADDRESS = "server.duinocoin.com"
                    NODE_PORT = 2813
                    self.log_signal.emit(f'{current_time()} : Using default server port and address')
                soc.connect((str(NODE_ADDRESS), int(NODE_PORT)))
                self.log_signal.emit(f'{current_time()} : Fastest connection found')
                server_version = soc.recv(100).decode()
                self.log_signal.emit(f'{current_time()} : Server Version: '+ server_version)
                while self.running:
                    if self.diff_choice == "l":
                        soc.send(bytes(
                            "JOB,"
                            + str(self.username)
                            + ",LOW,"
                            + str(self.mining_key),
                            encoding="utf8"))
                    elif self.diff_choice == "m":
                        soc.send(bytes(
                            "JOB,"
                            + str(self.username)
                            + ",MEDIUM,"
                            + str(self.mining_key),
                            encoding="utf8"))
                    else:
                        soc.send(bytes(
                            "JOB,"
                            + str(self.username)
                            + ",HIGH,"
                            + str(self.mining_key),
                            encoding="utf8"))

                    job = soc.recv(1024).decode().rstrip("\n")
                    self.log_signal.emit(job)
                    job = job.split(",")
                    difficulty = job[2]

                    hashingStartTime = time.time()
                    base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
                    temp_hash = None

                    for result in range(100 * int(difficulty) + 1):
                        temp_hash = base_hash.copy()
                        temp_hash.update(str(result).encode('ascii'))
                        ducos1 = temp_hash.hexdigest()
                        if job[1] == ducos1:
                            hashingStopTime = time.time()
                            timeDifference = hashingStopTime - hashingStartTime
                            hashrate = result / timeDifference
                            soc.send(bytes(
                                str(result)
                                + ","
                                + str(hashrate)
                                + ","
                                + str(self.miner_id),
                                encoding="utf8"))
                            feedback = soc.recv(1024).decode().rstrip("\n")
                            self.hashrate_signal.emit(int(hashrate/1000))
                            if feedback == "GOOD":
                                self.log_signal.emit(f'{current_time()} : Accepted share, {result}, Hashrate, {int(hashrate/1000)}, kH/s, Difficulty, {difficulty}')
                            elif feedback == "BAD":
                                self.log_signal.emit(f'{current_time()} : Rejected share, {result}, Hashrate, {int(hashrate/1000)}, kH/s, Difficulty, {difficulty}')
                            break
            except Exception as e:
                self.log_signal.emit(f'{current_time()} : Error occured: ' + str(e) + ", restarting in 5s.")
                time.sleep(5)
                os.execl(sys.executable, sys.executable, *sys.argv)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    GUI = GUI()
    GUI.show()
    app.setStyle("Fusion")
    sys.exit(app.exec_())