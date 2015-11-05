import communication


def start():
    sock = communication.init_receiver('', 5003)
    message = ''
    message, addr = communication.receive_message(sock)
    status =  "In auto_bot_test"
    communication.send_broadcast_message(5003, status)
    return message
    
    