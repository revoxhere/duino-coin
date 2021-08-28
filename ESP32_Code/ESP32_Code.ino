/*
  ,------.          ,--.                       ,-----.       ,--.         
  |  .-.  \ ,--.,--.`--',--,--,  ,---. ,-----.'  .--./ ,---. `--',--,--,  
  |  |  \  :|  ||  |,--.|      \| .-. |'-----'|  |    | .-. |,--.|      \ 
  |  '--'  /'  ''  '|  ||  ||  |' '-' '       '  '--'\' '-' '|  ||  ||  | 
  `-------'  `----' `--'`--''--' `---'         `-----' `---' `--'`--''--' 
  Official code for ESP32 boards                            version 2.6.5
  
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
/ Define watchdog timer seconds
#define WDT_TIMEOUT 60

/* WARNING choosing the pool from the device will require at least 4k of dynamic memory on your board
 *  It is also not known what the full extent on the pools will be so use with caution for now. If 
 *  you disable the pool choice from the server report any issue you find. Here is the history for 
 *  this change: https://github.com/revoxhere/duino-coin/issues/894 
 */
#define USE_SERVER_CHOSEN_POOL true

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

#if (USE_SERVER_CHOSEN_POOL)
const char *get_pool_api = "http://51.15.127.80:4242/getPool";
#else
const char *get_pool_list_api = "TBD"; // To be implimented - will hard code to SSL server for now
const int con_cap = 10000; // do not connect to servers with over this many connections
const float cpu_cap = 90; // do not connect to servers with over thisCPU in use
const float ram_cap = 90; // do not connect to servers with over this RAM in use
#define FIND_POOL_DEBUG false
#endif

TaskHandle_t WiFirec;
TaskHandle_t Task1;
TaskHandle_t Task2;
TaskHandle_t MinerCheckin;
SemaphoreHandle_t xMutex;

String host;
int port;
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

#if (USE_SERVER_CHOSEN_POOL)
// This is the 'current' functionality where the server chooses a pool for you.
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

  port = p;
  host = h;

  Serial.println("Fetched pool: " + String(name) + " - " + String(host) + ":" +
                 String(port));
}

#else
// This is the 'new' functionality where the server returns all of the pools and the ESP will iterate through checking for the fastest connection.
// All it does is sets the host/port global variables for the connection it chooses, then the threads kick in as normal after that
String getPoolList() {
	if(strlen(get_pool_list_api)) {
		String pools = "";
	
		// Hard code a default for testing until we get a public URL
		pools += "{\"result\":[";
		pools += "{\"ip\":\"149.91.88.18\",\"name\":\"pulse-pool-1\",\"port\":1612,\"status\":\"True\",\"ram\":50,\"cpu\":50,\"connections\":50},";
		pools += "{\"ip\":\"149.91.88.18\",\"name\":\"pulse-pool-2\",\"port\":6004,\"status\":\"True\",\"ram\":50,\"cpu\":50,\"connections\":50},";
		pools += "{\"ip\":\"51.158.182.90\",\"name\":\"star-pool-1\",\"port\":6000,\"status\":\"True\",\"ram\":50,\"cpu\":50,\"connections\":50},";
		pools += "{\"ip\":\"50.112.145.154\",\"name\":\"beyond-pool-1\",\"port\":6000,\"status\":\"True\",\"ram\":50,\"cpu\":50,\"connections\":50},";
		pools += "{\"ip\":\"35.173.194.122\",\"name\":\"beyond-pool-2\",\"port\":6000,\"status\":\"True\",\"ram\":50,\"cpu\":50,\"connections\":50}";
		pools += "],\"success\":true}";

		// If the server returns a pool list, then use that instead
		String http_pools = httpGetString(get_pool_list_api);
		if(http_pools.length()) {
			pools = http_pools;
		}
	
		return pools;
	}
	String server = "server.duinocoin.com";
	String uri = "/all_pools";
	const char* root_ca = \
		"-----BEGIN CERTIFICATE-----\n" \
		"MIIDSjCCAjKgAwIBAgIQRK+wgNajJ7qJMDmGLvhAazANBgkqhkiG9w0BAQUFADA/\n" \
		"MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT\n" \
		"DkRTVCBSb290IENBIFgzMB4XDTAwMDkzMDIxMTIxOVoXDTIxMDkzMDE0MDExNVow\n" \
		"PzEkMCIGA1UEChMbRGlnaXRhbCBTaWduYXR1cmUgVHJ1c3QgQ28uMRcwFQYDVQQD\n" \
		"Ew5EU1QgUm9vdCBDQSBYMzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB\n" \
		"AN+v6ZdQCINXtMxiZfaQguzH0yxrMMpb7NnDfcdAwRgUi+DoM3ZJKuM/IUmTrE4O\n" \
		"rz5Iy2Xu/NMhD2XSKtkyj4zl93ewEnu1lcCJo6m67XMuegwGMoOifooUMM0RoOEq\n" \
		"OLl5CjH9UL2AZd+3UWODyOKIYepLYYHsUmu5ouJLGiifSKOeDNoJjj4XLh7dIN9b\n" \
		"xiqKqy69cK3FCxolkHRyxXtqqzTWMIn/5WgTe1QLyNau7Fqckh49ZLOMxt+/yUFw\n" \
		"7BZy1SbsOFU5Q9D8/RhcQPGX69Wam40dutolucbY38EVAjqr2m7xPi71XAicPNaD\n" \
		"aeQQmxkqtilX4+U9m5/wAl0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNV\n" \
		"HQ8BAf8EBAMCAQYwHQYDVR0OBBYEFMSnsaR7LHH62+FLkHX/xBVghYkQMA0GCSqG\n" \
		"SIb3DQEBBQUAA4IBAQCjGiybFwBcqR7uKGY3Or+Dxz9LwwmglSBd49lZRNI+DT69\n" \
		"ikugdB/OEIKcdBodfpga3csTS7MgROSR6cz8faXbauX+5v3gTt23ADq1cEmv8uXr\n" \
		"AvHRAosZy5Q6XkjEGB5YGV8eAlrwDPGxrancWYaLbumR9YbK+rlmM6pZW87ipxZz\n" \
		"R8srzJmwN0jP41ZL9c8PDHIyh8bwRLtTcm1D9SZImlJnt1ir/md2cXjbDaJWFBM5\n" \
		"JDGFoqgCWjBH4d1QB7wCCZAA62RjYJsWvIjJEubSfZGL+T0yjWW06XyxV3bqxbYo\n" \
		"Ob8VZRzI9neWagqNdwvYkQsEjgfbKbYK7p2CNTUQ\n" \
		"-----END CERTIFICATE-----\n";

	String payload = "";
	WiFiClientSecure client;
	client.setCACert(root_ca);

#if (FIND_POOL_DEBUG) 
	Serial.println("[HTTPS] CONNECT: " + server);
#endif
	if (!client.connect(server.c_str(), 443)) {
		Serial.println("[HTTPS] Connection failed.");
		return payload;
	}
	String tx = "";

	tx = "GET " + uri + " HTTP/1.1";
#if (FIND_POOL_DEBUG)
	Serial.println("[TX] " + tx);
#endif
	client.print(tx + "\r\n");

	tx = "Host: " + server;
#if (FIND_POOL_DEBUG)
	Serial.println("[TX] " + tx);
#endif
	client.print(tx + "\r\n");

	tx = "Connection: close";
#if (FIND_POOL_DEBUG)
	Serial.println("[TX] " + tx);
#endif
	client.print(tx + "\r\n");

	tx = "";
#if (FIND_POOL_DEBUG)
	Serial.println("[TX] " + tx);
#endif
	client.print(tx + "\r\n");
	
	int maxloops = 0;
	
	//wait for the server's reply to become available
	while (!client.available() && maxloops < 1000) {
		yield();
		delay(1);
		maxloops++;
	}

	bool body = false;
	while (client.available() && maxloops < 1000) {
		//read back one line from the server
		String line = client.readStringUntil('\n'); // Ending is \r\n
		line.trim();
#if (FIND_POOL_DEBUG)
		Serial.println("[RX] " + line);
#endif
		if(line.length() == 0 && !body) {
			body = true;
		}
		if(body && line.length()) {
			payload += line;
		}
		yield();
		maxloops++;
	}
	
#if (FIND_POOL_DEBUG)
	Serial.println("[HTTPS] Closing connection.");
#endif
	client.stop();

  return payload;
}

void findPool() {
	Serial.println(F("findPool(): Retrieving pool list"));
	String pools = getPoolList();

	if(pools.length()) {
		StaticJsonDocument<4096> doc; // 4k might be big, but we need at least 2k right now with 5 pools
		DeserializationError error = deserializeJson(doc, pools);
		if (error) {
			Serial.print(F("findPool(): Bad JSON: "));
			Serial.println(error.f_str());
			delay(5000);
            esp_restart();
		} else {
			if(doc.containsKey("result")) {
				String best_name = "";
				String best_host = "";
				int best_port = 0;
				unsigned long best_ms = 99999;
	
				const JsonArray& result =  doc["result"];
				for(JsonVariant v : result) {
					String status = v["status"].as<const char*>();
					String name = v["name"].as<const char*>();
					String ip = v["ip"].as<const char*>();
					int lp = v["port"].as<const int>();
					float ram = v["ram"].as<const float>();
					float cpu = v["cpu"].as<const float>();
					int con = v["connections"].as<const int>();
	
					// Only connect to servers that are 'safe'
					if(status == "True") {
						if(ram > 0 && ram < ram_cap) {
							if(cpu > 0 && cpu < cpu_cap) {
								if(con > 0 && con < con_cap) {
									Serial.print(String("findPool(): Checking '") + name + "'");
									//Serial.print ("url: http://" + url);
				
								    unsigned long start = millis();
									WiFiClient client;
								    client.setTimeout(1);
								    client.flush();
								    yield();
				
									if (!client.connect(ip.c_str(), lp)) {
										Serial.println(F(" - connection failed"));
									} else {
										while (!client.available()) {
											yield();
											if (!client.connected()) break;
											delay(10);
										}
				
										// Server sends SERVER_VERSION after connecting
										String server_version = client.readString();
									    unsigned long duration = millis() - start;
										Serial.println(String(" - ") + duration + " ms");
									    if(duration < best_ms) {
									    	best_ms = duration;
									    	best_host = ip;
									    	best_port = lp;
									    	best_name = name;
									    }
										client.flush();
										client.stop();
										esp_task_wdt_reset();
										yield();
									}
								} else {
#if (FIND_POOL_DEBUG)
									Serial.print(String("findPool(): Skipping '") + name + "'");
									Serial.print (F(" - ("));
									Serial.print (String("connections: ") + con + "/" + con_cap);
									Serial.print (F(")"));
									//Serial.print (String(" on http://") + url);
									Serial.println();
#endif
								}
							} else {
#if (FIND_POOL_DEBUG)
								Serial.print(String("findPool(): Skipping '") + name + "'");
								Serial.print (F(" - ("));
								Serial.print (String("cpu: ") + cpu + "/" + cpu_cap);
								Serial.print (F(")"));
								//Serial.print (String(" on http://") + url);
								Serial.println();
#endif
							}
						} else {
#if (FIND_POOL_DEBUG)
							Serial.print(String("findPool(): Skipping '") + name + "'");
							Serial.print (F(" - ("));
							Serial.print (String("ram: ") + ram + "/" + ram_cap);
							Serial.print (F(")"));
							//Serial.print (String(" on http://") + url);
							Serial.println();
#endif
						}
					} else {
#if (FIND_POOL_DEBUG)
						Serial.print(String("findPool(): Skipping '") + name + "'");
						Serial.print (F(" - ("));
						Serial.print (String("status: ") + status);
						Serial.print (F(")"));
						//Serial.print (String(" on http://") + url);
						Serial.println();
#endif
					}
				}
	
				if(best_host.length()) {
					Serial.print(String("\nfindPool(): best connection: '") + best_name + "'");
#if (FIND_POOL_DEBUG)
					Serial.print(String(" at ") + best_ms + "ms");
#endif
					Serial.println();
					port = best_port;
					host = best_host;
				} else {
					Serial.println(F("findPool(): no pools"));
					delay(5000);
		            esp_restart();
				}
			} else {
				Serial.println(F("findPool(): bad response"));
				delay(5000);
	            esp_restart();
			}
		}
	}
}
#endif

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

#if (USE_SERVER_CHOSEN_POOL)
      UpdatePool();
      yield();
      delay(100);
#else
      findPool();
#endif
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
    while (wifi_state != WL_CONNECTED) {
      yield();
      delay(1000);
      esp_task_wdt_reset();
    }
    if(host.length()) {
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
	    digitalWrite(LED_BUILTIN, HIGH);  // Turn off built-in led
	    delay(50);
	    digitalWrite(LED_BUILTIN, LOW);  // Turn on built-in led
	    Serial.println("CORE1 Connected to the server. Server version: " +
	                   String(SERVER_VER));
	    digitalWrite(LED_BUILTIN, HIGH);  // Turn off built-in led
	    delay(50);
	    digitalWrite(LED_BUILTIN, LOW);  // Turn on built-in led
	
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
	                           ",ESP32 CORE1 Miner v2.65," +
	                           String(rig_identifier) + "," +
	                           String((char *)chip_id));  // Send result to server
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
	
	          if (hashrate_one < 4000) {
	            Serial.println(F("CORE1 Low hashrate. Restarting"));
	            client_one.flush();
	            client_one.stop();
	            esp_restart();
	          }
	          break;  // Stop and ask for more work
	        }
	      }
	    }
	    Serial.println(F("CORE1 Not connected. Restarting core 1"));
	    client_one.flush();
	    client_one.stop();
	  } else {
	    esp_task_wdt_reset();
	    delay(100);
	  	yield();
	  }
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
    while (wifi_state != WL_CONNECTED) {
      yield();
      delay(1000);
      esp_task_wdt_reset();
    }
 
	if(host.length()) {
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
	    digitalWrite(LED_BUILTIN, HIGH);  // Turn off built-in led
	    delay(50);
	    digitalWrite(LED_BUILTIN, LOW);  // Turn on built-in led
	    Serial.println("CORE2 Connected to the server. Server version: " +
	                   String(SERVER_VER));
	    digitalWrite(LED_BUILTIN, HIGH);  // Turn off built-in led
	    delay(50);
	    digitalWrite(LED_BUILTIN, LOW);  // Turn on built-in led
	
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
	                       ",ESP32 CORE2 Miner v2.65," + String(rig_identifier) +
	                       "," + String((char *)chip_id));  // Send result to server
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
	          if (hashrate_two < 4000) {
	            Serial.println(F("CORE2 Low hashrate. Restarting"));
	            client.flush();
	            client.stop();
	            esp_restart();
	          }
	          break;  // Stop and ask for more work
	        }
	      }
	    }
	    Serial.println(F("CORE2 Not connected. Restarting core 2"));
	    client.flush();
	    client.stop();
	  } else {
	    esp_task_wdt_reset();
	    delay(100);
	  	yield();
	  }
  }
}

void setup() {
  // disableCore0WDT();
  // disableCore1WDT();
  Serial.begin(500000);  // Start serial connection
  Serial.println("\n\nDuino-Coin ESP32 Miner v2.65");

  WiFi.mode(WIFI_STA);  // Setup ESP in client mode
  btStop();
  WiFi.begin(wifi_ssid, wifi_password);  // Connect to wifi

  uint64_t chipid = ESP.getEfuseMac();  // Getting chip chip_id
  uint16_t chip =
      (uint16_t)(chipid >> 32);  // Preparing for printing a 64 bit value (it's
                                 // actually 48 bits long) into a char array
  snprintf(
      (char *)chip_id, 23, "DUCOID%04X%08X", chip,
      (uint32_t)chipid);  // Storing the 48 bit chip chip_id into a char array.

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
	// This function can periodically update a server on the status of the ESP32 miner. 
	// The server details and request parameters are specific, but I have an example below.

	unsigned long lastWdtReset = 0;
	unsigned long wdtResetDelay = 1000;
	for(;;) {
		if ((millis() - lastWdtReset) > wdtResetDelay) {
			esp_task_wdt_reset();
			lastWdtReset = millis();
		}
		yield();
	}
	
//	const char* apiUrl = "http://10.10.1.1/api/espCheckin.php"; // the URL of the checking API
//
//	unsigned long checkinDelay = 10000; // Check in to the IOT service every 10 seconds
//	unsigned long lastCheckin = 0;
//	unsigned long lastShares = 0;
//
//	esp_task_wdt_add(NULL);// Register this task with the watchdog
//	for(;;) { // Loop forever
//		if ((millis() - lastWdtReset) > wdtResetDelay) {
//			esp_task_wdt_reset();
//			lastWdtReset = millis();
//		}
//
//		if (WiFi.status() == WL_CONNECTED && (millis() - lastCheckin) > checkinDelay) {
//			WiFiClient client;
//			HTTPClient http;
//			http.begin(client, apiUrl);
//			http.setTimeout(2000); // Set the timeout low so we don't hang anything too much
//			http.addHeader("Content-Type", "application/x-www-form-urlencoded");
//			String httpRequestData = String("rigname=") + rig_identifier;
//			httpRequestData = httpRequestData + "&username=" + username;
//			httpRequestData = httpRequestData + "&pool=" + host + ":" + port;
//			httpRequestData = httpRequestData + "&accepted_1=" + shares_one;
//			httpRequestData = httpRequestData + "&accepted_2=" + shares_two;
//			httpRequestData = httpRequestData + "&hashrate_1=" + hashrate_one;
//			httpRequestData = httpRequestData + "&hashrate_2=" + hashrate_two;
//			httpRequestData = httpRequestData + "&difficulty_1=" + (diff_one-1)/100;
//			httpRequestData = httpRequestData + "&difficulty_2=" + (diff_two-1)/100;
//			httpRequestData = httpRequestData + "&connected=" + ((shares_one + shares_two)>lastShares);
//			
//			int httpResponseCode = http.POST(httpRequestData);
//			if(0) { // Save cycles and I don't care what they said, but could do
//				yield();
//				Serial.print("CHECKIN: Response code: ");
//				Serial.print(httpResponseCode);
//				if(httpResponseCode == HTTP_CODE_OK) {
//					String payload = http.getString();
//					DynamicJsonDocument doc(1024);
//					char buffer[2048];
//	
//					yield();
//					deserializeJson(doc, payload);
//					serializeJsonPretty(doc, buffer);
//					Serial.print(" ");
//					Serial.println(buffer);
//				} else {
//					Serial.print(", Error: ");
//					Serial.println(http.errorToString(httpResponseCode).c_str());
//				}
//			}
//			http.end();
//			lastCheckin = millis();
//			lastShares = shares_one + shares_two;
//		}
//		yield();
//	}
}
void loop() {}
