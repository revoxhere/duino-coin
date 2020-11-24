#include <Hash.h> // Include crypto library

void setup() {
  Serial.begin(9600); // Enable serial
}


void loop() {
  Serial.println("\nWaiting 500ms before starting test..."); // Print to the console
  delay(500);

  // Test 1 hash
  unsigned long StartTime = micros(); // Start time
  sha1(String(random(0, 3000))); // Simulate hashing process - Hash a random number from 0 to 3000, do it 1000 times
  unsigned long CurrentTime = micros(); // End time
  
  unsigned long ElapsedTime = CurrentTime - StartTime; // Elapsed time
  Serial.println("Test 1: Generated 1 hash in " + String(ElapsedTime) + " microseconds."); // Print to the console

  // Test 1000 hashes
  StartTime = micros(); // Start time
  for (int i = 0; i < 1000; i++) {
    sha1(String(random(0, 3000))); // Simulate hashing process - Hash a random number from 0 to 3000, do it 1000 times
  }
  CurrentTime = micros(); // End time
  
  ElapsedTime = CurrentTime - StartTime; // Elapsed time
  float ElapsedTimeS = CurrentTime - StartTime; // Elapsed time in seconds
  ElapsedTimeS = ElapsedTimeS / 1000000; // Convert to seconds
  Serial.println("Test 2: Generated 1000 hashes in " + String(ElapsedTime) + " microseconds (" + String(ElapsedTimeS) + " seconds)."); // Print to the console

  // Calculate hashrate
  /* 1000 hashes - ElapsedTime microseconds
   *  x   hashes - 1000000 microseconds (1 s)
   *  1000*1000000 / ElapsedTime = x */
  float hashrate = 1000*1000000 / ElapsedTime;
  hashrate = hashrate / 1000; // Convert to kH
  Serial.println("Calculated theoretical hashrate: " + String(hashrate, 4) + "kH/s."); // Print to the console
}
