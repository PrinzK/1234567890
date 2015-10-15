import pi2go, time
import socket

# ROUTER "192.168.178.1"
UDP_IP = ""
UDP_PORT = 5010

sock = init_nonblocking_receiver("", UDP_PORT)

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
        data = receive_message(sock)
        #print "time: %f", %time.time() 
        print "received message:", data
        #print "address:", address
        state = data       
        # set LEDs
        if state != prev_state:
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
