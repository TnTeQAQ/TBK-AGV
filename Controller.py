import json

import tbkpy._core as tbkpy
from can_py import _can_py
from WTJY901.chs.JY901S import jy901s
import time
import pickle
import threading


class Controller:
    def __init__(self) -> None:
        self._can_data = {}
        self._imu_data = {}
        self.data = {}
        self.subscriber = {}
        self.publisher = {}
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()
        self.get_all_data()

    def listen(self):
        while True:
            self.get_all_data()

    def pack_msg(self, data, msg_type="unknown", serialize_type="pickle"):
        serialize_func = None
        if serialize_type == "pickle":
            serialize_func = pickle.dumps
        elif serialize_type == "json":
            serialize_func = json.dumps
        elif serialize_type == "dict":
            serialize_func = None
        else:
            pass
        return {
            "msg_type": msg_type,
            "serialize_type": serialize_type,
            "data": serialize_func(data) if callable(serialize_func) else data,
        }
    
    def get_all_data(self):
        self.data = {"can_data": self.can_data, "imu_data": self.imu_data}
        return self.pack_msg(
            data=self.data,
            msg_type="all",
            serialize_type="pickle"
        )

    @property
    def can_data(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        self._can_data[id] = data
        return self.pack_msg(
            data=self._can_data,
            msg_type="can_data",
            serialize_type="pickle"
        )

    @property
    def imu_data(self):
        self._imu_data = jy901s.get_data()
        return self.pack_msg(
            data=self._imu_data,
            msg_type="imu_data",
            serialize_type="pickle"
        )
    
    def create_subscriber(self):
        for i in self._can_data.keys():
            if i not in self.subscriber.keys():
                self.subscriber[i] = tbkpy.Subscriber(f"MOTOR_CONTROL_{i}", "RPM", self.set_speed)
    
    def create_publisher(self):
        pass
        
    def set_speed(msg):
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
            t = ctr.get_all_data()
            print(t)
            time.sleep(0.03)
    finally:
        del _can_py