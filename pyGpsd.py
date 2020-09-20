#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#   http://yingyan.baidu.com/api/v3/track/addpoint
#   ak                      9OOSFllyelB4Ph9vcyIThPVajcHzyHLf
#   service_id              223512
#   entity_name             big_raspi
#   latitude                纬度
#   longitude               经度
#   loc_time                时间  utc时间0时区
#   coord_type_input        wgs84
#   speed                   速度  米每秒
#   direction               方向
#   height                  海拔
#   radius                  精度
#   object_name             X
#   column-key              X
#   sn
#   SK：tp2OtcwKmOMs51z6F8uFtUBKGuDKsoDG
# 第一行必须有，否则报中文字符非ascii码错误
import urllib
import urllib.parse
import hashlib
import http.client
import json
import time
#import sys

from gps3 import agps3

# 以get请求为例http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak
queryUrl='yingyan.baidu.com'
query_ak='9OOSFllyelB4Ph9vcyIThPVajcHzyHLf'
queryStr = '/api/v3/track/addpoint'
query_sk='tp2OtcwKmOMs51z6F8uFtUBKGuDKsoDG'
query_service_id='223512'
query_entity_name='big_raspi'
coord_type_input='wgs84'

# 参数
p_latitude=0.0
p_longitude=0.0
p_speed=0.0
p_direction=0.0
p_height=0.0
p_radius=0.0
p_time=''

def calc_sn(url):
    # 对queryStr进行转码，safe内的保留字符不转换
    # 在最后直接追加上yoursk
    # md5计算出的sn值7de5a22212ffaa9e326444c75a58f9a0
    # 最终合法请求url是http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak&sn=7de5a22212ffaa9e326444c75a58f9a0

    global query_sk
    encodedStr = urllib.parse.quote(url, safe="/:=&?#+!$,;'@()*[]")
    rawStr = encodedStr + query_sk
    sn=hashlib.md5(urllib.parse.quote_plus(rawStr).encode("utf-8")).hexdigest()
    url=url+'&sn='+sn
    print(rawStr+'-->'+sn)
    return sn

sleep_time=1
last_time=0

datalist={}
def upload():
    global queryUrl
    global queryStr
    global query_ak
    global query_entity_name
    global query_service_id
    global coord_type_input

    global p_direction
    global p_height
    global p_latitude
    global p_longitude
    global p_radius
    global p_speed
    global p_time

    global datalist
    global sleep_time
    global last_time

    utc=time.strptime(p_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    #换算中国时区
    p_utc = int(time.mktime(utc))
    p_utc+=28800

    if int(last_time)>int(p_utc):
        last_time=0
        sleep_time=0
        print('skip:{0}+{1}->{2}'.format(last_time,sleep_time,p_utc))
        return {}

    header = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}

    datalist = {
    'coord_type_input':coord_type_input,
    'direction':int(p_direction),
    'entity_desc':query_entity_name,
    'entity_name':query_entity_name,
    'height':p_height,
    'latitude':p_latitude,
    'loc_time':p_utc,
    'longitude':p_longitude,
    'radius':p_radius,
    'service_id':query_service_id,
    'speed':3600*p_speed/1000
    }

    body='ak='+query_ak
    for k,v in datalist.items():
        body+=('&{0}={1}'.format(k,v))

    if 'n/a' in body:
        print('data n/a!')
        last_time=0
        sleep_time=0
        return {}
    
    test_queryStr=queryStr+'?'+body
    sn=calc_sn(test_queryStr)
    body+='&sn='+sn
    print(body)

    conn = http.client.HTTPConnection(queryUrl)
    req = conn.request('POST', queryStr, body, header)
    print(conn.getresponse().read().decode())
    print('===')
    last_time=int(p_utc)+int(sleep_time)-2
    return datalist

running = True

def bedtime(old_data,new_data):
    global sleep_time
    
    if sleep_time<1:
        sleep_time=1
    time=sleep_time+0.1

    if 'speed' not in new_data:
        return time+2
    elif 'speed' not in old_data:
        return time+1
    
    speed=new_data['speed']
    if speed=='n/a':
        return time*2
    elif speed>27:
        return 1
    elif speed>16:
        time*=0.9
    elif speed<1.3:
        return time+60
    elif speed<5:
        time+=10
    elif speed<11:
        time+=1
    elif speed<time:
        time-=1

    direction=old_data['direction']-new_data['direction']
    speed-=old_data['speed']
    if abs(direction)<3 or abs(speed)<1:
        time*=2-speed/100
    elif abs(direction)<5 or abs(speed)<2:
        time*=1.1
    else:
        time=1

    if time<1:
        time=1
    elif time>90:
        time=90+time/1000
    elif time>60:
        time=60+time/10

    return time
    

def getPositionData(gps):
    global p_direction
    global p_height
    global p_latitude
    global p_longitude
    global p_radius
    global p_speed
    global p_time

    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    nx = agps3.DataStream()
    nx.unpack(new_data)
    #if nx['class'] == 'TPV':
    p_latitude = getattr(nx,'lat', p_latitude)
    p_longitude = getattr(nx,'lon', p_longitude)
    p_direction = getattr(nx,'track', p_direction)
    p_height = getattr(nx,'alt', p_height)
    p_radius = getattr(nx,'epv', p_radius)
    p_speed = getattr(nx,'speed', p_speed)
    p_time = getattr(nx,"time",p_time)

    if p_height=='n/a':
        p_height=0
    if p_radius=='n/a':
        p_radius=0
    if p_speed=='n/a':
        p_speed=0

    print("Your position: lon = " + str(p_longitude) + ", lat = " + str(p_latitude)+'[d:'+str(p_direction)+' h:'+str(p_height)+' s:'+str(p_speed)+' r:'+str(p_radius)+' t:'+p_time)

gps_socket = agps3.GPSDSocket()
gps_socket.connect()
gps_socket.watch()
try:
    print("Application started!")
    while running:
        #getPositionData(gpsd)
        for new_data in gps_socket:
            if new_data:
                getPositionData(new_data)
                break
            #print('.')
        print('==='+str(sleep_time))
        time.sleep(1)
        if p_time=='n/a':
            continue
        try:
            old=datalist
            new=upload()
            sleep_time=bedtime(old,new)
        except(Exception):
            print('upload error!')

except (KeyboardInterrupt):
    running = False
    print("Applications closed!")
