//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for Arduino boards v1.7 
//  © Duino-Coin Community 2019-2020
//
//  Big thanks to JoyBed for optimizations!
//  Thanks to daknuett for help in library migration!
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://duinocoin.com - Official Website
//  https://discord.gg/k48Ht5y - Discord
//  https://github.com/revoxhere - @revox
//  https://github.com/daknuett - @daknuett
//  https://github.com/JoyBed - @JoyBed
//////////////////////////////////////////////////////////
//  If you don't know what to do, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

// Include SHA1 part of cryptosuite2 library
#include "sha1.h"
String result; // Create globals
char buffer[64] = "";
unsigned int iJob = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Prepare built-in led pin as output
  Serial.begin(115200); // Open serial port
  Serial.println("ready"); // Send start word to miner program
  Serial.flush();
}

void loop() {
  String startStr = Serial.readStringUntil('\n');
  if (startStr == "start") { // Wait for start word, serial.available caused problems
    Serial.flush();
    String hash = Serial.readStringUntil('\n'); // Read hash
    String job = Serial.readStringUntil('\n'); // Read job
    unsigned int diff = Serial.parseInt(); // Read difficulty
    unsigned long StartTime = micros();
    for (unsigned int iJob = 0; iJob < diff * 100 + 1; iJob++) { // Difficulty loop
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
        unsigned long EndTime = micros();
        unsigned long ElapsedTime = EndTime - StartTime;
        Serial.println(String(iJob) + "," + String(ElapsedTime)); // Send result back to the program with share time
        PORTB = PORTB | B00100000;   // Turn on built-in led
        delay(75); // Wait a bit
        PORTB = PORTB & B11011111; // Turn off built-in led
        break; // Stop and wait for more work
      }
    }
  }
}
