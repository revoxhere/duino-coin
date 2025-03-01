// Copyright © Luiz Henrique Cassettari. All rights reserved.
// Licensed under the MIT license.

#pragma GCC optimize ("-Ofast")

#ifndef _ARDUINO_UNIQUE_ID_H_
#define _ARDUINO_UNIQUE_ID_H_

#include <Arduino.h>

#if defined(ARDUINO_ARCH_AVR)
#include <avr/boot.h>
#ifndef SIGRD
#define SIGRD 5
#endif
#elif defined(ARDUINO_ARCH_ESP8266)
#elif defined(ARDUINO_ARCH_ESP32)
#elif defined(ARDUINO_ARCH_SAM)
#elif defined(ARDUINO_ARCH_SAMD)
#elif defined(ARDUINO_ARCH_STM32)
#elif defined(TEENSYDUINO)
#elif defined(ARDUINO_ARCH_MBED_RP2040) || defined(ARDUINO_ARCH_RP2040)
//#include <pico/unique_id.h>
#elif defined(ARDUINO_ARCH_MEGAAVR)
#elif defined(NRF51_SERIES) || defined(NRF52_SERIES) || defined(NRF53_SERIES)
#else
#error "ArduinoUniqueID only works on AVR, SAM, SAMD, STM32, Teensy, megaAVR, nRF5 and ESP Architecture"
#endif

#if defined(ARDUINO_ARCH_AVR)

#if defined(__AVR_ATmega328PB__)
#define UniqueIDsize 10
#else
#define UniqueIDsize 9
#endif

#define UniqueIDbuffer UniqueIDsize

#elif defined(ARDUINO_ARCH_ESP8266)
#define UniqueIDsize 4
#define UniqueIDbuffer 8
#elif defined(ARDUINO_ARCH_ESP32)
#define UniqueIDsize 6
#define UniqueIDbuffer 8
#elif defined(ARDUINO_ARCH_SAM)
#define UniqueIDsize 16
#define UniqueIDbuffer 16
#elif defined(ARDUINO_ARCH_SAMD)
#define UniqueIDsize 16
#define UniqueIDbuffer 16
#elif defined(ARDUINO_ARCH_STM32)
#define UniqueIDsize 12
#define UniqueIDbuffer 12
#elif defined(ARDUINO_TEENSY40) || defined (ARDUINO_TEENSY41)
#define UniqueIDsize 8
#define UniqueIDbuffer 8
#elif defined(TEENSYDUINO)
#define UniqueIDsize 16
#define UniqueIDbuffer 16
#elif defined(ARDUINO_ARCH_MBED_RP2040) || defined(ARDUINO_ARCH_RP2040)
#define UniqueIDsize 32
#define UniqueIDbuffer 32
#elif defined(ARDUINO_ARCH_MEGAAVR)
#define UniqueIDsize 10
#define UniqueIDbuffer 10
#elif defined(NRF51_SERIES) || defined(NRF52_SERIES) || defined(NRF53_SERIES)
#define UniqueIDsize 8
#define UniqueIDbuffer 8
#endif

#define UniqueID8 (_UniqueID.id + UniqueIDbuffer - 8)
#define UniqueID (_UniqueID.id + UniqueIDbuffer - UniqueIDsize)

#define UniqueIDdump(stream)                      \
	{                                             \
		stream.print("UniqueID: ");       \
		for (size_t i = 0; i < UniqueIDsize; i++) \
		{                                         \
			if (UniqueID[i] < 0x10)               \
				stream.print("0");                \
			stream.print(UniqueID[i], HEX);       \
			stream.print(" ");                    \
		}                                         \
		stream.println();                         \
	}

#define UniqueID8dump(stream)                \
	{                                        \
		stream.print("UniqueID: ");  \
		for (size_t i = 0; i < 8; i++)       \
		{                                    \
			if (UniqueID8[i] < 0x10)         \
				stream.print("0");           \
			stream.print(UniqueID8[i], HEX); \
			stream.print(" ");               \
		}                                    \
		stream.println();                    \
	}

class ArduinoUniqueID
{
  public:
	ArduinoUniqueID();
	uint8_t id[UniqueIDbuffer];
};

extern ArduinoUniqueID _UniqueID;

#endif
