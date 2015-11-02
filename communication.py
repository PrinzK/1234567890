#!/usr/bin/python

import socket
import subprocess
<<<<<<< HEAD
=======

>>>>>>> 0be388872b37da8739d15f33c16bcc8731c55636


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
		message_list.append((cur_data, get_id_from_ip(cur_addr)))
		cur_data, cur_addr = receive_message(sock)
	return message_list


def get_ip():
<<<<<<< HEAD
	ip = subprocess.check_output(['hostname', '-I'])
 	ip = ip[:-2]
	return ip


def get_id_from_ip(ip_addr):
  	x = ".".join(ip_addr.split('.')[0:-1]) + '.'
   	identifier = int(ip_addr.replace(x,''))
	return identifier


def get_id():
	ip = get_ip()
   	identifier = get_id_from_ip(ip)
	return identifier
=======
	IP = subprocess.check_output(['hostname', '-I'])
 	IP = IP[:-2]
	return IP


def get_id():
	IP = get_ip()
  	x = ".".join(IP.split('.')[0:-1]) + '.'
   	ID = int(IP.replace(x,''))
  	#ID = int(IP[-3:])
	return ID


def get_id_from_ip(addr):
	IP = addr[0]
  	x = ".".join(IP.split('.')[0:-1]) + '.'
   	ID = int(IP.replace(x,''))
	return ID
>>>>>>> 0be388872b37da8739d15f33c16bcc8731c55636
 

def string_to_command(data):
	try:
		command = data.split()
		identifier = int(command[0])
		parameter = command[1]
		value = int(command[2])
	except:
		identifier = 0
		parameter = ''
		value = 0
	return (identifier,parameter,value)