import communication
import comm_bot_test
import auto_bot_test
import pi2go
import time
from constants import *

sock = communication.init_receiver('', COMMAND_PORT)

print "Hey there!"

try:
    message, addr = communication.receive_message(sock)
    communication.close_socket(sock)
    while True:
        if "GO_COMM" in message:
            pi2go.setAllLEDs(LED_ON, LED_ON, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_ON, LED_ON, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            status = "I'm in comm_mode now!"            
            communication.send_broadcast_message(STATUS_PORT, status)             
            message = comm_bot_test.start()            
            status = "Exiting comm_mode"
            communication.send_broadcast_message(STATUS_PORT, status)
        elif "GO_AUTO" in message:
            pi2go.setAllLEDs(LED_ON, LED_OFF, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_ON, LED_OFF, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            status ="I'm in auto_mode now!"            
            communication.send_broadcast_message(STATUS_PORT, status)
            message = auto_bot_test.start()
            status = "Exiting auto_mode"
            communication.send_broadcast_message(STATUS_PORT, status)
        elif "GO_IDLE" in message:
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_ON)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_ON)
            time.sleep(0.1)
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_OFF)
            status = "I'm in idle_mode now!"
            communication.send_broadcast_message(STATUS_PORT, status)
            sock = communication.init_receiver('', PORT)
            message, addr = communication.receive_message(sock)
            communication.close_socket(sock)
            status = "Exiting idle_mode"
            communication.send_broadcast_message(STATUS_PORT, status)
        else:
            print "Error! Going in idle_mode..."
            message = "GO_IDLE"
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
        