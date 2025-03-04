import tkinter as tk
from tkinter import font
from spintest import control_led, close_serial

# LED 名稱對應表
led_names = [
    "PROG",
    "FN",
    "SAVE",
    "VAC",
    "SPIN",
    "Move Down",  # '-' button
    "Move Up",    # '+' button
    " - ",        # additional '-' button next to Move Down
    " + "         # additional '+' button next to Move Up
]

class LEDControlApp:
    def __init__(self, master, actions):
        self.master = master
        self.actions = actions  # 傳入的動作暫存
        master.title("Spin Coater")

        # 設定窗口可調整大小
        master.resizable(True, True)
        master.geometry("600x300")  # 調整窗口大小

        # 設定字體
        self.default_font = font.Font(size=12)
        master.option_add("*Font", self.default_font)

        # LED 控制
        self.label = tk.Label(master, text="Control LEDs:")
        self.label.grid(row=0, column=0, pady=10, padx=10, columnspan=6)

        # LED 1-5 (PROG, FN, SAVE, VAC, SPIN) 由左至右
        for i in range(1, 6):
            button = tk.Button(master, text=led_names[i-1], command=lambda led=i: self.control_led(led))
            button.grid(row=1, column=i-1, padx=10, pady=10)

        # Move Down (-) 和 Move Up (+) 及其旁邊的附加按鈕
        move_down_button = tk.Button(master, text=led_names[5], command=lambda: self.control_led(6))
        move_down_button.grid(row=2, column=4, padx=10, pady=10)  # Move Down

        extra_down_button = tk.Button(master, text=led_names[7], command=lambda: self.control_led(8))
        extra_down_button.grid(row=2, column=5, padx=10, pady=10)  # Extra -

        move_up_button = tk.Button(master, text=led_names[6], command=lambda: self.control_led(7))
        move_up_button.grid(row=1, column=4, padx=10, pady=10)  # Move Up

        extra_up_button = tk.Button(master, text=led_names[8], command=lambda: self.control_led(9))
        extra_up_button.grid(row=1, column=5, padx=10, pady=10)  # Extra +

        # 退出按鈕
        self.quit_button = tk.Button(master, text="Quit", command=self.quit)
        self.quit_button.grid(row=3, column=0, columnspan=6, pady=10)  # 將退出按鈕放在下方，並且占滿整行

    def control_led(self, led_number):
        try:
            # 暫存選擇的動作
            self.actions.append(f"Control LED {led_number}")
            control_led(led_number)  # 控制 LED

        except Exception as e:
            print(f"Error controlling LED {led_number}: {str(e)}")

    def quit(self):
        close_serial()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    actions = []  # 建立空的動作暫存
    app = LEDControlApp(root, actions)  # 傳遞動作暫存
    root.mainloop()
