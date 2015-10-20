import pi2go
import time
import communication
import multiprocessing
from socket import error

LEDS_ON = 4095

def send_distance():
    try:
	while True:
		distance = (int(pi2go.getDistance()*10))/10.0
		communication.send_udp_unicast_message("127.0.0.1", 38235, str(distance))
		print "Sent distance: " + str(distance) + " at: %f " %time.time()
		time.sleep(0.1)
    except KeyboardInterrupt:
	pass

def line_follower():
    """
    State:
    L R
    1 1 - Both White  - Depends on P
    1 0 - Left White  - Turn Left
    0 1 - Right White - Turn Right
    0 0 - Both Black  - Go Forward

    P - previous State
    ------------------
    0 - Left
    1 - Right

    :return:
    """
    dist = 0
    speed = 70
    change = 20
    start = 0

    STATE = 00
    prev_STATE = 11
    DIST_STATE = 00
    prev_DIST_STATE = 11
    
    distance_socket = communication.init_nonblocking_receiver("127.0.0.1", 38235)
    
    while True:
        #print "line follower %f" %time.time()
        # print 'get dist: %f' % time.time()
        left = pi2go.irLeftLine()
        right = pi2go.irRightLine()
        # print 'get ir: %f' % time.time()
        if not left and not right:    # If both sensors are the on --> forward
            STATE = 00
        elif left and not right:          # If the left sensor is Off --> move right
            STATE = 10
        elif right and not left:         # If the right sensor is off --> move left
            STATE = 01
        else:
	    STATE = 11
        
        try:    
            received_distance, addr = communication.receive_message(distance_socket)
            if received_distance != "":
                dist = received_distance
		print " - Received distance: " + str(dist) + " at: %f " %time.time()
		if dist < 10:
		    print "SO CLOSE!"
		    DIST_STATE = 11
		elif dist > 40:
		    DIST_STATE = 00
		else:
		    DIST_STATE = 01
		    
        except error as e:
	    print "Houston experienced a problem: " + e

	if DIST_STATE == prev_DIST_STATE:
	    pass
	elif DIST_STATE == 00:
	    pi2go.setAllLEDs(0, LEDS_ON, 0)
	elif DIST_STATE == 01:
	    pi2go.setAllLEDs(LEDS_ON, LEDS_ON, 0)
	elif DIST_STATE == 11:
	    pi2go.setAllLEDs(LEDS_ON, 0, 0)
	    STATE = 11
        prev_DIST_STATE = DIST_STATE
        
        if STATE == prev_STATE:
            pass
        elif STATE == 00:
            pi2go.forward(speed)
        elif STATE == 10:
            pi2go.turnForward(speed + change, speed - change)
        elif STATE == 01:
            pi2go.turnForward(speed - change, speed + change)
        elif STATE == 11:
            pi2go.stop()
        prev_STATE = STATE

if __name__ == "__main__":
    pi2go.init()
    pi2go.cleanup()
    pi2go.init()
    distance_process = multiprocessing.Process(name='send_distance', target=send_distance)
    distance_process.daemon = True
    distance_process.start()
    

    try:
        line_follower()
    except KeyboardInterrupt:
        print 'end'
	distance_process.join(0.2)
    
    finally:
        pi2go.cleanup()
