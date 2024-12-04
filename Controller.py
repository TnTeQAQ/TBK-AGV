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
        self.info = {
            "subscriber": {},
            "publisher": {},
        }
        self.subscriber = {}
        self.publisher = None
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
        self.data = {"info": self.info, "can_data": can_data, "imu_data": imu_data}

    def get_can_data(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        t_data = {}
        for i in data._fields_:
            key = i[0]
            t_data[key] = getattr(data, key)
        self.can_data[id] = t_data
        return self.can_data

    def get_imu_data(self):
        self.imu_data = jy901s.get_data()
        return self.imu_data

    def flash_tbk(self):
        self.flash_subscriber()
        self.flash_publisher()

    def flash_subscriber(self):
        for i in list(self.can_data.keys()):
            if i not in self.subscriber.keys():
                sub_info = {}
                sub_info["name"] = "RPM"
                sub_info["msg_name"] = f"MOTOR_CONTROL_{i}"
                sub_info["msg_type"] = "float"
                self.info["subscriber"][i] = sub_info
                self.subscriber[i] = tbkpy.Subscriber(
                    sub_info["name"],
                    sub_info["msg_name"],
                    lambda msg: self.set_speed(msg, i),
                    print,
                )

    def flash_publisher(self):
        if self.publisher is None:
            can_info = tbkpy.EPInfo()
            can_info.name = "AGV_DATA"
            can_info.msg_name = f"ALL_DATA"
            can_info.msg_type = "dict"
            self.info["publisher"] = {
                "name": can_info.name,
                "msg_name": can_info.msg_name,
                "msg_type": can_info.msg_type,
            }
            self.publisher = tbkpy.Publisher(can_info)
        else:
            self.publisher.publish(pickle.dumps(self.data))

    def set_speed(self, msg, can_id):
        data = pickle.loads(msg)
        print(can_id)
        print(self.subscriber)
        print(data)
        # v_motor = motor_msg.motor2self(x, y, w)
        # try:
        #     for id in v_motor:
        #         rpm = v_motor[id]["rpm"]
        #         _can_py.send_rpm(id, float(rpm))
        #         # time.sleep(0.02)
        # except Exception as e:
        #     print(e)


if __name__ == "__main__":
    ctr = Controller()
    try:
        while True:
            time.sleep(0.03)
    finally:
        del _can_py
