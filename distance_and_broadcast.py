import pi2go, time
import communication
#from __future__ import print_function

DIST_RUN = 40
DIST_STOP = 15
LEDon = 1024
LEDoff = 0
TIME_BETWEEN_MEASUREMENT = 0.2
PORT = 38234
#states
STATE_STOP = 00
STATE_WARN = 01
STATE_RUN = 11
OWN_IP = communication.get_ip()

start = time.time()
dist = 50
state = "RUN"
prev_state = state
data = ''

pi2go.init()
pi2go.cleanup()
pi2go.init()

sock = communication.init_nonblocking_receiver('', PORT)
#log = open(senseless_log)

try:
	while True:
		if time.time() - start > TIME_BETWEEN_MEASUREMENT:
			#print("Starting distance measuring", file = log)
			#print "Starting distance measuring"
			#dist = 5+4
			dist = (int(pi2go.getDistance()*10))/10.0
			start = time.time()
			#print "Distance measuring finished"
			
		data_buf, addr = communication.receive_message(sock)
		if "State" in data_buf and not OWN_IP in addr:
			data = data_buf
			print data
			#print "OWN_IP: " + OWN_IP
			#print "addr: " + str(addr)
		
			
		
		if dist < DIST_STOP:
			state = STATE_STOP
			state_string = "STOP"
		elif dist < DIST_RUN or ("WARN" in data and not OWN_IP in addr):
			state = STATE_WARN
			state_string = "WARN"
		else:
			state = STATE_RUN
			state_string = "RUN"
			
		if state != prev_state:
			print state_string
			if state == STATE_RUN:
				pi2go.setAllLEDs(LEDoff,LEDon,LEDoff)
			elif state == STATE_WARN:
				pi2go.setAllLEDs(LEDon,LEDon,LEDoff)
			elif state == STATE_STOP:
				pi2go.setAllLEDs(LEDon,LEDoff, LEDoff)
			else:
				print "unknown state!"
			#print time.time()
			#message = "State: " + state + " at " + str(time.time())
			print "Starting broadcast"
			for x in range(0,10):
				message = "    State: " + state_string + " at " + str(time.time()) + " #" + str(x)
				communication.send_broadcast_message(38234, message)
			#print time.time()
			print "Broadcast finished"
		prev_state = state
except KeyboardInterrupt:
	pass
finally:
	pi2go.cleanup()
		
				
	

