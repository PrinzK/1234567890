import communication
import comm_bot_test
import auto_bot_test
import pi2go
import time
import constants as c

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


sock = communication.init_receiver('', c.PORT)


print "Hey there!"

try:
    message, addr = communication.receive_message(sock)
    communication.close_socket(sock)
    while True:
        if c.COMMAND_GO_COMM in message:
            blink('yellow')
            status = "I'm in comm_mode now!"            
            print status
            #communication.send_broadcast_message(c.PORT, status)             
            message = comm_bot_test.start()            
            status = "Exiting comm_mode"
            print status
            #communication.send_broadcast_message(c.PORT, status)
        elif c.COMMAND_GO_AUTO in message:
            blink('red')
            status ="I'm in auto_mode now!"            
            print status
            #communication.send_broadcast_message(PORT, status)
            message = auto_bot_test.start()
            status = "Exiting auto_mode"
            print status
            #communication.send_broadcast_message(PORT, status)
        elif "GO_IDLE" in message:
            blink('white')
            status = "I'm in idle_mode now!"
            print status
            #communication.send_broadcast_message(PORT, status)
            sock = communication.init_receiver('', c.PORT)
            message, addr = communication.receive_message(sock)
            communication.close_socket(sock)
            status = "Exiting idle_mode"
            print status
            #communication.send_broadcast_message(c.PORT, status)
        else:
            print "Error! Going in idle_mode..."
            message = "GO_IDLE"
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
        