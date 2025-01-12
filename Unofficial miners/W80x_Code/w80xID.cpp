// Copyright (C) 2025 Duino-Coin Community
// SPDX-License-Identifier: MIT

#pragma GCC optimize ("-Ofast")

#include "w80xID.h"

W80xUniqueID::W80xUniqueID()
{
  id[0] = 0x57; // W
  id[1] = 0x38; // 8
  id[2] = 0x30; // 0
  id[3] = 0x78; // x
  id[4] = 0x00;
  id[5] = 0x00;
  id[6] = 0x00;
  id[7] = VARIANT;
}

W80xUniqueID _UniqueID;
