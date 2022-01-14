// Copyright © Luiz Henrique Cassettari. All rights reserved.
// Licensed under the MIT license.

#pragma GCC optimize ("-Ofast")

#include "uniqueID.h"

ArduinoUniqueID::ArduinoUniqueID()
{
#if defined(ARDUINO_ARCH_AVR)
  for (size_t i = 0; i < UniqueIDsize; i++)
  {
    id[i] = boot_signature_byte_get(0x0E + i + (UniqueIDsize == 9 && i > 5 ? 1 : 0));
  }
#elif defined(ARDUINO_ARCH_ESP8266)
  uint32_t chipid = ESP.getChipId();
  id[0] = 0;
  id[1] = 0;
  id[2] = 0;
  id[3] = 0;
  id[4] = chipid >> 24;
  id[5] = chipid >> 16;
  id[6] = chipid >> 8;
  id[7] = chipid;

#elif defined(ARDUINO_ARCH_ESP32)
  uint64_t chipid = ESP.getEfuseMac();
  id[0] = 0;
  id[1] = 0;
  id[2] = chipid;
  id[3] = chipid >> 8;
  id[4] = chipid >> 16;
  id[5] = chipid >> 24;
  id[6] = chipid >> 32;
  id[7] = chipid >> 40;

#elif defined(ARDUINO_ARCH_SAM)
  uint16_t status ;
  /* Send the Start Read unique Identifier command (STUI) by writing the Flash Command Register with the STUI command.*/
  EFC1->EEFC_FCR = (0x5A << 24) | EFC_FCMD_STUI;
  do
  {
    status = EFC1->EEFC_FSR ;
  } while ( (status & EEFC_FSR_FRDY) == EEFC_FSR_FRDY ) ;

  /* The Unique Identifier is located in the first 128 bits of the Flash memory mapping. So, at the address 0x400000-0x400003. */
  uint32_t pdwUniqueID[4];
  pdwUniqueID[0] = *(uint32_t *)IFLASH1_ADDR;
  pdwUniqueID[1] = *(uint32_t *)(IFLASH1_ADDR + 4);
  pdwUniqueID[2] = *(uint32_t *)(IFLASH1_ADDR + 8);
  pdwUniqueID[3] = *(uint32_t *)(IFLASH1_ADDR + 12);
  for (uint8_t i = 0; i < 4; i++)
  {
    id[i*4+0] = (uint8_t)(pdwUniqueID[i] >> 24);
    id[i*4+1] = (uint8_t)(pdwUniqueID[i] >> 16);
    id[i*4+2] = (uint8_t)(pdwUniqueID[i] >> 8);
    id[i*4+3] = (uint8_t)(pdwUniqueID[i] >> 0);
  }

  /* To stop the Unique Identifier mode, the user needs to send the Stop Read unique Identifier
  command (SPUI) by writing the Flash Command Register with the SPUI command. */
  EFC1->EEFC_FCR = (0x5A << 24) | EFC_FCMD_SPUI ;

  /* When the Stop read Unique Unique Identifier command (SPUI) has been performed, the
  FRDY bit in the Flash Programming Status Register (EEFC_FSR) rises. */
  do
  {
    status = EFC1->EEFC_FSR ;
  } while ( (status & EEFC_FSR_FRDY) != EEFC_FSR_FRDY );

#elif defined(ARDUINO_ARCH_SAMD)

#if defined (__SAMD51__)
  // SAMD51 from section 9.6 of the datasheet
  #define SERIAL_NUMBER_WORD_0  *(volatile uint32_t*)(0x008061FC)
  #define SERIAL_NUMBER_WORD_1  *(volatile uint32_t*)(0x00806010)
  #define SERIAL_NUMBER_WORD_2  *(volatile uint32_t*)(0x00806014)
  #define SERIAL_NUMBER_WORD_3  *(volatile uint32_t*)(0x00806018)
#else
//#elif defined (__SAMD21E17A__) || defined(__SAMD21G18A__)  || defined(__SAMD21E18A__) || defined(__SAMD21J18A__)
  // SAMD21 from section 9.3.3 of the datasheet
  #define SERIAL_NUMBER_WORD_0  *(volatile uint32_t*)(0x0080A00C)
  #define SERIAL_NUMBER_WORD_1  *(volatile uint32_t*)(0x0080A040)
  #define SERIAL_NUMBER_WORD_2  *(volatile uint32_t*)(0x0080A044)
  #define SERIAL_NUMBER_WORD_3  *(volatile uint32_t*)(0x0080A048)
#endif

  uint32_t pdwUniqueID[4];
  pdwUniqueID[0] = SERIAL_NUMBER_WORD_0;
  pdwUniqueID[1] = SERIAL_NUMBER_WORD_1;
  pdwUniqueID[2] = SERIAL_NUMBER_WORD_2;
  pdwUniqueID[3] = SERIAL_NUMBER_WORD_3;

  for (uint8_t i = 0; i < 4; i++)
  {
    id[i*4+0] = (uint8_t)(pdwUniqueID[i] >> 24);
    id[i*4+1] = (uint8_t)(pdwUniqueID[i] >> 16);
    id[i*4+2] = (uint8_t)(pdwUniqueID[i] >> 8);
    id[i*4+3] = (uint8_t)(pdwUniqueID[i] >> 0);
  }

#elif defined(ARDUINO_ARCH_STM32)
  uint32_t pdwUniqueID[3];
  pdwUniqueID[0] = HAL_GetUIDw0();
  pdwUniqueID[1] = HAL_GetUIDw1();
  pdwUniqueID[2] = HAL_GetUIDw2();
  for (uint8_t i = 0; i < 3; i++)
  {
    id[i*4+0] = (uint8_t)(pdwUniqueID[i] >> 24);
    id[i*4+1] = (uint8_t)(pdwUniqueID[i] >> 16);
    id[i*4+2] = (uint8_t)(pdwUniqueID[i] >> 8);
    id[i*4+3] = (uint8_t)(pdwUniqueID[i] >> 0);
  }
#elif defined(ARDUINO_TEENSY40) || defined (ARDUINO_TEENSY41)
  uint32_t uid0 = HW_OCOTP_CFG0;
  uint32_t uid1 = HW_OCOTP_CFG1;
  id[0] = uid0 >> 24;
  id[1] = uid0 >> 16;
  id[2] = uid0 >> 8;
  id[3] = uid0;
  id[4] = uid1 >> 24;
  id[5] = uid1 >> 16;
  id[6] = uid1 >> 8;
  id[7] = uid1;
#elif defined(TEENSYDUINO)
  uint8_t mac[6];
  uint8_t sn[4];
  uint32_t num = 0;
  __disable_irq();
  #if defined(HAS_KINETIS_FLASH_FTFA) || defined(HAS_KINETIS_FLASH_FTFL)
    FTFL_FSTAT = FTFL_FSTAT_RDCOLERR | FTFL_FSTAT_ACCERR | FTFL_FSTAT_FPVIOL;
    FTFL_FCCOB0 = 0x41;
    FTFL_FCCOB1 = 15;
    FTFL_FSTAT = FTFL_FSTAT_CCIF;
    while (!(FTFL_FSTAT & FTFL_FSTAT_CCIF)) ; // wait
    num = *(uint32_t *)&FTFL_FCCOB7;
  #elif defined(HAS_KINETIS_FLASH_FTFE)
    kinetis_hsrun_disable();
    FTFL_FSTAT = FTFL_FSTAT_RDCOLERR | FTFL_FSTAT_ACCERR | FTFL_FSTAT_FPVIOL;
    *(uint32_t *)&FTFL_FCCOB3 = 0x41070000;
    FTFL_FSTAT = FTFL_FSTAT_CCIF;
    while (!(FTFL_FSTAT & FTFL_FSTAT_CCIF)) ; // wait
    num = *(uint32_t *)&FTFL_FCCOBB;
    kinetis_hsrun_enable();
  #endif
  __enable_irq();
  sn[0] = num >> 24;
  sn[1] = num >> 16;
  sn[2] = num >> 8;
  sn[3] = num;
  mac[0] = 0x04;
  mac[1] = 0xE9;
  mac[2] = 0xE5;
  mac[3] = sn[1];
  mac[4] = sn[2];
  mac[5] = sn[3];
  id[0] = SIM_UIDML >> 24;
  id[1] = SIM_UIDML >> 16;
  id[2] = SIM_UIDML >> 8;
  id[3] = SIM_UIDML;
  id[4] = SIM_UIDL >> 24;
  id[5] = SIM_UIDL >> 16;
  id[6] = 0x40; // marked as version v4, but this uuid is not random based !!!
  id[7] = SIM_UIDL >> 8;
  id[8] = 0x80; //variant
  id[9] = SIM_UIDL;
  id[10] = mac[0];
  id[11] = mac[1];
  id[12] = mac[2];
  id[13] = mac[3];
  id[14] = mac[4];
  id[15] = mac[5];
#elif defined(ARDUINO_ARCH_MBED_RP2040)
  getUniqueSerialNumber(id);
#elif defined(ARDUINO_ARCH_MEGAAVR)
  id[0] = SIGROW.SERNUM0;
  id[1] = SIGROW.SERNUM1;
  id[2] = SIGROW.SERNUM2;
  id[3] = SIGROW.SERNUM3;
  id[4] = SIGROW.SERNUM4;
  id[5] = SIGROW.SERNUM5;
  id[6] = SIGROW.SERNUM6;
  id[7] = SIGROW.SERNUM7;
  id[8] = SIGROW.SERNUM8;
  id[9] = SIGROW.SERNUM9;
#endif
}

ArduinoUniqueID _UniqueID;
