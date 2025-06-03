
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

def parse_jpkdp_txt(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    data_lines = []
    for line in lines:
        if line.startswith("#") or line.strip() == "":
            continue
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                x = float(parts[0])
                y = float(parts[1])
                data_lines.append((x, y))
            except ValueError:
                continue

    if not data_lines:
        return None, None

    x_raw = np.array([d[0] for d in data_lines])
    y_raw = np.array([d[1] for d in data_lines])

    x_nm = x_raw * 1e9  # m → nm
    y_pn = -y_raw * 1e12  # N → pN（符号反転）

    return x_nm, y_pn

def generate_fdcurve_image(x, y, out_path, x_range=(-20, 150), y_range=(-200, 2000),
                           img_size=(224, 224), line_width=2, smooth_sigma=1):
    if len(x) == 0 or len(y) == 0:
        return

    # 原点合わせ
    x = x - x[0]
    y = gaussian_filter1d(y, sigma=smooth_sigma)

    plt.figure(figsize=(img_size[0] / 100, img_size[1] / 100), dpi=100)
    plt.plot(x, y, color='black', linewidth=line_width)
    plt.xlim(x_range)
    plt.ylim(y_range)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

if __name__ == "__main__":
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]
    if not txt_files:
        print("カレントディレクトリに .txt ファイルが見つかりません。")
    else:
        print(f"{len(txt_files)} 件の .txt ファイルを処理します。")
        for txt_file in txt_files:
            try:
                x, y = parse_jpkdp_txt(txt_file)
                if x is None or y is None:
                    print(f"⚠ {txt_file} は有効なデータを含みません。スキップします。")
                    continue
                out_file = os.path.splitext(txt_file)[0] + "_ml_sigma1.png"
                generate_fdcurve_image(x, y, out_file)
                print(f"✅ {out_file} を出力しました")
            except Exception as e:
                print(f"❌ {txt_file} の処理に失敗しました: {e}")
