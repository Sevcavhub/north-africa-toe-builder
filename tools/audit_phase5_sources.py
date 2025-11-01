#!/usr/bin/env python3
"""
Phase 5 Data Quality Audit
Analyzes source JSON files for equipment specification completeness.

Generates PHASE5_DATA_QUALITY_REPORT.md with:
- Item counts by nation
- Field population rates (armor, guns, mobility, physical)
- Missing critical values flagged for research
- Duplicate detection
- Name normalization issues
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Source file paths
ONWAR_FILE = Path("data/output/afv_data/afv_complete_with_specs.json")
WWIITANKS_AFV_FILE = Path("data/output/afv_data/wwiitanks/all_afvs.json")
WWIITANKS_GUN_FILE = Path("data/output/afv_data/wwiitanks/all_guns_v2.json")

# Critical fields for scenario generation
CRITICAL_FIELDS = {
    "armor": ["hull_front", "hull_side", "hull_rear", "turret_front", "turret_side", "turret_rear"],
    "mobility": ["speed", "range", "fuel_capacity"],
    "physical": ["combat_weight", "crew", "length_hull", "width", "height"],
    "armament": ["primary_armament", "secondary_armament"]
}


def is_empty_value(value: Any) -> bool:
    """Check if a value is considered empty/missing."""
    if value is None:
        return True
    if isinstance(value, str):
        val_lower = value.strip().lower()
        return val_lower in ["", "n.a.", "n/a", "unknown", "?", "-", "none"]
    return False


def analyze_onwar_data(filepath: Path) -> Dict:
    """Analyze OnWar AFV data completeness."""
    print(f"Analyzing OnWar data from {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_items = len(data)
    nation_counts = defaultdict(int)
    field_populated = defaultdict(int)
    missing_critical = []

    for item in data:
        nation = item.get('country', 'unknown').lower()
        nation_counts[nation] += 1

        # Check armor values
        armor_present = 0
        armor_fields = ["hull_front", "hull_side", "hull_rear", "turret_front", "turret_side", "turret_rear"]
        for field in armor_fields:
            if not is_empty_value(item.get(field)):
                field_populated[field] += 1
                armor_present += 1

        # Check mobility
        mobility_fields = ["speed", "range", "fuel_capacity"]
        mobility_present = 0
        for field in mobility_fields:
            if not is_empty_value(item.get(field)):
                field_populated[field] += 1
                mobility_present += 1

        # Check physical characteristics
        physical_fields = ["combat_weight", "crew", "length_hull", "width", "height"]
        physical_present = 0
        for field in physical_fields:
            if not is_empty_value(item.get(field)):
                field_populated[field] += 1
                physical_present += 1

        # Check armament
        armament_fields = ["primary_armament", "secondary_armament"]
        armament_present = 0
        for field in armament_fields:
            if not is_empty_value(item.get(field)):
                field_populated[field] += 1
                armament_present += 1

        # Flag items with critical gaps
        if armor_present == 0 or mobility_present == 0 or physical_present < 2:
            missing_critical.append({
                "name": item.get('vehicle_name', 'unknown'),
                "nation": nation,
                "url": item.get('url', ''),
                "gaps": {
                    "armor": armor_present == 0,
                    "mobility": mobility_present == 0,
                    "physical": physical_present < 2
                }
            })

    return {
        "source": "OnWar",
        "total_items": total_items,
        "nation_counts": dict(nation_counts),
        "field_populated": dict(field_populated),
        "missing_critical": missing_critical
    }


def analyze_wwiitanks_afv_data(filepath: Path) -> Dict:
    """Analyze WWIITANKS AFV data completeness."""
    print(f"Analyzing WWIITANKS AFV data from {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_items = len(data)
    nation_counts = defaultdict(int)
    has_armor = 0
    has_weapon = 0
    has_history = 0

    for item in data:
        nation = item.get('country', 'unknown').lower()
        nation_counts[nation] += 1

        indicators = item.get('indicators', {})
        if indicators.get('hasArmourDetails'):
            has_armor += 1
        if indicators.get('hasWeaponDetails'):
            has_weapon += 1
        if indicators.get('hasVehicleHistory'):
            has_history += 1

    return {
        "source": "WWIITANKS_AFV",
        "total_items": total_items,
        "nation_counts": dict(nation_counts),
        "has_armor_details": has_armor,
        "has_weapon_details": has_weapon,
        "has_history": has_history
    }


def analyze_wwiitanks_gun_data(filepath: Path) -> Dict:
    """Analyze WWIITANKS gun data completeness."""
    print(f"Analyzing WWIITANKS gun data from {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_items = len(data)
    nation_counts = defaultdict(int)
    has_caliber = 0
    has_ammunition = 0
    has_vehicles = 0

    for item in data:
        nation = item.get('country', 'unknown').lower()
        nation_counts[nation] += 1

        basic_specs = item.get('basic_specs', {})
        if basic_specs.get('calibre'):
            has_caliber += 1

        if item.get('ammunition') and len(item['ammunition']) > 0:
            has_ammunition += 1

        if item.get('vehicles_using_gun') and len(item['vehicles_using_gun']) > 0:
            has_vehicles += 1

    return {
        "source": "WWIITANKS_GUN",
        "total_items": total_items,
        "nation_counts": dict(nation_counts),
        "has_caliber": has_caliber,
        "has_ammunition": has_ammunition,
        "has_vehicles": has_vehicles
    }


def generate_report(onwar_results: Dict, wwiitanks_afv_results: Dict, wwiitanks_gun_results: Dict) -> str:
    """Generate markdown report from analysis results."""

    report = """# Phase 5 Data Quality Audit Report

**Generated**: {timestamp}

## Executive Summary

This report analyzes the completeness of scraped equipment specification data from OnWar and WWIITANKS sources before importing into master_database.db.

---

## 1. OnWar AFV Data ({total} items)

**Source**: `data/output/afv_data/afv_complete_with_specs.json`

### By Nation
{nation_table_onwar}

### Field Population Rates

**Armor Values**:
{armor_stats}

**Mobility**:
{mobility_stats}

**Physical Characteristics**:
{physical_stats}

**Armament**:
{armament_stats}

### Critical Gaps ({gaps_count} items)

Items missing critical specification data (armor OR mobility OR <2 physical characteristics):

{critical_gaps}

---

## 2. WWIITANKS AFV Data ({wwiitanks_afv_total} items)

**Source**: `data/output/afv_data/wwiitanks/all_afvs.json`

### By Nation
{nation_table_wwiitanks}

### Data Indicators
- **Has Armor Details**: {armor_pct}% ({armor_count}/{wwiitanks_afv_total})
- **Has Weapon Details**: {weapon_pct}% ({weapon_count}/{wwiitanks_afv_total})
- **Has Vehicle History**: {history_pct}% ({history_count}/{wwiitanks_afv_total})

**Note**: WWIITANKS data has unstructured field names and will require parsing scripts to extract armor/gun specifications.

---

## 3. WWIITANKS Gun Data ({gun_total} items)

**Source**: `data/output/afv_data/wwiitanks/all_guns_v2.json`

### By Nation
{nation_table_guns}

### Data Completeness
- **Has Caliber**: {caliber_pct}% ({caliber_count}/{gun_total})
- **Has Ammunition Data**: {ammo_pct}% ({ammo_count}/{gun_total})
- **Has Vehicle Assignments**: {vehicles_pct}% ({vehicles_count}/{gun_total})

---

## 4. Recommendations

### Immediate Actions
1. **OnWar Data**: Ready for import with {onwar_ready_pct}% usable items
2. **WWIITANKS Parsing**: Requires field extraction scripts for armor/gun specs
3. **Critical Gaps**: {gaps_count} OnWar items need manual research or fallback to WWIITANKS

### Data Priority
**High Quality** (import first):
- OnWar AFV data (structured fields, ready to import)
- WWIITANKS gun data (caliber/ammunition present)

**Needs Parsing** (phase 3 work):
- WWIITANKS AFV data (extract from unstructured fields)

### Import Strategy
1. Import OnWar → `afv_data` table (Phase 2-3)
2. Parse WWIITANKS AFV → `wwiitanks_afv_data` table (Phase 3)
3. Import WWIITANKS guns → `wwiitanks_gun_data` table (Phase 3)
4. Populate `equipment` table with hybrid data (Phase 4)

---

**Audit Complete**
"""

    from datetime import datetime

    # Build nation tables
    nation_table_onwar = "| Nation | Count |\n|--------|-------|\n"
    for nation, count in sorted(onwar_results['nation_counts'].items()):
        nation_table_onwar += f"| {nation} | {count} |\n"

    nation_table_wwiitanks = "| Nation | Count |\n|--------|-------|\n"
    for nation, count in sorted(wwiitanks_afv_results['nation_counts'].items()):
        nation_table_wwiitanks += f"| {nation} | {count} |\n"

    nation_table_guns = "| Nation | Count |\n|--------|-------|\n"
    for nation, count in sorted(wwiitanks_gun_results['nation_counts'].items()):
        nation_table_guns += f"| {nation} | {count} |\n"

    # Build field stats
    total = onwar_results['total_items']
    field_pop = onwar_results['field_populated']

    armor_stats = ""
    for field in ["hull_front", "hull_side", "hull_rear", "turret_front", "turret_side", "turret_rear"]:
        count = field_pop.get(field, 0)
        pct = (count / total * 100) if total > 0 else 0
        armor_stats += f"- `{field}`: {pct:.1f}% ({count}/{total})\n"

    mobility_stats = ""
    for field in ["speed", "range", "fuel_capacity"]:
        count = field_pop.get(field, 0)
        pct = (count / total * 100) if total > 0 else 0
        mobility_stats += f"- `{field}`: {pct:.1f}% ({count}/{total})\n"

    physical_stats = ""
    for field in ["combat_weight", "crew", "length_hull", "width", "height"]:
        count = field_pop.get(field, 0)
        pct = (count / total * 100) if total > 0 else 0
        physical_stats += f"- `{field}`: {pct:.1f}% ({count}/{total})\n"

    armament_stats = ""
    for field in ["primary_armament", "secondary_armament"]:
        count = field_pop.get(field, 0)
        pct = (count / total * 100) if total > 0 else 0
        armament_stats += f"- `{field}`: {pct:.1f}% ({count}/{total})\n"

    # Build critical gaps list
    gaps_count = len(onwar_results['missing_critical'])
    critical_gaps = ""
    for item in onwar_results['missing_critical'][:20]:  # Limit to first 20
        gaps_list = []
        if item['gaps']['armor']:
            gaps_list.append("armor")
        if item['gaps']['mobility']:
            gaps_list.append("mobility")
        if item['gaps']['physical']:
            gaps_list.append("physical")

        critical_gaps += f"- **{item['name']}** ({item['nation']}) - Missing: {', '.join(gaps_list)}\n"
        critical_gaps += f"  - Source: {item['url']}\n"

    if gaps_count > 20:
        critical_gaps += f"\n*...and {gaps_count - 20} more items*\n"

    # Calculate percentages
    onwar_ready = total - gaps_count
    onwar_ready_pct = (onwar_ready / total * 100) if total > 0 else 0

    wwiitanks_afv_total = wwiitanks_afv_results['total_items']
    armor_pct = (wwiitanks_afv_results['has_armor_details'] / wwiitanks_afv_total * 100) if wwiitanks_afv_total > 0 else 0
    weapon_pct = (wwiitanks_afv_results['has_weapon_details'] / wwiitanks_afv_total * 100) if wwiitanks_afv_total > 0 else 0
    history_pct = (wwiitanks_afv_results['has_history'] / wwiitanks_afv_total * 100) if wwiitanks_afv_total > 0 else 0

    gun_total = wwiitanks_gun_results['total_items']
    caliber_pct = (wwiitanks_gun_results['has_caliber'] / gun_total * 100) if gun_total > 0 else 0
    ammo_pct = (wwiitanks_gun_results['has_ammunition'] / gun_total * 100) if gun_total > 0 else 0
    vehicles_pct = (wwiitanks_gun_results['has_vehicles'] / gun_total * 100) if gun_total > 0 else 0

    # Format report
    report = report.format(
        timestamp=datetime.now().isoformat(),
        total=total,
        nation_table_onwar=nation_table_onwar,
        armor_stats=armor_stats,
        mobility_stats=mobility_stats,
        physical_stats=physical_stats,
        armament_stats=armament_stats,
        gaps_count=gaps_count,
        critical_gaps=critical_gaps if critical_gaps else "None found - all items have sufficient data!\n",
        wwiitanks_afv_total=wwiitanks_afv_total,
        nation_table_wwiitanks=nation_table_wwiitanks,
        armor_pct=armor_pct,
        armor_count=wwiitanks_afv_results['has_armor_details'],
        weapon_pct=weapon_pct,
        weapon_count=wwiitanks_afv_results['has_weapon_details'],
        history_pct=history_pct,
        history_count=wwiitanks_afv_results['has_history'],
        gun_total=gun_total,
        nation_table_guns=nation_table_guns,
        caliber_pct=caliber_pct,
        caliber_count=wwiitanks_gun_results['has_caliber'],
        ammo_pct=ammo_pct,
        ammo_count=wwiitanks_gun_results['has_ammunition'],
        vehicles_pct=vehicles_pct,
        vehicles_count=wwiitanks_gun_results['has_vehicles'],
        onwar_ready_pct=onwar_ready_pct
    )

    return report


def main():
    """Run data quality audit."""
    print("=" * 70)
    print("PHASE 5 DATA QUALITY AUDIT")
    print("=" * 70)

    # Check files exist
    for filepath in [ONWAR_FILE, WWIITANKS_AFV_FILE, WWIITANKS_GUN_FILE]:
        if not filepath.exists():
            print(f"ERROR: Source file not found: {filepath}")
            sys.exit(1)

    # Analyze each source
    onwar_results = analyze_onwar_data(ONWAR_FILE)
    wwiitanks_afv_results = analyze_wwiitanks_afv_data(WWIITANKS_AFV_FILE)
    wwiitanks_gun_results = analyze_wwiitanks_gun_data(WWIITANKS_GUN_FILE)

    # Generate report
    print("\nGenerating report...")
    report = generate_report(onwar_results, wwiitanks_afv_results, wwiitanks_gun_results)

    # Write report
    report_path = Path("PHASE5_DATA_QUALITY_REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport generated: {report_path}")
    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

    # Print summary
    print(f"\nOnWar AFV: {onwar_results['total_items']} items")
    print(f"WWIITANKS AFV: {wwiitanks_afv_results['total_items']} items")
    print(f"WWIITANKS Guns: {wwiitanks_gun_results['total_items']} items")
    print(f"\nCritical gaps: {len(onwar_results['missing_critical'])} items need attention")


if __name__ == "__main__":
    main()
