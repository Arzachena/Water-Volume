
import serial as Serial
import datetime, time
import sqlite3
import math
import requests

db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
cursor = db.cursor()
    # Check if table users does not exist and create it
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_minute (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_hour (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_day (timestamp DATETIME PRIMARY KEY ASC NOT NULL UNIQUE, volume NUMERIC) WITHOUT ROWID''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_params (name PRIMARY KEY, value)''')

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
if (len(indata)== 4):   #did we get 4 bytes, or did we timeout?
    distance = ((indata[1] * 256) + indata[2]) / 1000  # div by 1000 to convert mm to metres
else: distance = 1   # we timed out

cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "shape"''')
data=cursor.fetchone()
if data is None:
    volume=1000 #default value to store if water tank has not yet been specified
elif data[0] == 'VertCyl':
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''') 
    max_height=cursor.fetchone()[0]
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "diameter"''')
    diameter=cursor.fetchone()[0]
    volume=(max_height- distance) * (math.pi * (diameter / 2) * (diameter / 2)) * 1000 #multiply by 1000 to convert cubic metres to litres
elif data[0] == 'Rectangle':
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''') 
    max_height=cursor.fetchone()[0]
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "length"''')
    length=cursor.fetchone()[0]
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "width"''')
    width=cursor.fetchone()[0]
    volume=(max_height - distance) * length * width * 1000 #multiply by 1000 to convert cubic metres to litres
elif data[0] == 'HorizCyl':
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "length"''')
    length=cursor.fetchone()[0]
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''')
    max_water_height=cursor.fetchone()[0]
    # do compicated calculation
    L=length
    d=max_water_height
    h=max_water_height - distance
    Pcyl=((d/2)**2*math.acos(((d/2)-h)/(d/2))-((d/2)-h)*(2*(d/2)*h-h**2)**(0.5))*L
    Pelipt=math.pi/6*h**2*(1.5*d-h)
    volume=(Pcyl+Pelipt) * 1000 #multiply by 1000 to convert cubic metres to litres
else:
    volume=1000 #default value to store if water tank has not yet been specified - should NEVER get here

data={"Volume": volume}
try:
        r = requests.put("http://10.0.0.18:39501/", json=data);
except:
        pass;
 

#add record to database
now = datetime.datetime.now()

cursor.execute('''INSERT INTO Water_Volume_minute (timestamp, volume) VALUES (?,?)''',(now,volume))
db.commit()
#close database
db.close()
