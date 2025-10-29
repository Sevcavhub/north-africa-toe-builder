#!/bin/bash

# Search for air force related content in Nafziger PDFs
# Focus on Italian and British sources with strength data

DIR="D:/north-africa-toe-builder/Resource Documents/Nafziger Collection/WWII/1941-1942/Pt_I_1941-1942"

echo "Searching Italian PDFs for Regia Aeronautica units..."
echo ""

cd "$DIR"

for file in 941i*.pdf 942i*.pdf; do
    if [ -f "$file" ]; then
        text=$(pdftotext "$file" - 2>/dev/null)
        if echo "$text" | grep -qiE "(stormo|gruppo.*caccia|gruppo.*bomba|squadriglia|regia aeronautica)"; then
            # Check if it has strength numbers
            if echo "$text" | grep -qE "[0-9]+.*aircraft|[0-9]+/[0-9]+"; then
                echo "✅ $file (has strength data)"
                echo "$text" | grep -iE "(stormo|gruppo)" | head -2
                echo ""
            else
                echo "⚠️  $file (structure only, no strength)"
            fi
        fi
    fi
done

echo ""
echo "Searching British PDFs for RAF units..."
echo ""

for file in 941b*.pdf 942b*.pdf; do
    if [ -f "$file" ]; then
        text=$(pdftotext "$file" - 2>/dev/null)
        if echo "$text" | grep -qiE "(squadron|wing.*air|desert air force|raf|saaf.*squadron)"; then
            # Check if it has strength numbers
            if echo "$text" | grep -qE "squadron.*[0-9]+.*aircraft"; then
                echo "✅ $file (has strength data)"
                echo "$text" | grep -iE "squadron" | head -2
                echo ""
            else
                echo "⚠️  $file (structure only, no strength)"
            fi
        fi
    fi
done
