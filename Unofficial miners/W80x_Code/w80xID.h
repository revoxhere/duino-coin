// Copyright (C) 2025 Duino-Coin Community
// SPDX-License-Identifier: MIT

#pragma GCC optimize ("-Ofast")

#ifndef _W80x_UNIQUE_ID_H_
#define _W80x_UNIQUE_ID_H_

#include <stdint.h>
#include "variant.h"

/* Detect variant of WinnerMicro board */
#if defined(_VARIANT_ARDUINO_W800_)
#define VARIANT 0x1
#elif defined(_VARIANT_ARDUINO_W801_)
#define VARIANT 0x2
#elif defined(_VARIANT_ARDUINO_W802_)
#define VARIANT 0x3
#elif defined(_VARIANT_ARDUINO_W806_)
#define VARIANT 0x4
#elif defined(_VARIANT_ARDUINO_Air101_)
#define VARIANT 0x10
#elif defined(_VARIANT_ARDUINO_Air103_)
#define VARIANT 0x11
#else
#error "w80xID requires the board to be WinnerMicro W80x, Air101 or Air103"
#endif

#define UniqueID8 (_UniqueID.id + UniqueIDbuffer - 8)

/*
 * Stores variant information of the board
 *
 * Use the last byte for variant information:
 * - 0x0: Unknown
 * - 0x1: WinnerMicro W800
 * - 0x2: WinnerMicro W801
 * - 0x3: WinnerMicro W802
 * - 0x4: WinnerMicro W806
 * - 0x10: Air101
 * - 0x11: Air103
 *
 * The String W80x is provided as the first 4 bytes.
 */
#define UniqueIDbuffer 8

class W80xUniqueID
{
  public:
	W80xUniqueID();
	uint8_t id[UniqueIDbuffer];
};

extern W80xUniqueID _UniqueID;

#endif // _W80x_UNIQUE_ID_H_
