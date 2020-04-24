#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "Hash.h"

const char* ssid     = "SSID"; // Wifi SSID
const char* password = "WIFIPASS"; // Wifi password
const char* ducouser = "USERNAME"; // Duino-Coin username
const char* ducopass = "PASSSWORD"; // Duino-Coin password
String port = "";
int maxshares = 100; //Restart every 100 shares
int var = 0;

const uint8_t fingerprint[20] = {0xCC, 0xAA, 0x48, 0x48, 0x66, 0x46, 0x0E, 0x91, 0x53, 0x2C, 0x9C, 0x7C, 0x23, 0x2A, 0xB1, 0x74, 0x4D, 0x29, 0x9D, 0x33}; // GitHub SHA1 fingerprint to access HTTPS

#define LED_BUILTIN 2 // Uncomment this if your board has built-in led on non-standard pin (NodeMCU - 16 or 2)

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void serverport() {
  std::unique_ptr<BearSSL::WiFiClientSecure>client(new BearSSL::WiFiClientSecure);
  client->setFingerprint(fingerprint);

  HTTPClient https;

  if (https.begin(*client, "https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")) {  // Server IP from GitHub
    int httpCode = https.GET();
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
        port = https.getString();
        port.remove(0, 14); // Remove six characters starting at index=2
        port.remove(6, 600); // Remove six characters starting at index=2
        port.toInt();
        Serial.println(port);
      }
    } else {
      Serial.printf("[HTTPS] GET... failed, error: %s\n", https.errorToString(httpCode).c_str());
    }
    https.end();
  }
}

void loop()
{
  serverport(); // Grab server port function
  const char * host = "0.tcp.ngrok.io"; // ip or dns

  Serial.print("Connecting to ");
  Serial.println(host);

  // Use WiFiClient class to create TCP connections
  WiFiClient client;

  if (!client.connect(host, port.toInt())) {
    Serial.println("Connection failed.");
    Serial.println("Waiting 5 seconds before retrying...");
    delay(5000);
    return;
  }

  // This will send a request to the server
  String line = client.readStringUntil('\n'); // Server sends SERVER_VERSION after connecting
  client.print("LOGI," + String(ducouser) + "," + String(ducopass)); // Ask for login
  line = client.readStringUntil('\n'); // Server sends NO or OK if login successful or failed
  Serial.println("Login feedback: " + line); // Print response in serial monitor

  while (var < maxshares) {
    client.print("JOB2"); // Ask for balance
    String hash = client.readStringUntil(','); // Read hash
    String job = client.readStringUntil(','); // Read job
    unsigned int diff = client.readStringUntil('\n').toInt(); // Read difficulty

    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
      yield(); // Let Arduino/ESP do background tasks - else watchdog will trigger
      String result = sha1(String(hash) + String(iJob)); // Hash previous block hash and current iJob
      if (result == job) { // If result is found
        Serial.println("Share found: " + String(iJob)); // Print the result
        client.print(iJob); // Send result to server
        String accepted = client.readStringUntil('\n'); // Receive feedback
        Serial.println("Share feedback: " + accepted);
        digitalWrite(LED_BUILTIN, HIGH);   // Turn on built-in led
        delay(50); // Wait a bit
        digitalWrite(LED_BUILTIN, LOW); // Turn off built-in led
        var++;
        break; // Stop and wait for more work
      }
    }
  }
}
