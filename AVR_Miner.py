#!/usr/bin/env python3
##########################################
# Duino-Coin Python AVR Miner (v2.49)
# https://github.com/revoxhere/duino-coin
# Distributed under MIT license
# © Duino-Coin Community 2019-2021
##########################################
# Import libraries
import sys
from configparser import ConfigParser
from datetime import datetime
from json import load as jsonload
from locale import LC_ALL, getdefaultlocale, getlocale, setlocale
from os import _exit, execl, mkdir
from os import name as osname
from os import path
from os import system as ossystem
from pathlib import Path
from platform import system
from re import sub
from signal import SIGINT, signal
from socket import socket
from subprocess import DEVNULL, Popen, check_call
from threading import Thread as thrThread
from threading import Lock
from time import ctime, sleep, strptime, time
from statistics import mean
import select
import pip

def install(package):
    pip.main(["install",  package])

def now():
    # Return datetime object
    return datetime.now()


try:
    # Check if pyserial is installed
    from serial import Serial
    import serial.tools.list_ports
except ModuleNotFoundError:
    print(
        now().strftime('%H:%M:%S ')
        + 'Pyserial is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "pyserial" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install('pyserial')

try:
    # Check if colorama is installed
    from colorama import Back, Fore, Style, init
except ModuleNotFoundError:
    print(
        now().strftime('%H:%M:%S ')
        + 'Colorama is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "colorama" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install('colorama')

try:
    # Check if requests is installed
    import requests
except ModuleNotFoundError:
    print(
        now().strftime('%H:%M:%S ')
        + 'Requests is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "requests" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install('requests')

try:
    # Check if pypresence is installed
    from pypresence import Presence
except ModuleNotFoundError:
    print(
        now().strftime('%H:%M:%S ')
        + 'Pypresence is not installed. '
        + 'Miner will try to install it. '
        + 'If it fails, please manually install "pypresence" python3 package.'
        + '\nIf you can\'t install it, use the Minimal-PC_Miner.')
    install('pypresence')

# Global variables
MINER_VER = '2.49'  # Version number
SOCKET_TIMEOUT = 15
AVR_TIMEOUT = 3  # diff 5(*100) / 190 H/s = 2.6, rounded to nearest int
BAUDRATE = 115200
RESOURCES_DIR = 'AVRMiner_' + str(MINER_VER) + '_resources'
shares = [0, 0]
hashrate_mean = []
diff = 0
donator_running = False
job = ''
debug = 'n'
rig_identifier = 'None'
# Serverip file
server_ip_file = ('https://raw.githubusercontent.com/'
                  + 'revoxhere/'
                  + 'duino-coin/gh-pages/serverip.txt')
donation_level = 0
hashrate = 0
config = ConfigParser()
thread_lock = Lock()

# Create resources folder if it doesn't exist
if not path.exists(RESOURCES_DIR):
    mkdir(RESOURCES_DIR)

# Check if languages file exists
if not Path(RESOURCES_DIR + '/langs.json').is_file():
    url = ('https://raw.githubusercontent.com/'
           + 'revoxhere/'
           + 'duino-coin/master/Resources/'
           + 'AVR_Miner_langs.json')
    r = requests.get(url)
    with open(RESOURCES_DIR + '/langs.json', 'wb') as f:
        f.write(r.content)

# Load language file
with open(RESOURCES_DIR + '/langs.json', 'r', encoding='utf8') as lang_file:
    lang_file = jsonload(lang_file)

# OS X invalid locale hack
if system() == 'Darwin':
    if getlocale()[0] is None:
        setlocale(LC_ALL, 'en_US.UTF-8')

# Check if miner is configured, if it isn't, autodetect language
try:
    if not Path(RESOURCES_DIR + '/Miner_config.cfg').is_file():
        locale = getdefaultlocale()[0]
        if locale.startswith('es'):
            lang = 'spanish'
        elif locale.startswith('sk'):
            lang = 'slovak'
        elif locale.startswith('ru'):
            lang = 'russian'
        elif locale.startswith('pl'):
            lang = 'polish'
        elif locale.startswith('fr'):
            lang = 'french'
        elif locale.startswith('tr'):
            lang = 'turkish'
        elif locale.startswith('pt'):
            lang = 'portugese'
        elif locale.startswith('zh'):
            lang = 'chinese_simplified'
        else:
            lang = 'english'
    else:
        try:
            # Read language from configfile
            config.read(RESOURCES_DIR + '/Miner_config.cfg')
            lang = config['arduminer']['language']
        except Exception:
            # If it fails, fallback to english
            lang = 'english'
except:
    lang = 'english'


def get_string(string_name):
    # Get string form language file
    if string_name in lang_file[lang]:
        return lang_file[lang][string_name]
    elif string_name in lang_file['english']:
        return lang_file['english'][string_name]
    else:
        return 'String not found: ' + string_name


def debug_output(text):
    # Debug output
    if debug == 'y':
        print(
            Style.RESET_ALL
            + now().strftime(Style.DIM + '%H:%M:%S.%f ')
            + 'DEBUG: '
            + str(text))


def title(title):
    # Window title
    if osname == 'nt':
        # Windows systems
        ossystem('title ' + title)
    else:
        # Most standard terminals
        print('\33]0;' + title + '\a', end='')
        sys.stdout.flush()


def connect():
    # Server connection
    global server_ip
    global server_port
    serverVersion = 0
    while True:
        try:
            try:
                socket.close()
            except Exception:
                pass
            debug_output('Connecting to '
                         + str(server_ip)
                         + str(':')
                         + str(server_port))
            soc = socket()
            soc.settimeout(SOCKET_TIMEOUT)

            # Establish socket connection to the server
            soc.connect(
                (str(server_ip),
                    int(server_port)))

            # Get server version
            ready = select.select([soc], [], [], SOCKET_TIMEOUT)
            if ready[0]:
                serverVersion = soc.recv(10).decode().rstrip('\n')
                debug_output('Server version: ' + serverVersion)
            else:
                raise Exception("No ver received")

            if float(serverVersion) <= float(MINER_VER):
                # If miner is up-to-date, display a message and continue
                pretty_print(
                    'net0',
                    get_string('connected')
                    + Style.NORMAL
                    + Fore.RESET
                    + get_string('connected_server')
                    + str(serverVersion)
                    + ')',
                    'success')
                break
            else:
                pretty_print(
                    'sys0',
                    ' Miner is outdated (v'
                    + MINER_VER
                    + ') -'
                    + get_string('server_is_on_version')
                    + serverVersion
                    + Style.NORMAL
                    + Fore.RESET
                    + get_string('update_warning'),
                    'warning')
                sleep(10)
                break
        except Exception as e:
            pretty_print(
                'net0',
                get_string('connecting_error')
                + Style.NORMAL
                + ' ('
                + str(e)
                + ')',
                'error')
            debug_output('Connection error: ' + str(e))
            sleep(10)
    return soc


def handler(signal_received, frame):
    # SIGINT handler
    pretty_print(
        'sys0',
        get_string('sigint_detected')
        + Style.NORMAL
        + Fore.RESET
        + get_string('goodbye'),
        'warning')
    try:
        # Close previous socket connection (if any)
        socket.close()
    except Exception:
        pass
    _exit(0)


# Enable signal handler
signal(SIGINT, handler)


def load_config():
    # Config loading section
    global username
    global donation_level
    global avrport
    global debug
    global rig_identifier

    # Initial configuration section
    if not Path(str(RESOURCES_DIR) + '/Miner_config.cfg').is_file():
        print(
            Style.BRIGHT
            + get_string('basic_config_tool')
            + RESOURCES_DIR
            + get_string('edit_config_file_warning'))

        print(
            Style.RESET_ALL
            + get_string('dont_have_account')
            + Fore.YELLOW
            + get_string('wallet')
            + Fore.RESET
            + get_string('register_warning'))

        username = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + get_string('ask_username')
            + Fore.RESET
            + Style.BRIGHT)

        print(Style.RESET_ALL
              + Fore.YELLOW
              + get_string('ports_message'))
        portlist = serial.tools.list_ports.comports(include_links=True)
        for port in portlist:
            print(Style.RESET_ALL
                  + Style.BRIGHT
                  + Fore.RESET
                  + '  '
                  + str(port))
        print(Style.RESET_ALL
              + Fore.YELLOW
              + get_string('ports_notice'))

        port_names = []
        for port in portlist:
            port_names.append(port.device)

        avrport = ''
        while True:
            current_port = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + get_string('ask_avrport')
                + Fore.RESET
                + Style.BRIGHT)

            if current_port in port_names:
                avrport += current_port
                confirmation = input(
                    Style.RESET_ALL
                    + Fore.YELLOW
                    + get_string('ask_anotherport')
                    + Fore.RESET
                    + Style.BRIGHT)

                if confirmation == 'y' or confirmation == 'Y':
                    avrport += ','
                else:
                    break
            else:
                print(Style.RESET_ALL
                      + Fore.RED
                      + 'Please enter a valid COM port from the list above')

        rig_identifier = input(
            Style.RESET_ALL
            + Fore.YELLOW
            + get_string('ask_rig_identifier')
            + Fore.RESET
            + Style.BRIGHT)
        if rig_identifier == 'y' or rig_identifier == 'Y':
            rig_identifier = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + get_string('ask_rig_name')
                + Fore.RESET
                + Style.BRIGHT)
        else:
            rig_identifier = 'None'

        donation_level = '0'
        if osname == 'nt' or osname == 'posix':
            donation_level = input(
                Style.RESET_ALL
                + Fore.YELLOW
                + get_string('ask_donation_level')
                + Fore.RESET
                + Style.BRIGHT)

        # Check wheter donation_level is correct
        donation_level = sub(r'\D', '', donation_level)
        if donation_level == '':
            donation_level = 1
        if float(donation_level) > int(5):
            donation_level = 5
        if float(donation_level) < int(0):
            donation_level = 0

        # Format data
        config['arduminer'] = {
            'username': username,
            'avrport': avrport,
            'donate': donation_level,
            'language': lang,
            'identifier': rig_identifier,
            'debug': 'n'}

        # Write data to file
        with open(str(RESOURCES_DIR)
                  + '/Miner_config.cfg', 'w') as configfile:
            config.write(configfile)

        avrport = avrport.split(',')
        print(Style.RESET_ALL + get_string('config_saved'))

    else:  # If config already exists, load from it
        config.read(str(RESOURCES_DIR) + '/Miner_config.cfg')
        username = config['arduminer']['username']
        avrport = config['arduminer']['avrport']
        avrport = avrport.split(',')
        donation_level = config['arduminer']['donate']
        debug = config['arduminer']['debug']
        rig_identifier = config['arduminer']['identifier']


def greeting():
    # greeting message depending on time
    global greeting
    print(Style.RESET_ALL)

    current_hour = strptime(ctime(time())).tm_hour

    if current_hour < 12:
        greeting = get_string('greeting_morning')
    elif current_hour == 12:
        greeting = get_string('greeting_noon')
    elif current_hour > 12 and current_hour < 18:
        greeting = get_string('greeting_afternoon')
    elif current_hour >= 18:
        greeting = get_string('greeting_evening')
    else:
        greeting = get_string('greeting_back')

    # Startup message
    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Fore.YELLOW
        + Style.BRIGHT
        + get_string('banner')
        + Style.RESET_ALL
        + Fore.MAGENTA
        + ' (v'
        + str(MINER_VER)
        + ') '
        + Fore.RESET
        + '2019-2021')

    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Style.NORMAL
        + Fore.MAGENTA
        + 'https://github.com/revoxhere/duino-coin')

    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Style.NORMAL
        + Fore.RESET
        + get_string('avr_on_port')
        + Style.BRIGHT
        + Fore.YELLOW
        + ' '.join(avrport))

    if osname == 'nt' or osname == 'posix':
        print(
            Style.DIM
            + Fore.MAGENTA
            + ' ‖ '
            + Style.NORMAL
            + Fore.RESET
            + get_string('donation_level')
            + Style.BRIGHT
            + Fore.YELLOW
            + str(donation_level))
    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Style.NORMAL
        + Fore.RESET
        + get_string('algorithm')
        + Style.BRIGHT
        + Fore.YELLOW
        + 'DUCO-S1A @ AVR diff')

    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Style.NORMAL
        + Fore.RESET
        + get_string('rig_identifier')
        + Style.BRIGHT
        + Fore.YELLOW
        + rig_identifier)

    print(
        Style.DIM
        + Fore.MAGENTA
        + ' ‖ '
        + Style.NORMAL
        + Fore.RESET
        + str(greeting)
        + ', '
        + Style.BRIGHT
        + Fore.YELLOW
        + str(username)
        + '!\n')

    if donation_level > 0:
        if osname == 'nt':
            # Initial miner executable section
            if not Path(RESOURCES_DIR + '/donate_executable.exe').is_file():
                debug_output(
                    'OS is Windows, downloading developer donation executable')
                url = ('https://github.com/'
                       + 'revoxhere/'
                       + 'duino-coin/blob/useful-tools/'
                       + 'donateExecutableWindows.exe?raw=true')
                r = requests.get(url)
                with open(RESOURCES_DIR + '/donate_executable.exe', 'wb') as f:
                    f.write(r.content)
        elif osname == 'posix':
            # Initial miner executable section
            if not Path(RESOURCES_DIR + '/donate_executable').is_file():
                debug_output(
                    'OS is *nix, downloading developer donation executable')
                url = ('https://github.com/'
                       + 'revoxhere/'
                       + 'duino-coin/blob/useful-tools/'
                       + 'donateExecutableLinux?raw=true')
                r = requests.get(url)
                with open(RESOURCES_DIR + '/donate_executable', 'wb') as f:
                    f.write(r.content)


def donate():
    global donation_level
    global donator_running
    global donateExecutable

    if osname == 'nt':
        cmd = (
            'cd '
            + RESOURCES_DIR
            + '& donate_executable.exe '
            + '-o stratum+tcp://xmg.minerclaim.net:7008 '
            + '-u revox.donate '
            + '-p x -s 4 -e ')

    elif osname == 'posix':
        cmd = (
            'cd '
            + RESOURCES_DIR
            + '&& chmod +x donate_executable '
            + '&& ./donate_executable '
            + '-o stratum+tcp://xmg.minerclaim.net:7008 '
            + '-u revox.donate '
            + '-p x -s 4 -e ')

    if int(donation_level) <= 0:
        pretty_print(
            'sys0',
            Fore.YELLOW
            + get_string('free_network_warning')
            + get_string('donate_warning')
            + Fore.GREEN
            + 'https://duinocoin.com/donate'
            + Fore.YELLOW
            + get_string('learn_more_donate'),
            'warning')
        sleep(5)

    elif donator_running == False:
        if int(donation_level) == 5:
            cmd += '50'
        elif int(donation_level) == 4:
            cmd += '40'
        elif int(donation_level) == 3:
            cmd += '30'
        elif int(donation_level) == 2:
            cmd += '20'
        elif int(donation_level) == 1:
            cmd += '10'
        if int(donation_level) > 0:
            debug_output(get_string('starting_donation'))
            donator_running = True
            # Launch CMD as subprocess
            donateExecutable = Popen(
                cmd, shell=True, stderr=DEVNULL)
            pretty_print(
                'sys0',
                get_string('thanks_donation'),
                'warning')


def init_rich_presence():
    # Initialize Discord rich presence
    global RPC
    try:
        RPC = Presence(808056068113563701)
        RPC.connect()
        debug_output('Discord rich presence initialized')
    except Exception:
        # Discord not launched
        pass


def update_rich_presence():
    # Update rich presence status
    startTime = int(time())
    while True:
        try:
            RPC.update(
                details='Hashrate: ' + str(hashrate) + ' H/s',
                start=startTime,
                state='Acc. shares: '
                + str(shares[0])
                + '/'
                + str(shares[0] + shares[1]),
                large_image='ducol',
                large_text='Duino-Coin, '
                + 'a coin that can be mined with almost everything, '
                + 'including AVR boards',
                buttons=[
                    {'label': 'Learn more',
                     'url': 'https://duinocoin.com'},
                    {'label': 'Discord Server',
                     'url': 'https://discord.gg/k48Ht5y'}])
        except Exception:
            # Discord not launched
            pass
        # 15 seconds to respect Discord's rate limit
        sleep(15)


def pretty_print(message_type, message, state):
    # Print output messages in the DUCO 'standard'
    # Usb/net/sys background
    if message_type.startswith('net'):
        background = Back.BLUE
    elif message_type.startswith('usb'):
        background = Back.MAGENTA
    if message_type.startswith('sys'):
        background = Back.GREEN

    # Text color
    if state == 'success':
        color = Fore.GREEN
    elif state == 'warning':
        color = Fore.YELLOW
    else:
        color = Fore.RED

    with thread_lock:
        print(Style.RESET_ALL
              + Fore.WHITE
              + now().strftime(Style.DIM + '%H:%M:%S ')
              + Style.BRIGHT
              + background
              + ' '
              + message_type
              + ' '
              + Back.RESET
              + color
              + Style.BRIGHT
              + message
              + Style.NORMAL
              + Fore.RESET)


def mine_avr(com):
    # Mining section
    global hashrate
    global server_ip
    global server_port
    errorCounter = 0
    while True:
        # Grab server IP and port
        while True:
            try:
                # Use request to grab data from raw github file
                res = requests.get(server_ip_file, data=None)
                if res.status_code == 200:
                    # Read content and split into lines
                    content = (res.content.decode().splitlines())
                    server_ip = content[0]  # Line 1 = pool address
                    server_port = content[1]  # Line 2 = pool port
                    debug_output(
                        'Retrieved pool IP: '
                        + server_ip
                        + ':'
                        + str(server_port))
                    # Connect to the server
                    soc = connect()
                    break
            except Exception as e:
                # If there was an error with grabbing data from GitHub
                pretty_print(
                    'net'
                    + str(''.join(filter(str.isdigit, com))),
                    get_string('data_error')
                    + Style.NORMAL
                    + Fore.RESET
                    + ' (git err: '
                    + str(e)
                    + ')',
                    'error')
                debug_output('GitHub error: ' + str(e))
                sleep(10)

        pretty_print(
            'sys'
            + str(''.join(filter(str.isdigit, com))),
            get_string('mining_start')
            + Style.NORMAL
            + Fore.RESET
            + get_string('mining_algorithm')
            + str(com)
            + ')',
            'success')

        while True:
            while True:
                try:
                    # Send job request
                    debug_output(com + ': requested job from the server')
                    soc.sendall(
                        bytes(
                            'JOB,'
                            + str(username)
                            + ',AVR',
                            encoding='utf8'))

                    # Retrieve work
                    ready = select.select([soc], [], [], SOCKET_TIMEOUT)
                    if ready[0]:
                        job = soc.recv(103).decode()

                    # Split received data
                    job = job.rstrip('\n').split(',')

                    # Check if username is correct
                    if job[1] == 'This user doesn\'t exist':
                        pretty_print(
                            'net'
                            + str(''.join(filter(str.isdigit, com))),
                            get_string('mining_user')
                            + str(username)
                            + get_string('mining_not_exist')
                            + Style.NORMAL
                            + Fore.RESET
                            + get_string('mining_not_exist_warning'),
                            'error')
                        sleep(10)

                    # If job was received, continue
                    elif job[0] and job[1] and job[2]:
                        diff = int(job[2])
                        debug_output(com + ': job received: ' + ' '.join(job))
                        break
                except Exception as e:
                    pretty_print(
                        'net'
                        + str(''.join(filter(str.isdigit, com))),
                        get_string('connecting_error')
                        + Style.NORMAL
                        + Fore.RESET
                        + ' (net err: '
                        + str(e)
                        + ')',
                        'error')
                    debug_output('Connection error: ' + str(e))
                    sleep(5)
                    soc = connect()

            while True:
                while True:
                    try:
                        ser.close()
                    except:
                        pass

                    try:
                        ser = Serial(com,
                                     baudrate=BAUDRATE,
                                     timeout=AVR_TIMEOUT)
                        break
                    except Exception as e:
                        pretty_print(
                            'usb'
                            + str(''.join(filter(str.isdigit, com))),
                            get_string('board_connection_error')
                            + str(com)
                            + get_string('board_connection_error2')
                            + Style.NORMAL
                            + Fore.RESET
                            + ' (port connection err: '
                            + str(e)
                            + ')',
                            'error')
                    sleep(10)
                while True:
                    retry_counter = 0
                    while True:
                        if retry_counter >= 3:
                            break
                        try:
                            debug_output(com + ': sending job to AVR')
                            ser.write(
                                bytes(
                                    str(
                                        job[0]
                                        + ',' + job[1]
                                        + ',' + job[2]
                                        + ','), encoding='utf8'))


                            debug_output(com + ': reading result from AVR')
                            result = ser.read_until(b'\n').decode().strip()
                            ser.flush()

                            if "\x00" in result or not result:
                                raise Exception("Empty data received")

                            debug_output(com + ': retrieved result: '
                                         + str(result)
                                         + ' len: '
                                         + str(len(result)))
                            result = result.split(',')

                            try:
                                if result[0] and result[1]:
                                    break
                            except Exception as e:
                                debug_output(
                                    com + ': retrying reading data: ' + str(e))
                                retry_counter += 1
                        except Exception as e:
                            debug_output(
                                com + ': retrying sending data: ' + str(e))
                            retry_counter += 1

                    try:
                        ducos1result = result[0]
                        debug_output(
                            com + ': received result (' + str(ducos1result) + ')')

                        debug_output(
                            com + ': received time (' + str(result[1]) + ')')
                        # Convert AVR time to seconds
                        computetime = round(int(result[1]) / 1000000, 3)

                        # Calculate hashrate
                        hashrate_t = round(
                            int(result[0]) * 1000000 / int(result[1]), 2)
                        hashrate_mean.append(hashrate_t)
                        # Get average from the last hashrate measurements
                        hashrate = mean(hashrate_mean[-5:])
                        debug_output(
                            com +
                            ': calculated hashrate (' + str(hashrate_t) + ')'
                            + ' (avg:' + str(hashrate) + ')')

                        try:
                            chipID = result[2]
                            debug_output(
                                com + ': received chip ID (' + str(result[2]) + ')')
                            """ Check if user is using the latest Arduino code
                                    This is not used yet anywhere, but will soon be
                                    added as yet another a security measure in the
                                    Kolka security system for identifying AVR boards """
                            if not chipID.startswith('DUCOID'):
                                raise Exception('Wrong chipID string')
                        except Exception:
                            pretty_print(
                                'usb'
                                + str(''.join(filter(str.isdigit, com))),
                                ' Possible incorrect chip ID!'
                                + Style.NORMAL
                                + Fore.RESET
                                + ' This will cause problems with the future'
                                + ' release of Kolka security system',
                                'warning')
                            chipID = 'None'
                        break
                    except Exception as e:
                        pretty_print(
                            'usb'
                            + str(''.join(filter(str.isdigit, com))),
                            get_string('mining_avr_connection_error')
                            + Style.NORMAL
                            + Fore.RESET
                            + ' (err splitting avr data: '
                            + str(e)
                            + ')',
                            'warning')
                        debug_output(
                            com + ': error splitting data: ' + str(e))
                        sleep(1)

                try:
                    # Send result to the server
                    soc.sendall(
                        bytes(
                            str(ducos1result)
                            + ','
                            + str(hashrate)
                            + ',Official AVR Miner (DUCO-S1A) v'
                            + str(MINER_VER)
                            + ','
                            + str(rig_identifier)
                            + ','
                            + str(chipID),
                            encoding='utf8'))
                except Exception as e:
                    pretty_print(
                        'net'
                        + str(''.join(filter(str.isdigit, com))),
                        get_string('connecting_error')
                        + Style.NORMAL
                        + Fore.RESET
                        + ' ('
                        + str(e)
                        + ')',
                        'error')
                    debug_output(com + ': connection error: ' + str(e))
                    sleep(5)
                    soc = connect()

                while True:
                    try:
                        responsetimetart = now()
                        # Get feedback
                        ready = select.select(
                            [soc], [], [], SOCKET_TIMEOUT)
                        if ready[0]:
                            feedback = soc.recv(48).decode().rstrip('\n')
                        responsetimestop = now()
                        # Measure server ping
                        time_delta = (responsetimestop -
                                      responsetimetart).microseconds
                        ping = round(time_delta / 1000)
                        debug_output(com + ': successfully retrieved feedback: '
                                     + str(feedback)
                                     + ' with ping: '
                                     + str(ping))
                        break
                    except Exception as e:
                        pretty_print(
                            'net'
                            + str(''.join(filter(str.isdigit, com))),
                            get_string('connecting_error')
                            + Style.NORMAL
                            + Fore.RESET
                            + ' (err parsing response: '
                            + str(e)
                            + ')',
                            'error')
                        debug_output(com + ': error parsing response: '
                                     + str(e))
                        sleep(5)
                        soc = connect()

                if feedback == 'GOOD':
                    # If result was correct
                    shares[0] += 1
                    title(
                        get_string('duco_avr_miner')
                        + str(MINER_VER)
                        + ') - '
                        + str(shares[0])
                        + '/'
                        + str(shares[0] + shares[1])
                        + get_string('accepted_shares'))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + '%H:%M:%S ')
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + ' usb'
                            + str(''.join(filter(str.isdigit, com)))
                            + ' '
                            + Back.RESET
                            + Fore.GREEN
                            + ' ✓'
                            + get_string('accepted')
                            + Fore.RESET
                            + str(int(shares[0]))
                            + '/'
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + ' ('
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + '%)'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' ∙ '
                            + str('%01.3f' % float(computetime))
                            + 's'
                            + Style.NORMAL
                            + ' ∙ '
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(round(hashrate))
                            + ' H/s'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' @ diff '
                            + str(diff)
                            + ' ∙ '
                            + Fore.CYAN
                            + 'ping '
                            + str('%03.0f' % int(ping))
                            + 'ms')

                elif feedback == 'BLOCK':
                    # If block was found
                    shares[0] += 1
                    title(
                        get_string('duco_avr_miner')
                        + str(MINER_VER)
                        + ') - '
                        + str(shares[0])
                        + '/'
                        + str(shares[0] + shares[1])
                        + get_string('accepted_shares'))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + '%H:%M:%S ')
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + ' usb'
                            + str(''.join(filter(str.isdigit, com)))
                            + ' '
                            + Back.RESET
                            + Fore.CYAN
                            + ' ✓'
                            + get_string('block_found')
                            + Fore.RESET
                            + str(int(shares[0]))
                            + '/'
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + ' ('
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + '%)'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' ∙ '
                            + str('%01.3f' % float(computetime))
                            + 's'
                            + Style.NORMAL
                            + ' ∙ '
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(int(hashrate))
                            + ' H/s'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' @ diff '
                            + str(diff)
                            + ' ∙ '
                            + Fore.CYAN
                            + 'ping '
                            + str('%02.0f' % int(ping))
                            + 'ms')

                else:
                    # If result was incorrect
                    shares[1] += 1
                    title(
                        get_string('duco_avr_miner')
                        + str(MINER_VER)
                        + ') - '
                        + str(shares[0])
                        + '/'
                        + str(shares[0] + shares[1])
                        + get_string('accepted_shares'))
                    with thread_lock:
                        print(
                            Style.RESET_ALL
                            + Fore.WHITE
                            + now().strftime(Style.DIM + '%H:%M:%S ')
                            + Style.BRIGHT
                            + Back.MAGENTA
                            + Fore.RESET
                            + ' usb'
                            + str(''.join(filter(str.isdigit, com)))
                            + ' '
                            + Back.RESET
                            + Fore.RED
                            + ' ✗'
                            + get_string('rejected')
                            + Fore.RESET
                            + str(int(shares[0]))
                            + '/'
                            + str(int(shares[0] + shares[1]))
                            + Fore.YELLOW
                            + ' ('
                            + str(int((shares[0]
                                       / (shares[0] + shares[1]) * 100)))
                            + '%)'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' ∙ '
                            + str('%01.3f' % float(computetime))
                            + 's'
                            + Style.NORMAL
                            + ' ∙ '
                            + Fore.BLUE
                            + Style.BRIGHT
                            + str(int(hashrate))
                            + ' H/s'
                            + Style.NORMAL
                            + Fore.RESET
                            + ' @ diff '
                            + str(diff)
                            + ' ∙ '
                            + Fore.CYAN
                            + 'ping '
                            + str('%02.0f' % int(ping))
                            + 'ms')
                break


if __name__ == '__main__':
    # Colorama
    init(autoreset=True)
    # Window title
    title(get_string('duco_avr_miner') + str(MINER_VER) + ')')

    try:
        # Load config file or create new one
        load_config()
        debug_output('Config file loaded')
    except Exception as e:
        pretty_print(
            'sys0',
            get_string('load_config_error')
            + RESOURCES_DIR
            + get_string('load_config_error_warning')
            + Style.NORMAL
            + Fore.RESET
            + ' ('
            + str(e)
            + ')',
            'error')
        debug_output('Error reading configfile: ' + str(e))
        sleep(10)
        _exit(1)

    try:
        # Display greeting message
        greeting()
        debug_output('greeting displayed')
    except Exception as e:
        debug_output('Error displaying greeting message: ' + str(e))

    try:
        # Start donation thread
        donate()
    except Exception as e:
        debug_output('Error launching donation thread: ' + str(e))

    try:
        # Launch avr duco mining threads
        for port in avrport:
            thrThread(
                target=mine_avr,
                args=(port,)).start()
    except Exception as e:
        debug_output('Error launching AVR thead(s): ' + str(e))

    try:
        # Discord rich presence threads
        init_rich_presence()
        thrThread(
            target=update_rich_presence).start()
    except Exception as e:
        debug_output('Error launching Discord RPC thead: ' + str(e))
