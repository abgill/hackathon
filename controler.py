#!/usr/bin/env python3

import os
import struct
from ControllerState import ControllerState
from time import sleep

from gpiozero import Motor
from adafruit_servokit import ServoKit
import threading

from pprint import pprint

JS_EVENT_SIZE = 8

js_disconnected = True

while js_disconnected:
    try:
        dev = os.open("/dev/input/js0", os.O_RDONLY)
        js_disconnected = False
        print("Connected")
    except:
        sleep(3)


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
            # pprint(vars(controller_state))
        elif(event[2] == b'\x02'):
            unpack_axis(event[1], event[3])
            # pprint(vars(controller_state))


def start_js_poller():
    motor1 = Motor(17, 18)
    motor2 = Motor(27, 22)
    motor3 = Motor(23, 24)
    motor4 = Motor(6, 12)
    kit = ServoKit(channels=16)
    kit.servo[0].angle = 90
    kit.servo[4].angle = 90
   
    left_angle = 90
    # right_angle = 90

    while True:
        lock.acquire()
        # pprint(vars(controller_state))
        if controller_state.ls_y > 0:
            motor1.forward(controller_state.ls_y)
        elif controller_state.ls_y < 0:
            motor1.backward(-controller_state.ls_y)
        else:
            motor1.stop()

        if controller_state.rs_y > 0:
            motor2.forward(controller_state.rs_y)
        elif controller_state.rs_y < 0:
            motor2.backward(-controller_state.rs_y)
        else:
            motor2.stop()

        if controller_state.rs_x > 0:
            motor3.forward(controller_state.rs_x)
        elif controller_state.rs_x < 0:
            motor3.backward(-controller_state.rs_x)
        else:
            motor3.stop()

        if controller_state.ls_x > 0:
            motor4.forward(controller_state.ls_x)
        elif controller_state.ls_x < 0:
            motor4.backward(-controller_state.ls_x)
        else:
            motor4.stop()

        

        if controller_state.a > 0:
            kit.servo[0].angle = 180
            kit.servo[4].angle = 0
        if controller_state.b > 0:
            kit.servo[0].angle = 0
            kit.servo[4].angle = 180

        if(controller_state.rt > -.8):
            print(controller_state.rt)
            left_angle = ((controller_state.rt + 1) / 2 ) + left_angle
            if left_angle > 180:
                left_angle = 180
            elif left_angle < 0:
                left_angle = 0
            
            kit.servo[0].angle = left_angle
            kit.servo[4].angle = 180 - left_angle

        if(controller_state.lt > 0):

            print(controller_state.lt)
            left_angle = left_angle - ((controller_state.lt + 1) / 2 )
            if left_angle > 180:
                left_angle = 180
            elif left_angle < 0:
                left_angle = 0
            
            kit.servo[0].angle = left_angle
            kit.servo[4].angle = 180 - left_angle

        # print("s0 ", kit.servo[0].angle,"\ns4 ", kit.servo[4].angle)
        # kit.servo[0].angle = 90
        # kit.servo[4].angle = 90


        lock.release()
        sleep(1.0 / 60.0)


t1 = threading.Thread(target=start_js_listner).start()
t2 = threading.Thread(target=start_js_poller).start()



