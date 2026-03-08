# ESP32 MicroPython 蓝牙控制使用指南

## 项目功能
通过蓝牙接收手机或遥控器发送的命令，控制以下硬件：
- 直流电机（前进、后退、停止、旋转指定圈数）
- 舵机（旋转到指定角度、扫描）
- LED（开、关、闪烁）

## 上传到ESP32

### 方法1: 使用Thonny IDE
1. 安装Thonny IDE
2. 连接ESP32到电脑
3. 在Thonny中打开 `src/main.py`
4. 点击"运行"或"上传到设备"

### 方法2: 使用ampy
```bash
pip install adafruit-ampy
ampy --port COM3 put src/main.py /main.py
ampy --port COM3 put src/boot.py /boot.py
ampy --port COM3 put src/command_controller.py /command_controller.py
ampy --port COM3 put lib/bluetooth/ble_peripheral.py /lib/ble_peripheral.py
ampy --port COM3 put lib/motor/dc_motor.py /lib/dc_motor.py
ampy --port COM3 put lib/servo/servo.py /lib/servo.py
ampy --port COM3 put lib/servo/pca9685.py /lib/pca9685.py
ampy --port COM3 put config/config.py /config.py
ampy --port COM3 put config/commands.py /commands.py
```

### 方法3: 使用rshell
```bash
pip install rshell
rshell -p COM3
> cp src/main.py /main.py
> cp src/boot.py /boot.py
> cp src/command_controller.py /
> cp lib/bluetooth/ble_peripheral.py /lib/
> cp lib/motor/dc_motor.py /lib/
> cp lib/servo/servo.py /lib/
> cp lib/servo/pca9685.py /lib/
> cp config/config.py /
> cp config/commands.py /
```

## 蓝牙命令格式

### 命令结构
`[命令字节] [参数1] [参数2] ...`

### 可用命令

#### 电机控制
- `0x01` [速度] - 电机前进，速度范围0-255
- `0x02` [速度] - 电机后退，速度范围0-255
- `0x03` - 电机停止
- `0x04` [圈数] - 电机旋转指定圈数（1-255）

**示例：**
- 电机前进，速度100: `01 64`
- 电机旋转2圈: `04 02`

#### 舵机控制
- `0x10` [舵机ID] [角度] - 舵机转到指定角度
  - 舵机ID: 0-4（对应5个舵机）
  - 角度: 0-180
- `0x11` [舵机ID] [延迟] - 舵机扫描
  - 延迟: 0-255（扫描速度，值越小越快）

**示例：**
- 舵机0转到90度: `10 00 5A`
- 舵机1扫描: `11 01 0A`

#### LED控制
- `0x20` - LED开
- `0x21` - LED关
- `0x22` [次数] - LED闪烁指定次数（1-255）

**示例：**
- LED闪烁3次: `22 03`

#### 系统命令
- `0xF0` - 心跳检测
- `0xF1` - 获取系统状态

## 使用蓝牙APP控制

### 推荐APP
1. **nRF Connect** (iOS/Android) - Nordic官方APP
2. **LightBlue** (iOS/Android)
3. **BLE Scanner** (Android)

### 连接步骤
1. 打开ESP32，等待蓝牙广播
2. 手机打开蓝牙APP，扫描设备
3. 找到设备名称（默认：ESP32_Device）
4. 连接设备
5. 找到特征值UUID: `0x2A19`
6. 写入命令数据

### 使用nRF Connect示例
1. 扫描并连接ESP32_Device
2. 展开服务列表
3. 找到Battery Service (0x180F)
4. 找到特征值Battery Level (0x2A19)
5. 点击写入按钮
6. 输入十六进制数据，例如：`04 02`（电机旋转2圈）
7. 点击发送

## 硬件连接

### 电机连接
- 电机方向引脚1: GPIO 12
- 电机方向引脚2: GPIO 14
- 电机使能引脚: GPIO 13

### 舵机连接 (PCA9685)
PCA9685通过I2C接口连接到ESP32，最多支持16个舵机：

**PCA9685与ESP32的连接：**
- PCA9685 VCC: 5V（舵机供电）
- PCA9685 GND: GND
- PCA9685 SDA: GPIO 21（默认）
- PCA9685 SCL: GPIO 22（默认）
- PCA9685 VCC: 3.3V（逻辑电平）

**舵机连接到PCA9685：**
- 舵机0: PCA9685 PWM0
- 舵机1: PCA9685 PWM1
- 舵机2: PCA9685 PWM2
- 舵机3: PCA9685 PWM3
- 舵机4: PCA9685 PWM4
- 舵机5-15: PCA9685 PWM5-15（可扩展）

**注意事项：**
1. PCA9685需要5V供电用于驱动舵机
2. ESP32和PCA9685需要共地
3. I2C地址默认为0x40，可通过硬件跳线修改
4. PCA9685支持最多16个舵机或PWM设备

### LED连接
- 内置LED: GPIO 2

## 自定义配置

修改 `config/config.py` 文件来自定义硬件引脚和参数：

```python
# 修改引脚
PIN_LED = 2           # LED引脚
PIN_MOTOR1_1 = 12     # 电机引脚
PIN_SERVO1 = 15       # 舵机引脚

# 修改设备名称
BLE_NAME = "我的ESP32"

# 修改电机/舵机参数
MOTOR_MAX_SPEED = 1023
SERVO_MAX_ANGLE = 180
```

## 故障排除

### 蓝牙无法连接
1. 检查ESP32是否正常启动
2. 确认设备名称正确
3. 重启ESP32
4. 检查蓝牙权限

### 电机不转
1. 检查电源供应是否充足
2. 检查引脚连接是否正确
3. 确认电机驱动模块是否正常

### 舵机不动作
1. 检查舵机供电（通常需要5V）
2. 确认舵机信号线连接正确
3. 检查引脚配置

### 命令无响应
1. 检查命令格式是否正确
2. 查看ESP32串口输出错误信息
3. 确认特征值UUID正确

## 开发建议

1. 先测试单个模块功能
2. 使用串口监视器查看调试信息
3. 逐步添加更多功能
4. 记录每次修改便于调试