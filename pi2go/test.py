# Pi2Go 'follower sketch' - for the third episode of my robot tutorial series
# This program is also fairly simple - it utilises the Line IRs
# on the Pi2Go in order to sense obstacles and avoid them
# Created by Matthew Timmons-Brown and Simon Beal


import pi2go
import time

pi2go.init()

# Here we set the speed to 60 out of 100 - feel free to change!
speed = 40
change = 25

try:

  stime = time.time()
  while True:
    # Defining the sensors
    left = pi2go.irLeftLine()
    right = pi2go.irRightLine()   
    ntime = time.time()

    # timecheck for distance         
    if ntime > (stime + 0.1):
      #print "%.5f" %time.time()
      dist = (int(pi2go.getDistance()*10))/10.0
      #print "%.5f" %time.time()
      stime = ntime
      
      # distance groups 
      if dist < 10: 
        pi2go.setAllLEDs(2000, 0, 0)
      elif dist > 20:
        pi2go.setAllLEDs(0, 0, 2000)
      else:
        pi2go.setAllLEDs(0, 2000, 0)
    
    # line follower
    if left == right: # If both sensors are the same (either on or off) --> forward
      pi2go.forward(speed)
    elif left == True: # If the left sensor is on --> move right
      pi2go.turnForward(speed+change, speed-change)
    elif right == True: #If the right sensor is on --> move left
      pi2go.turnForward(speed-change, speed+change)

finally: # Even if there was an error, cleanup
  pi2go.cleanup()

