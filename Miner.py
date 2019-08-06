import serial, time, random, socket

#2597!!!!!!!!!

users = {}
status = ""
ser = serial.Serial('COM8')
host = '127.0.0.1'
port = 5000
s = socket.socket()
s.connect((host, port))
#
#print("Key is:", key)

welcome = input("Do you have an duino-coin acount? y/n: ")
print(" ")
if welcome == "n":
    while True:
        print("***Please register on pool:***")
        username = input("Enter a username:")
        password = input("Enter a password:")
        password1 = input("Confirm password:")
        if password == password1:
            s.send(bytes('REGI' , encoding='utf8'))
            time.sleep(0.1)
            s.send(bytes(username , encoding='utf8'))
            time.sleep(0.1)
            s.send(bytes(password , encoding='utf8'))
            key = s.recv(2)
            key=key.decode()
            if key == "OK":
                print(" ")
                print("Successfully registered!")
                print("Now you can login!")
                welcome = "y"
                break
            if key == "NO":
                print(" ")
                print("That user is already registered!")
        
if welcome == "y":
    while True:
        print("***Please login to pool:***")
        username = input("Username:")
        password = input("Password:")
        time.sleep(0.1)
        s.send(bytes('LOGI' , encoding='utf8'))
        time.sleep(0.1)
        s.send(bytes(username , encoding='utf8'))
        time.sleep(0.1)
        s.send(bytes(password , encoding='utf8'))
        key = s.recv(2)
        key=key.decode()
        if key == "OK":
            print(" ")
            print("Login success!")
            print(" ")
            break
        if key == "NO":
            print(" ")
            print("Invalid credentials! If you don't have an account, restart and register.")
 

def mine():
    s.send(bytes("MINE", encoding='utf8'))
    time.sleep(0.1)
    while True:
        work = random.randint(0,9)
        work2 = random.randint(0,9)

        ser.write(b'1') #connection establishment key
        connection = ser.readline()
        connection=connection.decode('utf-8')
    
        ser.write(str(work).encode())
        ser.write(str(work2).encode())
    
        result = ser.readline()
        result=result.decode('utf-8')
        print("The result is", result)
        s.send(bytes(result, encoding='utf8'))
        time.sleep(0.1)

mine()


