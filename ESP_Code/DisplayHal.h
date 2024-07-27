// Abstraction layer for handling various types of screens
// See Settings.h for enabling the screen of your choice
#ifndef DISPLAY_HAL_H
#define DISPLAY_HAL_H

// Abstraction layer: custom fonts, images, etc.
#if defined(DISPLAY_SSD1306)
    static const unsigned char image_check_contour_bits[] U8X8_PROGMEM = {0x00,0x04,0x00,0x0a,0x04,0x11,0x8a,0x08,0x51,0x04,0x22,0x02,0x04,0x01,0x88,0x00,0x50,0x00,0x20,0x00};
    static const unsigned char image_network_1_bar_bits[] U8X8_PROGMEM = {0x00,0x70,0x00,0x50,0x00,0x50,0x00,0x50,0x00,0x57,0x00,0x55,0x00,0x55,0x00,0x55,0x70,0x55,0x50,0x55,0x50,0x55,0x50,0x55,0x57,0x55,0x57,0x55,0x77,0x77,0x00,0x00};
    static const unsigned char image_network_2_bars_bits[] U8X8_PROGMEM = {0x00,0x70,0x00,0x50,0x00,0x50,0x00,0x50,0x00,0x57,0x00,0x55,0x00,0x55,0x00,0x55,0x70,0x55,0x70,0x55,0x70,0x55,0x70,0x55,0x77,0x55,0x77,0x55,0x77,0x77,0x00,0x00};
    static const unsigned char image_network_3_bars_bits[] U8X8_PROGMEM = {0x00,0x70,0x00,0x50,0x00,0x50,0x00,0x50,0x00,0x57,0x00,0x57,0x00,0x57,0x00,0x57,0x70,0x57,0x70,0x57,0x70,0x57,0x70,0x57,0x77,0x57,0x77,0x57,0x77,0x77,0x00,0x00};
    static const unsigned char image_network_4_bars_bits[] U8X8_PROGMEM = {0x00,0x70,0x00,0x70,0x00,0x70,0x00,0x70,0x00,0x77,0x00,0x77,0x00,0x77,0x00,0x77,0x70,0x77,0x70,0x77,0x70,0x77,0x70,0x77,0x77,0x77,0x77,0x77,0x77,0x77,0x00,0x00};
    static const unsigned char image_duco_logo_bits[] U8X8_PROGMEM = {0x20,0x00,0x20,0x00,0x20,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x7f,0x00,0xff,0x00,0xc0,0x01,0x9f,0x01,0x20,0x01,0x20,0x01,0x20,0x01,0x9f,0x01,0xc0,0x01,0xff,0x00,0x7f,0x00};
    static const unsigned char image_duco_logo_big_bits[] U8X8_PROGMEM = {0x00,0x00,0x00,0x00,0x00,0x00,0xfc,0xff,0xff,0x01,0x00,0x00,0xfc,0xff,0xff,0x0f,0x00,0x00,0xfc,0xff,0xff,0x3f,0x00,0x00,0xfc,0xff,0xff,0x7f,0x00,0x00,0xfc,0xff,0xff,0xff,0x00,0x00,0xfc,0xff,0xff,0xff,0x01,0x00,0xfc,0xff,0xff,0xff,0x03,0x00,0xf8,0xff,0xff,0xff,0x07,0x00,0x00,0x00,0x00,0xfe,0x0f,0x00,0xfc,0xff,0x03,0xf8,0x0f,0x00,0xfc,0xff,0x0f,0xf0,0x1f,0x00,0xfc,0xff,0x1f,0xe0,0x1f,0x00,0xfc,0xff,0x3f,0xe0,0x3f,0x00,0xfc,0xff,0x7f,0xc0,0x3f,0x00,0xfc,0xff,0xff,0xc0,0x7f,0x00,0xf8,0xff,0xff,0x80,0x7f,0x00,0x00,0x00,0xfe,0x80,0x7f,0x00,0x00,0x00,0xfc,0x81,0x7f,0x00,0x00,0x00,0xfc,0x01,0x7f,0x00,0x00,0x00,0xfc,0x01,0xff,0x00,0x00,0x00,0xfc,0x01,0xff,0x00,0x00,0x00,0xfc,0x01,0xff,0x00,0x00,0x00,0xfc,0x01,0xff,0x00,0x00,0x00,0xfc,0x01,0xff,0x00,0x00,0x00,0xfc,0x81,0x7f,0x00,0x00,0x00,0xfe,0x81,0x7f,0x00,0x00,0x80,0xff,0x80,0x7f,0x00,0xfc,0xff,0xff,0xc0,0x7f,0x00,0xfc,0xff,0xff,0xc0,0x7f,0x00,0xfc,0xff,0x7f,0xe0,0x3f,0x00,0xfc,0xff,0x3f,0xf0,0x3f,0x00,0xfc,0xff,0x1f,0xf8,0x1f,0x00,0xfc,0xff,0x0f,0xfc,0x1f,0x00,0xf8,0xff,0x01,0xfe,0x0f,0x00,0x00,0x00,0xc0,0xff,0x0f,0x00,0xfc,0xff,0xff,0xff,0x07,0x00,0xfc,0xff,0xff,0xff,0x03,0x00,0xfc,0xff,0xff,0xff,0x01,0x00,0xfc,0xff,0xff,0xff,0x00,0x00,0xfc,0xff,0xff,0x7f,0x00,0x00,0xfc,0xff,0xff,0x1f,0x00,0x00,0xfc,0xff,0xff,0x07,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
#endif

#if defined(DISPLAY_16X2)
    static byte duco_logo[] = {0x1E, 0x01, 0x1D, 0x05, 0x1D, 0x01, 0x1E, 0x00};
    static byte check_mark[] = {0x00, 0x00, 0x00, 0x01, 0x02,0x14, 0x08, 0x00};
    static byte kh[] = {0x08, 0x0A, 0x0C, 0x0A, 0x00, 0x0A, 0x0E, 0x0A};
    static byte msec[] = {0x0A, 0x15, 0x11, 0x06, 0x08, 0x04, 0x02, 0x0C};
#endif

  #if defined(DISPLAY_SSD1306)
    void drawStrMultiline(const char *msg, int xloc, int yloc) {
     //https://github.com/olikraus/u8g2/discussions/1479
     int dspwidth = u8g2.getDisplayWidth();    
     int strwidth = 0;          
     char glyph[2]; glyph[1] = 0;
  
     for (const char *ptr = msg, *lastblank = NULL; *ptr; ++ptr) {
        while (xloc == 0 && *msg == ' ')
           if (ptr == msg++) ++ptr;                     
  
        glyph[0] = *ptr;
        strwidth += u8g2.getStrWidth(glyph);                   
        if (*ptr == ' ')  lastblank = ptr;                 
        else ++strwidth;                       
  
        if (xloc + strwidth > dspwidth) {                       
           int starting_xloc = xloc;
           while (msg < (lastblank ? lastblank : ptr)) {                       
              glyph[0] = *msg++;
              xloc += u8g2.drawStr(xloc, yloc, glyph); 
           }
  
           strwidth -= xloc - starting_xloc;                       
           yloc += u8g2.getMaxCharHeight();                      
           xloc = 0; lastblank = NULL;
        }
     }
     while (*msg) {                        
        glyph[0] = *msg++;
        xloc += u8g2.drawStr(xloc, yloc, glyph);
     }
    }
#endif

#if defined(DISPLAY_SSD1306) || defined(DISPLAY_16X2)
    void screen_setup() {
      // Ran during setup()
      // Abstraction layer: screen initialization

      #if defined(DISPLAY_SSD1306)
          u8g2.begin();
          u8g2.clearBuffer();
          u8g2.setFontMode(1);
          u8g2.setBitmapMode(1);
          u8g2.sendBuffer();
      #endif

      #if defined(DISPLAY_16X2)
          lcd.begin(16, 2);
          lcd.createChar(0, duco_logo);
          lcd.createChar(1, check_mark);
          lcd.createChar(2, kh);
          lcd.createChar(3, msec);
          lcd.home();
          lcd.clear();
      #endif
    }


    void display_boot() {
      // Abstraction layer: compilation time, features, etc.

      #if defined(DISPLAY_16X2)
          lcd.clear();
          #if defined(ESP8266)
            lcd.print("ESP8266 ");
          #elif defined(CONFIG_FREERTOS_UNICORE)
            lcd.print("ESP32S2 ");
          #else
            lcd.print("ESP32 ");
          #endif
          #if defined(ESP8266)
            lcd.print(String(ESP.getCpuFreqMHz()).c_str());
          #else
            lcd.print(String(getCpuFrequencyMhz()).c_str());
          #endif
          lcd.print(" MHz");

          lcd.setCursor(0, 1);
          lcd.print(__DATE__);
      #endif

      #if defined(DISPLAY_SSD1306)
          u8g2.clearBuffer();
          
          u8g2.setFont(u8g2_font_profont15_tr);
          u8g2.setCursor(2, 13);
          #if defined(ESP8266)
            u8g2.print("ESP8266 ");
          #elif defined(CONFIG_FREERTOS_UNICORE)
            u8g2.print("ESP32S2/C3 ");
          #else
            u8g2.print("ESP32 ");
          #endif
  
          #if defined(ESP8266)
            u8g2.print(String(ESP.getCpuFreqMHz()).c_str());
          #else
            u8g2.print(String(getCpuFrequencyMhz()).c_str());
          #endif
          u8g2.print(" MHz");
  
          u8g2.setFont(u8g2_font_profont10_tr);
          u8g2.drawLine(1, 27, 126, 27);
          u8g2.setCursor(2, 24);
          u8g2.print("Compiled ");
          u8g2.print(__DATE__);
          
          
          u8g2.drawStr(2, 37, "Features:");
          u8g2.setCursor(2, 46);
          String features_str = "OTA ";
          #if defined(USE_LAN)
            features_str += "LAN ";
          #endif
          #if defined(LED_BLINKING)
            features_str += "Blink ";
          #endif
          #if defined(SERIAL_PRINTING)
            features_str += "Serial ";
          #endif
          #if defined(WEB_DASHBOARD)
            features_str += "Webserver ";
          #endif
          #if defined(DISPLAY_16X2)
            features_str += "LCD16X2 ";
          #endif
          #if defined(DISPLAY_SSD1306)
            features_str += "SSD1306 ";
          #endif
          #if defined(USE_INTERNAL_SENSOR)
            features_str += "Int. sensor ";
          #endif
          #if defined(USE_DS18B20)
            features_str += "DS18B20 ";
          #endif
          #if defined(USE_DHT)
            features_str += "DHT ";
          #endif
          #if defined(USE_HSU07M)
            features_str += "HSU07M ";
          #endif
          drawStrMultiline(features_str.c_str(), 2, 46);
          u8g2.sendBuffer();
      #endif
    }

    void display_info(String message) {
      // Abstraction layer: info screens (setups)
      
      #if defined(DISPLAY_SSD1306)
          u8g2.clearBuffer();
          u8g2.drawXBMP(-1, 3, 41, 45, image_duco_logo_big_bits);
          u8g2.setFont(u8g2_font_t0_16b_tr);
          #if defined(ESP8266)
              u8g2.drawStr(42, 27, "ESP8266");
          #elif defined(CONFIG_FREERTOS_UNICORE)
              u8g2.drawStr(42, 27, "ESP32S2/C3");
          #else
              u8g2.drawStr(42, 27, "ESP32");
          #endif
          u8g2.setFont(u8g2_font_t0_13b_tr);
          u8g2.drawStr(41, 14, "Duino-Coin");
          u8g2.setFont(u8g2_font_6x10_tr);
          u8g2.drawStr(98, 36, "MINER");
          u8g2.setFont(u8g2_font_6x13_tr);
          u8g2.drawStr(1, 60, message.c_str());
          u8g2.setFont(u8g2_font_5x8_tr);
          u8g2.drawStr(42, 46, "www.duinocoin.com");
          u8g2.setFont(u8g2_font_4x6_tr);
          u8g2.drawStr(116, 14, String(SOFTWARE_VERSION).c_str());
          u8g2.sendBuffer();
      #endif

      #if defined(DISPLAY_16X2)
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.write(0);
          lcd.print(" Duino-Coin ");
          lcd.print(SOFTWARE_VERSION);
          lcd.setCursor(0, 1);
          lcd.print(message);
      #endif
    }


    void display_mining_results(String hashrate, String accepted_shares, String total_shares, String uptime, String node, 
                                String difficulty, String sharerate, String ping, String accept_rate) {
      // Ran after each found share
      // Abstraction layer: displaying mining results
      Serial.println("Displaying mining results");
      
      #if defined(DISPLAY_SSD1306)
          u8g2.clearBuffer();
          u8g2.setFont(u8g2_font_profont10_tr);
          u8g2.drawStr(67, 26, "kH");
          if (hashrate.toFloat() < 100.0) {
            u8g2.setFont(u8g2_font_profont29_tr);
            u8g2.drawStr(2, 36, hashrate.c_str());
          } else {
            u8g2.setFont(u8g2_font_profont22_tr);
            u8g2.drawStr(3, 35, hashrate.c_str());
          }
          
          u8g2.setFont(u8g2_font_haxrcorp4089_tr);
          u8g2.drawStr(52, 12, node.c_str());
          
          u8g2.setFont(u8g2_font_t0_11_tr);
          u8g2.drawStr(17, 47, (accepted_shares + "/" + total_shares).c_str());
          u8g2.setFont(u8g2_font_5x7_tr);
          u8g2.drawStr(88, 47, ("(" + accept_rate + "%)").c_str());
          
          u8g2.setFont(u8g2_font_profont12_tr);
          u8g2.drawStr(20, 12, (ping + "ms").c_str());
          u8g2.drawStr(69, 36, "s");
          
          u8g2.setFont(u8g2_font_6x13_tr);
          u8g2.drawStr(125-u8g2.getStrWidth(uptime.c_str()), 61, uptime.c_str());
          
          u8g2.drawStr(85, 38, sharerate.c_str());
          u8g2.drawStr(85, 27, difficulty.c_str());
          u8g2.drawLine(67, 28, 75, 28);
          
          u8g2.drawXBMP(2, 38, 13, 10, image_check_contour_bits);
          
          if (WiFi.RSSI() > -40) {
            u8g2.drawXBMP(1, 0, 15, 16, image_network_4_bars_bits);
          } else if (WiFi.RSSI() > -60) {
            u8g2.drawXBMP(1, 0, 15, 16, image_network_3_bars_bits);
          } else if (WiFi.RSSI() > -75) {
            u8g2.drawXBMP(1, 0, 15, 16, image_network_2_bars_bits);
          } else {
            u8g2.drawXBMP(1, 0, 15, 16, image_network_1_bar_bits);
          }
          
          u8g2.setFont(u8g2_font_4x6_tr);
          u8g2.drawStr(14, 61, String(WiFi.localIP().toString()).c_str());
          u8g2.drawStr(14, 55, ("Duino-Coin " + String(SOFTWARE_VERSION)).c_str());
          u8g2.drawXBMP(2, 11, 9, 50, image_duco_logo_bits);
          u8g2.drawStr(111, 27, "diff");
          u8g2.drawStr(107, 38, "shr/s");
          
          u8g2.sendBuffer();
      #endif

      #if defined(DISPLAY_16X2)
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print(hashrate);
          lcd.setCursor(4,0);
          lcd.write(2); // kh

          lcd.setCursor(7, 0);
          lcd.print(difficulty);
          lcd.print(" diff");

          lcd.setCursor(0, 1);
          lcd.write(1); // checkmark
          lcd.print(accepted_shares);

          lcd.setCursor(7, 1);
          lcd.print(ping);
          lcd.write(3); // ms

          lcd.setCursor(12, 1);
          lcd.print(sharerate);
          lcd.print("s");
      #endif
    }
#endif

#endif
