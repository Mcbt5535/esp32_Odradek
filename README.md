# ESP32 MicroPython 项目

这是一个基于ESP32的MicroPython项目，用于控制各种硬件模块。

## 项目结构

```
esp32_project/
├── src/           # 主程序文件
├── lib/           # 库文件
│   ├── motor/     # 电机控制模块
│   ├── servo/     # 舵机控制模块
│   └── bluetooth/ # 蓝牙通讯模块
├── drivers/       # 硬件驱动
├── config/        # 配置文件
└── README.md
```

## 模块说明

### 机动
- 舵机 (Servo): 1-4路舵机控制、5路舵机控制
- 直流电机 (DC Motor): 电机控制

### 通讯
- 蓝牙 (Bluetooth): 蓝牙通讯功能

## 快速开始

1. 将代码上传到ESP32开发板
2. 确保已安装MicroPython固件
3. 运行主程序

## 依赖

- MicroPython固件 (ESP32)
- 相关硬件模块

## 许可证

MIT License