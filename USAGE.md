# BLE 写入指令（简版）

## 指令格式

所有 BLE 写入数据采用固定字节结构：

```
Byte0   Module ID
Byte1   Command ID
Byte2   Parameter1
Byte3   Parameter2
```

---

## Servo 控制

**Module ID**

```
0x01
```

### 设置舵机角度

```
01 01 CH ANGLE
```

参数说明：

| 参数    | 说明            |
| ----- | ------------- |
| CH    | 舵机通道 (0–15)   |
| ANGLE | 舵机角度 (0–180°) |

---

## Example

设置 **0 号舵机为 90°**

发送 HEX：

```
01 01 00 5A
```

含义：

```
Servo[0] → 90°
```
