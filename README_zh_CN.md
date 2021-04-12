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

<h2 align="center">Duino-Coin 是一种可以在电脑、树莓派、Arduino(及其变种板)、ESP 板子等设备上挖的币。</h2><br />

<table align="center">
  <tr>
    <th>关键特性</th>
    <th>技术指标</th>
  </tr>
  <tr>
    <td>
      💻 支持多种平台<br>
      👥 一个友好且成长中的社区<br>
      💱 易于使用和交换<br>
      🌎 随处可用<br>
      :new: 完全原创的项目<br>
      :blush: 对新手友好<br>
      💰 高性价比<br>
      ⛏️ 容易开采<br>
      📚 开源<br>
    </td>
    <td>
      ♾️ 硬币供应量：无限（2020年12月之前：350k个）<br>
      😎 预挖: <5k 个区块 (<500 个币)<br>
      ⚡ 交易时间：即时<br>
      🔢 小数：最多20个<br>
      🔤 代号: DUCO (ᕲ)<br>
      ⚒️ 算法: DUCO-S1, DUCO-S1A, XXHASH ,未来会有更多<br>
      ♐ 奖励：由"Kolka系统"支持，有助于公平地奖励矿工<br>
    </td>
  </tr>
</table>

<h2 align="center">开始吧</h2><br>

| 官方版钱包 | 官方版矿工端 |
:----------------:|:----------------:
[<img src="https://i.imgur.com/OEh0JxK.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/QNWkoee.png">](https://duinocoin.com/getting-started#pc)

#### 可在<a href="https://revoxhere.github.io/duino-coin/getting-started">官方网站</a>查看含有如何创建账户以及如何安装矿工客户端的官方版的开始指南

<h3 align="center">安装 Duino-Coin</h2><br>

下载与您的操作系统匹配的[最新版本的](https://github.com/revoxhere/duino-coin/releases/latest) Duino-Coin。<br>
After downloading, unzip it and launch the desired program.<br>
下载之后,解压并运行想运行的程序。<br>
完全没有依赖。

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
Note: Make sure python and pip are added to your PATH

After doing this, you are good to go with launching the software (e.g. `python3 PC_Miner.py` OR `py PC_Miner.py`).

<hr>

You can also get the whole Duino-Coin bundle on the AUR - just install it with your favourite AUR Helper:

```BASH
sudo pacman -S git
git clone https://aur.archlinux.org/yay-git.git
cd yay-git
makepkg -si
yay -S duino-coin
```

Duino-Coin AUR bundle is maintained by [PhereloHD](https://github.com/PhereloHD).

<h3 align="center">社区贡献者开发的软件</h3><br>

**其它已知的可以挖掘 Duino-Coin 的矿工端:**
*   [Duino-Coin_Android_Cluster Miner](https://github.com/DoctorEenot/DuinoCoin_android_cluster) by DoctorEenot
*   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner) by fabiopolancoe
*   [DUCO Miner for Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) by PhereloHD & HGEpro
*   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) by Alicia426
*   [nonceMiner](https://github.com/colonelwatch/nonceMiner) by colonelwatch
*   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) by DarkThinking
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) by phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
*   [ducominer](https://github.com/its5Q/ducominer) by its5Q
*   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
    *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) by revox
    *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) by revox
    *   [Minimal Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) by revox
<!--*   [Multithreaded Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Multithreaded_PC_Miner.py) by Bilaboz (DEPRECATED) -->

**其它工具:**
*   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) by SandUhrGucker
*   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) by LDarki
*   [DUCO Monitor](https://siunus.github.io/duco-monitor/) by siunus
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
*   [Duino Stats](https://github.com/Bilaboz/duino-stats) (Discord bot) by Bilaboz
<!--*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz (DEPRECATED) -->

此列表将被积极更新。如想将软件添加到此列表中，请提交PR或联系其中一位开发人员。

<h3 align="center">wDUCO 教程</h3><br>

wDUCO is DUCO wrapped on the Tron network. Currently there aren't many uses for it, other than just storing funds in external wallet or exchanging wDUCO to another token on JustSwap. Before doing anything, make sure you have `tronpy` (tron lib) and `cryptography` (for encrypting private key) modules for python3 installed.

### 配置 wDUCO 包装器

1. Open your DUCO GUI (desktop) or CLI (console) Wallet
2. If you're using the GUI Wallet:
    1. Open the settings tab
    2. Click the **Configure Wrapper** button
3. If you're using the CLI Wallet:
    1. Start wrapper configuration tool by typing `wrapperconf`
4. Input your private key (for example your tronlink key) and set a passphrase used for encrypting it

### 在命令行钱包中配置 wDUCO 包装器

### 打包 DUCO

After setting up the wrapper in one of the two wallets, you can wrap DUCOs (convert them to wDUCO).

1. Open your Wallet
2. Type `wrap` to start the wrapping process OR click **Wrap DUCO** button
3. Follow the instructions displayed by the wallet

### 解包 DUCO

After setting up the wrapper in one of the two wallets, you can unwrap wDUCOs (convert them to DUCO).
**Note: make sure you have some TRX in your wallet for the fees!** Unwraping will use ~5 TRX (~0.5 USD) as fees.

1. Open your Wallet
2. Type `unwrap` to start the wrapping process OR click **Unwrap DUCO** button
3. Follow the instructions displayed by the wallet

<h2 align="center">开发</h2><br>

贡献使开源社区成为了一个令人赞叹的学习，启发和创造场所。
感谢您为Duino-Coin项目所做的任何贡献。

怎么帮助?

* Fork 这个项目
* 创建你的特性分支
* 提交你的更改
* 确保一切正常
* 提交PR

[有用的工具](https://github.com/revoxhere/duino-coin/tree/useful-tools)中提供了服务器源代码，API调用文档以及用于开发自己的Duino-Coin应用程序的官方库。

<h2 align="center">一些经过官方测试的设备</h2><br>

* Arduino Pro Mini / Uno / Nano (ATmega328p @ 16 MHz 5V): ~155 H/s (15-20 DUCO/day)
* NodeMCU (ESP8266 @ 160 MHz): ~9.3 kH/s (~4.5 kH/s at 80 MHz clock) (8-12 DUCO/day)
* ESP32 (dual-threaded): ~13 kH/s (6 kH/s (core1) and 7 kH/s (core2)) (WIP)

在[有用的工具分支](https://github.com/revoxhere/duino-coin/tree/useful-tools)提供有用于AVR/ESP8266平台的哈希计算器.

<h2 align="center">License</h2><br>

Duino-Coin 主要根据MIT许可证进行分发。有关更多信息，请参见`LICENSE`文件。
某些第三方随附的文件可能具有不同的许可证-请检查其`LICENSE`（通常在源代码文件的顶部）。

<h2 align="center">服务协议</h2><br>
1. Duino-Coins ("DUCOs") are earned by miners with a process called mining.<br/>
2. Mining is described as using DUCO-S1 algorithm (explained in the <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), in which finding a correct result to a mathematical problem gives the miner a reward.<br/>
3. Mining can be officially done using CPUs, AVR boards (e.g. Arduino boards), Single-board computers (e.g. Raspberry Pi boards), ESP32/8266 boards with the usage of official miners (other officially allowed miners are described in the upper part of README).<br/>
4. Mining on GPUs, FPGAs and other high-efficiency hardware is allowed, but using only the `EXTREME` mining difficulty.<br/>
5. Any users using miners on difficulty not suited for their hardware (see the <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">difficulty list</a>) will be automatically throttled and/or blocked.<br/>
6. Any users spotted using inappropriate and/or overpowered hardware will be banned manually or automatically from the network without prior notice.<br/>
7. Banning involves blocking the user from accessing his coins along with the removal of an account.<br/>
8. Only coins earned legally are eligible for the exchange.<br/>
9. Users spotted using a VPN (or similar) with malicious intents (e.g. bypassing limits) may be banned without prior notice.<br/>
10. Multiple accounts used to bypass limits may be banned without prior notice.<br/>
11. Accounts may be suspended temporarily to investigate ("investigations") ToS violations ("violation" or "abuse").<br/>
12. Multiple accounts used to evade bans will be banned without prior notice.<br/>
13. An exchange request made to the offical DUCO-Exchange ("the offical exchange") may be delayed and/or declined during investigations. <br/>
14. Exchange requests made to the offical exchange may be declined due to ToS violations and/or low funding.<br/>
15. A user's DUCOs may be burnt if a violation can be proven.<br/>
16. These terms of service can change at any time without prior notice.<br/>
17. Every user using Duino-Coin agrees to comply with the above rules.<br/>
<h4 align="center">隐私政策</h2><br>
1. On the master server we only store usernames, hashed passwords (with the help of bcrypt) and e-mails of users as their account data.<br/>
2. E-mails are not publicly available and are only used for contacting user when needed, confirming exchanges on the <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> and receiving an occasional newsletter (planned for the future).<br/>
3. Balances, transactions and mining-related data is publicly available in the public <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON APIs</a>.<br/>
4. The privacy policy may be changed in the future with a prior notification.

<h2 align="center">开发者</h2><br>

*  **开发者:**
    *   [@revox](https://github.com/revoxhere/) (Founder/lead dev) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/) (Lead dev)
    *   [@connorhess](https://github.com/connorhess) (Lead dev)
    *   [@JoyBed](https://github.com/JoyBed) (Lead dev)
    *   [@HGEcode](https://github.com/HGEcode) (Dev)
    *   [@LDarki](https://github.com/LDarki) (Web dev)
    *   [@travelmode](https://github.com/colonelwatch) (Dev)
    *   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) dev)
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Webmaster)
    *   [@EinWildesPanda](https://github.com/EinWildesPanda) (Dev)

*   **贡献者:**
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@BastelPichi](https://github.com/BastelPichi)
    *   Thanks to [@Furim](https://github.com/Furim) for help in the early development stage
    *   Thanks to [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) for designing early logos
    *   Thanks to [@Tech1k](https://github.com/Tech1k) for [Beyondcoin](https://beyondcoin.io) partnership and providing [duinocoin.com](https://duinocoin.com) domain
    *   Thanks to [@MrKris7100](https://github.com/MrKris7100) for help with implementing SHA1 algorithm
    *   Thanks to [@daknuett](https://github.com/daknuett) for help with Arduino SHA1 library

<hr>

项目链接: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
