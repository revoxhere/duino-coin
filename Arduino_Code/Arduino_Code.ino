//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Arduino Code remastered - v1.6 © revox 2019-2020
//  Big thanks to daknuett for help in library migration!
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://revoxhere.github.io/duino-coin/ - Website
//  https://discord.gg/874adGU - Discord
//  https://github.com/daknuett - @daknuett
//////////////////////////////////////////////////////////
//  If you don't know what to do, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

// Include crypto library
#define SHA256_DISABLE_WRAPPER // Disable sha256 wrapper
#include "sha1.h"

String result; // Create globals
char buffer[64];
unsigned int iJob = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Prepare built-in led pin as output
  Serial.begin(115200); // Open serial port
  Serial.println("ready"); // Send feedback to miner
}

void loop() {
  String startStr = Serial.readStringUntil('\n');
  if (startStr == "start") { // Wait for start word, serial.available caused problems
    String hash = Serial.readStringUntil('\n'); // Read hash
    String job = Serial.readStringUntil('\n'); // Read job
    unsigned int diff = Serial.parseInt(); // Read difficulty
    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
      yield(); // Let Arduino/ESP do background tasks - else watchdog will trigger
      Sha1.init(); // Create sha1 hasher
      Sha1.print(String(hash) + String(iJob));
      uint8_t * hash_bytes = Sha1.result(); // Get result
      for (int i = 0; i < 10; i++) { // Cast result to array
        for (int i = 0; i < 32; i++) {
          buffer[2 * i] = "0123456789abcdef"[hash_bytes[i] >> 4];
          buffer[2 * i + 1] = "0123456789abcdef"[hash_bytes[i] & 0xf];
        }
      }
      result = String(buffer); // Convert and prepare array
      result.remove(40, 28); // First 40 characters are good, rest is garbage
      if (String(result) == String(job)) { // If result is found
        Serial.println(String(iJob)); // Send result back to Arduino Miner
        PORTB = PORTB | B00100000;   // Turn on built-in led
        delay(40); // Wait a bit
        PORTB = PORTB & B11011111; // Turn off built-in led
        break; // Stop and wait for more work
      }
    }
  }
}
