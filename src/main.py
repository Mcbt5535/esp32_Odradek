from machine import Pin, SoftI2C
import time

from lib.ble import BLE

from modules.servo import Servo
from modules.motor import Motor
import uasyncio as asyncio


def parse_hex_string(hex_str):
    """
    将空格分隔的十六进制字符串转换为数字列表

    参数:
        hex_str: 字符串，如 "00 01 02 aa"

    返回:
        数字列表，如 [0, 1, 2, 170]
    """
    # 按空格分割字符串
    parts = hex_str.split()

    # 将每个部分转换为整数（自动识别十六进制）
    result = []
    for part in parts:
        try:
            # 使用int()转换，base=0表示自动识别进制（0x前缀会按十六进制处理）
            result.append(int(part, 16))
        except ValueError:
            # 如果转换失败，则返回原始字符串
            print(f"Input error: {part}")
            result = [-1]
    return result


class Device:

    def __init__(self):

        print("device init")

        self.modules = {}

        i2c_servo = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

        # 注册模块
        self.register(Servo(i2c_servo))
        print(f"servo init, now modules:{self.modules}")
        self.register(Motor())
        print(f"motor init, now modules:{self.modules}")

        # BLE
        self.ble = BLE(name="BB-ESP32", callback=self.on_ble)

    def register(self, module):
        # 0 保留
        # 1 servo, pca9685

        self.modules[module.ID] = module

    def on_ble(self, data):

        print("recv:", data)
        data = parse_hex_string(data)
        if data == [-1]:
            return

        print(f"data:{data},type:{type(data)},len:{len(data)}")
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

    async def run(self):

        self.ble.advertise()

        while True:
            await asyncio.sleep(1)


async def main():
    print("main")
    dev = Device()
    await dev.run()
    print("main end")


asyncio.run(main())
