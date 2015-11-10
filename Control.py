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
    
def set_numberof_com_bots(number_of_com_bots):
    pass


print bcolors.UNDERLINE + "Either type command in form IDcommandvalue or one after the other. To repeat the last command, simply press 'r' and enter'\n" + bcolors.ENDC
while True:
    print "_" * 100
    identifier = raw_input('ID ([0:11] or \'a\') or whole command: \t\t\t')
    if identifier == 'r':
        if message == '':
            print bcolors.FAIL + 'No message sent so far!' + bcolors.ENDC
        else:
            print bcolors.OKGREEN + "Repeating last command:\t\t\t\t\t" + bcolors.OKBLUE + message + bcolors.ENDC
            communication.send_broadcast_message(c.PORT, message)
    # not repeating        
    else:
        # one-input mode
        if len(identifier) > 2:
            string = identifier
            if string[0].lower() == 'a':
                identifier = 'a'
                string = string[1:]
            elif not string[0].isdigit():
                print bcolors.FAIL + 'First character must be digit!' + bcolors.ENDC
                continue
            elif string[1].isdigit():
                identifier = str("1" + string[0:2])
                string = string[2:]
            else:
                identifier = str('10' + string[0])
                string = string[1:]
            # mode command
            if string[0].lower() == 's':
                command = c.COMMAND_STATE
                string = string[1:]
                if 'i' in string.lower():
                    value = c.VALUE_STATE_IDLE
                elif 'r' in string.lower():
                    value = c.VALUE_STATE_RUNNING
                else:
                    print bcolors.FAIL + "STATE NOT RECOGNIZED" + bcolors.ENDC
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
            elif string[0].lower() == 't':
                command = c.COMMAND_TYPE
                string = string[1:]
                if 'c' in string.lower():
                    value = c.VALUE_TYPE_COM
                elif 'a' in string.lower():
                    value = c.VALUE_TYPE_AUTO
                elif 'i' in string.lower():
                    value = c.VALUE_TYPE_IDLE
                else:
                    print bcolors.FAIL + "TYPE NOT RECOGNIZED" + bcolors.ENDC
                    continue
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
                
            if c.TEAM_START > int(identifier) or int(identifier) > c.TEAM_END:
                print bcolors.FAIL + "NO ROBOT WITH THIS ID IN SQUAD. \nrepeat!" + bcolors.ENDC
                continue
            
            # parsing command            
            command = raw_input("Type command:\t(s)peed | (t)ype | st(a)te | (b)link\t")
            command = command.lower()
            # mode change
            if command == 'T':                
                command = c.COMMAND_STATE
                # parsing value
                value = raw_input("Type mode:\t (i)dle | (r)unning\t\t")
                value = value.lower()
                if value == 'i':
                    value = c.VALUE_STATE_IDLE
                elif value == 'r':
                    value = c.VALUE_STATE_RUNNING
                else:
                    print bcolors.FAIL + "STATE NOT RECOGNIZED" + bcolors.ENDC
                    continue
            # speed change
            elif command == 's':                
                command = c.COMMAND_SPEED
                #parsing value
                value = raw_input("Type absolute value OR \'+\' or \'-\'\t\t\t")
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
            elif command == 't':
                command = c.COMMAND_TYPE
                value = raw_input("Type type:\t(c)omm | (a)uto | (i)dle\t\t").lower()
                if value == 'c':
                    value == c.VALUE_TYPE_COMM
                elif value == 'a':
                    value == c.VALUE_TYPE_AUTO
                elif value == 'i':
                    value == c.VALUE_TYPE_IDLE
                else:
                    print bcolors.FAIL + "TYPE NOT RECOGNIZED" + bcolors.ENDC
                    continue
                
            elif command == 'b':                
                command = c.COMMAND_BLINK
                value = ""
                

            else:
                print bcolors.FAIL + 'COMMAND UNKNOWN! \n repeat!' + bcolors.ENDC
                continue
        # everything should be valid...
        # to all...
        if identifier == 'a':
            for identifier in range(c.TEAM_START, c.TEAM_END + 1):
                target_ip = c.SUBNET_IP + identifier
                message = command + " " + value
                communication.send_broadcast_message(c.PORT, message)
        # to one bot
        else:
            target_ip = c.SUBNET_IP + identifier
            message = command + " " + value    
            communication.send_udp_unicast_message(target_ip, c.PORT, message)
        print bcolors.OKGREEN +  'Sent message:\t\t\t\t\t\t' + bcolors.OKBLUE + message + bcolors.ENDC
    
                
            
    
        