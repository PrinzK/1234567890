import socket, sys

def send_message(port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	try:
		sock.sendto(message, ('<broadcast>', port))
		string = "message: \'" + message + "\' sent"
		return string
	except socket.timeout:
		return "Error while sending!"
	finally:
		sock.close()
	
