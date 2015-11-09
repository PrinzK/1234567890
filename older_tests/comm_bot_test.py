import communication
import constants as c

def start():
    sock = communication.init_receiver('', c.PORT)
    message = ''
    message, addr = communication.receive_message(sock)
    status = "In comm_bot_test"
    print status
    communication.send_broadcast_message(5003, status)
    return message
    
    