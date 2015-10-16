import pi2go, time
import socket

# ROUTER "192.168.178.1"
UDP_IP = ""
UDP_PORT = 5010
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP,UDP_PORT))

LEDon = 4095
LEDoff = 0

pi2go.init()
pi2go.setAllLEDs(LEDoff, LEDoff, LEDoff)

state = 'RUN'
prev_state = 'STOPP'
# state = 'RUN'  robot detect no obstacles
# state = 'STOP' robot detect an obstacles
# state = 'WARN' robot get message
 
try:
    while True:
        data, addr = sock.recvfrom(1024)
        print "time: ", time.time() 
        print "received message:", data
        #print "address:", address
        
        # set LEDs
        if state != prev_state:
			print state
            if state == 'RUN':
                pi2go.setAllLEDs(LEDoff, LEDon, LEDoff)      
            elif state == 'WARN':
                pi2go.setAllLEDs(LEDoff, LEDoff, LEDon)
            elif state == 'STOP':
                pi2go.setAllLEDs(LEDon, LEDoff, LEDoff)
        prev_state = state

except KeyboardInterrupt:
    print 'KEYBOARD_STOPP'

finally:
    pi2go.cleanup()
