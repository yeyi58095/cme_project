import json
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = "config.json"

# 讀取 JSON 設定檔
def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# 儲存 JSON 設定檔
def save_config():
    try:
        for key, entries in input_fields.items():
            if isinstance(config[key], list):  # 如果是數值陣列（機械手臂位置）
                config[key] = [float(entry.get()) for entry in entries]
            else:  # 如果是單一值（例如 espCam_ip）
                config[key] = entries.get()

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

        messagebox.showinfo("成功", "設定已儲存！")
        root.quit()  # 關閉 Tkinter UI
    except Exception as e:
        messagebox.showerror("錯誤", f"儲存失敗: {e}")

# 讀取設定檔
config = load_config()

# 建立 Tkinter UI
root = tk.Tk()
root.title("機械手臂 & ESP32 設定")
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas)

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# 建立輸入欄位
input_fields = {}

for i, (key, value) in enumerate(config.items()):
    tk.Label(scroll_frame, text=key, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=5)

    if isinstance(value, list):  # 如果是座標
        entries = []
        for j, val in enumerate(value):
            entry = tk.Entry(scroll_frame, width=10)
            entry.grid(row=i, column=j+1, padx=2)
            entry.insert(0, str(val))
            entries.append(entry)
        input_fields[key] = entries
    else:  # 如果是單一值（如 espCam_ip）
        entry = tk.Entry(scroll_frame, width=20)
        entry.grid(row=i, column=1, padx=2)
        entry.insert(0, str(value))
        input_fields[key] = entry

# 加入儲存按鈕
save_button = tk.Button(root, text="儲存設定", command=save_config)
save_button.pack(pady=10)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# 啟動 Tkinter UI
root.mainloop()
