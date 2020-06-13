'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: http://randomnerdtutorials.com

'''
import sqlite3
import requests

db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Water_Volume_params (name PRIMARY KEY, value)''')
cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "domain"''')
data=cursor.fetchone()
if data is not None:
    domain=data[0]
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "token"''')
    data=cursor.fetchone()
    token=data[0]
    try:
        params = {
        "domains": domain,
        "token": token
        }
        r = requests.get("https://www.duckdns.org/update", params)
    except:
        pass;
db.close()

