"""
蓝牙BLE外设模块
"""

import ubluetooth
from ubluetooth import UUID

class BLEPeripheral:
    """蓝牙BLE外设类"""
    
    # 服务和特征值UUID
    SERVICE_UUID = UUID(0x180F)  # 电池服务作为示例
    COMMAND_CHAR_UUID = UUID(0x2A19)  # 命令特征值
    
    def __init__(self, name="ESP32", callback=None):
        """
        初始化BLE外设
        
        Args:
            name: 设备名称
            callback: 接收到数据时的回调函数 callback(data)
        """
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        
        self._connected = False
        self._callback = callback
        self._rx_handle = None
        
        # 注册IRQ处理
        self.ble.irq(self._irq)
        
        # 创建服务
        self._setup_services()
    
    def _setup_services(self):
        """设置BLE服务和特征值"""
        SERVICES = (
            (
                self.SERVICE_UUID,
                (
                    (self.COMMAND_CHAR_UUID, ubluetooth.FLAG_READ | ubluetooth.FLAG_WRITE),
                ),
            ),
        )
        
        handles = self.ble.gatts_register_services(SERVICES)
        self._rx_handle = handles[0][0]
    
    def _irq(self, event, data):
        """蓝牙中断处理"""
        if event == 1:  # 中央设备连接
            self._connected = True
            conn_handle, addr_type, addr = data
            print(f"设备已连接: {bytes(addr).hex()}")
        
        elif event == 2:  # 中央设备断开
            self._connected = False
            print("设备已断开")
        
        elif event == 3:  # 写入数据
            conn_handle, value_handle = data
            if value_handle == self._rx_handle:
                value = self.ble.gatts_read(self._rx_handle)
                print(f"接收到数据: {value}")
                if self._callback:
                    self._callback(value)
    
    def advertise(self):
        """开始广播"""
        self.ble.gap_advertise(
            interval_ms=100,
            adv_data=b'\x02\x01\x06\x02\x0A\x00' + bytes(self.SERVICE_UUID)
        )
        print("开始广播...")
    
    def stop_advertise(self):
        """停止广播"""
        self.ble.gap_advertise(None)
        print("停止广播")
    
    def is_connected(self):
        """检查是否连接"""
        return self._connected
    
    def send_response(self, data):
        """发送响应数据"""
        if self._connected:
            try:
                self.ble.gatts_write(self._rx_handle, data)
                self.ble.gatts_notify(0, self._rx_handle, data)
            except:
                pass