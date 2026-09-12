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

// Classic dual-core ESP32 can use the on-chip SHA-1 accelerator.
// Other ESP variants and ESP8266 keep the existing software path unchanged.
#if defined(CONFIG_IDF_TARGET_ESP32) && !defined(CONFIG_FREERTOS_UNICORE) && \
    !defined(DISABLE_ESP32_HARDWARE_SHA1)
    #if defined(__has_include)
        #if __has_include(<sha/sha_parallel_engine.h>)
            #include <esp_timer.h>
            #include "HardwareSHA1.h"
            #define DUCO_USE_ESP32_HARDWARE_SHA1 1
        #else
            #define DUCO_USE_ESP32_HARDWARE_SHA1 0
        #endif
    #else
        #define DUCO_USE_ESP32_HARDWARE_SHA1 0
    #endif
#else
    #define DUCO_USE_ESP32_HARDWARE_SHA1 0
#endif

#ifndef DUCO_ESP32_HW_SHA1_TARGET_HPS
    // Public daily-use target per existing ESP32 worker. Two workers target ~220 kH/s total.
    #define DUCO_ESP32_HW_SHA1_TARGET_HPS 110000UL
#endif

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
        #if DUCO_USE_ESP32_HARDWARE_SHA1
            hardware_sha1_ready = HardwareSHA1::selfTest();
            #if defined(SERIAL_PRINTING)
              Serial.println("Core [" + String(core) + "] - Hardware SHA-1: "
                              + String(hardware_sha1_ready ? "PASS" : "FAIL - software fallback"));
            #endif
        #endif
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

    void handleSystemEvents(void) {
        #if defined(ESP32) && CORE == 2
          esp_task_wdt_reset();
        #endif
        delay(10); // Required vTaskDelay by ESP-IDF
        yield();
        ArduinoOTA.handle();
    }

    void mine() {
        connectToNode();
        askForJob();

        #if DUCO_USE_ESP32_HARDWARE_SHA1
            if (hardware_sha1_ready) {
                mineHardwareSHA1();
                return;
            }
        #endif
          
        dsha1->reset().write((const unsigned char *)getLastBlockHash().c_str(), getLastBlockHash().length());

        int start_time = micros();
        max_micros_elapsed(start_time, 0);
        #if defined(LED_BLINKING)
            #if defined(BLUSHYBOX)
              for (int i = 0; i < 72; i++) {
                analogWrite(LED_BUILTIN, i);
                delay(1);
              }
            #else
              digitalWrite(LED_BUILTIN, LOW);
            #endif
        #endif
        for (Counter<10> counter; counter < job_difficulty; ++counter) {
            DSHA1 ctx = *dsha1;
            ctx.write((const unsigned char *)counter.c_str(), counter.strlen()).finalize(hashArray);
            
            #ifndef CONFIG_FREERTOS_UNICORE
                #if defined(ESP32)
                    #define SYSTEM_TIMEOUT 100000 // 10ms for esp32 looks like the lowest value without false watchdog triggers
                #else 
                    #define SYSTEM_TIMEOUT 500000 // 50ms for 8266 for same reason as above
                #endif
                if (max_micros_elapsed(micros(), SYSTEM_TIMEOUT)) {
                    handleSystemEvents();
                } 
            #endif

            if (memcmp(getExpectedHash(), hashArray, 20) == 0) {
                unsigned long elapsed_time = micros() - start_time;
                float elapsed_time_s = elapsed_time * .000001f;
                share_count++;

                #if defined(LED_BLINKING)
                    #if defined(BLUSHYBOX)
                        for (int i = 72; i > 0; i--) {
                          analogWrite(LED_BUILTIN, i);
                          delay(1);
                        }
                    #else
                        digitalWrite(LED_BUILTIN, HIGH);
                    #endif
                #endif

                if (String(core) == "0") {
                    hashrate = counter / elapsed_time_s;
                    submit(counter, hashrate, elapsed_time_s);
                } else {
                    hashrate_core_two = counter / elapsed_time_s;
                    submit(counter, hashrate_core_two, elapsed_time_s);
                }

                #if defined(BLUSHYBOX)
                    gauge_set(hashrate + hashrate_core_two);
                #endif
                
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
    uint32_t job_difficulty = 0;

    #if DUCO_USE_ESP32_HARDWARE_SHA1
        bool hardware_sha1_ready = false;
    #endif

    #if defined(ESP8266)
        #if defined(BLUSHYBOX)
          String MINER_BANNER = "Official BlushyBox Miner (ESP8266)";
        #else
          String MINER_BANNER = "Official ESP8266 Miner";
        #endif
    #elif defined(CONFIG_FREERTOS_UNICORE)
        String MINER_BANNER = "Official ESP32-S2 Miner";
    #else
        #if defined(BLUSHYBOX)
          String MINER_BANNER = "Official BlushyBox Miner (ESP32)";
        #else
          String MINER_BANNER = "Official ESP32 Miner";
        #endif
    #endif

    #if DUCO_USE_ESP32_HARDWARE_SHA1
    void mineHardwareSHA1() {
        uint32_t prefix[10];
        uint32_t expected_words[5];
        HardwareSHA1::preparePrefix40(last_block_hash.c_str(), prefix);
        HardwareSHA1::expectedWords(expected_hash, expected_words);

        uint32_t found_nonce = 0;
        uint32_t attempts = 0;
        bool hit = false;
        const uint32_t job_limit = job_difficulty;
        const uint64_t start_us = esp_timer_get_time();

        #if defined(LED_BLINKING)
            #if defined(BLUSHYBOX)
              for (int i = 0; i < 72; i++) {
                analogWrite(LED_BUILTIN, i);
                delay(1);
              }
            #else
              digitalWrite(LED_BUILTIN, LOW);
            #endif
        #endif

        // The original ESP32 has one SHA accelerator shared by both CPU cores.
        // Serialize only the raw search; release it before rate pacing/network I/O
        // so the second official mining worker can use the engine immediately.
        HardwareSHA1::lock();
        for (Counter<10> counter; counter < job_limit; ++counter) {
            ++attempts;
            if (HardwareSHA1::hash40Locked(
                    prefix, counter.c_str(), counter.strlen(), expected_words)) {
                found_nonce = counter;
                hit = true;
                break;
            }
        }
        HardwareSHA1::unlock();

        if (!hit) return;

        // Pace each existing ESP32 worker to the public daily-use target. Waiting
        // time is included in reported hashrate, so the submitted figure reflects
        // actual worker throughput rather than the accelerator's short burst rate.
        const uint64_t target_us =
            (uint64_t(attempts) * 1000000ULL + DUCO_ESP32_HW_SHA1_TARGET_HPS - 1ULL)
            / DUCO_ESP32_HW_SHA1_TARGET_HPS;

        while ((uint64_t)(esp_timer_get_time() - start_us) < target_us) {
            const uint64_t elapsed_us = (uint64_t)(esp_timer_get_time() - start_us);
            const uint64_t remain_us = target_us - elapsed_us;

            if (remain_us >= 20000ULL) {
                delay(10);
                yield();
                ArduinoOTA.handle();
            } else if (remain_us >= 2000ULL) {
                delay(1);
            } else {
                delayMicroseconds(50);
            }
        }

        const uint64_t elapsed_us = (uint64_t)(esp_timer_get_time() - start_us);
        const float elapsed_time_s = elapsed_us * .000001f;
        const float hardware_hashrate = elapsed_time_s > 0.0f
            ? attempts / elapsed_time_s
            : 0.0f;

        share_count++;

        #if defined(LED_BLINKING)
            #if defined(BLUSHYBOX)
                for (int i = 72; i > 0; i--) {
                  analogWrite(LED_BUILTIN, i);
                  delay(1);
                }
            #else
                digitalWrite(LED_BUILTIN, HIGH);
            #endif
        #endif

        if (core == 0) {
            hashrate = hardware_hashrate;
            submit(found_nonce, hashrate, elapsed_time_s);
        } else {
            hashrate_core_two = hardware_hashrate;
            submit(found_nonce, hashrate_core_two, elapsed_time_s);
        }

        #if defined(BLUSHYBOX)
            gauge_set(hashrate + hashrate_core_two);
        #endif
    }
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
            if (max_micros_elapsed(micros(), 100000)) {
                handleSystemEvents();
            } 
            if (millis()-stopWatch>100000) ESP.restart();
        }
        
        waitForClientData();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - Connected. Node reported version: "
                          + client_buffer);
        #endif

        blink(BLINK_CLIENT_CONNECT); 

        /* client.print("MOTD" + END_TOKEN);
        waitForClientData();
        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - MOTD: "
                          + client_buffer);
        #endif */
    }

    void waitForClientData() {
        client_buffer = "";
        unsigned int stopWatch = millis();
        while (client.connected()) {
            if (client.available()) {
                client_buffer = client.readStringUntil(END_TOKEN);
                if (client_buffer.length() == 1 && client_buffer[0] == END_TOKEN)
                    client_buffer = "???\n"; // NOTE: Should never happen
                break;
            }
            if (max_micros_elapsed(micros(), 100000)) {
                handleSystemEvents();
            }
            if (millis()-stopWatch>120000) {
              Serial.println("Timeout after 120s. Forced restart..");
              ESP.restart();
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

        unsigned long ping_start = millis();
        waitForClientData();
        ping = millis() - ping_start;

        if (client_buffer == "GOOD") {
          accepted_share_count++;
        }

        #if defined(SERIAL_PRINTING)
          Serial.println("Core [" + String(core) + "] - " +
                          client_buffer +
                          " share #" + String(share_count) +
                          " (" + String(counter) + ")" +
                          " hashrate: " + String(hashrate / 1000, 2) + " kH/s (" +
                          String(elapsed_time_s) + "s) " + 
                          "Ping: " + String(ping) + "ms " +
                          "(" + node_id + ")\n");
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
            job_difficulty = tokens[2].toInt() * 100 + 1;
            // Keep the legacy global updated for dashboard/telemetry compatibility,
            // but mining itself uses this MiningJob's own difficulty value.
            difficulty = job_difficulty;

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
        #elif defined(USE_HSU07M)
            float temp = read_hsu07m();
            #if defined(SERIAL_PRINTING)
              Serial.println("HSU reading: " + String(temp) + "°C");
            #endif

            client.print("JOB," +
                         String(config->DUCO_USER) +
                         SEP_TOKEN + config->START_DIFF + 
                         SEP_TOKEN + String(config->MINER_KEY) + 
                         SEP_TOKEN + "Temp:" + String(temp) + "*C" +
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
    unsigned int getDifficulty() const { return job_difficulty; }
};

#endif
