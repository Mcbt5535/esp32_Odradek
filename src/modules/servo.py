from modules.base import Module
from lib.pca9685 import PCA9685
from micropython import const
import uasyncio as asyncio

DEBUG_MODE = False


def debug_print(msg):
    if DEBUG_MODE:
        print(msg)


class Servo(Module):

    ID = const(1)

    CMD_SET_ANGLE = const(1)
    CMD_OPEN = const(2)  # open
    CMD_CLOSE = const(3)  # close
    CMD_WORK = const(4)  # work

    def __init__(self, i2c):
        self.pwm = PCA9685(i2c)
        print("[Servo] Servo init")
        self.current_cmd = None  # 当前指令
        self.current_data = None  # 指令参数
        # 启动后台循环任务
        self.task = asyncio.create_task(self.run_loop())
        print("[Servo] run loop started")

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
            debug_print("[Servo] run_loop")
            cmd = self.current_cmd
            data = self.current_data

            if cmd == self.CMD_SET_ANGLE and data is not None:
                ch = data[0]
                angle = data[1]
                debug_print(f"set_angle ch:{ch}, angle:{angle}")
                self.pwm.set_servo_angle(ch, angle)
                await asyncio.sleep_ms(50)

            elif cmd == self.CMD_OPEN:
                debug_print("mode_open")
                await self.mode_open()

            elif cmd == self.CMD_CLOSE:
                debug_print("mode_close")
                await self.mode_close()

            elif cmd == self.CMD_WORK:
                debug_print("mode_work")
                await self.mode_work()

            else:
                debug_print("unknown cmd")
                await asyncio.sleep_ms(1000)  # 空闲等待

    # ---------------------
    # 动作模式
    # ---------------------

    async def mode_open(self):
        self.pwm.set_servo_angle(0, 180)
        self.pwm.set_servo_angle(15, 180)
        await asyncio.sleep_ms(50)

    async def mode_close(self):
        self.pwm.set_servo_angle(0, 0)
        self.pwm.set_servo_angle(15, 0)
        await asyncio.sleep_ms(50)

    async def mode_work(self, delay_ms=200):
        if delay_ms < 200:
            delay_ms = 200
        elif delay_ms > 2000:
            delay_ms = 2000

        self.pwm.set_servo_angle(0, 90)
        self.pwm.set_servo_angle(15, 90)
        if not await self.sleep_ms_intr(delay_ms, self.CMD_WORK):
            return

        self.pwm.set_servo_angle(0, 180)
        self.pwm.set_servo_angle(15, 180)
        await self.sleep_ms_intr(delay_ms, self.CMD_WORK)
