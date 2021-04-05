//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for Arduino boards v2.4
//  © Duino-Coin Community 2019-2021
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://duinocoin.com - Official Website
//  https://discord.gg/k48Ht5y - Discord
//////////////////////////////////////////////////////////
//  If you don't know what to do, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

// Include SHA1 library
// Authors: https://github.com/daknuett, https://github.com/JoyBed, https://github.com/revox
#include "sha1.h"
#include <Arduino.h>
#include "printf.h"
// Create globals
char buffer[44];
String lastblockhash = "";
String newblockhash = "";
unsigned int difficulty = 0;
unsigned int ducos1result = 0;

// Setup stuff
void setup() {
  // Open serial port
  Serial.begin(115200);
  Serial.setTimeout(5000);
}

// DUCO-S1A hasher
int ducos1a(String lastblockhash, String newblockhash, int difficulty) {
  // DUCO-S1 algorithm implementation for AVR boards (DUCO-S1A)
  // Difficulty loop
  int ducos1res = 0;
  for (int ducos1res = 0; ducos1res < difficulty * 100 + 1; ducos1res++) {
    Sha1.init();
    Sha1.print(lastblockhash + ducos1res);
    // Get SHA1 result
    uint8_t * hash_bytes = Sha1.result();
    // Cast result to array
    for (int i = 0; i < 10; i++) {
      for (int i = 0; i < 20; i++) {
        // MSB to LSB (Depending on the address in hash_bytes)
        buffer[2 * i] = "0123456789abcdef"[hash_bytes[i] >> 4];
        // Choose that from the given array of characters
        // and retreve the value from address next spot over
        buffer[2 * i + 1] = "0123456789abcdef"[hash_bytes[i] & 0xf];
      }
    }
    if (String(buffer) == String(newblockhash)) {
      // If expected hash is equal to the found hash, return the result
      return ducos1res;
    }
  }
}

// Infinite loop
void loop() {
  // Wait for serial data
  while (Serial.available() > 0) {
    // Read last block hash
    lastblockhash = Serial.readStringUntil(',');
    // Read expected hash
    newblockhash = Serial.readStringUntil(',');
    // Read difficulty
    difficulty = Serial.readStringUntil(',').toInt();
    // Start time measurement
    unsigned long startTime = micros();
    // Call DUCO-S1A hasher
    ducos1result = ducos1a(lastblockhash, newblockhash, difficulty);
    // End time measurement
    unsigned long endTime = micros();
    // Calculate elapsed time
    unsigned long elapsedTime = endTime - startTime;
    // Send result back to the program with share time
    Serial.print(String(ducos1result) + "," + String(elapsedTime) + "\n");
    // Wait a bit
    delay(25);
  }
}
