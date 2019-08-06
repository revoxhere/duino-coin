/*///////////////////////////////////////////////
/   Duino-Coin arduino code version 0.1 alpha   /
/     https://github.com/revoxhere/duino-coin   /
/             copyright by revox 2019           /
///////////////////////////////////////////////*/

//set some variables
String input; 
int work;
int result;
int hash;
void setup() { //setup
  Serial.begin(9600); //send replies using serial port at 9600
}

void loop() { //main loop
  input = Serial.readString(); //check for connection establishment key
  if (input == 1) {
    Serial.println("CONNECTED"); //feedback for the miner
    delay (1000); //important, propably can be changed but works best at 1000
    char work  = Serial.read(); //get work
    char work2  = Serial.read();
    hash = work+work2*work2+work*work; //hash the work
    Serial.println(hash); //send back the result
    delay(500); //important, propably can be changed but the miner needs time to communcate with server
    //if both delays are set too low, you will get invalid shares
  }
}
