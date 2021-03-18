## Table of contents
- [Commnicating with the master server](#Commnicating-with-the-master-server)
  * [Socket API](#Socket-API)
  * [HTTP JSON API](#HTTP-JSON-API)
- [C DUCO library](#C-DUCO-library)
- [Python3 DUCO module](#Python3-DUCO-module)

## Commnicating with the master server

### Socket API

To build your own Duino-Coin apps, here's a list of of commands the master server accepts.
To start communication however, firstly you need to connect to the server. For now you have two options:
*   TCP connection (recommended) - server IP and port are static: `tcp://51.15.127.80:2811`
*   Websocket connection (through proxy - may not be available 100% of the time) - server IP and port are static: `ws://51.15.127.80:15808`

**Make sure you don't create more than 24 connections per IP address and don't make more than 24 connections in time shorter than 30 seconds.**
If you do that, the server may ban your IP for creating too much traffic and being a potential DDoS attacker.
If you happen to get banned, wait about 315 seconds to get unbanned automatically.

After connecting, the server will send its version number it's currently on (2.2).
At this point you can send `LOGI` or `REGI` request to login or register an account or `JOB,username` to receive job for mining.
To login, send `LOGI,username,password` - replace username and password with credentials. After sucessfull login server will send `OK`.
If login fails, server will send `NO,Reason of failed login`.

To register, send `REGI,username,password,email` - again, by replacing the placeholders with the respective data.
After sucessful registration, the server will send `OK`.
If the registration fails, the server will send `NO,Reason of failed registration`.

After loging-in you have access to the following commands:
*   `BALA` - Server will return balance of current user
*   `JOB` - Server will return job for mining
    *   You can also use `JOB,username` to mine without loging-in

    *   You can ask for a specific mining difficulty: `JOB,username,DIFF` (**if you don't ask for a specific difficulty, you'll get the network diff**) where diff is one of the below:
        * `AVR`     - diff      3 - used for official AVR boards mining
        * `ESP`     - diff     75 - used for official ESP boards mining
        * `ESP32`   - diff    100 - used for official ESP32 boards mining
        * `LOW`     - diff   8.5k - used for official Web Miner
        * `MEDIUM`  - diff    30k - used for lower-diff PC mining
        * `NET`     - diff   ~70k - used for PC mining - network difficulty
        * `EXTREME` - diff   950k - not used anywhere officially
    
    *   When sending the mining result, you can pass the hashrate count and the name of the miner along with rig name to display in the API, e.g.`6801,250000,My Cool Miner v4.20,House Miner` indicates that result 6801 was found, the hashrate was 250000H/s (250kH/s) and the name of the software was "My Cool Miner v4.20" with a rig named "House Miner"
        *   If hashrate is not received, server estimates it from time it took to receive share and sets `"Is estimated": "True"` in the API
        *   If software name is not received, server uses `"Software": "Unknown"` in the API
        *   If rig name is not received, server uses `"Identifier": "None"` in the API
*   `SEND,-,recipientUsername,amount` - Send funds to someone, the server will return a message about the state of the transaction
*   `GTXL,username,num` - Get last *num* of transactions involving *username* (both deposits and withdrawals)
*   `CHGP,oldPassword,newPassword` - Change password of current user
*   `WRAP,amount,tronAddress` - Wrap DUCO on Tron network (wDUCO)
*    wDUCO unwrapping protocol:
     1.  Send a Tron transaction with method `initiateWithdraw(ducoUsername,amount)`
     2.  Send a server call `UNWRAP,amount,tronAddress`

### HTTP JSON API

You can use one of the following links to get some data from Duino-Coin Server:
*   General statistics & worker API: [api.json](http://51.15.127.80/api.json) - refreshed every 5s
*   User balances API: [balances.json](http://51.15.127.80/balances.json) - refreshed every 30s
*   Transactions API: [transactions.json](http://51.15.127.80/transactions.json) - refreshed every 30s
*   Found blocks API: [foundBlocks.json](http://51.15.127.80/foundBlocks.json) - refreshed every 2m

## C DUCO library

If you want to easily access the Duino-Coin API with your C apps, you can use [libduco](https://github.com/SarahIsWeird/libduco) which is made by [@Sarah](https://github.com/SarahIsWeird/). [@ygboucherk](https://github.com/ygboucherk) is also working on one wich you can access here [duino-coin-C-lib](https://github.com/ygboucherk/duino-coin-C-lib)

## Python3 DUCO module

If you want to easily access the Duino-Coin API with your Python3 apps, [@connorhess](https://github.com/connorhess) made an official module for that here: [duco_api.py](https://github.com/revoxhere/duino-coin/blob/master/duco_api/duco_api.py) and you can find the documentation for it here: [README.md](https://github.com/revoxhere/duino-coin/blob/master/duco_api/README.md)
