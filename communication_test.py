from communication import *
import time


def test_receiver(address, port):
	sock = init_nonblocking_receiver(address, port)
	print 'Trying to receive messages from ' + address + ' on port ' + str(port) + '...' 
	try:
		while True:
                  message, addr = receive_message(sock)
                  if message != '':
                      print 'Received :' + message + ' from: ' + str(addr)
	except KeyboardInterrupt:
		print 'Stopped sending messages'
	
		
def test_localhost_receiver():
	test_receiver('127.0.0.1', 38234)

def test_sender(address, port):
	print 'Sending messages to ' + address + ' on port ' + str(port) + '...' 
	try:
		while True:
                  message = raw_input("Type message: ")
                  send_udp_unicast_message(address, port, message)
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
  
def test_cut_addr_to_id():
    try:
        while True:
            addr = raw_input("Type address with port in form [xx]x.[xx]x.[xx]x.[xx]x:xxxx")
            print str(cut_addr_to_id(addr))
    except KeyboardInterrupt:
        print "KeyboardInterrupt"
        
# tests broadcast, receiving and list handling        
def test_receive_message_list():
    port = 5001
    sock = init_nonblocking_receiver('', port)
    for x in range(1,4):
        send_broadcast_message(port, str(x))
    print receive_message_list(sock)

def test_update_state_list():
    state_list = []
    for x in range (0,12):
        state_list.append("RUN")
    port = 5001
    sock = init_nonblocking_receiver('', port)
    send_broadcast_message(port, "WARN")
    state_list = update_state_list(state_list, receive_message_list(sock))
    print state_list
    send_broadcast_message(port, "RUN")
    state_list = update_state_list(state_list, receive_message_list(sock))
    print state_list
    send_broadcast_message(port, "RUN")
    send_broadcast_message(port, "WARN")
    state_list = update_state_list(state_list, receive_message_list(sock))
    print state_list
    
#test_receive_message_list()
test_update_state_list()
