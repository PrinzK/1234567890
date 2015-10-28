# Libraries
import communication
import pi2go
import time

# Initail Values
STATE = 'INIT'
mode = ''
area = 10
prev_dist = 0
OWN_IP = communication.get_ip()
message = ''

# Parameters
speed = 50
change = 10 
#change = 17.5
BC_IP = '192.168.178.255'
PORT = 5005
LEDoff = 0
LEDon = 1000


# Programm
try:
    while True:
        #print STATE
        if STATE == 'INIT':
            prev_STATE = STATE
            #pi2go.cleanup()
            pi2go.init()
            sock = communication.init_nonblocking_receiver('',PORT)
            STATE = 'RECEIVE'


        elif STATE == 'RECEIVE':
            prev_STATE = STATE
            data, addr = communication.receive_message(sock)
            
            if OWN_IP in addr:
                data = ''
            if data != '':
                print data
            
            if data == 'PROBLEM':
                STATE = 'MODE'
            else:
                STATE = 'OBSTACLE'

       
        elif STATE == 'OBSTACLE':
            prev_STATE = STATE            
            cur_dist = time.time()            
            if cur_dist - prev_dist > 0.2:
                prev_dist = cur_dist                
                dist = pi2go.getDistance()
                print dist
            # Obstacle = 1, No Obstacle = 0
            centre = pi2go.irCentre()
            
            if centre or (dist < 20):
                # Distance not okay
                danger = True
            else:
                # Distance okay
                danger = False
            STATE = 'MODE'        


        elif STATE == 'MODE':
            prev_STATE = STATE            
            prev_mode = mode
                    
            if danger:
                mode = 'STOP'
            if data == 'PROBLEM':        
                mode = 'WARN'
            elif prev_mode == 'WARN' and data == 'OKAY':
                mode = 'RUN'
            elif prev_mode == 'STOP' and not danger:
                mode = 'RUN'
            elif mode == '':
                mode = 'RUN'
            #print mode
            #print danger
            STATE = 'LED'

 
        elif STATE == 'LED':
            prev_STATE = STATE
            if mode != prev_mode:                          
                if mode == 'RUN':
                    pi2go.setAllLEDs(LEDoff, LEDon, LEDoff)      
                elif mode == 'WARN':
                    pi2go.setAllLEDs(LEDon, LEDon, LEDoff)
                elif mode == 'STOP':
                    pi2go.setAllLEDs(LEDon, LEDoff, LEDoff)                
            STATE = 'LINE'

       
        elif STATE == 'LINE':
            prev_STATE = STATE
            prev_area = area 
            # Logik: White = 1 / BLACK = 0  
            left = pi2go.irLeftLine()
            right = pi2go.irRightLine() 
            # area = 11/10/00/01/11 == -2/-1/0/1/2       
            if left and right and (prev_area < 0):
                area = 0 #changed: -2
            elif left and not right:
                area = -1
            elif not left and not right:
                area = 0
            elif not left and right:
                area = 1
            elif left and right and (prev_area > 0):
                area = 0 #changed: ss2
            else:
                #print 'lost Line'
                #break           
                area = 0
            STATE = 'MOTOR'

        
        elif STATE == 'MOTOR':
            prev_STATE = STATE
            
            if mode == 'RUN':
                if (prev_mode != 'RUN') or (area != prev_area):
                    if area == 0:
                        leftspeed = speed
                        rightspeed = speed
                    elif area == -1:
                        leftspeed = speed + change
                        rightspeed = speed - change
                    elif area == 1:
                        leftspeed = speed - change
                        rightspeed = speed + change
                    else:
                        leftspeed = 0
                        rightspeed = 0
                        
                    if leftspeed < 0:
                        leftspeed = 0
                    elif leftspeed > 100:
                        leftspeed = 100
                    
                    if rightspeed < 0:
                        rightspeed = 0
                    elif rightspeed > 100:
                        rightspeed = 100
                        
                    pi2go.turnForward(leftspeed, rightspeed)
            
            else:
                if mode != prev_mode: 
                    pi2go.stop()
            
            if mode == 'STOP' or (mode == 'RUN' and prev_mode == 'STOP'):
                STATE = 'SEND'
            else:
                STATE = 'RECEIVE'


        elif STATE == 'SEND':
            prev_STATE = STATE
            if danger == True:
                message = 'PROBLEM'
                communication.send_broadcast_message(PORT, message)
                time.sleep(0.00001)
            elif danger == False:
                message = 'OKAY'
                for x in range(0,3):
                    communication.send_broadcast_message(PORT, message)
                    time.sleep(0.00001)
            
            STATE = 'RECEIVE'
 
           
        else:
            print 'impossible STATE'
            pi2go.stop()
            break
            
except KeyboardInterrupt:
    print 'KEYBOARD'

finally:
    pi2go.stop()
    sock.close()
    pi2go.cleanup()
    print 'END'
