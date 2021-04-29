<!--
*** Official Duino Coin README
*** by revox, 2019-2021
-->

<p align = "center">
  <a href="https://duinocoin.com">
    <img width="80%" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/ducobanner.png?raw=true" />
  </a>
  <br />
  <a href="https://github.com/revoxhere/duino-coin/blob/master/README.md">
    <img src="https://img.shields.io/badge/English-fb6404.svg?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_es_MX.md">
    <img src="https://img.shields.io/badge/-Espa%C3%B1ol-fb6404?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_zh_CN.md">
    <img src="https://img.shields.io/badge/简体中文-fb6404.svg?style=for-the-badge" />
  </a>
  <a href="https://github.com/revoxhere/duino-coin/blob/master/Resources/README_TRANSLATIONS/README_pl_PL.md">
    <img src="https://img.shields.io/badge/Polski-fb6404.svg?style=for-the-badge" />
  </a>
</p>
<br />
<p align = "center">
  <a href="https://wallet.duinocoin.com">
    <img src="https://img.shields.io/badge/Online Wallet-555555.svg?style=for-the-badge" /></a>
  <a href="https://play.google.com/store/apps/details?id=com.pripun.duinocoin">
    <img src="https://img.shields.io/badge/Android App-555555.svg?style=for-the-badge" /></a>
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
  <a href="https://github.com/revoxhere/duino-coin/releases/tag/2.4.5">
    <img src="https://img.shields.io/badge/release-2.4.5-fb6404.svg?style=for-the-badge" /></a>
</p>

<h2 align="center">Duino-Coin es una moneda que puede ser minada con Computadoras, Raspberry Pis, Arduinos, placas ESP, incluso enrutadores WiFI y muchos más.</h2><br />

<table align="center">
  <tr>
    <th>Características clave</th>
    <th>Especificaciones técnicas</th>
  </tr>
  <tr>
    <td>
      💻 Soportada por una gran cantidad de plataformas<br>
      👥 Una comunidad amistosa y en crecimiento<br>
      💱 Fácil de usar e intercambiar<br>
      🌎 Disponible en todos lados<br>
      :new: Proyecto completamente original<br>
      :blush: Amistoso con principiantes<br>
      💰 Rentable<br>
      ⛏️ Fácil de minar<br>
      📚 De código abierto<br>
    </td>
    <td>
      ♾️ Suministro de monedas: Infinito (antes de diciembre de 2020: 350k monedas)<br>
      😎 Preminado: <5k bloques (<500 monedas)<br>
      ⚡ Tiempo de transacción: Instantánea<br>
      🔢 Decimales: hasta 20<br>
      🔤 Ticker: DUCO (ᕲ)<br>
      ⚒️ Algoritmos: DUCO-S1, DUCO-S1A, XXHASH + más planeados<br>
      ♐ Recompensas: soportadas por el "sistema Kolka" ayudando a recompensar a los mineros justamente<br>
    </td>
  </tr>
</table>

<h2 align="center">Comenzar</h2><br>

| Billeteras oficiales | Mineros oficiales |
:-----------------:|:----------------:
[<img src="https://i.imgur.com/msVtLHs.png">](https://duinocoin.com/getting-started#register)  |  [<img src="https://i.imgur.com/SMkKHOK.png">](https://duinocoin.com/getting-started#computer)

#### Las guías oficiales para crear una cuenta y preparar mineros en una variedad de dispositivos están disponibles <a href="https://revoxhere.github.io/duino-coin/getting-started">en el sitio oficial (Inglés)</a>.

<h3 align="center">Instalando Duino-Coin</h2><br>

La forma más fácil de comenzar es descargar [el lanzamiento más nuevo](https://github.com/revoxhere/duino-coin/releases/latest) para tu sistema operativo.<br>
Luego de la descarga, extrae el archivo y lanza el programa deseado.<br>
No hay dependencias requeridas.

<hr>

Su quieres correr los programas desde su código fuente, podrías necesitar instalar algunas dependencias. Aquí están las instrucciones para sistemas basados en Debian(por ejemplo: Ubuntu, Debian, raspbian):
```BASH
sudo apt install python3 python3-pip git
git clone https://github.com/revoxhere/duino-coin
cd duino-coin
python3 -m pip install -r requirements.txt
```
Si estás en Windows, descarga [Python 3](https://www.python.org/downloads/), luego [nuestro repositorio](https://github.com/revoxhere/duino-coin/archive/master.zip), extráelo y abre la línea de comandos. En CMD, escribe:
```BASH
py -m pip install -r requirements.txt
```
Nota para usuarios de Windows: Asegúrense que Python y Pip están agregados a la PATH

Luego de hacer esto, están listos para lanzar el programa (por ejemplo: `python3 PC_Miner.py` O `py PC_Miner.py`).

<hr>

También puedes conseguir el paquete completo de Duino-Coin en AUR - solo instálalo con tu AUR Helper favorito:

```BASH
sudo pacman -S yay
yay -S duino-coin
```

El paquete de Duino-Coin en AUR es mantenido por [PhereloHD](https://github.com/PhereloHD).

<h3 align="center">Software hecho por la comunidad</h3><br>

**Otros mineros que funcionan con Duino-Coin:**
*   [MineCryptoOnWifiRouter](https://github.com/BastelPichi/MineCryptoOnWifiRouter) - Script de Python para minar Duino-Coin en enrutadores por BastelPichi
*   [Duino-Coin_Android_Cluster Miner](https://github.com/DoctorEenot/DuinoCoin_android_cluster) - mina con menos conexiones en múltiples dispositivos por DoctorEenot
*   [ESPython DUCO Miner](https://github.com/fabiopolancoe/ESPython-DUCO-Miner) - Minero MicroPython para dispositivos ESP por fabiopolancoe
*   [DUCO Miner for Nintendo 3DS](https://github.com/BunkerInnovations/duco-3ds) - Minero de Python para Nintento 3DS por PhereloHD y HGEpro
*   [Dockerized DUCO Miner](https://github.com/Alicia426/Dockerized_DUCO_Miner_minimal) - Minero en Docker por Alicia426
*   [nonceMiner](https://github.com/colonelwatch/nonceMiner) - El minero Duino-Coin más rápido disponible por  colonelwatch
*   [NodeJS-DuinoCoin-Miner](https://github.com/DarkThinking/NodeJS-DuinoCoin-Miner/) - Minero NodeJS simple por DarkThinking
*   [d-cpuminer](https://github.com/phantom32-0/d-cpuminer) - Minero en C puro por phantom32
*   [Go Miner](https://github.com/yippiez/go-miner) por yippiez
*   [ducominer](https://github.com/its5Q/ducominer) por its5Q
*   [Directorio de mineros no oficiales](https://github.com/revoxhere/duino-coin/tree/master/Unofficial%20miners)
    *   [Julia Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Julia_Miner.jl) por revox
    *   [Ruby Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Ruby_Miner.rb) por revox
    *   [Minimal Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Minimal_PC_Miner.py) por revox
<!--*   [Multithreaded Python Miner](https://github.com/revoxhere/duino-coin/blob/master/Unofficial%20miners/Multithreaded_PC_Miner.py) por Bilaboz (OBSOLETO) -->

**Otras herramientas:**
<!--*   [Duino-Coin Mining Dashboard](https://lulaschkas.github.io/duco-mining-dashboard/) ayudante de resolución de problemas por Lulaschkas (NO LISTO AÚN) -->
*   [duco-miners](https://github.com/dansinclair25/duco-miners) panel de control de minado CLI por dansinclair25
*   [Duco-Coin Symbol Icon ttf](https://github.com/SandUhrGucker/Duco-Coin-Symbol-Icon-ttf-.h) por SandUhrGucker
*   [DUCO Browser Extension](https://github.com/LDarki/DucoExtension) para Chrome y derivados por LDarki
*   [DUCO Monitor](https://siunus.github.io/duco-monitor/) sitio web de estadísticas de cuenta por siunus
*   [duino-tools](https://github.com/kyngs/duino-tools) escrito en Java por kyngs
*   [Duino Stats](https://github.com/Bilaboz/duino-stats) bot de Discord oficial por Bilaboz
<!--*   [Duino-Coin Auto Updater](https://github.com/Bilaboz/duino-coin-auto-updater) por Bilaboz (OBSOLETO) -->

Esta lista será actualizada activamente (Al menos en la versión en inglés :joy:). Si quieres añadir software a esta lista, envía un PR o contacta a uno de los desarrolladores.

<h3 align="center">Tutorial de wDUCO</h3><br>

wDUCO es DUCO envuelto en la red Tron. Actualmente no hay muchos usos para él, más que solo guardando fondos en otra cartera o intercambiando wDUCO por otro token en JustSwap. Antes de hacer algo, asegúrate que tienes los módulos `tronpy` (tron lib) y `cryptography` (para encriptar la llave privada) para python3 instalados.

### Configurando el Wrapper de wDUCO

1. Abre tu monedero gráfico (de escritorio) o textual (de consola)
2. Si usas la billetera gráfica:
    1. Abre la pestaña de configuraciones
    2. Presiona el botón **Configurar Wrapper**
3. Si usas la billetera textual:
    1. Inicia la configuración del wrapper escribiendo `wrapperconf`
4. Introduce tu clave privada (por ejemplo tu clave tronlink) y establece una contraseña para encriptarla

### Configurando wDUCO en la billetera CLI

### Envolviendo DUCO

Luego de preparar el wrapper en una de las dos carteras, puedes envolver DUCOs (convertirlos en wDUCO).

1. Abre tu billetera
2. Escribe `wrap` para iniciar el proceso de envolvimiento O  haz click en el botón **Envolver DUCO**
3. Sigue las instrucciones mostradas en el monedero

### Desenvolviendo DUCO

Luego de preparar el wrapper en una de las dos carteras, puedes desenvolver wDUCOs (convertirlos en DUCO).
**Nota: ¡asegúrate que tienes algunos TRX en tu monedero por las tarifas!** El desenvolvimiento usará 5 TRX aprox. (~0.5 USD) como tarifas.

1. Abre ti cartera
2. Escribe `unwrap` para iniciar el proceso de desenvolvimiento O haz click en el botón **Desenvolver DUCO**
3. Sigue las instrucciones mostradas en la billetera

<h2 align="center">Desarrollo</h2><br>

Las contribuciones son lo que hacen a la comunidad de código abierto un lugar asombroso para aprender, inspirar y crear.
Cualquier contribución que hagas al proyecto Duino-Coin es muy apreciada.

¿Cómo ayudar?

*   Clona el proyecto
*   Crea tu rama de desarrollo
*   Sube tus cambios
*   Asegúrate de que todo funciona como se espera
*   Abre un Pull Request

El código fuente del servidor, la documentación de las llamadas a la API y las librerías oficiales para desarrollar tus propias aplicaciones para Duino-Coin están disponibles en la rama [useful tools](https://github.com/revoxhere/duino-coin/tree/useful-tools).

<h2 align="center">Alguno de los dispositivos oficialmente probados (DUCO-S1)</h2><br>

*   Arduino Pro Mini / Uno / Nano (ATmega328p con reloj a 16 MHz y 5V): ~155 H/s (15-20 DUCO/día)
*   NodeMCU (ESP8266 con reloj a 160 MHz): ~9.3 kH/s (~4.5 kH/s con reloj a 80 MHz clock) (8-12 DUCO/día)
*   ESP32 (doble-hilo): ~13 kH/s (6 kH/s (núcleo 1) y 7 kH/s (núcleo 2)) (Trabajo en progreso)
*   Raspberry Pi Zero: ~17 kH/s
*   Raspberry Pi 3 (4 hilos): ~440 kH/s
*   Raspberry Pi 4 (4 hilos): ~1.3 MH/s
*   Intel Core i5-3230M (4 hilos): ~1.4 MH/s
*   Intel Core i5-7200U (4 hilos): ~1.6 MH/s

<h2 align="center">Licencia</h2><br>

Duino-Coin está mayormente distribuido bajo la licencia MIT. Ve el archivo `LICENSE` para más información.
Algunos archivos de terceros incluidos podrían tener otras licensias - por favor checa sus declaraciones `LICENSE` (usualmente en la cima de los archivos de código fuente).

<h2 align="center">Términos de servicio</h2><br>
1. Los Duino-Coins ("DUCOs") son ganados con un proceso llamado minado.<br/>
2. El minado se describe como usar el algoritmo DUCO-S1 (explicado en el <a href="https://github.com/revoxhere/duino-coin/blob/gh-pages/assets/whitepaper.pdf">Duino-Coin Whitepaper</a>), en el cual encontrar un resultado correcto a un problema matemático da al minero una recompensa.<br/>
3. La minería se puede hacer oficialmente usando CPUs, placas AVR (como placas Arduino), Computadoras de una sola placa (como placas Raspberry Pi), placas ESP32/8266 usando los mineros oficiales (otros mineros permitidos oficialmente son descritos arriba en el LÉEME/README).<br/>
4. El minado en GPUs, FPGAs y otros dispositivos de alta eficiencia está permitido, pero solo usando la dificultad `EXTREMA` de minado.<br/>
5. Cualquier usuario usando mineros en una dificultad no adecuada para su hardware (mira la <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#socket-api">lista de dificultades</a>) será automáticamente limitado y/o bloqueado.<br/>
6. Cualquier usuario descubierto usando hardware inapropiado o demasiado poderoso será vetado de la red sin previo aviso.<br/>
7. La expulsión implica bloquear al usuario de acceder a sus monedas junto con la eliminación de su cuenta.<br/>
8. Otras monedas ganadas legalmente son elegibles para intercambiar.<br/>
9. Usuarios encontrados usando una VPN (o similar) con intenciones maliciosas (como eludir los límites) podrían ser vetados sin previo aviso.<br/>
10. Múltiples cuentas para eludir los límites pordían ser vetadas sin previo aviso.<br/>
11. Las cuentas podrían ser suspendidas temporalmente para investigar ("investigaciones") violaciones de los términos de servicio ("violación" o "abuso").<br/>
12. Múltiples cuentas utilizadas para eludir expulsiones podrían ser vetadas sin previo aviso.<br/>
13. Una solicitud de cambio hecha al DUCO-Exchange ("el cambio oficial") podrían ser retrasadas y/o rechazadas por investigaciones. <br/>
14. Solcitudes de cambio hechas al cambio oficial podrían ser declinadas por violaciones a los términos de servicio y/o bajos fondos.<br/>
15. Los DUCOs de un usuario podrían ser "quemados" si una violación puede ser probada.<br/>
16. Estos términos de servicio pueden cambiar en cualquier momento sin previo aviso.<br/>
17. Todos los usuarios usando Duino-Coin aceptan cumplir con las anteriores reglas.<br/>
<h4 align="center">Póliza de privacidad</h2><br>
1. En el servidor principal, solo almacenamos nombres de usuario, contraseñas hasheadas (con la ayuda de bcrypt) y correos electrónicos de usuarios como datos de cuenta.<br/>
2. Los correos electrónicos no están disponibles públicamente y solo son usados para contactar usuarios user cuando sea necesario, confirmar cambios en el <a href="https://revoxhere.github.io/duco-exchange/">DUCO-Exchange</a> y recibir noticias ocasionales (planeado para un futuro).<br/>
3. Los balances, transacciones y datos relacionados a la minería son disponibles en las <a href="https://github.com/revoxhere/duino-coin/tree/useful-tools#http-json-api">APIs JSON</a> públicas.<br/>
4. La póliza de privacidad podría ser cambiada en el futuro sin notificación previa.

<h2 align="center">Desarrolladores</h2><br>

*   **Desarrolladores:**
    *   [@revox](https://github.com/revoxhere/) (Fundador/desarrollador principal) - robik123.345@gmail.com
    *   [@Bilaboz](https://github.com/bilaboz/) (Desarrollador principal)
    *   [@connorhess](https://github.com/connorhess) (Desarrollador principal)
    *   [@JoyBed](https://github.com/JoyBed) (Desarrollador principal)
    *   [@HGEcode](https://github.com/HGEcode) (Desarrollador)
    *   [@LDarki](https://github.com/LDarki) (Desarrollador web)
    *   [@travelmode](https://github.com/colonelwatch) (Desarrollador)
    *   [@ygboucherk](https://github.com/ygboucherk) (Desarollador de [wDUCO](https://github.com/ygboucherk/wrapped-duino-coin-v2))
    *   [@Tech1k](https://github.com/Tech1k/) - kristian@beyondcoin.io (Webmaster)
    *   [@EinWildesPanda](https://github.com/EinWildesPanda) (Desarrollador)

*   **Contributors:**
    *   [@5Q](https://github.com/its5Q)
    *   [@kyngs](https://github.com/kyngs)
    *   [@httsmvkcom](https://github.com/httsmvkcom)
    *   [@Nosh-Ware](https://github.com/Nosh-Ware)
    *   [@BastelPichi](https://github.com/BastelPichi)
    *   [@suifengtec](https://github.com/suifengtec)
    *   Gracias a [@Furim](https://github.com/Furim) por ayudar en una etapa temprana del desarrollo
    *   Gracias a [@ATAR4XY](https://www.youtube.com/channel/UC-gf5ejhDuAc_LMxvugPXbg) por diseñar los logos
    *   Gracias a [@Tech1k](https://github.com/Tech1k) por el patrocinio de [Beyondcoin](https://beyondcoin.io) y haber provisto el dominio [duinocoin.com](https://duinocoin.com)
    *   Gracias a [@MrKris7100](https://github.com/MrKris7100) por ayudar a implementar el algoritmo SHA1
    *   Gracias a [@daknuett](https://github.com/daknuett) por ayudar con la librería SHA1 para Arduino

<hr>

Liga del proyecto: [https://github.com/revoxhere/duino-coin/](https://github.com/revoxhere/duino-coin/)
