//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for WiFi ESP boards - v1.0 © revox 2019-2020
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
const char* password = "WiFi Pass"; // Change this to your WiFi password
const char* ducouser = "Username"; // Change this to your Duino-Coin username
const char* ducopass = "Password"; // Change this to your Duino-Coin password

#define LED_BUILTIN 2 // Uncomment this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)
int maxshares = 100; // Restart every 100 shares, you can change it if you want

#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266HTTPClient.h> // Include HTTP library
#include "Hash.h" // Include crypto library

const uint8_t fingerprint[20] = {0x70, 0x94, 0xDE, 0xDD, 0xE6, 0xC4, 0x69, 0x48, 0x3A, 0x92, 0x70, 0xA1, 0x48, 0x56, 0x78, 0x2D, 0x18, 0x64, 0xE0, 0xB7}; // GitHub SHA1 fingerprint to access HTTPS

int var = 0; // Global variable
String port = ""; // Global variable

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Define built-in led as output
  Serial.begin(115200); // Start serial connection
  Serial.println("\n\nDuino-Coin ESP Miner v1.0 by revox");

  Serial.print("Connecting to: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA); // Setup ESP in client mode
  WiFi.begin(ssid, password); // Connect to wifi

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi!");
  Serial.print("Local IP address: ");
  Serial.println(WiFi.localIP()); // Print local IP address
}

void serverport() { // Grab server port from GitHub file function
  std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure); // Prepare HTTPS
  client->setFingerprint(fingerprint); // Prepare fingerprint
  HTTPClient https;

  if (https.begin(*client, "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")) {  // Server IP file
    int httpCode = https.GET(); // Get HTTP code
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
        port = https.getString(); // Get data
        port.remove(0, 14); // Remove unwanted characters
        port.remove(6, 600); // Remove unwanted characters
        port.toInt(); // Convert to int
        Serial.print("\nGitHub port: ");
        Serial.println(port);
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
    Serial.println("Waiting 5 seconds before retrying...");
    delay(5000);
    return;
  }

  String SERVER_VER = client.readStringUntil('\n'); // Server sends SERVER_VERSION after connecting
  Serial.print("\nServer is on version: ");
  Serial.println(SERVER_VER);
  delay(150); // Small delays are used to make connection with the server more stable, without them ESP likes to timeout

  Serial.print("Loging-in user: ");
  Serial.println(ducouser);
  client.print("LOGI," + String(ducouser) + "," + String(ducopass)); // Ask for login
  delay(150); // Small delays are used to make connection with the server more stable, without them ESP likes to timeout

  String feedback = client.readStringUntil('\n'); // Server sends NO or OK if login successful or failed
  Serial.print("Login feedback: ");
  Serial.println(feedback); // Print the feedback
  Serial.print("\n");

  while (var < maxshares) { // While remaining shares is less than max shares
    Serial.println("Asking for a new job");
    client.print("Job"); // Ask for new job
    delay(150); // Small delays are used to make connection with the server more stable, without them ESP likes to timeout
    
    String hash = client.readStringUntil(','); // Read hash
    String job = client.readStringUntil(','); // Read job
    unsigned int diff = client.readStringUntil('\n').toInt(); // Read difficulty

    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
      yield(); // Let Arduino/ESP do background tasks - else watchdog will trigger
      String result = sha1(String(hash) + String(iJob)); // Hash previous block hash and current iJob
      if (result == job) { // If result is found
        Serial.print("Share found: ");
        Serial.println(iJob); // Print the result
        client.print(iJob); // Send result to server
        delay(150); // Small delays are used to make connection with the server more stable, without them ESP likes to timeout

        String accepted = client.readStringUntil('\n'); // Receive feedback
        Serial.print("Share feedback: ");
        Serial.println(accepted);

        digitalWrite(LED_BUILTIN, HIGH);   // Turn on built-in led
        delay(100); // Wait a bit
        digitalWrite(LED_BUILTIN, LOW); // Turn off built-in led
        delay(100); // Wait a bit
        digitalWrite(LED_BUILTIN, HIGH); // Turn off built-in led
        delay(100); // Wait a bit
        digitalWrite(LED_BUILTIN, LOW); // Turn off built-in led
        
        Serial.println("-----");
        var++; // Increase share counter
        break; // Stop and wait for more work
      }
    }
  }
}
