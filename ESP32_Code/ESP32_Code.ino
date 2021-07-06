//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP32 boards v2.55
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

const char* ssid     = "Your WiFi SSID";            // Change this to your WiFi SSID
const char* password = "Your WiFi password";        // Change this to your WiFi password
const char* ducouser = "Your Duino-Coin username";  // Change this to your Duino-Coin username
const char* rigname  = "None";                     // Change this if you want to display a custom rig name in the Wallet
#define LED_BUILTIN     2                           // Change this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)
#define WDT_TIMEOUT 60                              // Define watchdog timer seconds

//////////////////////////////////////////////////////////
//  If you're using the ESP32-CAM board or other board
//  that doesn't support OTA (Over-The-Air programming)
//  comment the ENABLE_OTA definition line
//  (#define ENABLE_OTA)
//////////////////////////////////////////////////////////

#define ENABLE_OTA

//////////////////////////////////////////////////////////
//  If you don't want to use the Serial interface comment
//  the ENABLE_SERIAL definition line (#define ENABLE_SERIAL)
//////////////////////////////////////////////////////////

#define ENABLE_SERIAL

#ifndef ENABLE_SERIAL
// disable Serial output
#define Serial DummySerial
static class {
public:
    void begin(...) {}
    void print(...) {}
    void println(...) {}
    void printf(...) {}
} Serial;
#endif

#include <esp_task_wdt.h>                           //Include WDT libary
#include "hwcrypto/sha.h" // Include hardware accelerated hashing library
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>

#ifdef ENABLE_OTA
#include <ArduinoOTA.h>
#endif

TaskHandle_t WiFirec;
TaskHandle_t Task1;
TaskHandle_t Task2;
SemaphoreHandle_t xMutex;

// Since 2.5.5 additional mining nodes available - you can change it manually to one of these:
// Official Master Server: 51.15.127.80 port 2820
// Official Kolka Pool: 149.91.88.18 port 6000
// This will be replaced with an automatic picker in the future version
const char * host = "149.91.88.18"; // Static server IP
const int port = 6000;

volatile int wifiStatus = 0;
volatile int wifiPrev = WL_CONNECTED;
volatile bool OTA_status = false;

volatile char ID[23]; // DUCO MCU ID

void WiFireconnect( void * pvParameters ) {
  int n = 0;
  unsigned long previousMillis = 0;
  const long interval = 500;
  esp_task_wdt_add(NULL);
  for(;;) {
    wifiStatus = WiFi.status();
    
    #ifdef ENABLE_OTA
    ArduinoOTA.handle();
    #endif
    
    if (OTA_status)  // If the OTA is working then reset the watchdog.
      esp_task_wdt_reset();
    // check if WiFi status has changed.
    if ((wifiStatus == WL_CONNECTED)&&(wifiPrev != WL_CONNECTED)) {
      esp_task_wdt_reset(); // Reset watchdog timer
      Serial.println(F("\nConnected to WiFi!"));
      Serial.println("Local IP address: " + WiFi.localIP().toString());
      Serial.println();
    }
    else if ((wifiStatus != WL_CONNECTED)&&(wifiPrev == WL_CONNECTED)) {
      esp_task_wdt_reset(); // Reset watchdog timer
      Serial.println(F("\nWiFi disconnected!"));
      WiFi.disconnect();
      Serial.println(F("Scanning for WiFi networks"));
      n = WiFi.scanNetworks(false, true);
      Serial.println(F("Scan done"));
      if (n == 0) {
          Serial.println(F("No networks found. Resetting ESP32."));
          esp_restart();
      } else {
          Serial.print(n);
          Serial.println(F(" networks found"));
          for (int i = 0; i < n; ++i) {
              // Print SSID and RSSI for each network found
              Serial.print(i + 1);
              Serial.print(F(": "));
              Serial.print(WiFi.SSID(i));
              Serial.print(F(" ("));
              Serial.print(WiFi.RSSI(i));
              Serial.print(F(")"));
              Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":"*");
              delay(10);
          }
      }
      esp_task_wdt_reset(); // Reset watchdog timer
      Serial.println();
      Serial.println(F("Please, check if your WiFi network is on the list and check if it's strong enough (greater than -90)."));
      Serial.println("ESP32 will reset itself after "+String(WDT_TIMEOUT)+" seconds if can't connect to the network");
      Serial.print("Connecting to: " + String(ssid));
      WiFi.reconnect();
    }
    else if ((wifiStatus == WL_CONNECTED)&&(wifiPrev == WL_CONNECTED)) {
      esp_task_wdt_reset(); // Reset watchdog timer
      delay(1000);
    }
    else {
       // Don't reset watchdog timer. If the timer gets to the timeout then it will reset the MCU
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        Serial.print(F("."));
      }
    }
    wifiPrev = wifiStatus;
  }
}

// Task1code
void Task1code( void * pvParameters ) {
  WiFiClient client1;  
  unsigned long Shares1 = 0; // Share variable
  String SERVER_VER = "";
  int buff1size = 0;
  String hash1 = "";
  String job1 = "";
  unsigned int diff1 = 0;
  size_t len = 0;
  size_t final_len = 0;
  unsigned int sizeofjob11 = 100;
  unsigned char* job11 = (unsigned char*)malloc(sizeofjob11 * sizeof(unsigned char));
  byte shaResult1[20];
  unsigned long StartTime1 = 0;
  String hash11 = "";
  unsigned int payloadLenght1 = 0;
  unsigned long EndTime1 = 0;
  unsigned long ElapsedTime1 = 0;
  float ElapsedTimeMiliSeconds1 = 0.0;
  float ElapsedTimeSeconds1 = 0.0;
  float HashRate1 = 0.0;
  String feedback1 = "";
  esp_task_wdt_add(NULL);
  for(;;) {
    if (OTA_status)  // If the OTA is working then reset the watchdog.
      esp_task_wdt_reset();
    while(wifiStatus != WL_CONNECTED){
      delay(1000);
      esp_task_wdt_reset();
    }
    Shares1 = 0; // Share variable
    Serial.println(F("\nCORE1 Connecting to Duino-Coin server..."));
    // Use WiFiClient class to create TCP connection
    client1.setTimeout(1);
    client1.flush();
    yield();
    if (!client1.connect(host, port)) {
      Serial.println(F("CORE1 connection failed"));
      delay(500);
      continue;
    }
    Serial.println(F("CORE1 is connected"));
    while(!client1.available()){
      yield();
      if (!client1.connected())
        break;
      delay(10);
    }
    
    SERVER_VER = client1.readString(); // Server sends SERVER_VERSION after connecting
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
    Serial.println("CORE1 Connected to the server. Server version: " + String(SERVER_VER));
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
    
    while (client1.connected()) {
      esp_task_wdt_reset();
      Serial.println("CORE1 Asking for a new job for user: " + String(ducouser));
      client1.flush();
      client1.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job
      while(!client1.available()){
        if (!client1.connected())
          break;
        delay(10);
      }
      yield();
      if (!client1.connected())
        break;
      delay(50);
      yield();
      buff1size = client1.available();
      Serial.print(F("CORE1 Buffer size is "));
      Serial.println(buff1size);
      if (buff1size<=10) {
        Serial.println(F("CORE1 Buffer size is too small. Requesting another job."));
        continue;
      }
      hash1 = client1.readStringUntil(','); // Read data to the first peroid - last block hash
      job1 = client1.readStringUntil(','); // Read data to the next peroid - expected hash
      diff1 = client1.readStringUntil('\n').toInt() * 100 + 1; // Read and calculate remaining data - difficulty
      client1.flush();
      job1.toUpperCase();
      const char * c = job1.c_str();
      
      len = job1.length();
      final_len = len / 2;
      memset(job11, 0, sizeofjob11);
      for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
        job11[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;
      memset(shaResult1, 0, sizeof(shaResult1));
      
      Serial.println("CORE1 Job received: " + String(hash1) + " " + String(job1) + " " + String(diff1));
      StartTime1 = micros(); // Start time measurement
      
      for (unsigned long iJob1 = 0; iJob1 < diff1; iJob1++) { // Difficulty loop
        hash11 = hash1 + String(iJob1);
        payloadLenght1 = hash11.length();
        
        while( xSemaphoreTake( xMutex, portMAX_DELAY ) != pdTRUE );
        esp_sha(SHA1, (const unsigned char*)hash11.c_str(), payloadLenght1, shaResult1);
        xSemaphoreGive( xMutex );
        
        if (memcmp(shaResult1, job11, sizeof(shaResult1)) == 0) { // If result is found
          EndTime1 = micros(); // End time measurement
          ElapsedTime1 = EndTime1 - StartTime1; // Calculate elapsed time
          ElapsedTimeMiliSeconds1 = ElapsedTime1 / 1000; // Convert to miliseconds
          ElapsedTimeSeconds1 = ElapsedTimeMiliSeconds1 / 1000; // Convert to seconds
          HashRate1 = iJob1 / ElapsedTimeSeconds1; // Calculate hashrate
          if (!client1.connected()) {
            Serial.println(F("CORE1 Lost connection. Trying to reconnect"));
            if (!client1.connect(host, port)) {
              Serial.println(F("CORE1 connection failed"));
              break;
            }
            Serial.println(F("CORE1 Reconnection successful."));
          }
          client1.flush();
          client1.print(String(iJob1) + "," + String(HashRate1) + ",ESP32 CORE1 Miner v2.55," + String(rigname) + "," + String((char*)ID)); // Send result to server
          Serial.println(F("CORE1 Posting result and waiting for feedback."));
          while(!client1.available()){
            if (!client1.connected()) {
              Serial.println(F("CORE1 Lost connection. Didn't receive feedback."));
              break;
            }
            delay(10);
            yield();
          }
          delay(50);
          yield();
          feedback1 = client1.readStringUntil('\n'); // Receive feedback
          client1.flush();
          Shares1++;
          Serial.println("CORE1 " + String(feedback1) + " share #" + String(Shares1) + " (" + String(iJob1) + ")" + " Hashrate: " + String(HashRate1));
          if (HashRate1 < 4000) {
            Serial.println(F("CORE1 Low hashrate. Restarting"));
            client1.flush();
            client1.stop();
            esp_restart();
          }
          break; // Stop and ask for more work
        }
      }
    }
    Serial.println(F("CORE1 Not connected. Restarting core 1"));
    client1.flush();
    client1.stop();
  }
}

//Task2code
void Task2code( void * pvParameters ) {
  WiFiClient client;
  unsigned long Shares = 0;
  String SERVER_VER = "";
  int buff1size = 0;
  String hash = "";
  String job = "";
  unsigned int diff = 0;
  size_t len = 0;
  size_t final_len = 0;
  unsigned int sizeofjob1 = 100;
  unsigned char* job1 = (unsigned char*)malloc(sizeofjob1 * sizeof(unsigned char));
  byte shaResult[20];
  unsigned long StartTime = 0;
  String hash1 = "";
  unsigned int payloadLength = 0;
  unsigned long EndTime = 0;
  unsigned long ElapsedTime = 0;
  float ElapsedTimeMiliSeconds = 0.0;
  float ElapsedTimeSeconds = 0.0;
  float HashRate = 0.0;
  String feedback = "";
  esp_task_wdt_add(NULL);
  for(;;) {
    if (OTA_status)  // If the OTA is working then reset the watchdog.
      esp_task_wdt_reset();
    while(wifiStatus != WL_CONNECTED){
      delay(1000);
      esp_task_wdt_reset();
    }
    Shares = 0; // Share variable
    
    Serial.println(F("\nCORE2 Connecting to Duino-Coin server..."));
    // Use WiFiClient class to create TCP connection
    client.setTimeout(1);
    client.flush();
    yield();
    if (!client.connect(host, port)) {
      Serial.println(F("CORE2 connection failed"));
      delay(500);
      continue;
    }
    Serial.println(F("CORE2 is connected"));
    while(!client.available()){
      yield();
      if (!client.connected())
        break;
      delay(10);
    }
    
    SERVER_VER = client.readString(); // Server sends SERVER_VERSION after connecting
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
    Serial.println("CORE2 Connected to the server. Server version: " + String(SERVER_VER));
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
    
    while (client.connected()) {
      esp_task_wdt_reset();
      Serial.println("CORE2 Asking for a new job for user: " + String(ducouser));
      client.flush();
      client.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job
      while(!client.available()){
        if (!client.connected())
          break;
        delay(10);
      }
      yield();
      if (!client.connected())
        break;
      delay(50);
      yield();
      buff1size = client.available();
      Serial.print(F("CORE2 Buffer size is "));
      Serial.println(buff1size);
      if (buff1size<=10) {
        Serial.println(F("CORE2 Buffer size is too small. Requesting another job."));
        continue;
      }
      hash = client.readStringUntil(','); // Read data to the first peroid - last block hash
      job = client.readStringUntil(','); // Read data to the next peroid - expected hash
      diff = client.readStringUntil('\n').toInt() * 100 + 1; // Read and calculate remaining data - difficulty
      client.flush();
      job.toUpperCase();
      const char * c = job.c_str();
      
      len = job.length();
      final_len = len / 2;
      memset(job1, 0, sizeofjob1);
      for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
        job1[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;
      memset(shaResult, 0, sizeof(shaResult));
      
      Serial.println("CORE2 Job received: " + String(hash) + " " + String(job) + " " + String(diff));
      StartTime = micros(); // Start time measurement
      
      for (unsigned long iJob = 0; iJob < diff; iJob++) { // Difficulty loop
        hash1 = hash + String(iJob);
        payloadLength = hash1.length();
        
        while( xSemaphoreTake( xMutex, portMAX_DELAY ) != pdTRUE );
        esp_sha(SHA1, (const unsigned char*)hash1.c_str(), payloadLength, shaResult);
        xSemaphoreGive( xMutex );
        
        if (memcmp(shaResult, job1, sizeof(shaResult)) == 0) { // If result is found
          EndTime = micros(); // End time measurement
          ElapsedTime = EndTime - StartTime; // Calculate elapsed time
          ElapsedTimeMiliSeconds = ElapsedTime / 1000; // Convert to miliseconds
          ElapsedTimeSeconds = ElapsedTimeMiliSeconds / 1000; // Convert to seconds
          HashRate = iJob / ElapsedTimeSeconds; // Calculate hashrate
          if (!client.connected()) {
            Serial.println(F("CORE2 Lost connection. Trying to reconnect"));
            if (!client.connect(host, port)) {
              Serial.println(F("CORE2 connection failed"));
              break;
            }
            Serial.println(F("CORE2 Reconnection successful."));
          }
          client.flush();
          client.print(String(iJob) + "," + String(HashRate) + ",ESP32 CORE2 Miner v2.55," + String(rigname) + "," + String((char*)ID)); // Send result to server
          Serial.println(F("CORE2 Posting result and waiting for feedback."));
          while(!client.available()){
            if (!client.connected()) {
              Serial.println(F("CORE2 Lost connection. Didn't receive feedback."));
              break;
            }
            delay(10);
            yield();
          }
          delay(50);
          yield();
          feedback = client.readStringUntil('\n'); // Receive feedback
          client.flush();
          Shares++;
          Serial.println("CORE2 " + String(feedback) + " share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate));
          if (HashRate < 4000) {
            Serial.println(F("CORE2 Low hashrate. Restarting"));
            client.flush();
            client.stop();
            esp_restart();
          }
          break; // Stop and ask for more work
        }
      }
    }
    Serial.println(F("CORE2 Not connected. Restarting core 2"));
    client.flush();
    client.stop();
  }
}

void setup() {
  //disableCore0WDT();
  //disableCore1WDT();
  Serial.begin(500000); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP32 Miner v2.55");
  
  WiFi.mode(WIFI_STA); // Setup ESP in client mode
  btStop();
  WiFi.begin(ssid, password); // Connect to wifi
  
  uint64_t chipid = ESP.getEfuseMac(); // Getting chip ID
  uint16_t chip = (uint16_t)(chipid >> 32); // Preparing for printing a 64 bit value (it's actually 48 bits long) into a char array
  snprintf((char*)ID, 23, "DUCOID%04X%08X", chip, (uint32_t)chipid); // Storing the 48 bit chip ID into a char array.
  
  OTA_status = false;
  
  // Port defaults to 3232
  // ArduinoOTA.setPort(3232);
  
  // Hostname defaults to esp3232-[MAC]
  // ArduinoOTA.setHostname("myesp32");
  
  // No authentication by default
  // ArduinoOTA.setPassword("admin");
  
  // Password can be set with it's md5 value as well
  // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

  #ifdef ENABLE_OTA
  ArduinoOTA
    .onStart([]() {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
        type = "sketch";
      else // U_SPIFFS
        type = "filesystem";
      
      // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
      Serial.println("Start updating " + type);
      OTA_status = true;
    })
    .onEnd([]() {
      Serial.println(F("\nEnd"));
    })
    .onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
      OTA_status = true;
    })
    .onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println(F("Auth Failed"));
      else if (error == OTA_BEGIN_ERROR) Serial.println(F("Begin Failed"));
      else if (error == OTA_CONNECT_ERROR) Serial.println(F("Connect Failed"));
      else if (error == OTA_RECEIVE_ERROR) Serial.println(F("Receive Failed"));
      else if (error == OTA_END_ERROR) Serial.println(F("End Failed"));
      OTA_status = false;
      esp_restart();
    });
  
  ArduinoOTA.begin();
  #endif
  
  esp_task_wdt_init(WDT_TIMEOUT, true); // Init Watchdog timer
  pinMode(LED_BUILTIN,OUTPUT);
  
  xMutex = xSemaphoreCreateMutex();
  xTaskCreatePinnedToCore(WiFireconnect, "WiFirec", 10000, NULL, 3, &WiFirec, 0); //create a task with priority 3 and executed on core 0
  delay(250);
  xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 1, &Task1, 0); //create a task with priority 1 and executed on core 0
  delay(250);
  xTaskCreatePinnedToCore(Task2code, "Task2", 10000, NULL, 2, &Task2, 1); //create a task with priority 2 and executed on core 1
  delay(250);
}

void loop() {}
