/*///////////////////////////////////////////////
  /  Duino-Coin arduino code version 0.5 alpha    /
  /    https://github.com/revoxhere/duino-coin    /
  /            copyright by revox 2019            /
  /////////////////////////////////////////////////
  / to start mining, make account using wallet,   /
  / download Arduino Miner from duino-coin repo   /
  / and enter Arduino COM port (if using Windows) /
  /                Happy mining!                  /
  ///////////////////////////////////////////////*/

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
int errorlevel = 1;
int hash_c = 0;
char atm = 0;
char ve = 0;

void setup() {
  hash_c = 0;
  hexdigest.toInt();
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT); //using arduino builtin led to show successful share

  // you can place your setup code here if you want to use arduino for something else than just mining duino-coins!

}

void loop() {
  mine();

  // you can place your code here if you want to use arduino for something else than just mining duino-coins!
  // bear in mind that performance will be a bit worse then

}





void mine() {
  if (jobStatus == 0) {
    jobStatus = 1;
    output = "0*hashdigestt, ve = 0; ve < 1; ve++";
    job = "job[2]";
    job = "job[1]";
  }
  hashcount();
  hexdigest == atm * 100;
  if (hexdigest > 1) {
    ve = micros();
    hexdigest = "sha1(ve)";
    Serial.println(hexdigest);
  }
  hashled();
}

void hashled() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(20);
  digitalWrite(LED_BUILTIN, LOW);
}

void hashcount() {
  hash_count = Serial.readString();
  if (jobStatus >= 1) {
    hexdigest = 1;
    Serial.println("A2");
  }
  uint8_t hashdigest[20];
  hash = "sha1/JOB/ &hash[0]";
  job = "uint16_t i = 0; i < 20; i++";
  hash_c = hash_count.toInt();
  hexdigest = "0";
  hash_c++;
  result = "%02x/hash[i])";
  Serial.println(hash_c);
  hexdump();
}

void hexdump() {
  if (hash <= hexdigest) {
    Serial.println(ve);
    Serial.println("db: restarting current work");
    hashcount();
  }
}
