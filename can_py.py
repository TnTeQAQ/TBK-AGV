import can
import numpy as np
import os
from ctypes import *
import time

VCI_USBCAN2 = 4
STATUS_OK = 1


class VESC_CAN_STATUS:
    VESC_ID_A = 20
    VESC_ID_B = 25
    VESC_CAN_PACKET_STATUS_1 = 0x09
    VESC_CAN_PACKET_STATUS_2 = 0x0E
    VESC_CAN_PACKET_STATUS_3 = 0x0F
    VESC_CAN_PACKET_STATUS_4 = 0x10
    VESC_CAN_PACKET_STATUS_5 = 0x1B


class VESC_PACK(Structure):
    _fields_ = [
        ("id", c_int),
        ("rpm", c_int),
        ("current", c_float),
        ("pid_pos_now", c_float),
        ("amp_hours", c_float),
        ("amp_hours_charged", c_float),
        ("watt_hours", c_float),
        ("watt_hours_charged", c_float),
        ("temp_fet", c_float),
        ("temp_motor", c_float),
        ("tot_current_in", c_float),
        ("duty", c_float),
        ("tachometer_value", c_float),
        ("input_voltage", c_float),
    ]


class VCI_INIT_CONFIG(Structure):
    _fields_ = [
        ("AccCode", c_uint),
        ("AccMask", c_uint),
        ("Reserved", c_uint),
        ("Filter", c_ubyte),
        ("Timing0", c_ubyte),
        ("Timing1", c_ubyte),
        ("Mode", c_ubyte),
    ]


class VCI_CAN_OBJ(Structure):
    _fields_ = [
        ("ID", c_uint),
        ("TimeStamp", c_uint),
        ("TimeFlag", c_ubyte),
        ("SendType", c_ubyte),
        ("RemoteFlag", c_ubyte),
        ("ExternFlag", c_ubyte),
        ("DataLen", c_ubyte),
        ("Data", c_ubyte * 8),
        ("Reserved", c_ubyte * 3),
    ]


def buffer_get_int16(buffer, index):
    value = buffer[index] << 8 | buffer[index + 1]
    return value


def buffer_get_int32(buffer, index):
    value = (
        buffer[index] << 24
        | buffer[index + 1] << 16
        | buffer[index + 2] << 8
        | buffer[index + 3]
    )
    return value


def buffer_get_float16(buffer, scale, index):
    value = buffer_get_int16(buffer, index)
    return float(value) / scale


def buffer_get_float32(buffer, scale, index):
    value = buffer_get_int32(buffer, index)
    return float(value) / scale


class CAN_PY:
    # init default: socketcan(mcp2515)
    def __init__(self, _interface="canalystii", _channel=(0), _bitrate=500000):
        # def __init__(self, _interface='socketcan', _channel='can0', _bitrate=500000):

        self.os_can_open()
        self.bus = can.ThreadSafeBus(
            interface=_interface,
            channel=_channel,
            bitrate=_bitrate,
            receive_own_messages=False,
        )
        self.can_packet = VESC_PACK()

    def __del__(self):
        self.bus.shutdown()

    def os_can_open(self):
        pass
        # os.system("sudo ip link set can0 down")
        # os.system("sudo ip link set can0 type can bitrate 500000")
        # os.system("sudo ip link set can0 up")

    def test(self):
        pass

    def send(self, id, data):

        message = can.Message(arbitration_id=id, is_extended_id=True, data=data)

        self.bus.send(message, timeout=0.2)

    def send_can_msg(self, msg):
        self.bus.send(msg)

    def send_pos(self, _id: np.uint8, _pos: float, usb_channel=0, can_channel=0):
        id = _id + 0x400
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        pos_int = np.uint32(int(_pos * 1e6))
        data[0] = (pos_int >> 24) & 0xFF
        data[1] = (pos_int >> 16) & 0xFF
        data[2] = (pos_int >> 8) & 0xFF
        data[3] = pos_int & 0xFF
        print("SEND vesc id: {}, pos: {}, data: {}".format(id & 0xFF, pos_int, data))
        self.send(id, data)

    def send_rpm(self, _id: np.uint8, _rpm: float):
        # Ensure id is handled with a larger integer type to avoid overflow
        id = int(_id) + 0x300

        # Initialize data array
        data = [0, 0, 0, 0, 0, 0, 0, 0]

        # Convert RPM to a 32-bit integer
        rpm_int = np.int32(int(_rpm))

        # Pack the RPM into the data array
        data[0] = (rpm_int >> 24) & 0xFF
        data[1] = (rpm_int >> 16) & 0xFF
        data[2] = (rpm_int >> 8) & 0xFF
        data[3] = rpm_int & 0xFF

        # Send the id and data
        # print(id, data)
        self.send(id, data)

    def send_current(self, _id: np.uint8, _cur: float, usb_channel=0, can_channel=0):
        id = _id + 0x100
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        cur_int = np.uint32(int(_cur * 1000))
        data[0] = (cur_int >> 24) & 0xFF
        data[1] = (cur_int >> 16) & 0xFF
        data[2] = (cur_int >> 8) & 0xFF
        data[3] = cur_int & 0xFF
        print("SEND vesc id: {}, cur: {}, data: {}".format(id & 0xFF, cur_int, data))
        self.send(id, data)
        return id, data

    def send_pass_through(self, _id: np.uint8, _pos: float, _vel: float, _cur: float):
        id = _id + 0x3F00
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        pos_int = np.uint16(int(_pos * 100))
        vel_int = np.uint16(int(_vel))
        cur_int = np.uint16(int(_cur * 1000))
        data[0] = (pos_int >> 8) & 0xFF
        data[1] = pos_int & 0xFF
        data[2] = (vel_int >> 8) & 0xFF
        data[3] = vel_int & 0xFF
        data[4] = (cur_int >> 8) & 0xFF
        data[5] = cur_int & 0xFF
        # print("SEND vesc id: {}, pos: {}, data: {}".format(id & 0xff, pos_int, data))
        self.send(id, data)
        return id, data

    def recv(self, is_decode=True):
        msg = self.bus.recv(1)
        if msg is None:
            return None, None
        _, packet = self.msg_decode(msg.data, msg.arbitration_id)
        return packet.id, packet

    def msg_decode(self, data, id=None):
        if id is None:
            return None, None
        self.can_packet.id = id & 0xFF
        # uint8_t can_packet_status_id = (msg->identifier >> 8) & 0xff;
        # int32_t send_index = 0;
        status_id = (id >> 8) & 0xFF
        if status_id == VESC_CAN_STATUS.VESC_CAN_PACKET_STATUS_1:
            self.can_packet.rpm = int(buffer_get_float32(data, 1, 0))
            self.can_packet.current = buffer_get_float16(data, 1e2, 4)
            self.can_packet.pid_pos_now = buffer_get_float16(data, 50.0, 6)
        if status_id == VESC_CAN_STATUS.VESC_CAN_PACKET_STATUS_2:
            self.can_packet.amp_hours = buffer_get_float32(data, 1e4, 0)
            self.can_packet.amp_hours_charged = buffer_get_float32(data, 1e4, 4)
        if status_id == VESC_CAN_STATUS.VESC_CAN_PACKET_STATUS_3:
            self.can_packet.watt_hours = buffer_get_float32(data, 1e4, 0)
            self.can_packet.watt_hours_charged = buffer_get_float32(data, 1e4, 4)
        if status_id == VESC_CAN_STATUS.VESC_CAN_PACKET_STATUS_4:
            self.can_packet.temp_fet = buffer_get_float16(data, 1e1, 0)
            self.can_packet.temp_motor = buffer_get_float16(data, 1e1, 2)
            self.can_packet.tot_current_in = buffer_get_float16(data, 1e1, 4)
            self.can_packet.duty = buffer_get_float16(data, 1e3, 6)
        if status_id == VESC_CAN_STATUS.VESC_CAN_PACKET_STATUS_5:
            self.can_packet.tachometer_value = buffer_get_float32(data, 1, 0)
            self.can_packet.input_voltage = buffer_get_float16(data, 1e1, 4)
        return id, self.can_packet


_can_py = CAN_PY()
