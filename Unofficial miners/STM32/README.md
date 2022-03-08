# Duino-Coin miner for STM32 chips family

- Use platform.io to open/build
- Edit platformio.ini file to setup your upload method
    - I'm uploading my via `serial` connected to A9/A10 pins
    - If you have board with bootloader use `upload_protocol = dfu` method  
- Use AVR_Miner as with any other Arduino board
- Tested on:
    - Bluepill (STM32F103) ~6000 H/s
    - Blackpill (STM32F401) ~13700 H/s
    - Blackpill (STM32F411) ~15500 H/s

Happy mining!:)

# Changelog

- 1.0   7/1/2022
    - base
- 1.1   7/25/2022
    - improved performance of SHA1 calculation ~22% (STM32F401 -> ~16800 H/s)
    - now can be build and deployed on AVR chips too (tested on Arduino NANO -> ~282 H/s)
    - switch to ArduinoUniqueID library for better compability
