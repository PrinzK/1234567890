import communication
COMMAND_PORT = 5005
MODE_PORT= 5006 
SENDING_ATTEMPTS = 20

sock = communication.init_nonblocking_receiver('', MODE_PORT)
state_list = []
for x in range (0,12):
    state_list.append("RUN")


def get_modes():
    message_list = communication.receive_message_list(sock)
    state_list = communication.update_state_list(state_list, message_list)
    print state_list
		

def start_comm_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, "STARTCOMM", SENDING_ATTEMPTS)
def start_auto_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, "STARTAUTO", SENDING_ATTEMPTS)
def start_all_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, "STARTALL", SENDING_ATTEMPTS)
def stop_all_robots():
    communication.send_x_broadcast_messages(COMMAND_PORT, "GOIDLE", SENDING_ATTEMPTS)