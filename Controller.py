import tbkpy._core as tbkpy
from can_py import _can_py
from WTJY901.chs.JY901S import jy901s
import time
import pickle
import numpy as np
import math
import threading
from tzcp.ros.sensor_pb2 import IMU
from tzcp.ros.geometry_pb2 import Vector3
from google.protobuf.json_format import MessageToDict

class Controller:
    def __init__(self) -> None:
        self.can_data = {}
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def listen(self):
        while True:
            self.get_all_data()

    def get_can_data(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        # 通过can传回的数据
        self.can_data[id] = pickle.dumps(data)

    def get_imu_data(self):
        self.imu_data = jy901s.get_data()
        return self.imu_data

    def get_all_data(self):
        self.imu_data = self.get_imu_data()
        self.agv_msg = {
            "can": self.motor_msg,
            "imu": self.imu_data,
        }
        return self.agv_msg
