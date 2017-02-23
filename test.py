import RPi.GPIO as GPIO

# Set up pins for motion detection
GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN)

while True:
    if not GPIO.input(3):
        print 'broken'
