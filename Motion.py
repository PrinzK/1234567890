def distance_control(speed_slow = 0, SPEED_RUN, DIST_REF, distance, KP, SPEED_CONTROL_MAX):
    SPEED_SLOW = SPEED_RUN - (DIST_REF-DISTANCE) * KP
                # Controlllimits
                if SPEED_SLOW > SPEED_CONTROL_MAX:
                    SPEED_SLOW = SPEED_CONTROL_MAX
                elif SPEED_SLOW < SPEED_CONTROL_MIN:
                    SPEED_SLOW = SPEED_CONTROL_MIN