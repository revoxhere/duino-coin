// Duino-coin miner for STM32 chip family
// https://duinocoin.com/

// by: pankleks 2021
// https://github.com/pankleks
// MIT License

#include <Arduino.h>
#include <Hash.h>
#include <Id.h>

// features
#define LOG           // comment to disable debug logs to Serial1
#define RESET_NO_JOBS // comment to not reset board if no jobs

#define SHA1_HASH_LEN 20
#define JOB_MAX_SIZE 104 // 40 + 40 + 20 + 3
#define LED_BUILTIN PC13
#define NO_JOBS_RESET_S 60 // reset board if no jobs for longer than 60s

String clientId;
uint8_t job[JOB_MAX_SIZE];

void log(String msg)
{
#ifdef LOG
  Serial1.println(msg);
#endif
}

String getClientId()
{
  uint32_t id[3];
  GetSTM32MCUID(id);

  char buf[22];
  sprintf(buf, "%08X%08X%08X", id[0], id[1], id[2]); // 12 byte
  return "DUCOID" + String(buf);
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

uint32_t ducos1a(String lastHash, String expHash, uint32_t difficulty)
{
  const char *c = expHash.c_str();
  uint8_t length = expHash.length() / 2;

  memset(job, 0, JOB_MAX_SIZE);
  for (size_t i = 0, j = 0; j < length; i += 2, j++)
    job[j] = (c[i] % 32 + 9) % 25 * 16 + (c[i + 1] % 32 + 9) % 25;

  uint8_t hashBuf[SHA1_HASH_LEN];

  for (uint32_t result = 0; result < difficulty * 100 + 1; result++)
  {
    sha1(lastHash + String(result), hashBuf);

    if (memcmp(hashBuf, job, SHA1_HASH_LEN * sizeof(char)) == 0) // if found hash = expected hash -> result
      return result;
  }

  return 0; // not found
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

    difficulty = Serial.readStringUntil(',').toInt();
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

    log("R: " + String(result) + ", " + String((float)elapsedT / 1000000) + " s.");

    lastOkJobT = millis();
  }

  if (millis() - t > 1000)
  {
    t = millis();

    long n = millis() - lastOkJobT;
    log("last ok job " + String(n) + " ms ago");

#ifdef RESET_NO_JOBS
    if (n > NO_JOBS_RESET_S * 1000)
    {
      log(F("no jobs, reset"));
      NVIC_SystemReset();
    }
#endif
  }
}
