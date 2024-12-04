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
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def listen(self):
        while True:
            self.get_all_data()

    def pack_msg(self, data, msg_type="unknown", serialize_type="pickle"):
        serialize_func = pickle.dumps
        if serialize_type == "pickle":
            serialize_func = pickle.dumps
        elif serialize_type == "json":
            serialize_func = json.dumps
        else:
            pass
        return {
            "msg_type": msg_type,
            "serialize_type": serialize_type,
            "data": serialize_func(data),
        }

    @property
    def can_data(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        self._can_data[id] = self.pack_msg(
            data={"id": id, "data": data},
            msg_type="can",
            serialize_type="pickle"
        )
        return self._can_data

    @property
    def imu_data(self):
        self._imu_data = self.pack_msg(
            data=jy901s.get_data(),
            msg_type="imu",
            serialize_type="pickle"
        )
        return self._imu_data

    def get_all_data(self):
        self.data = self.pack_msg(
            data={"can_data": self._can_data, "imu_data": self._imu_data},
            msg_type="all",
            serialize_type="pickle"
        )
        return self.data


if __name__ == '__main__':
    ctr = Controller()
    try:
        while True:
            print(ctr.get_all_data())
            time.sleep(0.03)
    finally:
        del _can_py