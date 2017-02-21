import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN)

while True:
    if not GPIO.input(3):
        print 'Triggered'
        time.sleep(3)
