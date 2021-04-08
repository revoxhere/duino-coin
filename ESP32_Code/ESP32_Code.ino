//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP32 boards v2.3
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
const char* rigname  = "ESP32";                     // Change this if you want to display a custom rig name in the Wallet
#define LED_BUILTIN     2                           // Change this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)

#include "mbedtls/md.h" // Include software hashing library
#include "hwcrypto/sha.h" // Include hardware accelerated hashing library
#include <WiFi.h>

TaskHandle_t Task1;
TaskHandle_t Task2;

const char * host = "51.15.127.80"; // Static server IP
const int port = 2811;

// Task1code
void Task1code( void * pvParameters ) {
  unsigned int Shares1 = 0; // Share variable

  Serial.println("\nCORE1 Connecting to Duino-Coin server...");
  // Use WiFiClient class to create TCP connection
  WiFiClient client1;
  client1.setTimeout(2);
  Serial.println("CORE1 is connected: " + String(client1.connect(host, port)));

  String SERVER_VER = client1.readString(); // Server sends SERVER_VERSION after connecting
  digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
  Serial.println("CORE1 Connected to the server. Server version: " + String(SERVER_VER));
  digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led

  while (client1.connected()) {
    Serial.println("CORE1 Asking for a new job for user: " + String(ducouser));
    client1.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job

    String       hash1 = client1.readStringUntil(','); // Read data to the first peroid - last block hash
    String        job1 = client1.readStringUntil(','); // Read data to the next peroid - expected hash
    unsigned int diff1 = client1.readStringUntil('\n').toInt() * 100 + 1; // Read and calculate remaining data - difficulty
    job1.toUpperCase();
    const char * c = job1.c_str();

    size_t len = strlen(c);
    size_t final_len = len / 2;
    unsigned char* job11 = (unsigned char*)malloc((final_len + 1) * sizeof(unsigned char));
    for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
      job11[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;

    byte shaResult1[20];

    Serial.println("CORE1 Job received: " + String(hash1) + " " + String(job1) + " " + String(diff1));
    unsigned long StartTime1 = micros(); // Start time measurement

    for (unsigned long iJob1 = 0; iJob1 < diff1; iJob1++) { // Difficulty loop
      yield(); // uncomment if ESP watchdog triggers
      String hash11 = String(hash1) + String(iJob1);
      const unsigned char* payload1 = (const unsigned char*) hash11.c_str();
      unsigned int payloadLenght1 = hash11.length();

      esp_sha(SHA1, payload1, payloadLenght1, shaResult1);

      if (memcmp(shaResult1, job11, sizeof(shaResult1)) == 0) { // If result is found
        unsigned long EndTime1 = micros(); // End time measurement
        unsigned long ElapsedTime1 = EndTime1 - StartTime1; // Calculate elapsed time
        float ElapsedTimeMiliSeconds1 = ElapsedTime1 / 1000; // Convert to miliseconds
        float ElapsedTimeSeconds1 = ElapsedTimeMiliSeconds1 / 1000; // Convert to seconds
        float HashRate1 = iJob1 / ElapsedTimeSeconds1; // Calculate hashrate
        client1.print(String(iJob1) + "," + String(HashRate1) + ",ESP32 CORE1 Miner v2.3," + String(rigname)); // Send result to server
        String feedback1 = client1.readStringUntil('\n'); // Receive feedback
        Shares1++;
        Serial.println("CORE1 " + String(feedback1) + " share #" + String(Shares1) + " (" + String(iJob1) + ")" + " Hashrate: " + String(HashRate1));
        if (HashRate1 < 4000) {
          Serial.println("CORE1 Low hashrate. Restarting");
          client1.stop();
          esp_restart();
        }
        break; // Stop and ask for more work
      }
    }
  }
  Serial.println("CORE1 Not connected. Restarting core 1");
  client1.stop();
  xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 1, &Task1, 0);
  vTaskDelete( NULL );
}

//Task2code
void Task2code( void * pvParameters ) {
  unsigned int Shares = 0; // Share variable

  Serial.println("\nCORE2 Connecting to Duino-Coin server...");
  // Use WiFiClient class to create TCP connection
  WiFiClient client;
  client.setTimeout(2);
  Serial.println("CORE2 is connected: " + String(client.connect(host, port)));

  String SERVER_VER = client.readString(); // Server sends SERVER_VERSION after connecting
  digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
  Serial.println("CORE2 Connected to the server. Server version: " + String(SERVER_VER));
  digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led

  while (client.connected()) {
    Serial.println("CORE2 Asking for a new job for user: " + String(ducouser));
    client.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job

    String       hash = client.readStringUntil(','); // Read data to the first peroid - last block hash
    String        job = client.readStringUntil(','); // Read data to the next peroid - expected hash
    unsigned int diff = client.readStringUntil('\n').toInt() * 100 + 1; // Read and calculate remaining data - difficulty
    job.toUpperCase();
    const char * c = job.c_str();

    size_t len = strlen(c);
    size_t final_len = len / 2;
    unsigned char* job1 = (unsigned char*)malloc((final_len + 1) * sizeof(unsigned char));
    for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
      job1[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;

    byte shaResult[20];

    Serial.println("CORE2 Job received: " + String(hash) + " " + String(job) + " " + String(diff));
    unsigned long StartTime = micros(); // Start time measurement

    for (unsigned long iJob = 0; iJob < diff; iJob++) { // Difficulty loop
      yield(); // uncomment if ESP watchdog triggers
      String hash1 = String(hash) + String(iJob);
      const unsigned char* payload = (const unsigned char*) hash1.c_str();
      unsigned int payloadLength = hash1.length();

      mbedtls_md_context_t ctx;
      mbedtls_md_type_t md_type = MBEDTLS_MD_SHA1;
      mbedtls_md_init(&ctx);
      mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 0);
      mbedtls_md_starts(&ctx);
      mbedtls_md_update(&ctx, (const unsigned char *) payload, payloadLength);
      mbedtls_md_finish(&ctx, shaResult);
      mbedtls_md_free(&ctx);

      if (memcmp(shaResult, job1, sizeof(shaResult)) == 0) { // If result is found
        unsigned long EndTime = micros(); // End time measurement
        unsigned long ElapsedTime = EndTime - StartTime; // Calculate elapsed time
        float ElapsedTimeMiliSeconds = ElapsedTime / 1000; // Convert to miliseconds
        float ElapsedTimeSeconds = ElapsedTimeMiliSeconds / 1000; // Convert to seconds
        float HashRate = iJob / ElapsedTimeSeconds; // Calculate hashrate
        client.print(String(iJob) + "," + String(HashRate) + ",ESP32 CORE2 Miner v2.3," + String(rigname)); // Send result to server
        String feedback = client.readStringUntil('\n'); // Receive feedback
        Shares++;
        Serial.println("CORE2 " + String(feedback) + " share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate));
        if (HashRate < 4000) {
          Serial.println("CORE2 Low hashrate. Restarting");
          client.stop();
          esp_restart();
        }
        break; // Stop and ask for more work
      }
    }
  }
  Serial.println("CORE2 Not connected. Restarting core 2");
  client.stop();
  xTaskCreatePinnedToCore(Task2code, "Task2", 10000, NULL, 2, &Task2, 1);
  vTaskDelete( NULL );
}

void setup() {
  disableCore0WDT();
  disableCore1WDT();
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP32 Miner v2.3");
  Serial.println("Connecting to: " + String(ssid));
  WiFi.mode(WIFI_STA); // Setup ESP in client mode
  WiFi.begin(ssid, password); // Connect to wifi

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.println("Local IP address: " + WiFi.localIP().toString());
  xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 1, &Task1, 0); //create a task with priority 1 and executed on core 0
  delay(250);
  xTaskCreatePinnedToCore(Task2code, "Task2", 10000, NULL, 2, &Task2, 1); //create a task with priority 2 and executed on core 1
  delay(250);
}

void loop() {}
