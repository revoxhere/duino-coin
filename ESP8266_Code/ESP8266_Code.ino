//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP8266 boards - V2.52
//  © Duino-Coin Community 2019-2021
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://duinocoin.com - Official Website
//  https://discord.gg/k48Ht5y - Discord
//  https://github.com/revoxhere - @revox
//  https://github.com/JoyBed - @JoyBed
//  https://github.com/kickshawprogrammer - @kickshawprogrammer
//////////////////////////////////////////////////////////
//  If you don't know what to do, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266mDNS.h> // OTA libraries
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

//////////////////////////////////////////////////////////
// NOTE: If during compilation, the below line causes a
// "fatal error: Crypto.h: No such file or directory"
// message to occur; it means that you do NOT have the
// latest version of the ESP8266/Arduino Core library.
//
// To install/upgrade it, go to the below link and 
// follow the instructions of the readme file: 
// 
//       https://github.com/esp8266/Arduino
//////////////////////////////////////////////////////////
#include <Crypto.h>  // experimental SHA1 crypto library
using namespace experimental::crypto;

#include <Ticker.h>

namespace {
  const char* ssid          = "WiFi SSID";   // Change this to your WiFi SSID
  const char* password      = "WiFi Pass";    // Change this to your WiFi password
  const char* ducouser      = "DUCO Username";     // Change this to your Duino-Coin username
  const char* rigIdentifier = "None";       // Change this if you want a custom miner name
  
  const char * host = "51.15.127.80"; // Static server IP
  const int port = 2811;
  unsigned int Shares = 0; // Share variable

  WiFiClient client;
  String clientBuffer = "";

  // Loop WDT... please don't feed me...
  // See lwdtcb() and lwdtFeed() below
  Ticker lwdTimer; 
  #define LWD_TIMEOUT   60000

  unsigned long lwdCurrentMillis = 0;
  unsigned long lwdTimeOutMillis = LWD_TIMEOUT;

  #define END_TOKEN  '\n'
  #define SEP_TOKEN  ','

  #define LED_BUILTIN 2

  #define BLINK_SHARE_FOUND    1
  #define BLINK_SETUP_COMPLETE 2
  #define BLINK_CLIENT_CONNECT 3
  #define BLINK_RESET_DEVICE   5

  void SetupWifi() {
    Serial.println("Connecting to: " + String(ssid));
    WiFi.mode(WIFI_STA); // Setup ESP in client mode
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    WiFi.begin(ssid, password); // Connect to wifi

    int wait_passes = 0;
    while (WiFi.waitForConnectResult() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      if (++wait_passes >= 10) {
        WiFi.begin(ssid, password);
        wait_passes = 0;
      }
    }

    Serial.println("\nConnected to WiFi!");
    Serial.println("Local IP address: " + WiFi.localIP().toString());
  }

  void SetupOTA() {
    ArduinoOTA.onStart([]() { // Prepare OTA stuff
      Serial.println("Start");
    });
    ArduinoOTA.onEnd([]() {
      Serial.println("\nEnd");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

    ArduinoOTA.setHostname(rigIdentifier); // Give port a name not just address
    ArduinoOTA.begin();
  }

  void blink(uint8_t count, uint8_t pin = LED_BUILTIN) {
    uint8_t state = HIGH;

    for (int x=0; x<(count << 1); ++x) {
      digitalWrite(pin, state ^= HIGH);
      delay(50);
    }
  }

  void RestartESP(String msg) {
    Serial.println(msg);
    Serial.println("Resetting ESP...");
    blink(BLINK_RESET_DEVICE); 
    ESP.reset();
  }

  // Our new WDT to help prevent freezes
  // code concept taken from https://sigmdel.ca/michel/program/esp8266/arduino/watchdogs2_en.html
  void ICACHE_RAM_ATTR lwdtcb(void) 
  {
    if ((millis() - lwdCurrentMillis > LWD_TIMEOUT) || (lwdTimeOutMillis - lwdCurrentMillis != LWD_TIMEOUT))
      RestartESP("Loop WDT Failed!");
  }

  void lwdtFeed(void) {
    lwdCurrentMillis = millis();
    lwdTimeOutMillis = lwdCurrentMillis + LWD_TIMEOUT;
  }

  void VerifyWifi() {
    while (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0,0,0,0)) 
      WiFi.reconnect();
  }

  void handleSystemEvents(void) {
    VerifyWifi();
    ArduinoOTA.handle();
    yield();
  }

  // https://stackoverflow.com/questions/9072320/split-string-into-string-array
  String getValue(String data, char separator, int index)
  {
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length()-1;

    for(int i=0; i<=maxIndex && found<=index; i++){
      if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
      }
    }

    return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
  }
  
  void waitForClientData(void) {
    clientBuffer = "";
    
    while (client.connected()) {
      if (client.available()) {
        clientBuffer = client.readStringUntil(END_TOKEN);
        if (clientBuffer.length() == 1 && clientBuffer[0] == END_TOKEN)
          clientBuffer = "???\n"; // NOTE: Should never happen...

        break;
      }
      handleSystemEvents();
    }
  }

  void ConnectToServer() {
    if (client.connected())
      return;

    Serial.println("\nConnecting to Duino-Coin server...");
    while (!client.connect(host, port));
  
    waitForClientData();
    Serial.println("Connected to the server. Server version: " + clientBuffer );
    blink(BLINK_CLIENT_CONNECT); // Blink 3 times - indicate sucessfull connection with the server
  }

  bool max_micros_elapsed(unsigned long current, unsigned long max_elapsed) {
    static unsigned long _start = 0;

    if ((current - _start) > max_elapsed) {
      _start = current;
      return true;
    }
      
    return false;
  }
} // namespace

void setup() {
  Serial.begin(115200); // Start serial connection
  Serial.println("\nDuino-Coin ESP8266 Miner v2.52");

  pinMode(LED_BUILTIN, OUTPUT); // prepare for blink() function

  SetupWifi();
  SetupOTA();
  
  lwdtFeed();
  lwdTimer.attach_ms(LWD_TIMEOUT, lwdtcb); 
  
  blink(BLINK_SETUP_COMPLETE); // Blink 2 times - indicate sucessfull connection with wifi network
}

void loop() {
  lwdtFeed(); // Feed the DOG! You now have 1-minute to feed me again or I cause Reboot...!

  VerifyWifi();
  ArduinoOTA.handle(); // Enable OTA handler
  ConnectToServer();

  Serial.println("Asking for a new job for user: " + String(ducouser));

  client.print("JOB," + String(ducouser) + ",ESP8266"); // Ask for new job
  waitForClientData();

  String hash = getValue(clientBuffer, SEP_TOKEN, 0); // Read data to the first peroid - last block hash
  String job = getValue(clientBuffer, SEP_TOKEN, 1); // Read data to the next peroid - expected hash
  unsigned int diff = getValue(clientBuffer, SEP_TOKEN, 2).toInt() * 100 + 1; // Read and calculate remaining data - difficulty
  Serial.println("Job received: " + hash + " " + job + " " + String(diff));

  job.toUpperCase();

  float StartTime = micros(); // Start time measurement
  max_micros_elapsed(StartTime, 0);

  for (unsigned int iJob = 0; iJob < diff; iJob++) { // Difficulty loop
    String result = SHA1::hash(hash + String(iJob));

    if (result == job) { // If result is found
      unsigned long ElapsedTime = micros() - StartTime;  // Calculate elapsed time
      float ElapsedTimeSeconds = ElapsedTime * .000001f; // Convert to seconds
      float HashRate = iJob / ElapsedTimeSeconds;

      client.print(String(iJob) + "," + String(HashRate) + ",ESP8266 Miner v2.52" + "," + String(rigIdentifier)); // Send result to server
      waitForClientData();

      Shares++;
      Serial.println(clientBuffer + " share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate) + " Free RAM: " + String(ESP.getFreeHeap()));
      blink(BLINK_SHARE_FOUND);
      break; // Stop and ask for more work
    }

    if (max_micros_elapsed(micros(), 250000)) 
      handleSystemEvents();
      
  }
}
