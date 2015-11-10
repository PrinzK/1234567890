# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:43:35 2015

@author: christopher
"""

# Libraries
import communication as com
import constants as c
import pi2go
import time

# Initail Values
state = 'INIT'
prev_state = ''
mode = 'STOP'
prev_mode = ''

speed = 0
distance = 0
warning = []
last_time = 0

times = []
times.append(['prev_get_dist',0.0])
times.append(['prev_get_switch',0.0])
times.append(['prev_set_motor',0.0])
times.append(['get_warning',0.0])
times.append(['prev_set_LED',0.0])
      
flags = []
flags.append(['set_motor',False])
flags.append(['button_release',False])
flags.append(['master_set_speed',False])
flags.append(['masater_set_button',False])
flags.append(['master_set_LED',False])
flags.append(['status_warn_LED',False])

def find_element(list_2D,element):
    for x in range(len(list_2D)):
        if list_2D[x][0] == element:
            row = x
            break
        else:
            row = []
    return row


def get_element(list_2D,element):
    row = find_element(list_2D,element)
    value = list_2D[row][1]
    return value
    
    
def set_element(list_2D,element,value):
    row = find_element(list_2D,element)
    list_2D[row][1] = value
    return list_2D 


def check_time_limit(list_2D,element,limit):
    if time.time() - get_element(list_2D,element) > limit:
        set_element(list_2D,element,time.time())
        return True
    else:
        return False

def send_new_status(msg,repetitions,space):
    for x in range(repetitions):
        com.send_broadcast_message(c.PORT, msg)
        time.sleep(space)  
        
    
# Parameters
SPEED_RUN = c.SPEED_RUN
SPEED_MIN = 20
SPEED_WARN = c.SPEED_WARN
SPEED_CONTROL_MAX = c.SPEED_CONTROL_MAX
SPEED_CONTROL_MIN = c.SPEED_STOP
DIST_MIN = c.DIST_MIN

# Programm
try:
    while True:

        if state == 'INIT':
            pi2go.init()
            pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_ON)
            time.sleep(1)
            sock = com.init_nonblocking_receiver('',c.PORT)
            for x in range(c.TEAM_SIZE):
                warning.append(True)
            OWN_IP = com.get_ip()
            OWN_ID = com.get_id_from_ip(OWN_IP)
            #print 'ID:' , OWN_ID
            prev_state = state
            #state = 'IDLE'
            state = 'RUNNING'


        if state == 'IDLE':
            if prev_state != 'IDLE':
                pi2go.setAllLEDs(c.LED_OFF,c.LED_OFF,c.LED_OFF)
                pi2go.stop()
            if check_time_limit(times,'prev_get_switch',c.WAIT_SWITCH):
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    set_element(flags,'button_release',True)
                if button and get_element(flags,'button_release'):
                    set_element(flags,'button_release',False)
                    prev_state = state
                    state = 'RUNNING'
                

        elif state == 'RUNNING':
            # Distance
            if check_time_limit(times,'prev_get_dist',c.WAIT_DIST):
                distance = pi2go.getDistance()
                time_between = time.time() - last_time
                print 'dt:', time_between , distance
                last_time = time.time()
            
            # Obstacle = 1, No Obstacle = 0
            irCentre = pi2go.irCentre()
            
            # Obstacle Analysis
            if irCentre or (distance < DIST_MIN):
                distance_level = 0
            elif distance > c.DIST_MAX:
                distance_level = 2
            else:
                distance_level = 1

                
            # Receive
            data = 'new_round'
            while data != '':
                data, addr = com.receive_message(sock) 
                if data != '':
                    sender_ID = com.get_id_from_ip(addr[0])
                    if sender_ID == OWN_ID:
                        #print 'OWN: ' , sender_ID, ' : ' , data
                        continue
                    if sender_ID >= c.TEAM_START and sender_ID <= c.TEAM_END:
                        print 'ROBOT: ', sender_ID, ' : ' , data , sender_ID-c.TEAM_START
                        if data == 'PROBLEM':
                            warning[sender_ID-c.TEAM_START] = False
                        elif data == 'RELEASE':
                            warning[sender_ID-c.TEAM_START] = True
                    else:
                        print 'MASTER:' , sender_ID , ' : ' , data
                        sender_ID, PARAM, VALUE = com.string_to_command(data)
                        if sender_ID == OWN_ID:
                            #print 'MasterID: ', ID , 'PARAM: ' , PARAM , 'VALUE: ' , VALUE
                            if PARAM == 'speed':
                                set_element(flags,'master_set_speed',True)
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
                            elif PARAM == 'mode':    
                                print 'master want to change MODE'
                        # change MODE, STATUS, SPEED, DISTANCELIMITS#
                #print warning
                                    
            # Analyse --> Calculate MODE
            if prev_state == 'RUNNING':                
                prev_mode = mode
            if distance_level == 0:
                mode = 'STOP'
            elif distance_level == 1 and all(warning):
                mode = 'SLOW'
            elif distance_level == 2 and all(warning):
                mode = 'RUN'
            elif distance_level != 0 and not all(warning):
                mode = 'WARN'
            else:
                print 'check MODE-Conditions'
                break

            
            # Set own Warning-Flag                           
            if mode == 'STOP':
                warning[OWN_ID-c.TEAM_START] = False
            else:
                warning[OWN_ID-c.TEAM_START] = True


            # LEDs  
            if mode != prev_mode or get_element(flags,'master_set_LED'):
                if get_element(flags,'master_set_LED'):
                    set_element(flags,'master_set_speed',False)
                if mode == 'RUN':
                    pi2go.setAllLEDs(c.LED_OFF,c.LED_ON,c.LED_OFF)
                elif mode == 'SLOW':
                    pi2go.setAllLEDs(c.LED_OFF,c.LED_OFF,c.LED_ON)
                #elif mode == 'WARN':
                    #pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                elif mode == 'STOP':
                   pi2go.setAllLEDs(c.LED_ON,c.LED_OFF,c.LED_OFF)
            # Blinking-Mode
            if mode == 'WARN':
                if check_time_limit(times,'prev_set_LED',c.WAIT_LED):
                    if get_element(flags,'status_warn_LED'):
                        pi2go.setAllLEDs(c.LED_OFF,c.LED_OFF,c.LED_OFF)
                        set_element(flags,'status_warn_LED',False)
                    else:
                        pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                        set_element(flags,'status_warn_LED',True)
                        
                

            # Calculate new speed
            if mode == 'RUN':
                if prev_mode != 'RUN' or get_element(flags,'master_set_speed'):
                    speed = SPEED_RUN
                    set_element(flags,'master_set_speed',False)
                    set_element(flags,'set_motor',True)
            
            # Blocking Avoidance
            elif mode == 'SLOW':
                #linear
                gradient = float(SPEED_RUN - SPEED_MIN)/float(c.DIST_MAX-DIST_MIN)
                error = c.DIST_MAX - distance
                new_value = round(SPEED_RUN - error * gradient,1)               
                
                if new_value < SPEED_MIN:
                    new_value = SPEED_MIN
                elif new_value > c.SPEED_CONTROL_MAX:
                    new_value = c.SPEED_CONTROL_MAX
                                 
                if new_value != speed:
                    speed = new_value
                    set_element(flags,'set_motor',True)
            
            
            # Slow-Down in Warning-Mode    
            elif mode == 'WARN':
                if prev_mode != 'WARN':
                    set_element(times,'get_warning',time.time())
                    speed_get_warning = speed
                new_value = round(speed_get_warning * (1-(time.time()-get_element(times,'get_warning'))/c.TIME_TO_SLOW_DOWN),1)
                
                if new_value < SPEED_WARN:
                    new_value = SPEED_WARN
                
                if new_value != speed:
                    speed = new_value
                    set_element(flags,'set_motor',True)
         
            elif mode == 'STOP':
                if prev_mode != 'STOP':
                    speed = c.SPEED_STOP
                    set_element(flags,'set_motor',True)

            #print 'mode: ', mode , 'speed: ', speed , 'dist: ' , distance
            
            # Motor
            if get_element(flags,'set_motor'):
                if speed > c.SPEED_MAX:
                    speed = c.SPEED_MAX
                elif speed < c.SPEED_MIN:
                    speed = c.SPEED_MIN  
                if mode == 'SLOW' or mode == 'WARN':
                    if check_time_limit(times,'prev_set_motor',c.WAIT_MOTOR):
                        pi2go.go(speed,speed)
                        set_element(flags,'set_motor',False)
                else:
                    pi2go.go(speed,speed)
                    set_element(flags,'set_motor',False)
                
                
            # Send
            if mode != prev_mode:                          
                if prev_mode == 'STOP':
                    send_new_status('RELEASE',c.SENDING_ATTEMPTS,c.WAIT_SEND)                 
                elif mode == 'STOP':
                    send_new_status('PROBLEM',c.SENDING_ATTEMPTS,c.WAIT_SEND) 
            
            prev_state = state

            # Button
            if check_time_limit(times,'prev_get_switch',c.WAIT_SWITCH):
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    set_element(flags,'button_release',True)
                if button and get_element(flags,'button_release'):
                    set_element(flags,'button_release',False)
                    prev_state = state
                    #state = 'IDLE'
                    state = 'RUNNING'


        
        else:
            print 'impossible STATE'
            state == 'RUNNING'

                        
except KeyboardInterrupt:
    print 'KEYBOARD'

finally:
    pi2go.stop()
    pi2go.cleanup()
    sock.close()
    print 'END'