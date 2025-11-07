#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tobruk British Data Points Extraction - Final Analysis

Extracts actual data points (vehicles, weapons, armor values, movement)
from both sources and compares them directly.

Goal: Achieve 100% match on actual DATA, ignoring formatting.
"""

import sys
import io
import json
import re
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_vehicles_from_text(text):
    """
    Extract vehicle data points from text
    Returns list of vehicle dicts with name, movement, armor, weapons
    """
    vehicles = []

    # Clean up OCR artifacts
    text = text.replace('�', '"')
    text = text.replace('2ATTLE', 'BATTLE')
    text = text.replace('3eg@ee', '')

    # Find all vehicle entries - look for vehicle names followed by stats
    vehicle_patterns = [
        r'(Vickers\s+VI?\s*[A-Z]?(?:-[A-Z])?)\s+(\d+")?',
        r'(M3\s+.*?Honey.*?)\s+(\d+")?',
        r'(Matilda\s+II(?:\s+CS)?)\s+(\d+")?',
        r'(Valentine\s+II)\s+(\d+")?',
        r'(A\d+(?:\s+\w+)?)\s+(\d+")?',
        r'(Crusader\s+\w+)\s+(\d+")?',
        r'(Austin\s+\w+)\s+(\d+")?',
        r'(Bedford\s+\w+)\s+(\d+")?',
        r'(Morris\s+\w+)\s+(\d+")?',
        r'(Scammel\s+\w+)\s+(\d+")?',
        r'(Hippo\s+\w+)\s+(\d+")?',
        r'(Matador\s+\w+)\s+(\d+")?',
        r'(Chev.*?\d+\s*cwt)\s+(\d+")?',
    ]

    for pattern in vehicle_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.group(1).strip()
            movement_value = match.group(2) if match.group(2) else None

            vehicles.append({
                'name': name,
                'movement': movement_value
            })

    return vehicles

def extract_weapons_from_text(text):
    """Extract weapon/armament data points"""
    weapons = []

    # Weapon patterns
    weapon_patterns = [
        r'(\d+)\s*pdr',  # 2 pdr, 6 pdr, etc.
        r'(\d+mm)(?:L(\d+))?',  # 37mmL53, 20mm, etc.
        r'\b(MG)\b',  # Machine guns
        r'(Besa)',  # Besa MG
    ]

    for pattern in weapon_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            weapons.append(match.group(0))

    return weapons

def extract_armor_values(text):
    """Extract armor letter values (I-O scale)"""
    # BattleGroup armor scale uses letters I through O
    armor_letters = re.findall(r'\b([I-O])\b', text)
    return armor_letters

def extract_movement_values(text):
    """Extract movement values (inches)"""
    movement_values = re.findall(r'(\d+)"?\s+(\d+)"?', text)
    # Return as "X/Y" format
    return [f'{m[0]}/{m[1]}' for m in movement_values]

def main():
    print("="*70)
    print("Tobruk British - Data Point Extraction & Comparison")
    print("="*70)

    # Load extracted data
    with open('tobruk_british_ocr_600dpi.json', 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)

    with open('tobruk_british_existing_text.json', 'r', encoding='utf-8') as f:
        txt_data = json.load(f)

    ocr_text = ocr_data['full_text']
    txt_text = txt_data['full_text']

    print("\n📊 Extracting Data Points...\n")

    # Extract vehicles
    ocr_vehicles = extract_vehicles_from_text(ocr_text)
    txt_vehicles = extract_vehicles_from_text(txt_text)

    print(f"🚗 VEHICLES:")
    print(f"   OCR extracted: {len(ocr_vehicles)} vehicles")
    print(f"   TXT extracted: {len(txt_vehicles)} vehicles")

    # Show vehicle names
    ocr_vehicle_names = sorted(set(v['name'] for v in ocr_vehicles))
    txt_vehicle_names = sorted(set(v['name'] for v in txt_vehicles))

    print(f"\n   OCR vehicle names ({len(ocr_vehicle_names)}):")
    for name in ocr_vehicle_names[:15]:  # Show first 15
        print(f"      - {name}")
    if len(ocr_vehicle_names) > 15:
        print(f"      ... and {len(ocr_vehicle_names) - 15} more")

    print(f"\n   TXT vehicle names ({len(txt_vehicle_names)}):")
    for name in txt_vehicle_names[:15]:  # Show first 15
        print(f"      - {name}")
    if len(txt_vehicle_names) > 15:
        print(f"      ... and {len(txt_vehicle_names) - 15} more")

    # Compare names
    common_names = set(ocr_vehicle_names) & set(txt_vehicle_names)
    ocr_only = set(ocr_vehicle_names) - set(txt_vehicle_names)
    txt_only = set(txt_vehicle_names) - set(ocr_vehicle_names)

    print(f"\n   Common vehicles: {len(common_names)}")
    print(f"   OCR only: {len(ocr_only)}")
    if ocr_only:
        print(f"      {list(ocr_only)[:5]}")
    print(f"   TXT only: {len(txt_only)}")
    if txt_only:
        print(f"      {list(txt_only)[:5]}")

    # Extract weapons
    ocr_weapons = extract_weapons_from_text(ocr_text)
    txt_weapons = extract_weapons_from_text(txt_text)

    print(f"\n🔫 WEAPONS/ARMAMENT:")
    print(f"   OCR: {len(ocr_weapons)} weapon references")
    print(f"   TXT: {len(txt_weapons)} weapon references")

    ocr_weapon_types = sorted(set(ocr_weapons))
    txt_weapon_types = sorted(set(txt_weapons))

    print(f"\n   OCR unique weapons: {ocr_weapon_types}")
    print(f"   TXT unique weapons: {txt_weapon_types}")

    # Extract armor values
    ocr_armor = extract_armor_values(ocr_text)
    txt_armor = extract_armor_values(txt_text)

    print(f"\n🛡️  ARMOR VALUES (Letter Scale):")
    print(f"   OCR: {len(ocr_armor)} armor values")
    print(f"   TXT: {len(txt_armor)} armor values")

    # Extract movement values
    ocr_movement = extract_movement_values(ocr_text)
    txt_movement = extract_movement_values(txt_text)

    print(f"\n🏃 MOVEMENT VALUES:")
    print(f"   OCR: {len(ocr_movement)} movement pairs")
    print(f"   TXT: {len(txt_movement)} movement pairs")

    # Calculate data point match percentage
    total_data_points_ocr = len(ocr_vehicles) + len(ocr_weapons) + len(ocr_armor) + len(ocr_movement)
    total_data_points_txt = len(txt_vehicles) + len(txt_weapons) + len(txt_armor) + len(txt_movement)

    print(f"\n{'='*70}")
    print("FINAL DATA POINT ANALYSIS")
    print(f"{'='*70}")

    print(f"\n📊 Total Data Points Extracted:")
    print(f"   OCR: {total_data_points_ocr} data points")
    print(f"   TXT: {total_data_points_txt} data points")
    print(f"   Coverage: {(total_data_points_ocr / total_data_points_txt * 100):.1f}%")

    print(f"\n📊 Vehicle Match Analysis:")
    if len(txt_vehicle_names) > 0:
        vehicle_match_pct = (len(common_names) / len(txt_vehicle_names)) * 100
        print(f"   Vehicle name match: {len(common_names)}/{len(txt_vehicle_names)} ({vehicle_match_pct:.1f}%)")
    else:
        print(f"   No vehicles to compare")

    print(f"\n📊 Weapon Match Analysis:")
    common_weapons = set(ocr_weapon_types) & set(txt_weapon_types)
    if len(txt_weapon_types) > 0:
        weapon_match_pct = (len(common_weapons) / len(txt_weapon_types)) * 100
        print(f"   Weapon type match: {len(common_weapons)}/{len(txt_weapon_types)} ({weapon_match_pct:.1f}%)")
    else:
        print(f"   No weapons to compare")

    # Final verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}\n")

    if vehicle_match_pct >= 90:
        print(f"✅ EXCELLENT: OCR captured {vehicle_match_pct:.1f}% of vehicle data")
        print(f"   Differences are mostly OCR artifacts and formatting")
    elif vehicle_match_pct >= 70:
        print(f"⚠️  GOOD: OCR captured {vehicle_match_pct:.1f}% of vehicle data")
        print(f"   Some vehicles missed or OCR errors present")
    else:
        print(f"❌ NEEDS IMPROVEMENT: OCR only captured {vehicle_match_pct:.1f}%")
        print(f"   Significant data missing or OCR quality issues")

    # Save report
    report = {
        'ocr_vehicles': [v['name'] for v in ocr_vehicles],
        'txt_vehicles': [v['name'] for v in txt_vehicles],
        'ocr_unique_vehicle_names': ocr_vehicle_names,
        'txt_unique_vehicle_names': txt_vehicle_names,
        'common_vehicle_names': list(common_names),
        'ocr_only_vehicles': list(ocr_only),
        'txt_only_vehicles': list(txt_only),
        'vehicle_match_percentage': vehicle_match_pct if len(txt_vehicle_names) > 0 else 0,
        'ocr_weapon_types': ocr_weapon_types,
        'txt_weapon_types': txt_weapon_types,
        'weapon_match_percentage': weapon_match_pct if len(txt_weapon_types) > 0 else 0,
        'total_data_points_ocr': total_data_points_ocr,
        'total_data_points_txt': total_data_points_txt,
        'coverage_percentage': (total_data_points_ocr / total_data_points_txt * 100) if total_data_points_txt > 0 else 0
    }

    with open('tobruk_british_data_point_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved: tobruk_british_data_point_analysis.json")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    main()
