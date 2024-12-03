from can_py import _can_py
import time

while True:
    id, msg = _can_py.recv()
    if id == 31:
        print(id, msg.rpm, msg.current, msg.pid_pos_now)
