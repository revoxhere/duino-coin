@echo off
set /p port=Enter port for the Arduino:
cd Arduino_Code
.\avrdude\avrdude.exe -c arduino -P %port% -p ATMEGA328P -b 115200 -U flash:w:avrminer.hex
PAUSE
EXIT