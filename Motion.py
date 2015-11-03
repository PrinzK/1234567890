import constants

def distance_control(distance, speed_slow, SPEED_RUN = 0, DIST_REF, KP, SPEED_CONTROL_MAX, SPEED_CONTROL_MIN):
    if speed_slow == 0:
        SPEED_RUN = constants.SPEED_RUN
        DIST_REF = constants.SPEED_RUN
        KP = constants.KP
        SPEED_CONTROL_MAX = constants.SPEED_CONTROL_MAX
        SPEED_CONTROL_MIN = constants.SPEED_CONTROL_MIN
    speed_slow = SPEED_RUN - (DIST_REF-DISTANCE) * KP
                # Controlllimits
    if speed_slow > SPEED_CONTROL_MAX:
        speed_slow = SPEED_CONTROL_MAX
    elif speed_slow < SPEED_CONTROL_MIN:
        speed_slow = SPEED_CONTROL_MIN
    return speed_slow
    