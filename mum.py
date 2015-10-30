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
            print "I'm in comm_mode now!"            
            message = comm_bot_test.start()            
            print "Exiting comm_mode"
        elif "GO_AUTO" in message:
            print "I'm in auto_mode now!"
            message = auto_bot_test.start()
            print "Exiting auto_mode"
        elif "GO_IDLE" in message:
            print "I'm in idle_mode now!"
            sock = communication.init_receiver('', PORT)
            message, addr = communication.receive_message(sock)
            communication.close_socket(sock)
            print "Exiting idle_mode"
        else:
            print "Error! Going in idle_mode..."
            message = "GO_IDLE"
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
        