<!--
*** Official Duino Coin README
*** by revoxhere, 2019-2022
-->

<a href="https://duinocoin.com">
  <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true" width="215px" align="right" />
</a>

<h1>
  <a href="https://duinocoin.com">
    <img src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" width="430px" />
  </a>
  <br>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/README.md">
    <img src="https://img.shields.io/badge/English-f39c12.svg?style=for-the-badge" /></a>
</h1>
<a href="https://wallet.duinocoin.com">
  <img src="https://img.shields.io/badge/Online Wallet-8e44ad.svg?style=for-the-badge&logo=Web" /></a>
<a href="https://play.google.com/store/apps/details?id=com.pripun.duinocoin">
  <img src="https://img.shields.io/badge/Android App-e84393.svg?style=for-the-badge&logo=Android" /></a>
<a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">
  <img src="https://img.shields.io/badge/whitepaper-1abc9c.svg?style=for-the-badge&logo=Academia" /></a>
<a href="https://youtu.be/bFnCdqMke34">
  <img src="https://img.shields.io/badge/Video-Watch-e74c3c.svg?style=for-the-badge&logo=Youtube" /></a>
<a href="https://discord.gg/kvBkccy">
  <img src="https://img.shields.io/discord/677615191793467402.svg?color=5539cc&label=Discord&logo=Discord&style=for-the-badge" /></a>
<a href="https://github.com/revoxhere/duino-coin/releases/tag/2.5.5">
  <img src="https://img.shields.io/badge/release-2.5.5-ff4112.svg?style=for-the-badge" /></a>
<br>

<h3>
  Duino-Coin, Arduinolarla, ESP8266/32 kartlarıyla, Raspberry pi'larla, bilgisayarla ve çok daha fazlası ile kazılabilen bir coindir.<br>
  (Wi-Fi yönlendiricileri, akıllı TV'ler, akıllı telefonlar, akıllı saatler, Tek Kart Bilgisayarları(SBC'ler), mikrodenetleyiciler hatta ekran kartları dahil)
</h3>


| Ana özellikleri | Teknik Ayrıntıları | Desteklenen kartlar(dan bazıları) |
|-|-|-|
| 💻 Çoğu platform tarafından destekleniyor<br>👥 Arkadaş canlısı ve büyüyen bir topluluk<br>💱 Kullanması & Takas etmesi kolay<br>(DUCO Exchange, Node-S, JustSwap'da)<br>🌎 Heryerde mevcut<br>:new: Tamamen orijinal & açık kaynaklı proje<br>🌳 Acemi & Çevre Dostu<br>💰 Uygun maliyetli & madenciliği kolay | ⚒️ Algoritmalar: DUCO-S1, XXHASH,<br>dahası planlanıyor(PoS dahil)<br>♐ Ödüller: "Kolka sistemi" tarafından,<br>Madencilerin adil bir şekilde ödüllendirilmesine yardımcı olmak adına destekleniyor<br>⚡ Aktarım hızı: Anlık<br>🪙 Maksimum Arz: Sonsuz<br>(Aralık 2020'den önce: 350 bin)<br>(gelecekte yeni limitler berirlenmesi planlandı)<br>🔤 Ticker: DUCO (ᕲ)<br>🔢 Ondalıkları: 20'ye kadar | ♾️ Arduinolar<br>(Uno, Nano, Mega, Due, Pro Mini, vb.)<br>📶 ESP8266'lar<br>(NodeMCU, Wemos, vb.)<br>📶 ESP32'ler<br>(ESP-WROOM, ESP32-CAM, vb.)<br>🍓 Raspberry Pi'lar<br>(1, 2, Zero (W/WH), 3, 4, Pico, 400)<br>🍊 Orange Pi'lar<br>(Zero, Zero 2, PC, Plus, vb.)<br>⚡ Teensy 4.1 kartları |

## Duino-Coin'i kullanmaya başlamak

#### Duino-Coin'i kullanmaya başlamanın en kolay yolu sizin işletim sisteminize uygun [son sürümü indirmek](https://github.com/revoxhere/duino-coin/releases/latest)<br>
İndirmeden sonra, zip paketini açıp istenilen programı başlatın.<br>
Hiçbir bağımlı kütüphane indirmenize gerek yoktur.

Yardıma ihtiyacınız varsa, resmi Duino-Coin'i kullanmaya başlama kılavuzunu <a href="https://duinocoin.com/getting-started">burada</a> bulabilirsiniz.<br>
Sıkça Sorulan Sorular ve hata giderme yolları [burada](https://github.com/revoxhere/duino-coin/wiki).<br>

### Manuel Kurulum

#### Linux

```BASH
sudo apt update
sudo apt install python3 python3-pip git python3-pil python3-pil.imagetk -y # Install dependencies
git clone https://github.com/revoxhere/duino-coin # Clone Duino-Coin repository
cd duino-coin
python3 -m pip install -r requirements.txt # Install pip dependencies
````

Bunu yaptıktan sonra yazılımı Python Yorumlayıcısı ile çalıştırabilirsiniz (`python3 PC_Miner.py` gibi).

#### Windows

1. [Python 3](https://www.python.org/downloads/)'ü indirin ve kurun (Python'u ve Pip'i PATH'e eklediğinizden emin olun)
2. [Duino-Coin deposunu](https://github.com/revoxhere/duino-coin/archive/master.zip) indirin
3. İndirdiğiniz zip arşivini bir klasöre çıkarın ve komut istemini o klasörde başlatın
4. Komut isteminde gerekli kütüphaneleri indirmek için `py -m pip install -r requirements.txt` komutunu çalıştırın

Bunu yaptıktan sonra istediğiniz yazılımı çalıştırabilirsiniz (istediğiniz ´.py´ dosyasına çift tıklayın veya komut isteminde ´py PC_miner.py´ vb. ile çalıştırın).

## Topluluk tarafından geliştirilen yazılımlar

<details>
  <summary>
    Bu liste çok uzadığı için, varsayılan olarak kapalı. Bu yazıya tıklayarak listeyi gösterin!
  </summary>

  ### Duino-Coin ile çalışan diğer madenci yazılımları:
  *   [DuinoCoinbyLabVIEW](https://github.com/ericddm/DuinoCoinbyLabVIEW) - LabVIEW ailesi için ericddm tarafından geliştirilmiş madenci
  *   [Duino-JS](https://github.com/Hoiboy19/Duino-JS) - Hoiboy19 tarafından websitenize kolayca ekleyebileceğiniz bir madenci
  *   [Mineuino](https://github.com/VatsaDev/Mineuino) - VatsaDev tarafınan websitelerinizden para kazanmanızı sağlayan bir yalızım
  *   [hauchel's duco-related stuff repository](https://github.com/hauchel/duco/) - farklı mikronetleyicilerde DUCO kazan yazılımların bir koleksiyonu
  *   [duino-coin-php-miner](https://github.com/ricardofiorani/duino-coin-php-miner) ricardofiorani tarafından Docker'da çalışan bir madenci
  *   [duino-coin-kodi](https://github.com/SandUhrGucker/duino-coin-kodi) - SandUhrGucker tarafından  Kodi Media Center Eklentisi olarak çalışan bir madenci
  *   [MineCryptoOnWifiRouter](https://github.com/BastelPichi/MineCryptoOnWifiRouter) - BastelPichi tarafından Wifi Yönlendiricilerinde madencilik yapmak için bir python scripti
  *   [Duino-Coin_Android_Cluster Miner](https://github.com/DoctorEenot/DuinoCoin_android_cluster) - DoctorEenot tarafından  az bağlantı ile çoklu cihazlanrda madencilik yapmanızı sağlayan bir yazılım
  *   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner) - fabiopolancoe tarafından ESP kartları için MicroPython'da yazılmmış madenci
  *   [DUCO Miner for Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) - PhereloHD & HGEpro tarafından Nintendo 3DS için madenci yazılımı
  *   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) - Alicia426 tarafından Docker içinde çalışan madenci
  *   [nonceMiner](https://github.com/colonelwatch/nonceMiner) - colonelwatch tarafından şu ana kadar ki en hızlı madenci yazılımı
  *   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) - DarkThinking tarafından basit bir NodeJS'de yazılmış madenci
  *   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) - phantom32 & revoxhere tarafından saf C içinde yazılmış madenci
  *   [Go Miner](https://github.com/yippiez/go-miner) yippiez tarafından Go'da yazılmış madenci
  *   [ducominer](https://github.com/its5Q/ducominer) its5Q tarafından
  *   [Resmi Olmayan Madenciler Dizini](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
      *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) revoxhere tarafından
      *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) revoxhere tarafından
      *   [Minimal Python Miner (DUCO-S1)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) revoxhere tarafından
      *   [Minimal Python Miner (XXHASH)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner_XXHASH.py) revoxhere tarafından
      *   [Arduino IDE için Teensy 4.1 code](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Teensy_code/Teensy_code.ino) joaquinbvw tarafından

  ### Diğer araçlar:
  *   [DuinoCoin-balance-Home-Assistant](https://github.com/NL647/DuinoCoin-balance-Home-Assistant) - NL647 tarafından geliştirilen ve Home Assistant'ta mevcut bakiyenizi görmenizi sağlayan bir eklenti
  *   [Duino Coin Status Monitor](https://github.com/TSltd/duino_coin) - TSltd tarafından ESP8266 üzerinde 128x64 SSD1306 OLED kullanan bir yazılım
  *   [ducopanel](https://github.com/ponsato/ducopanel) - ponsato tarafından Duino-Coin madencilerinizi kontrol etmek için bir GUI uygulaması
  *   [Duino AVR Monitör](https://www.microsoft.com/store/apps/9NJ7HPFSR9V5) - niknak tarafından AVR madencileri kontrol etmek için GUI Windows uygulaması 
  *   [Duino-Coin Arduino kütüphanesi](https://github.com/ricaun/arduino-DuinoCoin) ricaun tarafından
  *   [DuinoCoinI2C](https://github.com/ricaun/DuinoCoinI2C) - ricaun tarafından ESP8266'yı Arduinolara master olarak kullanın
  *   [Duino-Coin Madenci Paneli](https://lulaschkas.github.io/duco-mining-dashboard/) Lulaschkas tarafından madencileri monitörlemeye yardımcı
  *   [duco-miners](https://github.com/dansinclair25/duco-miners) dansinclair25 tarafından komut istemi madencilik paneli
  *   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) SandUhrGucker tarafından
  *   [DUCO Tarayıcı Eklentisi](https://github.com/LDarki/DucoExtension) LDarki tarafından Google Chrome ve türevleri için
  *   [DUCO Monitor](https://siunus.github.io/duco-monitor/) siunus tarafından hesap statistikleri
  *   [duino-tools](https://github.com/kyngs/duino-tools) kyngs tarafından Java'da yazılmış araçlar
  *   [Duino Stats](https://github.com/Bilaboz/duino-stats) Bilaboz tarafından resmi Discord Bot'u
  *   [DuCoWallet](https://github.com/viktor02/DuCoWallet) - viktor02 tarafından geliştirilen Cüzdan arayüzü

  Bu liste aktif olarak güncelleniyor. Eğer bu listeye ekleme yapmak isterseniz, bir PR sunun veya geliştiricilerin biri ile iletişime geçin.
  Ayrıca benzer bir listeyi [burada](https://duinocoin.com/apps) bulabilirsiniz.
</details>

## DUCO & wDUCO

Duino-Coin bir hibrit coin'dir, bunun anlamı DUCO'lar wDUCO'ya çevirilebilir' bunu [Tron](https://tron.network) ağını kullanarak yapabilir (bir token olarak). Şu anda harici bir cüzdana aktarmak veya wDUCO'yu Tron blok-zincirindeki başka bir token ile takas yapmak dışında çok kullanımı yok. wDUCO'yu kullanma kılavuzu [wDUCO wikisinde](https://github.com/revoxhere/duino-coin/wiki/wDUCO-tutorial) mevcut.

## Katkıda bulunma

Katkılar açık kaynaklı toplulukları öğrenmek, ilham vermek ve üretmek için harika bir yer yapar.<br>
Duino-Coin'e yaptığınız her bir katkı için size minnetkarız.

Nasıl katkıda bulunabilirim?

*   Bu projeyi fork'layın
*   Kendi özellik branch'inizi oluşturun
*   Katkılarınızı işleyin
*   Her şeyin doğru çalıştığından emin olun
*   Bir pull request açın

Sunucu kaynak kodu, API çağrıları için dokümentasyon ve Duino-Coin'i kendi uygulamalırınızda kullanmak için resmi kütüphaneler [useful tools](https://github.com/revoxhere/duino-coin/tree/useful-tools) branch'inde mevcuttur.

## Resmi olarak kıyaslanmış kartlar ve cihazların listesi

<details>
  <summary>
    Bu liste çok uzadığı için, varsayılan olarak kapalı. Bu yazıya tıklayarak listeyi gösterin!
  </summary>

  | Cihaz/İşlemci/SBC/MCU/çip                                 | Ortalama hashrate<br>(tüm çekirdekler) | Madenci İşlemleri | Güç<br>kullanımı | Ortalama DUCO/gün |
  |-----------------------------------------------------------|-----------------------------------|-------------------|----------------|---------------------|
  | Arduino Pro Mini, Uno, Nano vb.<br>(Atmega 328p/pb/16u2)  | 196 H/s                           | 1                 | 0.2 W          | 9-10                |
  | Teensy 4.1 (yazılım kriptografi)                          | 80 kH/s                           | 1                 | 0.5 W          | -                   |
  | NodeMCU, Wemos D1 etc.<br>(ESP8266)                       | 9.3 kH/s (160MHz) 4.6 kH/s (80Mhz)| 1                 | 0.6 W          | 6-7                 |
  | ESP32                                                     | 23 kH/s                           | 2                 | 1 W            | 8-9                 |
  | Raspberry Pi Zero                                         | 17 kH/s                           | 1                 | 1.1 W          | -                   |
  | Raspberry Pi 3                                            | 440 kH/s                          | 4                 | 5.1 W          | -                   |
  | Raspberry Pi 4                                            | 1.3 MH/s                          | 4                 | 6.4 W          | -                   |
  | ODROID XU4                                                | 1.0 MH/s                          | 8                 | 5 W            | 9                   |
  | Atomic Pi                                                 | 690 kH/s                          | 4                 | 6 W            | -                   |
  | Orange Pi Zero 2                                          | 740 kH/s                          | 4                 | 2.55 W         | -                   |
  | Khadas Vim 2 Pro                                          | 1.12 MH/s                         | 8                 | 6.2 W          | -                   |
  | Libre Computers Tritium H5CC                              | 480 kH/s                          | 4                 | 5 W            | -                   |
  | Libre Computers Le Potato                                 | 410 kH/s                          | 4                 | 5 W            | -                   |
  | Pine64 ROCK64                                             | 640 kH/s                          | 4                 | 5 W            | -                   |
  | Intel Celeron G1840                                       | 1.25 MH/s                         | 2                 | -              | 5-6                 |
  | Intel Core i5-2430M                                       | 1.18 MH/s                         | 4                 | -              | 6.5                 |
  | Intel Core i5-3230M                                       | 1.52 MH/s                         | 4                 | -              | 7.2                 |
  | Intel Core i5-5350U                                       | 1.35 MH/s                         | 4                 | -              | 6.0                 |
  | Intel Core i5-7200U                                       | 1.62 MH/s                         | 4                 | -              | 7.5                 |
  | Intel Core i5-8300H                                       | 3.67 MH/s                         | 8                 | -              | 9.1                 |   
  | Intel Core i3-4130                                        | 1.45 MH/s                         | 4                 | -              | -                   |
  | AMD Ryzen 5 2600                                          | 4.9 MH/s                          | 12                | 67 W           | 15.44               |

  Tüm testler DUCO-S1 algoritması ile yapıldı. Bu tablo aktif olarak güncelleniyor.
</details>


## Lisans

Duino-Coin çoğunlukla MIT Lisansı altında dağıtılıyor. Daha fazla bilgi için `LICENCE` dosyasına göz atın.
Bazı üçüncü-parti dosyalar farklı lisanslar kullanıyor olabilir - lütfen lisanslarına göz atın (çoğunlukla kaynak kodlarının başında yer alır).

## Kullanım Şartları
1. Duino-Coin'ler ("DUCO'lar") madenciler tarafından madencilik ("mining") adı verilen bir işlem sonucunda kazanılır.<br/>
2. Madencilik, DUCO-S1 (veya XXHASH) algoritmasını kullanarak (burada açıklandığı gibi <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>) bir matematik problemine doğru çözümü bulma işine denir.<br/>
3. Madencilik resmi olarak işlemciler(CPU'lar), AVR mikrodenetleyicili kartlar (Arduino kartları gibi), Tek Kart Bilgisayarları (Raspberry Pi kartları gibi), resmi madenci yazılımını kullanarak (diğer resmi olarak izin verilen madenci yazılımları bu README dosyasının üst kısında) ESP8266/32 mikrodenetleyicili kartlar.<br/>
4. Ekran kartları , FPGA veya başka yüksek verimlilikte olan madencileri kullanmak mümkündür ama sadece `EXTREME` madencilik zorluğunda.<br/>
5. Kendi donanımına uygun olmayan zorlukta madencilik yapan kullanıcılar (buraya göz atın <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">zorluk listesi</a>) otomatik olarak uygun zorluk seviyesine geçirilecektir.<br/>
6. Herhangi kullanıcı sürekli olarak düşük zorluk seviyesini kullanmaya çalışacak olursa geçici olarak bloklanabilir.<br/>
7. Bir kullanıcıyı yasaklamak, kullanıcının coinlerine erişimini devre dışı bırakmak ve hesabını silmek olarak tanımlanmıştır.<br/>
8. Sadece yasal olarak elde edilmiş coinler DUCO Exchange'i kullanmaya uygundur.<br/>
9. VPN yada benzeri araçları kötü amaçlı kullanan (mesela limitleri geçmek için) kullanıcılar ihbar verilmeden yasaklanabilir.<br/>
10. Limitleri geçmek için kullanılan çoklu hesaplar ihbar verilmeden yasaklanabilir.<br/>
11. Hesaplar geçici olarak Kullanım Şartları'nın ihlalinin araştırılması için yasaklanabilir.<br/>
12. DUCO Exchange'e yapılan exchange işlemleri ihlal araştırması yapılırken gecikebilir. <br/>
13. Exchange requests made to the offical exchange may be declined due to ToS violations and/or low funding.<br/>
14. Bedava hosting servisleri ile madencilik(bedava VPS'ler, Repl.it veya Github Actions gibi) yasaktır.<br />
15. Bir kullanıcının DUCO'ları bir ihlal kanıtlanabilirse yok edilebilir.<br/>
16. Bu Kullanım Şartları haber verilmeden herhangi bir an değişebilir.<br/>
17. Duino-Coin'i kullanan her kullanıcı bu şartları kabül etmiş sayılır.<br/>
## Gizlilik Politikası
1. Ana sunucuda kullanıcıların sadece kullanıcı adları, şifreleri(bcrypt ile hashlenmiş halde) ve e-postaları saklanır<br/>
2. E-postalar kullanıcılara açık değildir ve sadece kullanıcı ile gerektiğinde iletişim kurmak, <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a>'de exchange isteklerini doğrulamak ve haber e-postası almak için (gelecekte planlanıyor) kullanılır.<br/>
3. Bakiyeler, aktarımlar ve madencilik ile ilgili bilgiler açık <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON API</a>'lerinde açık olarak mevcuttur.<br/>
4. Bu Gizlilik Politikası gelecekte önceden haber verilerek değiştirilebilir.

## Aktif Proje Sorumluları

*   [@revoxhere](https://github.com/revoxhere/) - robik123.345@gmail.com (Ana Python geliştiricisi, proje kurucusu)
*   [@Bilaboz](https://github.com/bilaboz/) (Ana NodeJS geliştiricisi)
*   [@connorhess](https://github.com/connorhess) (Ana Python geliştiricisi, Node-S sahibi)
*   [@JoyBed](https://github.com/JoyBed) (Ana AVR geliştiricisi)
*   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Lead Webmaster and DUCO Developer) <!-- translation wanted -->
##
*   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) geliştiricisi)
*   [@DoctorEenot](https://github.com/DoctorEenot) (Geliştirici)
*   [@LDarki](https://github.com/LDarki) (Web geliştiricisi)
*   [@Lulaschkas](https://github.com/Lulaschkas) (Geliştirici)
*   [@Pripun](https://github.com/Pripun) (Mobil uygulama geliştiricisi)
##
*   [@joaquinbvw](https://github.com/joaquinbvw) (AVR geliştiricisi)

Bu arada Duino-Coin'i geliştirmeye yardımcı olan tüm [Katkıcılara](https://github.com/revoxhere/duino-coin/graphs/contributors) çok teşekkürler.

<hr>

Proje Linki: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)

## Not: Bu README'nin çevirisi tamamen topluluk tarafından yapılmıştır ve tamamen doğru çevrilmiş veya güncel olmayabilir.
