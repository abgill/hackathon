import os
import struct
from ControllerState import ControllerState
from time import sleep

from pprint import pprint

JS_EVENT_SIZE = 8

dev = os.open("/dev/input/js0", os.O_RDONLY)
print(dev)

controller_state = ControllerState()

def unpack_button(button_val, button):
    if(button == b'\x00'):
        controller_state.a = button_val
    elif(button == b'\x01'):
        controller_state.b = button_val
    elif(button == b'\x02'):
        controller_state.y = button_val
    elif(button == b'\x03'):
        controller_state.x = button_val


while True:
    evnt_str = os.read(dev, JS_EVENT_SIZE)

    event = struct.unpack("Ihcc", evnt_str)

    if(event[2] == b'\x01'):
        unpack_button(event[1], event[3])
        # pprint(vars(controller_state))
        print(event)
    elif(event[2] == b'\x02'):
        unpack_button(event[1], event[3])
        # pprint(vars(controller_state))
        print(event)
    else:
        print(event)

