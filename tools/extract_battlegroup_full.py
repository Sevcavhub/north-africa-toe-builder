#!/usr/bin/env python3
"""Extract all text from PDF for manual analysis"""
import fitz
from pathlib import Path

pdf_path = Path(r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Battlegroup-DataCards-French-Polish-Romanian-Hungarian.pdf")
doc = fitz.open(pdf_path)

output = []
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    output.append(f"\n{'='*100}\nPAGE {page_num + 1}\n{'='*100}\n{text}")

doc.close()

full_text = '\n'.join(output)
output_file = Path("D:/north-africa-toe-builder/data/output/battlegroup_pdf_full_text.txt")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"Saved full text to: {output_file}")
print(f"Total pages: {len(doc)}")
print(f"Total length: {len(full_text)} characters")
