import constants

def distance_control(distance, curr_speed, SPEED_RUN = 0, DIST_REF = 0, KP = 0, SPEED_CONTROL_MAX = 0, SPEED_CONTROL_MIN = 0):
    if SPEED_RUN == 0:
        SPEED_RUN = constants.SPEED_RUN
        DIST_REF = constants.SPEED_RUN
        KP = constants.KP
        SPEED_CONTROL_MAX = constants.SPEED_CONTROL_MAX
        SPEED_CONTROL_MIN = constants.SPEED_CONTROL_MIN
        print "Taking default constants"
    curr_speed = SPEED_RUN - (DIST_REF-distance) * KP
                # Controlllimits
    if curr_speed > SPEED_CONTROL_MAX:
        curr_speed = SPEED_CONTROL_MAX
        print "Upper limit reached!"
    elif curr_speed < SPEED_CONTROL_MIN:
        curr_speed = SPEED_CONTROL_MIN
        print "Lower limit reached!"
    return curr_speed
    