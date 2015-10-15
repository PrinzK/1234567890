#!/bin/bash


DHCP_IP="192.168.178.$1"

echo "Starting setup script for host $DHCP_IP"
ping -c 1 $DHCP_IP 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" -ne "0" ]
then
	echo "Host could not be reached! \n aborting..."
	exit
fi

ssh-copy-id pi@$DHCP_IP 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" = "0" ]
then
	echo "Copying SSH-Key successfull!"
else
	echo "Copying SSH-Key NOT successfull! \n aborting..."
	exit
fi

ssh pi@$DHCP_IP 'sudo apt-get remove dhcpcd5' 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" = "0" ]
then
	echo "Removing DHCP Packages successful!"
else
	echo "Removing DHCP Packages NOT successful! \n aborting..."
	exit
fi

sudo scp /setup_robots/interfaces pi@$DHCP_IP:/etc/network/ 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" = "0" ]
then
	echo "Copied interfaces file"
else
	echo "Failed: Copying interfaces file \n aborting..."
	exit
fi

sudo scp /setup_robots/wpa_supplicant.conf pi@$DHCP_IP:/etc/wpa_supplicant/ 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" = "0" ]
then
	echo "Copied wpa_supplicant.conf file"
else
	echo "Failed: Copying wpa_supplicant.conf file \n aborting..."
	exit
fi

sudo scp /setup_robots/resolv.conf pi@$DHCP_IP:/etc/ 2>setup_robots/logfile.txt 1>setup_robots/logfile.txt
if [ "$?" = "0" ]
then
	echo "Copied resolv.conf file"
else
	echo "Failed: Copying resolv.conf file \n aborting..."
	exit
fi

ssh pi@$DHCP_IP 'sudo reboot'
