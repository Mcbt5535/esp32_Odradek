"""
PCA9685 PWM驱动模块
"""

from machine import I2C, Pin
import time

class PCA9685:
    """PCA9685 PWM驱动器类"""
    
    # PCA9685寄存器地址
    __MODE1 = 0x00
    __MODE2 = 0x01
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD
    
    def __init__(self, i2c, address=0x40, freq=50):
        """
        初始化PCA9685
        
        Args:
            i2c: I2C对象
            address: I2C地址 (默认0x40)
            freq: PWM频率 (默认50Hz用于舵机)
        """
        self.i2c = i2c
        self.address = address
        self.freq = freq
        
        # 重置设备
        self.reset()
        
        # 设置PWM频率
        self.set_pwm_freq(freq)
    
    def reset(self):
        """重置PCA9685"""
        self.i2c.writeto_mem(self.address, self.__MODE1, bytes([0x80]))
        time.sleep(0.01)
    
    def set_pwm_freq(self, freq):
        """
        设置PWM频率
        
        Args:
            freq: PWM频率 (Hz)
        """
        # 限制频率范围
        if freq < 24:
            freq = 24
        elif freq > 1526:
            freq = 1526
        
        # 计算预分频值
        prescale = int(25000000 / (4096 * freq) - 1)
        
        # 设置预分频
        oldmode = self.i2c.readfrom_mem(self.address, self.__MODE1, 1)[0]
        newmode = (oldmode & 0x7F) | 0x10  # 休眠模式
        self.i2c.writeto_mem(self.address, self.__MODE1, bytes([newmode]))
        self.i2c.writeto_mem(self.address, self.__PRESCALE, bytes([prescale]))
        self.i2c.writeto_mem(self.address, self.__MODE1, bytes([oldmode]))
        time.sleep(0.005)
        self.i2c.writeto_mem(self.address, self.__MODE1, bytes([oldmode | 0x80]))
    
    def set_pwm(self, channel, on, off):
        """
        设置指定通道的PWM值
        
        Args:
            channel: 通道号 (0-15)
            on: 开启时间 (0-4095)
            off: 关闭时间 (0-4095)
        """
        if channel < 0 or channel > 15:
            return
        
        base = self.__LED0_ON_L + 4 * channel
        
        self.i2c.writeto_mem(self.address, base, bytes([on & 0xFF]))
        self.i2c.writeto_mem(self.address, base + 1, bytes([(on >> 8) & 0xFF]))
        self.i2c.writeto_mem(self.address, base + 2, bytes([off & 0xFF]))
        self.i2c.writeto_mem(self.address, base + 3, bytes([(off >> 8) & 0xFF]))
    
    def set_duty(self, channel, duty):
        """
        设置指定通道的占空比
        
        Args:
            channel: 通道号 (0-15)
            duty: 占空比 (0-4095)
        """
        self.set_pwm(channel, 0, duty)
    
    def set_servo_pulse(self, channel, pulse):
        """
        设置舵机脉冲宽度
        
        Args:
            channel: 通道号 (0-15)
            pulse: 脉冲宽度 (微秒)
        """
        # 脉冲宽度转换为PWM值
        # 周期 = 1/freq (秒)
        # PWM值 = (pulse / 1000000) / (1/freq) * 4095
        pwm = int((pulse / 1000000) * self.freq * 4095)
        self.set_pwm(channel, 0, pwm)