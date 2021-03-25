import os
import struct
import array
from fcntl import ioctl

AXIS_X = 0x00
AXIS_Y = 0x01
AXIS_Z = 0x02
AXIS_RX = 0x03
AXIS_RY = 0x04
AXIS_RZ = 0x05
AXIS_TROTTLE = 0x06
AXIS_RUDDER = 0x07
AXIS_WHEEL = 0x08
AXIS_GAS = 0x09
AXIS_BRAKE = 0x0a
AXIS_HAT0X = 0x10
AXIS_HAT0Y = 0x11
AXIS_HAT1X = 0x12
AXIS_HAT1Y = 0x13
AXIS_HAT2X = 0x14
AXIS_HAT2Y = 0x15
AXIS_HAT3X = 0x16
AXIS_HAT3Y = 0x17
AXIS_PRESSURE = 0x18
AXIS_DISTANCE = 0x19
AXIS_TILT_X = 0x1a
AXIS_TILT_Y = 0x1b
AXIS_TOOL_WIDTH = 0x1c
AXIS_VOLUME = 0x20
AXIS_MISC = 0x28

BTN_TRIGGER = 0x120
BTN_THUMB = 0x121
BTN_THUMB2 = 0x122
BTN_TOP = 0x123
BTN_TOP2 = 0x124
BTN_PINKIE = 0x125
BTN_BASE = 0x126
BTN_BASE2 = 0x127
BTN_BASE3 = 0x128
BTN_BASE4 = 0x129
BTN_BASE5 = 0x12a
BTN_BASE6 = 0x12b
BTN_DEAD = 0x12f
BTN_A = 0x130
BTN_B = 0x131
BTN_C = 0x132
BTN_X = 0x133
BTN_Y = 0x134
BTN_Z = 0x135
BTN_TL = 0x136
BTN_TR = 0x137
BTN_TL2 = 0x138
BTN_TR2 = 0x139
BTN_SELECT = 0x13a
BTN_START = 0x13b
BTN_MODE = 0x13c
BTN_THUMBL = 0x13d
BTN_THUMBR = 0x13e

BTN_DPAD_UP = 0x220
BTN_DPAD_DOWN = 0x221
BTN_DPAD_LEFT = 0x222
BTN_DPAD_RIGHT = 0x223
# XBox 360 controller uses these codes.
BTN_DPAD_LEFT_XB360 = 0x2c0
BTN_DPAD_RIGHT_XB360 = 0x2c1
BTN_DPAD_UP_XB360 = 0x2c2
BTN_DPAD_DOWN_XB360 = 0x2c3


class GamePad:

    def __init__(self):
        self.axis_map = []
        self.buttons_map = []
        self.jsdev = None
        self.attached_axis = {}
        self.attached_buttons = {}

    def open(self, dev="/dev/input/js0"):
        print('Opening %s...' % dev)
        self.jsdev = open(dev, 'rb')

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf)  # JSIOCGAXES
        num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf)  # JSIOCGBUTTONS
        num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf)   # JSIOCGAXMAP

        for axis in buf[:num_axes]:
            self.axis_map.append(axis)

        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf)   # JSIOCGBTNMAP

        for btn in buf[:num_buttons]:
            self.buttons_map.append(btn)

    def close(self):
        if self.jsdev:
            self.jsdev.close()
            self.jsdev = None

    def attach_axis(self, axis_id: int, func):
        self.attached_axis[axis_id] = func

    def attach_button(self, btn_id: int, func):
        self.attached_buttons[btn_id] = func

    def loop(self):
        while True:
            ev_buf = self.jsdev.read(8)
            if ev_buf:
                time, value, ev_type, number = struct.unpack('IhBB', ev_buf)

                if ev_type & 0x80:
                    continue

                if ev_type & 0x01:
                    button = self.buttons_map[number]
                    fnc = self.attached_buttons.get(button, None)
                    if fnc:
                        fnc(value)

                if ev_type & 0x02:
                    axis = self.axis_map[number]
                    fnc = self.attached_axis.get(axis, None)
                    if fnc:
                        fnc(value, -32767, 32767)
