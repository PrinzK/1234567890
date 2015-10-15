import pi2go, time
import communication


start = time.time()
dist = 50
state = "RUN"
prev_state = state
pi2go.init()
try:
	while True:
		if time.time() - start > 0.15:
			dist = (int(pi2go.getDistance()*10))/10.0
			start = time.time()
		if dist > 30:
			state = "RUN"
		elif dist > 10:
			state = "WARN"
		else:
			state = "STOP"
			
		if state != prev_state:
			if state == "RUN":
				pi2go.setAllLEDs(4095,0,0)
			elif state == "WARN":
				pi2go.setAllLEDs(0,4095,0)
			elif state == "STOP":
				pi2go.setAllLEDs(0,0,4095)
			else:
				print "unknown state!"
			communication.send_broadcast_message(38234, state)
		print state
		prev_state = state
except KeyboardInterrupt:
	pass
finally:
	pi2go.cleanup()
		
				
	

