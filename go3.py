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
prev_STATE = ''
MODE = 'STOP'
prev_MODE = ''
DISTANCE = 0
SQUAD = []
prev_messurement_time_dist = 0
prev_measurement_time_switch = 0
prev_measurement_time_avoid = 0
prev_measurement_time_ramp = 0
message_buffer_slave = []
message_buffer_master = []
time_get_warning = 0
button_release = False
blocking_avoidance = False
ramp_active = False
temp = False
master_set_speed = False
master_set_LED = False
SPEED = 0

# Parameters
SPEED_RUN = 75
SPEED_SLOW = 50
SPEED_WARN = 25
SPEED_WARN_NEW = 25
SPEED_STOP = 0
SPEED_CONTROL_MAX = SPEED_RUN
SPEED_CONTROL_MIN = SPEED_SLOW
SQUAD_SIZE = 20
SQUAD_START = 100
DIST_MIN = 20
DIST_MAX = 50
DIST_REF = DIST_MAX
WAIT_DIST = 0.2
WAIT_SEND = 0.00001
WAIT_SWITCH = 0.1
WAIT_AVOID = 0.5  
WAIT_RAMP = 0.25
TIME_TO_STOP = 5
LED_ON = 1000
LED_OFF = 0
PUSH = 5
PORT = 5005
BROADCAST_IP = '192.168.178.255'
KP = float(SPEED_CONTROL_MAX - SPEED_CONTROL_MIN)/float(DIST_MAX-DIST_MIN)


# Programm
try:
    while True:


        
        if STATE == 'INIT':
            pi2go.init()
            pi2go.setAllLEDs(LED_ON,LED_ON,LED_ON)
            time.sleep(1)
            sock = communication.init_nonblocking_receiver('',PORT)
            for x in range(SQUAD_SIZE):
                SQUAD.append(True)
                message_buffer_slave.append(True)
            OWN_IP = communication.get_ip()
            OWN_ID = communication.get_id_from_ip(OWN_IP)
            #print 'ID:' , OWN_ID
            prev_STATE = STATE
            #STATE = 'IDLE'
            STATE = 'RUNNING'
            #print 'STATE:', STATE , 'RELEASE:', button_release

            

        if STATE == 'IDLE':
            if prev_STATE != 'IDLE':
                pi2go.setAllLEDs(LED_OFF,LED_OFF,LED_OFF)
                pi2go.stop()
            if time.time() - prev_measurement_time_switch > WAIT_SWITCH:
                prev_measurement_time_switch = time.time()
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    button_release = True
                if button and button_release:
                    button_release = False
                    prev_STATE = STATE
                    STATE = 'RUNNING'
                #print 'STATE:', STATE , 'RELEASE:', button_release , 'BUTTON:' , button


        elif STATE == 'RUNNING':
            # Distance         
            if time.time() - prev_messurement_time_dist > WAIT_DIST:
                prev_messurement_time_dist = time.time()                
                distance = pi2go.getDistance()
                print distance
            
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
                        #print 'OWN: ' , ID, ' : ' , data
                        continue
                    if ID >= SQUAD_START and ID <= SQUAD_START+SQUAD_SIZE:
                        #print 'ROBOT: ', ID, ' : ' , data
                        if data == 'PROBLEM':
                            curr_STATUS = False
                            SQUAD[ID-SQUAD_START] = curr_STATUS
                        elif data == 'RELEASE':
                            curr_STATUS = True
                            SQUAD[ID-SQUAD_START] = curr_STATUS
                    else:
                        #print 'MASTER:' , ID , ' : ' , data
                        ID, PARAM, VALUE = communication.string_to_command(data)
                        if ID == OWN_ID:
                            #print 'MasterID: ', ID , 'PARAM: ' , PARAM , 'VALUE: ' , VALUE
                            if PARAM == 'speed':
                                master_set_speed = True
                                prev_SPEED_RUN = SPEED_RUN
                                if VALUE == '+':
                                    SPEED_RUN += 1
                                elif VALUE == '-':
                                    SPEED_RUN -= 1
                                else:
                                    SPEED_RUN = VALUE
                                print 'Set SPEED_RUN from '+ str(prev_SPEED_RUN) + ' to ' + str(SPEED_RUN)           
                            elif PARAM == 'dist':
                                prev_DIST_MIN = DIST_MIN
                                DIST_MIN = VALUE
                               # print 'Set DIST_MIN from '+ str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)           
                            elif PARAM == 'led':
                                master_set_LED = True
                                prev_LED_ON = LED_ON
                                LED_ON = VALUE
                                if LED_ON > 4095:
                                    LED_ON = 4095
                                elif LED_ON < 0:
                                    LED_ON = 0
                                print 'Set LED_ON from '+ str(prev_LED_ON) + ' to ' + str(LED_ON)
                            elif PARAM == 'mode':    
                                print 'master want to change MODE'
                        # change MODE, STATUS, SPEED, DISTANCELIMITS#
                                    
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
            if MODE != prev_MODE or master_set_LED:
                if master_set_LED:
                    master_set_LED = False
                if MODE == 'RUN':
                    pi2go.setAllLEDs(LED_OFF,LED_ON,LED_OFF)
                elif MODE == 'SLOW':
                    pi2go.setAllLEDs(LED_OFF,LED_OFF,LED_ON)
                elif MODE == 'WARN':
                    pi2go.setAllLEDs(LED_ON,LED_ON,LED_OFF)
                elif MODE == 'STOP':
                    pi2go.setAllLEDs(LED_ON,LED_OFF,LED_OFF)


            # Ramp in Warning-Mode
            if MODE == 'WARN':
                if prev_MODE != 'WARN':
                    time_get_warning = time.time()
                    speed_get_warning = SPEED
                    SPEED_WARN = SPEED_RUN

                new_value = round(speed_get_warning * (1-(time.time()-time_get_warning)/TIME_TO_STOP),1)
                if new_value != SPEED_WARN:
                    SPEED_WARN = new_value
                    if SPEED_WARN < 20:
                        SPEED_WARN = 20
                    #print SPEED_WARN
                    temp = True


                if time.time() - prev_measurement_time_ramp > WAIT_RAMP and temp:
                    prev_measurement_time_ramp = time.time()
                    ramp_active = True
                    temp = False


            # Blocking Avoidance
            if MODE == 'SLOW':
                error = DIST_REF - distance
                SPEED_SLOW = round(SPEED_RUN - error * KP,1)
                # Controlllimits
                if SPEED_SLOW > SPEED_CONTROL_MAX:
                    SPEED_SLOW = SPEED_CONTROL_MAX
                elif SPEED_SLOW < SPEED_CONTROL_MIN:
                    SPEED_SLOW = SPEED_CONTROL_MIN
                if time.time() - prev_measurement_time_avoid > WAIT_AVOID:
                    prev_measurement_time_avoid = time.time()
                    blocking_avoidance = True

                    
            # Motor
            if MODE != prev_MODE or master_set_speed or blocking_avoidance or ramp_active:
                if master_set_speed:
                    master_set_speed = False                          
                if MODE == 'RUN':
                    SPEED = SPEED_RUN
                elif MODE == 'SLOW':
                    SPEED = SPEED_SLOW
                    if blocking_avoidance:
                        print 'speed_avoidance' , SPEED
                    blocking_avoidance = False
                elif MODE == 'WARN':
                    SPEED = SPEED_WARN
                    ramp_active = False
                elif MODE == 'STOP':
                    SPEED = SPEED_STOP 
                # Speedlimits
                if SPEED > 100:
                    SPEED = 100
                elif SPEED < 0:
                    SPEED = 0
                #print 'MODE: ', MODE , 'SPEED: ', SPEED , 'DIST: ' , distance
                pi2go.go(SPEED,SPEED)
                
            # Send
            if MODE != prev_MODE:                          
                if prev_MODE == 'STOP':
                    #print 'RELEASE'
                    message = 'RELEASE'
                    for x in range(PUSH):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(WAIT_SEND)                    
                elif MODE == 'STOP':
                    #print 'PROBLEM'
                    message = 'PROBLEM'
                    for x in range(PUSH):
                        communication.send_broadcast_message(PORT, message)
                        time.sleep(WAIT_SEND)

            # Button
            if time.time() - prev_measurement_time_switch > WAIT_SWITCH:
                prev_measurement_time_switch = time.time()
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    button_release = True
                if button and button_release:
                    button_release = False
                    prev_STATE = STATE
                    STATE = 'IDLE'
                #print 'STATE:', STATE , 'RELEASE:', button_release , 'BUTTON:' , button

        
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