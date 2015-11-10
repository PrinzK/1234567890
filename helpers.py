# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 18:11:32 2015

@author: david
"""

import time
import communication as com
import pi2go
import constants as c
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
        
def blink(color = 'white'):
    if color == 'white':
        red = c.LED_ON
        green = c.LED_ON
        blue = c.LED_ON
    elif color == 'red':
        red = c.LED_ON
        green = c.LED_OFF
        blue = c.LED_OFF
    elif color == 'yellow':
        red = c.LED_ON
        green = c.LED_ON
        green = c.LED_OFF
    elif color == 'blue':
        red = c.LED_OFF
        green = c.LED_OFF
        blue = c.LED_ON
    elif color == 'green':
        red = c.LED_OFF
        green = c.LED_ON
        blue = c.LED_OFF
    else:
        red = c.LED_ON
        green = c.LED_ON
        blue = c.LED_ON    
    pi2go.setAllLEDs(red, green, blue)
    time.sleep(0.1)
    pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_OFF)
    time.sleep(0.1)
    pi2go.setAllLEDs(red, green, blue)
    time.sleep(0.1)
    pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_OFF)