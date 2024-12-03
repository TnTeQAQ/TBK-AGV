import tbkpy._core as tbkpy
from WTJY901.chs.JY901S import jy901s
import time
import pickle
from tzcp.ros.sensor_pb2 import IMU

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
        self.avg_msg = {}
        self.motorA = 31
        self.motorB = 32
        self.motorC = 33

    def read_imu_msg(self):
        self.imu_msg = jy901s.get_data()
        return self.imu_msg


if __name__ == "__main__":
    imu_msg_info = tbkpy.EPInfo()
    imu_msg_info.name = "AGV_MSG"
    imu_msg_info.msg_name = "IMU_MSG"
    imu_msg_info.msg_type = "IMU"
    puber = tbkpy.Publisher(imu_msg_info)
    motor_msg = MotorMsg()
    while True:
        imu_msg = motor_msg.read_imu_msg()
        imu_msg = convert_to_IMU(imu_msg)
        # agv_msg_dumps = pickle.dumps(agv_msg)
        # # print(agv_msg)
        puber.publish(imu_msg)
        time.sleep(0.003)
