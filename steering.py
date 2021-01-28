import math


class Steering:
    """
    Steering management
    """

    def __init__(self,
                 mount_height: float,
                 mount_width: float,
                 wheel_arm: float,
                 servo_horn: float,
                 bridge: float,
                 width: float,
                 length: float):
        """
        Steering management

        :param mount_height: distance between wheel mount and servo rotor along the body
        :param mount_width: distance between wheel mount and servo rotor across the body
        :param wheel_arm: length of wheel arm
        :param servo_horn: length of servo horn
        :param bridge: length of bridge between wheel arm and servo horn
        """
        self.mount_height = mount_height
        self.mount_width = mount_width
        self.wheel_arm = wheel_arm
        self.servo_horn = servo_horn
        self.bridge = bridge
        self.debug = True
        self.radius_left = 0
        self.radius_right = 0
        self.width = width
        self.length = length

    def print_val(self, label, value):
        """
        Print debug message in format label: value

        :param label: label text
        :param value: value
        :return: None
        """
        if self.debug:
            print("{}:\t{}".format(label, value))

    def calc_servo_angle(self, wheel_angle):
        """
        Calculate servo angle for given wheel angle

        :param wheel_angle: wheel angle (degree)
        :return: servo angle (degree)
        """
        wheel_angle = math.radians(wheel_angle)
        d1 = self.wheel_arm * math.sin(wheel_angle)
        d2 = self.wheel_arm * math.cos(wheel_angle)
        u = self.mount_height - d2
        o = self.mount_width + d1
        e = math.sqrt(u * u + o * o)
        x1 = math.acos(
            (math.pow(e, 2) + math.pow(self.servo_horn, 2) - math.pow(self.bridge, 2)) / (2 * e * self.servo_horn)
        )
        x2 = math.acos((math.pow(e, 2) + math.pow(o, 2) - math.pow(u, 2)) / (2 * o * e))
        return 90 - math.degrees(x1 + x2)

    def calc_wheels_angles(self, angle):
        if angle < 0:
            left_angle = angle
            a = math.radians(90 + angle)
            b = self.length * math.tan(a)
            c = self.width + b
            d = 180 - 90 - math.degrees(math.atan(self.length / c))
            right_angle = -math.degrees(math.atan(self.length / c))
            left_radius = math.sqrt(math.pow(self.length, 2) + math.pow(b, 2))
            right_radius = math.sqrt(math.pow(self.length, 2) + math.pow(c, 2))
            return left_angle, right_angle, left_radius, right_radius
        elif angle > 0:
            right_angle = angle
            a = math.radians(90 - angle)
            b = self.length * math.tan(a)
            c = self.width + b
            d = 180 - 90 - math.degrees(math.atan(self.length / c))
            left_angle = math.degrees(math.atan(self.length / c))
            left_radius = math.sqrt(math.pow(self.length, 2) + math.pow(c, 2))
            right_radius = math.sqrt(math.pow(self.length, 2) + math.pow(b, 2))
            return left_angle, right_angle, left_radius, right_radius
        else:
            return 0.0, 0.0, -1, -1

    def get_servo_angles(self, angle):
        left_angle, right_angle, radius_left, radius_right = self.calc_wheels_angles(angle)
        if angle != 0:
            right_servo = -self.calc_servo_angle(-right_angle)
            left_servo = self.calc_servo_angle(left_angle)
            return left_servo, right_servo, radius_left, radius_right
        else:
            return 0.0, 0.0, radius_left, radius_right


if __name__ == '__main__':
    steering = Steering(
        mount_height=46.1,
        mount_width=40.0,
        wheel_arm=26.1,
        servo_horn=20.0,
        bridge=40.0,
        width=123,
        length=193.650
    )

    servo_angle = steering.get_servo_angles(30)
    print(servo_angle)
