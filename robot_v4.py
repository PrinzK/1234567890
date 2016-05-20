# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 17:30:44 2015

@author: christopher

Same as V3 (Stops after rx warn msg ) + Diff measurement interval during STOP mode
"""

# Libraries
import communication as com
import constants as c
import pi2go
import time
import helper


# Initial
state = 'INIT'
prev_state = ''
mode = 'STOP'
prev_mode = ''


SPEED_RUN = c.SPEED_RUN
SPEED_WARN = round(float(SPEED_RUN)/3, 0)
SPEED_CONTROL_MAX = SPEED_RUN
SPEED_CONTROL_MIN = SPEED_WARN
DIST_MIN = c.DIST_MIN

speed = 0
distance = 0
distance_level = 0
last_meas_time = 0

warning = []
for x in range(c.TEAM_SIZE):
    warning.append(True)

times = [['prev_get_dist', 0.0],
         ['prev_get_switch', 0.0],
         ['prev_set_motor', 0.0],
         ['get_warning', 0.0],
         ['prev_set_LED', 0.0],
         ['new_in_RUN', 0.0]]

flags = [['set_motor', False],
         ['status_warn_LED', False],
         ['button_release', False],
         ['master_set_speed', False],
         ['master_set_button', False],
         ['master_set_LED', False],
         ['master_set_state', False],
         ['robot_type_com', False],
         ['master_set_type', False]]

try:
    while True:       
        if state == 'INIT':
            pi2go.init()            
            sock = com.init_nonblocking_receiver('', c.PORT)
                
            OWN_IP = com.get_ip()
            OWN_ID = com.get_id_from_ip(OWN_IP)
            
            value = helper.determine_team(OWN_ID)
            if helper.determine_team(OWN_ID) == c.VALUE_TYPE_COM:
                print "I'm in com_mode now!"
                helper.set_element(flags, 'robot_type_com', True)
            elif helper.determine_team(OWN_ID) == c.VALUE_TYPE_AUTO:
                print "I'm in auto_mode now!"
                helper.set_element(flags, 'robot_type_com', False)
            local_prev_value = helper.determine_team(OWN_ID)
            # TODO: IDLE-STATE?
            prev_state = state
            state = 'IDLE'

        if state == 'IDLE':
            if prev_state != 'IDLE' or helper.get_element(flags, 'master_set_type'):
                helper.set_element(flags, 'master_set_type', False)
                if helper.get_element(flags, 'robot_type_com'):
                    pi2go.setAllLEDs(c.LED_ON, c.LED_OFF, c.LED_ON)
                else: 
                    pi2go.setAllLEDs(c.LED_OFF, c.LED_ON, c.LED_ON)
                pi2go.stop()
            if helper.check_time_limit(times, 'prev_get_switch', c.WAIT_SWITCH):
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    helper.set_element(flags, 'button_release', True)
                if button and helper.get_element(flags, 'button_release'):
                    helper.set_element(flags, 'button_release', False)
                    prev_mode = ''
                    prev_state = state
                    state = 'RUNNING'
                    helper.set_element(flags, 'master_set_LED', True)
                    helper.set_element(flags, 'set_motor', True)

            # change to sensor-based or master_idle type        
            data = 'new_round'
            while data != '':
                data, addr = com.receive_message(sock) 
                if data != '':
                    sender_ID = com.get_id_from_ip(addr[0])
                    if sender_ID == OWN_ID:
                        # print 'OWN: ' , sender_ID, ' : ' , data
                        continue
                    if c.TEAM_END >= sender_ID >= c.TEAM_START:
                        # print 'ROBOT: ', sender_ID, ' : ' , data
                        if data == 'PROBLEM':
                            warning[sender_ID-c.TEAM_START] = False
                        elif data == 'RELEASE':
                            warning[sender_ID-c.TEAM_START] = True
                    else:
                        command, value = com.string_to_command(data)

                        print 'MASTER:', sender_ID, ' : ', data
                        try:
                            if command == c.COMMAND_SPEED:
                                helper.set_element(flags, 'master_set_speed', True)
                                prev_SPEED_RUN = SPEED_RUN
                                if value == '+':
                                    SPEED_RUN += 5
                                elif value == '-':
                                    SPEED_RUN -= 5
                                else:
                                    SPEED_RUN = value
                                print 'Set SPEED_RUN from ' + str(prev_SPEED_RUN) + ' to ' + str(SPEED_RUN)
                            elif command == c.COMMAND_DIST:
                                prev_DIST_MIN = DIST_MIN
                                DIST_MIN = value
                                print 'Set DIST_MIN from ' + str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)
                            elif command == c.COMMAND_BLINK:
                                helper.blink('white')
                                helper.set_element(flags, 'master_set_LED', True)
                            elif command == c.COMMAND_RESET:    
                                SPEED_RUN = c.SPEED_RUN
                                SPEED_WARN = round(float(SPEED_RUN)/3, 0)
                                SPEED_CONTROL_MAX = SPEED_RUN
                                SPEED_CONTROL_MIN = SPEED_WARN
                                DIST_MIN = c.DIST_MIN
                                helper.set_element(times, 'prev_get_dist', 0)
                                helper.set_element(flags, 'master_set_LED', True)
                                helper.set_element(flags, 'master_set_speed', True)
                                helper.set_element(flags, 'set_motor', True)
                                warning = [True] * len(warning)
                                print "Reset major values"
                            elif command == c.COMMAND_STATE:
                                helper.set_element(flags, 'set_motor', True)
                                helper.set_element(flags, 'master_set_LED', True)
                                local_prev_state = state
                                if value == c.VALUE_STATE_RUNNING:
                                    state = 'RUNNING'
                                elif value == c.VALUE_STATE_IDLE:
                                    state = 'IDLE'
                                print 'Going from state ' + local_prev_state + ' to state ' + state
                            elif command == c.COMMAND_TYPE:
                                helper.set_element(flags, 'master_set_type', True)
                                helper.set_element(flags, 'master_set_LED', True)
                                if value == c.VALUE_TYPE_ORIGINAL:
                                    if helper.determine_team(OWN_ID) == c.VALUE_TYPE_COM:
                                        helper.set_element(flags, 'robot_type_com', True)
                                    else:
                                        helper.set_element(flags, 'robot_type_com', False)
                                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS,
                                                                      c.WAIT_SEND)
                                elif value == c.VALUE_TYPE_COM:
                                    helper.set_element(flags, 'robot_type_com', True)
                                elif value == c.VALUE_TYPE_AUTO:
                                    helper.set_element(flags, 'robot_type_com', False)
                                    com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                                print "MASTER: Changing from type " + local_prev_value + " to type " + value
                                local_prev_value = value
                        except:
                            print "Error interpreting message from master! Continuing anyway"

        elif state == 'RUNNING':
            # Distance

            if mode == 'STOP':
                interval = c.WAIT_DIST_STOP
            else:
                interval = c.WAIT_DIST

            if helper.check_time_limit(times, 'prev_get_dist', c.WAIT_DIST):
                time_between = time.time() - last_meas_time
                last_meas_time = time.time()                
                new_dist = pi2go.getDistance()
                if new_dist > 1:
                    prev_distance = distance
                    distance = new_dist
                    print 'dt:', time_between, distance
            
            # Obstacle = 1, No Obstacle = 0
            irCentre = pi2go.irCentre()

            # Obstacle Analysis
            prev_distance_level = distance_level
            if mode == 'STOP':
                if irCentre or (distance < DIST_MIN and prev_distance < DIST_MIN):
                    distance_level = 0
                elif distance > c.DIST_MAX and prev_distance > c.DIST_MAX:
                    distance_level = 2
                elif DIST_MIN <= distance <= c.DIST_MAX and DIST_MIN <= prev_distance <= c.DIST_MAX:
                    distance_level = 1
            else:
                if irCentre or distance < DIST_MIN:
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
                        # print 'OWN: ' , sender_ID, ' : ' , data
                        continue
                    if c.TEAM_END >= sender_ID >= c.TEAM_START:
                        # print 'ROBOT: ', sender_ID, ' : ' , data
                        if data == 'PROBLEM':
                            warning[sender_ID-c.TEAM_START] = False
                        elif data == 'RELEASE':
                            warning[sender_ID-c.TEAM_START] = True
                    else:
                        try:
                            # print 'MASTER:' , sender_ID , ' : ' , data
                            command, value = com.string_to_command(data)
                            if command == c.COMMAND_SPEED:
                                helper.set_element(flags, 'master_set_speed', True)
                                prev_SPEED_RUN = SPEED_RUN
                                if value == '+':
                                    SPEED_RUN += 5
                                elif value == '-':
                                    SPEED_RUN -= 5
                                else:
                                    SPEED_RUN = value
                                print 'MASTER: Set SPEED_RUN from ' + str(prev_SPEED_RUN) + ' to ' + str(SPEED_RUN)
                            elif command == c.COMMAND_DIST:
                                prev_DIST_MIN = DIST_MIN
                                DIST_MIN = value
                                print 'MASTER: Set DIST_MIN from ' + str(prev_DIST_MIN) + ' to ' + str(DIST_MIN)
                            elif command == c.COMMAND_BLINK:
                                helper.blink('white')
                                helper.set_element(flags, 'master_set_LED', True)
                            elif command == c.COMMAND_RESET:    
                                SPEED_RUN = c.SPEED_RUN
                                SPEED_WARN = round(float(SPEED_RUN)/3, 0)
                                SPEED_CONTROL_MAX = SPEED_RUN
                                SPEED_CONTROL_MIN = SPEED_WARN
                                DIST_MIN = c.DIST_MIN
                                helper.set_element(times, 'prev_get_dist', 0)
                                helper.set_element(flags, 'master_set_LED', True)
                                helper.set_element(flags, 'master_set_speed', True)
                                helper.set_element(flags, 'set_motor', True)
                                warning = [True] * len(warning)
                                print 'MASTER: Reset major values'
                            elif command == c.COMMAND_STATE:
                                helper.set_element(flags, 'master_set_state', True)
                                if value == c.VALUE_STATE_RUNNING:
                                    next_state = 'RUNNING'
                                elif value == c.VALUE_STATE_IDLE:
                                    next_state = 'IDLE'
                                print 'MASTER: Going from state ' + state + ' to state ' + next_state
                            # elif command == c.COMMAND_TYPE and value != c.VALUE_TYPE_COM:
                            elif command == c.COMMAND_TYPE:
                                helper.set_element(flags, 'master_set_type', True)
                                helper.set_element(flags, 'master_set_LED', True)
                                local_prev_value = value
                                if value == c.VALUE_TYPE_ORIGINAL:
                                    if helper.determine_team(OWN_ID) == c.VALUE_TYPE_COM:
                                        helper.set_element(flags, 'robot_type_com', True)
                                    else:
                                        helper.set_element(flags, 'robot_type_com', False)
                                        com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS,
                                                                      c.WAIT_SEND)
                                elif value == c.VALUE_TYPE_COM:
                                    helper.set_element(flags, 'robot_type_com', True)
                                elif value == c.VALUE_TYPE_AUTO:
                                    helper.set_element(flags, 'robot_type_com', False)
                                    com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                                    
                                print "MASTER: Changing from type " + local_prev_value + " to type " + value
                        except:
                            print "Error interpreting message from master! Continuing anyway"
                                    
            # Analyse --> Calculate MODE
            if prev_state == 'RUNNING':                
                prev_mode = mode
            
            # Find Mode
            if helper.get_element(flags, 'robot_type_com'):
                if distance_level == 0:
                    mode = 'STOP'
                elif distance_level == 1 and all(warning):
                    mode = 'SLOW'
                elif distance_level == 2 and all(warning):
                    mode = 'RUN'
                elif distance_level != 0 and not all(warning):
                    mode = 'WARN'
            else:
                if distance_level == 0:
                    mode = 'STOP'
                elif distance_level == 1:
                    mode = 'SLOW'
                elif distance_level == 2:
                    mode = 'RUN'

            # Set own Warning-Flag 
            if mode != prev_mode:                          
                if mode == 'STOP':
                    warning[OWN_ID-c.TEAM_START] = False
                else:
                    warning[OWN_ID-c.TEAM_START] = True

            # LEDs  
            if mode != prev_mode or helper.get_element(flags, 'master_set_LED'):
                if helper.get_element(flags, 'master_set_LED'):
                    helper.set_element(flags, 'master_set_LED', False)
                if mode == 'RUN':
                    pi2go.setAllLEDs(c.LED_OFF, c.LED_ON, c.LED_OFF)
                elif mode == 'SLOW':
                    # pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_ON)      #TODO: test
                    # pi2go.setAllLEDs(c.LED_ON, c.LED_ON, c.LED_OFF)
                    pi2go.setAllLEDs(c.LED_OFF, c.LED_ON, c.LED_OFF)      # TODO: presentation
                # elif mode == 'WARN':
                    # pi2go.setAllLEDs(c.LED_ON, c.LED_ON, c.LED_OFF)
                elif mode == 'STOP':
                    pi2go.setAllLEDs(c.LED_ON, c.LED_OFF, c.LED_OFF)
            # Blinking-Mode
            if mode == 'WARN' and helper.get_element(flags, 'robot_type_com'):
                if helper.check_time_limit(times, 'prev_set_LED', c.WAIT_LED):
                    if helper.get_element(flags, 'status_warn_LED'):
                        pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_OFF)
                        helper.set_element(flags, 'status_warn_LED', False)
                    else:
                        pi2go.setAllLEDs(c.LED_ON, c.LED_ON, c.LED_OFF)
                        helper.set_element(flags, 'status_warn_LED', True)
                    
            # Calculate new speed
            if mode == 'RUN':
                if prev_mode != 'RUN' or helper.get_element(flags, 'master_set_speed'):
                    helper.set_element(flags, 'master_set_speed', False)
                    helper.set_element(times, 'new_in_RUN', time.time())
                    speed_new_in_RUN = speed
                    dspeed = SPEED_RUN-speed_new_in_RUN
                
                if speed != SPEED_RUN:
                    dt = time.time()-helper.get_element(times, 'new_in_RUN')
                    new_value = round(speed_new_in_RUN + dspeed*(dt/c.TIME_TO_SPEED_UP), 1)
                
                if new_value > SPEED_RUN:
                    new_value = SPEED_RUN
                
                if new_value != speed:
                    speed = new_value
                    helper.set_element(flags, 'set_motor', True)

            # Blocking Avoidance
            elif mode == 'SLOW':
                # linear
                gradient = float(SPEED_CONTROL_MAX - SPEED_CONTROL_MIN)/float(c.DIST_MAX-DIST_MIN)
                error = c.DIST_MAX - distance
                new_value = round(SPEED_RUN - error * gradient, 1)
                
                if new_value < SPEED_CONTROL_MIN:
                    new_value = SPEED_CONTROL_MIN
                elif new_value > SPEED_CONTROL_MAX:
                    new_value = SPEED_CONTROL_MAX
                                 
                if new_value != speed:
                    speed = new_value
                    helper.set_element(flags, 'set_motor', True)

            # Slow-Down in Warning-Mode    
            elif mode == 'WARN' and helper.get_element(flags, 'robot_type_com'):
                if prev_mode != 'WARN':
                    helper.set_element(times, 'get_warning', time.time())
                    speed_get_warning = speed
                
                if prev_distance_level == 0 and distance_level != 0:
                    speed_get_warning = 50
                    helper.set_element(times, 'get_warning', time.time())
                    
                new_value = round(speed_get_warning * (1 - (time.time()-helper.get_element(times, 'get_warning')) /
                                                       c.TIME_TO_SLOW_DOWN), 1)
                
            # ###############################changed from SPEED_WARN to c.SPEED_STOP
                if new_value < c.SPEED_STOP:
                    new_value = c.SPEED_STOP
            #########################
                
                if new_value != speed:
                    speed = new_value
                    helper.set_element(flags, 'set_motor', True)
         
            elif mode == 'STOP':
                if prev_mode != 'STOP':
                    speed = c.SPEED_STOP
                    helper.set_element(flags, 'set_motor', True)

            # Motor
            if helper.get_element(flags, 'set_motor'):
                if speed > c.SPEED_LIMIT_MAX:
                    speed = c.SPEED_LIMIT_MAX
                elif speed < c.SPEED_LIMIT_MIN:
                    speed = c.SPEED_LIMIT_MIN  
                if mode == 'SLOW' or mode == 'WARN':
                    if helper.check_time_limit(times, 'prev_set_motor', c.WAIT_MOTOR):
                        pi2go.go(speed, speed)
                        helper.set_element(flags, 'set_motor', False)
                else:
                    pi2go.go(speed, speed)
                    helper.set_element(flags, 'set_motor', False)
                
            # Send
            if mode != prev_mode and helper.get_element(flags, 'robot_type_com'):                          
                if prev_mode == 'STOP':
                    com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
                elif mode == 'STOP':
                    com.send_x_broadcast_messages(c.PORT, "PROBLEM", c.SENDING_ATTEMPTS, c.WAIT_SEND)

            # Next State                
            prev_state = state
            if helper.get_element(flags, 'master_set_state'):
                helper.set_element(flags, 'master_set_state', False)
                state = next_state
            
            # Button
            if helper.check_time_limit(times, 'prev_get_switch', c.WAIT_SWITCH):
                # Pressed = 1, Released = 0
                button = pi2go.getSwitch()
                if not button:
                    helper.set_element(flags, 'button_release', True)
                if button and helper.get_element(flags, 'button_release'):
                    helper.set_element(flags, 'button_release', False)
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
