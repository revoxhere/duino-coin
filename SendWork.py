import serial
import time
import random
#2597!!!!!!!!!
ser = serial.Serial('COM8')
while True:
    work = random.randint(0,9)
    work2 = random.randint(0,9)

    ser.write(b'1') #connection establishment key
    connection = ser.readline()
    connection=connection.decode('utf-8')
    print(connection) #check if connection has been established
    
    ser.write(str(work).encode())
    ser.write(str(work2).encode())
    
    result = ser.readline()
    result=result.decode('utf-8')
    print("The result is", result)
    time.sleep(0.1)

