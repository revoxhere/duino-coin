//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP8266 boards v2.1
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

const char* ssid     = "Your WiFi SSID"; // Change this to your WiFi SSID
const char* password = "Your WiFi password"; // Change this to your WiFi password
const char* ducouser = "Your Duino-Coin username"; // Change this to your Duino-Coin username
#define LED_BUILTIN 2 // Change this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)

#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266mDNS.h> // OTA libraries
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <Hash.h> // SHA1 crypto library

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Define built-in led as output
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP Miner v2.1");

  Serial.println("Connecting to: " + String(ssid));
  WiFi.mode(WIFI_STA); // Setup ESP in client mode
  WiFi.begin(ssid, password); // Connect to wifi

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

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

  Serial.println("\nConnected to WiFi!");
  Serial.println("Local IP address: " + WiFi.localIP().toString());
  blink(2); // Blink 2 times - indicate sucessfull connection with wifi network
}

void blink(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(150);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
    delay(150);
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
  }
}

void loop() {
  ArduinoOTA.handle(); // Enable OTA handler
  const char * host = "51.15.127.80"; // Static server IP
  const int port = 2811;
  unsigned int Shares = 0; // Share variable

  Serial.println("\nConnecting to Duino-Coin server...");
  // Use WiFiClient class to create TCP connection
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("Connection failed.");
    Serial.println("Retrying...");
    blink(7); // Blink 7 times indicating connection error
    ESP.reset(); // Restart the board
    ESP.restart();
  }
  client.setTimeout(5000);
  String SERVER_VER = client.readString(); // Server sends SERVER_VERSION after connecting
  Serial.println("Connected to the server. Server version: " + String(SERVER_VER));
  blink(3); // Blink 3 times - indicate sucessfull connection with the server

  while (client.connected()) {
    ArduinoOTA.handle(); // Enable OTA handler
    Serial.println("Asking for a new job for user: " + String(ducouser));
    client.print("JOB," + String(ducouser) + ",ESP"); // Ask for new job

    String hash = client.readStringUntil(','); // Read last block hash
    String job = client.readStringUntil(','); // Read expected hash
    unsigned int diff =  (1500) * 100 + 1; // Low power devices use the low diff job, we don't read it as no termination character causes unnecessary network lag
    Serial.println("Job received: " + String(hash) + " " + String(job) + " " + String(diff));
    unsigned long StartTime = micros(); // Start time measurement

    for (unsigned int iJob = 0; iJob < diff; iJob++) { // Difficulty loop
      ArduinoOTA.handle(); // Enable OTA handler
      yield(); // uncomment if ESP watchdog triggers
      String result = sha1(String(hash) + String(iJob)); // Hash previous block hash and current iJob
      if (result == job) { // If result is found
        unsigned long EndTime = micros(); // End time measurement
        unsigned long ElapsedTime = EndTime - StartTime; // Calculate elapsed time
        float ElapsedTimeMiliSeconds = ElapsedTime / 1000; // Convert to miliseconds
        float ElapsedTimeSeconds = ElapsedTimeMiliSeconds / 1000; // Convert to seconds
        float HashRate = iJob / ElapsedTimeSeconds; // Calculate hashrate
        client.print(String(iJob) + "," + String(HashRate) + ",ESP Miner v2.1"); // Send result to server

        String feedback = client.readStringUntil('D'); // Receive feedback
        Shares++;
        Serial.println(String(feedback) + "D share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate) + " Free RAM: " + String(ESP.getFreeHeap()));
        digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
        delay(3); // Wait shortly so LED flash isn't distracting
        digitalWrite(LED_BUILTIN, HIGH); // Turn off built-in led
        break; // Stop and ask for more work
      }
    }
  }
  Serial.println("Not connected. Restarting ESP");
  blink(7); // Blink 7 times indicating connection error
  ESP.reset(); // Restart the board
  ESP.restart();
}
