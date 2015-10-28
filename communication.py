#!/usr/bin/python

import socket
import commands


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
		return "Sent: " + str(message) + " to " + str(address) + " on port " + str(port)
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
	addr = ""
	try:
		data, addr = sock.recvfrom(1024)
		# print "received message: " +  data + " at: %f" %time.time()
	except socket.error as e:
		#print e
		pass
	finally:
		return (data, addr)


def receive_message_list(sock):
	message_list = []
	cur_data, cur_addr = receive_message(sock)
	while cur_data != '':
		message_list.append((cur_data, cut_addr_to_id(cur_addr)))
		cur_data, cur_addr = receive_message(sock)
	return message_list


def cut_addr_to_id((addr, port)):
	ID = addr.split()[0][len(addr)-2:len(addr)-0]
	return int(ID)
		

def get_id():
	return int(commands.getoutput("/sbin/ifconfig").split("\n")[16].split()[1][18:])


def get_ip():
	return commands.getoutput("/sbin/ifconfig").split("\n")[16].split()[1][5:]


