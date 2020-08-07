#!/usr/bin/env python
import ADC0832
import time
from datetime import datetime as dt


SLEEP_NEXT = 60

def init():
	ADC0832.setup()

def loop():
	STOP_DETECT = 5		# Stop at AM5 
	
	d_today = dt.now().strftime('%Y%m%d')
	logfile = "/home/pi/mycode/logs/plog" + d_today + ".log"   # logfile name

	while dt.now().hour != STOP_DETECT :
		res = ADC0832.getResult() - 80
		if res < 0:
			res = 0
		if res > 100:
			res = 100
		#print ('res = %d' % res)
		


		logmsg = time.strftime("%Y-%m-%d %H:%M:%S,") + str(res) + "\n"
		print(logmsg, end="")
		fileobj = open (logfile,"a", encoding="utf_8") 
		#fileobj.write(time.strftime("%Y-%m-%d %H:%M:%S,"))
		fileobj.write(logmsg)
		fileobj.close()
		time.sleep(SLEEP_NEXT)


if __name__ == '__main__':
	init()
	try:
		loop()
	except KeyboardInterrupt: 
		ADC0832.destroy()
		print ('The end !')
