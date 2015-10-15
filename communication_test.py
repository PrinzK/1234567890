from communication import *
import time


def test_receiver(address, port):
	sock = init_nonblocking_receiver(address, port)
	print 'Trying to receive messages from ' + address + ' on port ' + port + '...' 
	try:
		while True:
			print receive_message(sock)
	except KeyboardInterrupt:
		print 'Stopped sending messages'
	
		
def test_localhost_receiver():
	test_receiver('127.0.0.1', 38234)

def test_sender(address, port):
	print 'Sending messages to ' + address + ' on port ' + port + '...' 
	try:
		while True:
			send_unicast_message(address, port)
	except KeyboardInterrupt:
		print 'Stopping sending messages'
		
def test_localhost_sender():
	test_sender('127.0.0.1', 38234)
	
def test_broadcast_sender(port):
	try:
		while True:
			message = raw_input("Broadcast message to sent: ")
			for x in range(0,3):
				send_broadcast_message(port, message + str(x))
						
	except KeyboardInterrupt:
		print 'Stopped sending messages'
