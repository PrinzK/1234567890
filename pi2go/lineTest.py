#!/usr/bin/env python
#Simply prints the state of the line follower sensors

# Must be run as root - sudo python .py 

import time, pi2go
import RPi.GPIO as GPIO

pi2go.init()

vsn = pi2go.version()
if vsn == 1:
  print "Running on Pi2Go"
else:
  print "Running on Pi2Go-Lite"


try:
    while True:
	print 'obstacle'
	print 'irLeft', GPIO.input(11)
	print pi2go.irLeft()
	print 'irRight', GPIO.input(7)
	print pi2go.irRight()
	print 'irCentre', GPIO.input(13)
	print pi2go.irCentre()
	print 'line'
	print 'LeftLine', GPIO.input(12)
	print pi2go.irLeftLine()
	print 'RightLine', GPIO.input(15)
	print pi2go.irRightLine()
        #print 'Left:', pi2go.irLeftLine()
        #print 'Right:', pi2go.irRightLine()
	print
        time.sleep(5)
                          
except KeyboardInterrupt:
    print

finally:
    pi2go.cleanup()
