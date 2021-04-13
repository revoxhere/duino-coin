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
下载之后,解压并运行想运行的程序。<br>
完全没有依赖。

<hr>

如果要从源代码运行程序，则可能需要安装一些依赖项。这是在基于Debian的发行版（例如Ubuntu，Debian，raspian）上执行此操作的方法：

```bash
sudo apt install python3 python3-pip git
git clone https://github.com/revoxhere/duino-coin
cd duino-coin
python3 -m pip install -r requirements.txt
```

如果您在使用 Windows, 下载 [Python 3](https://www.python.org/downloads/), then [our repository](https://github.com/revoxhere/duino-coin/archive/master.zip), 解压缩并在命令提示符下打开文件夹。在CMD中，键入：

```bash
py -m pip install -r requirements.txt
```

注意：确保将python和pip添加到您的`PATH`中.

完成此操作后，您就可以启动该软件了(例如`python3 PC_Miner.py` 或者 `py PC_Miner.py`).

<hr>

您还可以在AUR上获得整个Duino-Coin捆绑包-只需使用您最喜欢的AUR Helper进行安装即可：

```bash
sudo pacman -S git
git clone https://aur.archlinux.org/yay-git.git
cd yay-git
makepkg -si
yay -S duino-coin
```

Duino-Coin AUR 由 [PhereloHD](https://github.com/PhereloHD)进行维护.

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

wDUCO 是 DUCO 在 Tron 网络上的一种包装. 目前，除了将资金存储在外部钱包中或将wDUCO交换为JustSwap上的另一个令牌外，它没有太多用途。

在做任何事情之前，请确保已经安装了用于python3的 `tronpy`模块和`cryptography`模块（用于加密私钥）。

### 配置 wDUCO 包装器

1. 打开您的DUCO GUI（桌面）或CLI（控制台）钱包
2. 如果您使用的是GUI版的电子钱包:
    1. 打开设置选项卡;
    2. 点击 **配置包装器** 按钮;
3. 如果您使用的是CLU版的电子钱包:
    1. 通过输入 `wrapperconf`启动包装器配置工具。
4. 输入您的私钥（例如您的tronlink密钥）并设置用于加密它的密码;

### 在命令行钱包中配置 wDUCO 包装器

### 打包 DUCO

在两个钱包之一中设置包装器后，您可以包装DUCO（将其转换为wDUCO）。

1. 打开钱包
2. 输入 `wrap` 开始包装过程，或者点击 **包装 DUCO** 按钮;
3. 请遵循钱包显示的说明;

### 解包 DUCO

在两个钱包之一中设置包装器后，您可以解开wDUCO（将它们转换为DUCO）。

**注意：请确保您的钱包里有TRX来支付费用！**取消包装将使用~5 TRX（~0.5 USD）作为费用。

1. 打开您的钱包;
2. 输入 `unwrap`  开始解包过程,或点击 **解包 DUCO** 按钮;
3. 请遵循钱包显示的说明;

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
1. Duino-Coins ("DUCOs")是由矿工挖矿挖出来的。<br/>
2. 挖矿被描述为使用DUCO-S1算法（在<a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf"> Duino-Coin白皮书</a>中进行了解释），在其中找到正确的数学问题结果会给矿工以奖励。<br/>
3.可以使用CPU、AVR板（例如Arduino板）、单板计算机（例如Raspberry Pi板）、ESP32 / 8266板（使用官方矿工）来正式进行挖矿（自述文件的上部描述了其他官方允许的矿工） ）。<br/>
4.允许在GPU，FPGA和其他高效硬件上进行挖掘，但仅使用`EXTREME`挖掘难度。<br/>
5. 任何因困难而使用矿工的用户都不适合其硬件（请参见<a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">困难列表</a> ）将被自动节流和/或阻塞。<br/>
6. 任何发现使用不适当和/或过载的硬件的用户都将被手动或自动从网络禁止，恕不另行通知。<br/>
7. 禁止包括阻止用户访问他的硬币以及删除帐户。<br/>
8. 只有合法赚取的币才有资格兑换。<br/>
9. 可能禁止使用具有恶意（例如绕过限制）的VPN（或类似网络）发现的用户，恕不另行通知。<br/>
10.  可能会禁止使用多个绕过限额的帐户，恕不另行通知。<br/>
11. 帐户可能会暂时被暂停以调查（`调查`）ToS违规行为（`违规`或`滥用`）。<br/>
12. 多个用于逃避禁令的帐户将被禁止，恕不另行通知。<br/>
13.在调查过程中，向官方DUCO-Exchange提出的交换请求（`官方交换`）可能会被延迟和/或拒绝。 <br/>
14. 由于违反服务条款和/或资金不足，向正式交易所提出的交易所请求可能会被拒绝。<br/>
15. 如果可以证明违规，则可能会烧毁用户的DUCO。<br/>
16. 这些服务条款可以随时更改，恕不另行通知。<br/>
17. 每个使用Duino-Coin的用户均同意遵守上述规则。
<br/>

<h4 align="center">隐私政策</h2><br>

1. 在主服务器上，我们仅存储用户名，哈希密码（在bcrypt的帮助下）和用户的电子邮件作为其帐户数据。<br/>
2. 电子邮件不是公开可用的，仅在需要时用于联系用户,在<a href="https://revoxhere.github.io/duco-exchange/"> DUCO-Exchange </a>上确认交流，并偶尔收到通讯（计划在将来进行）。<br/>
3. 余额，交易和与采矿相关的数据可以在公共<a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api"><strong>JSON APIs </strong>中公开获得</a>.<br/>
4. 将来可能会在事先通知的情况下更改隐私政策。

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
