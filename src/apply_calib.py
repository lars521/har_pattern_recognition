import json
import numpy as np
import pandas as pd
import os

with open('calib_params.json', 'r') as f:
    cal = json.load(f)

M = np.array(cal['accelerometer']['M'])
b = np.array(cal['accelerometer']['b'])

input_dir = 'data/raw'
output_dir = 'data/calibrated'
os.makedirs(output_dir, exist_ok=True)

for fname in os.listdir(input_dir):
    if fname.endswith('.csv') and not fname.startswith('cal'):
        df = pd.read_csv(os.path.join(input_dir, fname))
        # 应用标定
        acc_raw = df[['ax','ay','az']].values.astype(float)
        acc_cal = (acc_raw - b) @ M.T
        df_cal = df.copy()
        df_cal[['ax','ay','az']] = acc_cal
        out_name = fname.replace('raw', 'cal')
        df_cal.to_csv(os.path.join(output_dir, out_name), index=False)
        print(f"已生成 {out_name}")
