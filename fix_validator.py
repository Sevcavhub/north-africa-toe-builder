#!/usr/bin/env python3
"""
Fix validator.js quarter format check
Changes from 1943-Q1 format to 1943q1 format
"""

# Read the file
with open('scripts/lib/validator.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 52 (0-indexed line 51) - the regex pattern
if len(lines) > 51:
    old_regex = r"if (quarter !== 'unknown' && !/^\d{4}-Q[1-4]$/.test(quarter)) {"
    new_regex = r"if (quarter !== 'unknown' && !/^\d{4}q[1-4]$/.test(quarter)) {"
    lines[51] = lines[51].replace(old_regex, new_regex)

# Fix line 53 (0-indexed line 52) - the error message
if len(lines) > 52:
    old_msg = 'Quarter format should be YYYY-QN'
    new_msg = 'Quarter format should be yyyyqn (e.g., 1943q1)'
    lines[52] = lines[52].replace(old_msg, new_msg)

# Write back
with open('scripts/lib/validator.js', 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(lines)

print('Validator updated successfully')
print(f'Line 52: {lines[51].strip()}')
print(f'Line 53: {lines[52].strip()}')
