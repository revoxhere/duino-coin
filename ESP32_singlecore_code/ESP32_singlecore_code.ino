//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for ESP32 boards v2.1
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

#include "hwcrypto/sha.h" // Include hardware accelerated libraries for hashing
#include <WiFi.h>

#define LED_BUILTIN 2 // Change this if your board has built-in led on non-standard pin

// TIP for revox: MAKE SURE THERE ISN'T ANY OF YOUR PASSWORDS BEFORE COMMIT
const char* ssid     = "Your WiFi SSID"; // Change this to your WiFi SSID
const char* password = "Your WiFi password"; // Change this to your WiFi password
const char* ducouser = "Your Duino-Coin username"; // Change this to your Duino-Coin username
// TIP for revox: MAKE SURE THERE ISN'T ANY OF YOUR PASSWORDS BEFORE COMMIT

void setup() {
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP32 Miner v2.1");
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

void loop() {
  const char * host = "51.15.127.80"; // Static server IP
  const int port = 2811;
  unsigned int Shares = 0; // Share variable

  Serial.println("\nConnecting to Duino-Coin server...");
  // Use WiFiClient class to create TCP connection
  WiFiClient client;
  Serial.println(client.connect(host, port));

  String SERVER_VER = client.readString(); // Server sends SERVER_VERSION after connecting
  Serial.println("Connected to the server. Server version: " + String(SERVER_VER));
  blink(3); // Blink 3 times - indicate sucessfull connection with the server

  while (client.connected()) {
    Serial.println("Asking for a new job for user: " + String(ducouser));
    client.print("JOB," + String(ducouser) + ",ESP32"); // Ask for new job

    String hash = client.readStringUntil(','); // Read last block hash
    String job = client.readStringUntil(','); // Read expected hash
    job.toUpperCase();
    const char * c = job.c_str();
    unsigned char* job1 = hexstr_to_char(c);
    byte shaResult[20];
    unsigned long diff =  10001; // Low power devices use the low diff job, we don't read it as no termination character causes unnecessary network lag
    Serial.println("Job received: " + String(hash) + " " + String(job) + " " + String(diff));
    unsigned long StartTime = micros(); // Start time measurement

    for (unsigned long iJob = 0; iJob < diff; iJob++) { // Difficulty loop
      yield(); // uncomment if ESP watchdog triggers
      String hash1 = String(hash) + String(iJob);
      const unsigned char* payload = (const unsigned char*) hash1.c_str();
      unsigned int payloadLenght = hash1.length();

      esp_sha(SHA1, payload, payloadLenght, shaResult);
      
      int compareresult = memcmp(shaResult, job1, sizeof(shaResult));
      
      if (compareresult == 0) { // If result is found
        unsigned long EndTime = micros(); // End time measurement
        unsigned long ElapsedTime = EndTime - StartTime; // Calculate elapsed time
        float ElapsedTimeMiliSeconds = ElapsedTime / 1000; // Convert to miliseconds
        float ElapsedTimeSeconds = ElapsedTimeMiliSeconds / 1000; // Convert to seconds
        float HashRate = iJob / ElapsedTimeSeconds; // Calculate hashrate
        client.print(String(iJob) + "," + String(HashRate) + ",ESP32 Miner v2.1"); // Send result to server
        String feedback = client.readStringUntil('D'); // Receive feedback
        Shares++;
        Serial.println(String(feedback) + "D share #" + String(Shares) + " (" + String(iJob) + ")" + " Hashrate: " + String(HashRate) + " Free RAM: " + String(ESP.getFreeHeap()));
        break; // Stop and ask for more work
      }
    }  
  }

  Serial.println("Not connected. Restarting ESP");
  esp_restart(); // Restart the board
}

unsigned char* hexstr_to_char(const char* hexstr) {
    size_t len = strlen(hexstr);
    if (len % 2 != 0)
        return NULL;
    size_t final_len = len / 2;
    unsigned char* chrs = (unsigned char*)malloc((final_len + 1) * sizeof(unsigned char));
    for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
        chrs[j] = (hexstr[i] % 32 + 9) % 25 * 16 + (hexstr[i + 1] % 32 + 9) % 25;
    return chrs;
}

void blink(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_BUILTIN, HIGH);   // Turn off built-in led
    delay(3);
    digitalWrite(LED_BUILTIN, LOW);   // Turn on built-in led
  }
}
