<!--
*** Official Duino-Coin APIs README
*** by revoxhere, 2021
-->

<a href="https://duinocoin.com">
  <img src="api.png" width="215px" align="right"/>
</a>


<a href="https://duinocoin.com">
  <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" width="430px"/>
</a>

## Official docs for developers

This branch of the Duino-Coin repository contains documentation for public API calls that can be useful for anyone trying to make their own Duino-related app.

### Table of contents

- Commnicating with the master server
  - Over a [TCP connection](#TCP-connection)
  - Over a [WebSocket connecton](#WebSocket-connection)
  - List of [server commands](#Server-commands)
- Duino-Coin [REST API](#REST-API)
- Duino-Coin [JSON user data](#JSON-data)
- Icons, colors - [branding](#Branding)

##

### TCP connection

Before starting, make sure your app doesn't create more more than 50 connections in time shorter than 30 seconds,
if you do that, the server may ban your IP address for creating too much traffic.

To communicate with the master server, create a simple tcp connection to one of the following addresses:

* `51.15.127.80:2811`
* `51.15.127.80:2812`
* `51.15.127.80:2813`
* `51.15.127.80:2814`
* `51.15.127.80:2815`

Note: you can also use `server.duinocoin.com` instead of `51.15.127.80`

### WebSocket connection

To communicate with the master server, create a secure websocket (wss) connection to one of the following addresses:

*  `wss://server.duinocoin.com:14808` - Proxied to PulsePool - **only mining commands accepted**
*  `wss://server.duinocoin.com:15808`

### Server commands

Right after connecting, the server will send its version, e.g. `2.4`.

After connecting you can send `LOGI,username,password` request to login or `REGI,username,password,email` to request registration of a new account (see below).<br>
You can also send `JOB` request to receive job for mining.

#### Auth

To login, send `LOGI,username,password` - replace username and password with credentials.<br>
After sucessfull login server will send `OK`.<br>
If login fails, server will send `NO,reason of failed login`.

#### Registration

To register, send `REGI,username,password,email` - replace the placeholders with the respective data.<br>
After sucessful registration, the server will send `OK`.<br>
If the registration fails, the server will send `NO,reason of failed registration`.

### Other commands

These commands are only available after a successfull login:

#### Ping

After sending `PING` the srver will return `Pong!` as fast as it can

#### User balance

After sending `BALA` the server will return balance of the current logged-in user

#### User exists

After sending `UEXI,username` the server will check if the user is registered.<br>
If this wallet is taken, the reply will be `NO,User is not registered`<br>
If not, the response will be `OK,User is registered`.<br>

#### DUCO-S1 Mining

After sending `JOB,username` (or `JOBXX,username` for XXHASH) the server will return job for mining using DUCO-S1.<br>
You can ask for a specific **start** difficulty: `JOB,username,diff` where diff is one of the below:
* `LOW` - used for mining on Web Miner, RPis, PC
* `MEDIUM` - used for mining on PC
* `NET` - used for mining on PC (network difficulty)
* `EXTREME` - not used anywhere officially

When sending the mining result you can pass the hashrate count and the name of the miner along with rig name to display in the API.<br>
Example: sending `6801,250000,My Cool Miner v4.20,House Miner` indicates that result 6801 was found, the hashrate was 250000H/s (250kH/s)
and the name of the software was "My Cool Miner v4.20" with a rig named "House Miner".<br>

If hashrate is not received, server estimates it from time it took to receive share and sets `"Is estimated": "True"` in the API
If software name is not received, server uses `"Software": "Unknown"` in the API
If rig name is not received, server uses `"Identifier": "None"` in the API

#### XXHASH Mining

After sending `JOBXX` the server will return job for mining using XXHASH algorithm.<br>
The documentation is the same as with the DUCO-S1 job protocol but only `XXHASH` difficulty is available.

#### Transfer funds

After sending `SEND,message,recipients_username,amount` the server will attempt to send funds to `recipients_username`.<br>
The server will return a message about the state of the transaction.<br>
A successfull transaction will return `OK,Successfully transferred funds,transaction_hash` where transaction_hash is the unique hash of each transaction that
can be checked in the explorer.

#### Last transactions

After sending `GTXL,username,num` the server will return last `num` of transactions involving `username` (both deposits and withdrawals) in JSON format.

#### Password change 

After sending `CHGP,oldPassword,newPassword` the server will change password of current user.<br>

#### wDUCO wrapping

After sending `WRAP,amount,tronAddress` the server will wrap DUCO on the Tron network (transfer to wDUCO).

#### wDUCO unwrapping

1. Send a Tron transaction - e.g. `initiateWithdraw(duco_username, amount)`
2. Send `UNWRAP,amount,tron_address` to the server

##

### REST API

Documentation for the DUCO REST api is available here: [duco-rest-api](https://github.com/revoxhere/duco-rest-api).
To access these functions, just add the query URL after the server address: `https://server.duinocoin.com/<query>`.

##

### JSON data

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
        
*   Found blocks API refreshed every 15s
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

##

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
