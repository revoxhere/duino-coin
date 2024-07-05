/**
 * This software is distributed under the terms of the MIT License.
 * Copyright (c) 2023 LXRobotics.
 * Author: Alexander Entinger <alexander.entinger@lxrobotics.com>
 * Contributors: https://github.com/107-systems/107-Arduino-UniqueId/graphs/contributors.
 */

/**************************************************************************************
 * INCLUDE
 **************************************************************************************/

#include "UniqueId16.h"

#if defined(ARDUINO_ARCH_ESP32)

#include <Arduino.h>

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

namespace impl
{

/**************************************************************************************
 * CTOR/DTOR
 **************************************************************************************/

UniqueId16::UniqueId16()
: _unique_id{0}
{
  size_t constexpr CHIP_ID_SIZE = 6;
  uint64_t const chipid = ESP.getEfuseMac();
  memcpy(_unique_id, &chipid, CHIP_ID_SIZE);
}

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

} /* impl */

#endif /* defined(ARDUINO_ARCH_ESP32) */
