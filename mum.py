import communication
import comm_bot_test
import auto_bot_test

PORT = 5003

sock = communication.init_receiver('', PORT)

print "Hey there!"

try:
    message, addr = communication.receive_message(sock)
    communication.close_socket(sock)
    while True:
        if "GO_COMM" in message:
            status = "I'm in comm_mode now!"            
            communication.send_broadcast_message(5003, status) 
            message = comm_bot_test.start()            
            status = "Exiting comm_mode"
            communication.send_broadcast_message(5003, status)
        elif "GO_AUTO" in message:
            status ="I'm in auto_mode now!"
            communication.send_broadcast_message(5003, status)
            message = auto_bot_test.start()
            status = "Exiting auto_mode"
            communication.send_broadcast_message(5003, status)
        elif "GO_IDLE" in message:
            status = "I'm in idle_mode now!"
            communication.send_broadcast_message(5003, status)
            sock = communication.init_receiver('', PORT)
            message, addr = communication.receive_message(sock)
            communication.close_socket(sock)
            status = "Exiting idle_mode"
            communication.send_broadcast_message(5003, status)
        else:
            print "Error! Going in idle_mode..."
            message = "GO_IDLE"
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
        