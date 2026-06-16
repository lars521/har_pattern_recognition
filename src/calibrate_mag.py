# calibrate_mag.py - 磁力计椭球拟合标定
import numpy as np
import pandas as pd
from scipy.linalg import svd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def ellipsoid_fit(X):
    """
    椭球拟合：使用 DLS（直接最小二乘）+ SVD
    X: N x 3，原始磁力计数据
    返回: center (硬铁偏移), transform (软铁变换矩阵)
    """
    x, y, z = X[:, 0], X[:, 1], X[:, 2]
    
    # 构造设计矩阵
    # 一般二次曲面方程：
    # ax^2 + by^2 + cz^2 + 2dxy + 2exz + 2fyz + 2gx + 2hy + 2iz + j = 0
    D = np.column_stack([
        x**2, y**2, z**2,
        2*x*y, 2*x*z, 2*y*z,
        2*x, 2*y, 2*z,
        np.ones_like(x)
    ])
    
    # 使用 SVD 求解 (求最小奇异值对应的右奇异向量)
    U, S, Vt = svd(D, full_matrices=False)
    v = Vt[-1, :]  # 取最后一个右奇异向量（最小奇异值对应的解）
    
    # 提取 A, B, C
    A = np.array([
        [v[0], v[3], v[4]],
        [v[3], v[1], v[5]],
        [v[4], v[5], v[2]]
    ])
    B = np.array([v[6], v[7], v[8]])
    C = v[9]
    
    # 计算中心
    center = -np.linalg.solve(A, B) / 2
    
    # 计算变换矩阵（将椭球变成球）
    eigenvalues, eigenvectors = np.linalg.eigh(A)
    eigenvalues = np.abs(eigenvalues)  # 确保正定
    transform = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
    
    return center, transform

# ====== 主程序 ======
# 查找最新的磁力计数据文件
data_dir = 'data/raw'
files = [f for f in os.listdir(data_dir) if f.startswith('mag_calib_data_') and f.endswith('.csv')]
if not files:
    print("❌ 错误：未找到磁力计数据文件！请先运行 collect_mag_calib.py 采集数据。")
    exit(1)

latest_file = sorted(files)[-1]
filepath = os.path.join(data_dir, latest_file)
print(f"📂 读取数据文件: {latest_file}")

# 读取数据
df = pd.read_csv(filepath, header=None)
X = df.values.astype(float)
print(f"   共 {len(X)} 个点")

if len(X) < 100:
    print("⚠️ 警告：点数少于100，标定结果可能不准确！")

# 执行椭球拟合
center, transform = ellipsoid_fit(X)
print("\n✅ 磁力计标定结果：")
print(f"硬铁偏置 (center): {center}")
print(f"软铁矩阵 (transform):\n{transform}")

# 保存到 calib_params.json
try:
    with open('calib_params.json', 'r') as f:
        calib = json.load(f)
except:
    calib = {}

calib['magnetometer'] = {
    'hard_iron': center.tolist(),
    'soft_iron': transform.tolist()
}
with open('calib_params.json', 'w') as f:
    json.dump(calib, f, indent=2)
print("✅ 参数已追加到 calib_params.json")

# ====== 绘制 3D 对比图 ======
X_cal = (X - center) @ transform.T

fig = plt.figure(figsize=(14, 6))

# 标定前
ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(X[:, 0], X[:, 1], X[:, 2], s=1, c='red', alpha=0.5)
ax1.set_title('标定前 (椭球)')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.axis('equal')

# 标定后
ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(X_cal[:, 0], X_cal[:, 1], X_cal[:, 2], s=1, c='blue', alpha=0.5)
ax2.set_title('标定后 (球)')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.axis('equal')

plt.tight_layout()
os.makedirs('docs/images', exist_ok=True)
plt.savefig('docs/images/mag_calibration.png', dpi=150, bbox_inches='tight')
print("✅ 对比图已保存到 docs/images/mag_calibration.png")

try:
    plt.show()
except:
    pass