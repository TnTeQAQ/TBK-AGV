import tbkpy._core as tbkpy
import time


def f(msg, i):
    print(time.time(), ": ", msg, " | ", i)


tbkpy.init("AGV2")
sub_motor = {}
motor_list = [1, 2, 3, 4, 5, 6, 7, 8]


for i in motor_list:
    ep_info = tbkpy.EPInfo()
    ep_info.name = "RPM"
    ep_info.msg_name = f"MOTOR_{i}"
    sub_motor[i] = tbkpy.Subscriber(ep_info, lambda msg, can_id=i: f(msg, can_id))
    # sub_motor.append(tbkpy.Subscriber(ep_info,lambda msg, i=i:f(msg,i)))
while True:
    time.sleep(1)
