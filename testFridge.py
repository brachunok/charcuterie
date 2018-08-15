# turns on the fridge relay, then turns it back off


import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26,GPIO.OUT)
print "output on"
GPIO.output(26,GPIO.HIGH)
time.sleep(5)
print "output off "
GPIO.output(26,GPIO.LOW)
