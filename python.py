import pyrebase
import ephem
import RPi.GPIO as GPIO
import time
from MPUTRIAL import MPU9255

#GPIO.setmode(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

latch = 0
rLat = 0
rLon = 0
observer = ephem.Observer()
eventType = "Single"
eventList = [""]

config = {
	"apiKey": "AIzaSyDV0HIgQTzSM-Yd72Y4b40OfQiLV0rwjLU",
	"authDomain": "pythontestdatabase.firebaseapp.com",
	"databaseURL": "https://pythontestdatabase.firebaseio.com/",
	"storageBucket": "pythontestdatabase.appspot.com"
}
firebase = pyrebase.initialize_app(config)

db = firebase.database()
#.child("users").push({"name": "Emily Ryan"})

def stream_gps(message):
	#print("Event: " + message["event"])
	#print("Path: " + message["path"])
	#print(message["data"]["lat"])
	#print(message["data"]["lon"])
	#print(message["data"]["alt"])
	observer.elevation = message["data"]["alt"]
	observer.lat = message["data"]["lat"]
	observer.lon = message["data"]["lon"]

def stream_event(message):
	eventType = message["data"]["eventType"]
	eventList = message["data"]["names"]
	print(eventType)
	print(eventList)
	

def getPlanet(planet):
	return {
		"Mercury": ephem.Mercury(),
		"Venus": ephem.Venus,
		"Mars": ephem.Mars(),
		"Jupiter": ephem.Jupiter(),
		"Saturn": ephem.Saturn(),
		"Uranus": ephem.Uranus(),
		"Neptune": ephem.Neptune()
	}.get(planet, ephem.Mars())

gpsStream = db.child("gps").stream(stream_gps)

db.child("Event").stream(stream_event)

#
#mars = ephem.Mars()
#mars.compute('2018/10/11')
#print(mars.ra)
#print(mars.dec)

mpu = MPU9255()
mpu.start()
time.sleep(1)
while True:
	imuList = mpu.getData()
	for i in imuList:
		print(imuList[i].getTemp())
	print("here")
	time.sleep(1)
