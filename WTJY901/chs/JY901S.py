# coding:UTF-8
import WTJY901.chs.lib.device_model as deviceModel
from WTJY901.chs.lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from WTJY901.chs.lib.protocol_resolver.roles.wit_protocol_resolver import WitProtocolResolver
import pylinalg as la
from math import pi
class JY901S:
    def __init__(self,uart_port):
        self.device = deviceModel.DeviceModel(
        "JY901",
        WitProtocolResolver(),
        JY901SDataProcessor(),
        "51_0"
        )
        self.device.serialConfig.portName = uart_port
        self.device.serialConfig.baud = 115200
        self.device.openDevice()
        self.JY901_DATA = {}
    def get_data(self):
        self.JY901_DATA["acc"] = [self.device.getDeviceData("accX"),self.device.getDeviceData("accY"),self.device.getDeviceData("accZ")]
        self.JY901_DATA["gyro"] = [self.device.getDeviceData("gyroX"),self.device.getDeviceData("gyroY"),self.device.getDeviceData("gyroZ")]
        self.JY901_DATA["angle"] = [self.device.getDeviceData("angleX"),self.device.getDeviceData("angleY"),self.device.getDeviceData("angleZ")]

        self.JY901_DATA["angle"] = [x if x is not None else 0 for x in self.JY901_DATA["angle"]]
        
        self.JY901_DATA["angle"] = [i/180*pi for i in self.JY901_DATA["angle"]]
        self.JY901_DATA["angle"][1] = -self.JY901_DATA["angle"][1]
        self.JY901_DATA["quat"] = la.quat_from_euler(self.JY901_DATA["angle"],order="YXZ").tolist()
        return self.JY901_DATA
    
jy901s = JY901S("/dev/ttyS0")

# if __name__ == '__main__':
#     while True:
#         j.get_data()
#         # time.sleep(0.1)