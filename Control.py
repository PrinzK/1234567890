import communication
from constants import *


sock = communication.init_nonblocking_receiver('', MODE_PORT)

def get_modes():
    state_list = []
    for x in range (0,15):
        state_list.append("RUN")
    message_list = communication.receive_message_list(sock)
    state_list = communication.update_state_list(state_list, message_list)
    print state_list
		

def start_comm_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, GO_COMM, SENDING_ATTEMPTS)
def start_auto_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, GO_AUTO, SENDING_ATTEMPTS)
def start_all_bots():
    communication.send_x_broadcast_messages(COMMAND_PORT, START_ALL, SENDING_ATTEMPTS)
def stop_all_robots():
    communication.send_x_broadcast_messages(COMMAND_PORT, GO_IDLE, SENDING_ATTEMPTS)
    
#get_modes()
    
def set_speed(robot = N, speed)