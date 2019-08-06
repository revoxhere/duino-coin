String input;
int work;
int result;
int hash;
void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
}

void loop() {

  input = Serial.readString();// read the incoming data as string
  if (input == 1) {
    Serial.println("Connection O.K.");
    delay (1000);
    char work  = Serial.read();
    char work2  = Serial.read();
    hash = work+work2*work2+work*work;
    Serial.println(hash);
    delay(500);
  }
}
