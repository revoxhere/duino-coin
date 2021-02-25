<!--
*** Official Duino Coin README
*** by revox, 2019-2021
-->

<p align = "center">
  <a href="https://github.com/revoxhere/duino-coin">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" /></a><br /><br />
  <a href="https://duinocoin.com">
    <img src="https://img.shields.io/badge/duinocoin.com-555555.svg?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAmklEQVQ4T7WUQQ6AIAwEIcaX%2BALj0fdz9gM%2BxMRESQ8ktSllrciZTneX0hg6n8h5Z5pvhD%2Bu26OO17iABaCBPwEJLKFV6ZZ1GQ2HwgqlEg51ATV7GhSyXFPjBpK6UsztdQdqjSDLNYVu4JGWaQjXLh%2BmaRn5eq8ybAGRWfx3sJFNo7lw%2FxStobkcWhlKYJf1ZS1XaggPNpIv3cls33EVXWotfwAAAABJRU5ErkJggg%3D%3D" /></a>
  <a href="http://51.15.127.80/webwallet.html">
    <img src="https://img.shields.io/badge/Online Wallet-555555.svg?style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">
    <img src="https://img.shields.io/badge/whitepaper-555555.svg?style=for-the-badge&logo=Academia" /></a>
  <a href="https://app.codacy.com/manual/revoxhere/duino-coin?utm_source=github.com&utm_medium=referral&utm_content=revoxhere/duino-coin">
    <br>
  <a href="https://discord.gg/kvBkccy">
    <img src="https://img.shields.io/discord/677615191793467402.svg?color=ffa502&label=Discord&logo=Discord&style=for-the-badge" /></a>
    <img src="https://img.shields.io/codacy/grade/a995acf7cd4c4211af6da874fe549ee5?color=f68e09&style=for-the-badge" /></a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-f97606.svg?style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/2.1">
    <img src="https://img.shields.io/badge/release-2.1-fb6404.svg?style=for-the-badge" /></a>
  <!--<a href="https://bitcointalk.org/index.php?topic=5197656.msg52942015#msg52942015">
    <img src="https://img.shields.io/badge/Bitcointalk-555555.svg?style=for-the-badge&logo=bitcoin" /></a> bitcointalk thread is VERY outdated-->
</p>

<h2 align="center">Duino-Coin is a coin that can be mined with Computers, Raspberry Pis, Arduino and ESP boards and many more.</h2><br />

Key features:
*   Supported by a large number of platforms 💻
*   A friendly & growing community 👥
*   Easy to use & exchange 💱
*   Available everywhere 🌎
*   Beginner-friendly :blush:
*   Cost-effective 💰
*   Easy to mine ⛏️
*   Open-source 📚

Technical specifications:
*   Coin supply: Infinite ♾️ (before December 2020: 350k coins)
*   Premine: <5k blocks (<500coins) 😎
*   Block time: Instant ⚡
*   Decimals: 20 🔢
*   Ticker: DUCO (ᕲ)
*   Algorithms: DUCO-S1, DUCO-S1A (+more planned) supported by [Kolka system](https://github.com/revoxhere/duino-coin/blob/master/Resources/kolkasystem.png) helping reward miners fairly ♐

<h2 align="center">Get started</h2><br>

| Official Wallet | Official Miners |
:----------------:|:----------------:
[<img src="https://i.imgur.com/OEh0JxK.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/QNWkoee.png">](https://duinocoin.com/getting-started#pc)

Official getting started guides for creating an account and setting up miners on variety of devices are available <a href="https://revoxhere.github.io/duino-coin/getting-started">on the official website</a> (or <a href="http://duinoyliedtvs4zp7wtz2o7uqmv4tfcyvdlclbwr3zbez2hxwolry7ad.onion/">.onion version</a>).

<h3 align="center">Community-made software</h3><br>

**Other miners:**
*   [nonceMiner](https://github.com/colonelwatch/nonceMiner) by colonelwatch
*   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) by DarkThinking
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) by phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
*   [ducominer](https://github.com/its5Q/ducominer) by its5Q
*   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)

**Other tools:**
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz

This list will be actively updated.

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
*   TCP connection (recommended) - server IP and port are static: `tcp://51.15.127.80:2811`
*   Websocket connection (through proxy - may not be available 100% of the time) - server IP and port are static: `ws://51.15.127.80:15808`

**Make sure you don't create more than 24 connections per IP address and don't make more than 24 connections in time shorter than 30 seconds.**
If you do that, server may ban your IP for creating too much traffic and being a potential DDoS attacker.
If you happen to get banned, wait about 315 seconds to get unbanned automatically.

After connecting, the server will send version number it's currently on (2.1).
At this point you can send `LOGI` or `REGI` request to login or register an account or `JOB,username` to receive job for mining.
To login, send `LOGI,username,password` - replace username and password with credentials. After sucessfull login server will send `OK`.
If login fails, server will send `NO,Reason of failed login`.

To register, send `REGI,username,password,email` - again, by replacing words with respective data.
After sucessfull registration server will send `OK`.
If registration fails, server will send `NO,Reason of failed registration`.

After loging-in you have access to the following commands:
*   `BALA` - Server will return balance of current user
*   `JOB` - Server will return job for mining
    * You can also use `JOB,username` to mine without loging-in
    * You can ask for a specific difficulty for mining: `JOB,username,DIFF` (**if you don't ask for specific difficulty, you'll get the network diff**) where diff is one of the below:
        * `AVR`     - diff     3 - used for official AVR boards mining
        * `ESP`     - diff    75 - used for official ESP boards mining
        * `MEDIUM`  - diff    30k - used as lower-diff PC mining
        * `EXTREME` - diff   950k - for custom high performance miners
    
    *   When sending result, you can pass hashrate count and miner name along with rig name to display in the API, e.g.`6801,250000,My Cool Miner v4.20,House Miner` indicates that result 6801 was found, hashrate was 250000H/s (250kH/s) and software name was My Cool Miner v4.20 with rig named House Miner
        *   If hashrate is not received, server estimates it from time it took to receive share and sets `"Is estimated": "True"` in the API
        *   If software name is not received, server uses `"Software": "Unknown"` in the API
        *   If rig name is not received, server uses `"Identifier": "None"` in the API
*   `SEND,-,recipientUsername,amount` - Send funds to someone, server will return a message about state of the transaction
*   `GTXL,username,num` - Get last *num* of transactions involving *username* (both deposits and withdrawals)
*   `CHGP,oldPassword,newPassword` - Change password of current user
*   `WRAP,amount,tronAddress` - Wrap DUCO on Tron network (wDUCO)
*    wDUCO unwrapping protocol:
     1. Send a Tron transaction with method `initiateWithdraw(ducoUsername,amount)`
     2. Send a server call `UNWRAP,amount,tronAddress`

<h2 align="center">C DUCO library</h2><br>

If you want to easily access Duino-Coin API with your C apps, there is [libduco](https://github.com/SarahIsWeird/libduco) made by [@Sarah](https://github.com/SarahIsWeird/). [@ygboucherk](https://github.com/ygboucherk) is also working on one wich you can access here [duino-coin-C-lib](https://github.com/ygboucherk/duino-coin-C-lib)

<h2 align="center">Python3 DUCO API module</h2><br>

If you want to easily access Duino-Coin API with your Python3 apps, [@connorhess](https://github.com/connorhess) made an official module for that here: [duco_api.py](https://github.com/revoxhere/duino-coin/blob/master/duco_api/duco_api.py) and you can find the documentation for it here: [README.md](https://github.com/revoxhere/duino-coin/blob/master/duco_api/README.md)

<h2 align="center">Duino-coin for the AUR!</h2><br>

You can get the whole duino-coin bundle now on the AUR.

Just install it with your favourite AUR Helper (for example: yay):

1. Install git

```sudo pacman -S git```

2. You have to clone the yay repo.

```sudo git clone https://aur.archlinux.org/yay-git.git```

3. Get into the Folder

```cd yay-git```

4. Next, build the package using the makepkg command below.

```makepkg -si```

5. Now you can use yay to install AUR packages

```yay -S duino-coin```

6. Have fun mining!


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

*   Arduino Uno Rev3 (ATmega328p @ 16MHz 5V) - ~170 H/s - Arduino Code & Miner
*   Arduino Pro Mini (ATmega328p @ 16MHz 5V) - ~170 H/s - Arduino Code & Miner
*   NodeMCU (ESP8266 @ 80 MHz) - ~1,15 kH/s - ESP8266 Code
*   NodeMCU (ESP8266 @ 160 MHz) - ~2,15 kH/s - ESP8266 Code
*   ESP32 dual-threaded - ~13 kH/s (6 kH/s (core1) + 7 kH/s (core2)) - Multithreaded ESP32 code

Hashrate Calculators for AVR/ESP8266 platforms are available in the [Useful tools branch](https://github.com/revoxhere/duino-coin/tree/useful-tools).

<h2 align="center">Terms of usage</h2><br>
1. Duino-Coins are earned by miners with a process called mining.<br/>
2. Mining is described as using DUCO-S1 algorithm (explained in Duino-Coin Whitepaper), in which finding a correct result to a mathematical problem gives miner a reward.<br/>
3. Mining can be officially done using CPUs, AVR boards (e.g. Arduino boards), Single-board computers (e.g. Raspberry Pi boards), ESP32/8266 boards with the preffered usage of official miners (other officially allowed miners are described in the upper part of README). <br/>
4. Even though Duino-Coin aims to fairly reward all the miners, mining with GPUs, ASICs, FPGAs is not allowed due to obvious reasons.<br/>
5. Any users spotted using inappropriate/overpowered hardware can be banned from the network.<br/>
6. Banning involves blocking user from accessing his account and removing his coins.<br/>
7. Only coins earned legally are elgible for the exchange.<br/>
8. These terms of usage can change at any time without prior notice and will be expanded in the future.<br/>
9. User using Duino-Coin agrees to comply with the above rules.<br/>

<h2 align="center">Developers</h2><br>

*   **Developers:**
    *   [@revox](https://github.com/revoxhere/) (Founder) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/)
    *   [@connorhess](https://github.com/connorhess)
    *   [@JoyBed](https://github.com/JoyBed)
    *   [@LDarki](https://github.com/LDarki)
    *   [@travelmode](https://github.com/colonelwatch)
    *   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) dev)

*   **Webmaster:**
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io

*   **Contributors:**
    *   [@HGEcode](https://github.com/HGEcode)
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@Furim](https://github.com/Furim)

<h2 align="center">Special thanks</h2><br>

*   [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) for designing early logos
*   [@Tech1k](https://github.com/Tech1k) for [Beyondcoin](https://beyondcoin.io) partnership and providing [duinocoin.com](https://duinocoin.com) domain
*   [@MrKris7100](https://github.com/MrKris7100) for help with implementing SHA1 algorithm
*   [@daknuett](https://github.com/daknuett) for help with Arduino SHA1 library

<hr>

Project Link: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
