<!--
*** Official Duino Coin README
*** by revox, 2019-2020
-->

<p align = "center">
  <a href="https://github.com/revoxhere/duino-coin">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" /></a><br /><br />
  <a href="https://duinocoin.com">
    <img src="https://img.shields.io/badge/duinocoin.com-555555.svg?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAmklEQVQ4T7WUQQ6AIAwEIcaX%2BALj0fdz9gM%2BxMRESQ8ktSllrciZTneX0hg6n8h5Z5pvhD%2Bu26OO17iABaCBPwEJLKFV6ZZ1GQ2HwgqlEg51ATV7GhSyXFPjBpK6UsztdQdqjSDLNYVu4JGWaQjXLh%2BmaRn5eq8ybAGRWfx3sJFNo7lw%2FxStobkcWhlKYJf1ZS1XaggPNpIv3cls33EVXWotfwAAAABJRU5ErkJggg%3D%3D" /></a>
  <a href="http://51.15.127.80/webwallet.html">
    <img src="https://img.shields.io/badge/Online Wallet-555555.svg?style=for-the-badge" /></a>
  <a href="https://duinocoin.com/whitepaper">
    <img src="https://img.shields.io/badge/whitepaper-555555.svg?style=for-the-badge&logo=Academia" /></a>
  <a href="https://app.codacy.com/manual/revoxhere/duino-coin?utm_source=github.com&utm_medium=referral&utm_content=revoxhere/duino-coin">
    <br>
  <a href="https://discord.gg/kvBkccy">
    <img src="https://img.shields.io/discord/677615191793467402.svg?color=ffa502&label=Discord&logo=Discord&style=for-the-badge" /></a>
    <img src="https://img.shields.io/codacy/grade/a995acf7cd4c4211af6da874fe549ee5?color=f68e09&style=for-the-badge" /></a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-f97606.svg?style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/1.7">
    <img src="https://img.shields.io/badge/release-1.7-fb6404.svg?style=for-the-badge" /></a>
  <a href="https://bitcointalk.org/index.php?topic=5197656.msg52942015#msg52942015">
    <img src="https://img.shields.io/badge/Bitcointalk-555555.svg?style=for-the-badge&logo=bitcoin" /></a>
</p>

<h2 align="center">Duino-Coin is a cryptocurrency that can be mined with AVR boards.</h2><br />

Key features:
*   Supported by large number of platforms
*   Friendly & growing community
*   Easy to use & exchange
*   Available everywhere
*   Cost-effective
*   Open-source
*   Easy to mine!

Technical specifications:
*   Coin supply: ~ 350k
*   Block supply: ~ 35 million
*   Premine: ~ 5k blocks
*   Block time: Instant ⚡
*   Ticker: DUCO (ᕲ)
*   Algorithms: DUCO-S1, DUCO-S1A
*   Original [Kolka system](https://github.com/revoxhere/duino-coin/blob/master/Resources/kolkasystem.png) helping reward miners fairly

<h2 align="center">Get started</h2><br>

| Official Wallet | Official Miners |
:----------------:|:----------------:
[<img src="https://i.imgur.com/JGhXFCW.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/WLVDljU.png">](https://duinocoin.com/getting-started#pc)

Official getting started guides for creating an account and setting up miners on variety of devices are available <a href="https://revoxhere.github.io/duino-coin/getting-started">on the official website</a> (or <a href="http://duinoyliedtvs4zp7wtz2o7uqmv4tfcyvdlclbwr3zbez2hxwolry7ad.onion/">.onion version</a>).

<h3 align="center">Community-made software</h3><br>

**Miners:**
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) by phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
*   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners) by various authors
*   [Duino DogeRock GUI Miner](https://github.com/DogeRock/Duino-Coin-Gui-Miner) by DogeRock

**Other tools:**
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz
*   [Duino DogeRock GUI Wallet](https://github.com/DogeRock/Duino-Coin-Gui-Wallet) by DogeRock
*   [Duino DogeRock CLI Wallet](https://github.com/DogeRock/DogeRock-Duino-Coin-cmd-line-wallet) by DogeRock

This list will be actively updated

<h2 align="center">Contributing</h2><br>

Contributions are what make the open source community such an amazing place to be learn, inspire, and create.
Any contributions you make are greatly appreciated.

*   Fork the Project
*   Create your feature branch
*   Commit your changes
*   Make sure everything works as intended
*   Open a pull request

<h2 align="center">Master server API</h2><br>

To build your own Duino-Coin apps, here's a list of of commands the master server accepts.
To start communication however, firstly you need to connect to the server. For now you have two options:
*   TCP connection (recommended) - server IP and port are now static (but can change) and can be found [here](https://github.com/revoxhere/duino-coin/blob/gh-pages/serverip.txt)
*   Websocket connection (through proxy - may not be available 100% of the time) - server IP and port are static and are `ws://51.15.127.80:15808`

After connecting, the server will send version number it's currently on (1.7).
At this point you can send `LOGI` or `REGI` request to login or register an account or `JOB,username` to receive job for mining.
To login, send `LOGI,username,password` - replace username and password with credentials. After sucessfull login server will send `OK`.
If login fails, server will send `NO,Reason of failed login`.

To register, send `REGI,username,password,email` - again, by replacing words with respective data.
After sucessfull registration server will send `OK`.
If registration fails, server will send `NO,Reason of failed registration`.

After loging-in you have access to the following commands:
*   `BALA` - Server will return balance of current user
*   `JOB` - Server will return job for mining - you can also use `JOB,username` to mine without loging-in
    *   When sending result, you can pass hashrate count and miner name to display in the API, e.g.(6801,250000,My Cool Miner v4.20) indicates that result 6801 was found, hashrate was 250000H/S (250kH/s) and software name was My Cool Miner v4.20
        *   If hashrate is not received, server estimates it from time it took to receive share and sets `"Is estimated": "True"` in the API
        *   If software name is not received, server uses `"Software": "Unknown"` in the API
*   `SEND,-,recipientUsername,amount` - Send funds to someone, server will return a message about state of the transaction
*   `CHGP,oldPassword,newPassword` - Change password of current user

<h2 align="center">Python DUCO API module</h2><br>

To build your own Duino-Coin apps, here's a some documentation for the python module.

<h3>Getting Started</h3>

```python
import duco_api
```

First you need to initialize the connection to the server

```python
api_connection = duco_api.api_actions() #creates the api connection instance
```

The next step is to Login/Register <i>*Note: login and register do not require you to init but they close the connection after use*</i>
<h4>Login</h4>

```python
api_connection.login(username="username", password="password")
```

<h4>Register</h4>

```python
api_connection.register(username="username", password="password", email="user@example.com")
```

<h3>Functions</h3>
These functions require user being loged-in.

<h4>Balance</h4>
Gets the current balance of the logged-in user

```python
api_connection.balance() # takes no args
```

<h4>Transfer</h4>
Transfers Duco from logged-in user to the specified username

```python
api_connection.transfer(recipient_username='test_user1', amount=1)
```

<h4>reset password</h4>
Resets the password of the logged-in user

```python
api_connection.reset_pass(old_password='123', new_password='abc')
```

<h3>Other Functions</h3>
Use of this functions does not require being loged-in.

<h4>Get Duco Price</h4>
starts a thread with a loop that runs every 15 seconds

```python
duco_api.GetDucoPrice() # access the value by using the global variable <ducofiat>
```

<h4>Example API script</h4>

```python
import duco_api

api_connection = duco_api.api_actions()

api_connection.login(username='YourUsername', password='YourPassword')

current_balance = api_connection.balance()
print(current_balance)

api_connection.close()
```

<h2 align="center">License</h2><br>

Duino-Coin is mostly distributed under the MIT License. See `LICENSE` file for more information.

Major frameworks used by Duino-Coin:
*   [cryptosuite2](https://github.com/daknuett/cryptosuite2) - Arduino SHA1 hashing
*   [Hash.h library](https://github.com/esp8266/Arduino/blob/master/libraries/Hash/src/Hash.h) - ESP8266 SHA1 hashing
*   [pySerial](https://pythonhosted.org/pyserial/) - Arduino and Python communication
*   [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) - creating executables
*   [PyGithub](https://github.com/PyGithub/PyGithub) - pool statistics API integration
*   [m-cpuminer-v2](https://github.com/m-pays/m-cpuminer-v2/) - Developer donation

<h2 align="center">Officially tested devices</h2><br>

*   Arduino Uno Rev3 (ATmega328p @ 16MHz 5V) - Unkown Hashrate - Arduino Code & Miner
*   Arduino Pro Mini (ATmega328p @ 16MHz 5V) - 150 H/s - Arduino Code & Miner
*   NodeMCU (ESP8266 @ 80 MHz) - 1,15 kH/s - ESP Code
*   NodeMCU (ESP8266 @ 160 MHz) - 2,15 kH/s - ESP Code

Hashrate Calculators for AVR/ESP platforms are available in the [Useful tools branch](https://github.com/revoxhere/duino-coin/tree/useful-tools).

<h2 align="center">Developers</h2><br>

*   **Lead developers:**
    *   [@revox](https://github.com/revoxhere/) - [YouTube](https://youtube.com/c/reVox96) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/)

*   **Developers:**
    *   [@kyngs](https://github.com/kyngs)

*   **Contributors:**
    *   [@connorhess](https://github.com/connorhess)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@IdotMaster1](https://github.com/IdotMaster1)
    *   [@JoyBed](https://github.com/JoyBed)
    *   [@Furim](https://github.com/Furim) - [YouTube](https://www.youtube.com/channel/UCKxFuOCalYxlQoS7R6zilRQ)

<h2 align="center">Special thanks</h2><br>

*   [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) for designing logos
*   [@Tech1k](https://github.com/Tech1k) from [Beyondcoin](https://beyondcoin.io) for providing [duinocoin.com](https://duinocoin.com) domain
*   [@MrKris7100](https://github.com/MrKris7100) - [YouTube](https://www.youtube.com/user/MrKris7100) for help with implementing SHA1 algorithm
*   [@daknuett](https://github.com/daknuett) for help with Arduino SHA1 library

<h2 align="center">Donate</h2><br>

If you want to support the project, visit [Donate page](https://revoxhere.github.io/duino-coin/donate) on our website.

<hr>

Project Link: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
