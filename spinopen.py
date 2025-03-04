import serial
import time

# 設置串行端口和波特率
ser = serial.Serial('COM6', 115200)  # Windows 上的 COM 埠，Linux/Mac 上通常是 /dev/ttyUSB0 或 /dev/ttyS0

# LED名稱對應表


def control_led():
    # 自動開啟LED 5
    led_number = 5
    command_on = f"{led_number} on\n"
    ser.write(command_on.encode())
    time.sleep(0.5)  # 等待 0.5 秒
    
    # 自動關閉LED
    command_off = f"{led_number} off\n"
    ser.write(command_off.encode())
    time.sleep(1)  # 等待 ESP32 處理命令
    response = ser.readline().decode().strip()
    print(response)

def close_serial():
    ser.close()

# 測試函數
if __name__ == "__main__":
    control_led()
    close_serial()

