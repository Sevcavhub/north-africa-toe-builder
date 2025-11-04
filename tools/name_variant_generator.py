#!/usr/bin/env python3
"""
Phase 5.5 - Phase 2: Name Variant Generator
Generates 2,000+ equipment name variants to solve Sherman/M4/M4 Medium Tank naming hell

Strategy:
1. Extract all existing equipment names from database tables
2. Apply programmatic variant generation rules
3. Deduplicate and rank variants by confidence
4. Export to equipment_name_variants table

Variant Rules:
- Abbreviation expansion (Pz.Kpfw. ↔ PzKpfw ↔ Panzer ↔ Panzerkampfwagen)
- Punctuation variations (M-4 ↔ M4 ↔ M 4)
- Special characters (& ↔ and ↔ +)
- Model number formats (Mk.II ↔ Mk II ↔ Mark 2 ↔ Mark II)
"""

import sqlite3
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"
OUTPUT_DIR = Path(__file__).parent.parent / "database" / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Variant generation rules
ABBREVIATION_RULES = {
    # German abbreviations
    r'\bPz\.Kpfw\.\s*': ['PzKpfw ', 'Panzer ', 'Panzerkampfwagen '],
    r'\bPz\.\s*': ['Pz ', 'Panzer '],
    r'\bSd\.Kfz\.\s*': ['SdKfz ', 'Sonderkraftfahrzeug '],
    r'\bAusf\.\s*': ['Ausf ', 'Ausfuehrung '],

    # British abbreviations
    r'\bMk\.\s*': ['Mk ', 'Mark '],
    r'\bMk\.([IVX]+)': [r'Mk \1', r'Mark \1'],

    # Weapon abbreviations
    r'\bpdr\b': ['pounder', 'pdr'],
    r'\b(\d+)\s*pdr\b': [r'\1-pounder', r'\1 pounder', r'\1pdr'],
    r'\bcm\b': ['mm'],  # 8.8cm = 88mm

    # American abbreviations
    r'\bM-(\d+)': [r'M\1', r'M \1'],

    # Other
    r'\bSP\b': ['Self-Propelled', 'SP'],
    r'\bAT\b': ['Anti-Tank', 'Anti Tank', 'AT'],
    r'\bAA\b': ['Anti-Aircraft', 'Anti Aircraft', 'AA'],
}

PUNCTUATION_VARIANTS = [
    (r'(\w)-(\w)', [r'\1\2', r'\1 \2']),  # M-4 → M4, M 4
    (r'(\w)/(\w)', [r'\1-\2', r'\1 \2']),  # M3/M5 → M3-M5, M3 M5
    (r'\.', ''),  # Remove periods
]

SPECIAL_CHARACTER_VARIANTS = {
    r'\s+&\s+': [' and ', ' + '],
    r'\s+#': [' No ', ' Number '],
}

def connect_db():
    """Connect to SQLite database"""
    return sqlite3.connect(str(DB_PATH))

def extract_existing_names(conn) -> Set[str]:
    """Extract all existing equipment names from database tables"""
    names = set()

    # Query all relevant tables
    queries = [
        "SELECT DISTINCT canonical_name FROM equipment_master_new WHERE canonical_name IS NOT NULL",
        "SELECT DISTINCT display_name FROM equipment_master_new WHERE display_name IS NOT NULL",
        "SELECT DISTINCT short_name FROM equipment_master_new WHERE short_name IS NOT NULL",
        "SELECT DISTINCT variant_name FROM equipment_name_variants_new WHERE variant_name IS NOT NULL",
    ]

    for query in queries:
        try:
            cursor = conn.execute(query)
            for row in cursor:
                if row[0]:
                    # Clean up canonical names (remove eq_123_ prefix)
                    name = row[0]
                    if name.startswith('eq_') and '_' in name:
                        # Extract the actual name after eq_{id}_
                        parts = name.split('_', 2)
                        if len(parts) == 3:
                            name = parts[2].replace('_', ' ').title()
                    names.add(name.strip())
        except sqlite3.Error as e:
            print(f"Warning: Query failed: {query[:50]}... - {e}")
            continue

    print(f"Extracted {len(names)} unique equipment names from database")
    return names

def generate_abbreviation_variants(name: str) -> Set[str]:
    """Generate variants using abbreviation expansion rules"""
    variants = {name}

    for pattern, replacements in ABBREVIATION_RULES.items():
        for replacement in replacements:
            variant = re.sub(pattern, replacement, name)
            if variant != name:
                variants.add(variant.strip())

    return variants

def generate_punctuation_variants(name: str) -> Set[str]:
    """Generate variants using punctuation variation rules"""
    variants = {name}

    for pattern, replacements in PUNCTUATION_VARIANTS:
        if not isinstance(replacements, list):
            replacements = [replacements]
        for replacement in replacements:
            variant = re.sub(pattern, replacement, name)
            if variant != name:
                variants.add(variant.strip())

    return variants

def generate_special_char_variants(name: str) -> Set[str]:
    """Generate variants using special character rules"""
    variants = {name}

    for pattern, replacements in SPECIAL_CHARACTER_VARIANTS.items():
        for replacement in replacements:
            variant = re.sub(pattern, replacement, name)
            if variant != name:
                variants.add(variant.strip())

    return variants

def generate_all_variants(name: str) -> Set[str]:
    """Generate all possible variants for a single equipment name"""
    # Start with original name
    current_variants = {name}
    all_variants = set()

    # Apply rules iteratively (up to 3 passes to catch compound variations)
    for _ in range(3):
        new_variants = set()
        for variant in current_variants:
            new_variants.update(generate_abbreviation_variants(variant))
            new_variants.update(generate_punctuation_variants(variant))
            new_variants.update(generate_special_char_variants(variant))

        all_variants.update(new_variants)
        current_variants = new_variants - all_variants

        if not current_variants:  # No new variants generated
            break

    # Remove duplicates and clean up
    cleaned_variants = set()
    for variant in all_variants:
        # Clean up multiple spaces
        variant = re.sub(r'\s+', ' ', variant).strip()
        if variant and len(variant) > 2:  # Skip very short variants
            cleaned_variants.add(variant)

    return cleaned_variants

def assign_confidence_score(original_name: str, variant: str) -> int:
    """Assign confidence score to a variant (100 = exact, 75-90 = programmatic)"""
    if variant == original_name:
        return 100

    # Official-looking variants get higher score
    if any(marker in variant for marker in ['Panzerkampfwagen', 'Sonderkraftfahrzeug', 'Ausfuehrung']):
        return 90  # Full German names

    if re.match(r'^M\d+[A-Z]?\d*\s+\w+$', variant):
        return 85  # American M-series with name (M4 Sherman)

    if re.match(r'^Mark\s+[IVX]+', variant):
        return 85  # British Mark variants

    # Default programmatic variant
    return 80

def deduplicate_variants(variants_by_master: Dict[int, Set[str]]) -> Dict[int, List[Tuple[str, int]]]:
    """Deduplicate variants across all equipment and assign confidence scores"""
    # Track which variant belongs to which master_id
    variant_to_masters = {}

    for master_id, variants in variants_by_master.items():
        for variant in variants:
            if variant not in variant_to_masters:
                variant_to_masters[variant] = []
            variant_to_masters[variant].append(master_id)

    # For duplicates, keep only the first master_id (arbitrary but consistent)
    deduplicated = {}
    for master_id in variants_by_master.keys():
        deduplicated[master_id] = []

    for variant, master_ids in variant_to_masters.items():
        # Assign to first master_id
        primary_master = min(master_ids)
        # Get original name for confidence scoring
        original_name = None
        conn = connect_db()
        cursor = conn.execute(
            "SELECT display_name FROM equipment_master_new WHERE master_id = ?",
            (primary_master,)
        )
        row = cursor.fetchone()
        if row:
            original_name = row[0]
        conn.close()

        confidence = assign_confidence_score(original_name or '', variant)
        deduplicated[primary_master].append((variant, confidence))

    return deduplicated

def main():
    """Main execution"""
    print("=" * 80)
    print("Phase 5.5 - Phase 2: Name Variant Generator")
    print("=" * 80)

    # Step 1: Extract existing names
    print("\nStep 1: Extracting existing equipment names from database...")
    conn = connect_db()
    existing_names = extract_existing_names(conn)

    # Step 2: Get all master_ids
    print("\nStep 2: Loading equipment master records...")
    cursor = conn.execute("""
        SELECT master_id, display_name, canonical_name
        FROM equipment_master_new
        ORDER BY master_id
    """)
    equipment_records = cursor.fetchall()
    print(f"  Found: {len(equipment_records)} equipment records")

    # Step 3: Generate variants for each equipment
    print("\nStep 3: Generating variants for each equipment...")
    variants_by_master = {}
    total_variants = 0

    for master_id, display_name, canonical_name in equipment_records:
        # Use display_name as primary source
        base_name = display_name or canonical_name or f"Equipment_{master_id}"

        # Generate all variants
        variants = generate_all_variants(base_name)
        variants_by_master[master_id] = variants
        total_variants += len(variants)

        if len(variants) > 1:
            print(f"  master_id {master_id}: {base_name} -> {len(variants)} variants")

    print(f"\nTotal variants generated: {total_variants}")

    # Step 4: Deduplicate
    print("\nStep 4: Deduplicating variants...")
    deduplicated = deduplicate_variants(variants_by_master)

    unique_variants = sum(len(variants) for variants in deduplicated.values())
    print(f"  Unique variants: {unique_variants}")

    # Step 5: Export to CSV
    print("\nStep 5: Exporting to CSV...")
    output_file = OUTPUT_DIR / "equipment_name_variants.csv"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("master_id,variant_name,confidence_score,created_at\n")

        for master_id, variants in sorted(deduplicated.items()):
            for variant_name, confidence in sorted(variants, key=lambda x: -x[1]):
                timestamp = datetime.now().isoformat()
                f.write(f"{master_id},\"{variant_name}\",{confidence},{timestamp}\n")

    print(f"  [OK] Exported to: {output_file}")
    print(f"  [OK] Total rows: {unique_variants}")

    # Step 6: Generate summary report
    print("\nStep 6: Generating summary report...")
    report = {
        "phase": "Phase 5.5 - Phase 2",
        "timestamp": datetime.now().isoformat(),
        "total_equipment": len(equipment_records),
        "total_variants_generated": total_variants,
        "unique_variants": unique_variants,
        "average_variants_per_equipment": round(unique_variants / len(equipment_records), 1),
        "confidence_distribution": {},
    }

    # Calculate confidence distribution
    confidence_counts = {}
    for variants in deduplicated.values():
        for _, confidence in variants:
            confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

    report["confidence_distribution"] = confidence_counts

    report_file = OUTPUT_DIR / "name_variant_generation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"  [OK] Report saved to: {report_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Equipment records:        {report['total_equipment']}")
    print(f"Variants generated:       {report['total_variants_generated']}")
    print(f"Unique variants:          {report['unique_variants']}")
    print(f"Avg variants/equipment:   {report['average_variants_per_equipment']}")
    print("\nConfidence Distribution:")
    for conf, count in sorted(confidence_counts.items(), reverse=True):
        print(f"  {conf}: {count} variants")

    conn.close()
    print("\n[SUCCESS] Phase 2: Name Variant Generation COMPLETE")

if __name__ == "__main__":
    main()
