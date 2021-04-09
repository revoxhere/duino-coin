import hashlib
import xxhash
import socket
import threading
import time
import struct
import traceback
import logging
import json

logger = logging.getLogger('Cluster_Client')
logger.setLevel(logging.DEBUG)
#fh = logging.FileHandler('Cluster_Client.log')
#fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
#logger.addHandler(fh)
logger.addHandler(ch)

WORKER_NAME = 'TEST'
CLUSTER_SERVER_ADDRESS = ('192.168.1.2',9090)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setblocking(False)

END_JOB = False

calculation_result = [None,0,0,0]
calculation_thread = None

def ducos1(
        lastBlockHash,
        expectedHash,
        start,
        end):
    global END_JOB,calculation_result
    hashcount = 0
    for ducos1xxres in range(int(start),int(end)):
        if END_JOB:
            logger.info('JOB TERMINATED')
            calculation_result = [None,hashcount,start,end]
            return None
        ducos1xx = hashlib.sha1(
                (str(lastBlockHash) + str(ducos1xxres)).encode('utf-8'))
        ducos1xx = ducos1xx.hexdigest()
        # Increment hash counter for hashrate calculator
        hashcount += 1
        # Check if result was found
        if ducos1xx == expectedHash:
            END_JOB = True
            logger.debug('LEFT '+str(ducos1xxres))
            calculation_result = [ducos1xxres, hashcount,start,end]
            return None
    logger.info('Empty block')
    END_JOB = True
    calculation_result = [None,hashcount,start,end]

def ducos1xxh(
        lastBlockHash,
        expectedHash,
        start,
        end):
    global END_JOB,calculation_result
    hashcount = 0
    for ducos1xxres in range(int(start),int(end)):
        if END_JOB:
            logger.info('JOB TERMINATED')
            calculation_result = [None,hashcount,start,end]
            return None
        ducos1xx = xxhash.xxh64(
        str(lastBlockHash) + str(ducos1xxres), seed=2811)
        ducos1xx = ducos1xx.hexdigest()
        # Increment hash counter for hashrate calculator
        hashcount += 1
        # Check if result was found
        if ducos1xx == expectedHash:
            END_JOB = True
            logger.debug('LEFT '+str(ducos1xxres))
            calculation_result = [ducos1xxres, hashcount,start,end]
            return None
    logger.info('Empty block')
    END_JOB = True
    calculation_result = [None,hashcount,start,end]
        

def ping():
    global client_socket,CLUSTER_SERVER_ADDRESS
    logger.info('Pinging master server')
    data = b'{"t":"e","event":"ping"}'
    client_socket.sendto(data,CLUSTER_SERVER_ADDRESS)

def register(dispatcher,event):
    '''
    event = {'t':'e',
            'event':'register',
            'address':(127.0.0.1,1234),
            'callback':socket}
    '''
    global WORKER_NAME

    logger.info('Registering worker')
    END_JOB = True
    calculation_result = [None,0,0,0]
    message = {'t':'e',
            'event':'register',
            'name':WORKER_NAME}
    data = json.dumps(message).encode('ascii')
    event.callback.sendto(data,event.address)

def start_job(dispatcher,event):
    '''
    event = {'t':'e',
             'event':'start_job',
             'lastBlockHash':JOB[0],
             'expectedHash':JOB[1],
             'start':JOB_START,
             'end':JOB_END,
             'algorithm':algorithm,
             'address':(),
             'callback':socket}
    '''
    global calculation_thread
    global END_JOB
    global calculation_result

    logger.info('Starting job')

    arguments = (event.lastBlockHash,
                 event.expectedHash,
                 event.start,
                 event.end)
    func = None
    if event.algorithm == 'XXHASH':
        logger.info('Using XXHASH algorithm')
        func = ducos1xxh
    elif event.algorithm == 'DUCO-S1':
        logger.info('Using DUCO-S1 algorithm')
        func = ducos1
    else:
        logger.warning('Algorithm not implemented')
        logger.debug(str(event.algorithm))

    if func == None:
        return None

    END_JOB = False
    calculation_result = [None,0,0,0]

    calculation_thread = threading.Thread(target=func,args=arguments,name='calculation thread')
    calculation_thread.start()

    data = json.dumps({'t':'a',
                        'status':'ok',
                        'message':'Job accepted'})
    event.callback.sendto(data.encode('ascii'),event.address)

def stop_job(dispatcher,event):
    '''
    event = {"t":"e",
            "event":"stop_job"}
    '''
    global END_JOB
    global calculation_result
    global calculation_thread

    logger.info('Terminating job')

    END_JOB = True

    try:
        calculation_thread.join()
    except:
        pass

    END_JOB = False
    calculation_result = [None,0,0,0]
    calculation_thread = None

    data = json.dumps({'t':'a',
                        'status':'ok',
                        'message':'Job terminated'})
    event.callback.sendto(data.encode('ascii'),event.address)

def send_result():
    global calculation_result
    global calculation_thread
    global END_JOB
    global client_socket
    global CLUSTER_SERVER_ADDRESS

    logger.info('Sending result')
    logger.debug(str(calculation_result))

    data = json.dumps({'t':'e',
                        'event':'job_done',
                        'result':calculation_result[:2],
                        'start_end':calculation_result[2:]})

    client_socket.sendto(data.encode('ascii'),CLUSTER_SERVER_ADDRESS)

    calculation_result = [None,0,0,0]
    calculation_thread = None
    END_JOB = False
    

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



def client():
    global client_socket
    global END_JOB
    global calculation_thread

    logger.debug('Initializing dispatcher')
    event_dispatcher = Dispatcher()
    event_dispatcher.register('register',register)
    event_dispatcher.register('stop_job',stop_job)
    event_dispatcher.register('start_job',start_job)
    logger.debug('Dispatcher initialized')


    ping_delay = 15
    last_ping = 0

    while True:
        data = None
        try:
            data, address = client_socket.recvfrom(1024)
        except:
            pass
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
                    message['callback'] = client_socket
                    event = Event(message)
                    event_dispatcher.add_to_queue(event)
                else:
                    pass
        
        try:
            event_dispatcher.dispatch_event()
        except Exception as e:
            logger.error('CANT DISPATCH EVENT')
            logger.debug('Traceback',exc_info=e)
                    
        if time.time()-last_ping>=ping_delay:
            ping()
            last_ping = time.time()

        if END_JOB:
            if calculation_thread != None:
                send_result()

        time.sleep(2)




if __name__ == '__main__':
    try:
        client()
    except Exception as e:
        #tr = traceback.format_exc()
        logger.warning('ERROR ACCURED',exc_info=e)

    input()