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

#if defined(ARDUINO_MINIMA) || defined(ARDUINO_UNOWIFIR4) || defined(ARDUINO_PORTENTA_C33)

#include <cstring>

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

namespace impl
{

/**************************************************************************************
 * DEFINE
 **************************************************************************************/

#if defined(ARDUINO_MINIMA) || defined(ARDUINO_UNOWIFIR4)
# define BSP_FEATURE_BSP_MCU_INFO_POINTER_LOCATION            (0x407FB19C)
# define BSP_FEATURE_BSP_UNIQUE_ID_OFFSET                     (0x14)
# define BSP_FEATURE_BSP_UNIQUE_ID_POINTER                    ((*(uint32_t *) BSP_FEATURE_BSP_MCU_INFO_POINTER_LOCATION) \
                                                               +                                                         \
                                                               BSP_FEATURE_BSP_UNIQUE_ID_OFFSET)
#elif defined(ARDUINO_PORTENTA_C33)
# define BSP_FEATURE_BSP_UNIQUE_ID_POINTER                    (0x01008190U)
#else
# error "Your selected Renesas MCU is not supported"
#endif

/**************************************************************************************
 * CTOR/DTOR
 **************************************************************************************/

UniqueId16::UniqueId16()
{
  typedef struct st_bsp_unique_id
  {
    union
    {
      uint32_t unique_id_words[4];
      uint8_t  unique_id_bytes[16];
    };
  } bsp_unique_id_t;

  bsp_unique_id_t const * unique_id = (bsp_unique_id_t *) BSP_FEATURE_BSP_UNIQUE_ID_POINTER;
  memcpy(_unique_id, unique_id->unique_id_bytes, ID_SIZE);
}

/**************************************************************************************
 * NAMESPACE
 **************************************************************************************/

} /* impl */

#endif /* defined(ARDUINO_MINIMA) || defined(ARDUINO_UNOWIFIR4) || defined(ARDUINO_PORTENTA_C33) */
