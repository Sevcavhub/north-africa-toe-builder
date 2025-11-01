#!/usr/bin/env python3
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

RAW_FILE = Path("data/output/fall_of_reich_raw_ocr.json")
DB_PATH = Path("database/master_database.db")
OUTPUT_DIR = Path("data/output")

def get_existing_data():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name, nation FROM bg_reference_vehicles")
    existing_vehicles = {(row[0].lower().strip(), row[1].lower()): row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT name, nation FROM bg_reference_guns")
    existing_guns = {(row[0].lower().strip(), row[1].lower()): row[0] for row in cursor.fetchall()}
    conn.close()
    return existing_vehicles, existing_guns

def clean_vehicle_name(name):
    name = re.sub(r"\s+pts\s+\d+-[rv]\s+BR.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(Restricted\)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(Unique\)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^\d+\s+", "", name)
    name = re.sub(r"\s{2,}", " ", name)
    return name.strip()

def clean_gun_name(name):
    name = re.sub(r"\s+with\s+\d+\s+crew.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+pts\s+\d+-[rv]\s+BR.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(Restricted\)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"Unit Composition:\s*", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^\d+\s+", "", name)
    name = re.sub(r"\s{2,}", " ", name)
    return name.strip()

def is_valid_datacard_vehicle(raw_data):
    name = raw_data["name"].lower()
    context = raw_data.get("context", "").lower()
    if not ("pts" in context and "br" in context):
        return False
    exclude_patterns = ["composition:", "bottom:", "roosevelt", "prime minister", "met for", "feared", "influence"]
    if any(pattern in name for pattern in exclude_patterns):
        return False
    return True

def is_valid_datacard_gun(raw_data):
    name = raw_data["name"].lower()
    context = raw_data.get("context", "").lower()
    if not ("crew" in context or "howitzer" in name or "gun" in context):
        return False
    exclude_patterns = ["captured", "support with", "anti-aircraft guns,"]
    if any(pattern in name for pattern in exclude_patterns):
        return False
    return True

def main():
    print("=" * 80)
    print("FALL OF THE REICH - CLEAN AND STRUCTURE OCR DATA")
    print("=" * 80)
    
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    print(f"Raw extraction: {len(raw_data[''vehicles''])} vehicles, {len(raw_data[''guns''])} guns")
    
    existing_vehicles, existing_guns = get_existing_data()
    print(f"Existing DB: {len(existing_vehicles)} vehicles, {len(existing_guns)} guns")
    
    clean_vehicles = []
    duplicate_vehicles = []
    
    for raw_v in raw_data["vehicles"]:
        if not is_valid_datacard_vehicle(raw_v):
            continue
        clean_name = clean_vehicle_name(raw_v["name"])
        nation = raw_v["nation"]
        key = (clean_name.lower().strip(), nation.lower())
        if key in existing_vehicles:
            duplicate_vehicles.append({"name": clean_name, "nation": nation, "existing_name": existing_vehicles[key]})
            continue
        clean_vehicles.append({
            "name": clean_name, "nation": nation,
            "source_file": "Battlegroup-Fall-of-the-Reich-Full.pdf",
            "extraction_confidence": raw_v.get("confidence", "medium"),
            "page_num": raw_v["page_num"]
        })
    
    clean_guns = []
    duplicate_guns = []
    
    for raw_g in raw_data["guns"]:
        if not is_valid_datacard_gun(raw_g):
            continue
        clean_name = clean_gun_name(raw_g["name"])
        context_lower = raw_g.get("context", "").lower()
        nation = "unknown"
        if "german" in context_lower or "sdkfz" in context_lower:
            nation = "german"
        elif "soviet" in context_lower or "russian" in context_lower:
            nation = "soviet"
        elif "american" in context_lower or "us" in context_lower:
            nation = "american"
        elif "british" in context_lower or "churchill" in context_lower:
            nation = "british"
        
        is_dup = False
        for existing_key in existing_guns.keys():
            if clean_name.lower().strip() in existing_key[0]:
                duplicate_guns.append({"name": clean_name, "nation": nation, "existing_name": existing_guns[existing_key]})
                is_dup = True
                break
        if is_dup:
            continue
        clean_guns.append({
            "name": clean_name, "nation": nation,
            "caliber_mm": raw_g.get("caliber_mm"),
            "source_file": "Battlegroup-Fall-of-the-Reich-Full.pdf",
            "extraction_confidence": raw_g.get("confidence", "medium"),
            "page_num": raw_g["page_num"]
        })
    
    print("
" + "=" * 80)
    print("CLEANING RESULTS")
    print("=" * 80)
    print(f"
Vehicles: {len(clean_vehicles)} valid, {len(duplicate_vehicles)} duplicates")
    print(f"Guns: {len(clean_guns)} valid, {len(duplicate_guns)} duplicates")
    
    print("
NEW VEHICLES (sample):")
    for v in clean_vehicles[:10]:
        print(f"  - {v[''name'']} ({v[''nation'']}) - page {v[''page_num'']}")
    
    print("
NEW GUNS (sample):")
    for g in clean_guns[:10]:
        print(f"  - {g[''name'']} ({g[''nation'']}, {g.get(''caliber_mm'')}mm) - page {g[''page_num'']}")
    
    vehicles_file = OUTPUT_DIR / "battlegroup_fall_of_reich_vehicles.json"
    with open(vehicles_file, "w", encoding="utf-8") as f:
        json.dump(clean_vehicles, f, indent=2, ensure_ascii=False)
    
    guns_file = OUTPUT_DIR / "battlegroup_fall_of_reich_guns.json"
    with open(guns_file, "w", encoding="utf-8") as f:
        json.dump(clean_guns, f, indent=2, ensure_ascii=False)
    
    print(f"
Cleaned data saved to {vehicles_file} and {guns_file}")

if __name__ == "__main__":
    main()
