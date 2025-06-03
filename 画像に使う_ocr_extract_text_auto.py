
import os
import pytesseract
from pdf2image import convert_from_path

# Tesseractの実行ファイルパス（必要に応じて環境に合わせて変更）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# カレントディレクトリ内の .pdf ファイルを自動検出（最初の1つ）
pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
if not pdf_files:
    print("PDFファイルが見つかりません。")
    exit()

pdf_path = pdf_files[0]
output_txt_path = f"ocr_extracted_text_from_{os.path.splitext(pdf_path)[0]}.txt"

# PDFを画像に変換（300dpi）
images = convert_from_path(pdf_path, dpi=300)

# 各ページにOCR処理を適用
with open(output_txt_path, "w", encoding="utf-8") as f:
    for i, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image, lang="jpn")
        f.write(f"--- Page {i} ({pdf_path}) ---\n{text}\n\n")

print(f"OCR完了：{output_txt_path}")
