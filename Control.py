import communication
import constants as c

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
print bcolors.UNDERLINE + "Either type command in form IDcommandvalue or one after the other. To repeat the last command, simply press 'r' and enter'\n" + bcolors.ENDC
while True:
    print "_" * 100
    identifier = raw_input('ID [0:11] or whole command: \t\t\t')
    if identifier == 'r':
        if message == '':
            print bcolors.FAIL + 'No message sent so far!' + bcolors.ENDC
        else:
            print bcolors.OKGREEN + "Repeating last command:\t\t\t\t" + bcolors.OKBLUE + message + bcolors.ENDC
            communication.send_broadcast_message(c.PORT, message)
    else:
        # one-input mode
        if len(identifier) > 2:
            string = identifier
            if not string[0].isdigit():
                print bcolors.FAIL + 'First character must be digit!' + bcolors.ENDC
                continue
            if string[1].isdigit():
                identifier = '1' + string[0:1]
                string = string[2:]
                
            else:
                identifier = str('10' + string[0])
                string = string[1:]
            # mode command
            if string[0].lower() == 'm':
                command = c.COMMAND_MODE
                string = string[1:]
                if 'd' in string.lower():
                    value = c.VALUE_MODE_IDLE
                elif 'n' in string.lower():
                    value = c.VALUE_MODE_INIT
                else:
                    print bcolors.FAIL + "MODE NOT RECOGNIZED" + bcolors.ENDC
                    continue
            # speed commmand
            elif string[0].lower() == 's':
                command = c.COMMAND_SPEED
                string = string[1:]
                if string[0] == '+':
                    value = c.VALUE_SPEED_INCREMENT
                elif string[0] == '-':
                    value = c.VALUE_SPEED_DECREMENT
                else:
                    try:                        
                        value = str(int(string))
                    except ValueError:
                        print bcolors.FAIL + 'VALUE NOT AN INTEGER \nrepeat!' + bcolors.ENDC
                        continue
                    print value                                                                    
            # blink command        
            elif string[0].lower() == 'b':
                commmand = c.COMMAND_BLINK
                value = ''
            else:
                print bcolors.FAIL + 'COMMAND UNKNOWN! \n repeat!' + bcolors.ENDC
                continue
                
        # sequential input mode
        else:
            # parsing identififer
            if len(identifier) == 1:
                identifier = '0' + identifier
            identifier = '1' + identifier
            #print 'Talking to robot with id ' + identifier
            try: 
                int(identifier)
            except ValueError:
                print bcolors.FAIL + 'VALUE NOT AN INTEGER \nrepeat!' + bcolors.ENDC
                continue
                
            if c.SQUAD_START > int(identifier) or int(identifier) > c.SQUAD_END:
                print bcolors.FAIL + "NO ROBOT WITH THIS ID IN SQUAD. \nrepeat!" + bcolors.ENDC
                continue
            
            # parsing command            
            command = raw_input("Type command:\t(s)peed | (m)ode | (b)link\t")
            command = command.lower()
            # mode change
            if command == 'm':                
                command = c.COMMAND_MODE
                # parsing value
                value = raw_input("Type mode:\t i(d)le | i(n)it\t\t")
                value = value.lower()
                if value == 'd':
                    value = c.VALUE_MODE_IDLE
                elif value == 'n':
                    value = c.VALUE_MODE_INIT
                else:
                    print bcolors.FAIL + "MODE NOT RECOGNIZED" + bcolors.ENDC
                    continue
            # speed change
            elif command == 's':                
                command = c.COMMAND_SPEED
                #parsing value
                value = raw_input("Type absolute value OR \'+\' or \'-\'\t")
                if value == '+':
                    value = c.VALUE_SPEED_INCREMENT
                elif value == '-':
                    value = c.VALUE_SPEED_DECREMENT
                else:
                    try:
                        int(value)
                    except ValueError:
                        print bcolors.FAIL + 'VALUE NEITHER \'+\' or \'-\' NOR AN INTEGER \nrepeat!' + bcolors.ENDC
                        continue
                    if 0 > int(value) or int(value) > 100:
                        print 'VALUE NOT IN RANGE \nrepeat!'
                        continue
            # blink       
            elif command == 'b':                
                command = c.COMMAND_BLINK
                value = ""
                

            else:
                print bcolors.FAIL + 'COMMAND UNKNOWN! \n repeat!' + bcolors.ENDC
                continue
            # everything should be valid...
        message = identifier + " " + command + " " + value    
        print bcolors.OKGREEN +  'Sent message:\t\t\t\t\t' + bcolors.OKBLUE + message + bcolors.ENDC
        communication.send_broadcast_message(c.PORT, message)
    
                
            
    
        