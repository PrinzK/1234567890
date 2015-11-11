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
  
    
# Programm
def start():
    state = 'INIT'
    prev_state = ''
    mode = 'STOP'
    prev_mode = ''

    try:
        while True:       
            if state == 'INIT':
                SPEED_RUN = c.SPEED_RUN
                SPEED_WARN = round(float(SPEED_RUN)/3,0)
                SPEED_CONTROL_MAX = SPEED_RUN
                SPEED_CONTROL_MIN = SPEED_WARN
                DIST_MIN = c.DIST_MIN
                speed = 0
                distance = 0
                warning = []
                last_meas_time = 0
                times = []
                times.append(['prev_get_dist',0.0])
                times.append(['prev_get_switch',0.0])
                times.append(['prev_set_motor',0.0])
                times.append(['get_warning',0.0])
                times.append(['prev_set_LED',0.0])    
                flags = []
                flags.append(['set_motor',False])
                flags.append(['status_warn_LED',False])
                flags.append(['button_release',False])
                flags.append(['master_set_speed',False])
                flags.append(['master_set_button',False])
                flags.append(['master_set_LED',False])
                flags.append(['master_set_state',False])
                pi2go.init()
                pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_ON)
                time.sleep(1)
                sock = com.init_nonblocking_receiver('',c.PORT)
                for x in range(c.TEAM_SIZE):
                    warning.append(True)
                OWN_IP = com.get_ip()
                OWN_ID = com.get_id_from_ip(OWN_IP)
                prev_state = state
                state = 'IDLE'
   
    
            if state == 'IDLE':
                if prev_state != 'IDLE':
                    pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                    pi2go.stop()
                if helper.check_time_limit(times,'prev_get_switch',c.WAIT_SWITCH):
                    # Pressed = 1, Released = 0
                    button = pi2go.getSwitch()
                    if not button:
                        helper.set_element(flags,'button_release',True)
                    if button and helper.get_element(flags,'button_release'):
                        helper.set_element(flags,'button_release',False)
                        prev_mode = ''
                        prev_state = state
                        state = 'RUNNING'

                # change to sensor-based or master_idle type        
                data = 'new_round'
                while data != '':
                    data, addr = com.receive_message(sock) 
                    if data != '':
                        sender_ID = com.get_id_from_ip(addr[0])
                        if sender_ID < c.TEAM_START or sender_ID > c.TEAM_END:
                            command, value = com.string_to_command(data)
                            #
                            print 'MASTER:' , sender_ID , ' : ' , data
                            try:
                                if command == c.COMMAND_SPEED:
                                    helper.set_element(flags,'master_set_speed',True)
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
                                    print 'Set DIST_MIN from '+ str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)  
                                elif command == c.COMMAND_BLINK:
                                    helper.blink('white')
                                    helper.set_element(flags, 'master_set_LED', True)
                                elif command == c.COMMAND_RESET:    
                                    SPEED_RUN = c.SPEED_RUN
                                    SPEED_WARN = round(float(SPEED_RUN)/3,0)
                                    SPEED_CONTROL_MAX = SPEED_RUN
                                    SPEED_CONTROL_MIN = SPEED_WARN
                                    DIST_MIN = c.DIST_MIN
                                    helper.set_element(times,'prev_get_dist',0)
                                    helper.set_element(flags,'master_set_LED', True)
                                    helper.set_element(flags,'master_set_speed', True)
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
                if helper.check_time_limit(times,'prev_get_dist',c.WAIT_DIST):
                    time_between = time.time() - last_meas_time
                    last_meas_time = time.time()                
                    new_dist = pi2go.getDistance()
                    if new_dist > 1:
                        distance = new_dist
                    print 'dt:', time_between , distance
                
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
                            #print 'ROBOT: ', sender_ID, ' : ' , data
                            if data == 'PROBLEM':
                                warning[sender_ID-c.TEAM_START] = False
                            elif data == 'RELEASE':
                                warning[sender_ID-c.TEAM_START] = True
                        else:
                            try:
                            #print 'MASTER:' , sender_ID , ' : ' , data
                                command, value = com.string_to_command(data)
                                if command == c.COMMAND_SPEED:
                                    helper.set_element(flags,'master_set_speed',True)
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
                                    print 'Set DIST_MIN from '+ str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)  
                                elif command == c.COMMAND_BLINK:
                                    helper.blink('white')
                                    helper.set_element(flags, 'master_set_LED', True)
                                elif command == c.COMMAND_RESET:    
                                    SPEED_RUN = c.SPEED_RUN
                                    SPEED_WARN = round(float(SPEED_RUN)/3,0)
                                    SPEED_CONTROL_MAX = SPEED_RUN
                                    SPEED_CONTROL_MIN = SPEED_WARN
                                    DIST_MIN = c.DIST_MIN
                                    helper.set_element(times,'prev_get_dist',0)
                                    helper.set_element(flags,'master_set_LED', True)
                                    helper.set_element(flags,'master_set_speed', True)
                                    warning = True * len(warning)
                                elif command == c.COMMAND_STATE:
                                    helper.set_element(flags,'master_set_state', True)
                                    if value == c.VALUE_STATE_RUNNING:
                                        next_state = 'RUNNING'
                                    elif value == c.VALUE_STATE_IDLE:
                                        next_state = 'IDLE'
                                #elif command == c.COMMAND_TYPE and value != c.VALUE_TYPE_COM:
                                elif command == c.COMMAND_TYPE:
                                    if value == c.VALUE_TYPE_ORIGINAL:
                                        value = helper.determine_team(OWN_ID)
                                    print "com_bot.py says: changing to", value
                                    return value
                            except:
                                print "Error interpreting message from master! Continuing anyway"

                                        
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


                # Set own Warning-Flag 
                if mode != prev_mode:                          
                    if mode == 'STOP':
                        warning[OWN_ID-c.TEAM_START] = False
                    else:
                        warning[OWN_ID-c.TEAM_START] = True


                # LEDs  
                if mode != prev_mode or helper.get_element(flags,'master_set_LED'):
                    if helper.get_element(flags,'master_set_LED'):
                        helper.set_element(flags,'master_set_LED',False)
                    if mode == 'RUN':
                        pi2go.setAllLEDs(c.LED_OFF,c.LED_ON,c.LED_OFF)
                    elif mode == 'SLOW':
                        pi2go.setAllLEDs(c.LED_OFF,c.LED_OFF,c.LED_ON)      #TODO: test
                        #pi2go.setAllLEDs(c.LED_OFF,c.LED_ON,c.LED_OFF)      #TODO: presentation
                    #elif mode == 'WARN':
                        #pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                    elif mode == 'STOP':
                        pi2go.setAllLEDs(c.LED_ON,c.LED_OFF,c.LED_OFF)
                # Blinking-Mode
                if mode == 'WARN':
                    if helper.check_time_limit(times,'prev_set_LED',c.WAIT_LED):
                        if helper.get_element(flags,'status_warn_LED'):
                            pi2go.setAllLEDs(c.LED_OFF,c.LED_OFF,c.LED_OFF)
                            helper.set_element(flags,'status_warn_LED',False)
                        else:
                            pi2go.setAllLEDs(c.LED_ON,c.LED_ON,c.LED_OFF)
                            helper.set_element(flags,'status_warn_LED',True)
    
                        
                # Calculate new speed
                if mode == 'RUN':
                    if prev_mode != 'RUN' or helper.get_element(flags,'master_set_speed'):
                        speed = SPEED_RUN
                        helper.set_element(flags,'master_set_speed',False)
                        helper.set_element(flags,'set_motor',True)


                # Blocking Avoidance
                elif mode == 'SLOW':
                    #linear
                    gradient = float(SPEED_CONTROL_MAX - SPEED_CONTROL_MIN)/float(c.DIST_MAX-DIST_MIN)
                    error = c.DIST_MAX - distance
                    new_value = round(SPEED_RUN - error * gradient,1) 
                    
                    if new_value < SPEED_CONTROL_MIN:
                        new_value = SPEED_CONTROL_MIN
                    elif new_value > SPEED_CONTROL_MAX:
                        new_value = SPEED_CONTROL_MAX
                                     
                    if new_value != speed:
                        speed = new_value
                        helper.set_element(flags,'set_motor',True)
                
                
                # Slow-Down in Warning-Mode    
                elif mode == 'WARN':
                    if prev_mode != 'WARN':
                        helper.set_element(times,'get_warning',time.time())
                        speed_get_warning = speed
                    new_value = round(speed_get_warning * (1-(time.time()-helper.get_element(times,'get_warning'))/c.TIME_TO_SLOW_DOWN),1)
                    
                    if new_value < SPEED_WARN:
                        new_value = SPEED_WARN
                    
                    if new_value != speed:
                        speed = new_value
                        helper.set_element(flags,'set_motor',True)
             
                elif mode == 'STOP':
                    if prev_mode != 'STOP':
                        speed = c.SPEED_STOP
                        helper.set_element(flags,'set_motor',True)

                
                # Motor
                if helper.get_element(flags,'set_motor'):
                    if speed > c.SPEED_LIMIT_MAX:
                        speed = c.SPEED_LIMIT_MAX
                    elif speed < c.SPEED_LIMIT_MIN:
                        speed = c.SPEED_LIMIT_MIN  
                    if mode == 'SLOW' or mode == 'WARN':
                        if helper.check_time_limit(times,'prev_set_motor',c.WAIT_MOTOR):
                            pi2go.go(speed,speed)
                            helper.set_element(flags,'set_motor',False)
                    else:
                        pi2go.go(speed,speed)
                        helper.set_element(flags,'set_motor',False)

                    
                # Send
                if mode != prev_mode:                          
                    if prev_mode == 'STOP':
                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                    elif mode == 'STOP':
                        com.send_x_broadcast_messages(c.PORT, "PROBLEM", c.SENDING_ATTEMPTS, c.WAIT_SEND)

                # Next State                
                prev_state = state
                if helper.get_element(flags,'master_set_state'):
                    helper.set_element(flags,'master_set_state',False)
                    state = next_state
                
                # Button
                if helper.check_time_limit(times,'prev_get_switch',c.WAIT_SWITCH):
                    # Pressed = 1, Released = 0
                    button = pi2go.getSwitch()
                    if not button:
                        helper.set_element(flags,'button_release',True)
                    if button and helper.get_element(flags,'button_release'):
                        helper.set_element(flags,'button_release',False)
                        prev_state = state
                        state = 'IDLE'
                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)

    
                            
    except KeyboardInterrupt:
        print 'KEYBOARD'
    
    finally:
        pi2go.stop()
        pi2go.cleanup()
        sock.close()
        print 'END'
