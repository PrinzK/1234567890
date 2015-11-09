import communication as com
import comm_bot.start
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


sock = com.init_receiver('', c.PORT)


print "Hey there!"

try:
    data, addr = com.receive_message(sock)
    command, value = com.string_to_command(data)
    com.close_socket(sock)
    while True:
        if c.VALUE_TYPE_COM == value:
            blink('yellow')
            status = "I'm in com_mode now!"            
            print status
            #communication.send_broadcast_message(c.PORT, status)             
            value = comm_bot.start()            
            status = "Exiting com_mode"
            print status
            #communication.send_broadcast_message(c.PORT, status)
        elif c.VALUE_TYPE_COMM == value:
            blink('red')
            status ="I'm in auto_mode now!"            
            print status
            #communication.send_broadcast_message(PORT, status)
            value = auto_bot_test.start()
            status = "Exiting auto_mode"
            print status
            #communication.send_broadcast_message(PORT, status)
        elif c.VALUE_TYPE_IDLE == value:
            blink('white')
            status = "I'm in idle_mode now!"
            print status
            #communication.send_broadcast_message(PORT, status)
            sock = com.init_receiver('', c.PORT)
            data, addr = com.receive_message(sock)
            command, value = com.string_to_command(data)
            if command != c.COMMAND_TYPE:
                value = c.VALUE_TYPE_IDLE
            com.close_socket(sock)
            status = "Exiting idle_mode"
            print status
            #communication.send_broadcast_message(c.PORT, status)
        else:
            print "Error! Going in idle_mode..."
            message = "GO_IDLE"
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
        