// Settings.h
#ifndef SETTINGS_H
#define SETTINGS_H

// ---------------------- General settings ---------------------- //
// Change the part in brackets to your Duino-Coin username
extern const char DUCO_USER[] = "my_cool_username";
// Change the part in brackets to your mining key (if you have set it in the wallet)
extern const char MINER_KEY[] = "mySecretPass";
// Change the part in brackets to your WiFi name
extern const char SSID[] = "SSID";
// Change the part in brackets to your WiFi password
extern const char PASSWORD[] = "PASSW0RD";
// Change the part in brackets if you want to set a custom miner name
// Use Auto to autogenerate, None for no custom identifier
extern const char RIG_IDENTIFIER[] = "None";

// Uncomment if you want to host the dashboard page (available on ESPs IP address)
// #define WEB_DASHBOARD

// Comment out the line below if you wish to disable LED blinking
#define LED_BLINKING

#define BLINK_SETUP_COMPLETE 2
#define BLINK_CLIENT_CONNECT 5
// -------------------------------------------------------------- //

// ---------------------- IoT examples -------------------------- //
// https://github.com/revoxhere/duino-coin/wiki/Duino's-take-on-the-Internet-of-Things
// Uncomment the line below if you wish to use a DS18B20 temperature sensor (Duino IoT example)
// #define USE_DS18B20

// Uncomment the line below if you wish to use a DHT11/22 temperature and humidity sensor (Duino IoT example)
// #define USE_DHT
// -------------------------------------------------------------- //

#define SOFTWARE_VERSION "4.0"
extern unsigned int hashrate = 0;
extern unsigned int difficulty = 0;
extern unsigned int share_count = 0;
extern String node_id = "";

#if defined(USE_DS18B20)
  // Install OneWire and DallasTemperature libraries if you get an error
  #include <OneWire.h>
  #include <DallasTemperature.h>
  // Change 12 to the pin you've connected your sensor to
  #define DSPIN 12
  
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

#endif  // End of SETTINGS_H
