"""
命令控制器模块
处理蓝牙接收的命令并执行相应动作
"""

import sys
sys.path.append('/lib')
sys.path.append('/config')

from lib.motor.dc_motor import DCMotor
from lib.servo.servo import Servo
from lib.servo.pca9685 import PCA9685
from config.commands import *
from machine import Pin, I2C
import time

class CommandController:
    """命令控制器类"""
    
    def __init__(self, config):
        """
        初始化命令控制器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 初始化LED
        self.led = Pin(config.get('PIN_LED', 2), Pin.OUT)
        
        # 初始化电机
        self.motor = DCMotor(
            config.get('PIN_MOTOR1_1', 12),
            config.get('PIN_MOTOR1_2', 14),
            config.get('PIN_MOTOR1_EN', 13),
            config.get('MOTOR_FREQ', 1000)
        )
        
        # 初始化PCA9685和舵机
        i2c = I2C(
            0,
            scl=Pin(config.get('PCA9685_I2C_SCL', 22)),
            sda=Pin(config.get('PCA9685_I2C_SDA', 21)),
            freq=100000
        )
        
        self.pca9685 = PCA9685(
            i2c,
            address=config.get('PCA9685_I2C_ADDR', 0x40),
            freq=config.get('SERVO_FREQ', 50)
        )
        
        self.servos = []
        for channel in range(5):  # 5个舵机通道
            self.servos.append(Servo(
                self.pca9685,
                channel,
                config.get('SERVO_MIN_ANGLE', 0),
                config.get('SERVO_MAX_ANGLE', 180),
                config.get('SERVO_MIN_PULSE', 500),
                config.get('SERVO_MAX_PULSE', 2500)
            ))
    
    def process_command(self, data):
        """
        处理接收到的命令
        
        Args:
            data: 接收到的字节数据
            
        Returns:
            响应字节数据
        """
        if not data:
            return bytes([RESP_ERROR])
        
        cmd = data[0]
        params = data[1:] if len(data) > 1 else []
        
        try:
            if cmd == CMD_MOTOR_FORWARD:
                self._motor_forward(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_MOTOR_BACKWARD:
                self._motor_backward(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_MOTOR_STOP:
                self._motor_stop()
                return bytes([RESP_OK])
            
            elif cmd == CMD_MOTOR_ROTATE:
                self._motor_rotate(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_SERVO_ANGLE:
                self._servo_angle(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_SERVO_SCAN:
                self._servo_scan(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_LED_ON:
                self._led_on()
                return bytes([RESP_OK])
            
            elif cmd == CMD_LED_OFF:
                self._led_off()
                return bytes([RESP_OK])
            
            elif cmd == CMD_LED_BLINK:
                self._led_blink(params)
                return bytes([RESP_OK])
            
            elif cmd == CMD_SYSTEM_PING:
                return bytes([RESP_OK])
            
            elif cmd == CMD_SYSTEM_STATUS:
                return bytes([RESP_OK, 0x01])  # 状态码：正常运行
            
            else:
                return bytes([RESP_ERROR])
        
        except Exception as e:
            print(f"命令执行错误: {e}")
            return bytes([RESP_ERROR])
    
    def _motor_forward(self, params):
        """电机前进"""
        speed = params[0] if params else 100
        self.motor.forward(speed)
    
    def _motor_backward(self, params):
        """电机后退"""
        speed = params[0] if params else 100
        self.motor.backward(speed)
    
    def _motor_stop(self):
        """电机停止"""
        self.motor.stop()
    
    def _motor_rotate(self, params):
        """电机旋转指定圈数"""
        circles = params[0] if params else 1
        # 简单实现：前进一段时间模拟旋转
        for _ in range(circles):
            self.motor.forward(100)
            time.sleep(0.5)  # 每圈0.5秒
        self.motor.stop()
    
    def _servo_angle(self, params):
        """舵机转到指定角度"""
        servo_id = params[0] if len(params) > 0 else 0
        angle = params[1] if len(params) > 1 else 90
        
        if 0 <= servo_id < len(self.servos):
            self.servos[servo_id].set_angle(angle)
    
    def _servo_scan(self, params):
        """舵机扫描"""
        servo_id = params[0] if len(params) > 0 else 0
        delay = params[1] if len(params) > 1 else 0.01
        
        if 0 <= servo_id < len(self.servos):
            self.servos[servo_id].sweep(delay)
    
    def _led_on(self):
        """LED开"""
        self.led.value(1)
    
    def _led_off(self):
        """LED关"""
        self.led.value(0)
    
    def _led_blink(self, params):
        """LED闪烁"""
        count = params[0] if params else 3
        for _ in range(count):
            self.led.value(1)
            time.sleep(0.2)
            self.led.value(0)
            time.sleep(0.2)