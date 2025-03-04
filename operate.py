import subprocess
import sys
import time
import tkinter as tk
from tkinter import simpledialog

# 確認當前 Python 解析器
print(sys.executable)

# 定義要執行的程式檔
script0 = "adjust_para_ui.py"
script1 = "start_copy_2.py"
script2 = "pitette1ui.py"
script3 = "spinui.py"
script4 = "pitette2ui.py"
script5 = "armtest2_with_tryInHome_multicheck_with_record_all_image.py"
script6 = "putglass.py"
script7 = "pitette1open.py"  # 開啟 LED 9 的腳本
script8 = "spinopen.py"       # 開啟 LED 5 的腳本
script9 = "pitette2open.py"   # 再次開啟 LED 9 的腳本
script10 = "stop.py"
script11 = "up.py"
script12 = "down.py"
script13 = "move.py"
script14 = "turn.py"  # 加入 turn.py 到腳本列表

# 使用當前 Python 解析器
python_path = sys.executable

def run_script(script):
    """執行單一程式檔並等待完成"""
    subprocess.run([python_path, script])

def run_script_async(script):
    """異步執行單一程式檔"""
    return subprocess.Popen([python_path, script])

def get_wait_time(prompt):
    """使用 tkinter UI 獲取使用者輸入的等待時間"""
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗
    wait_time = simpledialog.askfloat("等待時間", prompt)  # 顯示輸入框
    root.destroy()  # 關閉 tkinter 視窗
    return wait_time

def read_calculated_time1():
    """讀取計算出的時間"""
    try:
        with open("calculated_time1.txt", "r") as f:
            time = float(f.read().strip())
            return time
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading time: {e}")
        return None

def read_calculated_time2():
    """讀取計算出的時間"""
    try:
        with open("calculated_time2.txt", "r") as f:
            time = float(f.read().strip())
            return time
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading time: {e}")
        return None

run_script(script0)

'''
# Step 1: 同時執行 pitette1ui.py 和 turn.py
proc1 = run_script_async(script2)
proc_turn1 = run_script_async(script14)

# 等待這兩個腳本都結束
proc1.wait()
proc_turn1.wait()

# Step 2: 同時執行 pitette2ui.py 和 turn.py
#proc2 = run_script_async(script4)
#proc_turn2 = run_script_async(script14)

# 等待這兩個腳本都結束
#proc2.wait()
#proc_turn2.wait()

# 現在詢問用戶滴下第二種液體和停止 VAC 的時間
drop_second_liquid_time = get_wait_time("Enter the time (in seconds) until the second liquid drops:")
if drop_second_liquid_time is None:
    print("No valid input for second liquid drop time.")
    sys.exit()

stop_vac_time = get_wait_time("Enter the time (in seconds) until stopping VAC:")
if stop_vac_time is None:
    print("No valid input for stop VAC time.")
    sys.exit()

'''
# 執行 start.py
run_script(script1)

'''
# 等待 1 秒
time.sleep(5)

##run_script(script7)


# 在執行 run_script(script7) 之前，讀取計算出的等待時間
wait_time = read_calculated_time1()
if wait_time is not None:
    print(f"Waiting for {wait_time:.2f} sec")
    time.sleep(wait_time )  # Convert minutes to seconds

# 呼叫 pitette1test.py 開啟 LED 9
print("start")
##run_script(script7)
##run_script(script11)
# 等待 1 秒
time.sleep(3)

# 呼叫 spintest.py 開啟 LED 5
print("開啟 LED 5...")
'''
run_script(script8)  ## open spin
print('Be careful')
time.sleep(20)
'''
# 等待滴下第二種液體
print(f"等待 {drop_second_liquid_time} 秒，然後滴下第二種液體...")
time.sleep(drop_second_liquid_time)
print('for safety, wait for a while')
time.sleep(5)

#run_script(script12)  ## down
#time.sleep(4)
# 呼叫 pitette2test.py 開啟 LED 9
print("再次開啟 LED 9...")
#run_script(script9)


# 在執行 run_script(script7) 之前，讀取計算出的等待時間
wait_time = read_calculated_time2()
if wait_time is not None:
    print(f"Waiting for {wait_time:.2f} sec ")
    time.sleep(wait_time )  # Convert minutes to seconds

##run_script(script9)
'''
print('script 11')
run_script(script11)  ## up
'''
# 等待停止 VAC
print(f"等待 {stop_vac_time} 秒以停止 VAC...")
time.sleep(stop_vac_time)
##run_script(script10)  # stop

print('debugging')
#time.sleep(5)
print('Take a photo~~')
'''
# 執行 armtest.py 和 putglass.py
run_script(script13) # move
time.sleep(5)

print("really take a photo")
run_script(script5)  ## armtest

run_script(script6)

print("所有程式執行完畢。")
