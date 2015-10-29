# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:43:35 2015

@author: christopher
"""

# Libraries
import communication
import pi2go
import time


# Initail Values
STATE = 'INIT'
MODE = 'STOP'
prev_MODE = 'STOP'
DISTANCE = 0
SQUAD = []
prev_messurement_time = 0
message_buffer_slave = []
message_buffer_master = []

# Parameters
SPEED_RUN = 75
SPEED_SLOW = 50
SPEED_WARN = 25
SPEED_STOP = 0
SQUAD_SIZE = 20
LED_OFF = 0
LED_ON = 1000
PUSH = 5
PORT = 5005
BC_IP = '192.168.178.255'

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
            OWN_ID = communication.get_id()
            print OWN_ID
            STATE = 'RUNNING'


        elif STATE == 'RUNNING':
            # Distance         
            if time.time() - prev_messurement_time > 0.2:
                prev_messurement_time = time.time()                
                distance = pi2go.getDistance()
            
            # Obstacle = 1, No Obstacle = 0
            irCentre = pi2go.irCentre()
            
            # Obstacle Analysis
            if irCentre or (distance < 20):
                distance_level = 0
            elif distance > 40:
                distance_level = 2
            else:
                distance_level = 1
                
            # Receive
            data = 'new_round'
            while data != '':
                data, addr = communication.receive_message(sock) 
                ################ liste updaten wenn ID in SQUAD, Rest-ID's in andere Liste schreiben, Wiederholen bis der Buffer leer ist
                if data != '':
                    IP = addr[0]
                    ID = communication.get_id_from_addr(addr)
                    if ID == OWN_ID:
                        print 'OWN: ' , ID, ' : ' , data
                        continue
                    if ID >= 100 and ID <= 100+SQUAD_SIZE:
                        print 'ROBOT: ', ID, ' : ' , data
                        if data == 'PROBLEM':
                            curr_STATUS = False
                            SQUAD[ID-100] = curr_STATUS
                        elif data == 'RELEASE':
                            curr_STATUS = True
                            SQUAD[ID-100] = curr_STATUS
                    else:
                        print 'Master:' , ID , ' : ' , data
                    
            
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
            
            
            # Set SQUAD_VALUE  
            if MODE != prev_MODE:                          
                if MODE == 'STOP':
                    SQUAD[OWN_ID-100] = False
                else:
                    SQUAD[OWN_ID-100] = True

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
                pi2go.go(SPEED,SPEED)
                
            # Send
            if MODE != prev_MODE:                          
                if prev_MODE == 'STOP':
                    #print 'RELEASE'
                    message = 'RELEASE'
                    for x in range(PUSH):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(0.00001)                    
                elif MODE == 'STOP':
                    #print 'PROBLEM'
                    message = 'PROBLEM'
                    for x in range(PUSH):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(0.00001)
       
        else:
            print 'impossible STATE'
            pi2go.stop()
            break
            
except KeyboardInterrupt:
    print 'KEYBOARD'

finally:
    pi2go.stop()
    pi2go.cleanup()
    sock.close()
    print 'END'