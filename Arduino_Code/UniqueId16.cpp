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

#include <algorithm>

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

namespace impl
{

/**************************************************************************************
 * CTOR/DTOR
 **************************************************************************************/

#if !defined(ARDUINO_ARCH_SAMD) && !defined(ARDUINO_ARCH_RP2040) && !defined(ARDUINO_ARCH_ESP32)  && !defined(ARDUINO_ARCH_RENESAS) || defined(ARDUINO_ARCH_MBED)
# warning "No Unique ID support for your platform, defaulting to hard-coded ID"
UniqueId16::UniqueId16()
: _unique_id{0}
{ }
#endif

/**************************************************************************************
 * PUBLIC MEMBER FUNCTIONS
 **************************************************************************************/

UniqueId16 const & UniqueId16::instance()
{
  static UniqueId16 instance;
  return instance;
}

uint8_t UniqueId16::operator[](size_t const idx) const
{
  if (idx < ID_SIZE)
    return _unique_id[idx];
  else
    return 0;
}

UniqueId16::Array UniqueId16::operator()() const
{
  return value();
}

UniqueId16::Array UniqueId16::value() const
{
  Array uid;
  std::copy(std::begin(_unique_id),
            std::end  (_unique_id),
            std::begin(uid));
  return uid;
}

size_t UniqueId16::printTo(Print & p) const
{
  char msg[ID_SIZE * 2 + 1] = {0}; /* Reserve enough space for displaying ID including string 0 termination. */
  snprintf(msg, sizeof(msg), "%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X%0X",
    _unique_id[ 0], _unique_id[ 1], _unique_id[ 2], _unique_id[ 3],
    _unique_id[ 4], _unique_id[ 5], _unique_id[ 6], _unique_id[ 7],
    _unique_id[ 8], _unique_id[ 9], _unique_id[10], _unique_id[11],
    _unique_id[12], _unique_id[13], _unique_id[14], _unique_id[15]);

  return p.write(msg);
}

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

} /* impl */
