#!/bin/sh
echo !!!===try ping===!!! > /home/pi/src/pyGpsd.log
while [ -s $(ping -4 -c1 114.114.114.114 | grep '^rtt' | awk '{print $4}'| awk -F'/' '{print $3F}'| awk -F'.' '{print $1F}')]
do
	echo waiting
	sleep 10
done
while :
do
	/usr/bin/python3 /home/pi/src/pyGpsd.py >> /home/pi/src/pyGpsd.log
	echo !!!===end===!!! >> /home/pi/src/pyGpsd.log
	sleep 1
done
