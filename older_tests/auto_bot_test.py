import communication
import constants as c

def start():
    sock = communication.init_receiver('', c.PORT)
    message = ''
    message, addr = communication.receive_message(sock)
    status =  "In auto_bot_test"
    print status
    communication.send_broadcast_message(c.PORT, status)
    return message
    
    