#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Examine Excel template for new schema"""

import sys
import io
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_file = r"D:\north-africa-toe-builder\Resource Documents\Battlegroup Game\Vehicles Tobruk Input form for OCR.xlsx"

# Read Excel file
df = pd.read_excel(excel_file)

print("=" * 100)
print("EXCEL TEMPLATE SCHEMA")
print("=" * 100)
print(f"\nTotal columns: {len(df.columns)}\n")

print("Column order (left to right):")
print("-" * 100)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {col}")

print("\n" + "=" * 100)
print("SAMPLE DATA (first 3 rows)")
print("=" * 100)
print(df.head(3).to_string())

print("\n" + "=" * 100)
print("DATA TYPES")
print("=" * 100)
print(df.dtypes.to_string())
