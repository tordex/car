import Adafruit_PCA9685
import threading


class PWM(threading.Thread):

    def __init__(self, channels):
        super().__init__()
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)
        self._is_stopped = False
        self._lock = threading.Lock()
        self._condition = threading.Condition()
        self._channels = [None] * channels

    def run(self) -> None:
        with self._condition:
            while True:
                values = []
                self._condition.wait()
                if self._is_stopped:
                    break
                with self._lock:
                    for i in range(0, len(self._channels)):
                        if self._channels[i] is not None:
                            values.append((i, self._channels[i]))
                            self._channels[i] = None
                for channel, value in values:
                    for cnt in range(0, 5):
                        try:
                            self.pwm.set_pwm(channel, value[0], value[1])
                            break
                        except Exception as err:
                            print("PWM Error: {}".format(str(err)))

    def stop(self):
        with self._condition:
            self._is_stopped = True
            self._condition.notify_all()
        self.join()

    def set_pwm(self, channel, on, off):
        with self._lock:
            self._channels[channel] = (on, off)
        with self._condition:
            self._condition.notify_all()
