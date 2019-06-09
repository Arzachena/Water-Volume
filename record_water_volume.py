'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com

'''
import serial as Serial
import datetime, time
import sqlite3
import math

db = sqlite3.connect('/home/pi/web-server/volume.db')      #open database - create it if it doesn't exist

# Get a cursor object
cursor = db.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_minute (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_hour (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_day (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')

cursor.execute('''CREATE TRIGGER IF NOT EXISTS Limit_Size AFTER INSERT 
ON Water_Volume_minute WHEN (SELECT count(*) FROM Water_Volume_minute) > 60
BEGIN
 DELETE FROM Water_Volume_minute WHERE timestamp = (SELECT timestamp FROM Water_Volume_minute LIMIT (0,1) );
END''')

cursor.execute('''CREATE TRIGGER IF NOT EXISTS Limit_Size2 AFTER INSERT 
ON Water_Volume_hour WHEN (SELECT count(*) FROM Water_Volume_hour) > 24
BEGIN
 DELETE FROM Water_Volume_hour WHERE timestamp = (SELECT timestamp FROM Water_Volume_hour LIMIT (0,1) );
END''')

cursor.execute('''CREATE TRIGGER IF NOT EXISTS Limit_Size3 AFTER INSERT 
ON Water_Volume_day WHEN (SELECT count(*) FROM Water_Volume_day) > 30
BEGIN
 DELETE FROM Water_Volume_day WHERE timestamp = (SELECT timestamp FROM Water_Volume_day LIMIT (0,1) );
END''')
                    
distance = 0
#indata=[]
ser = Serial.Serial(
        port='/dev/serial0', 
        baudrate = 9600,
        parity=Serial.PARITY_NONE,
        stopbits=Serial.STOPBITS_ONE,
        bytesize=Serial.EIGHTBITS,
        timeout=1
)
ser.write(str.encode("0"))
time.sleep(1)
indata=ser.read(4)

distance = ((indata[1] * 256) + indata[2])
distance=((9560 - distance) * math.pi) / 10

#add record to database
now = datetime.datetime.now()

cursor.execute('''INSERT INTO Water_Volume_minute (timestamp, volume) VALUES (?,?)''',(now,distance))
db.commit()
#close database
db.close()
