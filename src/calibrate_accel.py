# calibrate_accel_v2.py
# 加速度计六位置标定 - 线性最小二乘版本（更稳健）

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def load_data(filepath):
    """读取CSV文件，返回加速度数据（N行x3列）"""
    df = pd.read_csv(filepath, header=None)
    return df.iloc[:, 1:4].values.astype(float)

def calibrate_accel_linear(data_dir):
    """
    使用线性最小二乘法直接求解 12 参数（M 和 b）
    模型：a_cal = M @ (a_raw - b)
    约束：静止时 ||a_cal|| = 1g（即 16384 ADC）
    """
    positions = ['px', 'nx', 'py', 'ny', 'pz', 'nz']
    means = []
    
    for p in positions:
        fpath = os.path.join(data_dir, p + '.csv')
        data = load_data(fpath)
        mean_val = data.mean(axis=0)
        means.append(mean_val)
        print(f"  {p}: 均值 = {mean_val}")
    
    X = np.array(means)  # shape: (6, 3)
    
    # 目标：找到 M (3x3) 和 b (3,)，使得 ||M @ (x_i - b)||^2 = 1 对所有 i 成立
    # 等价于：找到 A = M，c = b，使得 (x_i - c)^T A^T A (x_i - c) = 1
    # 令 S = A^T A（对称正定矩阵），则 (x_i - c)^T S (x_i - c) = 1
    
    # 为了简化，我们假设 S 是对角矩阵（即忽略非正交误差）
    # 这样每个轴独立标定：scale_x * (x - b_x), scale_y * (y - b_y), scale_z * (z - b_z)
    
    # 从 px 和 nx 估计 X 轴参数
    px_mean = means[0]  # +X朝上
    nx_mean = means[1]  # -X朝上
    # 零偏 = (px + nx) / 2
    b_x = (px_mean[0] + nx_mean[0]) / 2
    # 刻度 = 16384 / ((px - nx) / 2)
    scale_x = 16384 / ((px_mean[0] - nx_mean[0]) / 2)
    
    # 从 py 和 ny 估计 Y 轴参数
    py_mean = means[2]
    ny_mean = means[3]
    b_y = (py_mean[1] + ny_mean[1]) / 2
    scale_y = 16384 / ((py_mean[1] - ny_mean[1]) / 2)
    
    # 从 pz 和 nz 估计 Z 轴参数
    pz_mean = means[4]
    nz_mean = means[5]
    b_z = (pz_mean[2] + nz_mean[2]) / 2
    scale_z = 16384 / ((pz_mean[2] - nz_mean[2]) / 2)
    
    M = np.diag([scale_x, scale_y, scale_z])
    b = np.array([b_x, b_y, b_z])
    
    return M, b

if __name__ == '__main__':
    data_dir = 'data/raw/six_positions'
    
    if not os.path.exists(data_dir):
        print(f"❌ 错误：目录 {data_dir} 不存在！")
        exit(1)
    
    print("📊 读取六个姿态的均值数据...")
    M, b = calibrate_accel_linear(data_dir)
    
    print("\n✅ 加速度计标定结果：")
    print("M =")
    print(M)
    print("b =", b)
    
    # 保存到 calib_params.json
    try:
        with open('calib_params.json', 'r') as f:
            calib = json.load(f)
    except:
        calib = {}
    calib['accelerometer'] = {'M': M.tolist(), 'b': b.tolist()}
    with open('calib_params.json', 'w') as f:
        json.dump(calib, f, indent=2)
    print("✅ 参数已保存到 calib_params.json")
    
    # ====== 绘图验证 ======
    pz_data = load_data(os.path.join(data_dir, 'pz.csv'))
    raw_mag = np.linalg.norm(pz_data, axis=1)
    cal_mag = np.linalg.norm((pz_data - b) @ M.T, axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.hist(raw_mag, bins=50, alpha=0.6, label='标定前（原始）', color='red', edgecolor='black')
    plt.hist(cal_mag, bins=50, alpha=0.6, label='标定后（校正）', color='blue', edgecolor='black')
    plt.axvline(16384, color='black', linestyle='--', linewidth=2, label='理论值 16384 (1g)')
    plt.xlabel('合加速度模长 (ADC)')
    plt.ylabel('频数')
    plt.title('加速度计六位置标定 - 标定前后对比')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs('docs/images', exist_ok=True)
    plt.savefig('docs/images/acc_calibration.png', dpi=150, bbox_inches='tight')
    print("✅ 对比图已保存到 docs/images/acc_calibration.png")
    
    try:
        plt.show()
    except:
        pass