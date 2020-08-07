#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
from datetime import datetime as dt

# INTAVAL = 3
SLEEP_DETECT = 300  # 300sec 5min
SLEEP_NON = 5
SENSOR_PIN = 23
LED_PIN = 22
STOP_DETECT = 20    # PM8:00 Stop

def setup():
    GPIO.setmode(GPIO.BCM) # Pin Location
    GPIO.setup(SENSOR_PIN, GPIO.IN)	# inputの指定
    GPIO.setup(LED_PIN, GPIO.OUT)	# outの指定


def destroy():
    GPIO.cleanup()
    print ("cleanup GPIO.")


# st = time.time()-INTAVAL

def loop():
    cnt = 0
    d_today = dt.now().strftime('%Y%m%d')
    logfile="/home/pi/mycode/logs/mlog" + d_today + ".log"   # logfile name
    #fileobj = open (logfile,"w", encoding="utf_8") 
    #fileobj.close()
    
    while dt.now().hour < STOP_DETECT :
        #print (GPIO.input(SENSOR_PIN))
        if GPIO.input(SENSOR_PIN) == GPIO.HIGH :
        # st = time.time()
            GPIO.output(LED_PIN, GPIO.LOW) # LED ON
            cnt += 1
            print (cnt, "times motion detection ", end='')
            print (time.strftime("%H:%M:%S"))
            fileobj = open (logfile,"a", encoding="utf_8") 
            fileobj.write(time.strftime("%Y-%m-%d %H:%M:%S,"))
            fileobj.close()
            time.sleep(SLEEP_DETECT)
        else:
            print ("Non Move " + time.strftime("%H:%M:%S"))
            GPIO.output(LED_PIN, GPIO.HIGH) # LED OFF
            time.sleep(SLEEP_NON)
    destroy()

    
if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
		destroy()