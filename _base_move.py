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

tbkpy.init("AGV")


def convert_to_IMU(imu_data):
    imu_msg = IMU()

    # 辅助函数：判断值是否为0，如果是0则替换为极小值
    def replace_if_zero(value):
        return value if value != 0 else 1e-7

    # 设置 Orientation (四元数)
    x, y, z, w = imu_data["quat"]
    imu_msg.orientation.x = float(replace_if_zero(x))
    imu_msg.orientation.y = float(replace_if_zero(y))
    imu_msg.orientation.z = float(replace_if_zero(z))
    imu_msg.orientation.w = float(replace_if_zero(w))

    # 设置 Linear Acceleration (线性加速度)
    imu_msg.linear_acceleration.x = float(replace_if_zero(imu_data["acc"][0]))
    imu_msg.linear_acceleration.y = float(replace_if_zero(imu_data["acc"][1]))
    imu_msg.linear_acceleration.z = float(replace_if_zero(imu_data["acc"][2]))

    # 设置 Angular Velocity (角速度)
    imu_msg.angular_velocity.x = float(replace_if_zero(imu_data["gyro"][0]))
    imu_msg.angular_velocity.y = float(replace_if_zero(imu_data["gyro"][1]))
    imu_msg.angular_velocity.z = float(replace_if_zero(imu_data["gyro"][2]))

    # 序列化消息
    imu_msg = imu_msg.SerializeToString()
    return imu_msg


class MotorMsg:
    def __init__(self):
        self.motor_msg = {}
        self.imu_msg = {}
        self.agv_msg = {"motor": self.motor_msg, "imu": self.imu_msg}
        self.motorA = 31
        self.motorB = 32
        self.motorC = 33
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()

    def listen(self):
        while True:
            self.read_agv_msg()

    def read_motor_msg(self):
        recv = _can_py.recv()
        if not recv:
            return
        id, data = recv
        # 电机消息，包含了电机的信息
        self.motor_msg[id] = {
            "id": id,
            "rpm": data.rpm,
            "pos": data.pid_pos_now,
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
        print(self.imu_msg)
        self.agv_msg = {
            "motor": self.motor_msg,
            "imu": self.imu_msg,
        }
        return self.agv_msg


    def motor2self(self, vx, vy, w):
        L = 1000
        theta1 = math.pi / 3
        theta2 = math.pi / 6
        V = np.array(
            [
                [math.cos(w), math.sin(w), L],
                [
                    -math.cos(theta1) * math.cos(w) + math.sin(theta1) * math.sin(w),
                    -math.cos(theta1) * math.sin(w) - math.sin(theta1) * math.cos(w),
                    L,
                ],
                [
                    -math.sin(theta2) * math.cos(w) - math.cos(theta2) * math.sin(w),
                    -math.sin(theta2) * math.sin(w) + math.cos(theta2) * math.cos(w),
                    L,
                ],
            ]
        )
        result = V @ np.array([vx, vy, w]).transpose()

        v_motor = {
            self.motorA: {"rpm": result[0]},
            self.motorB: {"rpm": result[1]},
            self.motorC: {"rpm": result[2]},
        }
        return v_motor


def set_speed(msg):
    data = pickle.loads(msg)
    x, y, w = data

    v_motor = motor_msg.motor2self(x, y, w)
    try:
        for id in v_motor:
            rpm = v_motor[id]["rpm"]
            _can_py.send_rpm(id, float(rpm))
            # time.sleep(0.02)
    except Exception as e:
        print(e)


if __name__ == "__main__":

    all_msg_info = tbkpy.EPInfo()
    all_msg_info.name = "AGV_MSG"
    all_msg_info.msg_name = "ALL_MSG"
    all_msg_info.msg_type = "dict"
    puber = tbkpy.Publisher(all_msg_info)

    # imu_msg_info = tbkpy.EPInfo()
    # imu_msg_info.name = "AGV_MSG"
    # imu_msg_info.msg_name = "IMU_MSG"
    # imu_msg_info.msg_type = "float"
    # puber_imu = tbkpy.Publisher(imu_msg_info)

    imu_msg_info = tbkpy.EPInfo()
    imu_msg_info.name = "AGV_MSG"
    imu_msg_info.msg_name = "IMU_MSG"
    imu_msg_info.msg_type = "IMU"
    puber_imu = tbkpy.Publisher(imu_msg_info)

    motor_msg_info = tbkpy.EPInfo()
    motor_msg_info.name = "AGV_MSG"
    motor_msg_info.msg_name = "MOTOR_MSG"
    motor_msg_info.msg_type = "list"

    puber_motor = tbkpy.Publisher(motor_msg_info)
    suber_rpm = tbkpy.Subscriber("MOTOR_CONTROL", "RPM", set_speed)
    motor_msg = MotorMsg()
    try:
        while True:
            # motor_msg.agv_msg = motor_msg.read_agv_msg()
            agv_msg_dumps = pickle.dumps(motor_msg.agv_msg)
            puber_motor.publish(
                pickle.dumps(
                    [
                        motor_msg.agv_msg["motor"][id]["rpm"]
                        for id in motor_msg.agv_msg["motor"]
                    ]
                )
            )
            if "acc" in motor_msg.agv_msg["imu"]:
                agv_msg_imu = motor_msg.agv_msg["imu"]
                agv_msg_imu = convert_to_IMU(agv_msg_imu)
                # print(agv_msg_imu)
                puber_imu.publish(agv_msg_imu)
            puber.publish(agv_msg_dumps)
            time.sleep(0.03)
    finally:
        del _can_py
