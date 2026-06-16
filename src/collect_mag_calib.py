# collect_mag_calib.py
import serial
import time
import csv
import os

# ====== 修改为你的串口号 ======
PORT = 'COM7'   # 改成你的（如 COM3, COM4）
# ==============================

BAUD = 115200
OUTPUT_DIR = 'data/raw'
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = f"{OUTPUT_DIR}/mag_calib_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"

print("=" * 50)
print("磁力计椭球拟合标定 - 数据采集")
print(f"数据将保存到: {OUTPUT_FILE}")
print("")
print("请手持 ESP32+传感器，在空中缓慢画 '8' 字，")
print("并不断旋转各个方向（让传感器朝向所有可能的方向）。")
print("采集约 1000~2000 个点即可，按 Ctrl+C 停止。")
print("=" * 50)
input("按回车开始采集...")

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
print("开始采集... (按 Ctrl+C 停止)")

data = []
try:
    while True:
        line = ser.readline().decode().strip()
        if line:
            parts = line.split(',')
            if len(parts) == 3:
                # 验证是纯数字
                try:
                    float(parts[0])
                    float(parts[1])
                    float(parts[2])
                    data.append([float(p) for p in parts])
                    print(f"\r已采集 {len(data)} 个点", end='')
                except:
                    pass
except KeyboardInterrupt:
    pass

ser.close()
print(f"\n采集结束，共 {len(data)} 个点。")

if len(data) < 100:
    print("⚠️ 警告：采集点数太少（<100），建议重新采集！")
else:
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"✅ 数据已保存到 {OUTPUT_FILE}")