# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:43:35 2015

@author: christopher
"""

# Libraries
import pi2go
import time
from constants import * 

# Initail Values
state = 'INIT'
mode = 'STOP'
prev_mode = 'RUN'
speed = SPEED_RUN
distance = 0
prev_measurement_time = 0

# Programm
try:
    while True:
        #loopstart = time.time()
        if state == 'INIT':
            pi2go.init()
            state = 'RUNNING'

        elif state == 'RUNNING':
            # Distance 
            
            if time.time() - prev_measurement_time > WAIT_DIST:
                prev_measurement_time = time.time()                
                distance = pi2go.getDistance()
                
                print "US sensor time: ", time.time() - prev_measurement_time, " with distance: ", distance
                
                
            # Obstacle = 1, No Obstacle = 0
            irCentre = pi2go.irCentre() # TODO: edit pi2go library and uncomment!
            # Obstacle Analysis
            if irCentre or (distance < DIST_MIN):
                distance_area = 0
            elif distance > DIST_MAX:
                distance_area = 2
            else:
                distance_area = 1
                    
            # Analyse --> Calculate mode
            prev_mode = mode
            if distance_area == 0:
                mode = 'STOP'
            elif distance_area == 1:
                mode = 'SLOW'
            elif distance_area == 2:
                mode = 'RUN'
            else:
                print 'check mode-Conditions'
                break

            # LEDs  
            if mode != prev_mode:                          
                if mode == 'RUN':
                    # set LEDs to green
                    pi2go.setAllLEDs(LED_OFF,LED_ON,LED_OFF)
                elif mode == 'SLOW':
                    # set LEDs to blue
                    pi2go.setAllLEDs(LED_OFF,LED_OFF,LED_ON)
                elif mode == 'WARN':
                    # set LEDs to yellow
                    pi2go.setAllLEDs(LED_ON,LED_ON,LED_OFF)
                elif mode == 'STOP':
                    # set LEDs to red
                    pi2go.setAllLEDs(LED_ON,LED_OFF,LED_OFF)
            
            # Motor
            if mode != prev_mode:                          
                if mode == 'RUN':
                    speed = SPEED_RUN
                elif mode == 'SLOW':
                    speed = SPEED_SLOW
                elif mode == 'WARN':
                    speed = SPEED_WARN
                elif mode == 'STOP':
                    speed = SPEED_STOP
                pi2go.go(speed,speed)
       
        else:
            print 'impossible state'
            state == 'RUNNING'
        #print "Loop: ", time.time() - loopstart
            
except KeyboardInterrupt:
    print 'KEYBOARD'

finally:
    pi2go.stop()
    pi2go.cleanup()
    print 'END'