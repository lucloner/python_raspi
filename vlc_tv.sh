#!/bin/sh
echo try ping
while [ -s $(ping -4 -c1 114.114.114.114 | grep '^rtt' | awk '{print $4}'| awk -F'/' '{print $3F}'| awk -F'.' '{print $1F}')]
do
	echo waiting
	sleep 10
done
/usr/bin/vlc -f -L http://ivi.bupt.edu.cn/hls/dftv.m3u8 