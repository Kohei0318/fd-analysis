
import pdfplumber

# 抽出対象のPDFファイル名
pdf_path = "sample.pdf"

# 出力ファイル（任意）
output_txt_path = "extracted_text.txt"

# テキスト抽出処理
with pdfplumber.open(pdf_path) as pdf, open(output_txt_path, "w", encoding="utf-8") as out_file:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        out_file.write(f"--- Page {i} ---\n")
        if text:
            out_file.write(text + "\n\n")
        else:
            out_file.write("[このページにはテキストがありません]\n\n")

print(f"抽出完了：{output_txt_path}")
