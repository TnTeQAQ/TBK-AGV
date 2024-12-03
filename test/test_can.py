import can
import time


def main():
    # Initialize the CANalyst-II bus
    try:
        bus = can.interface.Bus(
            interface="canalystii", channel=0, device=0, bitrate=500000
        )
    except can.CanError as e:
        print(f"Failed to initialize CAN bus: {e}")
        return

    # Send a CAN message
    msg = can.Message(
        arbitration_id=0x123,
        data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
        is_extended_id=False,
    )
    try:
        bus.send(msg)
        print(f"Message sent on {bus.channel_info}")
    except can.CanError as e:
        print(f"Failed to send message: {e}")

    # Receive CAN messages
    try:
        while True:
            message = bus.recv(timeout=1.0)  # Timeout after 1 second
            if message:
                print(f"Received message: {message}")
            time.sleep(0.1)  # Delay to prevent buffer overflow
    except KeyboardInterrupt:
        print("Stopping CAN message reception.")
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
