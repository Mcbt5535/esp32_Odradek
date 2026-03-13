import bluetooth
from micropython import const
import time 

_IRQ_CONNECT = const(1)
_IRQ_DISCONNECT = const(2)
_IRQ_WRITE = const(3)


class BLE:

    def __init__(self, name="ESP32", callback=None):

        self.callback = callback

        self.ble = bluetooth.BLE()
        self.ble.active(True)

        self.conn = None

        SERVICE_UUID = bluetooth.UUID(0xFFF0)
        CHAR_UUID = bluetooth.UUID(0xFFF1)

        CHAR = (CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY)

        SERVICE = (SERVICE_UUID, (CHAR,))
        ((self.handle,),) = self.ble.gatts_register_services((SERVICE,))

        self.ble.irq(self._irq)

        self.name = name

    def _irq(self, event, data):

        if event == _IRQ_CONNECT:
            self.conn, _ = data
            print("BLE connected")

        elif event == _IRQ_DISCONNECT:
            self.conn = None
            print("BLE disconnected")
            self.advertise()

        elif event == _IRQ_WRITE:

            conn, handle = data

            if handle == self.handle:

                msg = self.ble.gatts_read(self.handle)

                if self.callback:
                    self.callback(msg)

    def advertise(self):

        name = self.name

        adv = (
            bytearray(b"\x02\x01\x06")
            + bytearray((len(name) + 1, 0x09))
            + name.encode()
        )

        self.ble.gap_advertise(100, adv)

        print("BLE advertising")

    def send(self, data):

        if self.conn:
            self.ble.gatts_notify(self.conn, self.handle, data)


if __name__ == "__main__":

    def on_ble(data):

        print("recv:", data)

        if len(data) < 2:
            return


    ble = BLE(name="BB-ESP32", callback=on_ble)
    ble.advertise()
    print("BLE started")
    while True:
        time.sleep(1)