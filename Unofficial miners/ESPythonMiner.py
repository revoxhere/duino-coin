"""
Unofficial DuinoCoin miner for ESP32/ESP8266 running Micropython, based on official Python PC_Miner
Created FabioPolancoE - 2021

This miner works standalone, just like official PC_Miner, so you don't need to connect your device via Serial to a PC (Although you can)
NOTE: This requires you to enter your network name and password in order to establish a WiFi connection.

It's recommended to connect the device via Serial to a PC before starting mining to make sure you have no errors, once the device
starts to mine, you can close your serial monitor so the only thing that your miner takes from your PC is current. Note, that this is
not required, only recommended, you can make sure your miner is working in the DUCO Webwallet or SIUNUSDEV's DUCOMonitor.

"""
# Fill this variables to configure your miner
username = "enter your DUCO username here"
rigIdentifier = "ESP Device"
netname = "enter the name of your WiFi network here"
password = "enter the password of you WiFi network here"
import usocket as socket, uhashlib as hashlib, time, network, ubinascii

print("Almost all modules imported...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Network interface activated")
if not wlan.isconnected():
    print('Connecting to network...')
    wlan.connect(netname, password)
    while not wlan.isconnected():
        print("Not connected to network, this happens commonly, retrying...")
        time.sleep(3)
        pass
print('Connected to WiFI! Network config:', wlan.ifconfig())

try:
    import urequests as requests
    print("uRequests imported")
except ImportError:
    print("Looks like uRequests is no installed, trying to install with uPip, if installation fails, please install manually")
    import upip
    upip.install("urequests")
    try:
        import urequests as requests
    except ImportError:
        print("Maybe installation failed, please install urequests manually")
        while True:
            pass

soc = socket.socket()
soc.settimeout(10)

def ducos1(lastBlockHash, expectedHash, difficulty):  # Loop from 1 too 100*diff
    hashcount = 0
    for ducos1res in range(100 * int(difficulty) + 1):
        ducos1 = hashlib.sha1(str(lastBlockHash + str(ducos1res)).encode("utf-8"))
        ducos1 = ubinascii.hexlify(ducos1.digest()).decode()  # Generate hash
        time.sleep(0.005)
        hashcount += 1  # Increment hash counter for hashrate calculator
        # Next line was used for debugging, uncomment it to see the miner work :3
        # print(str(ducos1) + " | " + str(expectedHash))
        if ducos1 == expectedHash:
            print("Hash found, sending for feedback...")
            return [ducos1res, hashcount]

try:
    # This sections grabs pool adress and port from Duino-Coin GitHub file
    serverip = requests.get("https://raw.githubusercontent.com/revoxhere/duino-coin/gh-pages/serverip.txt")  # Serverip file
    content = serverip.text.split("\n") # Read content and split into lines
    pool_address = content[0]  # Line 1 = pool address
    pool_port = content[1]  # Line 2 = pool port
    
    # This section connects and logs user to the server
    soc.connect((str(pool_address), int(pool_port)))  # Connect to the server
    server_version = soc.recv(3).decode()  # Get server version
    print("Server is on version", server_version)
    # Mining section
    while True:
        soc.send(
            bytes("JOB," + username + ",AVR", "utf8")
        )  # Send job request
        job = soc.recv(1024).decode()  # Get work from pool
        job = job.split(",")  # Split received data to job (job and difficulty)
        difficulty = job[2]

        hashingStartTime = time.time()
        print("Calculating...")
        result = ducos1(job[0], job[1], job[2])
        hashingStopTime = time.time()
        difference = hashingStopTime - hashingStartTime
        try:
            hashrate = result[1] / difference
        except ZeroDivisionError:
            hashrate = 0
        while True:
            soc.send(
                bytes(str(result[0]) + "," + str(hashrate) + ",ESPython Miner," + rigIdentifier, "utf8")
            )  # Send result of hashing algorithm to pool
            feedback = soc.recv(1024).decode()  # Get feedback about the result
            if feedback == "GOOD":  # If result was good
                print("Accepted share | Hashrate", int(hashrate/1000), "kH/s | Difficulty", difficulty)
                break
            elif feedback == "BLOCK":
                print("Block found | Hashrate", int(hashrate/1000), "kH/s | Difficulty", difficulty)
                break
            elif feedback == "BAD":  # If result was bad
                print("Rejected share | Hashrate", int(hashrate/1000), "kH/s | Difficulty", difficulty)
                break
            else:
                print(feedback)
except Exception as e:
    # Uncomment the next line to get the full exception data
    # raise
    print("Error occured:\n\t" + str(e))
