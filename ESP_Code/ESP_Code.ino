/*
   ____  __  __  ____  _  _  _____       ___  _____  ____  _  _
  (  _ \(  )(  )(_  _)( \( )(  _  )___  / __)(  _  )(_  _)( \( )
   )(_) ))(__)(  _)(_  )  (  )(_)((___)( (__  )(_)(  _)(_  )  (
  (____/(______)(____)(_)\_)(_____)     \___)(_____)(____)(_)\_)
  Official code for all ESP8266/32 boards            version 4.1
  Main .ino file

  The Duino-Coin Team & Community 2019-2024 © MIT Licensed
  https://duinocoin.com
  https://github.com/revoxhere/duino-coin

  If you don't know where to start, visit official website and navigate to
  the Getting Started page. Have fun mining!

  To edit the variables (username, WiFi settings, etc.) use the Settings.h tab!
*/

/* If optimizations cause problems, change them to -O0 (the default) */
#pragma GCC optimize("-Ofast")

/* If during compilation the line below causes a
  "fatal error: arduinoJson.h: No such file or directory"
  message to occur; it means that you do NOT have the
  ArduinoJSON library installed. To install it,
  go to the below link and follow the instructions:
  https://github.com/revoxhere/duino-coin/issues/832 */
#include <ArduinoJson.h>

#if defined(ESP8266)
    #include <ESP8266WiFi.h>
    #include <ESP8266mDNS.h>
    #include <ESP8266HTTPClient.h>
    #include <ESP8266WebServer.h>
#else
    #include <ESPmDNS.h>
    #include <WiFiClientSecure.h>
    #include <WiFi.h>
    #include <HTTPClient.h>
    #include <WebServer.h>
#endif

#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <WiFiClient.h>
#include <Ticker.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "MiningJob.h"
#include "Settings.h"

#ifdef USE_LAN
  #include <ETH.h>
#endif

#if defined(WEB_DASHBOARD)
  #include "Dashboard.h"
#endif

// Auto adjust physical core count
// (ESP32-S2/C3 have 1 core, ESP32 has 2 cores, ESP8266 has 1 core)
#if defined(ESP8266)
    #define CORE 1
    typedef ESP8266WebServer WebServer;
#elif defined(CONFIG_FREERTOS_UNICORE)
    #define CORE 1
#else
    #define CORE 2
    // Install TridentTD_EasyFreeRTOS32 if you get an error
    #include <TridentTD_EasyFreeRTOS32.h>
#endif

#if defined(WEB_DASHBOARD)
    WebServer server(80);
#endif

namespace {
    MiningConfig *configuration = new MiningConfig(
        DUCO_USER,
        RIG_IDENTIFIER,
        MINER_KEY
    );

    #if defined(ESP32) && CORE == 2
      EasyMutex mutexClientData, mutexConnectToServer;
    #endif

    #ifdef USE_LAN
      static bool eth_connected = false;
    #endif

    void UpdateHostPort(String input) {
        // Thanks @ricaun for the code
        DynamicJsonDocument doc(256);
        deserializeJson(doc, input);
        const char *name = doc["name"];

        configuration->host = doc["ip"].as<String>().c_str();
        configuration->port = doc["port"].as<int>();
        node_id = String(name);

        #if defined(SERIAL_PRINTING)
          Serial.println("Poolpicker selected the best mining node: " + node_id);
        #endif
    }

    String httpGetString(String URL) {
        String payload = "";
        WiFiClientSecure client;
        client.setInsecure();
        HTTPClient http;

        if (http.begin(client, URL)) {
          int httpCode = http.GET();

          if (httpCode == HTTP_CODE_OK)
            payload = http.getString();
          else
            #if defined(SERIAL_PRINTING)
               Serial.printf("Error fetching node from poolpicker: %s\n", http.errorToString(httpCode).c_str());
            #endif

          http.end();
        }
        return payload;
    }

    void SelectNode() {
        String input = "";
        int waitTime = 1;
        int poolIndex = 0;

        while (input == "") {
            #if defined(SERIAL_PRINTING)
              Serial.println("Fetching mining node from the poolpicker in " + String(waitTime) + "s");
            #endif
            input = httpGetString("https://server.duinocoin.com/getPool");
            
            delay(waitTime * 1000);
            // Increase wait time till a maximum of 32 seconds
            // (addresses: Limit connection requests on failure in ESP boards #1041)
            waitTime *= 2;
            if (waitTime > 32)
                  waitTime = 32;
        }

        UpdateHostPort(input);
      }

    #ifdef USE_LAN
    void WiFiEvent(WiFiEvent_t event)
    {
      switch (event) {
        case ARDUINO_EVENT_ETH_START:
          #if defined(SERIAL_PRINTING)
            Serial.println("ETH Started");
          #endif
          // The hostname must be set after the interface is started, but needs
          // to be set before DHCP, so set it from the event handler thread.
          ETH.setHostname("esp32-ethernet");
          break;
        case ARDUINO_EVENT_ETH_CONNECTED:
          #if defined(SERIAL_PRINTING)
            Serial.println("ETH Connected");
          #endif
          break;
        case ARDUINO_EVENT_ETH_GOT_IP:
          #if defined(SERIAL_PRINTING)
            Serial.println("ETH Got IP");
          #endif
          eth_connected = true;
          break;

        case ARDUINO_EVENT_ETH_DISCONNECTED:
          #if defined(SERIAL_PRINTING)
            Serial.println("ETH Disconnected");
          #endif
          eth_connected = false;
          break;
        case ARDUINO_EVENT_ETH_STOP:
          #if defined(SERIAL_PRINTING)
            Serial.println("ETH Stopped");
          #endif
          eth_connected = false;
          break;
        default:
          break;
      }
    }
    #endif

    void SetupWifi() {
      
      #ifdef USE_LAN
        #if defined(SERIAL_PRINTING)
          Serial.println("Connecting to Ethernet...");
        #endif
        WiFi.onEvent(WiFiEvent);  // Will call WiFiEvent() from another thread.
        ETH.begin();
        

        while (!eth_connected) {
            delay(500);
            #if defined(SERIAL_PRINTING)
                Serial.print(".");
            #endif
        }

        #if defined(SERIAL_PRINTING)
          Serial.println("\n\nSuccessfully connected to Ethernet");
          Serial.println("Local IP address: " + ETH.localIP().toString());
          Serial.println("Rig name: " + String(RIG_IDENTIFIER));
          Serial.println();
        #endif

      #else
        #if defined(SERIAL_PRINTING)
          Serial.println("Connecting to: " + String(SSID));
        #endif
        WiFi.mode(WIFI_STA); // Setup ESP in client mode
        #if defined(ESP8266)
            WiFi.setSleepMode(WIFI_NONE_SLEEP);
        #else
            WiFi.setSleep(false);
        #endif
        WiFi.begin(SSID, PASSWORD);

        int wait_passes = 0;
        while (WiFi.waitForConnectResult() != WL_CONNECTED) {
            delay(500);
            #if defined(SERIAL_PRINTING)
              Serial.print(".");
            #endif
            if (++wait_passes >= 10) {
                WiFi.begin(SSID, PASSWORD);
                wait_passes = 0;
            }
        }

        #if defined(SERIAL_PRINTING)
          Serial.println("\n\nSuccessfully connected to WiFi");
          Serial.println("Local IP address: " + WiFi.localIP().toString());
          Serial.println("Rig name: " + String(RIG_IDENTIFIER));
          Serial.println();
        #endif

      #endif

        SelectNode();
    }

    void SetupOTA() {
        // Prepare OTA handler
        ArduinoOTA.onStart([]()
                           { 
                             #if defined(SERIAL_PRINTING)
                               Serial.println("Start"); 
                             #endif
                           });
        ArduinoOTA.onEnd([]()
                         { 
                            #if defined(SERIAL_PRINTING)
                              Serial.println("\nEnd"); 
                            #endif
                         });
        ArduinoOTA.onProgress([](unsigned int progress, unsigned int total)
                              { 
                                 #if defined(SERIAL_PRINTING)
                                   Serial.printf("Progress: %u%%\r", (progress / (total / 100))); 
                                 #endif
                              });
        ArduinoOTA.onError([](ota_error_t error)
                           {
                                Serial.printf("Error[%u]: ", error);
                                #if defined(SERIAL_PRINTING)
                                  if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
                                  else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
                                  else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
                                  else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
                                  else if (error == OTA_END_ERROR) Serial.println("End Failed");
                                #endif
                          });

        ArduinoOTA.setHostname(RIG_IDENTIFIER); // Give port a name
        ArduinoOTA.begin();
    }

    void VerifyWifi() {
      #ifdef USE_LAN
        while ((!eth_connected) || (ETH.localIP() == IPAddress(0, 0, 0, 0))) {
          #if defined(SERIAL_PRINTING)
            Serial.println("Ethernet connection lost. Reconnect..." );
          #endif
          SetupWifi();
        }
      #else
        while (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0, 0, 0, 0))
            WiFi.reconnect();
      #endif
    }

    void handleSystemEvents(void) {
        VerifyWifi();
        ArduinoOTA.handle();
        yield();
    }

    #if defined(WEB_DASHBOARD)
        void dashboard() {
             #if defined(SERIAL_PRINTING)
               Serial.println("Handling HTTP client");
             #endif
             String s = WEBSITE;
             #ifdef USE_LAN
              s.replace("@@IP_ADDR@@", ETH.localIP().toString());
             #else
              s.replace("@@IP_ADDR@@", WiFi.localIP().toString());
             #endif
  
             s.replace("@@HASHRATE@@", String(hashrate / 1000));
             s.replace("@@DIFF@@", String(difficulty / 100));
             s.replace("@@SHARES@@", String(share_count));
             s.replace("@@NODE@@", String(node_id));
             
             #if defined(ESP8266)
                 s.replace("@@DEVICE@@", "ESP8266");
             #elif defined(CONFIG_FREERTOS_UNICORE)
                 s.replace("@@DEVICE@@", "ESP32-S2/C3");
             #else
                 s.replace("@@DEVICE@@", "ESP32");
             #endif
             
             s.replace("@@ID@@", String(RIG_IDENTIFIER));
             s.replace("@@MEMORY@@", String(ESP.getFreeHeap()));
             s.replace("@@VERSION@@", String(SOFTWARE_VERSION));
             server.send(200, "text/html", s);
        }
    #endif

} // End of namespace

MiningJob *job[CORE];

#if CORE == 2
  EasyFreeRTOS32 task1, task2;
#endif

void task1_func(void *) {
    #if defined(ESP32) && CORE == 2
      VOID SETUP() { }

      VOID LOOP() {
        job[0]->mine();
      }
    #endif
}

void task2_func(void *) {
    #if defined(ESP32) && CORE == 2
      VOID SETUP() {
        job[1] = new MiningJob(1, configuration);
      }

      VOID LOOP() {
        job[1]->mine();
      }
    #endif
}

void setup() {
    delay(500);
    
    #if defined(SERIAL_PRINTING)
      Serial.begin(500000);
      Serial.println("\n\nDuino-Coin " + String(configuration->MINER_VER));
    #endif
    pinMode(LED_BUILTIN, OUTPUT);

    assert(CORE == 1 || CORE == 2);
    WALLET_ID = String(random(0, 2811)); // Needed for miner grouping in the wallet
    job[0] = new MiningJob(0, configuration);

    #if defined(USE_DHT)
        #if defined(SERIAL_PRINTING)
          Serial.println("Initializing DHT sensor (Duino IoT)");
        #endif
        dht.begin();
        #if defined(SERIAL_PRINTING)
          Serial.println("Test reading: " + String(dht.readHumidity()) + "% humidity");
          Serial.println("Test reading: temperature " + String(dht.readTemperature()) + "°C");
        #endif
    #endif

    #if defined(USE_DS18B20)
        #if defined(SERIAL_PRINTING)
          Serial.println("Initializing DS18B20 sensor (Duino IoT)");
        #endif
        sensors.begin();
        sensors.requestTemperatures(); 
        #if defined(SERIAL_PRINTING)
          Serial.println("Test reading: " + String(sensors.getTempCByIndex(0)) + "°C");
        #endif
    #endif

    #if defined(USE_INTERNAL_SENSOR)
       #if defined(SERIAL_PRINTING)
         Serial.println("Initializing internal ESP32 temperature sensor (Duino IoT)");
       #endif
       temp_sensor_config_t temp_sensor = TSENS_CONFIG_DEFAULT();
       temp_sensor.dac_offset = TSENS_DAC_L2;
       temp_sensor_set_config(temp_sensor);
       temp_sensor_start();
       float result = 0;
       temp_sensor_read_celsius(&result);
       #if defined(SERIAL_PRINTING)
         Serial.println("Test reading: " + String(result) + "°C");
       #endif
    #endif

    SetupWifi();
    SetupOTA();

    #if defined(WEB_DASHBOARD)
      if (!MDNS.begin(RIG_IDENTIFIER)) {
        #if defined(SERIAL_PRINTING)
          Serial.println("mDNS unavailable");
        #endif
      }
      MDNS.addService("http", "tcp", 80);
      #if defined(SERIAL_PRINTING)
        #ifdef USE_LAN
          Serial.println("Configured mDNS for dashboard on http://" + String(RIG_IDENTIFIER) 
                     + ".local (or http://" + ETH.localIP().toString() + ")");
        #else
          Serial.println("Configured mDNS for dashboard on http://" + String(RIG_IDENTIFIER) 
                     + ".local (or http://" + WiFi.localIP().toString() + ")");
        #endif
      #endif

      server.on("/", dashboard);
      server.begin();
    #endif

    job[0]->blink(BLINK_SETUP_COMPLETE);

    #if CORE == 2 && defined(ESP32)
        task1.start(task1_func);
        task2.start(task2_func);
    #endif
}

void loopOneCore() {
    job[0]->mine();

    #if defined(ESP8266)
        // Fastest clock mode for 8266s
        system_update_cpu_freq(160);
    #else
        // Fastest clock mode for 32s
        setCpuFrequencyMhz(240);
    #endif
    
    VerifyWifi();
    ArduinoOTA.handle();
    #if defined(WEB_DASHBOARD) 
        server.handleClient();
    #endif
}

void loop() {
    #if CORE == 1
        loopOneCore();
    #endif
}
