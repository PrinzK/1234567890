import communication
import constants as c


sock = communication.init_nonblocking_receiver('', c.PORT)
message = ''

def get_modes():
    state_list = []
    for x in range (0,15):
        state_list.append("RUN")
    message_list = communication.receive_message_list(sock)
    state_list = communication.update_state_list(state_list, message_list)
    print state_list
		

def start_comm_bots():
    for identifier in range(c.SQUAD_START, c.SQUAD_END):
        communication.send_x_broadcast_messages(c.PORT, c.GO_COMM, c.SENDING_ATTEMPTS)
def start_auto_bots():
    communication.send_x_broadcast_messages(c.PORT, c.GO_AUTO, c.SENDING_ATTEMPTS)
def start_all_bots():
    communication.send_x_broadcast_messages(c.PORT, c.START_ALL, c.SENDING_ATTEMPTS)
def stop_all_robots():
    communication.send_x_broadcast_messages(c.PORT, c.GO_IDLE, c.SENDING_ATTEMPTS)
    
#get_modes()
    
def set_speed(robot, speed):
    pass

while True:
    print "Either type command in form IDcommandvalue or one after the other. To repeat the last command, simply press 'r' and enter"
    identifier = raw_input()
    if identifier == 'r':
        print "Repeating last command: " + message
        communication.send_broadcast_message(c.PORT, message)
    else:
        #len(identifier) > 3:
    
    
            # parsing identififer
            if len(identifier) == 1:
                identifier = '0' + identifier
            identifier = '1' + identifier
            print 'Talking to robot with id ' + identifier
            if c.SQUAD_START > int(identifier) or int(identifier) > c.SQUAD_END:
                print "NO ROBOT WITH THIS ID IN SQUAD. \nrepeat!"
                continue
            
            # parsing command            
            command = raw_input("Type command: (s)peed, (m)ode ")
            command = command.lower()
            # mode change
            if command == 'm':                
                command = c.COMMAND_MODE
                # parsing value
                value = raw_input("Type mode: i(d)le | i(n)it")
                value = value.lower()
                if value == 'd':
                    value = c.VALUE_MODE_IDLE
                elif value == 'n':
                    value = c.VALUE_MODE_INIT
                else:
                    print "MODE NOT RECOGNIZED"
                
                # speed change
            elif command == 's':                
                command = c.COMMAND_SPEED
                #parsing value
                value = raw_input("Type absolute value or \'+\' or \'-\'")
                if value == '+':
                    value = c.VALUE_SPEED_INCREMENT
                elif value == '-':
                    value = c.VALUE_SPEED_DECREMENT
                else:
                    try:
                        int(value)
                    except:
                        print 'VALUE NEITHER \'+\' or \'-\' NOR AN INTEGER \nrepeat!'
                        continue
                    if 0 < int(value) or int(value) > 100:
                        print 'VALUE NOT IN RANGE \nrepeat!'
                        continue
                    
            
            else:
                print 'COMMAND UNKNOWN! \n repeat!'
                continue
            # everything should be valid...
            message = identifier + " " + command + " " + value    
            print 'Sent message: ' + message
            communication.send_broadcast_message(c.PORT, message)
                
                
            
    
        