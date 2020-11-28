<!--
*** Official Duino Coin README
*** by revox, 2019-2020
-->

<p align = "center">
  <a href="https://github.com/revoxhere/duino-coin">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" /></a><br /><br />
  <a href="https://duinocoin.com">
    <img src="https://img.shields.io/badge/duinocoin.com-555555.svg?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAmklEQVQ4T7WUQQ6AIAwEIcaX%2BALj0fdz9gM%2BxMRESQ8ktSllrciZTneX0hg6n8h5Z5pvhD%2Bu26OO17iABaCBPwEJLKFV6ZZ1GQ2HwgqlEg51ATV7GhSyXFPjBpK6UsztdQdqjSDLNYVu4JGWaQjXLh%2BmaRn5eq8ybAGRWfx3sJFNo7lw%2FxStobkcWhlKYJf1ZS1XaggPNpIv3cls33EVXWotfwAAAABJRU5ErkJggg%3D%3D" /></a>
  <a href="http://163.172.179.54/webwallet.html">
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
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/1.6">
    <img src="https://img.shields.io/badge/release-1.6-fb6404.svg?style=for-the-badge" /></a>
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

<h2 align="center">Get started</h2><br>

| Official Wallet | Official Miners |
:----------------:|:----------------:
[<img src="https://media.discordapp.net/attachments/691626288376709140/719828194319925298/WALLET.gif">](https://duinocoin.com/getting-started#register)  |  [<img src="https://media.discordapp.net/attachments/691626288376709140/719828166478266398/MINER.gif">](https://duinocoin.com/getting-started#pc)

Official getting started guides for creating an account and setting up miners on variety of devices are available <a href="https://revoxhere.github.io/duino-coin/getting-started">on the official website</a>.

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
*   Websocket connection (through proxy - may not be available 100% of the time) - server IP and port are static and are `ws://163.172.179.54:15808`

After connecting, the server will send version number it's currently on (1.6).
At this point you can send `LOGI` or `REGI` request to login or register an account or `JOB,username` to receive job for mining.
To login, send `LOGI,username,password` - replace username and password with credentials. After sucessfull login server will send `OK`.
If login fails, server will send `NO,Reason of failed login`.

To register, send `REGI,username,password,email` - again, by replacing words with respective data.
After sucessfull registration server will send `OK`.
If registration fails, server will send `NO,Reason of failed registration`.

After loging-in you have access to the following commands:
*   `BALA` - Server will return balance of current user
*   `JOB` - Server will return job for mining - you can also use `JOB,username` to mine without loging-in
*   `SEND,-,recipientUsername,amount` - Send funds to someone, server will return a message about state of the transaction
*   `CHGP,oldPassword,newPassword` - Change password of current user
*   `FROM,Program Name,username,Other info` - Send metrics data to the server
*   `STAT` - Server will return rank and e-mail of the user

<h2 align="center">Duco API python Module</h2><br>

To build your own Duino-Coin apps, here's a some documentation for the python module.

<h3>Getting Started</h3>

```
import duco_api
```

First you need to initialize the connection to the server

```
duco_api.init_socket() #returns an instance of the socket connection but also makes it global
```

The next step is to Login/Register <i>*Note: login and register do not require you to init but they close the connection after use*</i>
<h4>Login</h4>

```
duco_api.login(username="username", password="password")
```

<h4>Register</h4>

```
duco_api.register(username="username", password="password", email="user@example.com")
```

<h3>Functions <i>*Requires Login*</i></h3>
<h4>Balance</h4>
Gets the current balance of the logged-in user

```
duco_api.balance() # takes no args
```

<h4>Transfer</h4>
Transfers Duco from logged-in user to the specified username

```
duco_api.transfer(recipient_username='test_user1', amount=1)
```

<h4>reset password</h4>
Resets the password of the logged-in user

```
duco_api.reset_pass(old_password='123', new_password='abc')
```

<h3>Other Functions <i>*Does NOT Require Login*</i></h3>
<h4>Get Duco Price</h4>
starts a thread with a loop that runs every 15 seconds


```
duco_api.GetDucoPrice() # access the value by using the global variable <ducofiat>
```

<h3>Example</h3>

```
import duco_api

sock = duco_api.init_socket()

duco_api.login(username='YourUsername', password='YourPassword')

current_balance = duco_api.balance()
print(current_balance)

sock.close()
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

* Arduino Pro Mini (ATmega328p @ 16MHz 5V) - 150 H/s - Arduino Code & Miner
* NodeMCU (ESP8266 @ 80 MHz) - 1,15 kH/s - ESP Code
* NodeMCU (ESP8266 @ 160 MHz) - 2,15 kH/s - ESP Code

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
