
# fd_plot_multi_segment_with_csv_graphmode.py

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import shutil
import pandas as pd
from scipy.signal import find_peaks

colors = ["red", "blue", "green", "orange", "magenta", "cyan", "purple", "brown", "pink", "gray", "black"]
y_offset = float(input("Y方向の平行移動量を入力してください: "))

txt_files = sorted(glob.glob("*.txt"))
if not txt_files:
    print("現在のディレクトリに .txt ファイルが見つかりません。")
    exit(1)

tmpdir = tempfile.mkdtemp()

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

    if not (2 <= len(segments) <= 11):
        continue

    last_seg = segments[-1]
    y_last = -last_seg[:, 1]
    x_last = last_seg[:, 0]
    abs_force = np.abs(y_last)
    min_force = np.min(abs_force)
    near_zero_indices = np.where(abs_force <= min_force + 5)[0]
    if len(near_zero_indices) == 0:
        continue
    origin_index = near_zero_indices[np.argmin(x_last[near_zero_indices])]
    x_origin = x_last[origin_index]

    aligned_segments = []
    for idx, seg in enumerate(segments):
        x = seg[:, 0]
        y = -seg[:, 1]
        if idx == len(segments) - 1:
            x_shifted = x * 1e9
        else:
            x_shift = x_origin - x[0]
            x_shifted = (x + x_shift) * 1e9
        y_shifted = y * 1e12 + idx * y_offset
        aligned_segments.append((x_shifted, y_shifted))

    x_peak, y_peak = aligned_segments[-1]
    peaks, _ = find_peaks(y_peak, height=500)
    found_valid_peak = any(150 <= x_peak[p] <= 250 for p in peaks)
    if not found_valid_peak:
        continue

    r_flag = False
    x_check, y_check = aligned_segments[0]
    r_peaks, _ = find_peaks(y_check, height=500)
    for rp in r_peaks:
        if 50 <= x_check[rp] <= 150 and y_check[rp] <= 1200:
            r_flag = True
            break

    fig, ax = plt.subplots(dpi=300)
    out_base = os.path.splitext(os.path.basename(file_path))[0]
    for idx, (x_seg, y_seg) in enumerate(aligned_segments):
        ax.plot(x_seg, y_seg, lw=2, color=colors[idx % len(colors)])
        if found_valid_peak:
            df = pd.DataFrame({"x (nm)": x_seg, "y (pN)": y_seg})
            df.to_csv(f"{out_base}_seg{idx+1}_raw.csv", index=False)

    ax.set_xlim(-50, 300)
    ax.set_ylim(-100, 3000 + (len(segments) - 2) * y_offset)
    ax.set_xlabel("Distance (nm)", fontsize=14)
    ax.set_ylabel("Force (pN)", fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plt.tight_layout()

    out_png = f"{'R' if r_flag else ''}{out_base}_aligned.png"
    plt.savefig(out_png)
    plt.close()

shutil.rmtree(tmpdir)
