##!/bin/bash
# send files to all robots

FILE=$1
IP_START=101
ROBOT_COUNT=2
IP_END=$(($IP_START+$ROBOT_COUNT))
echo "Transmitting $FILE to Robots in IP-Range from 192.168.178.$IP_START to 192.168.178.$IP_END"
for ip_counter in $(seq $IP_START $IP_END)
do
	# ping  192.168.178.$ip_counter  # 2>/dev/null 1>/dev/null
	if [ 0 = 0 ]
	then
		echo "Connection to 192.168.178.$ip_counter successfull!"
		scp  $FILE pi@192.168.178.$ip_counter:./pi2go >> filename
		
	else
		echo "failed: 192.168.178.$ip_counter"
	fi
done

