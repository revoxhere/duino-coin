/*///////////////////////////////////////////////
/   Duino-Coin arduino code version 0.2 alpha   /
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
    Serial.println("CONNECTED"); //feedback the miner
    delay(150); //fastest rate possible, pool doesn't accept more shares
    char work  = Serial.read(); //get work
    char work2  = Serial.read();
    hash = work+work2*work+work*work; //hash the work
    Serial.println(hash); //send back the result
    //delay(150); //fastest rate possible
  }
}
