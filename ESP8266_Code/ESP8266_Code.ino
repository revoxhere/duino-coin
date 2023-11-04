/*
   ____  __  __  ____  _  _  _____       ___  _____  ____  _  _
  (  _ \(  )(  )(_  _)( \( )(  _  )___  / __)(  _  )(_  _)( \( )
   )(_) ))(__)(  _)(_  )  (  )(_)((___)( (__  )(_)(  _)(_  )  (
  (____/(______)(____)(_)\_)(_____)     \___)(_____)(____)(_)\_)
  Official code for ESP8266 boards                   version 3.5

  Duino-Coin Team & Community 2019-2022 © MIT Licensed
  https://duinocoin.com
  https://github.com/revoxhere/duino-coin

  If you don't know where to start, visit official website and navigate to
  the Getting Started page. Have fun mining!
*/

/* If optimizations cause problems, change them to -O0 (the default)
  NOTE: For even better optimizations also edit your Crypto.h file.
  On linux that file can be found in the following location:
  ~/.arduino15/packages/esp8266/hardware/esp8266/3.0.2/cores/esp8266/ */
#pragma GCC optimize("-Ofast")

/* If during compilation the line below causes a
  "fatal error: arduinoJson.h: No such file or directory"
  message to occur; it means that you do NOT have the
  ArduinoJSON library installed. To install it,
  go to the below link and follow the instructions:
  https://github.com/revoxhere/duino-coin/issues/832 */
#include <ArduinoJson.h>

#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Ticker.h>
#include <ESP8266WebServer.h>

// Uncomment the line below if you wish to use a DHT sensor (Duino IoT beta)
// #define USE_DHT

// Uncomment the line below if you wish to register for IOT updates with an MQTT broker
// #define USE_MQTT

// If you don't know what MQTT means check this link:
// https://www.techtarget.com/iotagenda/definition/MQTT-MQ-Telemetry-Transport

#ifdef USE_DHT
float temp = 0.0;
float hum = 0.0;

// Install "DHT sensor library" if you get an error
#include <DHT.h>
// Change D3 to the pin you've connected your sensor to
#define DHTPIN D3
// Set DHT11 or DHT22 accordingly
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
#endif

#ifdef USE_MQTT
// Install "PubSubClient" if you get an error
#include <PubSubClient.h>

long lastMsg = 0;

// Change the part in brackets to your MQTT broker address
#define mqtt_server "broker.hivemq.com"
// broker.hivemq.com is for testing purposes, change it to your broker address

// Change this to your MQTT broker port
#define mqtt_port 1883
// If you want to use user and password for your MQTT broker, uncomment the line below
// #define mqtt_use_credentials

// Change the part in brackets to your MQTT broker username
#define mqtt_user "My cool mqtt username"
// Change the part in brackets to your MQTT broker password
#define mqtt_password "My secret mqtt pass"

// Change this if you want to send data to the topic every X milliseconds
#define mqtt_update_time 5000

// Change the part in brackets to your MQTT humidity topic
#define humidity_topic "sensor/humidity"
// Change the part in brackets to your MQTT temperature topic
#define temperature_topic "sensor/temperature"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void mqttReconnect()
{
  // Loop until we're reconnected
  while (!mqttClient.connected())
  {
    Serial.print("Attempting MQTT connection...");

    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);

    // Attempt to connect
#ifdef mqtt_use_credentials
    if (mqttClient.connect("ESP8266Client", mqtt_user, mqtt_password))
#else
    if (mqttClient.connect(clientId.c_str()))
#endif
    {
      Serial.println("connected");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
#endif

namespace
{
  // Change the part in brackets to your Duino-Coin username
  const char DUCO_USER[] = "USERNAME";
  // Change the part in brackets to your mining key (if you have enabled it in the wallet)
  const char MINER_KEY[] = "MINING_KEY";
  // Change the part in brackets to your WiFi name
  const char SSID[] = "WIFI_NAME";
  // Change the part in brackets to your WiFi password
  const char PASSWORD[] = "WIFI_PASSWORD";
  // Change the part in brackets if you want to set a custom miner name (use Auto to autogenerate, None for no name)
  const char *RIG_IDENTIFIER = "None";
  // Set to true to use the 160 MHz overclock mode (and not get the first share rejected)
  const bool USE_HIGHER_DIFF = true;
  // Set to true if you want to host the dashboard page (available on ESPs IP address)
  const bool WEB_DASHBOARD = false;
  // Set to true if you want to update hashrate in browser without reloading the page
  const bool WEB_HASH_UPDATER = false;
  // Set to false if you want to disable the onboard led blinking when finding shares
  const bool LED_BLINKING = true;

  /* Do not change the lines below. These lines are static and dynamic variables
     that will be used by the program for counters and measurements. */
  const char *DEVICE = "ESP8266";
  const char *POOLPICKER_URL[] = {"https://server.duinocoin.com/getPool"};
  const char *MINER_BANNER = "Official ESP8266 Miner";
  const char *MINER_VER = "3.5";
  unsigned int share_count = 0;
  unsigned int port = 0;
  unsigned int difficulty = 0;
  float hashrate = 0;
  String AutoRigName = "";
  String host = "";
  String node_id = "";

  const char WEBSITE[] PROGMEM = R"=====(
<!DOCTYPE html>
<html>
<!--
    Duino-Coin self-hosted dashboard
    MIT licensed
    Duino-Coin official 2019-2022
    https://github.com/revoxhere/duino-coin
    https://duinocoin.com
-->
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Duino-Coin @@DEVICE@@ dashboard</title>
    <link rel="stylesheet" href="https://server.duinocoin.com/assets/css/mystyles.css">
    <link rel="shortcut icon" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
    <link rel="icon" type="image/png" href="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
</head>
<body>
    <section class="section">
        <div class="container">
            <h1 class="title">
                <img class="icon" src="https://github.com/revoxhere/duino-coin/blob/master/Resources/duco.png?raw=true">
                @@DEVICE@@ <small>(@@ID@@)</small>
            </h1>
            <p class="subtitle">
                Self-hosted, lightweight, official dashboard for your <strong>Duino-Coin</strong> miner
            </p>
        </div>
        <br>
        <div class="container">
            <div class="columns">
                <div class="column">
                    <div class="box">
                        <p class="subtitle">
                            Mining statistics
                        </p>
                        <div class="columns is-multiline">
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    <span id="hashratex">@@HASHRATE@@</span>kH/s
                                </div>
                                <div class="heading is-size-5">
                                    Hashrate
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@DIFF@@
                                </div>
                                <div class="heading is-size-5">
                                    Difficulty
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@SHARES@@
                                </div>
                                <div class="heading is-size-5">
                                    Shares
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@NODE@@
                                </div>
                                <div class="heading is-size-5">
                                    Node
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="column">
                    <div class="box">
                        <p class="subtitle">
                            Device information
                        </p>
                        <div class="columns is-multiline">
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@DEVICE@@
                                </div>
                                <div class="heading is-size-5">
                                    Device type
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@ID@@
                                </div>
                                <div class="heading is-size-5">
                                    Device ID
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@MEMORY@@
                                </div>
                                <div class="heading is-size-5">
                                    Free memory
                                </div>
                            </div>
                            <div class="column" style="min-width:15em">
                                <div class="title is-size-5 mb-0">
                                    @@VERSION@@
                                </div>
                                <div class="heading is-size-5">
                                    Miner version
                                </div>
                            </div>
)====="
#ifdef USE_DHT
                                 "                            <div class=\"column\" style=\"min-width:15em\">"
                                 "                                <div class=\"title is-size-5 mb-0\">"
                                 "                                    @@TEMP@@ °C"
                                 "                                </div>"
                                 "                                <div class=\"heading is-size-5\">"
                                 "                                    Temperature"
                                 "                                </div>"
                                 "                            </div>"
                                 "                            <div class=\"column\" style=\"min-width:15em\">"
                                 "                                <div class=\"title is-size-5 mb-0\">"
                                 "                                    @@HUM@@ %"
                                 "                                </div>"
                                 "                                <div class=\"heading is-size-5\">"
                                 "                                    Humidity"
                                 "                                </div>"
                                 "                            </div>"
#endif
                                 R"=====(
                        </div>
                    </div>
                </div>
            </div>
            <br>
            <div class="has-text-centered">
                <div class="title is-size-6 mb-0">
                    Hosted on
                    <a href="http://@@IP_ADDR@@">
                        http://<b>@@IP_ADDR@@</b>
                    </a>
                    &bull;
                    <a href="https://duinocoin.com">
                        duinocoin.com
                    </a>
                    &bull;
                    <a href="https://github.com/revoxhere/duino-coin">
                        github.com/revoxhere/duino-coin
                    </a>
                </div>
            </div>
        </div>
        <script>
            setInterval(function(){
                getData();
            }, 3000);
            
            function getData() {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        document.getElementById("hashratex").innerHTML = this.responseText;
                    }
                };
                xhttp.open("GET", "hashrateread", true);
                xhttp.send();
            }
        </script>
    </section>
</body>
</html>
)=====";

  ESP8266WebServer server(80);

  void hashupdater()
  { // update hashrate every 3 sec in browser without reloading page
    server.send(200, "text/plain", String(hashrate / 1000));
    Serial.println("Update hashrate on page");
  };

  void UpdateHostPort(String input)
  {
    // Thanks @ricaun for the code
    DynamicJsonDocument doc(256);
    deserializeJson(doc, input);
    const char *name = doc["name"];

    host = doc["ip"].as<String>().c_str();
    port = doc["port"].as<int>();
    node_id = String(name);

    Serial.println("Poolpicker selected the best mining node: " + node_id);
  }

  String httpGetString(String URL)
  {
    String payload = "";
    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;

    if (http.begin(client, URL))
    {
      int httpCode = http.GET();

      if (httpCode == HTTP_CODE_OK)
        payload = http.getString();
      else
        Serial.printf("Error fetching node from poolpicker: %s\n", http.errorToString(httpCode).c_str());

      http.end();
    }
    return payload;
  }

  void UpdatePool()
  {
    String input = "";
    int waitTime = 1;
    int poolIndex = 0;
    int poolSize = sizeof(POOLPICKER_URL) / sizeof(char *);

    while (input == "")
    {
      Serial.println("Fetching mining node from the poolpicker in " + String(waitTime) + "s");
      input = httpGetString(POOLPICKER_URL[poolIndex]);
      poolIndex += 1;

      // Check if pool index needs to roll over
      if (poolIndex >= poolSize)
      {
        poolIndex %= poolSize;
        delay(waitTime * 1000);

        // Increase wait time till a maximum of 32 seconds (addresses: Limit connection requests on failure in ESP boards #1041)
        waitTime *= 2;
        if (waitTime > 32)
          waitTime = 32;
      }
    }

    // Setup pool with new input
    UpdateHostPort(input);
  }

  WiFiClient client;
  String client_buffer = "";
  String chipID = "";
  String START_DIFF = "";

  // Loop WDT... please don't feed me...
  // See lwdtcb() and lwdtFeed() below
  Ticker lwdTimer;
#define LWD_TIMEOUT 90000

  unsigned long lwdCurrentMillis = 0;
  unsigned long lwdTimeOutMillis = LWD_TIMEOUT;

#define END_TOKEN '\n'
#define SEP_TOKEN ','

#define LED_BUILTIN 2

#define BLINK_SETUP_COMPLETE 2
#define BLINK_CLIENT_CONNECT 3
#define BLINK_RESET_DEVICE 5

  template <unsigned int max_digits>
  class Counter
  {
  public:
    Counter() { reset(); }

    void reset()
    {
      memset(buffer, '0', max_digits);
      buffer[max_digits] = '\0';
      val = 0;
      len = 1;
    }

    inline Counter &operator++()
    {
      inc_string(buffer + max_digits - 1);
      ++val;
      return *this;
    }

    inline operator unsigned int() const { return val; }
    inline const char *c_str() const { return buffer + max_digits - len; }
    inline size_t strlen() const { return len; }

  protected:
    inline void inc_string(char *c)
    {
      // In theory, the line below should be uncommented to avoid writing outside the buffer.  In practice however,
      // with max_digits set to 10 or more, we can fit all possible unsigned 32-bit integers in the buffer.  The
      // check is skipped to gain a small extra speed improvement.
      // if (c >= buffer) return;

      if (*c < '9')
      {
        *c += 1;
      }
      else
      {
        *c = '0';
        inc_string(c - 1);
        len = max(max_digits - (c - buffer) + 1, len);
      }
    }

  protected:
    char buffer[max_digits + 1];
    unsigned int val;
    size_t len;
  };

  void SetupWifi()
  {
    Serial.println("Connecting to: " + String(SSID));
    WiFi.mode(WIFI_STA); // Setup ESP in client mode
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    WiFi.begin(SSID, PASSWORD);

    int wait_passes = 0;
    while (WiFi.waitForConnectResult() != WL_CONNECTED)
    {
      delay(500);
      Serial.print(".");
      if (++wait_passes >= 10)
      {
        WiFi.begin(SSID, PASSWORD);
        wait_passes = 0;
      }
    }

    Serial.println("\n\nSuccessfully connected to WiFi");
    Serial.println("Local IP address: " + WiFi.localIP().toString());
    Serial.println("Rig name: " + String(RIG_IDENTIFIER));
    Serial.println();

    UpdatePool();
  }

  void SetupOTA()
  {
    // Prepare OTA handler
    ArduinoOTA.onStart([]()
                       { Serial.println("Start"); });
    ArduinoOTA.onEnd([]()
                     { Serial.println("\nEnd"); });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
                          { Serial.printf("Progress: %u%%\r", (progress / (total / 100))); });
    ArduinoOTA.onError([](ota_error_t error)
                       {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed"); });

    ArduinoOTA.setHostname(RIG_IDENTIFIER); // Give port a name not just address
    ArduinoOTA.begin();
  }

  void blink(uint8_t count, uint8_t pin = LED_BUILTIN)
  {
    if (LED_BLINKING)
    {
      uint8_t state = HIGH;

      for (int x = 0; x < (count << 1); ++x)
      {
        digitalWrite(pin, state ^= HIGH);
        delay(50);
      }
    }
    else
    {
      digitalWrite(LED_BUILTIN, HIGH);
    }
  }

  void RestartESP(String msg)
  {
    Serial.println(msg);
    Serial.println("Restarting ESP...");
    blink(BLINK_RESET_DEVICE);
    ESP.reset();
  }

  // Our new WDT to help prevent freezes
  // code concept taken from https://sigmdel.ca/michel/program/esp8266/arduino/watchdogs2_en.html
  void IRAM_ATTR lwdtcb(void)
  {
    if ((millis() - lwdCurrentMillis > LWD_TIMEOUT) || (lwdTimeOutMillis - lwdCurrentMillis != LWD_TIMEOUT))
      RestartESP("Loop WDT Failed!");
  }

  void lwdtFeed(void)
  {
    lwdCurrentMillis = millis();
    lwdTimeOutMillis = lwdCurrentMillis + LWD_TIMEOUT;
  }

  void VerifyWifi()
  {
    while (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0, 0, 0, 0))
      WiFi.reconnect();
  }

  void handleSystemEvents(void)
  {
    VerifyWifi();
    ArduinoOTA.handle();
    yield();
  }

  void waitForClientData(void)
  {
    client_buffer = "";

    while (client.connected())
    {
      if (client.available())
      {
        client_buffer = client.readStringUntil(END_TOKEN);
        if (client_buffer.length() == 1 && client_buffer[0] == END_TOKEN)
          client_buffer = "???\n"; // NOTE: Should never happen

        break;
      }
      handleSystemEvents();
    }
  }

  void ConnectToServer()
  {
    if (client.connected())
      return;

    Serial.println("\n\nConnecting to the Duino-Coin server...");
    while (!client.connect(host.c_str(), port))
      ;

    waitForClientData();
    Serial.println("Connected to the server. Server version: " + client_buffer);
    blink(BLINK_CLIENT_CONNECT); // Sucessfull connection with the server
  }

  bool max_micros_elapsed(unsigned long current, unsigned long max_elapsed)
  {
    static unsigned long _start = 0;

    if ((current - _start) > max_elapsed)
    {
      _start = current;
      return true;
    }
    return false;
  }

  void dashboard()
  {
    Serial.println("Handling HTTP client");

    String s = WEBSITE;
    s.replace("@@IP_ADDR@@", WiFi.localIP().toString());

    s.replace("@@HASHRATE@@", String(hashrate / 1000));
    s.replace("@@DIFF@@", String(difficulty / 100));
    s.replace("@@SHARES@@", String(share_count));
    s.replace("@@NODE@@", String(node_id));

    s.replace("@@DEVICE@@", String(DEVICE));
    s.replace("@@ID@@", String(RIG_IDENTIFIER));
    s.replace("@@MEMORY@@", String(ESP.getFreeHeap()));
    s.replace("@@VERSION@@", String(MINER_VER));
#ifdef USE_DHT
    s.replace("@@TEMP@@", String(temp));
    s.replace("@@HUM@@", String(hum));
#endif
    server.send(200, "text/html", s);
  }

} // namespace

// https://github.com/esp8266/Arduino/blob/master/cores/esp8266/TypeConversion.cpp
const char base36Chars[36] PROGMEM = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};
const uint8_t base36CharValues[75] PROGMEM{
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0,                                                                        // 0 to 9
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 0, 0, 0, 0, 0, 0, // Upper case letters
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35                    // Lower case letters
};

uint8_t *hexStringToUint8Array(const String &hexString, uint8_t *uint8Array, const uint32_t arrayLength)
{
  assert(hexString.length() >= arrayLength * 2);
  const char *hexChars = hexString.c_str();
  for (uint32_t i = 0; i < arrayLength; ++i)
  {
    uint8Array[i] = (pgm_read_byte(base36CharValues + hexChars[i * 2] - '0') << 4) + pgm_read_byte(base36CharValues + hexChars[i * 2 + 1] - '0');
  }
  return uint8Array;
}

struct MiningJob
{
  String last_block_hash;
  String expected_hash_str;
  uint8_t expected_hash[20];
  unsigned int difficulty;

  bool parse(const char *job_str)
  {
    // Create a non-constant copy of the input string
    char *job_str_copy = strdup(job_str);

    if (job_str_copy)
    {
      String tokens[3];
      char *token = strtok(job_str_copy, ",");
      for (int i = 0; token != NULL && i < 3; i++)
      {
        tokens[i] = token;
        token = strtok(NULL, ",");
      }

      last_block_hash = tokens[0];
      expected_hash_str = tokens[1];
      hexStringToUint8Array(expected_hash_str, expected_hash, 20);
      difficulty = tokens[2].toInt() * 100 + 1;

      // Free the memory allocated by strdup
      free(job_str_copy);

      return true;
    }
    else
    {
      // Handle memory allocation failure
      return false;
    }
  }
};

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

class DSHA1
{
public:
  static const size_t OUTPUT_SIZE = 20;

  DSHA1()
  {
    initialize(s);
  }

  DSHA1 &write(const unsigned char *data, size_t len)
  {
    size_t bufsize = bytes % 64;
    if (bufsize && bufsize + len >= 64)
    {
      memcpy(buf + bufsize, data, 64 - bufsize);
      bytes += 64 - bufsize;
      data += 64 - bufsize;
      transform(s, buf);
      bufsize = 0;
    }
    while (len >= 64)
    {
      transform(s, data);
      bytes += 64;
      data += 64;
      len -= 64;
    }
    if (len > 0)
    {
      memcpy(buf + bufsize, data, len);
      bytes += len;
    }
    return *this;
  }

  void finalize(unsigned char hash[OUTPUT_SIZE])
  {
    const unsigned char pad[64] = {0x80};
    unsigned char sizedesc[8];
    writeBE64(sizedesc, bytes << 3);
    write(pad, 1 + ((119 - (bytes % 64)) % 64));
    write(sizedesc, 8);
    writeBE32(hash, s[0]);
    writeBE32(hash + 4, s[1]);
    writeBE32(hash + 8, s[2]);
    writeBE32(hash + 12, s[3]);
    writeBE32(hash + 16, s[4]);
  }

  DSHA1 &reset()
  {
    bytes = 0;
    initialize(s);
    return *this;
  }

  // it's a way to warmup the cache and gather a bit boost in performances
  DSHA1 &warmup()
  {
    uint8_t warmup[20];
    this->write((uint8_t *)"warmup", 6).finalize(warmup);
    return *this;
  }

private:
  uint32_t s[5];
  unsigned char buf[64];
  uint64_t bytes;

  const uint32_t k1 = 0x5A827999ul;
  const uint32_t k2 = 0x6ED9EBA1ul;
  const uint32_t k3 = 0x8F1BBCDCul;
  const uint32_t k4 = 0xCA62C1D6ul;

  uint32_t inline f1(uint32_t b, uint32_t c, uint32_t d) { return d ^ (b & (c ^ d)); }
  uint32_t inline f2(uint32_t b, uint32_t c, uint32_t d) { return b ^ c ^ d; }
  uint32_t inline f3(uint32_t b, uint32_t c, uint32_t d) { return (b & c) | (d & (b | c)); }

  uint32_t inline left(uint32_t x) { return (x << 1) | (x >> 31); }

  void inline Round(uint32_t a, uint32_t &b, uint32_t c, uint32_t d, uint32_t &e, uint32_t f, uint32_t k, uint32_t w)
  {
    e += ((a << 5) | (a >> 27)) + f + k + w;
    b = (b << 30) | (b >> 2);
  }

  void initialize(uint32_t s[5])
  {
    s[0] = 0x67452301ul;
    s[1] = 0xEFCDAB89ul;
    s[2] = 0x98BADCFEul;
    s[3] = 0x10325476ul;
    s[4] = 0xC3D2E1F0ul;
  }

  void transform(uint32_t *s, const unsigned char *chunk)
  {
    uint32_t a = s[0], b = s[1], c = s[2], d = s[3], e = s[4];
    uint32_t w0, w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14, w15;

    Round(a, b, c, d, e, f1(b, c, d), k1, w0 = readBE32(chunk + 0));
    Round(e, a, b, c, d, f1(a, b, c), k1, w1 = readBE32(chunk + 4));
    Round(d, e, a, b, c, f1(e, a, b), k1, w2 = readBE32(chunk + 8));
    Round(c, d, e, a, b, f1(d, e, a), k1, w3 = readBE32(chunk + 12));
    Round(b, c, d, e, a, f1(c, d, e), k1, w4 = readBE32(chunk + 16));
    Round(a, b, c, d, e, f1(b, c, d), k1, w5 = readBE32(chunk + 20));
    Round(e, a, b, c, d, f1(a, b, c), k1, w6 = readBE32(chunk + 24));
    Round(d, e, a, b, c, f1(e, a, b), k1, w7 = readBE32(chunk + 28));
    Round(c, d, e, a, b, f1(d, e, a), k1, w8 = readBE32(chunk + 32));
    Round(b, c, d, e, a, f1(c, d, e), k1, w9 = readBE32(chunk + 36));
    Round(a, b, c, d, e, f1(b, c, d), k1, w10 = readBE32(chunk + 40));
    Round(e, a, b, c, d, f1(a, b, c), k1, w11 = readBE32(chunk + 44));
    Round(d, e, a, b, c, f1(e, a, b), k1, w12 = readBE32(chunk + 48));
    Round(c, d, e, a, b, f1(d, e, a), k1, w13 = readBE32(chunk + 52));
    Round(b, c, d, e, a, f1(c, d, e), k1, w14 = readBE32(chunk + 56));
    Round(a, b, c, d, e, f1(b, c, d), k1, w15 = readBE32(chunk + 60));

    Round(e, a, b, c, d, f1(a, b, c), k1, w0 = left(w0 ^ w13 ^ w8 ^ w2));
    Round(d, e, a, b, c, f1(e, a, b), k1, w1 = left(w1 ^ w14 ^ w9 ^ w3));
    Round(c, d, e, a, b, f1(d, e, a), k1, w2 = left(w2 ^ w15 ^ w10 ^ w4));
    Round(b, c, d, e, a, f1(c, d, e), k1, w3 = left(w3 ^ w0 ^ w11 ^ w5));
    Round(a, b, c, d, e, f2(b, c, d), k2, w4 = left(w4 ^ w1 ^ w12 ^ w6));
    Round(e, a, b, c, d, f2(a, b, c), k2, w5 = left(w5 ^ w2 ^ w13 ^ w7));
    Round(d, e, a, b, c, f2(e, a, b), k2, w6 = left(w6 ^ w3 ^ w14 ^ w8));
    Round(c, d, e, a, b, f2(d, e, a), k2, w7 = left(w7 ^ w4 ^ w15 ^ w9));
    Round(b, c, d, e, a, f2(c, d, e), k2, w8 = left(w8 ^ w5 ^ w0 ^ w10));
    Round(a, b, c, d, e, f2(b, c, d), k2, w9 = left(w9 ^ w6 ^ w1 ^ w11));
    Round(e, a, b, c, d, f2(a, b, c), k2, w10 = left(w10 ^ w7 ^ w2 ^ w12));
    Round(d, e, a, b, c, f2(e, a, b), k2, w11 = left(w11 ^ w8 ^ w3 ^ w13));
    Round(c, d, e, a, b, f2(d, e, a), k2, w12 = left(w12 ^ w9 ^ w4 ^ w14));
    Round(b, c, d, e, a, f2(c, d, e), k2, w13 = left(w13 ^ w10 ^ w5 ^ w15));
    Round(a, b, c, d, e, f2(b, c, d), k2, w14 = left(w14 ^ w11 ^ w6 ^ w0));
    Round(e, a, b, c, d, f2(a, b, c), k2, w15 = left(w15 ^ w12 ^ w7 ^ w1));

    Round(d, e, a, b, c, f2(e, a, b), k2, w0 = left(w0 ^ w13 ^ w8 ^ w2));
    Round(c, d, e, a, b, f2(d, e, a), k2, w1 = left(w1 ^ w14 ^ w9 ^ w3));
    Round(b, c, d, e, a, f2(c, d, e), k2, w2 = left(w2 ^ w15 ^ w10 ^ w4));
    Round(a, b, c, d, e, f2(b, c, d), k2, w3 = left(w3 ^ w0 ^ w11 ^ w5));
    Round(e, a, b, c, d, f2(a, b, c), k2, w4 = left(w4 ^ w1 ^ w12 ^ w6));
    Round(d, e, a, b, c, f2(e, a, b), k2, w5 = left(w5 ^ w2 ^ w13 ^ w7));
    Round(c, d, e, a, b, f2(d, e, a), k2, w6 = left(w6 ^ w3 ^ w14 ^ w8));
    Round(b, c, d, e, a, f2(c, d, e), k2, w7 = left(w7 ^ w4 ^ w15 ^ w9));
    Round(a, b, c, d, e, f3(b, c, d), k3, w8 = left(w8 ^ w5 ^ w0 ^ w10));
    Round(e, a, b, c, d, f3(a, b, c), k3, w9 = left(w9 ^ w6 ^ w1 ^ w11));
    Round(d, e, a, b, c, f3(e, a, b), k3, w10 = left(w10 ^ w7 ^ w2 ^ w12));
    Round(c, d, e, a, b, f3(d, e, a), k3, w11 = left(w11 ^ w8 ^ w3 ^ w13));
    Round(b, c, d, e, a, f3(c, d, e), k3, w12 = left(w12 ^ w9 ^ w4 ^ w14));
    Round(a, b, c, d, e, f3(b, c, d), k3, w13 = left(w13 ^ w10 ^ w5 ^ w15));
    Round(e, a, b, c, d, f3(a, b, c), k3, w14 = left(w14 ^ w11 ^ w6 ^ w0));
    Round(d, e, a, b, c, f3(e, a, b), k3, w15 = left(w15 ^ w12 ^ w7 ^ w1));

    Round(c, d, e, a, b, f3(d, e, a), k3, w0 = left(w0 ^ w13 ^ w8 ^ w2));
    Round(b, c, d, e, a, f3(c, d, e), k3, w1 = left(w1 ^ w14 ^ w9 ^ w3));
    Round(a, b, c, d, e, f3(b, c, d), k3, w2 = left(w2 ^ w15 ^ w10 ^ w4));
    Round(e, a, b, c, d, f3(a, b, c), k3, w3 = left(w3 ^ w0 ^ w11 ^ w5));
    Round(d, e, a, b, c, f3(e, a, b), k3, w4 = left(w4 ^ w1 ^ w12 ^ w6));
    Round(c, d, e, a, b, f3(d, e, a), k3, w5 = left(w5 ^ w2 ^ w13 ^ w7));
    Round(b, c, d, e, a, f3(c, d, e), k3, w6 = left(w6 ^ w3 ^ w14 ^ w8));
    Round(a, b, c, d, e, f3(b, c, d), k3, w7 = left(w7 ^ w4 ^ w15 ^ w9));
    Round(e, a, b, c, d, f3(a, b, c), k3, w8 = left(w8 ^ w5 ^ w0 ^ w10));
    Round(d, e, a, b, c, f3(e, a, b), k3, w9 = left(w9 ^ w6 ^ w1 ^ w11));
    Round(c, d, e, a, b, f3(d, e, a), k3, w10 = left(w10 ^ w7 ^ w2 ^ w12));
    Round(b, c, d, e, a, f3(c, d, e), k3, w11 = left(w11 ^ w8 ^ w3 ^ w13));
    Round(a, b, c, d, e, f2(b, c, d), k4, w12 = left(w12 ^ w9 ^ w4 ^ w14));
    Round(e, a, b, c, d, f2(a, b, c), k4, w13 = left(w13 ^ w10 ^ w5 ^ w15));
    Round(d, e, a, b, c, f2(e, a, b), k4, w14 = left(w14 ^ w11 ^ w6 ^ w0));
    Round(c, d, e, a, b, f2(d, e, a), k4, w15 = left(w15 ^ w12 ^ w7 ^ w1));

    Round(b, c, d, e, a, f2(c, d, e), k4, w0 = left(w0 ^ w13 ^ w8 ^ w2));
    Round(a, b, c, d, e, f2(b, c, d), k4, w1 = left(w1 ^ w14 ^ w9 ^ w3));
    Round(e, a, b, c, d, f2(a, b, c), k4, w2 = left(w2 ^ w15 ^ w10 ^ w4));
    Round(d, e, a, b, c, f2(e, a, b), k4, w3 = left(w3 ^ w0 ^ w11 ^ w5));
    Round(c, d, e, a, b, f2(d, e, a), k4, w4 = left(w4 ^ w1 ^ w12 ^ w6));
    Round(b, c, d, e, a, f2(c, d, e), k4, w5 = left(w5 ^ w2 ^ w13 ^ w7));
    Round(a, b, c, d, e, f2(b, c, d), k4, w6 = left(w6 ^ w3 ^ w14 ^ w8));
    Round(e, a, b, c, d, f2(a, b, c), k4, w7 = left(w7 ^ w4 ^ w15 ^ w9));
    Round(d, e, a, b, c, f2(e, a, b), k4, w8 = left(w8 ^ w5 ^ w0 ^ w10));
    Round(c, d, e, a, b, f2(d, e, a), k4, w9 = left(w9 ^ w6 ^ w1 ^ w11));
    Round(b, c, d, e, a, f2(c, d, e), k4, w10 = left(w10 ^ w7 ^ w2 ^ w12));
    Round(a, b, c, d, e, f2(b, c, d), k4, w11 = left(w11 ^ w8 ^ w3 ^ w13));
    Round(e, a, b, c, d, f2(a, b, c), k4, w12 = left(w12 ^ w9 ^ w4 ^ w14));
    Round(d, e, a, b, c, f2(e, a, b), k4, left(w13 ^ w10 ^ w5 ^ w15));
    Round(c, d, e, a, b, f2(d, e, a), k4, left(w14 ^ w11 ^ w6 ^ w0));
    Round(b, c, d, e, a, f2(c, d, e), k4, left(w15 ^ w12 ^ w7 ^ w1));

    s[0] += a;
    s[1] += b;
    s[2] += c;
    s[3] += d;
    s[4] += e;
  }

  uint32_t static inline readBE32(const unsigned char *ptr)
  {
    return __builtin_bswap32(*(uint32_t *)ptr);
  }

  void static inline writeBE32(unsigned char *ptr, uint32_t x)
  {
    *(uint32_t *)ptr = __builtin_bswap32(x);
  }

  void static inline writeBE64(unsigned char *ptr, uint64_t x)
  {
    *(uint64_t *)ptr = __builtin_bswap64(x);
  }
};

DSHA1 sha1_ctx_base = DSHA1().warmup();

void setup()
{
  Serial.begin(500000);
  Serial.println("\nDuino-Coin " + String(MINER_VER));
  pinMode(LED_BUILTIN, OUTPUT);

#ifdef USE_MQTT
  mqttClient.setServer(mqtt_server, mqtt_port);
#endif

#ifdef USE_DHT
  Serial.println("Initializing DHT sensor");
  dht.begin();
  Serial.println("Test reading: " + String(dht.readHumidity()) + "% humidity");
  Serial.println("Test reading: temperature " + String(dht.readTemperature()) + "*C");
#endif

  // Autogenerate ID if required
  chipID = String(ESP.getChipId(), HEX);

  if (strcmp(RIG_IDENTIFIER, "Auto") == 0)
  {
    AutoRigName = "ESP8266-" + chipID;
    AutoRigName.toUpperCase();
    RIG_IDENTIFIER = AutoRigName.c_str();
  }

  SetupWifi();
  SetupOTA();

  lwdtFeed();
  lwdTimer.attach_ms(LWD_TIMEOUT, lwdtcb);
  START_DIFF = USE_HIGHER_DIFF ? "ESP8266NH" : "ESP8266N";

  if (WEB_DASHBOARD)
  {
    if (!MDNS.begin(RIG_IDENTIFIER))
    {
      Serial.println("mDNS unavailable");
    }
    MDNS.addService("http", "tcp", 80);
    Serial.print("Configured mDNS for dashboard on http://" + String(RIG_IDENTIFIER) + ".local (or http://" + WiFi.localIP().toString() + ")");
    server.on("/", dashboard);
    if (WEB_HASH_UPDATER)
      server.on("/hashrateread", hashupdater);
    server.begin();
  }

  blink(BLINK_SETUP_COMPLETE);
}

MiningJob job;

void loop()
{
  uint8_t hashArray[20];

  if (USE_HIGHER_DIFF)
    system_update_cpu_freq(160);

  // 1 minute watchdog
  lwdtFeed();

  // OTA handlers
  VerifyWifi();
  ArduinoOTA.handle();
  if (WEB_DASHBOARD)
    server.handleClient();

  ConnectToServer();
  Serial.println("Asking for a new job for user: " + String(DUCO_USER));

#ifndef USE_DHT
  client.print("JOB," +
               String(DUCO_USER) + SEP_TOKEN +
               String(START_DIFF) + SEP_TOKEN +
               String(MINER_KEY) + END_TOKEN);
#endif

#ifdef USE_DHT
  temp = dht.readTemperature();
  hum = dht.readHumidity();

  Serial.println("DHT readings: " + String(temp) + "*C, " + String(hum) + "%");
  client.print("JOB," +
               String(DUCO_USER) + SEP_TOKEN +
               String(START_DIFF) + SEP_TOKEN +
               String(MINER_KEY) + SEP_TOKEN +
               String(temp) + "@" + String(hum) + END_TOKEN);
#endif

#ifdef USE_MQTT

  if (!mqttClient.connected())
  {
    mqttReconnect();
  }
  mqttClient.loop();
#ifdef USE_DHT
  long now = millis();
  if (now - lastMsg > mqtt_update_time)
  {
    lastMsg = now;
    mqttClient.publish(temperature_topic, String(temp).c_str(), true);
    mqttClient.publish(humidity_topic, String(hum).c_str(), true);
  }
#endif

#endif

  waitForClientData();
  Serial.println("Received job with size of " + String(client_buffer));

  job.parse(client_buffer.c_str());
  difficulty = job.difficulty;

  Serial.println("Parsed job: " + job.last_block_hash + " " + job.expected_hash_str + " " + String(job.difficulty));

  sha1_ctx_base.reset().write((const unsigned char *)job.last_block_hash.c_str(), job.last_block_hash.length());

  float start_time = micros();
  max_micros_elapsed(start_time, 0);

  String result = "";
  if (LED_BLINKING)
    digitalWrite(LED_BUILTIN, LOW);
  for (Counter<10> counter; counter < difficulty; ++counter)
  {
    // Difficulty loop
    DSHA1 sha1_ctx = sha1_ctx_base;

    sha1_ctx.write((const unsigned char *)counter.c_str(), counter.strlen()).finalize(hashArray);

    if (memcmp(job.expected_hash, hashArray, 20) == 0)
    {
      // If result is found
      if (LED_BLINKING)
        digitalWrite(LED_BUILTIN, HIGH);
      unsigned long elapsed_time = micros() - start_time;
      float elapsed_time_s = elapsed_time * .000001f;
      hashrate = counter / elapsed_time_s;
      share_count++;
      client.print(String(counter) + "," + String(hashrate) + "," + String(MINER_BANNER) + " " + String(MINER_VER) + "," + String(RIG_IDENTIFIER) + ",DUCOID" + String(chipID) + "\n");

      waitForClientData();
      Serial.println(client_buffer + " share #" + String(share_count) + " (" + String(counter) + ")" + " hashrate: " + String(hashrate / 1000, 2) + " kH/s (" + String(elapsed_time_s) + "s)");
      break;
    }
    if (max_micros_elapsed(micros(), 500000))
    {
      handleSystemEvents();
    }
  }
}