from modules.base import Module
from micropython import const
from machine import Pin
import uasyncio as asyncio

DEBUG_MODE = False
# motor: 9.5V


def debug_print(msg):
    if DEBUG_MODE:
        print(msg)


class Motor(Module):

    ID = const(2)

    CMD_IDLE = const(0)
    CMD_STOP = const(1)
    CMD_CW = const(2)  # 顺时针
    CMD_CCW = const(3)  # 逆时针
    CMD_HELLO = const(4)  # 摇摆

    def __init__(self):
        print("[Motor] Motor init")
        self.in1 = Pin(8, Pin.OUT)
        self.in2 = Pin(9, Pin.OUT)
        self.current_cmd = None  # 当前指令
        self.current_data = None  # 指令参数
        # 启动后台循环任务
        self.task = asyncio.create_task(self.run_loop())
        print("[Motor] run loop started")

    def handle(self, cmd, data=None):
        """接收蓝牙指令，更新当前动作和参数"""
        self.current_cmd = cmd
        self.current_data = data

    async def sleep_ms_intr(self, total_ms, check_cmd):
        """
        可中断延时函数，每50ms检查一次指令是否被打断
        total_ms: 延时毫秒数
        check_cmd: 当前动作命令常量
        """
        step = 50
        for _ in range(total_ms // step):
            if self.current_cmd != check_cmd:
                return False  # 动作被打断
            await asyncio.sleep_ms(step)
        return True  # 延时完成

    async def run_loop(self):
        """后台循环任务，持续执行当前动作"""
        while True:
            debug_print("[Motor] run_loop")
            cmd = self.current_cmd
            data = self.current_data

            if cmd == self.CMD_STOP:
                self.in1.value(1)
                self.in2.value(1)
                debug_print(f"[Motor] STOP")
                await asyncio.sleep_ms(50)

            elif cmd == self.CMD_CW:
                self.in1.value(1)
                self.in2.value(0)
                debug_print("[Motor] CW")
                await asyncio.sleep_ms(50)

            elif cmd == self.CMD_CCW:
                self.in1.value(0)
                self.in2.value(1)
                debug_print("[Motor] CCW")
                await asyncio.sleep_ms(50)

            else:
                self.in1.value(0)
                self.in2.value(0)
                debug_print("[Motor] IDLE")
                await asyncio.sleep_ms(50)  # 空闲等待
