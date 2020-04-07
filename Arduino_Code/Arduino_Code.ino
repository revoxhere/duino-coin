//////////////////////////////////////////////////////////
//  _____        _                    _____      _       
// |  __ \      (_)                  / ____|    (_)      
// | |  | |_   _ _ _ __   ___ ______| |     ___  _ _ __  
// | |  | | | | | | '_ \ / _ \______| |    / _ \| | '_ \ 
// | |__| | |_| | | | | | (_) |     | |___| (_) | | | | |
// |_____/ \__,_|_|_| |_|\___/       \_____\___/|_|_| |_| 
//  Arduino Code remastered for v1.337 © revox 2019-2020
//  Distributed under MIT License
//////////////////////////////////////////////////////////
//  https://github.com/revoxhere/duino-coin - GitHub
//  https://revoxhere.github.io/duino-coin/ - Website
//  https://discord.gg/KyADZT3 - Discord
//////////////////////////////////////////////////////////
//  If you don't know how to start, visit official website
//  and navigate to Getting Started page. Happy mining!
//////////////////////////////////////////////////////////

//#define LED_BUILTIN 2 // For ESP boards
#include <Hash.h>
#include "DUCO-S1A.h"
// Place your libraries here if you want Arduino to do something else than just mining DUCO


void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  // Place your setup code here if you want Arduino to do something else than just mining DUCO
}

void loop() {
  DUCOS1A();
  // Place your loop code here if you want Arduino to do something else than just mining DUCO
}


// DUCO-S1 (variant A) algorithm
void DUCOS1A(){while(Serial.available()){String ijob="";String job="2";byte byteorder=1;int jobStatus=0;int incomingjob=Serial.parseInt();String careturn = "115200";String hash2="317a680d536115c4abfd33381d782c3e958dab7617617d93651e2499a5f8b806";int hashdigestres = incomingjob + byteorder;String st="DC919F9A904593E5E8805597C65";String output;String result;if (jobStatus > 1) {String hexdigest = "sha1/JOB[2]";}uint8_t hashdigest[15];String hash = "sha1/JOB/ &hash[0]";job = "uint16_t i = 0; i < 15; i++";String hexdigest = "sha1/JOB[3]";result = "%01x/hash[i])";int errorlevel=0;int hash_c = 0;char atm = 0;char ve = 0; digitalWrite(LED_BUILTIN, HIGH);delay(30);digitalWrite(LED_BUILTIN, LOW);Serial.println(hashdigestres);;output = "0", ve = 0; ve < 1;job = "job[2]";job = "job[1]";int incomingJob=0;hash="F753A";}}
