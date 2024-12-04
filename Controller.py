import json

import tbkpy._core as tbkpy
from can_py import _can_py
from WTJY901.chs.JY901S import jy901s
import time
import pickle
import threading


class Controller:
    def __init__(self) -> None:
        self.can_data = {}
        self.imu_data = {}
        self.data = {}
        self.subscriber = {}
        self.publisher = {}
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()
        self.flash_data()

    def listen(self):
        while True:
            self.flash_data()
            self.flash_tbk()

    def flash_data(self):
        can_data = self.get_can_data()
        imu_data = self.get_imu_data()
        self.data = {
            "can_data": can_data,
            "imu_data": imu_data
        }

    def get_can_data(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        self.can_data[id] = data
        return self.can_data

    def get_imu_data(self):
        self.imu_data = jy901s.get_data()
        return self.imu_data

    def flash_tbk(self):
        self.flash_subscriber()
        self.flash_publisher()

    def flash_subscriber(self):
        for i in self.can_data.keys():
            if i not in self.subscriber.keys():
                self.subscriber[i] = tbkpy.Subscriber(f"MOTOR_CONTROL_{i}", "RPM", self.set_speed)

    def flash_publisher(self):
        for i in list(self.can_data.keys()):
            if i not in self.publisher.keys():
                can_info = tbkpy.EPInfo()
                can_info.name = "AGV_DATA"
                can_info.msg_name = f"MOTOR_DATA{i}"
                can_info.msg_type = "int"
                self.publisher[i] = tbkpy.Publisher(can_info)
            else:
                self.publisher[i].publish(pickle.dumps(self.can_data[i]))

    def set_speed(self, msg):
        data = pickle.loads(msg)
        print(data)
        # v_motor = motor_msg.motor2self(x, y, w)
        # try:
        #     for id in v_motor:
        #         rpm = v_motor[id]["rpm"]
        #         _can_py.send_rpm(id, float(rpm))
        #         # time.sleep(0.02)
        # except Exception as e:
        #     print(e)


if __name__ == '__main__':
    ctr = Controller()
    try:
        while True:
            time.sleep(0.03)
    finally:
        del _can_py
