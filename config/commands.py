"""
蓝牙命令常量定义
"""

# 命令类型（单字节）
CMD_MOTOR_FORWARD = 0x01    # 电机前进
CMD_MOTOR_BACKWARD = 0x02   # 电机后退
CMD_MOTOR_STOP = 0x03       # 电机停止
CMD_MOTOR_ROTATE = 0x04     # 电机旋转指定圈数

CMD_SERVO_ANGLE = 0x10      # 舵机转到指定角度
CMD_SERVO_SCAN = 0x11       # 舵机扫描

CMD_LED_ON = 0x20           # LED开
CMD_LED_OFF = 0x21          # LED关
CMD_LED_BLINK = 0x22        # LED闪烁

CMD_SYSTEM_PING = 0xF0      # 系统心跳
CMD_SYSTEM_STATUS = 0xF1    # 系统状态

# 响应类型
RESP_OK = 0x00              # 成功
RESP_ERROR = 0xFF           # 错误

# 命令格式：[命令字节] [参数1] [参数2] ...
# 示例：
# 电机旋转2圈: [0x04] [0x02]
# 舵机转到90度: [0x10] [0x5A]
# LED闪烁3次: [0x22] [0x03]