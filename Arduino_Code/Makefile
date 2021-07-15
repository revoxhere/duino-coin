ARDUINO_BOARD?=uno
ARDUINO_BASE?=/usr/share/arduino
BUILD_DIR?=$(shell pwd)/build

default: all

$(BUILD_DIR)/$(ARDUINO_BOARD):
	mkdir -p $(BUILD_DIR)/$(ARDUINO_BOARD)

$(BUILD_DIR)/$(ARDUINO_BOARD)/Arduino_Code.ino.hex: $(BUILD_DIR)/$(ARDUINO_BOARD)
	arduino-builder -verbose -hardware $(ARDUINO_BASE)/hardware \
		-tools $(ARDUINO_BASE)/hardware/tools \
		-build-path $(BUILD_DIR)/$(ARDUINO_BOARD) \
		-fqbn arduino:avr:$(ARDUINO_BOARD) \
		Arduino_Code.ino

all: $(BUILD_DIR)/$(ARDUINO_BOARD)/Arduino_Code.ino.hex 

upload: $(BUILD_DIR)/$(ARDUINO_BOARD)/Arduino_Code.ino.hex
	@if [ -z "$(ARDUINO_PORT)" ]; then \
		echo "ARDUINO_PORT is not defined!"; \
		exit 1; \
	fi
	avrdude -c arduino -P $(ARDUINO_PORT) -p atmega328p -b 115200 -U flash:w:$(BUILD_DIR)/$(ARDUINO_BOARD)/Arduino_Code.ino.hex

clean:
	rm -rf $(BUILD_DIR)
