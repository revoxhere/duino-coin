// Settings.h
#ifndef SETTINGS_H
#define SETTINGS_H

extern bool displayLock = false;

// ---------------------- General settings ---------------------- //
// Change the part in brackets to your Duino-Coin username
extern char *DUCO_USER = "my_cool_username";
// Change the part in brackets to your mining key (if you have set it in the wallet)
extern char *MINER_KEY = "mySecretPass";
// Change the part in brackets if you want to set a custom miner name
// Use Auto to autogenerate, None for no custom identifier
extern char *RIG_IDENTIFIER = "None";
// Change the part in brackets to your WiFi name
extern const char SSID[] = "SSID";
// Change the part in brackets to your WiFi password
extern const char PASSWORD[] = "PASSW0RD";
// -------------------------------------------------------------- //

// -------------------- Advanced options ------------------------ //
// Uncomment if you want to host the dashboard page (available on ESPs IP address and mDNS)
// #define WEB_DASHBOARD

// Comment out the line below if you wish to disable LED blinking
#define LED_BLINKING

// Uncomment if you want to use LAN8720. WLAN-credentials will be ignored using LAN
// Select correct Board in ArduinoIDE!!! Really!
// #define USE_LAN

// Comment out the line below if you wish to disable Serial printing
#define SERIAL_PRINTING

// Edit the line below if you wish to change the serial speed (low values may reduce performance but are less prone to interference)
#define SERIAL_BAUDRATE 500000

// ESP8266 WDT loop watchdog. Do not edit this value, but if you must - do not set it too low or it will falsely trigger during mining!
#define LWD_TIMEOUT 30000

// Uncomment to disable ESP32 brownout detector if you're suffering from faulty insufficient power detection
// #define DISABLE_BROWNOUT

// Uncomment to enable WiFiManager captive portal in AP mode
// The board will create its own network you connect to and change the settings
// REQUIRES WiFiManager library by tzapu (https://github.com/tzapu/WiFiManager)
// #define CAPTIVE_PORTAL
// -------------------------------------------------------------- //

// ------------------------ Displays ---------------------------- //

// Uncomment to enable a SSD1306 OLED screen on the I2C bus to display mining info in real time
// Default connections (can be overriden by using a different u8g2 initializer, see line 140):
// GND - GND
// VCC - 5V or 3.3V depending on display
// SCL - GPIO22 (ESP32) or GPIO5 (D2 on ESP8266) or GPIO35 (ESP32-S2)
// SDA - GPIO21 (ESP32) or GPIO4 (D1 on ESP8266) or GPIO33 (ESP32-S2)
// #define DISPLAY_SSD1306

// Uncomment to enable a 16x2 LCD screen on a direct bus to display mining info in real time
// See line 150 for connections and initializer
// #define DISPLAY_16X2

//uncomment to enable ESP32 2432S08 module
 #define DISPLAY_2432S08

// Uncomment if your device is a Duino BlushyBox device
// #define BLUSHYBOX
// -------------------------------------------------------------- //

// ---------------------- IoT examples -------------------------- //
// https://github.com/revoxhere/duino-coin/wiki/Duino's-take-on-the-Internet-of-Things

// Uncomment the line below if you wish to use the internal temperature sensor (Duino IoT example)
// Only ESP32-S2, -S3, -H2, -C2, -C3, -C6 and some old models have one!
// More info: https://www.espboards.dev/blog/esp32-inbuilt-temperature-sensor/
// NOTE: Mining performance will decrease by about 20 kH/s!
// #define USE_INTERNAL_SENSOR

// Uncomment the line below if you wish to use a DS18B20 temperature sensor (Duino IoT example)
// NOTE: Mining performance should stay the same
// #define USE_DS18B20

// Uncomment the line below if you wish to use a DHT11/22 temperature and humidity sensor (Duino IoT example)
// NOTE: Mining performance should stay the same
// #define USE_DHT

// Uncomment the line below if you wish to use a HSU07M sensor (Duino IoT Example)
// NOTE: Untested as of right now
// #define USE_HSU07M
// -------------------------------------------------------------- //

//-------------------------Balance display settings--------------------------//
extern bool first_display = true;
extern bool first_start = true;  // to activate balance fetching on boot without waiting for the delay
extern String ducoReportJsonUrl = ""; //  url init
extern const int run_in_ms = 300000; //  5 minutes between each balance update
extern double result_balance_balance = 0;
extern String result_balance_username = "username";// Change the part in brackets to your Duino-Coin username
extern unsigned int total_miner = 0;
//---------------------------------------------------------------------------//

//---------------------------Time Display------------------------------------//
extern char mytime[6] ="";
extern char mydate[12] = "";
extern char myday[10] = "";
//---------------------------------------------------------------------------//

// ---------------- Variables and definitions ------------------- //
// You generally do not need to edit stuff below this line
// unless you're know what you're doing.

#if defined(ESP8266)
    // ESP8266
    #define LED_BUILTIN 2
#elif defined(CONFIG_FREERTOS_UNICORE) 
    #if defined(CONFIG_IDF_TARGET_ESP32C3)
      // ESP32-C3
      #define LED_BUILTIN 8
    #else
      // ESP32-S2
      #define LED_BUILTIN 15
    #endif
#else
    // ESP32
    #ifndef LED_BUILTIN
      #define LED_BUILTIN 2
    #endif
    #if defined(BLUSHYBOX) || defined(DISPLAY_2432S08)
      #define LED_BUILTIN 4
    #endif
#endif

#define BLINK_SETUP_COMPLETE 2
#define BLINK_CLIENT_CONNECT 5

#define SOFTWARE_VERSION "4.3"
extern unsigned int hashrate = 0;
extern unsigned int hashrate_core_two = 0;
extern unsigned int difficulty = 0;
extern unsigned long share_count = 0;
extern unsigned long accepted_share_count = 0;
extern String node_id = "";
extern String WALLET_ID = "";
extern unsigned int ping = 0;

#if defined(USE_INTERNAL_SENSOR)
  #include "driver/temp_sensor.h"
#endif

#if defined(USE_DS18B20)
  // Install OneWire and DallasTemperature libraries if you get an error
  #include <OneWire.h>
  #include <DallasTemperature.h>
  // Change 12 to the pin you've connected your sensor to
  const int DSPIN = 12;
  
  OneWire oneWire(DSPIN);
  DallasTemperature extern sensors(&oneWire);
#endif

#if defined(USE_DHT)
  // Install "DHT sensor library" if you get an error
  #include <DHT.h>
  // Change 12 to the pin you've connected your sensor to
  #define DHTPIN 12
  // Set DHT11 or DHT22 type accordingly
  #define DHTTYPE DHT11
  
  DHT extern dht(DHTPIN, DHTTYPE);
#endif

#if defined(DISPLAY_SSD1306)
    // Install "u8g2" if you get an error
    #include <U8g2lib.h>
    #include <Wire.h>
    // Display definition from the U8G2 library. Edit if you use a different display
    // For software I2C, use ..._F_SW_I2C and define the pins in the initializer
    U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);
#endif

#if defined(DISPLAY_16X2)
    #include "Wire.h"
    // Install "Adafruit_LiquidCrystal" if you get an error
    #include "Adafruit_LiquidCrystal.h"

    // initialize the library with the numbers of the interface pins
    //                         RS E  D4 D5 D6 D7
    Adafruit_LiquidCrystal lcd(1, 2, 3, 4, 5, 6);
#endif

#if defined(DISPLAY_2432S08)
    // Install "lilygo lib TFT_eSPI.h" if you get an error
      #include "esp_sntp.h"
      #include <TFT_eSPI.h>
      
    // Display definition from the tft_eSPI library. Edit if you use a different display
      TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h
#endif

#if defined(USE_HSU07M)
    #include "Wire.h"
    #define HSU07M_ADDRESS 0x4B // Change this if your sensor has a different address

    float read_hsu07m() {
      Wire.beginTransmission(HSU07M_ADDRESS);
      Wire.write(0x00);
      Wire.endTransmission();
      delay(100);
      Wire.requestFrom(HSU07M_ADDRESS, 2);
      if(Wire.available() >= 2) {
          byte tempMSB = Wire.read();
          byte tempLSB = Wire.read();
          int tempRaw = (tempMSB << 8) | tempLSB;
          float tempC = (tempRaw / 16.0) - 40.0;
          return tempC;
      }
      return -1.0;
    }
#endif

#if defined(BLUSHYBOX)
    #define GAUGE_PIN 5
    #define GAUGE_MAX 190
    #define GAUGE_MIN 0
    #if defined(ESP8266)
      #define GAUGE_MAX_HR 80000
    #else
      #define GAUGE_MAX_HR 200000
    #endif
    extern float hashrate_old = 0.0;

    void gauge_set(float hashrate) {
        float old = hashrate_old;
        float new_val = hashrate;

        if (hashrate_old == 0) {
          float delta = (new_val - old) / 50;
          for (int x=0; x < 50; x++) {
              analogWrite(5, map(old + x*delta, 0, GAUGE_MAX_HR, GAUGE_MIN, GAUGE_MAX) + random(0, 10));
              delay(20);
          }
        } else {
          float delta = (new_val - old) / 10;
          for (int x=0; x < 10; x++) {
              analogWrite(5, map(old + x*delta, 0, GAUGE_MAX_HR, GAUGE_MIN, GAUGE_MAX) + random(0, 10));
              delay(10);
          }
        }
        hashrate_old = hashrate;
    }
#endif

IPAddress DNS_SERVER(1, 1, 1, 1); // Cloudflare DNS server

#endif  // End of SETTINGS_H
