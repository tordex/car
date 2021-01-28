import Adafruit_PCA9685
from steering import Steering
from pwm_manager import PWM

SERVO_0 = 110
""" Servo value for 0 degrees """
SERVO_180 = 610
""" Servo value for 180 degrees """

MAX_ANGLE = -45
""" Maximum angle for steering wheel """
MIN_ANGLE = 45
""" Minimum angle for steering wheel """


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class RetryCount(object):

    def __init__(self, count: int):
        self.count = count

    def __call__(self, f):
        def wrapped_f(*args):
            for i in range(0, self.count):
                try:
                    f(*args)
                    break
                except Exception as err:
                    print("exception: {}".format(str(err)))
        return wrapped_f


class ServoMotor:

    def __init__(self, pwm: PWM, channel: int):
        self._pwm = pwm
        self._channel = channel
        self.last_angle = 0

    @RetryCount(3)
    def set_angle(self, value):
        servo_value = int(map_range(value, 0, 180, SERVO_0, SERVO_180))
        if self.last_angle != servo_value:
            self._pwm.set_pwm(self._channel, 0, servo_value)
            self.last_angle = servo_value


class DCMotor:
    """
    Class for controlling DC motor
    """

    def __init__(self, pwm: PWM, channel_fwd: int, channel_rev: int):
        self._pwm = pwm
        self._channel_fwd = channel_fwd
        self._channel_rev = channel_rev
        self._speed_fwd = 0
        self._speed_rev = 0
        self._brake = False
        self._differential = 1

    @RetryCount(3)
    def _update_speed(self):
        """
        Update speed of motor depending of class members.


        :return: None
        """
        if self._brake:
            self._pwm.set_pwm(self._channel_fwd, 0, 4095)
            self._pwm.set_pwm(self._channel_rev, 0, 4095)
        else:
            if self._speed_fwd > self._speed_rev:
                speed = int((self._speed_fwd - self._speed_rev) * self._differential)
                self._pwm.set_pwm(self._channel_fwd, 0, speed)
                self._pwm.set_pwm(self._channel_rev, 0, 0)
            else:
                speed = int((self._speed_rev - self._speed_fwd) * self._differential)
                self._pwm.set_pwm(self._channel_fwd, 0, 0)
                self._pwm.set_pwm(self._channel_rev, 0, speed)

    def forward(self, value, min_value, max_value):
        self._speed_fwd = int(map_range(value, min_value, max_value, 0, 4095))
        self._update_speed()

    def reverse(self, value, min_value, max_value):
        self._speed_rev = int(map_range(value, min_value, max_value, 0, 4095))
        self._update_speed()

    def brake(self, value):
        self._brake = value
        self._update_speed()

    def stop(self):
        self._speed_fwd = 0
        self._speed_rev = 0
        self._update_speed()

    def set_differential(self, diff):
        self._differential = diff
        self._update_speed()


class Car:
    """
    Class for controlling the car
    """

    def __init__(self):
        self.pwm = PWM(6)
        self.pwm.start()
        # self.pwm.set_pwm_freq(60)
        self.steering_wheel_left = ServoMotor(self.pwm, 0)
        self.steering_wheel_right = ServoMotor(self.pwm, 1)
        self.left_motor = DCMotor(self.pwm, 2, 3)
        self.right_motor = DCMotor(self.pwm, 4, 5)
        self.steering = Steering(
            mount_height=46.1,
            mount_width=40.0,
            wheel_arm=26.1,
            servo_horn=20.0,
            bridge=40.0,
            width=123,
            length=193.650
        )

    def on_steering_wheel(self, value, min_value, max_value):
        """
        Call on steering wheel moving

        :param value: current position of steering wheel
        :param min_value: minimum value for steering wheel position
        :param max_value: maximum value for steering wheel position
        :return: None
        """
        angle = map_range(value, min_value, max_value, MIN_ANGLE, MAX_ANGLE)
        left_angle, right_angle, left_radius, right_radius = self.steering.get_servo_angles(angle)
        self.steering_wheel_left.set_angle(90 - left_angle)
        self.steering_wheel_right.set_angle(90 - right_angle)
        if left_radius < 0 or right_radius < 0 or right_radius == left_radius:
            self.left_motor.set_differential(1)
            self.right_motor.set_differential(1)
        elif left_radius < right_radius:
            self.right_motor.set_differential(1)
            self.left_motor.set_differential(left_radius / right_radius)
        elif left_radius > right_radius:
            self.right_motor.set_differential(1)
            self.left_motor.set_differential(right_radius / left_radius)

    def on_forward(self, value, min_value, max_value):
        """
        Call on forward controller move.

        :param value: current position of forward controller
        :param min_value: minimum value for forward controller position
        :param max_value: maximum value for forward controller position
        :return: None
        """
        self.left_motor.forward(value, min_value, max_value)
        self.right_motor.forward(value, min_value, max_value)

    def on_reverse(self, value, min_value, max_value):
        """
        Call on reverse controller move.

        :param value: current position of reverse controller
        :param min_value: minimum value for reverse controller position
        :param max_value: maximum value for reverse controller position
        :return: None
        """
        self.left_motor.reverse(value, min_value, max_value)
        self.right_motor.reverse(value, min_value, max_value)

    def on_brake(self, value):
        """
        Call on brake key

        :param value: True - key is down, False - key is up
        :return: None
        """
        self.left_motor.brake(value)
        self.right_motor.brake(value)

    def _init_wheels(self):
        # Move wheel to center
        self.steering_wheel_left.set_angle(90)
        self.steering_wheel_right.set_angle(90)
        # Stop DC motors
        self.left_motor.stop()
        self.right_motor.stop()
        self.right_motor.set_differential(1)
        self.left_motor.set_differential(1)

    def on_disconnected(self):
        """
        Call on controller disconnect.
        Stop car

        :return: None
        """
        self._init_wheels()

    def on_connected(self):
        """
        Call on controller is connected.
        Stop car

        :return: None
        """
        self._init_wheels()

    def close(self):
        self.pwm.stop()


if __name__ == '__main__':
    my_car = Car()

    while True:
        val = int(input("angle: "))
        my_car.on_steering_wheel(val, -45, 45)


