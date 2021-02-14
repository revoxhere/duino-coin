//////////////////////////////////////////////////////////
//  ____        _                    ____      _       
// |  _ \ _   _(_)_ __   ___        / ___|___ (_)_ __  
// | | | | | | | | '_ \ / _ \ _____| |   / _ \| | '_ \ 
// | |_| | |_| | | | | | (_) |_____| |__| (_) | | | | |
// |____/ \__,_|_|_| |_|\___/       \____\___/|_|_| |_|
//  Code for Arduino boards v1.9
//  © Duino-Coin Community 2019-2021
//  Distributed under MIT License
//
//  If you don't know how to start,
//  visit our official website (duinocoin.com)
//  and navigate to the Getting Started page for help.
//  Happy mining!
//////////////////////////////////////////////////////////
//  https://duinocoin.com - Official Website
//  https://github.com/revoxhere/duino-coin - Official GitHub
//  https://discord.gg/k48Ht5y - Official Discord server
//  https://github.com/revoxhere - @revox (Lead Duino-Coin developer)
//  https://github.com/daknuett - @daknuett (Thanks for help in library migration!
//  https://github.com/JoyBed - @JoyBed (Big thanks for many optimizations!)
//////////////////////////////////////////////////////////

// If uncommented, the count is reversed.
// This allows to not repeat searching the same numbers twice if you have a second Arduino searching the "conventional" way
// and possibly increase efficiency of multi-Arduino setup.
//#define REVERSE_SEARCH

// Include SHA1 part of cryptosuite2 library
#include "sha1.h"
#include <Arduino.h>
#include "printf.h"

String result; // Create globals
char buffer[64] = "";
unsigned int iJob = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Prepare built-in led pin as output
  Serial.begin(115200); // Open serial port
  if (Serial.available()) {
    Serial.println("ready"); // Send start word to miner program
  }
}

void loop() {
  String startStr = Serial.readStringUntil('\n');
  if (startStr == "start") { // Wait for start word, serial.available caused problems
    Serial.flush(); // Clear serial buffer
    String hash = Serial.readStringUntil('\n'); // Read hash
    String job = Serial.readStringUntil('\n'); // Read job
    unsigned int diff = Serial.parseInt() * 100 + 1; // Read difficulty
    unsigned long StartTime = micros(); // Start time measurement
    #ifdef REVERSE_SEARCH
    for (unsigned int iJob = diff; iJob >= 0; iJob--) { // Reversed difficulty loop
    #else
    for (unsigned int iJob = 0; iJob < diff; iJob++) { // Difficulty loop
    #endif
      Sha1.init(); // Create SHA1 hasher
      Sha1.print(String(hash) + String(iJob));
      uint8_t * hash_bytes = Sha1.result(); // Get result
      for (int i = 0; i < 10; i++) { // Cast result to array
        for (int i = 0; i < 32; i++) {
          buffer[2 * i] = "0123456789abcdef"[hash_bytes[i] >> 4]; // MSB to LSB (Depending on the address in hash_bytes)
          // Choose that from the given array of characters
          buffer[2 * i + 1] = "0123456789abcdef"[hash_bytes[i] & 0xf]; // Retreve the value from address next spot over
        }
      }
      result = String(buffer); // Convert and prepare array
      result.remove(40); // First 40 characters are good, rest is garbage
      if (String(result) == String(job)) { // If result is found
        unsigned long EndTime = micros(); // End time measurement
        unsigned long ElapsedTime = EndTime - StartTime; // Calculate elapsed time
        Serial.println(String(iJob) + "," + String(ElapsedTime)); // Send result back to the program with share time
        break; // Stop the loop and wait for more work
      }
    }
  }
}
