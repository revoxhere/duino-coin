<!--
*** Official Duino Coin README
*** by revox, 2019-2022
-->

<p align = "center">
  <a href="https://github.com/revoxhere/duino-coin">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" />
  </a>
  <br />
</p>
<br />
<p align = "center">
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

<h2 align="center">Duino-Coin to moneta którą można wydobywać używając komputerów, płytek Raspberry Pi, Arduino, ESP i nie tylko.</h2><br />

<table align="center">
  <tr>
    <th>Główne cechy</th>
    <th>Specyfikacja</th>
  </tr>
  <tr>
    <td>
      💻 Wspierana przez ogromną ilość platform<br>
      👥 Posiada przyjazną społeczność<br>
      💱 Łatwa w użyciu i wymianie<br>
      🌎 Dostępna wszędzie<br>
      :new: W pełni oryginalna<br>
      :blush: Dobra dla początkujących<br>
      💰 Opłacalna<br>
      ⛏️ Łatwa w wydobyciu<br>
      📚 O otwartym kodzie źródłowym<br>
    </td>
    <td>
      ♾️ Zasób monet: Nieskończony (przed Grudniem 2020: 350 tys. monet)<br>
      😎 Premine: <5k bloków (<500 monet)<br>
      ⚡ Czas transakcji: Natychmiastowy<br>
      🔢 Cyfry po przecinku: maks. 20<br>
      🔤 Symbol: DUCO (ᕲ)<br>
      ⚒️ Algorytmy: DUCO-S1, DUCO-S1A, XXHASH +więcej planowanych<br>
      ♐ Dystrybucja nagród: wspierana przez "Kolka system" pomagający sprawiedliwie nagradzać górników<br>
    </td>
  </tr>
</table>

<h2 align="center">Jak zacząć?</h2><br>

| Oficjalny Portfel | Oficjalne Koparki |
:------------------:|:------------------:
[<img src="https://i.imgur.com/OEh0JxK.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/QNWkoee.png">](https://duinocoin.com/getting-started#pc)

#### Oficjalne poradniki odnośnie zakładania konta i ustawiania koparek na przeróżnych urządzeniach są dostępne na <a href="https://revoxhere.github.io/duino-coin/getting-started">naszej oficjalnej stronie</a>.

<h3 align="center">Instalowanie oprogramowania Duino-Coin</h2><br>

Najprostszym sposobem na zainstalowanie programów do obsługi Duino-Coin jest pobranie [najnowszego wydania](https://github.com/revoxhere/duino-coin/releases/latest) dla twojego systemu.<br>
Po pobraniu, wypakuj archiwum i uruchom wybrany program.<br>
Nie jest wymagane instalowanie żadnych dodatkowych bibliotek.

<hr>

Jeżeli chcesz uruchomić programy z kodu źródłowego, będzie wymagane zainstalowanie kilku bibliotek. W większości najpopularniejszych systemów unixowych (np. Ubuntu, Debian, Raspian) wygląda to w ten sposób:
```BASH
sudo apt install python3 python3-pip git
git clone https://github.com/revoxhere/duino-coin
cd duino-coin
python3 -m pip install -r requirements.txt
```
Jeżeli używasz Windowsa, pobierz [Python 3](https://www.python.org/downloads/), potem [nasze repozytorium](https://github.com/revoxhere/duino-coin/archive/master.zip), wypakuj je i otwórz folder w konsoli. W niej wpisz:
```BASH
py -m pip install -r requirements.txt
```
Uwaga: upewnij się że Python i PIP są dodane do twojej zmiennej środowiskowej PATH

Po wykonaniu jednego z powyższych kroków możesz włączyć wybrany program (np. `python3 PC_Miner.py` LUB `py PC_Miner.py`).

<hr>

Możesz również pobrać oprogramowanie Duino-Coin z AUR - zainstaluj je używając swojego ulubionego menedżera do AUR:

```BASH
sudo pacman -S git
git clone https://aur.archlinux.org/yay-git.git
cd yay-git
makepkg -si
yay -S duino-coin
```

Pakiet Duino-Coin dla AUR jest utrzymywany przez by [PhereloHD](https://github.com/PhereloHD).

<h3 align="center">Oprogramowanie stworzone przez społeczność</h3><br>

**Koparki działające z Duino-Coin:**
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

**Inne narzędzia:**
*   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) by SandUhrGucker
*   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) by LDarki
*   [DUCO Monitor](https://siunus.github.io/duco-monitor/) by siunus
*   [duino-tools](https://github.com/kyngs/duino-tools) by kyngs
*   [Duino Stats](https://github.com/Bilaboz/duino-stats) (Discord bot) by Bilaboz
<!--*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) by Bilaboz (DEPRECATED) -->

Ta lista jest aktywnie aktualizowana. Jeżeli chcesz coś do niej dodać, wyślij PR na GitHubie lub skontaktuj się z jednym z deweloperów.

<h3 align="center">Używanie wDUCO</h3><br>

wDUCO to DUCO "zwrapowane" na sieci innej kryptowaluty - Tron. Aktualnie nie ma dla niej wiele użyć, oprócz przechochywania monet w zewnętrznym portfelu wymieniania wDUCO na inny token na giełdzie JustSwap. Zanim zaczniesz używać wDUCO, upewnij się że masz zainstalowane moduły `tronpy` (biblioteka tron) i `cryptography` (do szyfrowania).

### Konfiguracja Wrappera wDUCO

1. Otwórz swój GUI (graficzny) lub CLI (konsolowy) Portfel DUCO
2. Jeżeli używasz portfela GUI:
    1. Otwórz ustawienia
    2. Kliknij na przycisk **Ustawienia Wrappera**
3. Jeżeli używasz portfela CLI:
    1. Włącz konfigurator wrappera wpisując `wrapperconf`
4. Wpisz swój prywatny klucz (np. klucz z tronlink) i ustaw hasło do jego zaszyfrowania

### Wrapowanie DUCO

Po ustawieniu wrappera w jednym z dwóch portfeli możesz przejść do wrapowania DUCO, czyli zamiany na wDUCO. 

1. Otwórz swoj portfel
2. Wpisz `wrap` aby rozpocząć proces wrapowania (CLI) lub kliknij na przycisk **Wrapuj DUCO** (GUI)
3. Podążaj za instrukcjami wyświetlanymi przez portfel

### Odwrapowanie DUCO

Po ustawieniu wrappera w jednym z dwóch portfeli możesz przejść do odwrapowania wDUCO, czyli zamiany spowrotem na DUCO. 
**Uwaga: upewnij się że masz kilka TRX w swoim portfelu które zostanie zużyte na prowizje sieci!** Odwrapowanie zużyje ok. ~5 TRX (~2zł).

1. Otwórz swój portfel
2. Wpisz `unwrap` aby rozpocząć proces odwrapowania (CLI) lub kliknij na przycisk **Odrapuj DUCO** (GUI)
3. Podążaj za instrukcjami wyświetlanymi przez portfel

<h2 align="center">Rozwój Duino-Coin</h2><br>

Każda pomoc sprawia, że społeczność open-source jest wspaniałym miejscem do nauki, inspiracji i tworzenia.
Nawet najmniejszy wkład w pomóc rozwoju projektu Duino-Coin jest przez nas bardzo doceniany.

Jak pomóc?

*   Zforkuj projekt
*   Stwórz branch ze swoją zmianą
*   Zastosuj swoje poprawki
*   Upewnij się, że wszystko działa poprawnie
*   Otwórz Pull Request

Kod źródłowy serwera, dokumentacja dla naszego API i oficjalne biblioteki do budowania własnych aplikacji są dostępne na branchu [useful tools](https://github.com/revoxhere/duino-coin/tree/useful-tools).

<h2 align="center">Niektóre z oficjalnie przetestowanych urządzeń</h2><br>

*   Arduino Pro Mini / Uno / Nano (ATmega328p @ 16 MHz 5V): ~155 H/s (15-20 DUCO/dzień)
*   NodeMCU (ESP8266 @ 160 MHz): ~9.3 kH/s (~4.5 kH/s przy 80 MHz zegarze) (8-12 DUCO/dzień)
*   ESP32 (przy dwóch rdzeniach): ~13 kH/s (6 kH/s (rdzeń 1) and 7 kH/s (rdzeń 2)) (WIP)

<h2 align="center">Licencja</h2><br>

Duino-Coin jest rozpowszechniany na licencji MIT. Zobacz plik `LICENSE` po więceji informacji.
Niektóre pliki niepochodzące od nas mogą mieć inne licencje - sprawdź ich klauzuly `LICENSE` (najczęściej u góry plików źródłowych).

<h2 align="center">Regulamin</h2><br>
1. Duino-Coin ("DUCO") są zarobione przez górników - "minerów" podczas procesu nazywanego górnictwem - "mining".<br/>
2. Górnictwo to wykorzystanie algorytmu DUCO-S1 (wyjaśnionego w <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), w którym znalezienie poprawnego wyniku do problemu matematycznego daje górnikowi nagrodę.<br/>
3. Mining może być oficjalnie wykonywany przy użyciu procesorów, płytek AVR (np. Arduino), komputerów jednopłytkowych (np. Raspberry Pi) lub płytek ESP32/8266 z wykorzystaniem oficjalnych minerów (inne oficjalnie dozwolone górniki są opisane w górnej części README).<br/>
4. Mining przu użyciu GPU, FPGA i innego sprzętu o wysokiej wydajności jest dozwolone, ale przy użyciu tylko trudności `EXTREME`.<br/>
5. Każdy użytkownik korzystający z górników na trudności niezgodnej dla ich wydajności (patrz <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">lista trudności</a>) będzie automatycznie przeniesiony (Kolka system) do odpowiedniej i / lub zablokowany.<br/>
6. Każdy użytkownik zauważony przy użyciu niewłaściwego sprzętu zostanie zbanowany ręcznie lub automatycznie z sieci bez uprzedzenia.<br/>
7. Banowanie polega na zablokowaniu użytkownikowi dostępu do jego monet wraz z usunięciem konta.<br/>
8. Do wymiany kwalifikują się tylko monety zdobyte legalnie.<br/>
9. Użytkownicy zauważeni przy użyciu VPN (lub podobnych) w złych zamiarach (np. omijanie limitów) mogą zostać zbanowani bez uprzedzenia.<br/>
10. Wiele kont używanych do ominięcia limitów mogą być zbanowane bez uprzedzenia.<br/>
11. Konta mogą zostać tymczasowo zawieszone w celu zbadania ("dochodzenia") naruszeń ToS ("naruszenie" lub "nadużycie").<br/>
12. Wielokrotne konta używane do unikania zakazów zostaną zbanowane bez uprzedzenia.<br/>
13. Żądanie wymiany dokonane na oficjalnej giełdzie DUCO-Exchange ("oficjalna giełda") może być opóźnione i/lub odrzucone podczas dochodzenia. <br/>
14. Żądania wymiany dokonane na oficjalnej giełdzie mogą zostać odrzucone z powodu naruszenia ToS i/lub niskich funduszy.<br/>
15. DUCO użytkownika mogą zostać usunięte, jeśli naruszenie zostanie udowodnione.<br/>
16. Niniejszy regulamin może ulec zmianie w dowolnym momencie bez wcześniejszego powiadomienia.<br/>
17. Każdy użytkownik korzystający z Duino-Coin zobowiązuje się do przestrzegania powyższych zasad.<br/>

<h4 align="center">Polityka prywatności</h2><br>
1. Na serwerze głównym przechowujemy tylko nazwy użytkowników, zaszyfrowane hasła (za pomocą bcrypt) i e-maile użytkowników jako ich dane konta.<br/>
2. E-maile nie są publicznie dostępne i są wykorzystywane wyłącznie do kontaktowania się z użytkownikiem w razie potrzeby, potwierdzania wymian na <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> i otrzymywania okazjonalnego newslettera (planowanego na przyszłość).<br/>
3. Salda, transakcje i dane związane z wydobyciem jest publicznie dostępne w publicznych <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON API</a>.<br/>
4. Polityka prywatności może ulec zmianie w przyszłości z uprzednim powiadomieniem.

<h2 align="center">Deweloperzy</h2><br>

*   **Deweloperzy:**
    *   [@revox](https://github.com/revoxhere/) (Założyciel/główny deweloper) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/) (główny deweloper)
    *   [@connorhess](https://github.com/connorhess) (główny deweloper
    *   [@JoyBed](https://github.com/JoyBed) (główny deweloper)
    *   [@LDarki](https://github.com/LDarki) (web deweloper)
    *   [@travelmode](https://github.com/colonelwatch) (deweloper)
    *   [@ygboucherk](https://github.com/ygboucherk) (deweloper [wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2))
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Lead Webmaster and DUCO Developer) <!-- translation wanted -->

*   **Współautorzy:**
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@BastelPichi](https://github.com/BastelPichi)
    *   [@suifengtec](https://github.com/suifengtec)
    *   Podziękowania dla [@Furim](https://github.com/Furim) za pomoc podczas wczesnego rozwoju
    *   Podziękowania dla [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) za pomoc w tworzeniu logotypów
    *   Podziękowania dla [@Tech1k](https://github.com/Tech1k) za współpracę z [Beyondcoin](https://beyondcoin.io) i domenę [duinocoin.com](https://duinocoin.com)
    *   Podziękowania dla [@MrKris7100](https://github.com/MrKris7100) za pomoc w implementacji algorytmu SHA1
    *   Podziękowania dla [@daknuett](https://github.com/daknuett) za pomoc w implementacji algorytmu SHA1 dla Arduino

<hr>

Link do projektu: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
