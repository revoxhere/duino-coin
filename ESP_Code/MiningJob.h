#pragma GCC optimize("-Ofast")

#ifndef MINING_JOB_H
#define MINING_JOB_H

#include <Arduino.h>
#include <assert.h>
#include <string.h>
#include <Ticker.h>
#include <WiFiClient.h>

#include "DSHA1.h"
#include "Counter.h"
#include "Settings.h"

// https://github.com/esp8266/Arduino/blob/master/cores/esp8266/TypeConversion.cpp
const char base36Chars[36] PROGMEM = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
};

const uint8_t base36CharValues[75] PROGMEM{
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0,                                                                        // 0 to 9
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 0, 0, 0, 0, 0, 0, // Upper case letters
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35                    // Lower case letters
};

#define SPC_TOKEN ' '
#define END_TOKEN '\n'
#define SEP_TOKEN ','
#define IOT_TOKEN '@'

struct MiningConfig {
    String host = "";
    int port = 0;
    String DUCO_USER = "";
    String RIG_IDENTIFIER = "";
    String MINER_KEY = "";
    String MINER_VER = SOFTWARE_VERSION;
    #if defined(ESP8266)
        // "High-band" 8266 diff
        String START_DIFF = "ESP8266H";
    #elif defined(CONFIG_FREERTOS_UNICORE)
        // Single core 32 diff
        String START_DIFF = "ESP32S";
    #else
        // Normal 32 diff
        String START_DIFF = "ESP32";
    #endif

    MiningConfig(String DUCO_USER, String RIG_IDENTIFIER, String MINER_KEY)
            : DUCO_USER(DUCO_USER), RIG_IDENTIFIER(RIG_IDENTIFIER), MINER_KEY(MINER_KEY) {}
};

class MiningJob {

public:
    MiningConfig *config;
    int core = 0;

    MiningJob(int core, MiningConfig *config) {
        this->core = core;
        this->config = config;
        this->client_buffer = "";
        dsha1 = new DSHA1();
        dsha1->warmup();
        generateRigIdentifier();
    }

    void blink(uint8_t count, uint8_t pin = LED_BUILTIN) {
        #if defined(LED_BLINKING)
            uint8_t state = HIGH;

            for (int x = 0; x < (count << 1); ++x) {
                digitalWrite(pin, state ^= HIGH);
                delay(50);
            }
        #else
            digitalWrite(LED_BUILTIN, HIGH);
        #endif
    }

    bool max_micros_elapsed(unsigned long current, unsigned long max_elapsed) {
        static unsigned long _start = 0;

        if ((current - _start) > max_elapsed) {
            _start = current;
            return true;
        }
        return false;
    }

    void mine() {
        connectToNode();
        askForJob();

        dsha1->reset().write((const unsigned char *)getLastBlockHash().c_str(), getLastBlockHash().length());

        int start_time = micros();
        max_micros_elapsed(start_time, 0);
        #if defined(LED_BLINKING)
            digitalWrite(LED_BUILTIN, LOW);
        #endif    
        for (Counter<10> counter; counter < difficulty; ++counter) {
            DSHA1 ctx = *dsha1;
            ctx.write((const unsigned char *)counter.c_str(), counter.strlen()).finalize(hashArray);

            #if CORE == 1
                yield();
            #elif defined(ESP8266)
                ESP.wdtFeed();
            #endif

            if (memcmp(getExpectedHash(), hashArray, 20) == 0) {
                unsigned long elapsed_time = micros() - start_time;
                float elapsed_time_s = elapsed_time * .000001f;
                hashrate = counter / elapsed_time_s;
                share_count++;

                #if defined(LED_BLINKING)
                    digitalWrite(LED_BUILTIN, HIGH);
                #endif    

                submit(counter, hashrate, elapsed_time_s);
                break;
            }
        }
    }

private:
    String client_buffer;
    uint8_t hashArray[20];
    String last_block_hash;
    String expected_hash_str;
    uint8_t expected_hash[20];
    DSHA1 *dsha1;
    WiFiClient client;
    String chipID = "";

    #if defined(ESP8266)
        String MINER_BANNER = "Official ESP8266 Miner";
    #elif defined(CONFIG_FREERTOS_UNICORE)
        String MINER_BANNER = "Official ESP32-S2 Miner";
    #else
        String MINER_BANNER = "Official ESP32 Miner";
    #endif

    uint8_t *hexStringToUint8Array(const String &hexString, uint8_t *uint8Array, const uint32_t arrayLength) {
        assert(hexString.length() >= arrayLength * 2);
        const char *hexChars = hexString.c_str();
        for (uint32_t i = 0; i < arrayLength; ++i) {
            uint8Array[i] = (pgm_read_byte(base36CharValues + hexChars[i * 2] - '0') << 4) + pgm_read_byte(base36CharValues + hexChars[i * 2 + 1] - '0');
        }
        return uint8Array;
    }

    void generateRigIdentifier() {
        String AutoRigName = "";

        #if defined(ESP8266)
            chipID = String(ESP.getChipId(), HEX);

            if (strcmp(config->RIG_IDENTIFIER.c_str(), "Auto") != 0)
                return;

            AutoRigName = "ESP8266-" + chipID;
            AutoRigName.toUpperCase();
            config->RIG_IDENTIFIER = AutoRigName.c_str();
        #else
            uint64_t chip_id = ESP.getEfuseMac();
            uint16_t chip = (uint16_t)(chip_id >> 32); // Prepare to print a 64 bit value into a char array
            char fullChip[23];
            snprintf(fullChip, 23, "%04X%08X", chip,
                    (uint32_t)chip_id); // Store the (actually) 48 bit chip_id into a char array

            chipID = String(fullChip);

            if (strcmp(config->RIG_IDENTIFIER.c_str(), "Auto") != 0)
                return;
            // Autogenerate ID if required
            AutoRigName = "ESP32-" + String(fullChip);
            AutoRigName.toUpperCase();
            config->RIG_IDENTIFIER = AutoRigName.c_str();
        #endif 
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Rig identifier: "
                          + config->RIG_IDENTIFIER);
        #endif
    }

    void connectToNode() {
        if (client.connected()) return;

        unsigned int stopWatch = millis();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Connecting to a Duino-Coin node...");
        #endif
        while (!client.connect(config->host.c_str(), config->port)) {
          if (millis()-stopWatch>100000) ESP.restart();
        }
        
        waitForClientData();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Connected. Node reported version: "
                          + client_buffer);
        #endif

        blink(BLINK_CLIENT_CONNECT); 

    }

    void waitForClientData() {
        client_buffer = "";

        while (client.connected()) {
            if (client.available()) {
                client_buffer = client.readStringUntil(END_TOKEN);
                if (client_buffer.length() == 1 && client_buffer[0] == END_TOKEN)
                    client_buffer = "???\n"; // NOTE: Should never happen
                break;
            }
        }
    }

    void submit(unsigned long counter, float hashrate, float elapsed_time_s) {
        client.print(String(counter) +
                     SEP_TOKEN + String(hashrate) +
                     SEP_TOKEN + MINER_BANNER +
                     SPC_TOKEN + config->MINER_VER +
                     SEP_TOKEN + config->RIG_IDENTIFIER +
                     SEP_TOKEN + "DUCOID" + String(chipID) +
                     SEP_TOKEN + String(WALLET_ID) +
                     END_TOKEN);
                     
        waitForClientData();

        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - " +
                          client_buffer +
                          " share #" + String(share_count) +
                          " (" + String(counter) + ")" +
                          " hashrate: " + String(hashrate / 1000, 2) + " kH/s (" +
                          String(elapsed_time_s) + "s)\n");
        #endif
    }

    bool parse() {
        // Create a non-constant copy of the input string
        char *job_str_copy = strdup(client_buffer.c_str());

        if (job_str_copy) {
            String tokens[3];
            char *token = strtok(job_str_copy, ",");
            for (int i = 0; token != NULL && i < 3; i++) {
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
        else {
            // Handle memory allocation failure
            return false;
        }
    }

    void askForJob() {
        Serial.println("Core [" + String(core) + "] - Asking for a new job for user: " 
                        + String(config->DUCO_USER));

        #if defined(USE_DS18B20)
            sensors.requestTemperatures(); 
            float temp = sensors.getTempCByIndex(0);
            #if defined(SERIAL_PRINTING)
              Serial.println("DS18B20 reading: " + String(temp) + "°C");
            #endif
        
            client.print("JOB," +
                         String(config->DUCO_USER) +
                         SEP_TOKEN + config->START_DIFF + 
                         SEP_TOKEN + String(config->MINER_KEY) + 
                         SEP_TOKEN + "Temp:" + String(temp) + "*C" +
                         END_TOKEN);
        #elif defined(USE_DHT)
            float temp = dht.readTemperature();
            float hum = dht.readHumidity();
            #if defined(SERIAL_PRINTING)
              Serial.println("DHT reading: " + String(temp) + "°C");
              Serial.println("DHT reading: " + String(hum) + "%");
            #endif

            client.print("JOB," +
                         String(config->DUCO_USER) +
                         SEP_TOKEN + config->START_DIFF + 
                         SEP_TOKEN + String(config->MINER_KEY) + 
                         SEP_TOKEN + "Temp:" + String(temp) + "*C" +
                         IOT_TOKEN + "Hum:" + String(hum) + "%" +
                         END_TOKEN);
        #elif defined(USE_INTERNAL_SENSOR)
            float temp = 0;
            temp_sensor_read_celsius(&temp);
            #if defined(SERIAL_PRINTING)
              Serial.println("Internal temp sensor reading: " + String(temp) + "°C");
            #endif

            client.print("JOB," +
                         String(config->DUCO_USER) +
                         SEP_TOKEN + config->START_DIFF + 
                         SEP_TOKEN + String(config->MINER_KEY) + 
                         SEP_TOKEN + "CPU Temp:" + String(temp) + "*C" +
                         END_TOKEN);
        #else
            client.print("JOB," +
                         String(config->DUCO_USER) +
                         SEP_TOKEN + config->START_DIFF + 
                         SEP_TOKEN + String(config->MINER_KEY) + 
                         END_TOKEN);
        #endif

        waitForClientData();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Received job with size of "
                          + String(client_buffer.length()) 
                          + " bytes " + client_buffer);
        #endif

        parse();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Parsed job: " 
                          + getLastBlockHash() + " " 
                          + getExpectedHashStr() + " " 
                          + String(getDifficulty()));
        #endif
    }

    const String &getLastBlockHash() const { return last_block_hash; }
    const String &getExpectedHashStr() const { return expected_hash_str; }
    const uint8_t *getExpectedHash() const { return expected_hash; }
    unsigned int getDifficulty() const { return difficulty; }
};

#endif
