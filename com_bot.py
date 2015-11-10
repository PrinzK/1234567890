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
import helper

# Initail Values



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


# Programm
def start():
    state = 'INIT'
    prev_state = ''
    mode = 'STOP'
    prev_mode = ''

    speed = 0
    distance = 0
    warning = []

    times = []
    times.append(['prev_get_dist',0.0])
    times.append(['prev_get_switch',0.0])
    times.append(['prev_set_motor',0.0])
    times.append(['get_warning',0.0])
          
    flags = []
    flags.append(['set_motor',False])
    flags.append(['button_release',False])
    flags.append(['master_set_speed',False])
    flags.append(['master_set_button',False])
    flags.append(['master_set_LED',False])    
    
    SPEED_RUN = c.SPEED_RUN
    SPEED_WARN = c.SPEED_WARN
    SPEED_CONTROL_MAX = c.SPEED_CONTROL_MAX
    SPEED_CONTROL_MIN = c.SPEED_STOP
    DIST_MIN = c.DIST_MIN
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
                state = 'IDLE'
                #state = 'RUNNING'
    
    
            if state == 'IDLE':
                if prev_state != 'IDLE':
                    pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
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
                        set_element(flags,'master_set_button',True)
                        set_element(flags,'master_set_LED',True)
                # change to sensor-based or master_idle type        
                data = 'new_round'
                while data != '':
                    data, addr = com.receive_message(sock) 
                    if data != '':
                        sender_ID = com.get_id_from_ip(addr[0])
                        if sender_ID == OWN_ID:
                            #print 'OWN: ' , ID, ' : ' , data
                            continue
                        if sender_ID >= c.TEAM_START and sender_ID <= c.TEAM_END:
                            #print 'ROBOT: ', ID, ' : ' , data
                            if data == 'PROBLEM':
                                curr_status = False
                                warning[sender_ID-c.TEAM_START] = curr_status
                            elif data == 'RELEASE':
                                curr_status = True
                                warning[sender_ID-c.TEAM_START] = curr_status
                        else:
                            #print 'MASTER:' , ID , ' : ' , data
                            command, value = com.string_to_command(data)
                            # change MODE, STATUS, SPEED, DISTANCELIMITS#
                                #print 'MasterID: ', ID , 'PARAM: ' , PARAM , 'VALUE: ' , VALUE
                            try:
                                if command == c.COMMAND_SPEED:
                                    set_element(flags,'master_set_speed',True)
                                    prev_SPEED_RUN = SPEED_RUN
                                    if value == '+':
                                        SPEED_RUN += 5
                                    elif value == '-':
                                        SPEED_RUN -= 5
                                    else:
                                        SPEED_RUN = value
                                    print 'Set SPEED_RUN from '+ str(prev_SPEED_RUN) + ' to ' + str(SPEED_RUN)           
                                elif command == c.COMMAND_DIST:
                                    prev_DIST_MIN = DIST_MIN
                                    DIST_MIN = value
                                   # print 'Set DIST_MIN from '+ str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)  
                                elif command == c.COMMAND_BLINK:
                                    helper.blink('white')
                                    set_element(flags, 'master_set_LED', True)
                                elif command == c.COMMAND_RESET:    
                                    SPEED_RUN = c.SPEED_RUN
                                    SPEED_WARN = c.SPEED_WARN
                                    SPEED_CONTROL_MAX = c.SPEED_CONTROL_MAX
                                    SPEED_CONTROL_MIN = c.SPEED_STOP
                                    DIST_MIN = c.DIST_MIN
                                    set_element(times,'prev_get_dist',0)
                                    set_element(flags,'master_set_LED', True)
                                    set_element(flags,'master_set_speed', True)
                                    warning = True * len(warning)
                                elif command == c.COMMAND_STATE:    
                                    if value == c.VALUE_STATE_RUNNING:
                                        state = 'RUNNING'
                                    elif value == c.VALUE_STATE_IDLE:
                                        state = 'IDLE'
                                elif command == c.COMMAND_TYPE:
                                    if value == c.VALUE_TYPE_ORIGINAL:
                                        value = helper.determine_team(OWN_ID)
                                    return value
                            except:
                                print "Error interpreting message from master! Continuing anyway"
                    
    
            elif state == 'RUNNING':
                # Distance         
                if check_time_limit(times,'prev_get_dist',c.WAIT_DIST):
                    distance = pi2go.getDistance()
                    print distance
                
                # Obstacle = 1, No Obstacle = 0
                irCentre = pi2go.irCentre()
                
                # Obstacle Analysis
                if irCentre or (distance < DIST_MIN):
                    distance_level = 0
                elif distance > c.DIST_REF:
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
                            #print 'OWN: ' , ID, ' : ' , data
                            continue
                        if sender_ID >= c.TEAM_START and sender_ID <= c.TEAM_END:
                            #print 'ROBOT: ', ID, ' : ' , data
                            if data == 'PROBLEM':
                                curr_status = False
                                warning[sender_ID-c.TEAM_START] = curr_status
                            elif data == 'RELEASE':
                                curr_status = True
                                warning[sender_ID-c.TEAM_START] = curr_status
                        else:
                            try:
                            #print 'MASTER:' , ID , ' : ' , data
                                command, value = com.string_to_command(data)
                                # change MODE, STATUS, SPEED, DISTANCELIMITS#
                                    #print 'MasterID: ', ID , 'PARAM: ' , PARAM , 'VALUE: ' , VALUE
                                if command == c.COMMAND_SPEED:
                                    set_element(flags,'master_set_speed',True)
                                    prev_SPEED_RUN = SPEED_RUN
                                    if value == '+':
                                        SPEED_RUN += 5
                                    elif value == '-':
                                        SPEED_RUN -= 5
                                    else:
                                        SPEED_RUN = value
                                    print 'Set SPEED_RUN from '+ str(prev_SPEED_RUN) + ' to ' + str(SPEED_RUN)           
                                elif command == c.COMMAND_DIST:
                                    prev_DIST_MIN = DIST_MIN
                                    if not value.isdigit():
                                        print "Something went terribly wrong with the protocol..."
                                        raise KeyboardInterrupt
                                    DIST_MIN = value
                                elif command == c.COMMAND_BLINK:
                                    helper.blink('white')
                                    set_element(flags, 'master_set_LED', True)
                                   # print 'Set DIST_MIN from '+ str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)           
                                elif command == c.COMMAND_RESET:    
                                    SPEED_RUN = c.SPEED_RUN
                                    SPEED_WARN = c.SPEED_WARN
                                    SPEED_CONTROL_MAX = c.SPEED_CONTROL_MAX
                                    SPEED_CONTROL_MIN = c.SPEED_STOP
                                    DIST_MIN = c.DIST_MIN
                                    set_element(times,'prev_get_dist',0)
                                    set_element(flags,'master_set_LED', True)
                                    set_element(flags,'master_set_speed', True)
                                    warning = True * len(warning)
                                elif command == c.COMMAND_STATE:    
                                    if value == c.VALUE_STATE_RUNNING:
                                        state = 'RUNNING'
                                    elif value == c.VALUE_STATE_IDLE:
                                        state = 'IDLE'
                                #elif command == c.COMMAND_TYPE and value != c.VALUE_TYPE_COM:
                                elif command == c.COMMAND_TYPE:
                                    if value == c.VALUE_TYPE_ORIGINAL:
                                        value = helper.determine_team(OWN_ID)
                                    print "com_bot.py says: changing to", value
                                    return value
                            except:
                                print "Error interpreting message from master! Continuing anyway"
                        
    
                                        
                # Analyse --> Calculate MODE
                prev_mode = mode
                # overwrite for coming from idle state
                if get_element(flags, 'master_set_button'):
                    prev_mode = ''
                    
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
                if mode != prev_mode:                          
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
                    elif mode == 'WARN':
                        pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                    elif mode == 'STOP':
                        pi2go.setAllLEDs(c.LED_ON,c.LED_OFF,c.LED_OFF)
    
                        
                # Calculate new speed
                if mode == 'RUN':
                    if prev_mode != 'RUN' or get_element(flags,'master_set_speed'):
                        speed = SPEED_RUN
                        set_element(flags,'master_set_speed',False)
                        set_element(flags,'set_motor',True)
                
                # Blocking Avoidance
                elif mode == 'SLOW':
                    KP = float(SPEED_CONTROL_MAX - SPEED_CONTROL_MIN)/float(c.DIST_REF-DIST_MIN)
                    error = c.DIST_REF - distance
                    new_value = round(SPEED_RUN - error * KP,1)
                    
                    if new_value < SPEED_CONTROL_MIN:
                        new_value = SPEED_CONTROL_MIN
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
      
                
                # Motor
                #print 'mode: ', mode , 'speed: ', speed , 'dist: ' , distance
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
                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                    elif mode == 'STOP':
                        com.send_x_broadcast_messages(c.PORT, "PROBLEM", c.SENDING_ATTEMPTS, c.WAIT_SEND)
    
    
                # Button
                if check_time_limit(times,'prev_get_switch',c.WAIT_SWITCH):
                    # Pressed = 1, Released = 0
                    button = pi2go.getSwitch()
                    if not button:
                        set_element(flags,'button_release',True)
                    if button and get_element(flags,'button_release'):
                        set_element(flags,'button_release',False)
                        prev_state = state
                        state = 'IDLE'
                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                        #state = 'RUNNING'
    
            
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