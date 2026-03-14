import bluetooth
from micropython import const
import time

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)


class BLE:

    def __init__(self, name="ESP32", callback=None):

        self.name = name
        self.callback = callback
        self.conn_handle = None

        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        # UUID
        SERVICE_UUID = bluetooth.UUID(0xFFF0)
        CHAR_UUID = bluetooth.UUID(0xFFF1)

        # Characteristic
        CHAR = (
            CHAR_UUID,
            bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY,
        )

        SERVICE = (
            SERVICE_UUID,
            (CHAR,),
        )

        ((self.handle,),) = self.ble.gatts_register_services((SERVICE,))

        self.ble.irq(self._irq)

    # BLE interrupt
    def _irq(self, event, data):

        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.conn_handle = conn_handle
            print("BLE connected")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.conn_handle = None
            print("BLE disconnected")
            self.advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, attr_handle = data

            if attr_handle == self.handle:
                msg = self.ble.gatts_read(self.handle)

                if self.callback:
                    self.callback(msg)

    # start advertising
    def advertise(self):

        name = self.name.encode()

        adv_data = b"\x02\x01\x06" + bytes((len(name) + 1, 0x09)) + name

        self.ble.gap_advertise(100, adv_data)

        print("BLE advertising:", self.name)

    # send notify
    def send(self, data):

        if self.conn_handle is not None:
            self.ble.gatts_notify(
                self.conn_handle,
                self.handle,
                data,
            )


# test
if __name__ == "__main__":

    def on_ble(data):
        print("recv:", data)

        if len(data) < 1:
            return

    ble = BLE(name="BB-ESP32", callback=on_ble)

    ble.advertise()

    print("BLE started")

    while True:
        time.sleep(1)
