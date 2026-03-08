"""
ESP32 MicroPython 启动文件
"""

# 导入必要的库
import machine
import time

# 配置CPU频率
machine.freq(240000000)  # 240MHz

# 设置WiFi（可选）
# import network
# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)

print("ESP32 启动完成")
print(f"CPU频率: {machine.freq()} Hz")