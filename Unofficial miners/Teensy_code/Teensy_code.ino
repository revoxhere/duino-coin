//////////////////////////////////////////////////////////
//  _____        _                    _____      _
// |  __ \      (_)                  / ____|    (_)
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_|
//  Code for Teensy 4.1 boards v2.4
//  © Duino-Coin Community 2019-2022
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/joaquinbvw - Teensy 4.1 code
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
// Include Arduino identifier library
// Author: https://github.com/ricaun
//#include "uniqueID.h"
#include "Arduino.h"
#include <TeensyID.h>
// Create globals
char buffer[44];
String IDstring = "DUCOID";
String lastblockhash = "";
String newblockhash = "";
unsigned int difficulty = 0;
unsigned int ducos1result = 0;
int led = 13;
unsigned int sizeofblockhash1 = 100;
unsigned char* newblockhash1;

// Setup stuff
void setup() {
  lastblockhash.reserve(200);
  newblockhash.reserve(200);
  // Prepare built-in led pin as output
  //pinMode(LED_BUILTIN, OUTPUT);
  pinMode(led, OUTPUT);
  // Open serial port
  Serial.begin(1000000);
  Serial.setTimeout(5000);
  // Grab Arduino chip ID
  uint8_t uid64[8];
  teensyUID64(uid64);
  IDstring = IDstring + teensyUID64();
  IDstring.remove(IDstring.length()-3,1);
  IDstring.remove(IDstring.length()-5,1);
  IDstring.remove(IDstring.length()-7,1);
  IDstring.remove(IDstring.length()-9,1);
  IDstring.remove(IDstring.length()-11,1);
  IDstring.remove(IDstring.length()-13,1);
  IDstring.remove(IDstring.length()-15,1);
  //for (size_t i = 0; i < 8; i++)
    //IDstring += uid64[i];
    //IDstring += UniqueID[i];
  newblockhash1 = (unsigned char*)malloc(sizeofblockhash1 * sizeof(unsigned char));
  Serial.flush();
  //Serial.println(IDstring);
  //Serial.println(SHA1_HASH_LEN*sizeof(char));
}

// DUCO-S1A hasher
int ducos1a(String lastblockhash_, String newblockhash_, int difficulty_) {
  // DUCO-S1 algorithm implementation for AVR boards (DUCO-S1A)
  // Difficulty loop
  //Conversion
  const char * c = newblockhash_.c_str();
  size_t len = newblockhash_.length();
  size_t final_len = len / 2;
  //unsigned char* newblockhash1 = (unsigned char*)malloc((final_len + 1) * sizeof(unsigned char));
  memset(newblockhash1, 0, sizeofblockhash1);
  for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
    newblockhash1[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;
  for (int ducos1res = 0; ducos1res < difficulty_ * 100 + 1; ducos1res++) {
    delayMicroseconds(65);
    Sha1.init();
    Sha1.print(lastblockhash_ + String(ducos1res));
    //Sha1.print(lastblockhash_ + ducos1res);
    // Get SHA1 result
    uint8_t * hash_bytes = Sha1.result();
    //delayMicroseconds(50);
    //if (memcmp(hash_bytes, newblockhash1, sizeof(hash_bytes)) == 0) {
    //if (memcmp(hash_bytes, newblockhash1, SHA1_HASH_LEN) == 0) {
    if (memcmp(hash_bytes, newblockhash1, SHA1_HASH_LEN*sizeof(char)) == 0) {
      // If expected hash is equal to the found hash, return the result
      return ducos1res;
    }
  }
  return 0;
}

// Infinite loop
void loop() {
  // Wait for serial data
  while (Serial.available() > 10) {
    // Read last block hash
    lastblockhash = Serial.readStringUntil(',');
    // Read expected hash
    newblockhash = Serial.readStringUntil(',');
    // Read difficulty
    difficulty = Serial.readStringUntil(',').toInt();
    while(Serial.available())
      Serial.read();
    newblockhash.toUpperCase();
    // Start time measurement
    unsigned long startTime = micros();
    // Call DUCO-S1A hasher
    ducos1result = ducos1a(lastblockhash, newblockhash, difficulty);
    lastblockhash = "";
    newblockhash = "";
    difficulty = 0;
    // End time measurement
    unsigned long endTime = micros();
    // Calculate elapsed time
    unsigned long elapsedTime = endTime - startTime;
    // Send result back to the program with share time
    while(Serial.available())
      Serial.read();
    Serial.print(String(ducos1result) + "," + String(elapsedTime) + "," + String(IDstring) + "\n");
    // Turn on built-in led
    //PORTB = PORTB | B00100000;
    digitalWrite(led, HIGH);
    // Wait a bit
    delay(25);
    // Turn off built-in led
    //PORTB = PORTB & B11011111;
    digitalWrite(led, LOW);
  }
}
