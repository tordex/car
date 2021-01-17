import Adafruit_PCA9685


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class ServoMotor:

    def __init__(self, pwm: Adafruit_PCA9685.PCA9685, channel: int, min_val: int, max_val: int):
        self._pwm = pwm
        self._channel = channel
        self._servo_min = min_val  # Min pulse length out of 4096
        self._servo_max = max_val  # Max pulse length out of 4096

    def set_value(self, value, min_value, max_value):
        servo_value = int(map_range(value, min_value, max_value, self._servo_min, self._servo_max))
        self._pwm.set_pwm(self._channel, 0, servo_value)


class DCMotor:
    """
    Class for controlling DC motor
    """

    def __init__(self, pwm: Adafruit_PCA9685.PCA9685, channel_fwd: int, channel_rev: int):
        self._pwm = pwm
        self._channel_fwd = channel_fwd
        self._channel_rev = channel_rev
        self._speed_fwd = 0
        self._speed_rev = 0
        self._brake = False

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
                speed = self._speed_fwd - self._speed_rev
                self._pwm.set_pwm(self._channel_fwd, 0, speed)
                self._pwm.set_pwm(self._channel_rev, 0, 0)
            else:
                speed = self._speed_rev - self._speed_fwd
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


class Car:
    """
    Class for controlling the car
    """

    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)
        self.steering_wheel = ServoMotor(self.pwm, 0, 225, 475)
        self.left_motor = DCMotor(self.pwm, 1, 2)
        self.right_motor = DCMotor(self.pwm, 3, 4)

    def on_steering_wheel(self, value, min_value, max_value):
        """
        Call on steering wheel moving

        :param value: current position of steering wheel
        :param min_value: minimum value for steering wheel position
        :param max_value: maximum value for steering wheel position
        :return: None
        """
        self.steering_wheel.set_value(value, min_value, max_value)

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

