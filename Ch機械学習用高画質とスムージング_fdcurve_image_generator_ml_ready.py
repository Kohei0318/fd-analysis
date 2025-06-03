
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def generate_fdcurve_image(x, y, out_path, x_range=(-20,150), y_range=(-200,2000),
                           img_size=(224, 224), line_width=2, smooth_window=11):
    """
    x: 距離 [nm]
    y: 力 [pN]
    out_path: 出力PNGファイルパス
    x_range: x軸描画範囲 (nm)
    y_range: y軸描画範囲 (pN)
    img_size: 出力画像サイズ (ピクセル)
    line_width: 線の太さ
    smooth_window: Savitzky-Golay平滑化のウィンドウ幅（奇数）
    """

    # 平滑化
    if len(y) >= smooth_window:
        y = savgol_filter(y, window_length=smooth_window, polyorder=2)

    # 描画
    plt.figure(figsize=(img_size[0]/100, img_size[1]/100), dpi=100)
    plt.plot(x, y, color='black', linewidth=line_width)
    plt.xlim(x_range)
    plt.ylim(y_range)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

# 使用例（スクリプト直実行用）
if __name__ == "__main__":
    import pandas as pd
    # 例: FDカーブのtxtから読み込む
    df = pd.read_csv("example_fdcurve.txt", delimiter='\t', header=None)
    x = df[0].values  # nm
    y = df[1].values  # pN
    generate_fdcurve_image(x, y, "example_output.png")
