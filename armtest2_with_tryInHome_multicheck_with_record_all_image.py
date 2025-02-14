import cv2
import numpy as np
import time
import traceback
from xarm.wrapper import XArmAPI
import requests
import base64
import os
import shutil

# 設定 ESP32-CAM 的 IP
esp32_ip = 'http://192.168.137.240'

# 定義資料夾路徑
base_folder = 'images'
original_folder = os.path.join(base_folder, 'originals')
output_folder = os.path.join(base_folder, 'tryInHouse')
results_folder = os.path.join(base_folder, 'results')

import json

with open('config.json', 'r') as f:
    config = json.load(f)

photo_position = config["photo_taking_position"]
pre_photo = photo_position + np.array([0, 0, 80, 0, 0, 0])
top_grabbing_glass = config["the_top_of_grabbing_glass"]

# 確保輸出資料夾存在
os.makedirs(output_folder, exist_ok=True)
os.makedirs(results_folder, exist_ok=True)

def clear_buffer():
    """清空ESP32-CAM的緩存影像"""
    try:
        for _ in range(3):
            requests.get(esp32_ip + '/capture', timeout=5)
            time.sleep(0.2)
    except requests.exceptions.RequestException as e:
        print(f"Error clearing buffer: {e}")

# 捕獲圖像函數
def capture_image():
    try:
        response = requests.get(esp32_ip + '/capture', timeout=10)
        if response.status_code == 200 and 'image/jpeg' in response.headers.get('Content-Type', ''):
            print("Image captured successfully!")
            return response.content
        else:
            print(f"HTTP Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error capturing image: {e}")
        return None

# 儲存圖像的函數
def save_image(image_data, suffix="", folder=""):
    timestamp = time.strftime('%Y%m%d%H%M%S')
    directory = os.path.join(output_folder, folder)
    os.makedirs(directory, exist_ok=True)
    filename = f"{folder}{suffix}.jpg"
    filepath = os.path.join(directory, filename)
    cv2.imwrite(filepath, image_data)
    print(f"Image saved as {filepath}")
    return filepath

# 將結果複製到 results 資料夾
def copy_to_results(image_path, folder_name):
    result_filename = f"{folder_name}_result.jpg"
    result_path = os.path.join(results_folder, result_filename)
    shutil.copy(image_path, result_path)
    print(f"Copied result image to {result_path}")

# 自適應影像處理與檢測
def process_and_detect(image, folder, threshold=60, blur_ksize=(5, 5)):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    save_image(gray, "_gray", folder)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    save_image(enhanced, "_enhanced", folder)

    blurred = cv2.GaussianBlur(enhanced, blur_ksize, 0)
    save_image(blurred, "_blurred", folder)

    _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)
    save_image(binary, "_binary", folder)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    save_image(closed, "_closed", folder)

    h, w = closed.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    center_x, center_y = w // 2, h // 2
    radius = int(min(h, w) * 0.4)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    masked_image = cv2.bitwise_and(closed, closed, mask=mask)
    save_image(masked_image, "_masked", folder)

    contours, _ = cv2.findContours(masked_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found.")
        return image, None

    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)
    if area < 1500 or area > 60000:
        print(f"Invalid contour area: {area}")
        return image, None

    rect = cv2.minAreaRect(largest_contour)
    angle = rect[-1]
    if angle < -45:
        angle += 90

    box = cv2.boxPoints(rect)
    box = np.intp(box)
    cv2.drawContours(image, [box], 0, (0, 0, 255), 2)

    print(f"Detected angle: {angle} degrees")
    return image, rect


def robust_process_and_detect(image, folder, iterations=5):
    max_area = 0
    best_rect = None
    best_angle = None
    best_image = None
    all_results = []

    for i in range(iterations):
        # 創建單獨的子文件夾保存每次檢測的結果
        iteration_folder = f"{folder}_iter_{i + 1}"
        os.makedirs(os.path.join(output_folder, iteration_folder), exist_ok=True)

        print(f"Detection iteration: {i + 1}")
        temp_image = image.copy()  # 使用副本避免影響原圖
        processed_image, rect = process_and_detect(temp_image, iteration_folder)

        if rect:
            # 保存每次的處理結果
            result_path = save_image(processed_image, f"_result_iter_{i + 1}", iteration_folder)
            all_results.append(processed_image)  # 收集結果圖像
            _, (width, height), angle = rect
            print(f"Iteration {i + 1}: Detected angle = {angle}, area = {width * height}")
            area = width * height
            if area > max_area:
                max_area = area
                best_rect = rect
                best_angle = angle
                best_image = processed_image

    if best_rect:
        # 保存最終選擇的處理結果到結果文件夾
        result_image_path = save_image(best_image, "_best_result", folder)
        copy_to_results(result_image_path, folder)
        print(f"Selected angle from largest contour: {best_angle}, area: {max_area}")

        # 合成所有結果到一個圖像中
        if all_results:
            combined_image = combine_results(all_results)
            combined_image_path = save_image(combined_image, "_total_result", folder)
            copy_to_results(combined_image_path, folder)
            print("Saved combined total result.")
        return best_rect
    else:
        print("No valid rectangle detected in multiple iterations.")
        return None


def combine_results(images):
    """
    合成所有迭代的結果圖像到一個總圖中。
    :param images: 包含多個迭代結果的圖像列表
    :return: 合成的圖像
    """
    max_width = max(img.shape[1] for img in images)
    total_height = sum(img.shape[0] for img in images)

    # 創建一個空白畫布來放置所有圖像
    combined_image = np.zeros((total_height, max_width, 3), dtype=np.uint8)

    current_y = 0
    for img in images:
        combined_image[current_y:current_y + img.shape[0], :img.shape[1]] = img
        current_y += img.shape[0]

    return combined_image

# 機器人控制類
class RobotMain:
    def __init__(self, robot, angle):
        self.alive = True
        self._arm = robot
        self.angle = angle
        self._tcp_speed = 100
        self._tcp_acc = 2000
        self._robot_init()

    def _robot_init(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)

    def clear_errors(self):
        self._arm.clean_error()
        self._arm.clean_warn()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)

    def move_to_initial_position(self):
        print('move to init position')
        self._arm.set_position(*pre_photo, speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
        time.sleep(1)

    def move_to_photo_position(self):
        try:
            self._arm.set_position(*photo_position,
                                   speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
            print('Moved to photo position.')
        except Exception as e:
            print(f"Photo Position Error: {e}")

    def adjust_to_short_side(self, rect):
        try:
            self._arm.set_position(*top_grabbing_glass,
                                   speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
            print('Moved to photo position.')
        except Exception as e:
            print(f"Photo Position Error: {e}")

        try:
            _, (width, height), angle = rect

            # 確定短邊方向
            if width > height:
                if angle < -45:
                    angle += 90
            else:
                if angle >= 0:
                    angle -= 90

            # 如果旋轉角度為負，則補償 180 度避免超出範圍
            if angle < 0:
                angle += 180

            print(f"Adjusting to short side with angle: {angle}")

            self._arm.set_tool_position(*[0.0, 0.0, 0.0, 0.0, 0.0, angle], speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
        except Exception as e:
            print(f"Adjustment Error: {e}")

    def grab(self):
        try:
            self._arm.set_tool_position(*[0.0, 0.0, 335-310.6, 0.0, 0.0, 0], speed=self._tcp_speed, mvacc=self._tcp_acc,
                                        wait=True)
        except Exception as e:
            print(f"Adjustment Error: {e}")
        return
    # 機器人動作
    def execute_actions(self):
        try:
            self.move_to_photo_position()
            time.sleep(2)
        except Exception as e:
            print(f"Action Execution Error: {e}")


def compute_bounding_box(rects):
    """
    計算多個矩形的外框
    :param rects: 多個矩形的列表，每個矩形是 ((cx, cy), (width, height), angle)
    :return: 外框的四個角點
    """
    all_points = []
    for rect in rects:
        box = cv2.boxPoints(rect)  # 獲取矩形的四個角點
        all_points.extend(box)

    # 尋找外框
    all_points = np.array(all_points)
    x_min, y_min = np.min(all_points[:, 0]), np.min(all_points[:, 1])
    x_max, y_max = np.max(all_points[:, 0]), np.max(all_points[:, 1])

    # 返回外框的四個角點
    return np.array([
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ], dtype=np.intp)



def main():
    arm = XArmAPI('192.168.1.172')
    robot = RobotMain(arm, angle=0)

    robot.clear_errors()
    robot.execute_actions()  # 移動到拍照位置
    clear_buffer()
    # 捕獲圖像
    image_data = capture_image()
    if image_data:
        timestamp = time.strftime('%Y%m%d%H%M%S')
        folder = timestamp

        # 原始圖像保存
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        save_image(image, "_original", folder)

        # 執行多次檢測並選擇最佳結果
        best_rect = robust_process_and_detect(image, folder, iterations=10)
        if best_rect:
            robot._arm.close_lite6_gripper()
            robot.adjust_to_short_side(best_rect)
            robot.grab()
            robot._arm.open_lite6_gripper()
            time.sleep(3)
            robot.move_to_initial_position()
        else:
            print("No valid rectangle detected.")
            robot.move_to_initial_position()

        print("Processing complete.")
    else:
        print("Failed to capture image.")

    arm.disconnect()

if __name__ == "__main__":
    main()


