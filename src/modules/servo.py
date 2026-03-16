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
    CMD_WARN = const(5)  # warning

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

            elif cmd == self.CMD_WARN:
                debug_print("mode_warn")
                await self.mode_warn()

            else:
                debug_print("unknown cmd")
                await asyncio.sleep_ms(1000)  # 空闲等待

    # ---------------------
    # 动作模式
    # ---------------------
    def control_servos(self, angle):
        servos = [0, 4, 8, 12]
        for i in servos:
            self.pwm.set_servo_angle(i, angle)

    async def mode_open(self):
        self.control_servos(180)
        await asyncio.sleep_ms(50)

    async def mode_close(self):
        self.control_servos(0)
        await asyncio.sleep_ms(50)

    async def step_move(self, start_angle, end_angle, event, step_delay_ms=100):
        step = 2  # 每次移动2度
        if start_angle < end_angle:
            angles = range(start_angle, end_angle + 1, step)
        else:
            angles = range(start_angle, end_angle - 1, -step)

        len_angles = len(angles)
        delay_per_step = max(40, step_delay_ms // len_angles)  # 每步至少40ms

        for angle in angles:
            self.control_servos(angle)
            if not await self.sleep_ms_intr(delay_per_step, event):
                return False  # 动作被打断
        return True  # 动作完成

    async def mode_work(self, delay_ms=200):
        if delay_ms < 200:
            delay_ms = 200
        elif delay_ms > 2000:
            delay_ms = 2000

        self.control_servos(90)
        if not await self.sleep_ms_intr(delay_ms, self.CMD_WORK):
            return

        self.control_servos(180)
        await self.sleep_ms_intr(delay_ms, self.CMD_WORK)

    async def mode_warn(self, delay_ms=1200):
        # TO DO 增加pid
        if delay_ms < 800:
            delay_ms = 800
        elif delay_ms > 2000:
            delay_ms = 2000

        # 匀速移动
        if not await self.step_move(55, 95, self.CMD_WARN, int(delay_ms / 2)):
            return
        if not await self.step_move(95, 55, self.CMD_WARN, int(delay_ms / 2)):
            return
