import Adafruit_PCA9685


def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class ServoMotor:

    def __init__(self, pwm: Adafruit_PCA9685.PCA9685, channel, min_val, max_val):
        self._pwm = pwm
        self._channel = channel
        self._servo_min = min_val  # Min pulse length out of 4096
        self._servo_max = max_val  # Max pulse length out of 4096

    def set_value(self, value, min_value, max_value):
        servo_value = int(map_range(value, min_value, max_value, self._servo_min, self._servo_max))
        self._pwm.set_pwm(self._channel, 0, servo_value)


class Car:

    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)
        self.steering_wheel = ServoMotor(self.pwm, 0, 225, 475)

    def on_steering_wheel(self, value, min_value, max_value):
        self.steering_wheel.set_value(value, min_value, max_value)
