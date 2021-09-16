/*
  ,------.          ,--.                       ,-----.       ,--.         
  |  .-.  \ ,--.,--.`--',--,--,  ,---. ,-----.'  .--./ ,---. `--',--,--,  
  |  |  \  :|  ||  |,--.|      \| .-. |'-----'|  |    | .-. |,--.|      \ 
  |  '--'  /'  ''  '|  ||  ||  |' '-' '       '  '--'\' '-' '|  ||  ||  | 
  `-------'  `----' `--'`--''--' `---'         `-----' `---' `--'`--''--' 
  Official code for ESP32 boards                            version 2.7.3
  
  Duino-Coin Team & Community 2019-2021 © MIT Licensed
  https://duinocoin.com
  https://github.com/revoxhere/duino-coin

  If you don't know where to start, visit official website and navigate to
  the Getting Started page. Have fun mining!
*/

// Change this to your WiFi name
const char *wifi_ssid = "Your WiFi SSID";
// Change this to your WiFi wifi_password
const char *wifi_password = "Your WiFi password";
// Change this to your Duino-Coin username
const char *username = "Your Duino-Coin username";
// Change this if you want a custom rig identifier
const char *rig_identifier = "None";
// Change this if your board has built-in led on non-standard pin
#define LED_BUILTIN 2
#define BLINK_SHARE_FOUND    1
#define BLINK_SETUP_COMPLETE 2
#define BLINK_CLIENT_CONNECT 3
#define BLINK_RESET_DEVICE   5

// Define watchdog timer seconds
#define WDT_TIMEOUT 60

// #include "hwcrypto/sha.h" // Uncomment this line if you're using an older
// version of the ESP32 core and sha_parellel_engine doesn't work for you
#include "sha/sha_parallel_engine.h"  // Include hardware accelerated hashing library

/* If you're using the ESP32-CAM board or other board
  that doesn't support OTA (Over-The-Air programming)
  comment the ENABLE_OTA definition line (#define ENABLE_OTA) */
#define ENABLE_OTA

/* If you don't want to use the Serial interface comment
  the ENABLE_SERIAL definition line (#define ENABLE_SERIAL)*/
#define ENABLE_SERIAL

#ifndef ENABLE_SERIAL
#define Serial DummySerial
static class {
 public:
  void begin(...) {}
  void print(...) {}
  void println(...) {}
  void printf(...) {}
} Serial;
#endif

#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <esp_task_wdt.h>  //Include WDT libary

#ifdef ENABLE_OTA
#include <ArduinoOTA.h>
#endif

TaskHandle_t WiFirec;
TaskHandle_t Task1;
TaskHandle_t Task2;
TaskHandle_t MinerCheckin;
SemaphoreHandle_t xMutex;

const char *get_pool_api = "http://51.15.127.80:4242/getPool";
String host = "";
int port = 0;
int walletid = 0;
volatile int wifi_state = 0;
volatile int wifi_prev_state = WL_CONNECTED;
volatile bool ota_state = false;
volatile char chip_id[23];  // DUCO MCU ID
float hashrate_two = 0.0;
float hashrate_one = 0.0;
unsigned long shares_one = 0;  // Share variable
unsigned long shares_two = 0;
unsigned int diff_one = 0;
unsigned int diff_two = 0;

void blink(uint8_t count, uint8_t pin = LED_BUILTIN) {
  uint8_t state = LOW;

  for (int x = 0; x < (count << 1); ++x) {
    digitalWrite(pin, state ^= HIGH);
    delay(75);
  }
}

void UpdatePool() {
  String input = "";

  while (input == "") {
    Serial.println("Fetching pool... ");
    input = httpGetString(get_pool_api);
  }

  UpdateHostPort(input);
}

void UpdateHostPort(String input) {
  // Thanks @ricaun for the code
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, input);

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }

  const char *name = doc["name"];
  const char *h = doc["ip"];
  int p = doc["port"];

  host = h;
  port = p;

  Serial.println("Fetched pool: " + String(name) + " - " + String(host) + ":" +
                 String(port));
}

String httpGetString(String URL) {
  String payload = "";
  WiFiClient client;
  HTTPClient http;

  if (http.begin(client, URL)) {
    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
      payload = http.getString();
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n",
                    http.errorToString(httpCode).c_str());
    }
    http.end();
  }
  return payload;
}

void WiFireconnect(void *pvParameters) {
  int n = 0;
  unsigned long previousMillis = 0;
  const long interval = 500;
  esp_task_wdt_add(NULL);
  for (;;) {
    wifi_state = WiFi.status();

#ifdef ENABLE_OTA
    ArduinoOTA.handle();
#endif

    if (ota_state)  // If OTA is working, reset the watchdog
      esp_task_wdt_reset();

    // check if WiFi status has changed.
    if ((wifi_state == WL_CONNECTED) && (wifi_prev_state != WL_CONNECTED)) {
      esp_task_wdt_reset();  // Reset watchdog timer
      Serial.println(F("\nConnected to WiFi!"));
      Serial.println("    IP address: " + WiFi.localIP().toString());
      Serial.println("      Rig name: " + String(rig_identifier));
      Serial.println();
      blink(BLINK_SETUP_COMPLETE);// Sucessfull connection with wifi network
      UpdatePool();
      yield();
      delay(100);
    }

    else if ((wifi_state != WL_CONNECTED) &&
             (wifi_prev_state == WL_CONNECTED)) {
      esp_task_wdt_reset();  // Reset watchdog timer
      Serial.println(F("\nWiFi disconnected!"));
      WiFi.disconnect();

      Serial.println(F("Scanning for WiFi networks"));
      n = WiFi.scanNetworks(false, true);
      Serial.println(F("Scan done"));

      if (n == 0) {
        Serial.println(F("No networks found. Resetting ESP32."));
	blink(BLINK_RESET_DEVICE);
        esp_restart();
      }

      else {
        Serial.print(n);
        Serial.println(F(" networks found"));
        for (int i = 0; i < n; ++i) {
          // Print wifi_ssid and RSSI for each network found
          Serial.print(i + 1);
          Serial.print(F(": "));
          Serial.print(WiFi.SSID(i));
          Serial.print(F(" ("));
          Serial.print(WiFi.RSSI(i));
          Serial.print(F(")"));
          Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? " "
                                                                    : "*");
          delay(10);
        }
      }

      esp_task_wdt_reset();  // Reset watchdog timer
      Serial.println();
      Serial.println(
          F("Please, check if your WiFi network is on the list and check if "
            "it's strong enough (greater than -90)."));
      Serial.println("ESP32 will reset itself after " + String(WDT_TIMEOUT) +
                     " seconds if can't connect to the network");

      Serial.print("Connecting to: " + String(wifi_ssid));
      WiFi.reconnect();
    }

    else if ((wifi_state == WL_CONNECTED) &&
             (wifi_prev_state == WL_CONNECTED)) {
      esp_task_wdt_reset();  // Reset watchdog timer
      delay(1000);
    }

    else {
      // Don't reset watchdog timer
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        Serial.print(F("."));
      }
    }
    wifi_prev_state = wifi_state;
  }
}

// Task1code
void Task1code(void *pvParameters) {
  WiFiClient client_one;
  String SERVER_VER = "";
  int buff_two_size = 0;
  String hash1 = "";
  String job1 = "";
  size_t len = 0;
  size_t final_len = 0;
  unsigned int job_size_task_one = 100;
  unsigned char *job11 =
      (unsigned char *)malloc(job_size_task_one * sizeof(unsigned char));
  byte shaResult1[20];
  unsigned long StartTime1 = 0;
  String hash11 = "";
  unsigned int payload_length_one = 0;
  unsigned long end_time_one = 0;
  unsigned long elapsed_time_one = 0;
  float elapsed_time_ms_one = 0.0;
  float elapsed_time_sec_one = 0.0;
  String feedback_one = "";
  esp_task_wdt_add(NULL);

  for (;;) {
    if (ota_state)  // If the OTA is working then reset the watchdog.
      esp_task_wdt_reset();
    while (wifi_state != WL_CONNECTED || port == 0) {
      delay(1000);
      esp_task_wdt_reset();
    }
    shares_one = 0;  // Share variable
    Serial.println(F("\nCORE1 Connecting to Duino-Coin server..."));
    // Use WiFiClient class to create TCP connection
    client_one.setTimeout(1);
    client_one.flush();
    yield();

    if (!client_one.connect(host.c_str(), port)) {
      Serial.println(F("CORE1 connection failed"));
      delay(500);
      continue;
    }

    Serial.println(F("CORE1 is connected"));
    while (!client_one.available()) {
      yield();
      if (!client_one.connected()) break;
      delay(10);
    }

    // Server sends SERVER_VERSION after connecting
    SERVER_VER = client_one.readString();
    Serial.println("CORE1 Connected to the server. Server version: " +
                   String(SERVER_VER));
    blink(BLINK_CLIENT_CONNECT); // Sucessfull connection with the server

    while (client_one.connected()) {
      esp_task_wdt_reset();
      Serial.println("CORE1 Asking for a new job for user: " +
                     String(username));
      client_one.flush();

      // Ask for new job
      client_one.print("JOB," + String(username) + ",ESP32");
      while (!client_one.available()) {
        if (!client_one.connected()) break;
        delay(10);
      }

      yield();
      if (!client_one.connected()) break;
      delay(50);
      yield();

      buff_two_size = client_one.available();
      Serial.print(F("CORE1 Buffer size is "));
      Serial.println(buff_two_size);
      if (buff_two_size <= 10) {
        Serial.println(
            F("CORE1 Buffer size is too small. Requesting another job."));
        continue;
      }

      hash1 = client_one.readStringUntil(
          ',');  // Read data to the first peroid - last block hash
      job1 = client_one.readStringUntil(
          ',');  // Read data to the next peroid - expected hash
      diff_one = client_one.readStringUntil('\n').toInt() * 100 +
                 1;  // Read and calculate remaining data - difficulty
      client_one.flush();
      job1.toUpperCase();
      const char *c = job1.c_str();

      len = job1.length();
      final_len = len / 2;
      memset(job11, 0, job_size_task_one);
      for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
        job11[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;
      memset(shaResult1, 0, sizeof(shaResult1));

      Serial.println("CORE1 Job received: " + String(hash1) + " " +
                     String(job1) + " " + String(diff_one));
      StartTime1 = micros();  // Start time measurement

      for (unsigned long duco_res_one = 0; duco_res_one < diff_one;
           duco_res_one++) {
        hash11 = hash1 + String(duco_res_one);
        payload_length_one = hash11.length();

        while (xSemaphoreTake(xMutex, portMAX_DELAY) != pdTRUE)
          ;
        esp_sha(SHA1, (const unsigned char *)hash11.c_str(), payload_length_one,
                shaResult1);
        xSemaphoreGive(xMutex);

        if (memcmp(shaResult1, job11, sizeof(shaResult1)) == 0) {
          end_time_one = micros();  // End time measurement
          elapsed_time_one =
              end_time_one - StartTime1;  // Calculate elapsed time
          elapsed_time_ms_one =
              elapsed_time_one / 1000;  // Convert to miliseconds
          elapsed_time_sec_one =
              elapsed_time_ms_one / 1000;  // Convert to seconds
          hashrate_one =
              duco_res_one / elapsed_time_sec_one;  // Calculate hashrate

          if (!client_one.connected()) {
            Serial.println(F("CORE1 Lost connection. Trying to reconnect"));
            if (!client_one.connect(host.c_str(), port)) {
              Serial.println(F("CORE1 connection failed"));
              break;
            }
            Serial.println(F("CORE1 Reconnection successful."));
          }

          client_one.flush();
          client_one.print(String(duco_res_one) + "," + String(hashrate_one) +
                           ",Official ESP32 Miner 2.73," +
                           String(rig_identifier) + ",DUCOID" +
                           String((char *)chip_id) + "," + String(walletid));  // Send result to server
          Serial.println(F("CORE1 Posting result and waiting for feedback."));

          while (!client_one.available()) {
            if (!client_one.connected()) {
              Serial.println(
                  F("CORE1 Lost connection. Didn't receive feedback."));
              break;
            }
            delay(10);
            yield();
          }
          delay(50);
          yield();

          feedback_one = client_one.readStringUntil('\n');  // Receive feedback
          client_one.flush();
          shares_one++;
          Serial.println("CORE1 " + String(feedback_one) + " share #" +
                         String(shares_one) + " (" + String(duco_res_one) +
                         ")" + " hashrate: " + String(hashrate_one));
          blink(BLINK_SHARE_FOUND);
		
          if (hashrate_one < 4000) {
            Serial.println(F("CORE1 Low hashrate. Restarting"));
            client_one.flush();
            client_one.stop();
            blink(BLINK_RESET_DEVICE);
            esp_restart();
          }
          break;  // Stop and ask for more work
        }
      }
    }
    Serial.println(F("CORE1 Not connected. Restarting core 1"));
    client_one.flush();
    client_one.stop();
  }
}

// Task2code
void Task2code(void *pvParameters) {
  WiFiClient client;
  String SERVER_VER = "";
  int buff_two_size = 0;
  String hash = "";
  String job = "";
  size_t len = 0;
  size_t final_len = 0;
  unsigned int job_two_size = 100;
  unsigned char *job1 =
      (unsigned char *)malloc(job_two_size * sizeof(unsigned char));
  byte shaResult[20];
  unsigned long StartTime = 0;
  String hash1 = "";
  unsigned int payloadLength = 0;
  unsigned long EndTime = 0;
  unsigned long elapsed_time = 0;
  float elapsed_time_ms = 0.0;
  float elapsed_time_sec = 0.0;
  String feedback = "";
  esp_task_wdt_add(NULL);

  for (;;) {
    if (ota_state)  // If the OTA is working then reset the watchdog.
      esp_task_wdt_reset();
    while (wifi_state != WL_CONNECTED || port == 0) {
      delay(1000);
      esp_task_wdt_reset();
    }
    shares_two = 0;  // Share variable

    Serial.println(F("\nCORE2 Connecting to Duino-Coin server..."));
    client.setTimeout(1);
    client.flush();
    yield();

    if (!client.connect(host.c_str(), port)) {
      Serial.println(F("CORE2 connection failed"));
      delay(500);
      continue;
    }

    Serial.println(F("CORE2 is connected"));
    while (!client.available()) {
      yield();
      if (!client.connected()) break;
      delay(10);
    }

    // Server sends SERVER_VERSION after connecting
    SERVER_VER = client.readString();
    Serial.println("CORE2 Connected to the server. Server version: " +
                   String(SERVER_VER));
    blink(BLINK_CLIENT_CONNECT); // Sucessfull connection with the server

    while (client.connected()) {
      esp_task_wdt_reset();
      Serial.println("CORE2 Asking for a new job for user: " +
                     String(username));

      client.flush();
      client.print("JOB," + String(username) + ",ESP32");  // Ask for new job
      while (!client.available()) {
        if (!client.connected()) break;
        delay(10);
      }
      yield();
      if (!client.connected()) break;
      delay(50);
      yield();

      buff_two_size = client.available();
      Serial.print(F("CORE2 Buffer size is "));
      Serial.println(buff_two_size);
      if (buff_two_size <= 10) {
        Serial.println(
            F("CORE2 Buffer size is too small. Requesting another job."));
        continue;
      }

      // Read data to the first peroid - last block hash
      hash = client.readStringUntil(',');
      // Read data to the next peroid - expected hash
      job = client.readStringUntil(',');
      // Read and calculate remaining data - difficulty
      diff_two = client.readStringUntil('\n').toInt() * 100 + 1;
      client.flush();
      job.toUpperCase();
      const char *c = job.c_str();

      len = job.length();
      final_len = len / 2;
      memset(job1, 0, job_two_size);
      for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
        job1[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;
      memset(shaResult, 0, sizeof(shaResult));

      Serial.println("CORE2 Job received: " + String(hash) + " " + String(job) +
                     " " + String(diff_two));
      StartTime = micros();  // Start time measurement

      for (unsigned long duco_res_two = 0; duco_res_two < diff_two;
           duco_res_two++) {
        hash1 = hash + String(duco_res_two);
        payloadLength = hash1.length();

        while (xSemaphoreTake(xMutex, portMAX_DELAY) != pdTRUE)
          ;
        esp_sha(SHA1, (const unsigned char *)hash1.c_str(), payloadLength,
                shaResult);
        xSemaphoreGive(xMutex);

        if (memcmp(shaResult, job1, sizeof(shaResult)) == 0) {
          EndTime = micros();                          // End time measurement
          elapsed_time = EndTime - StartTime;          // Calculate elapsed time
          elapsed_time_ms = elapsed_time / 1000;       // Convert to miliseconds
          elapsed_time_sec = elapsed_time_ms / 1000;   // Convert to seconds
          hashrate_two = duco_res_two / elapsed_time_sec;  // Calculate hashrate

          if (!client.connected()) {
            Serial.println(F("CORE2 Lost connection. Trying to reconnect"));
            if (!client.connect(host.c_str(), port)) {
              Serial.println(F("CORE2 connection failed"));
              break;
            }
            Serial.println(F("CORE2 Reconnection successful."));
          }

          client.flush();
          client.print(String(duco_res_two) + "," + String(hashrate_two) +
                       ",Official ESP32 Miner 2.73," + String(rig_identifier) +
                       ",DUCOID" + String((char *)chip_id) + "," + String(walletid));  // Send result to server
          Serial.println(F("CORE2 Posting result and waiting for feedback."));

          while (!client.available()) {
            if (!client.connected()) {
              Serial.println(
                  F("CORE2 Lost connection. Didn't receive feedback."));
              break;
            }
            delay(10);
            yield();
          }
          delay(50);
          yield();
          feedback = client.readStringUntil('\n');  // Receive feedback
          client.flush();
          shares_two++;

          Serial.println("CORE2 " + String(feedback) + " share #" +
                         String(shares_two) + " (" + String(duco_res_two) +
                         ")" + " hashrate: " + String(hashrate_two));
	  blink(BLINK_SHARE_FOUND);
		
          if (hashrate_two < 4000) {
            Serial.println(F("CORE2 Low hashrate. Restarting"));
            client.flush();
            client.stop();
	    blink(BLINK_RESET_DEVICE);
            esp_restart();
          }
          break;  // Stop and ask for more work
        }
      }
    }
    Serial.println(F("CORE2 Not connected. Restarting core 2"));
    client.flush();
    client.stop();
  }
}

void setup() {
  // disableCore0WDT();
  // disableCore1WDT();
  Serial.begin(500000);  // Start serial connection
  Serial.println("\n\nDuino-Coin Official ESP32 Miner 2.73");

  WiFi.mode(WIFI_STA);  // Setup ESP in client mode
  btStop();
  WiFi.begin(wifi_ssid, wifi_password);  // Connect to wifi

  uint64_t chipid = ESP.getEfuseMac();  // Getting chip chip_id
  uint16_t chip =
      (uint16_t)(chipid >> 32);  // Preparing for printing a 64 bit value (it's
                                 // actually 48 bits long) into a char array
  snprintf(
      (char *)chip_id, 23, "%04X%08X", chip,
      (uint32_t)chipid);  // Storing the 48 bit chip chip_id into a char array.
  walletid = random(0, 2811);

  ota_state = false;

  // Port defaults to 3232
  // ArduinoOTA.setPort(3232);

  // Hostname defaults to esp3232-[MAC]
  // ArduinoOTA.setHostname("myesp32");

  // No authentication by default
  // ArduinoOTA.setPassword("admin");

  // wifi_password can be set with it's md5 value as well
  // MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
  // ArduinoOTA.setPasswordHash("21232f297a57a5a743894a0e4a801fc3");

#ifdef ENABLE_OTA
  ArduinoOTA
      .onStart([]() {
        String type;
        if (ArduinoOTA.getCommand() == U_FLASH)
          type = "sketch";
        else  // U_SPIFFS
          type = "filesystem";

        // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS
        // using SPIFFS.end()
        Serial.println("Start updating " + type);
        ota_state = true;
      })
      .onEnd([]() { Serial.println(F("\nEnd")); })
      .onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
        esp_task_wdt_reset();
        ota_state = true;
      })
      .onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR)
          Serial.println(F("Auth Failed"));
        else if (error == OTA_BEGIN_ERROR)
          Serial.println(F("Begin Failed"));
        else if (error == OTA_CONNECT_ERROR)
          Serial.println(F("Connect Failed"));
        else if (error == OTA_RECEIVE_ERROR)
          Serial.println(F("Receive Failed"));
        else if (error == OTA_END_ERROR)
          Serial.println(F("End Failed"));
        ota_state = false;
	blink(BLINK_RESET_DEVICE);
        esp_restart();
      });

  ArduinoOTA.setHostname(rig_identifier);
  ArduinoOTA.begin();
#endif

  esp_task_wdt_init(WDT_TIMEOUT, true);  // Init Watchdog timer
  pinMode(LED_BUILTIN, OUTPUT);

  xMutex = xSemaphoreCreateMutex();
  xTaskCreatePinnedToCore(
      WiFireconnect, "WiFirec", 10000, NULL, 3, &WiFirec,
      0);  // create a task with priority 3 and executed on core 0
  delay(250);
  xTaskCreatePinnedToCore(
      Task1code, "Task1", 10000, NULL, 1, &Task1,
      0);  // create a task with priority 1 and executed on core 0
  delay(250);
  xTaskCreatePinnedToCore(
      Task2code, "Task2", 10000, NULL, 2, &Task2,
      1);  // create a task with priority 2 and executed on core 1
  delay(250);
  xTaskCreatePinnedToCore(
      MinerCheckinCode, "MinerCheckin", 10000, NULL, 1, &MinerCheckin, 
      1); //create a task with priority 1 and executed on core 1
  delay(250);
}

// ************************************************************
void MinerCheckinCode( void * pvParameters ) {
	// This function can periodically update a server on the EPS32. 
	// The sever details and request parameters are specific, but I have an example below

	unsigned long lastWdtReset = 0;
	unsigned long wdtResetDelay = 1000;
	for(;;) {
		if ((millis() - lastWdtReset) > wdtResetDelay) {
			esp_task_wdt_reset();
			lastWdtReset = millis();
		}
		yield();
	}
	/**************************************************
	 * Example code
	const char* serverName = "http://10.10.1.1/api/espCheckin.php"; // the URL of my checking API

	unsigned long checkinDelay = 10000; // Check in to the IOT service every 10 seconds
	unsigned long wdtResetDelay = 1000; // How often to reset the watchdog timer

	unsigned long lastCheckin = 0;
	unsigned long lastWdtReset = 0;
	unsigned long lastShares = 0;

	esp_task_wdt_add(NULL);// Register this task with the watchdog
	for(;;) { // Loop forever
		if ((millis() - lastWdtReset) > wdtResetDelay) {
			esp_task_wdt_reset();
			lastWdtReset = millis();
		}

		if (WiFi.status() == WL_CONNECTED && (millis() - lastCheckin) > checkinDelay) {
			WiFiClient client;
			HTTPClient http;
			http.begin(client, serverName);
			http.setTimeout(2000); // Set the timeout low so we don't hang anything too much
			http.addHeader("Content-Type", "application/x-www-form-urlencoded");
			String httpRequestData = String("rigname=") + rig_identifier;
			httpRequestData = httpRequestData + "&username=" + username;
			httpRequestData = httpRequestData + "&pool=" + host + ":" + port;
			httpRequestData = httpRequestData + "&accepted_1=" + shares_one;
			httpRequestData = httpRequestData + "&accepted_2=" + shares_two;
			httpRequestData = httpRequestData + "&hashrate_1=" + hashrate_one;
			httpRequestData = httpRequestData + "&hashrate_2=" + hashrate_two;
			httpRequestData = httpRequestData + "&difficulty_1=" + diff_one;
			httpRequestData = httpRequestData + "&difficulty_2=" + diff_two;
			httpRequestData = httpRequestData + "&connected=" + ((shares_one + shares_two)>lastShares);
			
			int httpResponseCode = http.POST(httpRequestData);
			if(0) { // Save cycles and I don't care what they said, but could do
				yield();
				Serial.print("CHECKIN: Response code: ");
				Serial.print(httpResponseCode);
				if(httpResponseCode == HTTP_CODE_OK) {
					String payload = http.getString();
					DynamicJsonDocument doc(1024);
					char buffer[2048];
	
					yield();
					deserializeJson(doc, payload);
					serializeJsonPretty(doc, buffer);
					Serial.print(" ");
					Serial.println(buffer);
				} else {
					Serial.print(", Error: ");
					Serial.println(http.errorToString(httpResponseCode).c_str());
				}
			}
			http.end();
			lastCheckin = millis();
			lastShares = shares_one + shares_two;
		}
		yield();
	}
	*/
}

void loop() {}
