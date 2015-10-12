import pi2go
import time
import threading
import Queue
import socket
import sys

def line_follower(run_event,in_q_dist, in_q_stop):
    
	# local variables
    dist = 0            # distance value in cm
    speed = 30          # speed value in %
    change = 15    
    curve = True        # Flag: Left = True, Right = False
    emergency_stop = False
	#start = time.time() # for avoiding time.sleep()
	
    while run_event.is_set():
        #print "line follower %f" %time.time()
        
        if not in_q_stop.empty():
			emergency_stop = in_q_stop.get()
        
        if in_q_dist.empty() == False:
            dist = in_q_dist.get()
        #print 'get dist: %f' %time.time()
		
        #if dist > 10 and (not emergency_stop): # move
        lock.aquire()
        if not emergency_stop: # move	
            left = pi2go.irLeftLine()
            right = pi2go.irRightLine()       
	        #print 'get ir: %f' %time.time()

            #Line Follower Logic: True = White, False = Black
            if left == False and right == False: # If both sensors detect the line -> forward
                pi2go.forward(80)
		#print 'area 0'                
            elif left == False and right == True: # If only the left sensor detect the line -> soft left curve
                pi2go.turnForward(40,90)
                curve = True
		#print 'area 1'
            elif left == True and right == False: # If only the right sensor detect the line -> soft right curve
                pi2go.turnForward(90,40)
                curve = False
		#print 'area -1'
            elif left == True and right == True: # If both sensors don't detect the line -> hard curve
                if curve == True:   # hard left curve
					pi2go.turnForward(10,100)
			#print 'area 2'
                else:               # hard right curve
                    pi2go.turnForward(100,10)
			#print 'area -2'


        else: # stop
            pi2go.stop()
        lock.release()
        # LED-Control
        if emergency_stop:
			pi2go.setAllLEDs(2000,2000,0)
		#	time.sleep(0.3)
		#	pi2go.setAllLEDs(0,0,0)
		#	time.sleep(0.3)
        elif dist < 10:
            pi2go.setAllLEDs(2000, 0, 0)
        elif dist > 20:
            pi2go.setAllLEDs(0, 0, 2000)
        else:
            pi2go.setAllLEDs(0, 2000, 0)

	#print 'end: %f' %time.time()	

def distance(run_event, out_q):
    start = time.time()
    curr_time = start
    dist = 15
    stop_sent = False
    while run_event.is_set():
        #print "dist %f" %time.time()
        #time.sleep(0.1)        
        curr_time = time.time()
        if curr_time - 0.1 > start:
			curr_time = start
			dist = (int(pi2go.getDistance()*10))/10.0
			out_q.put(dist)
	if dist < 10:
		broadcast('STOP')
		stop_sent = True
	if dist > 20 and stop_sent:
		broadcast('RESTART')
	       
def comm(run_event,out_q):
    udp_port = 5001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", udp_port))
    sock.settimeout(0.01)
    while run_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            if 'STOP' in str(data):
                print 'STOPPIGALOPPI'	
                out_q.put(True) # zu emergency_stop
            elif 'RESTART' in str(data):
				print 'ON WE GO!'
				out_q.put(False) # zu emergency_stop
            else:
				print data
        except socket.timeout:
			pass

def broadcast(message):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.sendto(message, ('<broadcast>', 5001))
    
if __name__ == "__main__":
    
    run_event = threading.Event()
    run_event.set()  
        
    pi2go.init()
    
    q_dist = Queue.Queue()
    q_stop = Queue.Queue()

    t1 = threading.Thread(target=line_follower, args=(run_event, q_dist, q_stop), name='line_follower')
    t2 = threading.Thread(target=distance, args=(run_event, q_dist), name='distance')
    t3 = threading.Thread(target=comm, args=(run_event, q_stop), name='comm')
    
    lock = threading.Lock()
    
    t1.start()
    t2.start()
    t3.start()
  
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
	#print 'vor run_event.clear()'
        run_event.clear()        
        t1.join()
        t2.join()
        #print 'vor t3.join()'
        t3.join()
        print 'end'
    
    finally: # Even if there was an error, cleanup
        pi2go.cleanup()
