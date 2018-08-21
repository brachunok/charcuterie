#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
from Adafruit_IO import Client

import RPi.GPIO as GPIO

import Adafruit_DHT
import time
from Adafruit_LED_Backpack import SevenSegment


# make connection to adafruit IO
aio = Client('df25f448176d4b07b85faaa103b86914')


# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#')
    print('example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4')

#hardcode the sensor and pin
sensor = Adafruit_DHT.AM2302
pin = 4
# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

# Un-comment the line below to convert the temperature to Fahrenheit.
temperature = temperature * 9/5.0 + 32

# Now here we set the constants
#
# templow is when we turn off the fridge
# temphigh is when we turn on the fridge
#
# humlow is when we turn on the humidifier
# humhigh is when we turn off the humidifier
#
# fridgepin is the GPIO pin we are using to control the fridge relay
# humpin is the humidifier relay pin we are using
#
# #################################################


templow = 58
temphigh = 60

humlow = 75
humhigh = 90

fridgepin = 26
humpin = 17
# now if we are above temphigh, turn on the fridge pin
# we are just going to turn it on until we hit the threshold then for a littl elonger
# hoping we can rely on the thermal mass of the fridge to keep it constant

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(fridgepin,GPIO.OUT)

# gonna have to set up the humidity pin out
GPIO.setup(humpin,GPIO.OUT)

# initialize
fridgeON = 0
humidityON = 0

# start control loop
for x in range(30):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)    
    
    # convert to fh
    temperature = temperature * 9/5.0 + 32

    # if the temperature is above our high temp, turn the fridge on
    if (temperature > temphigh):
        GPIO.output(fridgepin,GPIO.HIGH) # turn on fridgepin
        fridgeON = 1
        print("fridge on")
    elif temperature < templow:
        GPIO.output(fridgepin,GPIO.LOW) # if the temp is too low, turn the fridge ofj
        fridgeON = 0
        print("fridge off")
    # do the same for humidity

    if (humidity >humhigh):
        GPIO.output(humpin,GPIO.HIGH) # turn off humidity
        humidityON = 0
        print("humidity off")
    elif humidity< humlow:
        GPIO.output(humpin,GPIO.LOW) # turn on humidity
        humidityON = 1
        print("humidity on")

    # print the temp
    try:
        display = SevenSegment.SevenSegment()
        display.begin()
        display.clear()
        time.sleep(1.0)				
        display.print_float(temperature)
        display.write_display()
    except:
        print("display write error")

    # print a status
    print temperature
    print x
    # write to adafruit
    try:
        aio.send('fridge_temp',temperature)
        aio.send('fridge_humidity',humidity)
        aio.send('fridge_on', fridgeON)
        aio.send('humidity_on',humidityON)
    except:
       print("adafruit send error")
   # sleep for a bit 
    time.sleep(30)
    
#all this below is useless.

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!
if humidity is not None and temperature is not None:
    	aio.send('desk_temp',temperature)
	aio.send('desk_humidity',humidity)
	print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
)
