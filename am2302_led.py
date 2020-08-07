#!/usr/bin/python
# coding: utf-8
import RPi.GPIO as GPIO
import time
import Adafruit_DHT as DHT
import requests
from datetime import date, datetime as dt
# import paho.mqtt.client as mqtt

###### Edit variables to your environment #######
# broker_address = "test.mosquitto.org"     #MQTT broker_address
# Topic = "tkimura777"

# print("creating new instance")
# client = mqtt.Client("pub5") #create new instance
# print("connecting to broker")
# client.connect(broker_address) #connect to broker

## LED BAR
DATA_Pin = 20
CLK_Pin  = 21
CmdMode  = 0x0000  # Work on 8-bit mode
ON       = 0x00ff  # 8-byte 1 data
SHUT     = 0x0000  # 8-byte 0 data
 
global s_clk_flag
s_clk_flag = 0


## センサーの種類
SENSOR_TYPE = DHT.DHT22

## 接続したGPIOポート
DHT_GPIO = 26
SLEEP_NON = 60

STOP_DETECT = 23    # PM8:00 Stop

TMP_OFFSET = 28     # 28C -> 0
HUMD_OFFSET = 8     # 40%/5 = 8 -> 0


# LED BAR map
WBGT_BAR = {25:1, 26:3, 27:7, 28:15, 29:31, 30:63, 31:127, 32:255}

# WBGT Table 28-33 C, 40 - 80%
WBGT_TBL = [ 
[23,23,24,25,25,26,27,28,28],
[24,24,25,26,26,27,28,29,29],
[24,25,26,27,27,28,29,29,30],
[25,26,27,27,28,29,30,30,31],
[26,27,28,28,29,30,31,31,32],
[27,28,28,29,30,31,32,32,33]]

def send16bitData(data):
	global s_clk_flag
	for i in range(0, 16):
		if data & 0x8000:
			GPIO.output(DATA_Pin, GPIO.HIGH)
		else:
			GPIO.output(DATA_Pin, GPIO.LOW)
		
		if s_clk_flag == True:
			GPIO.output(CLK_Pin, GPIO.LOW)
			s_clk_flag = 0
		else:
			GPIO.output(CLK_Pin, GPIO.HIGH)
			s_clk_flag = 1
		time.sleep(0.001)
		data = data << 1
  
def latchData():
	latch_flag = 0
	GPIO.output(DATA_Pin, GPIO.LOW)
	
	time.sleep(0.05)
	for i in range(0, 8):
		if latch_flag == True:
			GPIO.output(DATA_Pin, GPIO.LOW)
			latch_flag = 0
		else:
			GPIO.output(DATA_Pin, GPIO.HIGH)
			latch_flag = 1
	time.sleep(0.05)
  
def sendLED(LEDstate):
	for i in range(0, 12):
		if (LEDstate & 0x0001) == True:
			send16bitData(ON)
		else:
			send16bitData(SHUT)
		LEDstate = LEDstate >> 1

def setup():
	print ("Adeept LED bar test code!")
	# print ("Using DATA = PIN16(GPIO23), CLK = PIN18(GPIO24)" )

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM) # Pin Location
	# GPIO.setmode(GPIO.BOARD)

	GPIO.setup(DATA_Pin, GPIO.OUT)
	GPIO.setup(CLK_Pin,  GPIO.OUT)

	GPIO.output(DATA_Pin, GPIO.LOW)
	GPIO.output(CLK_Pin,  GPIO.LOW)

def destroy():
    GPIO.cleanup()
    print ("cleanup GPIO.")

def line_notify(msg):
    token = "YhCkOGBQpwF6QZ5DrmMJ4lcFJ6zUR2De8SEel7AB2w7"
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": msg}
    requests.post(url, headers=headers, data=payload)


def loop():
    warning_flag = 0
    notify_flag = 0

    d_today = dt.now().strftime('%Y%m%d')
    logfile="/home/pi/mycode/logs/thlog" + d_today + ".log"   # logfile name

    while dt.now().hour < STOP_DETECT:
        ## 測定開始
        h,t = DHT.read_retry(SENSOR_TYPE, DHT_GPIO)

        ## 結果表示
        print (time.strftime("%H:%M:%S " ), end = "")
        print ("Temp= {0:0.1f} C " . format(t), end = "")
        print ("Humidity= {0:0.1f} % " . format(h), end = "")
        
        t = round(t,1)
        h = round(h,1)
        logmsg = time.strftime("%Y-%m-%d %H:%M:%S,") + str(t) + ',' + str(h) 

        ## WBGT Calc
        if t >= 28 and h >= 40:
            temp_index = round(t) - TMP_OFFSET
            hmd_index = round(h/5) - HUMD_OFFSET
            wbgt = WBGT_TBL[temp_index][hmd_index]
            logmsg = logmsg + ',' + str(wbgt)


            print(wbgt)
            if wbgt >= 25:
                warning_flag += 1
                if wbgt >= 28 and notify_flag == 0 :
                    wgbt_msg = "Alert! WBGT=" + str(wbgt) + time.strftime(" ,%Y-%m-%d %H:%M:%S,") + str(t) + "C, " + str(h)  + "%"
                    line_notify(wgbt_msg)
                    notify_flag = 10    # wait 10mins
                elif notify_flag > 0 :
                    notify_flag -= 1    
            else :  # Not warning
                if notify_flag > 0 :    # 
                    notify_flag -= 1
                warning_flag = 0

        else :  # Not calc WBGT
            warning_flag = 0
            print()

        logmsg = logmsg + "\n"
        fileobj = open (logfile,"a", encoding="utf_8") 
        fileobj.write(logmsg)
        fileobj.close()

        # client.publish(Topic, logmsg)
        if warning_flag == 0:
            wgbt_led = 0
        else:
            wgbt_led = WBGT_BAR[wbgt]

        send16bitData(CmdMode)
        sendLED(wgbt_led)
        latchData()

        time.sleep(SLEEP_NON)


if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be executed.
		print("end")
