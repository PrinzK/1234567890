import socket, sys

def receive_message(port, timeout):
	data, addr
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    sock.settimeout(timeout)
    try:
		data, addr = sock.recvfrom(1024)
	except socket.timeout:
		data = "Nothing received!"
	finally:
		sock.close()
    return (data, addr)
    
	
