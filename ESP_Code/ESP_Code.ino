//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for WiFi ESP boards - v1.6 © revox 2019-2020
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://revoxhere.github.io/duino-coin/ - Website
//  https://discord.gg/kvBkccy - Discord
//////////////////////////////////////////////////////////
//  If you don't know how to start, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////
const char* ssid     = "WiFi Name"; // Change this to your WiFi SSID
const char* password = "WiFi Password"; // Change this to your WiFi password
const char* ducouser = "Duino-Coin Username"; // Change this to your Duino-Coin username

#define LED_BUILTIN 2 // Uncomment this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)t

#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266HTTPClient.h> // Include HTTP library
#include <Hash.h> // Include crypto library

String port = ""; // Global variable

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Define built-in led as output
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP Miner v1.6");

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

void serverport() { // Grab server port from GitHub file function
  std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
  client->setInsecure();
  HTTPClient https;

  if (https.begin(*client, "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")) {  // Server IP file
    int httpCode = https.GET(); // Get HTTP code
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
        port = https.getString(); // Get data
        port.remove(0, 14); // Remove unwanted characters
        port.remove(6, 600); // Remove unwanted characters
        port.toInt(); // Convert to int
        Serial.println("\nGitHub port: " + String(port));
      }
    } else { // If error
      Serial.printf("[HTTPS] GET... failed, error: %s\n", https.errorToString(httpCode).c_str());
    } // Free the resources
    https.end();
  }
}

void loop()
{
  serverport(); // Grab server port
  const char * host = "0.tcp.ngrok.io"; // Server IP

  Serial.println("\nConnecting to Duino-Coin server...");

  // Use WiFiClient class to create TCP connection
  WiFiClient client;
  if (!client.connect(host, port.toInt())) {
    Serial.println("Connection failed.");
    Serial.println("Waiting 15 seconds before retrying...");
    delay(15000);
    return;
  }

  String SERVER_VER = client.readString(); // Server sends SERVER_VERSION after connecting
  Serial.print("\nServer version: " + String(SERVER_VER));
  client.print("FROM,ESP Miner," + String(ducouser)); // Metrics for the server

  while (1) {
    Serial.println("Asking for a new job for user: " + String(ducouser));
    client.print("Job," + String(ducouser)); // Ask for new job

    String hash = client.readStringUntil(','); // Read hash
    String job = client.readStringUntil(','); // Read job
    unsigned int diff =  3500; // Fixed difficulty - no need to read it from the server because no termination character causes a lot of network lag
    Serial.println("Job received: " + String(hash) + " " + String(job));

    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
      yield(); // Let ESP do background tasks - else watchdog will trigger
      String result = sha1(String(hash) + String(iJob)); // Hash previous block hash and current iJob
      if (result == job) { // If result is found
        Serial.println("Share found: " + String(iJob));
        client.print(iJob); // Send result to server

        String feedback = client.readStringUntil('D'); // Receive feedback
        digitalWrite(LED_BUILTIN, HIGH);   // Turn on built-in led
        delay(50); // Wait a bit
        digitalWrite(LED_BUILTIN, LOW); // Turn off built-in led
        delay(50); // Wait a bit

        Serial.println("-----");
        break; // Stop and wait for more work
      }
    }
  }
}
