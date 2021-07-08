#include <Arduino.h>

// https://www.programmersought.com/article/60711848839/

/* Get the unique ID of the MCU */
void GetSTM32MCUID(uint32_t *id)
{
    if (id != NULL)
    {
#ifdef STM32F0
        int addr = 0x1FFFF7AC;
#elif defined(STM32F1)
        int addr = 0x1FFFF7E8;
#elif defined(STM32F2)
        int addr = 0x1FFF7A10;
#elif defined(STM32F3)
        int addr = 0x1FFFF7AC;
#elif defined(STM32F4)
        int addr = 0x1FFF7A10;
#elif defined(STM32F7)
        int addr = 0x1FF0F420;
#elif defined(STM32L0)
        int addr = 0x1FF80050;
#elif defined(STM32L1)
        int addr = 0x1FF80050;
#elif defined(STM32L4)
        int addr = 0x1FFF7590;
#elif defined(STM32H7)
        int addr = 0x1FF0F420;
#else
#error "Not supported MCU"
#endif
        id[0] = *(uint32_t *)(addr);
        id[1] = *(uint32_t *)(addr + 4);
        id[2] = *(uint32_t *)(addr + 8);
    }
}