# Pi2Go 'follower sketch' - for the third episode of my robot tutorial series
# This program is also fairly simple - it utilises the Line IRs
# on the Pi2Go in order to sense obstacles and avoid them
# Created by Matthew Timmons-Brown and Simon Beal

import pi2go, time

pi2go.init()

# Here we set the speed to 60 out of 100 - feel free to change!
speed = 75

try:
  while True:
    # Defining the sensors
    left = pi2go.irLeftLine()
    right = pi2go.irRightLine()
    #dist = (int(pi2go.getDistance()*10))/10.0
    #time.sleep(0.1)

#    print "Distance: ", dist

    #if dist < 10: 
     # pi2go.setAllLEDs(4095, 0, 0)
    #elif dist > 20:
    #  pi2go.setAllLEDs(0, 0, 4095)
   # else:
    #  pi2go.setAllLEDs(0, 4095, 0)

    if left == right: # If both sensors are the same (either on or off):
      # Forward
      pi2go.forward(speed)
    elif left == True: # If the left sensor is on
      # Left
      pi2go.turnForward(speed+25, speed-25)
    elif right == True: #If the right sensor is on
      # Right
      pi2go.turnForward(speed-25, speed+25)

finally: # Even if there was an error, cleanup
  pi2go.cleanup()
