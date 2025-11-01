#!/usr/bin/env python3
"""
Comprehensive Database Analysis
Detailed inventory of all databases to inform consolidation decisions.

Outputs:
- Schema comparison across all databases
- Data overlap analysis
- Unique data identification
- Consolidation impact assessment
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Database inventory
DATABASES = {
    'ACTIVE': {
        'master_database': 'database/master_database.db',
    },
    'ITERATION_2': {
        'witw_data': 'data/iterations/iteration_2/Timeline_TOE_Reconstruction/witw_data.db',
    },
    'ITERATION_1': {
        'north_africa_wargame': 'data/iterations/iteration_1/North Africa Campaign Production/08_Database/north_africa_wargame.db',
        'witw_data_iter1': 'data/iterations/iteration_1/North Africa Campaign Production/08_Database/witw_data.db',
    },
    'BACKUPS': {
        'master_backup': 'database/master_database_backup_20251029.db',
    }
}

def analyze_database_schema(db_path: Path) -> dict:
    """Get complete schema information for a database."""

    if not db_path.exists():
        return {'error': 'File not found'}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]

        schema = {}

        for table in tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            # Get sample data (first 3 rows)
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            samples = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]

            schema[table] = {
                'columns': [(col[1], col[2]) for col in columns],
                'column_names': [col[1] for col in columns],
                'row_count': row_count,
                'sample_data': [dict(zip(col_names, row)) for row in samples]
            }

        conn.close()

        file_size = db_path.stat().st_size / (1024 * 1024)  # MB

        return {
            'file_size_mb': round(file_size, 2),
            'table_count': len(tables),
            'tables': schema
        }

    except Exception as e:
        return {'error': str(e)}


def find_equipment_tables(db_info: dict) -> list:
    """Identify tables that contain equipment/vehicle data."""
    equipment_keywords = ['vehicle', 'equipment', 'weapon', 'device', 'gun', 'tank', 'armor']

    equipment_tables = []

    if 'tables' in db_info:
        for table_name, table_info in db_info['tables'].items():
            # Check table name
            if any(kw in table_name.lower() for kw in equipment_keywords):
                equipment_tables.append({
                    'table': table_name,
                    'rows': table_info['row_count'],
                    'columns': len(table_info['columns'])
                })

    return equipment_tables


def compare_schemas(db1_info: dict, db2_info: dict, db1_name: str, db2_name: str) -> dict:
    """Compare schemas between two databases to find overlaps."""

    if 'tables' not in db1_info or 'tables' not in db2_info:
        return {'error': 'Invalid database info'}

    db1_tables = set(db1_info['tables'].keys())
    db2_tables = set(db2_info['tables'].keys())

    common_tables = db1_tables & db2_tables
    unique_db1 = db1_tables - db2_tables
    unique_db2 = db2_tables - db1_tables

    # For common tables, compare columns
    column_comparison = {}
    for table in common_tables:
        cols1 = set(db1_info['tables'][table]['column_names'])
        cols2 = set(db2_info['tables'][table]['column_names'])

        column_comparison[table] = {
            'common_columns': list(cols1 & cols2),
            f'unique_to_{db1_name}': list(cols1 - cols2),
            f'unique_to_{db2_name}': list(cols2 - cols1),
            f'{db1_name}_row_count': db1_info['tables'][table]['row_count'],
            f'{db2_name}_row_count': db2_info['tables'][table]['row_count']
        }

    return {
        'common_tables': list(common_tables),
        'unique_to_' + db1_name: list(unique_db1),
        'unique_to_' + db2_name: list(unique_db2),
        'column_comparison': column_comparison
    }


def assess_consolidation_value(db_info: dict, db_name: str, master_info: dict) -> dict:
    """Assess what value this database would add to master."""

    if 'tables' not in db_info:
        return {'error': 'Invalid database info'}

    master_tables = set(master_info.get('tables', {}).keys())
    db_tables = set(db_info['tables'].keys())

    # Categorize tables
    new_tables = []  # Tables not in master
    overlapping_tables = []  # Tables that exist in master

    for table in db_tables:
        table_info = db_info['tables'][table]

        if table not in master_tables:
            new_tables.append({
                'table': table,
                'rows': table_info['row_count'],
                'columns': len(table_info['columns']),
                'potential_value': 'NEW_DATA',
                'sample': table_info['sample_data'][0] if table_info['sample_data'] else None
            })
        else:
            # Compare row counts
            master_rows = master_info['tables'][table]['row_count']
            db_rows = table_info['row_count']

            overlapping_tables.append({
                'table': table,
                'master_rows': master_rows,
                'this_db_rows': db_rows,
                'difference': db_rows - master_rows,
                'potential_value': 'ADDITIONAL_ROWS' if db_rows > master_rows else 'DUPLICATE_DATA'
            })

    return {
        'database': db_name,
        'new_tables': new_tables,
        'overlapping_tables': overlapping_tables,
        'summary': {
            'new_table_count': len(new_tables),
            'new_data_rows': sum(t['rows'] for t in new_tables),
            'overlapping_table_count': len(overlapping_tables),
            'additional_rows_available': sum(t['difference'] for t in overlapping_tables if t['difference'] > 0)
        }
    }


def generate_consolidation_recommendations(all_analyses: dict, master_info: dict) -> dict:
    """Generate specific recommendations for consolidation."""

    recommendations = {
        'high_value': [],
        'medium_value': [],
        'low_value': [],
        'not_recommended': []
    }

    for category, databases in all_analyses.items():
        if category == 'ACTIVE':
            continue  # Skip master database

        for db_name, analysis in databases.items():
            if 'consolidation_value' not in analysis:
                continue

            value = analysis['consolidation_value']

            # Analyze each new table for value
            for table_info in value.get('new_tables', []):
                table_name = table_info['table']
                rows = table_info['rows']

                recommendation = {
                    'database': db_name,
                    'table': table_name,
                    'rows': rows,
                    'action': 'IMPORT',
                    'risk': 'LOW',
                    'reason': ''
                }

                # Assess value based on table name and row count
                if 'conversion' in table_name.lower() or 'formula' in table_name.lower():
                    recommendation['value'] = 'HIGH'
                    recommendation['reason'] = 'Game conversion formulas - useful for scenario generation'
                    recommendations['high_value'].append(recommendation)

                elif 'infantry' in table_name.lower() and rows > 0:
                    recommendation['value'] = 'HIGH'
                    recommendation['reason'] = 'Infantry data not in master_equipment'
                    recommendations['high_value'].append(recommendation)

                elif 'squad' in table_name.lower() and rows > 0:
                    recommendation['value'] = 'HIGH'
                    recommendation['reason'] = 'Squad data complements vehicle data'
                    recommendations['high_value'].append(recommendation)

                elif 'towed' in table_name.lower():
                    recommendation['value'] = 'MEDIUM'
                    recommendation['reason'] = 'Towed guns - small dataset, easy to import'
                    recommendations['medium_value'].append(recommendation)

                elif rows == 0:
                    recommendation['value'] = 'NONE'
                    recommendation['action'] = 'SKIP'
                    recommendation['reason'] = 'Empty table'
                    recommendations['not_recommended'].append(recommendation)

                else:
                    recommendation['value'] = 'MEDIUM'
                    recommendation['reason'] = f'New data type ({rows} rows)'
                    recommendations['medium_value'].append(recommendation)

            # Analyze overlapping tables
            for table_info in value.get('overlapping_tables', []):
                table_name = table_info['table']
                difference = table_info.get('difference', 0)

                if difference > 0 and 'equipment' not in table_name.lower():
                    recommendation = {
                        'database': db_name,
                        'table': table_name,
                        'rows': difference,
                        'action': 'MERGE',
                        'value': 'MEDIUM',
                        'risk': 'MEDIUM',
                        'reason': f'{difference} additional rows beyond master'
                    }
                    recommendations['medium_value'].append(recommendation)

                elif 'equipment' in table_name.lower() or 'vehicle' in table_name.lower():
                    recommendation = {
                        'database': db_name,
                        'table': table_name,
                        'rows': table_info['this_db_rows'],
                        'action': 'LINK_ONLY',
                        'value': 'LOW',
                        'risk': 'HIGH',
                        'reason': 'Potential duplicates - use for cross-referencing only'
                    }
                    recommendations['low_value'].append(recommendation)

    return recommendations


def main():
    """Generate comprehensive database analysis report."""

    print("=" * 100)
    print("COMPREHENSIVE DATABASE ANALYSIS")
    print("=" * 100)
    print("\nAnalyzing all databases in project...")
    print("This will take 1-2 minutes...\n")

    all_analyses = {}

    # Analyze each database
    for category, databases in DATABASES.items():
        print(f"\n{category} Databases:")
        all_analyses[category] = {}

        for db_name, db_path_str in databases.items():
            db_path = Path(db_path_str)
            print(f"  Analyzing {db_name}...")

            analysis = analyze_database_schema(db_path)
            all_analyses[category][db_name] = analysis

            if 'error' not in analysis:
                print(f"    - {analysis['table_count']} tables, {analysis['file_size_mb']:.2f} MB")

                # Identify equipment tables
                equipment_tables = find_equipment_tables(analysis)
                if equipment_tables:
                    print(f"    - Equipment tables found: {len(equipment_tables)}")
                    for eq_table in equipment_tables[:3]:
                        print(f"      • {eq_table['table']}: {eq_table['rows']} rows")
            else:
                print(f"    - ERROR: {analysis['error']}")

    # Get master database info
    master_info = all_analyses['ACTIVE']['master_database']

    print("\n\nPerforming cross-database comparisons...")

    # Compare each database to master
    for category, databases in all_analyses.items():
        if category == 'ACTIVE':
            continue

        for db_name, db_info in databases.items():
            if 'error' not in db_info:
                print(f"  Comparing {db_name} to master...")

                # Schema comparison
                comparison = compare_schemas(master_info, db_info, 'master', db_name)
                all_analyses[category][db_name]['comparison_to_master'] = comparison

                # Consolidation value assessment
                value_assessment = assess_consolidation_value(db_info, db_name, master_info)
                all_analyses[category][db_name]['consolidation_value'] = value_assessment

    print("\n\nGenerating consolidation recommendations...")
    recommendations = generate_consolidation_recommendations(all_analyses, master_info)

    # Save detailed analysis to JSON
    output_file = Path("DATABASE_CONSOLIDATION_ANALYSIS.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'analysis': all_analyses,
            'recommendations': recommendations
        }, f, indent=2, default=str)

    print(f"\nDetailed analysis saved to: {output_file}")

    # Generate summary report
    print("\n" + "=" * 100)
    print("CONSOLIDATION RECOMMENDATIONS SUMMARY")
    print("=" * 100)

    print(f"\n📊 HIGH VALUE (Recommended for Import):")
    print(f"   {len(recommendations['high_value'])} items")
    for rec in recommendations['high_value']:
        print(f"   ✅ {rec['database']}.{rec['table']} ({rec['rows']} rows)")
        print(f"      → {rec['reason']}")

    print(f"\n📈 MEDIUM VALUE (Consider Importing):")
    print(f"   {len(recommendations['medium_value'])} items")
    for rec in recommendations['medium_value'][:5]:
        print(f"   ⚠️  {rec['database']}.{rec['table']} ({rec['rows']} rows)")
        print(f"      → {rec['reason']}")
    if len(recommendations['medium_value']) > 5:
        print(f"   ... and {len(recommendations['medium_value']) - 5} more (see JSON for details)")

    print(f"\n📉 LOW VALUE (Cross-reference only):")
    print(f"   {len(recommendations['low_value'])} items")
    for rec in recommendations['low_value'][:3]:
        print(f"   🔗 {rec['database']}.{rec['table']} ({rec['rows']} rows)")
        print(f"      → {rec['reason']}")

    print(f"\n❌ NOT RECOMMENDED:")
    print(f"   {len(recommendations['not_recommended'])} items (empty or duplicate)")

    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    print(f"\nFull details in: {output_file}")
    print("\nNext steps:")
    print("  1. Review the recommendations above")
    print("  2. Check DATABASE_CONSOLIDATION_ANALYSIS.json for full details")
    print("  3. Decide which items to consolidate")
    print("  4. Run selective consolidation script (to be created)")


if __name__ == "__main__":
    main()
