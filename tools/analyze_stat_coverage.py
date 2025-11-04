#!/usr/bin/env python3
"""
Analyze BattleGroup stat coverage by category
"""

import sqlite3
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "database" / "master_database.db"

conn = sqlite3.connect(str(DB_PATH))

# Get coverage by category
query = """
SELECT
    em.equipment_category,
    COUNT(*) as total,
    SUM(CASE WHEN esb.armor_front IS NOT NULL THEN 1 ELSE 0 END) as armor_count,
    SUM(CASE WHEN esb.movement_offroad IS NOT NULL THEN 1 ELSE 0 END) as movement_count,
    SUM(CASE WHEN esb.weapon_description IS NOT NULL THEN 1 ELSE 0 END) as weapon_count,
    SUM(CASE WHEN esb.points IS NOT NULL THEN 1 ELSE 0 END) as points_count
FROM equipment_master_new em
JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
JOIN equipment_stats_battlegroup esb ON em.master_id = esb.master_id
WHERE etu.theater = 'north_africa'
GROUP BY em.equipment_category
ORDER BY total DESC
"""

print("=" * 100)
print("BATTLEGROUP STAT COVERAGE BY CATEGORY")
print("=" * 100)

print(f"{'Category':<20} {'Total':>6} {'Armor':>10} {'Movement':>10} {'Weapons':>10} {'Points/BR':>10}")
print("-" * 100)

totals = {'total': 0, 'armor': 0, 'movement': 0, 'weapon': 0, 'points': 0}

for row in conn.execute(query):
    cat, total, armor, movement, weapon, points = row

    totals['total'] += total
    totals['armor'] += armor
    totals['movement'] += movement
    totals['weapon'] += weapon
    totals['points'] += points

    armor_pct = f"{armor}/{total} ({armor*100/total:.0f}%)" if total > 0 else "0/0"
    movement_pct = f"{movement}/{total} ({movement*100/total:.0f}%)" if total > 0 else "0/0"
    weapon_pct = f"{weapon}/{total} ({weapon*100/total:.0f}%)" if total > 0 else "0/0"
    points_pct = f"{points}/{total} ({points*100/total:.0f}%)" if total > 0 else "0/0"

    print(f"{cat:<20} {total:>6} {armor_pct:>10} {movement_pct:>10} {weapon_pct:>10} {points_pct:>10}")

print("-" * 100)

armor_pct = f"{totals['armor']}/{totals['total']} ({totals['armor']*100/totals['total']:.1f}%)"
movement_pct = f"{totals['movement']}/{totals['total']} ({totals['movement']*100/totals['total']:.1f}%)"
weapon_pct = f"{totals['weapon']}/{totals['total']} ({totals['weapon']*100/totals['total']:.1f}%)"
points_pct = f"{totals['points']}/{totals['total']} ({totals['points']*100/totals['total']:.1f}%)"

print(f"{'TOTAL':<20} {totals['total']:>6} {armor_pct:>10} {movement_pct:>10} {weapon_pct:>10} {points_pct:>10}")

# Sample items without weapons
print("\n" + "=" * 100)
print("SAMPLE ITEMS WITHOUT WEAPONS (First 20)")
print("=" * 100)

query2 = """
SELECT em.master_id, em.display_name, em.equipment_category
FROM equipment_master_new em
JOIN equipment_theater_usage etu ON em.master_id = etu.master_id
JOIN equipment_stats_battlegroup esb ON em.master_id = esb.master_id
WHERE etu.theater = 'north_africa'
AND esb.weapon_description IS NULL
ORDER BY em.master_id
LIMIT 20
"""

for row in conn.execute(query2):
    master_id, display_name, category = row
    print(f"  [{master_id}] {display_name} ({category})")

conn.close()
