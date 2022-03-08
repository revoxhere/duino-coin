// Duino-coin miner for STM32 and AVR chip family
// https://duinocoin.com/

// by: pankleks 2022
// v: 1.2
// https://github.com/pankleks
// MIT License

#include <Arduino.h>
#include <sha1.h>
#include <ArduinoUniqueID.h>

// features
#define RESET_NO_JOBS // comment to not reset board if no jobs

#ifdef ARDUINO_ARCH_STM32
#define LOG // comment to disable debug logs to Serial1
#define LED_BUILTIN PC13
#endif

#define NO_JOBS_RESET_S 60 // reset board if no jobs for longer than 60s

String clientId;

void log(String msg)
{
#ifdef LOG
  Serial1.println(msg);
#endif
}

String getClientId()
{
  String temp = "DUCOID";

  for (int i = 0; i < UniqueIDsize; i++)
    temp += String(UniqueID[i], HEX);

  return temp;
}

void ledOn()
{
  digitalWrite(LED_BUILTIN, false);
}

void ledOff()
{
  digitalWrite(LED_BUILTIN, true);
}

void setup()
{
  clientId = getClientId();
  pinMode(LED_BUILTIN, OUTPUT);
  ledOn();

#ifdef LOG
  Serial1.begin(115200);
#endif
  log(clientId);

  Serial.begin(115200);
  Serial.setTimeout(3000);

  // wait for connection
  while (!Serial)
    ;

  Serial.flush();

  log(F("setup done"));
  ledOff();
}

void clearSerial()
{
  while (Serial.available())
    Serial.read();
}

int ducos1a(String lastHash, String expHash, int difficulty)
{
  const char *c = expHash.c_str();
  uint8_t length = expHash.length() / 2;
  uint8_t job[104];

  for (size_t i = 0, j = 0; j < length; i += 2, j++)
    job[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;

  SHA1_CTX baseCtx;
  SHA1Init(&baseCtx);
  SHA1Update(&baseCtx, (uint8_t *)lastHash.c_str(), lastHash.length());

  uint8_t buf[20];

  for (int result = 0; result < difficulty * 100 + 1; result++)
  {
    SHA1_CTX ctx = SHA1Copy(baseCtx);
    itoa(result, (char *)buf, 10);

    SHA1Update(&ctx, buf, strlen((char *)buf));
    SHA1Final(buf, &ctx);

    if (memcmp(buf, job, 20) == 0) // if found hash = expected hash -> result
      return result;
  }

  return -1; // not found
}

#ifdef ARDUINO_ARCH_AVR
void (*resetFn)(void) = 0;
#endif

void reset()
{
#ifdef ARDUINO_ARCH_AVR
  resetFn();
#endif
#ifdef ARDUINO_ARCH_STM32
  NVIC_SystemReset();
#endif
}

String lastHash;
String expHash;
uint32_t difficulty;
long lastOkJobT = millis();
long t = 0;

void loop()
{
  if (Serial.available() > 0)
  {
    log(F("got data"));

    lastHash = Serial.readStringUntil(',');
    log("LH: " + lastHash);

    expHash = Serial.readStringUntil(',');
    log("EH: " + expHash);

    difficulty = Serial.readStringUntil(',').toInt() * 100;
    log("DF: " + String(difficulty));

    clearSerial();
    ledOn();

    long startT = micros();

    expHash.toUpperCase();
    int result = ducos1a(lastHash, expHash, difficulty);

    long elapsedT = micros() - startT;

    ledOff();
    clearSerial();

    Serial.print(String(result) + "," + String(elapsedT) + "," + clientId + "\n");

    log("R: " + String(result) + ", " + String((float)elapsedT / 1000000) + " s");

    lastOkJobT = millis();
  }

  if (millis() - t > 1000)
  {
    t = millis();

    long n = millis() - lastOkJobT;
    log("last ok job " + String(n) + " ms ago");

#ifdef RESET_NO_JOBS
    if (n > NO_JOBS_RESET_S * 1000L)
    {
      log(F("no jobs, reset"));
    }
#endif
  }
}
