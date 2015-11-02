# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:43:35 2015

@author: christopher
"""

# Libraries
import communication
import pi2go
import time
from crashing_constants import *

# Initail Values
STATE = 'INIT'
MODE = 'STOP'
prev_MODE = 'STOP'
DISTANCE = 0
SQUAD = []
prev_messurement_time = 0
message_buffer_slave = []
message_buffer_master = []


# Programm
try:
    while True:
        
        if STATE == 'INIT':
            pi2go.init()
            sock = communication.init_nonblocking_receiver('',PORT)
            for x in range(SQUAD_SIZE):
                SQUAD.append(True)
                message_buffer_slave.append(True)
            OWN_IP = communication.get_ip()
            OWN_ID = communication.get_id_from_ip(OWN_IP)
            print OWN_ID
            STATE = 'RUNNING'


        elif STATE == 'RUNNING':
            # Distance         
            if time.time() - prev_messurement_time > WAIT_DIST:
                prev_messurement_time = time.time()                
                distance = pi2go.getDistance()
            
            # Obstacle = 1, No Obstacle = 0
            irCentre = pi2go.irCentre()
            
            # Obstacle Analysis
            if irCentre or (distance < DIST_MIN):
                distance_level = 0
            elif distance > DIST_MAX:
                distance_level = 2
            else:
                distance_level = 1
                
            # Receive
            data = 'new_round'
            while data != '':
                data, addr = communication.receive_message(sock) 
                if data != '':
                    ID = communication.get_id_from_ip(addr[0])
                    if ID == OWN_ID:
                        print 'OWN: ' , ID, ' : ' , data
                        continue
                    if ID >= SQUAD_START and ID <= SQUAD_START+SQUAD_SIZE:
                        print 'ROBOT: ', ID, ' : ' , data
                        if data == 'PROBLEM':
                            curr_STATUS = False
                            SQUAD[ID-SQUAD_START] = curr_STATUS
                        elif data == 'RELEASE':
                            curr_STATUS = True
                            SQUAD[ID-SQUAD_START] = curr_STATUS
                    else:
                        print 'MASTER:' , ID , ' : ' , data
                        # make List with Master commands an react on this
                        # change MODE, STATUS, SPEED, DISTANCELIMITS
                    
            # Analyse --> Calculate MODE
            prev_MODE = MODE
            if distance_level == 0:
                MODE = 'STOP'
            elif distance_level == 1 and all(SQUAD):
                MODE = 'SLOW'
            elif distance_level == 2 and all(SQUAD):
                MODE = 'RUN'
            elif distance_level != 0 and not all(SQUAD):
                MODE = 'WARN'
            else:
                print 'check MODE-Conditions'
                break
            
            # Set own SQUAD_VALUE  
            if MODE != prev_MODE:                          
                if MODE == 'STOP':
                    SQUAD[OWN_ID-SQUAD_START] = False
                else:
                    SQUAD[OWN_ID-SQUAD_START] = True

            # LEDs  
            if MODE != prev_MODE:                          
                if MODE == 'RUN':
                    pi2go.setAllLEDs(LED_OFF,LED_ON,LED_OFF)
                elif MODE == 'SLOW':
                    pi2go.setAllLEDs(LED_OFF,LED_OFF,LED_ON)
                elif MODE == 'WARN':
                    pi2go.setAllLEDs(LED_ON,LED_ON,LED_OFF)
                elif MODE == 'STOP':
                    pi2go.setAllLEDs(LED_ON,LED_OFF,LED_OFF)
                    
            # Distance controller
            if MODE == 'SLOW':
                SPEED_SLOW = SPEED_RUN - (DIST_REF-DISTANCE) * KP
                # Controlllimits
                if SPEED_SLOW > SPEED_CONTROL_MAX:
                    SPEED_SLOW = SPEED_CONTROL_MAX
                elif SPEED_SLOW < SPEED_CONTROL_MIN:
                    SPEED_SLOW = SPEED_CONTROL_MIN
                print 'DIST: ', DISTANCE , 'SPEED: ', SPEED_SLOW
                        
            
            # Motor
            if MODE != prev_MODE:                          
                if MODE == 'RUN':
                    SPEED = SPEED_RUN
                elif MODE == 'SLOW':
                    SPEED = SPEED_SLOW
                elif MODE == 'WARN':
                    SPEED = SPEED_WARN
                elif MODE == 'STOP':
                    SPEED = SPEED_STOP 
                # Speedlimits
                if SPEED > 100:
                    SPEED = 100
                elif SPEED < 0:
                    SPEED = 0
                pi2go.go(SPEED,SPEED)
                
            # Send
            if MODE != prev_MODE:                          
                if prev_MODE == 'STOP':
                    #print 'RELEASE'
                    message = 'RELEASE'
                    for x in range(SENDING_ATTEMPTS):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(WAIT_SEND)                    
                elif MODE == 'STOP':
                    #print 'PROBLEM'
                    message = 'PROBLEM'
                    for x in range(PUSH):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(WAIT_SEND)
       
        else:
            print 'impossible STATE'
            STATE == 'RUNNING'
            
except KeyboardInterrupt:
    print 'KEYBOARD'

finally:
    pi2go.stop()
    pi2go.cleanup()
    sock.close()
    print 'END'