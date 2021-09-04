<!-- Translate up to line 118 so far :)
*** Offizielles Duino Coin README
*** by revox,BastelPichi, 2019-2021
-->

<p align = "center">
  <a href="https://duinocoin.com">
    <img width="300em" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" />
  </a>
  <br />
  <a href="https://github.com/revoxhere/duino-coin/blob/master/README.md">
    <img src="https://img.shields.io/badge/English-0097e6.svg?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_es_LATAM.md">
    <img src="https://img.shields.io/badge/-Espa%C3%B1ol-ff793f?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_zh_CN.md">
    <img src="https://img.shields.io/badge/简体中文-2ed573.svg?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_pl_PL.md">
    <img src="https://img.shields.io/badge/Polski-e66767.svg?style=for-the-badge" />
  </a>
  <br />
  <a href="https://wallet.duinocoin.com">
    <img src="https://img.shields.io/badge/Online Wallet-8e44ad.svg?style=for-the-badge&logo=Web" /></a>
  <a href="https://play.google.com/store/apps/details?id=com.pripun.duinocoin">
    <img src="https://img.shields.io/badge/Android App-e84393.svg?style=for-the-badge&logo=Android" /></a>
  <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">
    <img src="https://img.shields.io/badge/whitepaper-1abc9c.svg?style=for-the-badge&logo=Academia" /></a>
  <br>
  <a href="https://youtu.be/bFnCdqMke34">
    <img src="https://img.shields.io/badge/Video-Watch-e74c3c.svg?style=for-the-badge&logo=Youtube" /></a>
  <a href="https://discord.gg/kvBkccy">
    <img src="https://img.shields.io/discord/677615191793467402.svg?color=5539cc&label=Discord&logo=Discord&style=for-the-badge" /></a>
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/2.4.5">
    <img src="https://img.shields.io/badge/release-2.4.5-ff4112.svg?style=for-the-badge" /></a>
</p>

<h3 align="center">Duino-Coin ist eine Kryptowährung, die zum Beispiel auf Arduinos, ESP boards, Raspberry Pis, Computern, und mehr gemint werden kann</h3>
<h4 align="center">inklusive Wi-Fi Router, SmartTV's, Smartphones, Smartwatches, SBCs, MCUs, GPUs - eigentlich alles das einen kleinen Programmierbaren Microchip hat.!</h4><br />

<table align="center">
  <tr>
    <th>Besonderheiten:</th>
    <th>Technische Spezifikationen</th>
  </tr>
  <tr>
    <td>
      💻 Von vielen Betriebssystemen unterstützt<br>
      👥 freundliche & wachsende Community<br>
      💱 Einfach zu nutzten & in andere Währungen umzutauschen<br>
      🌎 Überall verfügbar<br>
      :new: Komplett originales Projekt<br>
      :blush: Anfänger freundlich <br>
      💰 Kosten-Effektiv<br>
      ⛏️ Einfach zu minen<br>
      📚 Open-source<br>
    </td>
    <td>
      ♾️ Coin supply: Unendlich (vor Dezember 2020: 350k coins) <br>
      😎 Prämie: <5k blöcke(<500 coins)<br>
      ⚡ Transaktionszeit: sofort<br>
      🔢 Dezimalstellen: bis zu 20<br>
      🔤 Ticker: DUCO (ᕲ)<br>
      ⚒️ Algorithmen: DUCO-S1, DUCO-S1A, XXHASH + mehr geplannt<br>
      ♐ Rewards: unterstützt durch das "Kolka System", welches hilft, miner fair zu belohnen<br>
    </td>
  </tr>
</table>

<h2 align="center">Get started</h2><br>

Offiziele Anleitungen um einen ACccount zu erstellen, und auf vielen Geräten zu minen, <a href="https://revoxhere.github.io/duino-coin/getting-started">auf der offizielen Website</a>.<br>
Ein FAQ und Hilfe kann in der Wiki-Seite gefunden werden [Wikis](https://github.com/revoxhere/duino-coin/wiki).
<br>

| Offiziele Wallets | Offiziele Miner |
:-----------------:|:----------------:
[<img src="https://i.imgur.com/msVtLHs.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/SMkKHOK.png">](https://duinocoin.com/getting-started#computer)

<h3 align="center">Duino-Coin Installieren</h2><br>

Der einfachste Weg zu starten, ist  [das neuste release](https://github.com/revoxhere/duino-coin/releases/latest) für dein OS herunterzuladen.<br>
<br> Wenn der Download fertig ist, Entpacke ihn und öffnen dein gewünschtes Programm. Es sind keine anderen Programme nötig. <br>

<hr>

 Wenn du die Programme dierekt über Python starten willst, musst du vielleicht einige zusätzliche pip-module installieren. So kann man es auf Debian-basierenden Linux distros (z.B. Ubuntu, Debian oder Raspian) machen:
```BASH
sudo apt install python3 python3-pip git
git clone https://github.com/revoxhere/duino-coin
cd duino-coin
python3 -m pip install -r requirements.txt
```
Wenn du Windows nutzt, musst du [Python 3](https://www.python.org/downloads/) herunterladen, das [Master Repository](https://github.com/revoxhere/duino-coin/archive/master.zip), dieses dann Entpacken (WinRar, 7zip) Danach kannst du ein CMD Fester öffnen (Windows + R Taste). 

Im CMD Fenster, Schreibe/kopiere dies hinein:
```BASH
py -m pip install -r requirements.txt
```
Wichtig für Windows nutzer: Immer sicher gehen das [Python 3](https://www.python.org/downloads/) und Python3-pip installiert und im PATH sind.

Jetzt kannst du den Miner starten. (z.b. `python3 PC_Miner.py` oder `py PC_Miner.py`).

<hr>

Du kannst das ganze Duino-Coin Paket auch mit AUR laden - dazu einfach ein Ladevorgang starten mit deinem Favorisierten AUR Helfer Programm:

```BASH
sudo pacman -S yay
yay -S duino-coin
```

das Duino-Coin AUR Paket wird bereitgestellt von [PhereloHD](https://github.com/PhereloHD).
<br><br>
<h2 align="center">Von der Community erstellte Software von Talentierten Mitgliedern</h2><br>

**Andere Miner-/Software/Hardware/Chips die bekannt sind das Duino-Coin damit Funktioniert:**
*   [duino-coin-kodi](https://github.com/SandUhrGucker/duino-coin-kodi) - Mining addon for Kodi Media Center by SandUhrGucker
*   [MineCryptoOnWifiRouter](https://github.com/BastelPichi/MineCryptoOnWifiRouter) - Python Script für das Mining von Duino-Coin auf Routern by BastelPichi
*   [Duino-Coin_Android_Cluster Miner](https://github.com/DoctorEenot/DuinoCoin_android_cluster) - Mining mit weniger Bandbreite für Android Handy by DoctorEenot
*   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner) - MicroPython Miner / ESP Boards  by fabiopolancoe
*   [DUCO Miner für Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) - Python Miner für Nintendo 3DS by PhereloHD & HGEpro
*   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) - Miner in Docker (Linux/ARM) by Alicia426
*   [nonceMiner](https://github.com/colonelwatch/nonceMiner) -  Schneller Duino-Coin Miner by colonelwatch
*   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) - Einfach NodeJS Miner by DarkThinking
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) - Pure C Miner by phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
*   [ducominer](https://github.com/its5Q/ducominer) by its5Q
*   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
    *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) by revox
    *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) by revox
    *   [Minimal Python Miner (DUCO-S1)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) by revox
    *   [Minimal Python Miner (XXHASH)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner_XXHASH.py) by revox
    *   [Teensy 4.1 code for Arduino IDE](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Teensy_code/Teensy_code.ino) by joaquinbvw
<!--*   [Multithreaded Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Multithreaded_PC_Miner.py) by Bilaboz (DEPRECATED) -->

**Other tools:**
*   [Duino-Coin Mining Dashboard](https://lulaschkas.github.io/duco-mining-dashboard/) Dashboard und Problembeseitigungs Hilfe by Lulaschkas
*   [duco-miners](https://github.com/dansinclair25/duco-miners) CLI Mining Dashboard by dansinclair25
*   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) by SandUhrGucker
*   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) Für Chrome  by LDarki
*   [DUCO Monitor](https://siunus.github.io/duco-monitor/) Account Statistiken by siunus
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
*   [Duino Stats](https://github.com/Bilaboz/duino-stats) DUINO-COIN Discord Bot by Bilaboz
<!--*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz (DEPRECATED) -->

Diese Liste wird ständig geupdatet. Wenn auch du deine Software hier auflisten möchtest die zum Projekt beiträgt, einfach einen Pull request auf Github erstellen, oder einen der Programmierer auf Discord anschreiben.
<br><br>
<h3 align="center">wDUCO Tutorial</h3><br>

Duino-Coin ist eine Hybridwährung, was bedeutet, dass sie in wDUCO umgewandelt werden kann, wo DUCO im [Tron-Netzwerk](https://tron.network) (als Token) verpackt ist. Derzeit gibt es nicht viele Verwendungszwecke dafür, außer nur Geld in einer externen Wallet zu speichern oder wDUCO auf JustSwap gegen einen anderen Token auszutauschen. 
Ein Tutorial zur Verwendung von wDUCO ist in der [wDUCO-Wiki](https://github.com/revoxhere/duino-coin/wiki/wDUCO-tutorial) verfügbar. 
<br> <br>

<h2 align="center">Entwicklung </h2><br>

Beiträge machen die Open-Source-Community zu einem großartigen Ort zum Lernen, Inspirieren und Gestalten.
Jeder Beitrag, den Sie zum Duino-Coin-Projekt leisten, wird sehr geschätzt.

Wie kann man helfen? 

* erstelle eine Fork für das Projekt
* Erstellen Sie Ihren Feature-Zweig
* Sende deine Änderungen ein 
* Stellen Sie sicher, dass alles wie vorgesehen funktioniert
* Öffnen Sie eine Pull-Anfrage 

Server-Quellcode, Dokumentation für API-Aufrufe und offizielle Bibliotheken zur Entwicklung eigener Apps für Duino-Coin sind im Zweig [nützliche Tools](https://github.com/revoxhere/duino-coin/tree/useful-tools) verfügbar . 

<h2 align="center">Einige der offiziell geprüften Geräte mit (DUCO-S1)</h2><br>

| Gerät/CPU/SBC/MCU/Chip                                   | durchschnittliche Hashrate<br>(all threads) | Mining<br>threads | Strom<br>verbrauch | Durchschnittliche<br>DUCO/Tag |
|-----------------------------------------------------------|-----------------------------------|-------------------|----------------|---------------------|
| Arduino Pro Mini, Uno, Nano etc.<br>(Atmega 328p/pb/16u2) | 170 H/s                           | 1                 | 0.2 W          | 15-20               |
| Teensy 4.1                                                | 12.8 kH/s                         | 1                 | -              | -                   |
| NodeMCU, Wemos D1 etc.<br>(ESP8266)                       | 9.3 kH/s                          | 1                 | 0.6 W          | 6-8                 |
| ESP32                                                     | 27 kH/s                           | 2                 | 1.25 W         | -                   |
| Raspberry Pi Zero                                         | 17 kH/s                           | 1                 | 0.7 W          | -                   |
| Raspberry Pi 3                                            | 440 kH/s                          | 4                 | 5.1 W          | -                   |
| Raspberry Pi 4                                            | 1.3 MH/s                          | 4                 | 6.4 W          | -                   |
| Atomic Pi                                                 | 690 kH/s                          | 4                 | 6 W            | -                   |
| Orange Pi Zero 2                                          | 740 kH/s                          | 4                 | 2.55 W         | -                   |
| Khadas Vim 2 Pro                                          | 1.12 MH/s                         | 8                 | 6.2 W          | -                   |
| Libre Computers Tritium H5CC                              | 480 kH/s                          | 4                 | 5 W            | -                   |
| Libre Computers Le Potato                                 | 410 kH/s                          | 4                 | 5 W            | -                   |
| Pine64 ROCK64                                             | 640 kH/s                          | 4                 | 5 W            | -                   |
| Intel Celeron G1840                                       | 1.25 MH/s                         | 2                 | -              | 5-6                 |
| Intel Core i5-2430M                                       | 1.18 MH/s                         | 4                 | -              | 6.5                 |
| Intel Core i5-3230M                                       | 1.48 MH/s                         | 4                 | -              | 6.1                 |
| Intel Core i5-5350U                                       | 1.35 MH/s                         | 4                 | -              | 6.0                 |
| Intel Core i5-7200U                                       | 1.62 MH/s                         | 4                 | -              | 7.5                 |
| Intel Core i5-8300H                                       | 3.67 MH/s                         | 8                 | -              | 9.1                 |   
| Intel Core i3-4130                                        | 1.45 MH/s                         | 4                 | -              | -                   |

<br><br>
<h2 align="center">Lizenz</h2><br>

Duino-Coin wird hauptsächlich unter der MIT-Lizenz vertrieben. Weitere Informationen finden Sie in der Datei `LICENSE`.
Einige von Drittanbietern enthaltene Dateien können unterschiedliche Lizenzen haben - überprüfen Sie bitte deren `LICENSE`-Anweisungen (normalerweise oben in den Quellcodedateien). <br><br>

<h2 align="center">Nutzungsbedingungen</h2><br>
1. Duino-Coins ("DUCOs") werden von Minern mit einem Prozess namens Mining verdient. <br/>
2. Mining wird mit dem DUCO-S1-Algorithmus beschrieben (erklärt in der <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), in dem das Finden eines korrekten Ergebnisses für ein mathematisches Problem dem Miner eine Belohnung gibt.<br/> 
3. Mining kann offiziell mit CPUs, AVR Boards (zB Arduino Boards), Single Board Computern (zB Raspberry Pi Boards), ESP32/8266 Boards unter Einsatz von offiziellen Minern durchgeführt werden (andere offiziell erlaubte Miner werden im oberen Teil beschrieben von README).<br/>
4. Das Mining auf GPUs, FPGAs und anderer hocheffizienter Hardware ist erlaubt, jedoch nur mit der Mining-Schwierigkeit `EXTREME`.<br/> 
5. Alle Benutzer, die Miner auf einem für ihre Hardware nicht geeigneten Schwierigkeitsgrad verwenden (siehe die <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">Schwierigkeitsliste</a>) wird automatisch gedrosselt und/oder gesperrt.<br/> 
6. Alle Benutzer, die entdeckt werden, mit unangemessener und/oder nicht geeignete Hardware verwenden, werden ohne vorherige Ankündigung manuell oder automatisch aus dem Netzwerk gesperrt.<br/>
7. Beim Bannen wird der Benutzer daran gehindert, auf seine Coins zuzugreifen, zusammen mit der Entfernung eines Kontos.<br/> 
8. Nur legal verdiente Coins können umgetauscht werden.<br/> 
9. Benutzer, die mit böswilligen Absichten (z. B. beim Umgehen von Beschränkungen) entdeckt werden, die ein VPN (oder ähnliches) verwenden, können ohne vorherige Ankündigung gesperrt werden.<br/>
10. Mehrere Konten, die verwendet werden, um Limits zu umgehen, können ohne vorherige Ankündigung gesperrt werden.<br/> 
11. Konten können vorübergehend gesperrt werden, um Verstöße gegen die ToS ("Untersuchungen") ("Verstoß" oder "Missbrauch") zu untersuchen.<br/> 
12. Mehrere Konten, die verwendet werden, um Sperren zu umgehen, werden ohne vorherige Ankündigung gesperrt.<br/> 
13. Eine Umtauschanfrage an die offizielle DUCO-Börse ("die offizielle Börse") kann während der Nachforschungen verzögert und/oder abgelehnt werden. <br/> 
14. Umtauschanfragen an die offizielle Börse können aufgrund von ToS-Verstößen und/oder geringer Finanzierung abgelehnt werden.<br/> 
15. Die DUCOs eines Benutzers können verbrannt werden, wenn ein Verstoß nachgewiesen werden kann.<br/> 
16. Diese Nutzungsbedingungen können jederzeit ohne vorherige Ankündigung geändert werden.<br/> 
17. Jeder Nutzer, der Duino-Coin verwendet, erklärt sich damit einverstanden, die oben genannten Regeln einzuhalten.<br/> <br>
<h2 align="center">Datenschutz-Bestimmungen </h2><br>
1. Auf dem Masterserver speichern wir nur Benutzernamen, gehashte Passwörter (mit Hilfe von bcrypt) und E-Mails der Benutzer als Kontodaten.<br/> 
2. E-Mails sind nicht öffentlich zugänglich und werden nur verwendet, um den Benutzer bei Bedarf zu kontaktieren und den Austausch auf der <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> zu bestätigen und ein gelegentlicher Newsletter (für die Zukunft geplant).<br/> 
3. Wallet Guthaben, Transaktionen und Mining Daten sind in den öffentlichen <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON-API's </a> öffentlich verfügbar.<br/> 
4. Die Datenschutzerklärung kann in Zukunft nach vorheriger Ankündigung geändert werden. <br><br><br>

<h1 align="center">Entwickler</h1><br>

*   **Entwickler:**
    *   [@revox](https://github.com/revoxhere/) (Gründer/Leitender Entwickler) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/) (Leitender Entwickler)
    *   [@connorhess](https://github.com/connorhess) (Leitender Entwickler)
    *   [@JoyBed](https://github.com/JoyBed) (Leitender Entwickler)
    *   [@LDarki](https://github.com/LDarki) (Web Entwickler)
    *   [@travelmode](https://github.com/colonelwatch) (Entwickler)
    *   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) Entwickler)
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Leitender Webmaster and DUCO Entwickler) <br><br>

*   **Mitwirkende:**
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@BastelPichi](https://github.com/BastelPichi)
    *   [@suifengtec](https://github.com/suifengtec)
    *   Danke an [@Furim](https://github.com/Furim) für Hilfe in der frühen Entwicklungsphase 
    *   Danke an [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) für die Gestaltung früherer Logos
    *   Danke an [@Tech1k](https://github.com/Tech1k) für die [Beyondcoin](https://beyondcoin.io) Partnerschaft und Bereitstellung der [duinocoin.com](https://duinocoin.com) Domain 
    *   Danke an [@MrKris7100](https://github.com/MrKris7100) für die Hilfe bei der Implementierung des SHA1-Algorithmus 
    *   Danke an [@daknuett](https://github.com/daknuett) für Hilfe bei der Arduino SHA1-Bibliothek 

<hr>

Projekt Link: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
