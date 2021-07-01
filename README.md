## Table of contents
- [Commnicating with the master server](#Commnicating-with-the-master-server)
  * [Socket API](#Socket-API)
  * [HTTP JSON API](#HTTP-JSON-API)
  * [REST JSON API](#REST-JSON-API)
- [C DUCO library](#C-DUCO-library)
- [Python3 DUCO module](#Python3-DUCO-module)
- [Branding colors](#Branding)

## Commnicating with the master server

### Socket API

To build your own Duino-Coin apps, here's a list of of commands the master server accepts.
To start communication however, firstly you need to connect to the server. For now you have two options:
*   TCP connection
    * `tcp://51.15.127.80:2811` - Legacy port
    * `tcp://51.15.127.80:2812` - Port preferred for Wallets and other miners
    * `tcp://51.15.127.80:2813` - Port preferred for AVR mining
    * `tcp://51.15.127.80:2814` - Port preferred for PC mining
    * `tcp://51.15.127.80:2815` - Port preferred for ESP mining
    * `tcp://51.15.127.80:2816` - Port preferred for AVR mining 2
    * `tcp://51.15.127.80:2817` - Port preferred for PC mining 2
    * Note: you can also use `server.duinocoin.com` instead of `51.15.127.80`
*   Secure Websocket sonnection (SSL required)
    *  `wss://server.duinocoin.com:14808` - All commands available (proxied to one of the TCP ports)
    *  `wss://server.duinocoin.com:15808` - Only wallet functions available (proxied to separate Wallet node)

**Make sure you don't create more more than 50 connections in time shorter than 30 seconds.**
If you do that, the server may ban your IP for creating too much traffic and being a potential DDoS attacker.

After connecting, the server will send its version number it's currently on (2.4).
At this point you can send `LOGI` or `REGI` request to login or register an account or `JOB,username` to receive job for mining.
To login, send `LOGI,username,password` - replace username and password with credentials. After sucessfull login server will send `OK`.
If login fails, server will send `NO,Reason of failed login`.

To register, send `REGI,username,password,email` - again, by replacing the placeholders with the respective data.
After sucessful registration, the server will send `OK`.
If the registration fails, the server will send `NO,Reason of failed registration`.

After loging-in you have access to the following commands:
*   `PING` - Server will return "Pong!" message ASAP 
*   `BALA` - Server will return balance of current user
*   `ESTP,username` - Server will return the 24h estimated profits of user
*   `UEXI,username` - Server will check if the user is registered and return `NO,User is not registered` or `OK,User is registered`
*   `JOB,username` (or `JOBXX,username` for XXHASH) - Server will return job for mining using DUCO-S1 (-S1A)
    *   You can ask for a specific mining difficulty: `JOB,username,DIFF` (if you don't ask for a specific difficulty, the network diff will be given) where diff is one of the below:
        * `AVR`     - diff      6 - used for mining on Arduino, AVR boards
        * `ARM`     - diff    500 - not used anywhere officially yet
        * `DUE`     - diff   1000 - planned for mining on Arduino Due boards
        * `ESP8266` - diff   1500 - used for mining on ESP8266 boards 
        * `ESP32`   - diff   2400 - used for mining on ESP32 boards
        * `LOW`     - diff   7.5k - used for mining on Web Miner, RPis, PC
        * `MEDIUM`  - diff    75k - used for mining on PC
        * `NET`     - diff  ~500k - used for mining on PC (network difficulty)
        * `EXTREME` - diff    1M+ - not used anywhere officially yet
    *   When sending the mining result, you can pass the hashrate count and the name of the miner along with rig name to display in the API, e.g.`6801,250000,My Cool Miner v4.20,House Miner` indicates that result 6801 was found, the hashrate was 250000H/s (250kH/s) and the name of the software was "My Cool Miner v4.20" with a rig named "House Miner"
        *   If hashrate is not received, server estimates it from time it took to receive share and sets `"Is estimated": "True"` in the API
        *   If software name is not received, server uses `"Software": "Unknown"` in the API
        *   If rig name is not received, server uses `"Identifier": "None"` in the API
*   `JOBXX` - Server will return job for mining using XXHASH algorithm; documentation is the same as with DUCO-S1 job protocol
*   `SEND,message,recipients_username,amount` - Send funds to someone, the server will return a message about the state of the transaction
*   `GTXL,username,num` - Get last *num* of transactions involving *username* (both deposits and withdrawals)
*   `CHGP,oldPassword,newPassword` - Change password of current user
*   `WRAP,amount,tronAddress` - Wrap DUCO on Tron network (wDUCO)
*    wDUCO unwrapping:
     1.  Send a Tron transaction with method `initiateWithdraw(duco_username,amount)`
     2.  Send a server call `UNWRAP,amount,tron_address`

### HTTP JSON API

You can use one of the following links to get some data from Duino-Coin Server:
*   General statistics & worker API refreshed every 5s
    *   HTTPS: `https://server.duinocoin.com/api.json`
    *   HTTP: `http://51.15.127.80/api.json`
    *   Small part of the response:
        ```JSON
         {
            "_Duino-Coin Public master server JSON API": "https://github.com/revoxhere/duino-coin",
            "Server version": 2.2,
            "Active connections": 1039,
            "Open threads": 13,
            "Server CPU usage": 61.0,
            "Server RAM usage": 9.73,
            "Last update": "24/03/2021 12:45 (UTC)"
         }
        ```

*   User balances API refreshed every 10s
    *   HTTPS: `https://server.duinocoin.com/balances.json`
    *   HTTP: `http://51.15.127.80/balances.json`
    *   Small part of the response:
        ```JSON
         {
            "magicsky": "3112.6 DUCO",
            "lulkas": "3047.01 DUCO",
            "revox": "2884.1194 DUCO",
            "ethux": "2812.2677 DUCO",
            "metal93": "2685.5714 DUCO"
         }
        ```
        Note: only users who have account balance greater than 0 are listed in this API.
        
*   Transactions API refreshed every 10s
    *   HTTPS: `https://server.duinocoin.com/transactions.json`
    *   HTTP: `http://51.15.127.80/transactions.json`
    *   Small part of the response:
        ```JSON
         "8bba65e9c2b8371f2dfd686a4465a530d8985861": {
             "Date": "23/01/2021",
             "Time": "11:23:41",
             "Sender": "revox",
             "Recipient": "ATAR4XY",
             "Amount": 2.0
          }
        ```
        
*   Found blocks API refreshed every 2m
    *   HTTPS: `https://server.duinocoin.com/foundBlocks.json`
    *   HTTP: `http://51.15.127.80/foundBlocks.json`
    *   Small part of the response:
        ```JSON
         "e39c8c290b3478d3d5c21a6caffd44d6799e0ae9": {
            "Date": "09/02/2021",
            "Time": "08:28:40",
            "Finder": "revox",
            "Amount generated": 7.00026306
         }
        ```
        
### REST JSON API

Documentation for DUCO REST api is available here: [duco-rest-api](https://github.com/dansinclair25/duco-rest-api).
To access these functions, add port 5000 to the URL: `https://server.duinocoin.com:5000/query`.

## C DUCO library

If you want to easily access the Duino-Coin API with your C apps, you can use [libduco](https://github.com/SarahIsWeird/libduco) which is made by [@Sarah](https://github.com/SarahIsWeird/). [@ygboucherk](https://github.com/ygboucherk) is also working on one wich you can access here [duino-coin-C-lib](https://github.com/ygboucherk/duino-coin-C-lib)

## Python3 DUCO module

If you want to easily access the Duino-Coin API with your Python3 apps, [@connorhess](https://github.com/connorhess) made an official module for that here: [duco_api](https://github.com/revoxhere/duino-coin/tree/useful-tools/duco_api).

## Branding

We suggest using these colors in creating DUCO-Related apps:

### Branding colors

* White accent: `#fafafa` ![#fafafa](https://via.placeholder.com/15/fafafa/000000?text=+)
* Orange accent: `#ff4112` ![#ff4112](https://via.placeholder.com/15/ff4112/000000?text=+)
* Sun yellow accent: `#ffb412` ![#ffb412](https://via.placeholder.com/15/ffb412/000000?text=+)
* Magenta accent: `#f31291` ![#f31291](https://via.placeholder.com/15/f31291/000000?text=+)
* Dark accent: `#121212` ![#121212](https://via.placeholder.com/15/121212/000000?text=+)

Gradient variations of the colors above are a welcome touch.

#### GUI colors
* Background: `#121212` (Dark) ![#121212](https://via.placeholder.com/15/121212/000000?text=+) or `#fffdee` (Light) ![#fffdee](https://via.placeholder.com/15/fffdee/000000?text=+)
* Font color: `#fffdee` (Dark) ![#fffdee](https://via.placeholder.com/15/fffdee/000000?text=+) or `#0f0f0f` (Light) ![#0f0f0f](https://via.placeholder.com/15/0f0f0f/000000?text=+)

### Icons

<img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png" width="128px"> <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco-alt.png" width="128px"> <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco_square.png" width="128px">
<img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/WebMiner.png" width="128px"> <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/PCMiner.png" width="128px"> <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/AVRMiner.png" width="128px">
<img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png" width="512px">

More resources available in the [Resources folder](https://github.com/revoxhere/duino-coin/tree/master/Resources)
