//////////////////////////////////////////////////////////
//  _____        _                    _____      _       
// |  __ \      (_)                  / ____|    (_)      
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __  
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_| 
//  Arduino Code remastered - v1.4 © revox 2019-2020
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://revoxhere.github.io/duino-coin/ - Website
//  https://discord.gg/KyADZT3 - Discord
//////////////////////////////////////////////////////////
//  If you don't know how to start, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

// Include SHA library
#include "Hash.h"

void setup() {
  Serial.begin(115200); // Open serial port
}

void loop() {
  if (Serial.available() > 0) { // Wait for serial to become available
    String hash = Serial.readStringUntil('\n'); // Read hash
    String job = Serial.readStringUntil('\n'); // Read job
    unsigned int diff = Serial.readStringUntil('\n').toInt(); // Read difficulty

    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
      yield(); // Let Arduino/ESP do background tasks - anti-watchdog
      String result = sha1(String(hash) + String(iJob)); // Hash previous block hash and current iJob
      if (result == job) { // If result is found
        Serial.println(iJob); // Send result back to Arduino Miner
        break; // Stop and wait for more work
      }
    }
  }
}
