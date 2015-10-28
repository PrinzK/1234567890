import multiprocessing
import communication
import time
import pi2go


def send_distance():
	while True:
		distance = (int(pi2go.getDistance()*10))/10.0
		communication.send_udp_unicast_message("127.0.0.1", 38235, str(distance))
		print "Sent distance: " + str(distance) + " at: %f " %time.time()
		time.sleep(0.1)

if __name__ == '__main__':
	pi2go.init()
	distance_process = multiprocessing.Process(name='send_distance', target=send_distance)
	distance_process.daemon = True
	distance_process.start()
	distance_socket = communication.init_nonblocking_receiver("127.0.0.1", 38235)
	try:
		while True:
			current_distance, addr = communication.receive_message(distance_socket)
			if current_distance != "":
				print " - Received distance: " + str(current_distance) + " at: %f " %time.time()
	except KeyboardInterrupt:
		print "Exciting! Exiting!"
		distance_process.join(0.2)
		pi2go.cleanup()
			
	
