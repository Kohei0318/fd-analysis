
# fd_plot_filtered_peaks_y3000_fixed_origin.py

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

colors = ["red", "blue"]

y_offset = float(input("Y方向の平行移動量を入力してください: "))

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

    if len(segments) != 2:
        continue

    x1 = segments[0][:, 0]
    y1 = -segments[0][:, 1]
    x2 = segments[1][:, 0]
    y2 = -segments[1][:, 1]

    # 原点の決定（成功スクリプトと同様）
    abs_force = np.abs(y2)
    min_force = np.min(abs_force)
    near_zero_indices = np.where(abs_force <= min_force + 5)[0]
    if len(near_zero_indices) == 0:
        continue
    origin_index = near_zero_indices[np.argmin(x2[near_zero_indices])]
    x_origin = x2[origin_index]

    # 平行移動
    x_shift_1 = x_origin - x1[0]
    x1_shifted = (x1 + x_shift_1) * 1e9
    x2_shifted = x2 * 1e9
    y1_shifted = y1 * 1e12
    y2_shifted = y2 * 1e12

    # 出力条件（2回目のピークチェック）
    peaks2, _ = find_peaks(y2_shifted, height=500)
    peak_check = any(150 <= x2_shifted[p] <= 250 for p in peaks2)
    if not peak_check:
        continue

    # R条件（1回目のピークチェック）
    peaks1, _ = find_peaks(y1_shifted, height=500)
    peak_check_1st = any(50 <= x1_shifted[p] <= 150 and y1_shifted[p] <= 1200 for p in peaks1)

    # 描画
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x1_shifted, y1_shifted, lw=2, color=colors[0])
    ax.plot(x2_shifted, y2_shifted + y_offset, lw=2, color=colors[1])

    ax.set_xlim(-50, 300)
    ax.set_ylim(-100, 3000)
    ax.set_xlabel("Distance (nm)", fontsize=14)
    ax.set_ylabel("Force (pN)", fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plt.tight_layout()

    out_name = os.path.splitext(os.path.basename(file_path))[0]
    if peak_check_1st:
        out_name = "R" + out_name

    out_png = f"{out_name}_aligned.png"
    plt.savefig(out_png)
    plt.close()
