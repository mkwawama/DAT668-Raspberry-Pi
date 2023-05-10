#!/usr/bin/python

from gpiozero import Servo
from gpiozero import DistanceSensor
import RPi.GPIO as GPIO
from time import sleep
import requests
from urllib.parse import urlparse
import httplib2 as http
import json


from datetime import datetime

servoGPIO = 17
ledGPIO = 14

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(ledGPIO, GPIO.OUT)

servo = Servo(servoGPIO)

ultrasonic = DistanceSensor(echo=27, trigger=4)


def dispensepills():
    servo.max()
    sleep(1)
    servo.min()


# check if cup is neer the dispenser exit door
def checkcup():
    print(ultrasonic.distance)
    cupIsAround = false
    if (ultrasonic.distance < 0.4):
        cupIsAround = true
        return true


def ongreen():
    GPIO.output(ledGPIO, GPIO.HIGH)


def offgreen():
    GPIO.output(ledGPIO, GPIO.LOW)


# get medications from the backend for this user with this dispenser
def getmeds():
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'userid': '6458521cc13a2b5d7bc50852'
    }

    uri = 'http://smartpillserver.mahinster.co.uk/medication'

    target = urlparse(uri)
    method = 'GET'
    body = ''
    h = http.Http()
    response, content = h.request(target.geturl(), method, body, headers)

    return json.loads(content)


def checkdates():
    meds = getmeds()
    for med in meds:
        for sched in med["medsched"]:
            if (sched["taken"] == "0"):  # medication not taken
                sched_date = sched["schedule_date"]
                now = datetime.now()

                # format dates for comparison
                sched_now = datetime.strptime(sched_date, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)
                now = now.strftime('%Y %m %d %I:%M %p')

                sched_now = sched_now + timedelta(minutes=50)  # pills to be dispensed 10 mins before the scheduled time
                sched_now = sched_now.strftime('%Y %m %d %I:%M %p')

                print(now)
                print(sched_now)

                if (now > sched_now):
                    print("Dispensing  medication ....")
                    if (checkcup()):  # check if medicine cup is around the dispenser exit
                        dispensepill()
                        ongreen()
                        sleep(300)
                        offgreen()


while True:
    checkdates()
    sleep(900)  # sleep for 15 mins

