import communication
import socket

def test_receiver(address, port)
	sock = init_nonblocking_receiver(address, port)
	communication.receive_message(sock)
		
def test_receiver()
	test_receiver('127.0.0.1', 38234)

def test_sender()
