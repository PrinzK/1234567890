#!/usr/bin/python

import socket
import subprocess
import constants as c
import time


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

  
def send_x_broadcast_messages(port, message, x, time_between):
    for iteration in range(x):
        send_broadcast_message(port, message)
        time.sleep(time_between)   


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
 
def close_socket(sock):
    sock.close()

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
	ip = subprocess.check_output(['hostname', '-I'])
	return ip[:-2]


def get_id_from_ip(ip_addr):
  	return int(ip_addr.split('.')[3])


def get_id():
	ip = get_ip()
	return get_id_from_ip(ip)
 

def string_to_command(data):
    strings = data.split(' ')
    command = strings[0]
    if len(strings) > 1:
        value = strings[1]
    else:
        value = ''
    if (command == c.COMMAND_SPEED  or command == c.COMMAND_DIST) and value.isdigit():
        value = int(value)
    return (command,value)
