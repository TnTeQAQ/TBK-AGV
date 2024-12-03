import tbkpy._core as tbkpy
from can_py import _can_py
from WTJY901.chs.JY901S import jy901s
import time
import pickle
import numpy as np
import math 
tbkpy.init("AGV")
class MotorMsg:
    def __init__(self):
        self.motor_msg = {}
        self.imu_msg = {}
        self.avg_msg = {}
    def read_motor_msg(self):
        id, data = _can_py.recv()
        self.motor_msg[id] = {
            'id': id,
            'rpm': data.rpm,
            'pos': data.pid_pos_now,
            "current": data.current,
            "duty": data.duty,
            "input_voltage": data.input_voltage,
        }
        return self.motor_msg
    def read_imu_msg(self):
        self.imu_msg = jy901s.get_data()
        return self.imu_msg
    def read_agv_msg(self):
        self.motor_msg = self.read_motor_msg()
        self.imu_msg = self.read_imu_msg()
        self.avg_msg = {
            "motor": self.motor_msg,
            "imu": self.imu_msg
        }
        return self.avg_msg
    def motor2self(self,vx,vy,w):
        L = 1000
        theta1 = math.pi / 3
        theta2 = math.pi / 6
        V = np.array(
            [
                [math.cos(w), math.sin(w), L],
                [
                    -math.cos(theta1) * math.cos(w)
                    + math.sin(theta1) * math.sin(w),
                    -math.cos(theta1) * math.sin(w)
                    - math.sin(theta1) * math.cos(w),
                    L,
                ],
                [
                    -math.sin(theta2) * math.cos(w)
                    - math.cos(theta2) * math.sin(w),
                    -math.sin(theta2) * math.sin(w)
                    + math.cos(theta2) * math.cos(w),
                    L,
                ],
            ]
        )
        result = V @ np.array([vx, vy, w]).transpose()
        return result

        
def set_rpm(msg):
    data = pickle.loads(msg)
    print(data)
    for id in data:
        rpm = data[id]["rpm"]
        _can_py.send_rpm(id, float(rpm))
        
def set_pos(msg):
    data = pickle.loads(msg)
    for id in data:
        pos = data[id]["pos"]
        _can_py.send_rpm(id, pos)


if __name__ == "__main__":
    puber = tbkpy.Publisher("AGV_MSG","MSG")
    suber_rpm = tbkpy.Subscriber("MOTOR_CONTROL","RPM",set_rpm)
    suber_pos = tbkpy.Subscriber("MOTOR_CONTROL","POS",set_pos)
    motor_msg = MotorMsg()

    try:
        while True:
            agv_msg = motor_msg.read_agv_msg()
            print(agv_msg['motor'])
            agv_msg_dumps = pickle.dumps(agv_msg)
            puber.publish(agv_msg_dumps)
            time.sleep(0.003)
    finally:
        del _can_py
        