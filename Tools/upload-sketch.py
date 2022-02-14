import sys
import subprocess
from configparser import ConfigParser

MINER_VER = '3.0'  # Version number
RESOURCES_DIR = 'AVRMiner_' + str(MINER_VER) + '_resources'

config = ConfigParser()

print('Checking for arduino-cli…')
try:
    subprocess.call(['arduino-cli'])
except Exception as e:
    print('arduino-cli is not installed. Please follow this tutorial https://siytek.com/arduino-cli-raspberry-pi/ and then try the script again.')
    sys.exit()

print('arduino-cli is installed…')

try:
    print('Fetching config…')
    config.read(RESOURCES_DIR + '/Miner_config.cfg')
    avrport = config['arduminer']['avrport']
except Exception as e:
    print(f'Cannot get config: {e}')
    sys.exit()

try:
    subprocess.call('arduino-cli compile --fqbn arduino:avr:uno Arduino_Code/Arduino_Code.ino'.split(' '))
except Exception as e:
    print(f'Cannot compile: {e}')
    sys.exit()

ports = avrport.split(',')
for port in ports:
    print(f'Uploading to {port}')
    try:
        subprocess.call(f'arduino-cli upload -p {port} --fqbn arduino:avr:uno Arduino_Code/Arduino_Code.ino'.split(' '))
    except Exception as e:
        print(f'Error uploading to {port}: {e}')
        sys.exit()
