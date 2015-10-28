import pi2go, time
import communication
import socket

# ROUTER "192.168.178.1"
UDP_IP = ""
UDP_PORT = 38234

sock = communication.init_nonblocking_receiver(UDP_IP, UDP_PORT)

LEDon = 4095
LEDoff = 0

pi2go.init()
pi2go.setAllLEDs(LEDoff, LEDoff, LEDoff)

state = 'RUN'
prev_state = 'STOP'
# state = 'RUN'  robot detect no obstacles
# state = 'STOP' robot detect an obstacles
# state = 'WARN' robot get message
 
try:
    while True:
		state = communication.receive_message(sock)
		#print "received message: " +  state + " at: %f" %time.time()
        #print "time: %f", %time.time() 
        
        # set LEDs
		if state != prev_state:
			print state
			if 'RUN' in state:
				pi2go.setAllLEDs(LEDoff, LEDon, LEDoff)      
			elif 'WARN' in state:
				pi2go.setAllLEDs(LEDon, LEDon, LEDoff)
			elif 'STOP' in state:
				pi2go.setAllLEDs(LEDon, LEDoff, LEDoff)
		prev_state = state
except KeyboardInterrupt:
    print 'KEYBOARD_STOPP'

finally:
    pi2go.cleanup()
    sock.close()
