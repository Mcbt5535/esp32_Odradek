"""
项目配置文件
"""

# 硬件配置
PIN_LED = 2  # 内置LED引脚
PIN_MOTOR1_1 = 12  # 电机1方向引脚1
PIN_MOTOR1_2 = 14  # 电机1方向引脚2
PIN_MOTOR1_EN = 13  # 电机1使能引脚

PIN_SERVO1 = 15  # 舵机1引脚
PIN_SERVO2 = 2  # 舵机2引脚
PIN_SERVO3 = 4  # 舵机3引脚
PIN_SERVO4 = 16  # 舵机4引脚
PIN_SERVO5 = 17  # 舵机5引脚

# WiFi配置
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# 蓝牙配置
BLE_NAME = "ESP32_Device"
BLE_SERVICE_UUID = UUID(0x180F)

# 电机配置
MOTOR_FREQ = 1000  # PWM频率
MOTOR_MAX_SPEED = 1023

# 舵机配置 (PCA9685)
SERVO_FREQ = 50  # PWM频率
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180
SERVO_MIN_PULSE = 500  # 最小脉冲宽度 (微秒)
SERVO_MAX_PULSE = 2500  # 最大脉冲宽度 (微秒)

# PCA9685 I2C配置
PCA9685_I2C_SDA = 4  # I2C SDA引脚
PCA9685_I2C_SCL = 5  # I2C SCL引脚
PCA9685_I2C_ADDR = 0x40  # PCA9685 I2C地址

# 调试配置
DEBUG = True
