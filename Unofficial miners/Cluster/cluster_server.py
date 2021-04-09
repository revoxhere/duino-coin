import socket
import time
import configparser
import json
import requests
import threading
import struct
import select
import traceback
import logging

# https://github.com/DoctorEenot/DuinoCoin_android_cluster
'''
For the simpler usage that miner uses the same config directory as official PC miner:

PCMiner_2.4_resources

So in that folder (PCMiner_2.4_resources) you must have config file "Miner_config.cfg"

For more details go to projects page:
https://github.com/DoctorEenot/DuinoCoin_android_cluster
'''

minerVersion = "2.4"  # Version number
resourcesFolder = "PCMiner_" + str(minerVersion) + "_resources"
username = ''
efficiency= ''
donationlevel= ''
debug= ''
threadcount= ''
requestedDiff= ''
rigIdentifier= ''
lang= ''
algorithm= ''
config = configparser.ConfigParser()
serveripfile = ("https://raw.githubusercontent.com/"
    + "revoxhere/"
    + "duino-coin/gh-pages/"
    + "serverip.txt")  # Serverip file
masterServer_address = ''
masterServer_port = 0

MIN_PARTS = 5
INC_COEF = 0

DISABLE_LOGGING = True

logger = logging.getLogger('Cluster_Server')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if not DISABLE_LOGGING:
    fh = logging.FileHandler('Cluster_Server.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)




# Config loading section
def loadConfig():
    global username
    global efficiency
    global donationlevel
    global debug
    global threadcount
    global requestedDiff
    global rigIdentifier
    global lang
    global algorithm

    logger.info('Loading config')
    config.read(resourcesFolder + "/Miner_config.cfg")
    username = config["miner"]["username"]
    threadcount = config["miner"]["threads"]
    requestedDiff = config["miner"]["requestedDiff"]
    algorithm = config["miner"]["algorithm"]
    rigIdentifier = config["miner"]["identifier"]



time_for_device = 90

class Device:
    def __init__(self,name,address):
        self.name = name
        self.last_updated = time.time()
        self.busy = False

    def is_alive(self):
        return (time.time()-self.last_updated)<time_for_device
    def update_time(self):
        self.last_updated = time.time()
    def isbusy(self):
        return self.busy
    def job_stopped(self):
        self.busy = False
    def job_started(self):
        self.busy = True

    def __str__(self):
        return self.name+' '+str(self.address)
    def __repr__(self):
        return str(self)



devices = {}


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
server_socket.setblocking(False)
SERVER_ADDRESS = ('0.0.0.0',9090)
server_socket.bind(SERVER_ADDRESS)

master_server_socket = socket.socket()

def connect_to_master():
    logger.info('CONNECTING TO MASTER')
    global master_server_socket
    try:
        master_server_socket.close()
    except:
        pass
    while True:
        master_server_socket = socket.socket()
        # Establish socket connection to the server
        try:
            master_server_socket.connect((str(masterServer_address),
                                        int(masterServer_port)))
            serverVersion = master_server_socket.recv(3).decode().rstrip("\n")  # Get server version
        except Exception as e:
            continue
        break



def register(dispatcher,event):
    '''
    event = {'t':'e',
              'event':'register',
              'name':'Test',
              'address':('127.0.0.1',1234),
              'callback':socket}
    '''
    global devices
    
    logger.info('Register')
    device = devices.get(event.address,None)
    if device != None:
        event.callback.sendto(b'{"t":"a",\
                                "status":"ok",\
                                "message":"already exists"}',
                                event.address)
        return None

    devices[event.address] = Device(event.name,event.address)
    event.callback.sendto(b'{"t":"a",\
                             "status":"ok",\
                             "message":"device added"}',
                             event.address)
    
    event.dict_representation['event'] = 'job_done'
    event.dict_representation['result'] = [None,0]
    event.dict_representation['start_end'] = [0,0]
    dispatcher.add_to_queue(event)

    return None

def ping(dispatcher,event):
    '''
    event = {'t':'e',
             'event':'ping',
             'address':('127.0.0.1',1234),
              'callback':socket}
    '''
    global devices

    logger.info('Ping')
    device = devices.get(event.address,None)
    if device == None:
        event.callback.sendto(b'{"t":"e",\
                             "event":"register",\
                             "message":"You must register in cluster"}',
                              event.address)
        return None
    
    device.update_time()
    data = b'{"t":"a","status":"ok","message":"server is running"}'
    event.callback.sendto(data,event.address)
    return None

JOB = None
JOB_START_SECRET = 'ejnejkfnhiuhwefiy87usdf'
JOBS_TO_PROCESS = {}
HASH_COUNTER = 0


class Job:
    def __init__(self,device = None):
        self.device = device
        self.done = False
    def set_device(self,device):
        self.device = device
    def get_device(self):
        return self.device
    def is_done(self):
        return self.done
    def set_done(self):
        self.done = True
    def is_claimed(self):
        return self.device == None



def job_start(dispatcher,event):
    '''
    event = {'t':'e',
             'event':'job_start',
             'secret':'',
             'callback':socket}
    '''
    global JOB
    global JOB_START_SECRET
    global algorithm
    global JOBS_TO_PROCESS


    
    logger.info('Job is starting')
    if event.secret != JOB_START_SECRET:
        logger.warning('bad secret')
        return


    for start_end,job in JOBS_TO_PROCESS.items():
        for addr,device in devices.items():
            if device.isbusy():
                continue
            data = json.dumps({'t':'e',
                            'event':'start_job',
                            'lastBlockHash':JOB[0],
                            'expectedHash':JOB[1],
                            'start':start_end[0],
                            'end':start_end[1],
                            'algorithm':algorithm})
            device.job_started()
            event.callback.sendto(data.encode('ascii'),addr)
            job.set_device(device)
            break
            

def send_results(result):
    global algorithm
    global minerVersion
    global rigIdentifier
    global HASH_COUNTER

    logger.info('Sending results')
    logger.debug(str(result))
    logger.info('Hashes were checked: '+str(HASH_COUNTER))
    while True:
        try:
            master_server_socket.send(bytes(
                                    str(result[0])
                                    + ","
                                    + str(HASH_COUNTER)
                                    + ","
                                    + "YeahNot Cluster ("
                                    + str(algorithm)
                                    + ") v" 
                                    + str(minerVersion)
                                    + ","
                                    + str(rigIdentifier),
                                    encoding="utf8"))
            feedback = master_server_socket.recv(8).decode().rstrip("\n")
            break
        except:
            connect_to_master()

    if feedback == 'GOOD':
        logger.info('Hash accepted')
    elif feedback == 'BLOCK':
        logger.info('Hash blocked')
    else:
        logger.info('Hash rejected')
    HASH_COUNTER = 0

def job_done(dispatcher,event):
    '''
    event = {'t':'e',
            'event':'job_done',
            'result':[1,1] | ['None',1],
            'start_end':[1,1],
            'address':('127.0.0.1',1234),
            'callback':socket}
    '''
    global JOB
    global algorithm
    global JOBS_TO_PROCESS
    global HASH_COUNTER

    logger.info('job done packet')
    if (event.result[0] == 'None' \
        or event.result[0] == None):
        logger.info('Empty block')
        device = devices.get(event.address,None)
        if device == None:
            logger.warning('device is not registered')
            event.callback.sendto(b'{"t":"e",\
                             "event":"register",\
                             "message":"You must register in cluster"}',
                              event.address)
            return None
        if not device.is_alive():
            logger.warning('Device '+device.name+' '+str(event.address)+' is dead')
            data = json.dumps({'t':'e',
                                'event':'ping'})
            event.callback.sendto(data.encode('ascii'),event.address)
            return None

        if JOB == None:
            logger.info('Job is already over')
            data = b'{"t":"a",\
                    "status":"ok",\
                    "message":"No job to send"}'
            event.callback.sendto(data,event.address)
            return

        HASH_COUNTER += event.result[1]

        recieved_start_end = tuple(event.start_end)
        if recieved_start_end[0] == 0 and recieved_start_end[1] == 0:
            logger.debug('redirect from register')
        else:
            try:
                JOBS_TO_PROCESS[recieved_start_end].set_done()
            except:
                logger.error('CANT FIND BLOCK: '+str(recieved_start_end))

        job_to_send = None
        # searching for unclaimed jobs
        for start_end,job in JOBS_TO_PROCESS.items():
            if not job.is_claimed() and not job.is_done():
                job.set_device(device)
                job_to_send = start_end
                break
        # searching for claimed undone jobs
        if job_to_send == None:
            for start_end,job in JOBS_TO_PROCESS.items():
                if not job.is_done():
                    job.set_device(device)
                    job_to_send = start_end
                    break


        data = json.dumps({'t':'e',
                        'event':'start_job',
                        'lastBlockHash':JOB[0],
                        'expectedHash':JOB[1],
                        'start':job_to_send[0],
                        'end':job_to_send[1],
                        'algorithm':algorithm})
        device.job_started()

        event.callback.sendto(data.encode('ascii'),event.address)
    
    else:
        logger.info('accepted result')
        HASH_COUNTER += event.result[1]
        send_results(event.result)
        JOBS_TO_PROCESS = {}
        data = b'{"t":"e","event":"stop_job","message":"terminating job"}'
        logger.debug('stopping workers')
        for addr,device in devices.items():
            device.job_stopped()
            event.callback.sendto(data,addr)
        JOB = None


def request_job(dispatcher,event):
    '''
    event = {'t':'e',
             'event':'requets_job',
             'secret':'',
             'parts':10}
    '''
    global JOB
    global JOB_START_SECRET
    global algorithm
    global username
    global requestedDiff
    global master_server_socket
    global JOBS_TO_PROCESS

    logger.info('requesting job')
    if event.secret != JOB_START_SECRET:
        logger.warning('bad secret')
        return
    while True:
        try:
            if algorithm == "XXHASH":
                master_server_socket.send(bytes(
                    "JOBXX,"
                    + str(username)
                    + ","
                    + str(requestedDiff),
                    encoding="utf8"))
            else:
                master_server_socket.send(bytes(
                    "JOB,"
                    + str(username)
                    + ","
                    + str(requestedDiff),
                    encoding="utf8"))
        except Exception as e:
            logger.error('asking for job error accured')
            connect_to_master()
            continue
        try:
            job = master_server_socket.recv(128).decode().rstrip("\n")
        except:
            connect_to_master()
            continue
        job = job.split(",")
        if job[0] == 'BAD':
            logger.warning('GOT "BAD" PACKET IN RESPONSE')
            return
        elif job[0] == '':
            logger.warning('CONNECTION WITH MASTER SERVER WAS BROKEN')
            connect_to_master()
            continue
        logger.info('job accepted')
        logger.info('Difficulty: '+str(job[2]))
        logger.debug(str(job))

        JOBS_TO_PROCESS = {}

        JOB = job[:2]
        real_difficulty = (100*int(job[2]))
        job_part = (real_difficulty//MIN_PARTS)
        start = 0
        end = job_part
        while start<real_difficulty:
            job_object = Job()
            JOBS_TO_PROCESS[(start,end)] = job_object
            start = end
            if real_difficulty<end+job_part:
                end = real_difficulty+1
            else:
                end += job_part 

        break


class Event(object):
    def __init__(self,input:dict):
        self.dict_representation = input
    def __dict__(self):
        return super(Event, self).__getattribute__('dict_representation')
    #def event_name(self) -> str:
    #    return self.dict_representation['event']
    def __getattribute__(self, item):
        # Calling the super class to avoid recursion
        return super(Event, self).__getattribute__(item)
    def __getattr__(self, item):
        
        try:
            return super(Event, self).__getattribute__('dict_representation')[item]
        except:
            logger.warning('NO SUCH ELEMENT AS '+str(item))
            pass
    def __str__(self):
        return str(self.dict_representation)

class Dispatcher:
    def __init__(self):
        self.actions = {}
        self.queue = []

    def register(self,event_name,action):
        self.actions[event_name] = action
    
    def add_to_queue(self,event:Event):
        logger.debug('added event')
        self.queue.append(event)

    def clear_queue(self):
        self.queue = []

    def dispatch_event(self):
        try:
            event = self.queue.pop(0)
        except:
            return None
        logger.debug('dispatching event')
        func = self.actions.get(event.event,None)
        if func == None:
            logger.warning('NO SUCH ACTION '+event.event)
            return None
        return self.actions[event.event](self,event)


def server():
    global server_socket
    global devices
    global MIN_PARTS
    global INC_COEF

    logger.debug('Initializing dispatcher')
    event_dispatcher = Dispatcher()
    event_dispatcher.register('register',register)
    event_dispatcher.register('ping',ping)
    event_dispatcher.register('job_start',job_start)
    event_dispatcher.register('job_done',job_done)
    event_dispatcher.register('request_job',request_job)
    logger.debug('Dispatcher initialized')

    while True:
        # recieving events
        data = None
        try:
            data, address = server_socket.recvfrom(1024)
        except:
            pass

        # parsing events and registering events
        if data != None:
            data_is_ok = False
            try:
                message = json.loads(data.decode('ascii'))
                data_is_ok = True
            except:
                logger.warning("can't parse packet")
                logger.debug(str(data))
            if data_is_ok:
                logger.debug('accepted packet')
                logger.debug(str(message))
                if message['t'] == 'e':
                    message['address'] = address
                    message['callback'] = server_socket
                    event = Event(message)
                    event_dispatcher.add_to_queue(event)
                else:
                    device = devices.get(address,None)
                    if device == None:
                        server_socket.sendto(b'{"t":"e",\
                                                "event":"register",\
                                                "message":"You must register in cluster"}',
                                                address)
                    else:
                        device.update_time()
        
        # dispatching events
        try:
            event_dispatcher.dispatch_event()
        except Exception as e:
            logger.error('CANT DISPATCH EVENT')
            logger.debug('Traceback',exc_info=e)


        # request job and start it
        if len(devices)>0:
            if JOB == None:
                MIN_PARTS = len(devices)+INC_COEF
                logger.debug('MIN_PARTS is setted to '+str(MIN_PARTS))
                event_dispatcher.clear_queue()
                event = Event({'t':'e',
                               'event':'request_job',
                               'secret':JOB_START_SECRET,
                               'parts':20})
                event_dispatcher.add_to_queue(event)
                event = Event({'t':'e',
                               'event':'job_start',
                               'secret':JOB_START_SECRET,
                               'callback':server_socket})
                event_dispatcher.add_to_queue(event)


        # cleenup devices
        for address,device in devices.items():
            if not device.is_alive()\
                and not device.busy:
                del devices[address]
                break
        
        time.sleep(0.5)



if __name__ == '__main__':
    logger.info('STARTING SERVER')
    loadConfig()
    logger.info('Getting Master server info')
    while True:
        try:
            res = requests.get(serveripfile, data=None)
            break
        except:
            pass
        logger.info('getting data again')
        time.sleep(10)

    if res.status_code == 200:
        logger.info('Master server info accepted')
        # Read content and split into lines
        content = (res.content.decode().splitlines())
        masterServer_address = content[0]  # Line 1 = pool address
        masterServer_port = content[1]  # Line 2 = pool port
    else:
        raise Exception('CANT GET MASTER SERVER ADDRESS')

    try:
        server()
    except Exception as e:
        #tr = traceback.format_exc()
        logger.error('ERROR ACCURED',exc_info=e)

    input()

    
