<!--
*** Official Duino Coin README
*** by revox, 2019-2021
-->

<p align = "center">
  <a href="https://github.com/revoxhere/duino-coin">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" /></a><br /><br />
  <a href="https://duinocoin.com">
    <img src="https://img.shields.io/badge/duinocoin.com-555555.svg?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAmklEQVQ4T7WUQQ6AIAwEIcaX%2BALj0fdz9gM%2BxMRESQ8ktSllrciZTneX0hg6n8h5Z5pvhD%2Bu26OO17iABaCBPwEJLKFV6ZZ1GQ2HwgqlEg51ATV7GhSyXFPjBpK6UsztdQdqjSDLNYVu4JGWaQjXLh%2BmaRn5eq8ybAGRWfx3sJFNo7lw%2FxStobkcWhlKYJf1ZS1XaggPNpIv3cls33EVXWotfwAAAABJRU5ErkJggg%3D%3D" /></a>
  <a href="https://wallet.duinocoin.com">
    <img src="https://img.shields.io/badge/Online Wallet-555555.svg?style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">
    <img src="https://img.shields.io/badge/whitepaper-555555.svg?style=for-the-badge&logo=Academia" /></a>
  <a href="https://app.codacy.com/manual/revoxhere/duino-coin?utm_source=github.com&utm_medium=referral&utm_content=revoxhere/duino-coin">
  <a href="https://youtu.be/bFnCdqMke34">
    <img src="https://img.shields.io/badge/YouTube_Video-Watch-fb6404.svg?style=for-the-badge&logo=Youtube" /></a>
    <br>
  <a href="https://discord.gg/kvBkccy">
    <img src="https://img.shields.io/discord/677615191793467402.svg?color=ffa502&label=Discord&logo=Discord&style=for-the-badge" /></a>
    <img src="https://img.shields.io/codacy/grade/a995acf7cd4c4211af6da874fe549ee5?color=f68e09&style=for-the-badge" /></a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-f97606.svg?style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/2.3">
    <img src="https://img.shields.io/badge/release-2.3-fb6404.svg?style=for-the-badge" /></a>
</p>

<h2 align="center">Duino-Coin is a coin that can be mined with Computers, Raspberry Pis, Arduinos, ESP boards and many more.</h2><br />

<table align="center">
  <tr>
    <th>Key features</th>
    <th>Technical specifications</th>
  </tr>
  <tr>
    <td>
      💻 Supported by a large number of platforms<br>
      👥 A friendly & growing community<br>
      💱 Easy to use & exchange<br>
      🌎 Available everywhere<br>
      :new: Fully original project<br>
      :blush: Beginner-friendly<br>
      💰 Cost-effective<br>
      ⛏️ Easy to mine<br>
      📚 Open-source<br>
    </td>
    <td>
      ♾️ Coin supply: Infinite (before December 2020: 350k coins)<br>
      😎 Premine: <5k blocks (<500 coins)<br>
      ⚡ Transaction time: Instant<br>
      🔢 Decimals: up to 20<br>
      🔤 Ticker: DUCO (ᕲ)<br>
      ⚒️ Algorithms: DUCO-S1, DUCO-S1A, XXHASH +more planned<br>
      ♐ Rewards: supported by "Kolka system" helping to reward miners fairly<br>
    </td>
  </tr>
</table>

<h2 align="center">Get started</h2><br>

| Official Wallet | Official Miners |
:----------------:|:----------------:
[<img src="https://i.imgur.com/OEh0JxK.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/QNWkoee.png">](https://duinocoin.com/getting-started#pc)

#### Official getting started guides for creating an account and setting up miners on variety of devices are available <a href="https://revoxhere.github.io/duino-coin/getting-started">on the official website</a>.

<h3 align="center">Installing Duino-Coin</h2><br>

The easiest way to get started with Duino-Coin is to download [the latest release](https://github.com/revoxhere/duino-coin/releases/latest) for your OS.<br>
After downloading, unzip it and launch the desired program.<br>
There are no dependencies required.

<hr>

If you want to run the programs from source, you may need to install some dependencies. Here's how to do it on debian-based distros(e.g. Ubuntu, Debian, raspian):
```BASH
sudo apt install python3 python3-pip git
git clone https://github.com/revoxhere/duino-coin
cd duino-coin
python3 -m pip install -r requirements.txt
```
If you are on Windows, download [Python 3](https://www.python.org/downloads/), then [our repository](https://github.com/revoxhere/duino-coin/archive/master.zip), extract it and open the folder in command prompt. In CMD, type:
```BASH
py -m pip install -r requirements.txt
```
After doing this, you are good to go with launching the software (e.g. `python3 PC_Miner.py` OR `py PC_Miner.py`). 

<hr>

You can also get the whole Duino-Coin bundle on the AUR - just install it with your favourite AUR Helper:

```BASH
sudo pacman -S git
sudo git clone https://aur.archlinux.org/yay-git.git
cd yay-git
makepkg -si
yay -S duino-coin
```

Duino-Coin AUR bundle is maintained by [PhereloHD](https://github.com/PhereloHD).

<h3 align="center">Community-made software</h3><br>

**Other miners known to work with Duino-Coin:**
*   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner)
*   [DUCO Miner for Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) by PhereloHD & HGEpro
*   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) by Alicia426
*   [nonceMiner](https://github.com/colonelwatch/nonceMiner) by colonelwatch
*   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) by DarkThinking
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) by phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
*   [ducominer](https://github.com/its5Q/ducominer) by its5Q
*   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
    *   [NodeJS Miner](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners/NodeJS_Miner) by Bilaboz
    *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) by revox
    *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) by revox
    *   [Minimal Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) by revox
    *   [(Old) Multithreaded Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Multithreaded_PC_Miner.py) by Bilaboz

**Other tools:**
*   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) by LDarki
*   [DUCO Monitor](https://siunus.github.io/duco-monitor/) by siunus
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
<!--*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz (DEPRECATED) -->

This list will be actively updated. If you want to add software to this list, submit a PR or contact one of the developers.

<h3 align="center">wDUCO tutorial</h3><br>

wDUCO is DUCO wrapped on the Tron network. Currently there aren't many uses for it, other than just storing funds in external wallet or exchanging wDUCO to another token on JustSwap. Before doing anything, make sure you have `tronpy` (tron lib) and `cryptography` (for encrypting private key) modules for python3 installed.

### Configuring wDUCO Wrapper in the GUI Wallet

1. Open the DUCO GUI (desktop) Wallet
2. Open the settings tab
3. Click the **Configure Wrapper** button
4. Input your private key (for example your tronlink key) and set a passphrase used for encrypting it

### Configuring wDUCO Wrapper in the CLI Wallet

1. Open the DUCO CLI (console) Wallet
2. Start wrapper configuration tool by typing `wrapperconf`
4. Input your private key (for example your tronlink key) and set a passphrase used for encrypting it

### Wrapping DUCO

After setting up the wrapper in one of the two wallets, you can wrap DUCOs (convert them to wDUCO).

1. Open the Wallet
2. Type `wrap` to start the wrapping process OR click **Wrap DUCO** button
3. Follow the instructions displayed by the wallet

### Unwrapping DUCO

After setting up the wrapper in one of the two wallets, you can unwrap wDUCOs (convert them to DUCO).
**Note: make sure you have some TRX in your wallet for the fees!** Unwraping will use ~5 TRX (~0.5 USD) as fees.

1. Open the Wallet
2. Type `unwrap` to start the wrapping process OR click **Unwrap DUCO** button
3. Follow the instructions displayed by the wallet

<h2 align="center">Development</h2><br>

Contributions are what make the open source community such an amazing place to be learn, inspire, and create.
Any contributions you make to the Duino-Coin project are greatly appreciated.

How to help?

*   Fork the Project
*   Create your feature branch
*   Commit your changes
*   Make sure everything works as intended
*   Open a pull request

Server source code, documentation for API calls and official libraries for developing your own apps for Duino-Coin are available in the [useful tools](https://github.com/revoxhere/duino-coin/tree/useful-tools) branch. 

<h2 align="center">Some of the officially tested devices</h2><br>

*   Arduino Pro Mini / Uno / Nano (ATmega328p @ 16 MHz 5V): ~170 H/s
*   NodeMCU (ESP8266 @ 160 MHz): ~2.6 kH/s (~1.6 kH/s at 80 MHz clock)
*   ESP32 (dual-threaded): ~13 kH/s (6 kH/s (core1) and 7 kH/s (core2)) (WIP)

Hashrate Calculators for AVR/ESP8266 platforms are available in the [Useful tools branch](https://github.com/revoxhere/duino-coin/tree/useful-tools).

<h2 align="center">License</h2><br>

Duino-Coin is mostly distributed under the MIT License. See `LICENSE` file for more information.
Some third-party included files may have different licenses - please check their `LICENSE` statements (usually at the top of the source code files).

<h2 align="center">Terms of usage</h2><br>
1. Duino-Coins are earned by miners with a process called mining.<br/>
2. Mining is described as using DUCO-S1 algorithm (explained in the <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), in which finding a correct result to a mathematical problem gives the miner a reward.<br/>
3. Mining can be officially done using CPUs, AVR boards (e.g. Arduino boards), Single-board computers (e.g. Raspberry Pi boards), ESP32/8266 boards with the usage of official miners (other officially allowed miners are described in the upper part of README).<br/>
4. Mining on GPUs, FPGAs and other high-efficiency hardware is allowed, but using only the `EXTREME` mining difficulty.<br/>
5. Any users using miners on difficulty not suited for their hardware (see the <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">difficulty list</a>) will be automatically throttled and/or blocked.<br/>
6. Any users spotted using inappropriate and/or overpowered hardware will be banned manually or automatically from the network without prior notice.<br/>
7. Banning involves blocking the user from accessing his coins along with the removal of an account.<br/>
8. Only coins earned legally are eligible for the exchange.<br/>
9. Users spotted using a VPN (or similar) with malicious intents (e.g. bypassing limits) may be banned without prior notice.<br/>
10. Multiple accounts used to evade bans will be banned without prior notice.<br/>
11. These terms of usage can change at any time without prior notice.<br/>
12. Every user using Duino-Coin agrees to comply with the above rules.<br/>
13. This list will be expanded in the future.<br/>
<h4 align="center">Privacy policy</h2><br>
1. On the master server we only store usernames, hashed passwords (with the help of bcrypt) and e-mails of users as their account data.<br/>
2. E-mails are not publicly available and are only used for contacting user when needed, confirming exchanges on the <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> and receiving an occasional newsletter (planned for the future).<br/>
3. Balances, transactions and mining-related data is publicly available in the public <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON APIs</a>.<br/>
4. The privacy policy may be changed in the future with a prior notification.

<h2 align="center">Developers</h2><br>

*   **Developers:**
    *   [@revox](https://github.com/revoxhere/) (Founder/lead dev) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/) (Lead dev)
    *   [@connorhess](https://github.com/connorhess) (Lead dev)
    *   [@JoyBed](https://github.com/JoyBed) (Lead dev)
    *   [@HGEcode](https://github.com/HGEcode) (Dev)
    *   [@LDarki](https://github.com/LDarki) (Web dev)
    *   [@travelmode](https://github.com/colonelwatch) (Dev)
    *   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) dev)
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Webmaster)

*   **Contributors:**
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   Thanks to [@Furim](https://github.com/Furim) for help in the early development stage
    *   Thanks to [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) for designing early logos
    *   Thanks to [@Tech1k](https://github.com/Tech1k) for [Beyondcoin](https://beyondcoin.io) partnership and providing [duinocoin.com](https://duinocoin.com) domain
    *   Thanks to [@MrKris7100](https://github.com/MrKris7100) for help with implementing SHA1 algorithm
    *   Thanks to [@daknuett](https://github.com/daknuett) for help with Arduino SHA1 library

<hr>

Project Link: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
