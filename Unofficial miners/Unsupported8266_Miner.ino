//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP8266 boards - unsupported
//  © Duino-Coin Community 2019-2021
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://duinocoin.com - Official Website
//  https://discord.gg/k48Ht5y - Discord
//  https://github.com/revoxhere - @revox
//  https://github.com/JoyBed - @JoyBed
//////////////////////////////////////////////////////////
//  If you don't know what to do, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////
// 2012.3.27 - By and large, the original code still 
//             stands, just re-organized to help me better
//             understand the existing code base. Also,
//             I changed the crypto code to instead 
//             call the experimental::crypto namespace's
//             hash function, and finally, re-vamped a 
//             few other lines of code all to minimize 
//             wasted cpu clock cycles
//////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////
// Project handlers and moderators: please do with this 
// code as you see fit. This code right here, compiled 
// using the 160mhz compiler flag in Arduino IDE 1.8(?)
// - or VS-Code's Arduino Extension - with the latest 
// ESP core stuff version 2.7(?) - gives each of 
// my two ESP-01 mining devices about a 6k hashrate.
//
// This puts the hashrate more in-line with a single
// ESP32 core; clearly well above the 3K limit of the
// "ESP" difficulty level. As a result, I changed 
// the requested difficulty level to "ESP32"
//////////////////////////////////////////////////////////
#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266mDNS.h> // OTA libraries
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
// #include <Hash.h> // SHA1 crypto library

#include <Crypto.h>  // experimental SHA1 crypto library
using namespace experimental::crypto;

namespace /* anonymous */ {
  const char* ssid          = "YourNetworkName";   // Change this to your WiFi SSID
  const char* password      = "YourNetworkPwd";    // Change this to your WiFi password
  const char* ducouser      = "YourDOCU_Name";     // Change this to your Duino-Coin username
  const char* rigIdentifier = "YourRigName";       // Change this if you want a custom miner name

  const char * host = "51.15.127.80"; // Static server IP
  const int port = 2811;
  unsigned int Shares = 0; // Share variable

  WiFiClient client;

  #define LED_BUILTIN 1 
  
  #define BLINK_SHARE_FOUND    1
  #define BLINK_SETUP_COMPLETE 2
  #define BLINK_CLIENT_CONNECT 3
  #define BLINK_RESET_DEVICE   5
  
  #define VersionInfo() "2021.3.xxx"

  void SetupWifi() {
    Serial.println("Connecting to: " + String(ssid));
    WiFi.mode(WIFI_STA); // Setup ESP in client mode
    WiFi.begin(ssid, password); // Connect to wifi

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
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
    ArduinoOTA.begin();
  }

  void blink(uint8_t count, uint8_t pin = LED_BUILTIN) {
    uint8_t state = HIGH;

    pinMode(pin, FUNCTION_3); // Set to GPIO / OUTPUT mode 
    for (int x=0; x<(count << 1); ++x) {
      digitalWrite(pin, state ^= HIGH);
      delay(250);
    }

    digitalWrite(pin, state); // NOTE: Is this really needed...?
    pinMode(pin, FUNCTION_0); // Reset back to TX/RX Serial mode
    yield();  // register updates can take several cpu cycles; 
              // lets give them a chance to change
  }

  void RestartESP(String msg) {
    Serial.println(msg);
    Serial.println("Resetting ESP...");
    blink(BLINK_RESET_DEVICE); 
    ESP.reset();
  }

  void ConnectToServer() {
    if (client.connected())
      return;

    Serial.println("\nConnecting to Duino-Coin server...");
    if (!client.connect(host, port)) 
      RestartESP("Connection failed.");
  
    Serial.println("Connected to the server. Server version: " + client.readString());
    blink(BLINK_CLIENT_CONNECT); // Blink 3 times - indicate sucessfull connection with the server
  }
} // namespace

void setup() {
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nCustom ESP Miner v"+VersionInfo());

  SetupWifi();
  SetupOTA();

  blink(BLINK_SETUP_COMPLETE); // Blink 2 times - indicate sucessfull connection with wifi network
}

void loop() {
  ArduinoOTA.handle(); // Enable OTA handler
  ConnectToServer();

  Serial.println("Asking for a new job for user: " + String(ducouser));

  client.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job
  String       hash = client.readStringUntil(','); // Read data to the first peroid - last block hash
  String        job = client.readStringUntil(','); // Read data to the next peroid - expected hash
  unsigned int diff = client.readStringUntil('\n').toInt() * 100 + 1; // Read and calculate remaining data - difficulty
  Serial.println("Job received: " + String(hash) + " " + String(job) + " " + String(diff));
  
  job.toUpperCase(); // SHA1::hash() returns Upper-Case results...

  float StartTime = micros(); // Start time measurement
  for (unsigned int iJob = 0; iJob < diff; iJob++) { // Difficulty loop
    String result = SHA1::hash(String(hash) + String(iJob));

    if (result == job) { // If result is found
      // Replaces two assignments and two divisions with a multiplication
      unsigned long ElapsedTime = micros() - StartTime;  // Calculate elapsed time
      float ElapsedTimeSeconds = ElapsedTime * .000001f; // Convert to seconds
      float HashRate = iJob / ElapsedTimeSeconds;

      client.print(String(iJob) + "," + String(HashRate) + ",Custom ESP Miner v"+VersionInfo()+"," + String(rigIdentifier)); // Send result to server

      String feedback = client.readStringUntil('\n'); // Receive feedback
      Shares++;
      Serial.println(String(feedback) + " share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate) + " Free RAM: " + String(ESP.getFreeHeap()));
      blink(BLINK_SHARE_FOUND);
      break; // Stop and ask for more work
    }
  }
}
