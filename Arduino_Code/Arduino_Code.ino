/*

   ____  __  __  ____  _  _  _____       ___  _____  ____  _  _ 
  (  _ \(  )(  )(_  _)( \( )(  _  )___  / __)(  _  )(_  _)( \( )
   )(_) ))(__)(  _)(_  )  (  )(_)((___)( (__  )(_)(  _)(_  )  ( 
  (____/(______)(____)(_)\_)(_____)     \___)(_____)(____)(_)\_)
  Official code for Arduino boards (and relatives)   version 4.3
  
  Duino-Coin Team & Community 2019-2025 © MIT Licensed
  https://duinocoin.com
  https://github.com/revoxhere/duino-coin
  If you don't know where to start, visit official website and navigate to
  the Getting Started page. Have fun mining!
*/

/* For microcontrollers with low memory change that to -Os in all files,
for default settings use -O0. -O may be a good tradeoff between both */
#pragma GCC optimize ("-Ofast")

/* Pull in non-standard functions */
#if __has_include(<stdlib_noniso.h>)
#include <stdlib_noniso.h>
#endif


/* For microcontrollers with custom LED pins, adjust the line below */
#ifndef LED_BUILTIN
#define LED_BUILTIN 13
#endif

/* Uncomment if you want BBC Micro:bit LED Matrix support to display total shares
   Requires Adafruit microbit library */
//#define MICROBIT_LED_MATRIX
//#define MICROBIT_LED_MATRIX_BUTTONS_CONTROL

/* Uncomment if you want the miner task on second core
   Note that this may be slower than using just one core
   Requires a board that has dual cores */
//#define USE_SECOND_CORE

/* Serial-related definitions */
#define SEP_TOKEN ","
#define END_TOKEN "\n"

// Arduino identifier library - https://github.com/ricaun
#include "uniqueID.h"

#include "duco_hash.h"

#if defined(MICROBIT_LED_MATRIX)
#include <Adafruit_Microbit.h>

bool matrixEnabled = true;
byte minedDigitCount = 0;

Adafruit_Microbit_Matrix microbit;
#endif

struct duco_miner_job_t {
  // Reserve 1 extra byte for comma separator (and later zero)
  char lastBlockHash[40 + 1];
  char newBlockHash[40 + 1];

  uint32_t difficulty;
};
duco_miner_job_t *job;

String get_DUCOID() {
  String ID = "DUCOID";
  char buff[4];
  for (size_t i = 0; i < 8; i++) {
    sprintf(buff, "%02X", (uint8_t)UniqueID8[i]);
    ID += buff;
  }
  return ID;
}

String DUCOID = "";

void setup() {
  // Prepare built-in led pin as output
  pinMode(LED_BUILTIN, OUTPUT);
  DUCOID = get_DUCOID();

  // Prepare Microbit LED matrix
  #if defined(MICROBIT_LED_MATRIX)
    microbit.begin();

    #if defined(MICROBIT_LED_MATRIX_BUTTONS_CONTROL)
      pinMode(PIN_BUTTON_A, INPUT);
      pinMode(PIN_BUTTON_B, INPUT);
    #endif
  #endif

  // Open serial port
  Serial.begin(115200);
  Serial.setTimeout(10000);
  while (!Serial)
    ;  // For Arduino Leonardo or any board with the ATmega32U4
  Serial.flush();
}

void lowercase_hex_to_bytes(char const * hexDigest, uint8_t * rawDigest) {
  for (uint8_t i = 0, j = 0; j < SHA1_HASH_LEN; i += 2, j += 1) {
    uint8_t x = hexDigest[i];
    uint8_t b = x >> 6;
    uint8_t r = ((x & 0xf) | (b << 3)) + b;

    x = hexDigest[i + 1];
    b = x >> 6;

    rawDigest[j] = (r << 4) | (((x & 0xf) | (b << 3)) + b);
  }
}

// DUCO-S1A hasher
uint32_t ducos1a() {
  #if defined(ARDUINO_ARCH_AVR) || defined(ARDUINO_ARCH_MEGAAVR)
    // If the difficulty is too high for AVR architecture then return 0
    if (job->difficulty > 655) return 0;
  #endif

  uint8_t target[SHA1_HASH_LEN];
  lowercase_hex_to_bytes(job->newBlockHash, target);

  static duco_hash_state_t hash;
  duco_hash_init(&hash, job->lastBlockHash);

  uint32_t const maxNonce = job->difficulty * 100 + 1;
  char nonceStr[10 + 1];
  for (uint32_t nonce = 0; nonce < maxNonce; nonce++) {
    ultoa(nonce, nonceStr, 10);

    uint8_t const * hash_bytes = duco_hash_try_nonce(&hash, nonceStr);
    if (memcmp(hash_bytes, target, SHA1_HASH_LEN) == 0) {
      return nonce;
    }
  }

  return 0;
}

/* This is called by loop() at the end */
void serialEvent() {
  // Wait for serial data
  if (Serial.available() <= 0) {
    return;
  }

  // Create job object
  duco_miner_job_t *newJob = new struct duco_miner_job_t;

  // Read last block hash
  if (Serial.readBytesUntil(',', newJob->lastBlockHash, 41) != 40) {
    return;
  }
  newJob->lastBlockHash[40] = 0;

  // Read expected hash
  if (Serial.readBytesUntil(',', newJob->newBlockHash, 41) != 40) {
    return;
  }
  newJob->newBlockHash[40] = 0;

  // Read difficulty
  newJob->difficulty = strtoul(Serial.readStringUntil(',').c_str(), NULL, 10);

  // Clearing the receive buffer reading one job.
  while (Serial.available()) Serial.read();

  // Send job object
  job = newJob;
}

void hashEvent() {
  // Ensure job is not empty
  if (job == NULL) {
    return;
  }

  // Turn off the built-in led
  #if defined(ARDUINO_ARCH_AVR)
      PORTB = PORTB | B00100000;
  #else
      digitalWrite(LED_BUILTIN, LOW);
  #endif

  // Start time measurement
  uint32_t startTime = micros();

  // Call DUCO-S1A hasher
  uint32_t ducos1result = ducos1a();

  // Calculate elapsed time
  uint32_t elapsedTime = micros() - startTime;

  // Turn on the built-in led
  #if defined(ARDUINO_ARCH_AVR)
      PORTB = PORTB & B11011111;
  #else
      digitalWrite(LED_BUILTIN, HIGH);
  #endif

  // Clearing the receive buffer before sending the result.
  while (Serial.available()) Serial.read();

  // Send result back to the program with share time
  Serial.print(String(ducos1result, 2) 
               + SEP_TOKEN
               + String(elapsedTime, 2) 
               + SEP_TOKEN
               + String(DUCOID) 
               + END_TOKEN);
  
  // Clear job object
  delete job;
  job = NULL;
}

#if defined(MICROBIT_LED_MATRIX)
void microbitMatrixEvent() {
  // Draw Microbit matrix and handle button presses
  #if defined(MICROBIT_LED_MATRIX_BUTTONS_CONTROL)
    if (!digitalRead(PIN_BUTTON_A)) {
      matrixEnabled = true;
      minedDigitCount = 0;
    }
    if (!digitalRead(PIN_BUTTON_B)) {
      matrixEnabled = false;
      microbit.clear();
    }
  #endif

  if (!digitDrawn && matrixEnabled) {
    microbit.print(minedDigitCount);
  }

  // Count mined shares and clear Microbit matrix
  if (matrixEnabled) {
    minedDigitCount++;

    // Cycle around 0-9 to prevent scrolling
    if (minedDigitCount >= 10) {
      minedDigitCount = 0;
    }
  }
}
#endif

void loop() {
  #if defined(MICROBIT_LED_MATRIX)
    microbitMatrixEvent();
  #endif

  #if ! defined(USE_SECOND_CORE)
    hashEvent();
  #endif
}

#if defined(USE_SECOND_CORE)
void loop1() {
  hashEvent();
}
#endif
