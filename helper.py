# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 18:11:32 2015

@author: david
"""


import time
import communication as com
import pi2go
import constants as c


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
    return list_2D[row][1]
    
    
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

        
def blink(color = 'white', sleeptime=0.1):
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
    time.sleep(sleeptime)
    pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_OFF)
    time.sleep(sleeptime)
    pi2go.setAllLEDs(red, green, blue)
    time.sleep(sleeptime)
    pi2go.setAllLEDs(c.LED_OFF, c.LED_OFF, c.LED_OFF)


def determine_team(OWN_ID): 
    if OWN_ID - c.TEAM_START < c.COM_TEAM_SIZE:
        return c.VALUE_TYPE_COM
    else:
        return c.VALUE_TYPE_AUTO
