#!/usr/bin/python

# import socket
# import subprocess
import constants as c
# import time
import communication as com


com_set = [108, 111, 110, 102, 113]
auto_set = [112, 107, 104, 109, 102]


def get_addr(id):
    return '192.168.178.' + str(id)

for id in com_set:
    print(get_addr(id))
    com.send_udp_unicast_message(get_addr(id), c.PORT, c.COMMAND_TYPE + " " + c.VALUE_TYPE_COM)

for id in auto_set:
    com.send_udp_unicast_message(get_addr(id), c.PORT, c.COMMAND_TYPE + " " + c.VALUE_TYPE_AUTO)
