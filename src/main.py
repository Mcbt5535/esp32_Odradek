"""
ESP32 MicroPython 蓝牙控制主程序
通过蓝牙接收命令并控制硬件设备
"""

import sys
sys.path.append('/lib')
sys.path.append('/config')
sys.path.append('/src')

from lib.bluetooth.ble_peripheral import BLEPeripheral
from src.command_controller import CommandController
import config.config as config
import time

class ESP32BLEController:
    """ESP32蓝牙控制器"""
    
    def __init__(self):
        """初始化控制器"""
        print("初始化ESP32蓝牙控制器...")
        
        # 提取配置
        config_dict = {
            'PIN_LED': config.PIN_LED,
            'PIN_MOTOR1_1': config.PIN_MOTOR1_1,
            'PIN_MOTOR1_2': config.PIN_MOTOR1_2,
            'PIN_MOTOR1_EN': config.PIN_MOTOR1_EN,
            'MOTOR_FREQ': config.MOTOR_FREQ,
            'SERVO_FREQ': config.SERVO_FREQ,
            'SERVO_MIN_ANGLE': config.SERVO_MIN_ANGLE,
            'SERVO_MAX_ANGLE': config.SERVO_MAX_ANGLE,
            'SERVO_MIN_PULSE': config.SERVO_MIN_PULSE,
            'SERVO_MAX_PULSE': config.SERVO_MAX_PULSE,
            'PCA9685_I2C_SCL': config.PCA9685_I2C_SCL,
            'PCA9685_I2C_SDA': config.PCA9685_I2C_SDA,
            'PCA9685_I2C_ADDR': config.PCA9685_I2C_ADDR
        }
        
        # 初始化命令控制器
        self.controller = CommandController(config_dict)
        
        # 初始化蓝牙
        self.ble = BLEPeripheral(
            name=config.BLE_NAME,
            callback=self._on_ble_data_received
        )
        
        print("控制器初始化完成")
    
    def _on_ble_data_received(self, data):
        """蓝牙数据接收回调"""
        print(f"接收到命令: {data.hex()}")
        response = self.controller.process_command(data)
        print(f"发送响应: {response.hex()}")
        self.ble.send_response(response)
    
    def run(self):
        """运行控制器"""
        print("开始蓝牙广播...")
        self.ble.advertise()
        
        print("系统运行中，等待蓝牙连接...")
        while True:
            time.sleep(1)
            
            # 定期检查连接状态
            if not self.ble.is_connected():
                print("等待设备连接...")

def main():
    """主函数"""
    try:
        controller = ESP32BLEController()
        controller.run()
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"程序错误: {e}")

if __name__ == "__main__":
    main()