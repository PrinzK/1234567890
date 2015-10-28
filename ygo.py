import communication
import pi2go
import time

# CONSTANTS
PORT= 5005
LED_ON = 1000
LED_OFF = 0
CLEAR = True
OBSTACLE = False

# Configuration
MIN_DIST= 15
SLOW_DIST= 40
L_SPEED_RUN = 60
R_SPEED_RUN = 60
L_SPEED_SLOW = 30
R_SPEED_SLOW = 30

OWN_ID = communication.get_id()

state = "NOT_IDLE"
sub_state_motor = "RUN"
prev_sub_state_motor = "STOP"
sub_sub_state_stop = "OWN"
state_list = []
prev_state_list = []

for x in range (0,12):
    state_list.append(CLEAR)
    prev_state_list.append(CLEAR)
slow = False

#distance = 50
last_dist_check = 0

try:
    pi2go.init()
    sock = communication.init_nonblocking_receiver('', PORT)

    def update_state_list():
        for msg, ID in message_list:
            if ID == OWN_ID:
                continue
            # print OWN_ID, " : ", message, " from ", ID
            if msg == "False":
                msg = False
            elif message == "True" or message == "SLOW":
                msg = True
            state_list[ID] = msg
        # return state_list

    while True:
        if state == "IDLE":
            pi2go.setAllLEDs(LED_OFF, LED_OFF, LED_ON)
            message, addr = communication.receive_message(sock)
            print OWN_ID
            if message != '':
                # print message
                pass
            #if  "MASTER_START" in message:
            if "START" in message:
                state = "NOT_IDLE"
        if state == "NOT_IDLE":
            ##### SENSOR
            if time.time() - last_dist_check > 0.2:
                last_dist_check = time.time()
                distance = pi2go.getDistance()

                # print state_list
            irCentre = pi2go.irCentre()

            if irCentre or distance < MIN_DIST:
                state_list[OWN_ID] = OBSTACLE
                #print "After setting it: own state: " + str(state_list[OWN_ID])
                #print "irCentre: " + str(irCentre)
            else:
                state_list[OWN_ID] = CLEAR
            # print "P : ", prev_state_list[OWN_ID]
            # print "C : ", state_list[OWN_ID]
            if prev_state_list[OWN_ID] != state_list[OWN_ID]:
                print "Sending state : ", str(state_list[OWN_ID])
                for x in range(10):
                    communication.send_broadcast_message(PORT, str(state_list[OWN_ID]))

            if distance < SLOW_DIST:
                slow = True
            else:
                slow = False

            # print "BEFORE RECEIVING: " + str(state_list)
            #### RECEIVE
            message_list = communication.receive_message_list(sock)
            update_state_list()
            
            ##### SEND
            # print "    AFTER RECEIVING: " + str(state_list)
            
            ##### SET SUB_STATE
            if all(state_list):
                if slow:                   
                    sub_state_motor = "SLOW"
                else:
                    sub_state_motor = "RUN"
            else:
                sub_state_motor = "STOP"
            # print "After receiving: own state: " + str(state_list[OWN_ID]) + " " + sub_state_motor
            ##### SUB_STATE: MOTOR
            if prev_sub_state_motor == sub_state_motor:
                #print "I'll pass.."
                pass
            elif sub_state_motor == "RUN":
                # print sub_state_motor
                pi2go.turnForward(L_SPEED_RUN, R_SPEED_RUN)
                pi2go.setAllLEDs(LED_OFF, LED_ON, LED_OFF)
            elif sub_state_motor == "SLOW":
                # print sub_state_motor
                pi2go.turnForward(L_SPEED_SLOW, R_SPEED_SLOW)
                pi2go.setAllLEDs(LED_ON, LED_ON, LED_OFF)
            elif sub_state_motor == "STOP":
                # print sub_state_motor
                pi2go.stop()
                pi2go.setAllLEDs(LED_ON, LED_OFF, LED_OFF)
            else:
                print "I am so confused...."

            prev_sub_state_motor = sub_state_motor
            prev_state_list = state_list[:]

                
except object as p:
    print p            
except KeyboardInterrupt:
    print "Exiting program"
finally:
    pi2go.cleanup()