#!/usr/bin/env python3
"""
Phase 1: Discovery & Analysis - COMPLETE DETECTION SUITE (READ-ONLY)
Database Normalization Agent v2.0.0

Runs all 5 detection capabilities:
1. Exact Duplicate Detection
2. Normalization Issue Detection
3. Denormalization Detection
4. Naming Inconsistency Detection
5. Constraint Violation Detection
"""

import sqlite3
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple

DB_PATH = Path("D:/north-africa-toe-builder/database/master_database.db")
OUTPUT_DIR = Path("D:/north-africa-toe-builder")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get read-only database connection"""
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

def get_db_connection_rw():
    """Get read-write connection (for creating temp tables if needed)"""
    return sqlite3.connect(str(DB_PATH))

class DuplicateDetector:
    """Detection Capability #1: Exact Duplicates"""

    def __init__(self, conn):
        self.conn = conn
        self.results = {}

    def detect_hash_based_duplicates(self, table: str, key_columns: List[str],
                                     value_columns: List[str]) -> List[Dict]:
        """Find exact duplicates using hash comparison"""
        cursor = self.conn.cursor()

        # Build hash expression
        hash_expr = " || '|' || ".join([f"COALESCE({col}, 'NULL')" for col in value_columns])
        key_list = ", ".join(key_columns)

        query = f"""
        SELECT {key_list}, COUNT(*) as dup_count,
               GROUP_CONCAT({key_columns[0]}) as all_keys
        FROM {table}
        GROUP BY {hash_expr}
        HAVING COUNT(*) > 1
        """

        try:
            cursor.execute(query)
            return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"  ! Error detecting hash duplicates in {table}: {e}")
            return []

    def detect_case_insensitive_duplicates(self, table: str, name_column: str,
                                           nation_column: str = None) -> List[Dict]:
        """Find case-insensitive name duplicates"""
        cursor = self.conn.cursor()

        group_by = f"LOWER({name_column})"
        if nation_column:
            group_by += f", LOWER({nation_column})"

        query = f"""
        SELECT {name_column} as name,
               {'nation, ' if nation_column else ''}
               COUNT(*) as count,
               GROUP_CONCAT({name_column}, ' | ') as variations
        FROM {table}
        WHERE {name_column} IS NOT NULL
        GROUP BY {group_by}
        HAVING COUNT(*) > 1
        """

        try:
            cursor.execute(query)
            return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
        except Exception as e:
            return []

    def analyze_equipment_table(self) -> Dict:
        """Analyze equipment table for duplicates"""
        print("  - Analyzing equipment table...")

        # Hash-based duplicates
        hash_dups = self.detect_hash_based_duplicates(
            'equipment',
            ['canonical_id'],
            ['name', 'nation', 'category', 'witw_id']
        )

        # Case-insensitive name duplicates
        case_dups = self.detect_case_insensitive_duplicates(
            'equipment', 'name', 'nation'
        )

        return {
            'table': 'equipment',
            'hash_based_duplicates': hash_dups,
            'case_insensitive_duplicates': case_dups,
            'total_duplicate_groups': len(hash_dups) + len(case_dups)
        }

    def run(self) -> Dict:
        """Run all duplicate detection"""
        print("\n[1/5] DUPLICATE DETECTION")
        print("=" * 80)

        results = {
            'detection_type': 'exact_duplicates',
            'analyzed_at': datetime.now().isoformat(),
            'tables_analyzed': []
        }

        # Focus on key equipment tables
        equipment_analysis = self.analyze_equipment_table()
        results['tables_analyzed'].append(equipment_analysis)

        # Similar analysis for other key tables
        for table in ['afv_data', 'wwiitanks_afv_data', 'bg_reference_vehicles']:
            print(f"  - Analyzing {table}...")
            case_dups = self.detect_case_insensitive_duplicates(table, 'name')
            results['tables_analyzed'].append({
                'table': table,
                'case_insensitive_duplicates': case_dups,
                'total_duplicate_groups': len(case_dups)
            })

        self.results = results
        return results


class NormalizationDetector:
    """Detection Capability #2: Normalization Issues"""

    def __init__(self, conn):
        self.conn = conn
        self.results = {}

    def detect_whitespace_issues(self, table: str, columns: List[str]) -> Dict:
        """Detect leading/trailing spaces, multiple spaces, tabs"""
        cursor = self.conn.cursor()
        issues = {}

        for col in columns:
            # Leading/trailing spaces
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE {col} IS NOT NULL AND {col} != TRIM({col})
            """)
            leading_trailing = cursor.fetchone()[0]

            # Multiple consecutive spaces
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE {col} LIKE '%  %'
            """)
            multiple_spaces = cursor.fetchone()[0]

            # Tab characters
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE {col} LIKE '%\t%'
            """)
            tabs = cursor.fetchone()[0]

            if leading_trailing or multiple_spaces or tabs:
                issues[col] = {
                    'leading_trailing_spaces': leading_trailing,
                    'multiple_consecutive_spaces': multiple_spaces,
                    'tab_characters': tabs
                }

        return issues

    def detect_case_inconsistencies(self) -> Dict:
        """Detect case inconsistencies in standard fields"""
        cursor = self.conn.cursor()
        issues = {}

        # Nation should be lowercase
        cursor.execute("""
            SELECT DISTINCT nation FROM equipment
            WHERE nation IS NOT NULL AND nation != LOWER(nation)
        """)
        uppercase_nations = [row[0] for row in cursor.fetchall()]

        if uppercase_nations:
            issues['nation_uppercase'] = {
                'count': len(uppercase_nations),
                'examples': uppercase_nations[:5]
            }

        # canonical_id should be uppercase
        cursor.execute("""
            SELECT canonical_id FROM equipment
            WHERE canonical_id != UPPER(canonical_id)
            LIMIT 10
        """)
        lowercase_ids = [row[0] for row in cursor.fetchall()]

        if lowercase_ids:
            issues['canonical_id_lowercase'] = {
                'count': len(lowercase_ids),
                'examples': lowercase_ids[:5]
            }

        return issues

    def detect_format_variations(self) -> Dict:
        """Detect format inconsistencies"""
        cursor = self.conn.cursor()
        issues = {}

        # Production dates should be YYYY format
        cursor.execute("""
            SELECT canonical_id, production_start, production_end
            FROM equipment
            WHERE (LENGTH(production_start) != 4 AND production_start IS NOT NULL)
               OR (LENGTH(production_end) != 4 AND production_end IS NOT NULL)
            LIMIT 10
        """)
        date_format_issues = cursor.fetchall()

        if date_format_issues:
            issues['production_date_format'] = {
                'count': len(date_format_issues),
                'examples': [
                    {'id': row[0], 'start': row[1], 'end': row[2]}
                    for row in date_format_issues[:5]
                ]
            }

        return issues

    def run(self) -> Dict:
        """Run all normalization detection"""
        print("\n[2/5] NORMALIZATION ISSUE DETECTION")
        print("=" * 80)

        results = {
            'detection_type': 'normalization_issues',
            'analyzed_at': datetime.now().isoformat(),
            'issues': {}
        }

        # Whitespace issues in equipment table
        print("  - Checking whitespace issues...")
        ws_issues = self.detect_whitespace_issues('equipment', ['name', 'category', 'manufacturers'])
        if ws_issues:
            results['issues']['whitespace'] = ws_issues

        # Case inconsistencies
        print("  - Checking case inconsistencies...")
        case_issues = self.detect_case_inconsistencies()
        if case_issues:
            results['issues']['case_inconsistencies'] = case_issues

        # Format variations
        print("  - Checking format variations...")
        format_issues = self.detect_format_variations()
        if format_issues:
            results['issues']['format_variations'] = format_issues

        self.results = results
        return results


class ConstraintViolationDetector:
    """Detection Capability #5: Constraint Violations"""

    def __init__(self, conn):
        self.conn = conn
        self.results = {}

    def detect_witw_id_collisions(self) -> List[Dict]:
        """Detect WITW ID collisions (CRITICAL)"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                witw_id,
                COUNT(*) as collision_count,
                GROUP_CONCAT(canonical_id, ' | ') as colliding_items,
                GROUP_CONCAT(name, ' | ') as names,
                GROUP_CONCAT(category, ' | ') as categories
            FROM equipment
            WHERE witw_id IS NOT NULL AND witw_id != 'NOT_IN_DATABASE'
            GROUP BY witw_id
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        """)

        collisions = []
        for row in cursor.fetchall():
            collisions.append({
                'witw_id': row[0],
                'collision_count': row[1],
                'colliding_items': row[2].split(' | '),
                'names': row[3].split(' | '),
                'categories': row[4].split(' | ') if row[4] else []
            })

        return collisions

    def detect_aircraft_as_tanks(self) -> List[Dict]:
        """Detect aircraft categorized as tanks (CRITICAL)"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT canonical_id, name, witw_name, category
            FROM equipment
            WHERE category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
              AND (witw_name LIKE '%(FI)%'
                OR witw_name LIKE '%(LB)%'
                OR witw_name LIKE '%Hurricane%'
                OR witw_name LIKE '%Spitfire%'
                OR witw_name LIKE '%Lysander%'
                OR witw_name LIKE '%Blenheim%')
        """)

        return [
            {'canonical_id': row[0], 'name': row[1], 'witw_name': row[2], 'category': row[3]}
            for row in cursor.fetchall()
        ]

    def detect_null_equipment_type(self) -> Dict:
        """Detect NULL equipment_type (HIGH priority)"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL")
        null_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM equipment")
        total_count = cursor.fetchone()[0]

        percentage = (null_count / total_count * 100) if total_count > 0 else 0

        return {
            'null_count': null_count,
            'total_count': total_count,
            'percentage': round(percentage, 1)
        }

    def detect_empty_equipment_guns(self) -> Dict:
        """Detect tanks without gun linkages (HIGH priority)"""
        cursor = self.conn.cursor()

        # Count tanks
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
        """)
        tank_count = cursor.fetchone()[0]

        # Count equipment_guns entries
        cursor.execute("SELECT COUNT(*) FROM equipment_guns")
        gun_linkage_count = cursor.fetchone()[0]

        return {
            'tank_count': tank_count,
            'gun_linkage_count': gun_linkage_count,
            'missing_linkages': tank_count - gun_linkage_count,
            'percentage_missing': round((tank_count - gun_linkage_count) / tank_count * 100, 1) if tank_count > 0 else 0
        }

    def detect_orphaned_foreign_keys(self) -> Dict:
        """Detect orphaned foreign key references"""
        cursor = self.conn.cursor()
        issues = {}

        # Orphaned equipment_guns
        cursor.execute("""
            SELECT COUNT(*) FROM equipment_guns eg
            LEFT JOIN equipment e ON eg.equipment_id = e.canonical_id
            WHERE e.canonical_id IS NULL
        """)
        orphaned_eq_guns = cursor.fetchone()[0]

        if orphaned_eq_guns > 0:
            issues['equipment_guns_orphaned_equipment'] = orphaned_eq_guns

        # Null equipment_ids in unit_equipment
        cursor.execute("""
            SELECT COUNT(*) FROM unit_equipment
            WHERE equipment_id IS NULL
        """)
        null_eq_in_units = cursor.fetchone()[0]

        if null_eq_in_units > 0:
            issues['unit_equipment_null_equipment_id'] = null_eq_in_units

        return issues

    def run(self) -> Dict:
        """Run all constraint violation detection"""
        print("\n[5/5] CONSTRAINT VIOLATION DETECTION")
        print("=" * 80)

        results = {
            'detection_type': 'constraint_violations',
            'analyzed_at': datetime.now().isoformat(),
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        # CRITICAL: WITW ID collisions
        print("  - Detecting WITW ID collisions...")
        witw_collisions = self.detect_witw_id_collisions()
        if witw_collisions:
            results['critical'].append({
                'type': 'witw_id_collision',
                'severity': 'CRITICAL',
                'count': len(witw_collisions),
                'total_affected_records': sum(c['collision_count'] for c in witw_collisions),
                'details': witw_collisions[:10]  # Top 10 worst
            })

        # CRITICAL: Aircraft as tanks
        print("  - Detecting aircraft-as-tanks violations...")
        aircraft_tanks = self.detect_aircraft_as_tanks()
        if aircraft_tanks:
            results['critical'].append({
                'type': 'aircraft_as_tanks',
                'severity': 'CRITICAL',
                'count': len(aircraft_tanks),
                'affected': aircraft_tanks
            })

        # HIGH: NULL equipment_type
        print("  - Detecting NULL equipment_type...")
        null_type = self.detect_null_equipment_type()
        results['high'].append({
            'type': 'null_equipment_type',
            'severity': 'HIGH',
            'metrics': null_type
        })

        # HIGH: Empty equipment_guns
        print("  - Detecting empty equipment_guns...")
        empty_guns = self.detect_empty_equipment_guns()
        results['high'].append({
            'type': 'empty_equipment_guns',
            'severity': 'HIGH',
            'metrics': empty_guns
        })

        # HIGH: Orphaned foreign keys
        print("  - Detecting orphaned foreign keys...")
        orphaned = self.detect_orphaned_foreign_keys()
        if orphaned:
            results['high'].append({
                'type': 'orphaned_foreign_keys',
                'severity': 'HIGH',
                'details': orphaned
            })

        self.results = results
        return results


class NamingInconsistencyDetector:
    """Detection Capability #4: Naming Inconsistencies"""

    def __init__(self, conn):
        self.conn = conn
        self.results = {}

    def normalize_name(self, name: str) -> str:
        """Normalize name for fuzzy matching"""
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove punctuation
        normalized = re.sub(r'[.,\-/]', ' ', normalized)

        # Normalize common abbreviations
        replacements = {
            'mk': 'mark',
            ' ii ': ' 2 ',
            ' iii ': ' 3 ',
            ' iv ': ' 4 ',
            ' v ': ' 5 ',
            'pzkpfw': 'panzer',
            'pz.kpfw': 'panzer',
            'pz': 'panzer'
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def tokenize(self, name: str) -> set:
        """Tokenize name for matching"""
        return set(self.normalize_name(name).split())

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate Jaccard similarity between names"""
        tokens1 = self.tokenize(name1)
        tokens2 = self.tokenize(name2)

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def find_name_variants(self) -> List[Dict]:
        """Find name variants across equipment and bg_reference_vehicles"""
        cursor = self.conn.cursor()

        # Get all equipment names
        cursor.execute("""
            SELECT canonical_id, name, category
            FROM equipment
            WHERE category IN ('tanks', 'main_tanks', 'light_tanks', 'medium_tanks', 'heavy_tanks')
        """)
        equipment_items = cursor.fetchall()

        # Get all bg_reference_vehicles names
        cursor.execute("SELECT DISTINCT name FROM bg_reference_vehicles")
        bg_names = set(row[0] for row in cursor.fetchall())

        # Find mismatches
        mismatches = []

        for eq_id, eq_name, eq_cat in equipment_items:
            # Exact match check
            if eq_name in bg_names:
                continue

            # Find fuzzy matches
            matches = []
            for bg_name in bg_names:
                similarity = self.calculate_similarity(eq_name, bg_name)
                if similarity > 0.6:  # 60% similarity threshold
                    matches.append({
                        'bg_name': bg_name,
                        'similarity': round(similarity, 3)
                    })

            if matches or not matches:
                mismatches.append({
                    'canonical_id': eq_id,
                    'equipment_name': eq_name,
                    'category': eq_cat,
                    'bg_exact_match': False,
                    'bg_fuzzy_matches': sorted(matches, key=lambda x: x['similarity'], reverse=True)[:3]
                })

        return mismatches

    def run(self) -> Dict:
        """Run naming inconsistency detection"""
        print("\n[4/5] NAMING INCONSISTENCY DETECTION")
        print("=" * 80)

        print("  - Finding name variants between equipment and bg_reference_vehicles...")
        name_variants = self.find_name_variants()

        results = {
            'detection_type': 'naming_inconsistencies',
            'analyzed_at': datetime.now().isoformat(),
            'name_variant_groups': name_variants[:50],  # Top 50
            'total_mismatches': len(name_variants)
        }

        self.results = results
        return results


class DenormalizationDetector:
    """Detection Capability #3: Denormalization Issues"""

    def __init__(self, conn):
        self.conn = conn
        self.results = {}

    def detect_transitive_dependencies(self) -> List[Dict]:
        """Detect transitive dependencies (A→B→C violations)"""
        cursor = self.conn.cursor()

        # Example: witw_id → witw_name → nation
        cursor.execute("""
            SELECT
                witw_id,
                COUNT(DISTINCT witw_name) as name_variations,
                COUNT(DISTINCT nation) as nation_variations,
                GROUP_CONCAT(DISTINCT witw_name, ' | ') as names,
                GROUP_CONCAT(DISTINCT nation, ' | ') as nations
            FROM equipment
            WHERE witw_id IS NOT NULL AND witw_id != 'NOT_IN_DATABASE'
            GROUP BY witw_id
            HAVING COUNT(DISTINCT witw_name) > 1 OR COUNT(DISTINCT nation) > 1
        """)

        violations = []
        for row in cursor.fetchall():
            violations.append({
                'witw_id': row[0],
                'name_variations': row[1],
                'nation_variations': row[2],
                'names': row[3].split(' | '),
                'nations': row[4].split(' | ')
            })

        return violations

    def detect_multivalued_attributes(self) -> Dict:
        """Detect multi-valued attributes (comma-separated values)"""
        cursor = self.conn.cursor()

        # Manufacturers with commas
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE manufacturers LIKE '%,%'
        """)
        multi_manufacturers = cursor.fetchone()[0]

        # Aliases (JSON arrays)
        cursor.execute("""
            SELECT COUNT(*) FROM equipment
            WHERE aliases IS NOT NULL AND aliases != '[]'
        """)
        multi_aliases = cursor.fetchone()[0]

        return {
            'manufacturers_comma_separated': multi_manufacturers,
            'aliases_json_arrays': multi_aliases
        }

    def run(self) -> Dict:
        """Run denormalization detection"""
        print("\n[3/5] DENORMALIZATION DETECTION")
        print("=" * 80)

        print("  - Detecting transitive dependencies...")
        transitive = self.detect_transitive_dependencies()

        print("  - Detecting multi-valued attributes...")
        multivalued = self.detect_multivalued_attributes()

        results = {
            'detection_type': 'denormalization_issues',
            'analyzed_at': datetime.now().isoformat(),
            'transitive_dependencies': transitive,
            'multivalued_attributes': multivalued
        }

        self.results = results
        return results


def main():
    """Main Phase 1 analysis"""
    print("=" * 80)
    print("DATABASE NORMALIZATION AGENT v2.0.0")
    print("PHASE 1: DISCOVERY & ANALYSIS (READ-ONLY)")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Connect to database
    conn = get_db_connection()

    # Run all 5 detection capabilities
    detectors = [
        DuplicateDetector(conn),
        NormalizationDetector(conn),
        DenormalizationDetector(conn),
        NamingInconsistencyDetector(conn),
        ConstraintViolationDetector(conn)
    ]

    all_results = {}

    for detector in detectors:
        try:
            result = detector.run()
            detection_type = result.get('detection_type', detector.__class__.__name__)
            all_results[detection_type] = result
        except Exception as e:
            print(f"ERROR in {detector.__class__.__name__}: {e}")
            import traceback
            traceback.print_exc()

    # Save individual reports
    print("\n" + "=" * 80)
    print("SAVING REPORTS...")
    print("=" * 80)

    report_files = {
        'duplicate_analysis.json': all_results.get('exact_duplicates', {}),
        'normalization_issues.json': all_results.get('normalization_issues', {}),
        'denormalization_report.json': all_results.get('denormalization_issues', {}),
        'naming_inconsistencies.json': all_results.get('naming_inconsistencies', {}),
        'constraint_violations.json': all_results.get('constraint_violations', {})
    }

    for filename, data in report_files.items():
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"[OK] {filename}")

    # Generate executive summary metrics
    print("\n" + "=" * 80)
    print("GENERATING EXECUTIVE SUMMARY...")
    print("=" * 80)

    conn.close()
    print("\n[OK] Phase 1 Complete!")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
