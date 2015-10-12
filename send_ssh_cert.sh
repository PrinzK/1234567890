#!/bin/bash
# send files to all robots

IP_START=$1
ROBOT_COUNT=10
IP_END=$2
echo "Transmitting public key to Robots in IP-Range from 192.168.178.$IP_START to 192.168.178.$IP_END"
for ip_counter in $(seq $IP_START $IP_END)
do
	ping -c 1  192.168.178.$ip_counter -w1  2>/dev/null 1>/dev/null
	if [ "$?" = 0 ]
	then
		echo "Connection to 192.168.178.$ip_counter successfull!"
		ssh pi@192.168.178.$ip_counter 'mkdir ~/.ssh'
		cat ~/.ssh/id_rsa.pub | ssh pi@192.168.178.$ip_counter 'cat >> .ssh/authorized_keys'
	else
		echo "failed: 192.168.178.$ip_counter"
	fi
done

