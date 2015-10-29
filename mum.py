import communication
#import comm_bot
#import auto_bot

PORT = 5004

sock = communication.init_blocking_receiver('', PORT, 1)

print "Hey there!"

try:
    while True:
        message, addr = communication.receive_message(sock)
        if "GO_COMM" in message:
            #message = bot_comm.start()
            print "I'm in comm_mode now!"            
        elif "GO_AUTO" in message:
            #message = bot_auto.start()
            print "I'm in auto_mode now!"
except KeyboardInterrupt:
    print "Exiting mum.py \n Talk to me with ssh!"
        