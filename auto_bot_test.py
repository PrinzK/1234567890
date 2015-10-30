import communication


def start():
    sock = communication.init_receiver('', 5003)
    message = ''
    message, addr = communication.receive_message(sock)
    print "In auto_bot_test"
    return message
    
    