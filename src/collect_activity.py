import serial
import time
import csv
import os

PORT = 'COM7'  # 修改
BAUD = 115200
SUBJECT = input("请输入被试编号（A/B/C）: ")
ACTIVITY = input("请输入活动编号（1=静坐,2=站立,3=步行,4=跑步,5=上楼,6=下楼）: ")
DURATION = 60  # 采集60秒

OUTPUT_DIR = 'data/raw'
os.makedirs(OUTPUT_DIR, exist_ok=True)
filename = f"{OUTPUT_DIR}/raw_Sub_{SUBJECT}_{time.strftime('%Y%m%d_%H%M%S')}.csv"

print(f"将采集 {DURATION} 秒，保存到 {filename}")
input("按回车开始采集...")

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp','ax','ay','az','label','subject_id'])
    start = time.time()
    while time.time() - start < DURATION:
        line = ser.readline().decode().strip()
        if line:
            parts = line.split(',')
            if len(parts) >= 3:
                row = [int(time.time()*1000)] + parts[:3] + [ACTIVITY, SUBJECT]
                writer.writerow(row)
                print(f"\r已采集 {int(time.time()-start)} 秒", end='')
ser.close()
print(f"\n采集完成，保存至 {filename}")