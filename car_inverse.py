import pi2go
import time
import threading
import Queue


def line_follower(run_event,in_q):
    
    # local variables
    dist = 0            # distance value in cm
    speed = 30          # speed value in %
    change = 15    
    curve = True        # Flag: Left = True, Right = False

    while run_event.is_set():
        #print "line follower %f" %time.time()
        
        if q.empty() == False:
            dist = in_q.get()
        #print 'get dist: %f' %time.time()
 
        if dist > 10: # move
            left = pi2go.irLeftLine()
            right = pi2go.irRightLine()       
	        #print 'get ir: %f' %time.time()

            #Line Follower Logic: True = White, False = Black
            if left == False and right == False: # If both sensors detect the line -> forward
                pi2go.forward(80)
		print 'area 0'                
            elif left == False and right == True: # If only the left sensor detect the line -> soft left curve
                pi2go.turnForward(40,90)
                curve = True
		print 'area 1'
            elif left == True and right == False: # If only the right sensor detect the line -> soft right curve
                pi2go.turnForward(90,40)
                curve = False
		print 'area -1'
            elif left == True and right == True: # If both sensors don't detect the line -> hard curve
                if curve == True:   # hard left curve
                    	pi2go.turnForward(5,100)
			print 'area 2'
                else:               # hard right curve
                    	pi2go.turnForward(100,5)
			print 'area -2'


        else: # stop
            pi2go.stop()

	#print 'end: %f' %time.time()	

def distance(run_event,out_q):
    while run_event.is_set():
        #print "dist %f" %time.time()
        time.sleep(0.1)        
        dist = (int(pi2go.getDistance()*10))/10.0
        out_q.put(dist)       
        
        # distance range
        if dist < 10:
            pi2go.setAllLEDs(2000, 0, 0)
        elif dist > 20:
            pi2go.setAllLEDs(0, 0, 2000)
        else:
            pi2go.setAllLEDs(0, 2000, 0)


if __name__ == "__main__":
    
    run_event = threading.Event()
    run_event.set()  
        
    pi2go.init()
    
    q = Queue.Queue()

    t1 = threading.Thread(target=line_follower, args=(run_event,q), name='line_follower')
    t2 = threading.Thread(target=distance, args=(run_event,q), name='distance')

    t1.start()
    t2.start()
  
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        run_event.clear()        
        t1.join()
        t2.join()
        print 'end'
    
    finally: # Even if there was an error, cleanup
        pi2go.cleanup()
