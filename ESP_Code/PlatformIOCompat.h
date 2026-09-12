#pragma once
#include <Arduino.h>

// PlatformIO test-build compatibility declarations for ESP_Code.ino.
// Arduino IDE normally auto-generates these prototypes for .ino sketches.
void RestartESP(String msg);

#if defined(CAPTIVE_PORTAL)
String getParam(String name);
#endif
