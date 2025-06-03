
# fd_plot_single_segment_clean_for_ml.py

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

txt_files = sorted(glob.glob("*.txt"))
if not txt_files:
    print("現在のディレクトリに .txt ファイルが見つかりません。")
    exit(1)

for file_path in txt_files:
    segments = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith("# recorded-num-points:"):
            try:
                n = int(lines[i].strip().split(":")[1])
            except:
                i += 1
                continue

            seg_data = []
            i += 1
            count = 0
            while i < len(lines) and count < n:
                if lines[i].strip() and not lines[i].startswith("#"):
                    try:
                        seg_data.append([float(x) for x in lines[i].split()])
                        count += 1
                    except:
                        pass
                i += 1
            if seg_data:
                segments.append(np.array(seg_data))
        else:
            i += 1

    if len(segments) != 1:
        continue

    x = segments[0][:, 0]
    y = -segments[0][:, 1]

    # 原点合わせ
    abs_force = np.abs(y)
    min_force = np.min(abs_force)
    near_zero_indices = np.where(abs_force <= min_force + 5)[0]
    if len(near_zero_indices) == 0:
        continue
    origin_index = near_zero_indices[np.argmin(x[near_zero_indices])]
    x_origin = x[origin_index]

    # 平行移動と単位換算
    x_shifted = (x - x[0] + x_origin - x[0]) * 1e9  # nm
    y_shifted = y * 1e12  # pN

    # 描画（軸・ラベルなし）
    fig, ax = plt.subplots(figsize=(2, 2), dpi=100)
    ax.plot(x_shifted, y_shifted, lw=2, color="black")

    ax.set_xlim(-20, 150)
    ax.set_ylim(-200, 2000)
    ax.axis("off")  # 軸・目盛・ラベルすべて消去
    plt.tight_layout(pad=0)

    out_name = os.path.splitext(os.path.basename(file_path))[0]
    out_png = f"{out_name}_ml_clean.png"
    plt.savefig(out_png, bbox_inches='tight', pad_inches=0)
    plt.close()
