#!/usr/bin/env python3
import fitz
import pytesseract
from PIL import Image
import json
import re
import sqlite3
from pathlib import Path
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

PDF_PATH = Path("D:/north-africa-toe-builder/Resource Documents/Battlegroup Game/Battlegroup-Fall-of-the-Reich-Full.pdf")
DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder/data/output")

def get_existing_data():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = {(row[0].lower().strip(), row[1].lower()): True for row in cursor.fetchall()}
    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = {(row[0].lower().strip(), row[1].lower()): True for row in cursor.fetchall()}
    conn.close()
    return existing_vehicles, existing_guns

def extract_text_from_page_ocr(page, dpi=300):
    try:
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return ""

def find_equipment_sections(pdf_doc, sample_interval=10):
    print(f"PDF has {len(pdf_doc)} pages")
    print(f"Sampling every {sample_interval}th page...")
    equipment_pages = []
    keywords = ["datacard", "vehicle", "tank", "gun", "artillery", "army list", "equipment", 
                "reference", "stats", "armor", "weapon", "penetration", "tiger", "panther",
                "is-2", "su-", "pershing", "comet"]
    sample_pages = list(range(0, len(pdf_doc), sample_interval))
    for idx, page_num in enumerate(sample_pages):
        print(f"  Sampling page {page_num} ({idx+1}/{len(sample_pages)})...", end=" ")
        page = pdf_doc[page_num]
        text = extract_text_from_page_ocr(page, dpi=200)
        text_lower = text.lower()
        keyword_count = sum(1 for kw in keywords if kw in text_lower)
        if keyword_count >= 2:
            equipment_pages.append({"page_num": page_num, "keyword_count": keyword_count})
            print(f"FOUND ({keyword_count} keywords)")
        else:
            print(".")
    return equipment_pages

def extract_structured_data(text, page_num):
    vehicles = []
    guns = []
    lines = text.split("\n")
    vehicle_patterns = {
        "king tiger": "german", "tiger i": "german", "panther": "german", "jagdpanther": "german",
        "hetzer": "german", "panzer iv": "german", "stug": "german", "nashorn": "german",
        "is-2": "soviet", "is-3": "soviet", "t-34/85": "soviet", "su-100": "soviet",
        "isu-152": "soviet", "su-76": "soviet", "m26 pershing": "american", "m4 sherman": "american",
        "m36 jackson": "american", "m18 hellcat": "american", "comet": "british", "churchill": "british",
        "firefly": "british", "cromwell": "british"
    }
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if len(line_clean) < 5:
            continue
        for pattern, nation in vehicle_patterns.items():
            if pattern in line_clean.lower():
                context = "\n".join(lines[max(0, i-2):min(len(lines), i+5)])
                vehicles.append({"name": line_clean, "nation": nation, "page_num": page_num, 
                               "confidence": "medium", "context": context})
                break
        caliber_match = re.search(r"(\d{2,3})\s*mm", line_clean)
        if caliber_match:
            context = "\n".join(lines[max(0, i-2):min(len(lines), i+5)])
            guns.append({"name": line_clean, "caliber_mm": int(caliber_match.group(1)), 
                        "page_num": page_num, "confidence": "medium", "context": context})
    return vehicles, guns

def main():
    print("=" * 80)
    print("BATTLEGROUP FALL OF THE REICH - OCR EXTRACTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    existing_vehicles, existing_guns = get_existing_data()
    print(f"Existing vehicles: {len(existing_vehicles)}")
    print(f"Existing guns: {len(existing_guns)}")
    
    pdf_doc = fitz.open(str(PDF_PATH))
    equipment_sections = find_equipment_sections(pdf_doc, sample_interval=10)
    print(f"\nFound {len(equipment_sections)} pages with equipment keywords")
    
    if not equipment_sections:
        print("Trying finer sampling...")
        equipment_sections = find_equipment_sections(pdf_doc, sample_interval=5)
    
    all_vehicles = []
    all_guns = []
    processed_pages = set()
    
    print("\nProcessing equipment sections with high-quality OCR...")
    for section in equipment_sections[:15]:
        page_num = section["page_num"]
        if page_num in processed_pages:
            continue
        processed_pages.add(page_num)
        print(f"\nProcessing page {page_num} (keywords: {section['keyword_count']})...")
        
        for offset in [-1, 0, 1]:
            current_page = page_num + offset
            if current_page < 0 or current_page >= len(pdf_doc):
                continue
            if current_page in processed_pages and offset != 0:
                continue
            processed_pages.add(current_page)
            
            page = pdf_doc[current_page]
            text = extract_text_from_page_ocr(page, dpi=400)
            vehicles, guns = extract_structured_data(text, current_page)
            all_vehicles.extend(vehicles)
            all_guns.extend(guns)
            if vehicles or guns:
                print(f"  Page {current_page}: {len(vehicles)} vehicles, {len(guns)} guns")
    
    total_pages = len(pdf_doc)
    pdf_doc.close()
    
    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Total pages: {total_pages}")
    print(f"Pages processed: {len(processed_pages)}")
    print(f"Raw vehicles: {len(all_vehicles)}")
    print(f"Raw guns: {len(all_guns)}")
    
    raw_output = {
        "metadata": {
            "source_file": "Battlegroup-Fall-of-the-Reich-Full.pdf",
            "extraction_date": datetime.now().isoformat(),
            "total_pages": total_pages,
            "pages_processed": sorted(list(processed_pages)),
            "extraction_method": "OCR (pytesseract + PyMuPDF)",
            "dpi": 400,
            "existing_vehicles_in_db": len(existing_vehicles),
            "existing_guns_in_db": len(existing_guns)
        },
        "vehicles": all_vehicles,
        "guns": all_guns
    }
    
    raw_file = OUTPUT_DIR / "fall_of_reich_raw_ocr.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nRaw extraction saved to: {raw_file}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
