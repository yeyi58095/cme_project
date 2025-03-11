import serial
import time

# 設置串行端口和波特率
ser = serial.Serial('COM6', 115200)  # Windows 上的 COM 埠，Linux/Mac 上通常是 /dev/ttyUSB0 或 /dev/ttyS0

# LED名稱對應表
led_names_1_to_5 = [
    "PROG",
    "FN",
    "SAVE",
    "VAC",
    "SPIN"
]

led_names_6_to_9 = [
    "Move Down",
    "Move Up",
    "-",
    "+"
]

def control_led(led_number):
    if led_number < 1 or led_number > 9:
        raise ValueError("LED number must be between 1 and 9")

    # 自動開啟LED
    command_on = f"{led_number} on\n"
    ser.write(command_on.encode())
    time.sleep(0.5)  # 等待 0.5 秒
    if(led_number == 9):
        print('it is up')
    # 自動關閉LED
    command_off = f"{led_number} off\n"
    ser.write(command_off.encode())
    time.sleep(0.5)  # 等待 ESP32 處理命令
    response = ser.readline().decode().strip()
    print(response)

def close_serial():
    ser.close()


