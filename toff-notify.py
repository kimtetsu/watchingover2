#!/usr/bin/env python
#-*- coding: utf-8 -*-
import csv
import requests
from datetime import date, timedelta, datetime as dt


def line_massage(msg):
    token = "YhCkOGBQpwF6QZ5DrmMJ4lcFJ6zUR2De8SEel7AB2w7"
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": msg}
    requests.post(url, headers=headers, data=payload)


toff_table = []
cnt = 0

yesterday = date.today() - timedelta(days=1) 
d_today = yesterday.strftime('%Y%m%d')
# d_today ="20200730"
logfile = "/home/pi/mycode/logs/plog" + d_today + ".log"   # logfile name
print (d_today)

cnt=0
toff_flag = 0
with open (logfile,"r", encoding="utf_8") as fileobj:
    #print(fileobj.read())
    reader = csv.reader(fileobj)
    for row in reader :
        print(row)
        if int(row[1]) > 30:
            toff_flag = 0
        else :
            if toff_flag ==0 : # first low level
                toff_time = row[0]
                toff_flag =1
            elif toff_flag < 5 : # 2nd-4th low level
                toff_flag +=1
            elif toff_flag == 5 : # 5th low level
                toff_table.append(toff_time)
                toff_flag +=1
                cnt +=1
            elif toff_flag > 5 : # after 6th low level
                toff_flag +=1         



sumfile = "/home/pi/mycode/logs/lightoff_sum.log"
with open (sumfile,"r", encoding="utf_8") as fileobj:
    l = fileobj.readlines()
smsg = ""
for toff_time in toff_table:
    smsg = smsg + toff_time + ','
smsg = smsg[:-1]
smsg = smsg + '\n'
l.insert(0,smsg)

with open (sumfile,"w", encoding="utf_8") as fileobj:
    # print(sline)
    fileobj.writelines(l)


# yesterday = date.today() - timedelta(days=1) 
# yesterday=today-oneday

loff_message = "Light Off " + yesterday.strftime('%Y-%m-%d ') + str(cnt) + "times "
loff_message = loff_message +smsg

line_massage(loff_message)


