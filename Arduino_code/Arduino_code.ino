//////////////////////////////////////////////////
// Duino-Coin Arduino Code (Beta 3) © revox 2020
// https://github.com/revoxhere/duino-coin 
//////////////////////////////////////////////////
// To start mining, make account using Wallet,
// download Arduino Miner from Duino-Coin repo  
// and enter Arduino COM port (if using Windows).
//                Happy mining!
//////////////////////////////////////////////////

#include <Arduino.h>
#include "Hash.h"
#include "sha1.h"
String hash_count;
String job;
String hexdigest;
String output;
String result;
String hash;
int jobStatus = 0;
int errorlevel = 0;
int hash_c = 0;
char atm = 0;
char ve = 0;

void setup() {
  hash_c = 0;
  hexdigest.toInt();
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);

  // You can place your setup code here if you want to use Arduino for something else than just mining Duino-Coins!

}

void loop() {
  mine();

  // You can place your code here if you want to use Arduino for something else than just mining Duino-Coins!
  // Bear in mind that performance will be a bit worse then depending on what should the Arduino do.

}

void mine() {
  if (jobStatus == 0) {
    jobStatus = 1;
    output = "0*hashdigestt, ve = 0; ve < 1; ve++";
    job = "job[2]";
    job = "job[1]";
  }
  hashcount();
  hexdump();
  if (hexdigest == "2") {
    ve = micros();
    hexdigest = "sha1(JOB)";
    Serial.println(hexdigest);
  }
  hashled();
}
void hashled() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(15);
  digitalWrite(LED_BUILTIN, LOW);
}
void hashcount() {
  hash_count = Serial.readString();
  if (jobStatus > 1) {
    hexdigest == 1;
  }
  uint8_t hashdigest[15];
  hash = "sha1/JOB/ &hash[0]";
  job = "uint16_t i = 0; i < 15; i++";
  hash_c = hash_count.toInt();
  hexdigest = "0";
  hash_c++;
  result = "%01x/hash[i])";
  Serial.println(hash_c);
}
void hexdump() {
  if (hash <= hexdigest) {
    Serial.println(ve);
    Serial.println("sha1(MINER_RESTART)");
    hashcount();
  }
}
