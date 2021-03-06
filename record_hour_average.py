'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com

'''
import datetime, time
import sqlite3

db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
#db.text_factory = str
# Get a cursor object
cursor = db.cursor()
    # Check if table users does not exist and create it

                     
cursor.execute("select avg(volume) from Water_Volume_minute")
   
temp = cursor.fetchall()
distance=temp[0][0]

#add record to database
now = datetime.datetime.now()

cursor.execute('''INSERT INTO Water_Volume_hour (timestamp, volume) VALUES (?,?)''',(now,distance))
db.commit()
#close database
db.close()
