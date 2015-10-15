import communication
import socket

def test_receiver(address, port):
	sock = init_nonblocking_receiver(address, port)
	print 'Trying to receive messages from ' + address ' on port ' + port + '...' 
	try:
		while True:
			print communication.receive_message(sock)
	except KeyboardInterrupt:
		print 'Stopping sending messages'
	
		
def test_localhost_receiver():
	test_receiver('127.0.0.1', 38234)

def test_sender(address, port):
	print 'Sending messages to ' + address ' on port ' + port + '...' 
	try:
		while True:
			communication.send_unicast_message(address, port)
	except KeyboardInterrupt:
		print 'Stopping sending messages'
		
def test_localhost_sender():
	test_sender('127.0.0.1', 38234)
def test_broadcast_sender(port):
	
