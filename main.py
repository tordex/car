import car
import time
import gamepad
from gpiozero import LED, Button
import pydbus

my_car = car.Car()
pad_led = LED(17)
pad_button = Button(pin=23)
connected = False


def connect_gamepad():
    if connected:
        print("connect_gamepad: gamepad is already connected")
        return
    gamepad_dev = "5C:BA:37:86:31:97"
    adapter_path = '/org/bluez/hci0'
    device_path = f'{adapter_path}/dev_{gamepad_dev.replace(":", "_")}'
    bluez_service = 'org.bluez'
    bus = pydbus.SystemBus()

    print("Starting bluetooth connection...")
    pad_led.blink(on_time=0.5, off_time=0.5, n=None, background=True)
    for i in range(0, 5):
        try:
            print("Try #{}".format(i))
            adapter = bus.get(bluez_service, adapter_path)
            device = bus.get(bluez_service, device_path)
            device.Connect()
            print("Bluetooth is connected")
            pad_led.on()
            return
        except Exception as er:
            print(str(er))
            time.sleep(5)
    print("Bluetooth connection error")
    pad_led.blink(on_time=0.2, off_time=0.2, n=2)


if __name__ == '__main__':
    xbox_time = 0
    menu_time = 0
    pad = None
    pad_button.when_pressed = connect_gamepad
    while True:
        try:
            time.sleep(2)
            pad = gamepad.GamePad()

            pad.attach_axis(gamepad.AXIS_GAS, my_car.on_forward)
            pad.attach_axis(gamepad.AXIS_BRAKE, my_car.on_reverse)
            pad.attach_axis(gamepad.AXIS_X, my_car.on_steering_wheel)
            pad.attach_axis(gamepad.AXIS_Z, my_car.on_camera_rotate)
            pad.attach_axis(gamepad.AXIS_HAT0Y, my_car.on_light)
            pad.attach_button(gamepad.BTN_B, my_car.on_brake)

            pad.open()

            print("Connected, starting GamePad loop")
            pad_led.on()
            my_car.on_connected()
            connected = True

            pad.loop()
        except KeyboardInterrupt:
            my_car.close()
            exit(0)
        except Exception as err:
            if connected:
                pad_led.off()
                my_car.on_disconnected()
            if pad:
                pad.close()
                pad = None
            connected = False
            print("main exception: {}".format(str(err)))
