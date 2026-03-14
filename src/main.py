from machine import Pin, SoftI2C
import time

from lib.ble import BLE

from modules.servo import Servo


class Device:

    def __init__(self):

        print("device init")

        self.modules = {}

        i2c_servo = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

        # 注册模块
        self.register(Servo(i2c_servo))

        # BLE
        self.ble = BLE(name="BB-ESP32", callback=self.on_ble)

    def register(self, module):
        # 0 保留
        # 1 servo, pca9685

        self.modules[module.ID] = module

    def on_ble(self, data):

        print("recv:", data)

        if len(data) < 2:
            return

        module_id = data[0]
        cmd = data[1]

        payload = data[2:]

        module = self.modules.get(module_id)

        if not module:
            print("unknown module")
            return

        resp = module.handle(cmd, payload)

        if resp:
            self.ble.send(resp)

    def run(self):

        self.ble.advertise()

        while True:
            time.sleep(1)


def main():
    print("main")
    dev = Device()
    dev.run()
    print("main end")

main()
