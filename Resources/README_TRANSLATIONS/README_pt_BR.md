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
  Duino-Coin é uma moeda que pode ser extraída com Arduinos, placas ESP8266/32, Raspberry Pis, computadores e muitos mais (incluindo roteadores Wi-Fi, smart TVs, smartphones, smartwatches, SBCs, MCUs ou até mesmo GPUs)
</h3>


| Principais recursos | Especificações técnicas | (Algumas de muitas) placas suportadas |
|-|-|-|
| 💻 Suportada por um grande número de plataformas<br>👥 Uma comunidade amigável e crescente<br>💱 Fácil de usar e intercambiar<br>🌎 Disponível em qualquer lugar<br>:new: Totalmente original & código aberto<br>:blush: Amistoso com principiantes<br>💰 Rentável<br> ⛏️ Fácil de minerar | ⚒️ Algorítimos: DUCO-S1, XXHASH,<br>mais planejado (incluindo PoS)<br>♐ Recompensas: suportado por "sistema Kolka"<br>ajudando a recompensar os mineradores de forma justa<br>⚡ Tempo de transação: Instantâneo<br>🪙 Fornecimento de moedas: infinito<br>(antes de dezembro de 2020: 350.000 moedas)<br>(novos limites planejados para o futuro)<br>🔤 Ticker: DUCO (ᕲ)<br>🔢 Decimais: up to 20 | ♾️ Arduinos<br>(Uno, Nano, Mega, Due, Pro Mini, etc.)<br>📶 ESP8266s<br>(NodeMCU, Wemos, etc.)<br>📶 ESP32s<br>(ESP-WROOM, ESP32-CAM, etc.)<br>🍓 Raspberry Pis<br>(1, 2, Zero (W/WH), 3, 4, Pico, 400)<br>🍊 Orange Pis<br>(Zero, Zero 2, PC, Plus, etc.)<br>⚡ Teensy 4.1 boards |

## Começando...

#### A maneira mais fácil de começar a usar o Duino-Coin é baixando [a última versão](https://github.com/revoxhere/duino-coin/releases/latest) para o seu sistema operacional.<br>
Depois de baixar o arquivo, descompacte e execute o programa desejado.<br>
Não há dependências necessárias.

Se precisar de ajuda, você pode dar uma olhada nos guias oficiais de primeiros passos localizados <a href="https://duinocoin.com/getting-started">no site oficial</a>.
Perguntas frequentes e ajuda para solução de problemas podem ser encontradas nas [Wikis](https://github.com/revoxhere/duino-coin/wiki).<br>


### Instalação

#### Linux

```BASH
sudo apt update
sudo apt install python3 python3-pip git python3-pil python3-pil.imagetk -y # Install dependencies
git clone https://github.com/revoxhere/duino-coin # Clone Duino-Coin repository
cd duino-coin
python3 -m pip install -r requirements.txt # Install pip dependencies
````

Depois de fazer isso, você está pronto para iniciar o software (e.g. `python3 PC_Miner.py`).


#### Windows

1. Baixar e instalar [Python 3](https://www.python.org/downloads/) (certifique-se de adicionar Python e Pip ao seu PATH)
2. Download [the Duino-Coin repository](https://github.com/revoxhere/duino-coin/archive/master.zip)
3. Extraia o arquivo zip que você baixou e abra a pasta no prompt de comando
4. No prompt de comando digite `py -m pip install -r requirements.txt` para instalar as dependências necessárias do pip

Depois de fazer isso, você está pronto para iniciar o software (apenas clique duas vezes nos arquivos `.py` desejados ou digite ` py PC_Miner.py` no prompt de comando).

## Softwares feitos pela comunidade

<details>
  <summary>
    Como essa lista está ficando muito longa, ela é recolhida por padrão. Clique neste texto para expandi-lo!
  </summary>

  ### Other miners known to work with Duino-Coin:
  *   [Duino-JS](https://github.com/Hoiboy19/Duino-JS) - a JavaScript miner which you can easily implement in your site by Hoiboy19
  *   [Mineuino](https://github.com/VatsaDev/Mineuino) - website monetizer by VatsaDev
  *   [hauchel's duco-related stuff repository](https://github.com/hauchel/duco/) - Collection of various codes for mining DUCO on other microcontrollers
  *   [duino-coin-php-miner](https://github.com/ricardofiorani/duino-coin-php-miner) Dockerized Miner in PHP by ricardofiorani
  *   [duino-coin-kodi](https://github.com/SandUhrGucker/duino-coin-kodi) - Mining addon for Kodi Media Center by SandUhrGucker
  *   [MineCryptoOnWifiRouter](https://github.com/BastelPichi/MineCryptoOnWifiRouter) - Python script to mine Duino-Coin on routers by BastelPichi
  *   [Duino-Coin_Android_Cluster Miner](https://github.com/DoctorEenot/DuinoCoin_android_cluster) - mine with less connections on multiple devices by DoctorEenot
  *   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner) - MicroPython miner for ESP boards by fabiopolancoe
  *   [DUCO Miner for Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) - Python miner for Nintendo 3DS by PhereloHD & HGEpro
  *   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) - Miner in Docker by Alicia426
  *   [nonceMiner](https://github.com/colonelwatch/nonceMiner) - Fastest Duino-Coin miner available by colonelwatch
  *   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) - simple NodeJS miner by DarkThinking
  *   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) - pure C miner by phantom32 & revoxhere
  *   [Go Miner](https://github.com/yippiez/go-miner) by yippiez
  *   [ducominer](https://github.com/its5Q/ducominer) by its5Q
  *   [Unofficial miners directory](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
      *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) by revoxhere
      *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) by revoxhere
      *   [Minimal Python Miner (DUCO-S1)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) by revoxhere
      *   [Minimal Python Miner (XXHASH)](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner_XXHASH.py) by revoxhere
      *   [Teensy 4.1 code for Arduino IDE](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Teensy_code/Teensy_code.ino) by joaquinbvw

  ### Other tools:
  *   [Duino Coin Status Monitor](https://github.com/TSltd/duino_coin) for 128x64 SSD1306 OLED and ESP8266 by TSltd
  *   [ducopanel](https://github.com/ponsato/ducopanel) - a GUI app for controling your Duino-Coin miners by ponsato
  *   [Duino AVR Monitor](https://www.microsoft.com/store/apps/9NJ7HPFSR9V5) - GUI Windows App for monitoring AVR devices mining DUCO by niknak
  *   [Duino-Coin Arduino library](https://github.com/ricaun/arduino-DuinoCoin) by ricaun
  *   [DuinoCoinI2C](https://github.com/ricaun/DuinoCoinI2C) - Use ESP8266 as a master for Arduinos by ricaun
  *   [Duino-Coin Mining Dashboard](https://lulaschkas.github.io/duco-mining-dashboard/) and troubleshooting helper by Lulaschkas
  *   [duco-miners](https://github.com/dansinclair25/duco-miners) CLI mining dashboard made by dansinclair25
  *   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) by SandUhrGucker
  *   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) for Chrome and derivatives by LDarki
  *   [DUCO Monitor](https://siunus.github.io/duco-monitor/) account statistics website by siunus
  *   [duino-tools](https://github.com/kyngs/duino-tools) written in Java by kyngs
  *   [Duino Stats](https://github.com/Bilaboz/duino-stats) official Discord bot by Bilaboz

  This list will be actively updated. If you want to add software to this list, submit a PR or contact one of the developers.
</details>

## DUCO & wDUCO

Duino-Coin é uma moeda híbrida, o que significa que pode ser convertida em wDUCO, que é DUCO empacotado na rede [Tron] (https://tron.network) (como um token). Atualmente não há muitos usos para ele, além de apenas armazenar fundos em uma carteira externa ou trocar wDUCO por outro token no JustSwap. O tutorial sobre como usar wDUCO está disponível no [wDUCO wiki](https://github.com/revoxhere/duino-coin/wiki/wDUCO-tutorial).

## Desenvolvimento

As contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar.<br>
Quaisquer contribuições que você fizer para o projeto Duino-Coin serão muito apreciadas.

Como ajudar?

* Faça um fork do projeto
* Crie seu branch
* Faça seu commit em suas mudanças
* Certifique-se de que tudo funciona como planejado
* Envie seu pull request 

O código-fonte do servidor, a documentação para chamadas de API e bibliotecas oficiais para desenvolver seus próprios aplicativos para Duino-Coin estão disponíveis em [ferramentas úteis](https://github.com/revoxhere/duino-coin/tree/useful-tools).

## Benchmarks de dispositivos e placas testadas oficialmente

<details>
  <summary>
    Como essa tabela está ficando muito longa, ela é recolhida por padrão. Clique neste texto para expandi-lo!
  </summary>

  | Device/CPU/SBC/MCU/chip                                   | Average hashrate<br>(all threads) | Mining<br>threads | Power<br>usage | Average<br>DUCO/day |
  |-----------------------------------------------------------|-----------------------------------|-------------------|----------------|---------------------|
  | Arduino Pro Mini, Uno, Nano etc.<br>(Atmega 328p/pb/16u2) | 196 H/s                           | 1                 | 0.2 W          | 9-10                |
  | Teensy 4.1 (soft cryptography)                            | 80 kH/s                           | 1                 | 0.5 W          | -                   |
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

  All tests were performed using the DUCO-S1 algorithm. This table will be actively updated.
</details>


## Licença

Duino-Coin é distribuído principalmente sob a licença MIT. Veja o arquivo `LICENSE` para mais informações.
Alguns arquivos incluídos de terceiros podem ter licenças diferentes - por favor, verifique suas declarações `LICENSE` (geralmente no topo dos arquivos de código-fonte).

## Termos de serviço
1. Duino-Coins ("Ducos") são ganhos por mineiros com um processo chamado mineração.<br/>
2. A mineração é descrita como o algoritmo Duco-S1 (e XXHash) (conforme explicado no <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), em que encontrar um resultado correto para um problema matemático dá ao mineiro uma recompensa.<br/>
3. A mineração pode ser feita oficialmente usando CPUs, placas AVR (por exemplo, placas Arduino), computadores de placa única (por exemplo, placas Raspberry Pi), placas ESP32/8266 com o uso de mineradores oficiais (outros mineradores oficialmente permitidos são descritos na parte superior do README).<br/>
4. A mineração em GPUs, FPGAs e outros hardwares de alta eficiência é permitida, mas usando apenas a dificuldade de mineração `EXTREME`.<br/>
5. Qualquer usuário usando mineradores em dificuldade não adequada para o seu hardware (consulte o <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">difficulty list</a>) será automaticamente regulado ao ser movido para o nível de dificuldade correto.<br/>
6. Qualquer usuário que continue tentando usar uma dificuldade menor do que o adequado pode ser bloqueado temporariamente.<br/>
7. Banimento envolve bloquear o acesso do usuário às suas moedas junto com a remoção de uma conta.<br/>
8. Apenas moedas ganhas legalmente são elegíveis para a troca.<br/>
9. Os usuários detectados usando uma VPN (ou similar) com intenções maliciosas (por exemplo, ultrapassando os limites) podem ser banidos sem aviso prévio.<br/>
10. Várias contas usadas para contornar os limites podem ser banidas sem aviso prévio.<br/>
11. As contas podem ser suspensas temporariamente para investigar ("investigações") violações dos Termos de Uso ("violação" ou "abuso").<br/>
12. Uma solicitação de troca feita à DUCO-Exchange oficial ("a troca oficial") pode ser atrasada e/ou recusada durante as investigações. <br/>
13. As solicitações de troca feitas para a troca oficial podem ser recusadas devido a violações dos Termos de Uso e/ou baixo financiamento.<br/>
14. A mineração com serviços gratuitos de hospedagem em nuvem (ou serviços VPS gratuitos - por exemplo, Repl.it, Ações GitHub, etc.) não é permitida.<br />
15. Os Ducos de um usuário podem ser queimados se uma violação puder ser comprovada.<br/>
16. Estes Termos de Serviço podem mudar a qualquer momento sem aviso prévio.<br/>
17. Cada usuário usando o Duino-Coin concorda em cumprir as regras acima.<br/>
## Política de Privacidade
1. No servidor mestre, armazenamos apenas nomes de usuário, com senhas hash (com a ajuda de Bcrypt) e e-mails de usuários como dados de sua conta.<br/>
2. E-mails não estão disponíveis publicamente e são usados apenas para entrar em contato com o usuário quando necessário, confirmando as trocas no <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> e recebendo uma newsletter ocasional (planejado para o futuro).<br/>
3. Saldos, transações e dados relacionados à mineração estão disponíveis publicamente no <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">JSON APIs</a>.<br/>
4. A política de privacidade pode ser alterada no futuro com uma notificação prévia.

## Mantenedores de projetos ativos

*   [@revoxhere](https://github.com/revoxhere/) - robik123.345@gmail.com (Lead Python dev, project founder)
*   [@Bilaboz](https://github.com/bilaboz/) (Lead NodeJS dev)
*   [@connorhess](https://github.com/connorhess) (Lead Python dev, Node-S owner)
*   [@JoyBed](https://github.com/JoyBed) (Lead AVR dev)
##
*   [@EinWildesPanda](https://github.com/EinWildesPanda) (Dev)
*   [@ygboucherk](https://github.com/ygboucherk) ([wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2) dev)
*   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Webmaster)
*   [@DoctorEenot](https://github.com/DoctorEenot) (Dev)
##
*   [@HGEcode](https://github.com/HGEcode) (Python dev)
*   [@LDarki](https://github.com/LDarki) (Web dev)
*   [@Lulaschkas](https://github.com/Lulaschkas) (Dev)
*   [@Pripun](https://github.com/Pripun) (Mobile apps dev)
*   [@joaquinbvw](https://github.com/joaquinbvw) (AVR dev)

Um grande agradecimento para todos [Contributors](https://github.com/revoxhere/duino-coin/graphs/contributors) que ajudaram a desenvolver o projeto Duino-Coin.

<hr>

Link do Projeto: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
