from can_py import _can_py
import time


class Motor:
    def __init__(self, can_id, dir=1):
        self.can_id = can_id
        self.dir = dir
        self.motor_msg = {}

    def set_rpm(self, rpm):
        _can_py.send_rpm(self.can_id, rpm * self.dir)

    def set_pos(self, pos):
        _can_py.send_pos(self.can_id, pos)


class Robot:
    def __init__(self):
        self.motor_left = Motor(33)
        self.motor_right = Motor(32)
        self.motor_front = Motor(31)
        self.motor_msg = {}

    def read_motor_msg(self):
        id, data = _can_py.recv()
        self.motor_msg[id] = {
            "id": id,
            "rpm": data.rpm,
            "pos": data.pid_pos_now,
            "current": data.current,
            "duty": data.duty,
            "input_voltage": data.input_voltage,
        }
        return self.motor_msg


if __name__ == "__main__":
    robot = Robot()
    try:
        while True:
            id, data = _can_py.recv()
            # print(id)
            robot.motor_left.set_rpm(1000)
            robot.motor_right.set_rpm(1000)
            robot.motor_front.set_rpm(1000)
            # time.sleep(0.0001)
    except Exception as e:
        assert False, e
    finally:
        del _can_py
