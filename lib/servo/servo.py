"""
舵机控制模块 (基于PCA9685)
"""

from machine import I2C, Pin
import time
from .pca9685 import PCA9685

class Servo:
    """舵机控制类"""
    
    def __init__(self, pca9685, channel, min_angle=0, max_angle=180, min_pulse=500, max_pulse=2500):
        """
        初始化舵机
        
        Args:
            pca9685: PCA9685驱动器实例
            channel: 通道号 (0-15)
            min_angle: 最小角度
            max_angle: 最大角度
            min_pulse: 最小脉冲宽度 (微秒)
            max_pulse: 最大脉冲宽度 (微秒)
        """
        self.pca9685 = pca9685
        self.channel = channel
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
    
    def angle_to_pulse(self, angle):
        """
        将角度转换为脉冲宽度
        
        Args:
            angle: 角度值
            
        Returns:
            脉冲宽度 (微秒)
        """
        if angle < self.min_angle:
            angle = self.min_angle
        elif angle > self.max_angle:
            angle = self.max_angle
        
        # 线性映射：角度 -> 脉冲宽度
        pulse = self.min_pulse + (angle - self.min_angle) * \
                (self.max_pulse - self.min_pulse) / (self.max_angle - self.min_angle)
        return int(pulse)
    
    def set_angle(self, angle):
        """
        设置舵机角度
        
        Args:
            angle: 角度值 (0-180)
        """
        pulse = self.angle_to_pulse(angle)
        self.pca9685.set_servo_pulse(self.channel, pulse)
    
    def set_pulse(self, pulse):
        """
        直接设置舵机脉冲宽度
        
        Args:
            pulse: 脉冲宽度 (微秒)
        """
        self.pca9685.set_servo_pulse(self.channel, pulse)
    
    def sweep(self, delay=0.01):
        """
        舵机扫描
        
        Args:
            delay: 每步延迟时间 (秒)
        """
        for angle in range(self.min_angle, self.max_angle + 1):
            self.set_angle(angle)
            time.sleep(delay)
        for angle in range(self.max_angle, self.min_angle - 1, -1):
            self.set_angle(angle)
            time.sleep(delay)
    
    def center(self):
        """将舵机置于中心位置"""
        center_angle = (self.min_angle + self.max_angle) // 2
        self.set_angle(center_angle)
