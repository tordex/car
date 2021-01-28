import evdev
import car
import time
import os

my_car = car.Car()


def process_key(name, ev):
    if ev.value == 1:
        print("**** {name}\tdown".format(name=name))
    else:
        print("**** {name}\tup".format(name=name))


def process_abs(name, value, absinfo):
    percent = 100 * float(value - absinfo.min) / float(absinfo.max - absinfo.min)
    # print("#### {name}\t{percent}".format(name=name, percent=percent))


if __name__ == '__main__':
    connected = False
    xbox_time = 0
    menu_time = 0
    while True:
        try:
            time.sleep(2)
            gamepad = evdev.InputDevice('/dev/input/event0')
            print(gamepad)

            my_car.on_connected()
            connected = True

            dev_caps = gamepad.capabilities()

            def find_caps(ev_type, ev_code):
                for data in dev_caps[ev_type]:
                    if data[0] == ev_code:
                        return data[1]
                return None

            for event in gamepad.read_loop():
                if event.type == evdev.ecodes.EV_SYN:
                    continue
                elif event.type == evdev.ecodes.EV_KEY:
                    if event.code == evdev.ecodes.BTN_A:
                        process_key("A", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_B:
                        my_car.on_brake(event.value == 1)
                        continue

                    elif event.code == evdev.ecodes.BTN_C:
                        process_key("X", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_NORTH:
                        process_key("Y", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_WEST:
                        process_key("LB", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_Z:
                        process_key("RB", event)
                        continue

                    elif event.code == evdev.ecodes.KEY_MENU:
                        if event.value == 1:
                            if time.time() - xbox_time < 0.5:
                                os.system("sudo poweroff")
                                xbox_time = 0
                            else:
                                xbox_time = time.time()
                        continue

                    elif event.code == evdev.ecodes.BTN_TL:
                        process_key("TOOLS", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_TR:
                        if event.value == 1:
                            if time.time() - menu_time < 0.5:
                                os.system("sudo reboot")
                                menu_time = 0
                            else:
                                menu_time = time.time()
                        continue

                    elif event.code == evdev.ecodes.BTN_TR2:
                        process_key("RIGHT_STICK", event)
                        continue

                    elif event.code == evdev.ecodes.BTN_TL2:
                        process_key("LEFT_STICK", event)
                        continue

                elif event.type == evdev.ecodes.EV_ABS:
                    caps = find_caps(event.type, event.code)
                    if event.code == evdev.ecodes.ABS_X:
                        my_car.on_steering_wheel(event.value, caps.min, caps.max)
                        # process_abs("X", event.value, caps)
                        continue

                    elif event.code == evdev.ecodes.ABS_Y:
                        process_abs("Y", event.value, find_caps(event.type, event.code))
                        continue

                    elif event.code == evdev.ecodes.ABS_Z:
                        my_car.on_reverse(event.value, caps.min, caps.max)
                        continue

                    elif event.code == evdev.ecodes.ABS_RZ:
                        my_car.on_forward(event.value, caps.min, caps.max)
                        continue

                    elif event.code == evdev.ecodes.ABS_RX:
                        process_abs("RX", event.value, find_caps(event.type, event.code))
                        continue

                    elif event.code == evdev.ecodes.ABS_RY:
                        process_abs("RY", event.value, find_caps(event.type, event.code))
                        continue

                    elif event.code == evdev.ecodes.ABS_HAT0X:
                        process_abs("HAT-X", event.value, find_caps(event.type, event.code))
                        continue

                    elif event.code == evdev.ecodes.ABS_HAT0Y:
                        process_abs("HAT-Y", event.value, find_caps(event.type, event.code))
                        continue
        except KeyboardInterrupt:
            my_car.close()
            exit(0)
        except Exception as err:
            if connected:
                my_car.on_disconnected()
            connected = False
            print("main exception: {}".format(str(err)))
