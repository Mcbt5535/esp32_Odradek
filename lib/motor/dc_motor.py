"""
直流电机控制模块
"""

from machine import Pin, PWM
import time

class DCMotor:
    """直流电机控制类"""
    
    def __init__(self, pin1, pin2, enable_pin, freq=1000):
        """
        初始化直流电机
        
        Args:
            pin1: 方向控制引脚1
            pin2: 方向控制引脚2
            enable_pin: 使能引脚（PWM）
            freq: PWM频率
        """
        self.pin1 = Pin(pin1, Pin.OUT)
        self.pin2 = Pin(pin2, Pin.OUT)
        self.enable = PWM(Pin(enable_pin), freq=freq)
        self.enable.duty(0)
    
    def forward(self, speed=100):
        """前进"""
        self.pin1.value(1)
        self.pin2.value(0)
        self.enable.duty(speed)
    
    def backward(self, speed=100):
        """后退"""
        self.pin1.value(0)
        self.pin2.value(1)
        self.enable.duty(speed)
    
    def stop(self):
        """停止"""
        self.enable.duty(0)
        self.pin1.value(0)
        self.pin2.value(0)
    
    def set_speed(self, speed):
        """设置速度 (0-1023)"""
        self.enable.duty(speed)