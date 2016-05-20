import communication as com
import com_bot
import auto_bot
import constants as c
import helper

helper.blink()
# sock = com.init_receiver('', c.PORT)

OWN_IP = com.get_ip()
OWN_ID = com.get_id_from_ip(OWN_IP)

value = helper.determine_team(OWN_ID)
sock = com.init_nonblocking_receiver('', c.PORT)
try:
    
    # data, addr = com.receive_message(sock)
    # command, value = com.string_to_command(data)
    # com.close_socket(sock)
    while True:
        if c.VALUE_TYPE_COM == value:
            status = "I'm in com_mode now!"            
            print status
            # communication.send_broadcast_message(c.PORT, status)
            com.close_socket(sock)
            value = com_bot.start() 
            sock = com.init_nonblocking_receiver('', c.PORT)
            status = "Exiting com_mode"
            com.send_x_broadcast_messages(c.PORT, "RELEASE", c.SENDING_ATTEMPTS, c.WAIT_SEND)
            print status
            # communication.send_broadcast_message(c.PORT, status)
        elif c.VALUE_TYPE_AUTO == value:
            status = "I'm in auto_mode now!"
            print status
            # communication.send_broadcast_message(PORT, status)
            com.close_socket(sock)
            value = auto_bot.start()
            sock = com.init_nonblocking_receiver('', c.PORT)
            status = "Exiting auto_mode"
            print status
            # communication.send_broadcast_message(PORT, status)
        elif c.VALUE_TYPE_IDLE == value:
            status = "I'm in idle_mode now!"
            print status
            # communication.send_broadcast_message(PORT, status)
            
            data, addr = com.receive_message(sock)
            command, value = com.string_to_command(data)
            while command != c.COMMAND_TYPE and (value != c.VALUE_TYPE_AUTO or value != c.VALUE_TYPE_COM):
                data, addr = com.receive_message(sock)
                command, value = com.string_to_command(data)
            # if command != c.COMMAND_TYPE:
            #    value = c.VALUE_TYPE_IDLE
            # else:
            #    value = c.VALUE_TYPE_IDLE
            
            status = "Exiting idle_mode"
            print status
            # communication.send_broadcast_message(c.PORT, status)
        else:
            print "Error! Going in idle_mode..."
            value = c.VALUE_TYPE_IDLE
        
        
except KeyboardInterrupt:
    print "Exiting mum.py \nTalk to me with ssh now!"
