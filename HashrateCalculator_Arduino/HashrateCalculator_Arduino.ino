#include "sha1.h"
String result; // Create globals
char buffer[64] = "";
unsigned int iJob = 0;

void setup() {
  Serial.begin(9600); // Enable serial
}

void loop() {
  Serial.println("\nWaiting 500ms before starting test..."); // Print to the console
  delay(500);

  // Test 1 hash
  unsigned long StartTime = micros(); // Start time
  Sha1.init(); // Create sha1 hasher
  Sha1.print("abc");
  uint8_t * hash_bytes = Sha1.result(); // Get result
  for (int i = 0; i < 10; i++) { // Cast result to array
    for (int i = 0; i < 32; i++) {
      buffer[2 * i] = "0123456789abcdef"[hash_bytes[i] >> 4];
      buffer[2 * i + 1] = "0123456789abcdef"[hash_bytes[i] & 0xf];
    }
  }
  result = String(buffer); // Convert and prepare array
  unsigned long CurrentTime = micros(); // End time

  unsigned long ElapsedTime = CurrentTime - StartTime; // Elapsed time
  Serial.println("Test 1: Generated 1 hash in " + String(ElapsedTime) + " microseconds."); // Print to the console

  // Test 1000 hashes
  StartTime = micros(); // Start time
  for (int i = 0; i < 1000; i++) {
    Sha1.init(); // Create sha1 hasher
    Sha1.print(String(iJob);
               uint8_t * hash_bytes = Sha1.result(); // Get result
    for (int i = 0; i < 10; i++) { // Cast result to array
    for (int i = 0; i < 32; i++) {
        buffer[2 * i] = "0123456789abcdef"[hash_bytes[i] >> 4];
        buffer[2 * i + 1] = "0123456789abcdef"[hash_bytes[i] & 0xf];
      }
    }
    result = String(buffer); // Convert and prepare array
  }
  CurrentTime = micros(); // End time

  ElapsedTime = CurrentTime - StartTime; // Elapsed time
  float ElapsedTimeS = CurrentTime - StartTime; // Elapsed time in seconds
  ElapsedTimeS = ElapsedTimeS / 1000000; // Convert to seconds
  Serial.println("Test 2: Generated 1000 hashes in " + String(ElapsedTime) + " microseconds (" + String(ElapsedTimeS) + " seconds)."); // Print to the console

  // Calculate hashrate
  /* 1000 hashes - ElapsedTime microseconds
      x   hashes - 1000000 microseconds (1 s)
      1000*1000000 / ElapsedTime = x */
  float hashrate = 1000 * 1000000 / ElapsedTime;
  hashrate = hashrate / 1000; // Convert to kH
  Serial.println("Calculated theoretical hashrate: " + String(hashrate, 4) + "kH/s."); // Print to the console
}
