#!/usr/bin/python

import socket, sys

def send_broadcast_message(port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	try:
		sock.sendto(message, ('192.168.178.255', port))
		string = "message: \'" + message + "\' sent"
		return string
	except socket.error:
		return "Error while sending!"
	finally:
		sock.close()

def send_udp_unicast_message(address, port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.sendto(message, (address, port))
		return "Sent: " + message + " to " + address + " on port " + port
	except socket.error as e:
		return "Error while sending : ",e
	finally:
		sock.close()

def init_receiver(address, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((address, port))
	return sock
	
def init_nonblocking_receiver(address, port):
	sock = init_receiver(address, port)
	sock.setblocking(0)
	return sock
	
def init_blocking_receiver(address, port, timeout):
	sock = init_receiver(address, port)
	sock.settimeout(timeout)
	return sock
	
def receive_message(sock):
	data = ""
	try:
		data, addr = sock.recvfrom(1024)
		#print "received message: " +  data + " at: %f" %time.time()
	except socket.error as e:
		#print e
		pass
	finally:
		return data
