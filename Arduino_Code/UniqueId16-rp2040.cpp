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

#if defined(ARDUINO_ARCH_RP2040) && !defined(ARDUINO_ARCH_MBED)

#include <cstring>
#include <pico/unique_id.h>

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
  pico_unique_board_id_t pico_id;
  pico_get_unique_board_id(&pico_id);

  memcpy(_unique_id, pico_id.id, PICO_UNIQUE_BOARD_ID_SIZE_BYTES);
}

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

} /* impl */

#endif /* defined(ARDUINO_ARCH_RP2040) && !defined(ARDUINO_ARDUINO_NANO_RP2040_CONNECT) */
