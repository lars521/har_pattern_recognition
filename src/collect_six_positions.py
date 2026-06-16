import serial
import time
import csv
import os

# ====== 唯一需要你修改的地方 ======
# 改成你的 ESP32 实际串口号
# Windows 示例: 'COM3', 'COM4', 'COM7' 等
# 在设备管理器 -> 端口 里查看
PORT = 'COM7'   # ← 改成你的
# =================================

BAUD = 115200
OUTPUT_DIR = 'data/raw/six_positions'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def collect_position(name, duration=5):
    input(f"请将传感器摆成【{name}】姿态（静止不动），然后按回车开始采集...")
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"❌ 串口打开失败: {e}")
        print("请检查：")
        print("1. ESP32 是否插好")
        print("2. Thonny 是否已关闭（占用串口）")
        print("3. 端口号是否正确")
        return
    
    time.sleep(2)
    print(f"⏳ 采集 {duration} 秒...")
    data = []
    start = time.time()
    
    while time.time() - start < duration:
        try:
            raw_line = ser.readline()
            line = raw_line.decode('utf-8', errors='ignore').strip()
        except:
            continue
        
        if not line:
            continue
        
        # 只接受纯数字行（三个逗号分隔的数字）
        parts = line.split(',')
        if len(parts) >= 3:
            try:
                # 验证三个都是数字
                float(parts[0])
                float(parts[1])
                float(parts[2])
                data.append([time.time()] + parts[:3])
            except ValueError:
                # 不是纯数字就跳过
                continue
    
    ser.close()
    
    if not data:
        print(f"⚠️ 警告: {name} 没有采集到任何数据！")
        print("   请检查 ESP32 是否在发送数据（打开 Thonny 看一下）")
        return
    
    filename = f"{OUTPUT_DIR}/{name}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"✅ 已保存 {len(data)} 行数据到 {filename}\n")

if __name__ == '__main__':
    print("=" * 50)
    print("MPU6050 六位置标定采集脚本")
    print("请确保：")
    print("1. ESP32 已烧录 main.py 并通电（自动发送数据）")
    print("2. Thonny 已关闭（释放串口）")
    print("3. 端口号设置正确")
    print("=" * 50)
    
    positions = ['px', 'nx', 'py', 'ny', 'pz', 'nz']
    for p in positions:
        collect_position(p)
    
    print("🎉 所有姿态采集完成！")
    print(f"数据保存在: {OUTPUT_DIR}/")