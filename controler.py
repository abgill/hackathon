import os
import struct
from ControllerState import ControllerState
from time import sleep

from gpiozero import Motor
from adafruit_servokit import ServoKit
import threading

from pprint import pprint

JS_EVENT_SIZE = 8

dev = os.open("/dev/input/js0", os.O_RDONLY)
print(dev)

controller_state = ControllerState()
lock = threading.Lock()

def unpack_button(button_val, button):
    lock.acquire()
    if(button == b'\x00'):
        controller_state.a = button_val
    elif(button == b'\x01'):
        controller_state.b = button_val
    elif(button == b'\x02'):
        controller_state.y = button_val
    elif(button == b'\x03'):
        controller_state.x = button_val
    lock.release()

def get_norm_axis_val(axis_val):
    return axis_val / 32767.0

def unpack_axis(axis_val, axis):
    lock.acquire()
    if axis == b'\x04':
        controller_state.lt = get_norm_axis_val(axis_val)
    elif axis == b'\x05':
        controller_state.rt = get_norm_axis_val(axis_val)
    elif axis == b'\x00':
        controller_state.ls_x = get_norm_axis_val(axis_val)
    elif axis == b'\x01':
        controller_state.ls_y = get_norm_axis_val(axis_val)
    elif axis == b'\x02':
        controller_state.rs_x = get_norm_axis_val(axis_val)
    elif axis == b'\x03':
        controller_state.rs_y = get_norm_axis_val(axis_val)
    lock.release()
        
    
    pass


def start_js_listner():
    while True:
        evnt_str = os.read(dev, JS_EVENT_SIZE)

        event = struct.unpack("Ihcc", evnt_str)

        if(event[2] == b'\x01'):
            unpack_button(event[1], event[3])
            pprint(vars(controller_state))
        elif(event[2] == b'\x02'):
            unpack_axis(event[1], event[3])
            pprint(vars(controller_state))


def start_js_poller():
    motor = Motor(17, 18)
    kit = ServoKit(channels=16)
    kit.servo[0].angle = 180
    while True:
        lock.acquire()
        pprint(vars(controller_state))
        if controller_state.lt > 0:
            motor.forward(controller_state.lt)
        else:
            motor.stop()
        lock.release()
        sleep(1.0 / 60.0)

threading.Thread(target=start_js_listner).start()
threading.Thread(target=start_js_poller).start()




c = raw_input("Type something to quit.")
os.close(dev)

