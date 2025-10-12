#!/bin/bash

echo "=== FILE ANALYSIS: data/output/units/ ==="
echo ""

for file in data/output/units/*.json; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "FILE: $(basename "$file")"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Timestamps
    echo "Created: $(stat -c %w "$file" 2>/dev/null || stat -f "%SB" "$file" 2>/dev/null || echo "N/A")"
    echo "Modified: $(stat -c %y "$file" 2>/dev/null || stat -f "%Sm" "$file" 2>/dev/null)"
    echo "Size: $(stat -c %s "$file" 2>/dev/null || stat -f "%z" "$file" 2>/dev/null) bytes"
    echo ""

    # Schema check
    echo "Schema fields:"
    head -30 "$file" | grep -E "(\"schema|\"nation\"|\"quarter\"|\"unit_designation\"|\"unit_type\"|\"organization_level\")" | head -5
    echo ""
    echo ""
done
