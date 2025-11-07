# OCR Scraper Architecture for BattleGroup DataCards

**Date**: November 5, 2025
**Purpose**: Future-proof design for OCR-based data extraction from BattleGroup PDFs
**Scope**: Automated extraction to replace manual CSV entry

---

## Problem Statement

**Current Process**: Manual CSV entry
- User views PDF datacard → types values into Excel → saves CSV → imports to database
- Time: ~5 minutes per vehicle, ~3 minutes per gun
- Error-prone: OCR issues in source PDFs, typos during entry
- Not scalable: 500+ vehicles, 100+ guns across all nations

**Desired Process**: Automated OCR extraction
- Script reads PDF → OCR extracts text → parser validates → direct database import
- Time: ~10 seconds per datacard (50x faster)
- Consistent: Same parser logic as manual CSV import
- Scalable: Process entire nation in minutes

---

## Architecture Overview

### Three-Stage Pipeline

```
Stage 1: PDF Extraction
├─ Input: BattleGroup PDF (Canada's Crucible.pdf, British DataCards.pdf, etc.)
├─ Process: Page segmentation, image preprocessing, OCR
└─ Output: Raw text blocks with coordinates

Stage 2: Datacard Parsing
├─ Input: Raw OCR text blocks
├─ Process: Pattern matching, field extraction, normalization
└─ Output: Structured JSON (one per datacard)

Stage 3: Database Import
├─ Input: Structured JSON
├─ Process: Validation (reuse GUN_IMPORT_VALIDATION_SPEC.md logic)
└─ Output: Database records + validation log
```

### Technology Stack

**OCR Engine**: Multiple options
- **Tesseract 5.x** (open source, good accuracy)
- **pdf2image + Tesseract** (PDF → images → text)
- **pdfplumber** (text extraction for searchable PDFs)
- **Azure Computer Vision** (cloud API, highest accuracy, costs money)

**Recommendation**: Tesseract 5.x (already used in project, proven results)

**Python Libraries**:
- `pdf2image` - Convert PDF pages to images
- `pytesseract` - Python wrapper for Tesseract
- `Pillow (PIL)` - Image preprocessing
- `opencv-python` - Advanced image manipulation
- `re` - Regex pattern matching
- `json` - Structured output
- `sqlite3` - Database import

---

## Stage 1: PDF Extraction

### Page Segmentation

**BattleGroup datacard layout** (3x2 grid per page):
```
┌─────────────┬─────────────┬─────────────┐
│  Card 1     │  Card 2     │  Card 3     │
│  (top-left) │  (top-mid)  │  (top-right)│
├─────────────┼─────────────┼─────────────┤
│  Card 4     │  Card 5     │  Card 6     │
│  (bot-left) │  (bot-mid)  │  (bot-right)│
└─────────────┴─────────────┴─────────────┘
```

**Segmentation Algorithm**:
```python
def segment_datacard_page(pdf_page_image):
    """
    Split A4 landscape page into 3x2 grid of individual datacards.
    Returns: List of 6 card images (PIL Image objects)
    """
    width, height = pdf_page_image.size

    # A4 landscape: ~297mm x 210mm at 300 DPI = 3508 x 2480 pixels
    # Each card: ~1169 x 1240 pixels (width x height)

    card_width = width // 3
    card_height = height // 2

    cards = []
    for row in range(2):
        for col in range(3):
            left = col * card_width
            upper = row * card_height
            right = left + card_width
            lower = upper + card_height

            card_image = pdf_page_image.crop((left, upper, right, lower))
            cards.append(card_image)

    return cards  # 6 card images
```

### Image Preprocessing

**OCR accuracy depends on image quality**. Apply preprocessing:

```python
def preprocess_for_ocr(image):
    """
    Enhance image for better OCR accuracy.
    """
    import cv2
    import numpy as np

    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 1. Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Noise reduction
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # 3. Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 4. Binarization (Otsu's method)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5. Morphological operations (remove small noise)
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return cleaned  # Return preprocessed image
```

### OCR Execution

```python
def extract_text_from_card(card_image):
    """
    Run Tesseract OCR on preprocessed card image.
    Returns: Raw text string
    """
    import pytesseract

    # Preprocess image
    preprocessed = preprocess_for_ocr(card_image)

    # Tesseract configuration
    # --psm 6: Assume uniform block of text
    # --oem 3: Use LSTM neural net mode (Tesseract 4+)
    custom_config = r'--psm 6 --oem 3'

    # Extract text
    text = pytesseract.image_to_string(preprocessed, config=custom_config)

    return text
```

---

## Stage 2: Datacard Parsing

### Field Extraction Patterns

**BattleGroup datacard structure** (vehicles):
```
[Vehicle Name]                    Points: 35   BR: 2
────────────────────────────────────────────────────
Type: AFV                         Crew: 4
Speed: 12"/18"                    Special: Open-topped
Armour: Front 2, Side 1, Rear 1, Top 0

ARMAMENT:
────────────────────────────────────────────────────
37mm M6 gun                       HE: D6/4+   AP: 4/4/3/2/1/-
.30 cal MMG (co-ax)              HE: -       AP: -
```

**Parsing Strategy**: Line-by-line regex patterns

```python
def parse_vehicle_datacard(ocr_text):
    """
    Extract structured data from OCR text.
    Returns: dict with vehicle fields
    """
    import re

    vehicle = {}

    # Line 1: Name + Points + BR
    match = re.search(r'^(.+?)\s+Points:\s*(\d+)\s+BR:\s*(\d+)', ocr_text, re.MULTILINE)
    if match:
        vehicle['name'] = match.group(1).strip()
        vehicle['points_cost'] = int(match.group(2))
        vehicle['battle_rating'] = int(match.group(3))

    # Type
    match = re.search(r'Type:\s*(.+?)(?:\s+Crew:|$)', ocr_text)
    if match:
        vehicle['vehicle_type'] = match.group(1).strip()

    # Crew
    match = re.search(r'Crew:\s*(\d+)', ocr_text)
    if match:
        vehicle['crew'] = int(match.group(1))

    # Speed (two values: slow/fast)
    match = re.search(r'Speed:\s*(\d+)"/(\d+)"', ocr_text)
    if match:
        vehicle['movement_slow'] = int(match.group(1))
        vehicle['movement_fast'] = int(match.group(2))

    # Special rules
    match = re.search(r'Special:\s*(.+?)(?:\n|$)', ocr_text)
    if match:
        vehicle['special_rules'] = match.group(1).strip()

    # Armor values
    match = re.search(r'Armour:\s*Front\s*(\d+),\s*Side\s*(\d+),\s*Rear\s*(\d+),\s*Top\s*(\d+)', ocr_text)
    if match:
        vehicle['armor_front'] = int(match.group(1))
        vehicle['armor_side'] = int(match.group(2))
        vehicle['armor_rear'] = int(match.group(3))
        vehicle['armor_top'] = int(match.group(4))

    # Armament (multi-line, complex parsing)
    vehicle['weapons'] = parse_armament_section(ocr_text)

    return vehicle
```

### Armament Parsing (Complex)

**Weapons have multiple formats**:
- Main gun: `37mm M6 gun    HE: D6/4+   AP: 4/4/3/2/1/-`
- MG: `.30 cal MMG (co-ax)   HE: -   AP: -`
- Flamethrower: `Wasp flamethrower   HE: D6   AP: -`

```python
def parse_armament_section(ocr_text):
    """
    Extract all weapons from armament section.
    Returns: List of weapon dicts
    """
    weapons = []

    # Find armament section
    armament_match = re.search(r'ARMAMENT:(.+?)(?:\n\n|$)', ocr_text, re.DOTALL)
    if not armament_match:
        return weapons

    armament_text = armament_match.group(1)

    # Split into weapon lines
    weapon_lines = [line.strip() for line in armament_text.split('\n')
                    if line.strip() and '────' not in line]

    for line in weapon_lines:
        weapon = parse_weapon_line(line)
        if weapon:
            weapons.append(weapon)

    return weapons


def parse_weapon_line(line):
    """
    Parse single weapon line.
    Example: "37mm M6 gun    HE: D6/4+   AP: 4/4/3/2/1/-"
    """
    weapon = {}

    # Split by HE/AP markers
    parts = re.split(r'\s+(HE:|AP:)', line)

    # Part 0: Weapon name
    weapon['name'] = parts[0].strip()

    # Extract HE data
    he_match = re.search(r'HE:\s*([\dD/\+\-]+)', line)
    if he_match:
        he_value = he_match.group(1).strip()
        if he_value != '-':
            # Parse "D6/4+" format
            if '/' in he_value:
                dice, target = he_value.split('/')
                weapon['he_dice'] = dice
                weapon['he_target'] = target
            else:
                weapon['he_dice'] = he_value

    # Extract AP data
    ap_match = re.search(r'AP:\s*([\d/\-]+)', line)
    if ap_match:
        ap_value = ap_match.group(1).strip()
        if ap_value != '-':
            # Parse "4/4/3/2/1/-" format (6 range bands)
            ap_values = ap_value.split('/')
            weapon['ap_0_10'] = parse_ap_value(ap_values[0]) if len(ap_values) > 0 else None
            weapon['ap_10_20'] = parse_ap_value(ap_values[1]) if len(ap_values) > 1 else None
            weapon['ap_20_30'] = parse_ap_value(ap_values[2]) if len(ap_values) > 2 else None
            weapon['ap_30_40'] = parse_ap_value(ap_values[3]) if len(ap_values) > 3 else None
            weapon['ap_40_50'] = parse_ap_value(ap_values[4]) if len(ap_values) > 4 else None
            weapon['ap_50_70'] = parse_ap_value(ap_values[5]) if len(ap_values) > 5 else None

    return weapon


def parse_ap_value(value):
    """Handle AP values: numbers, '-', or empty."""
    value = value.strip()
    if value == '-' or value == '':
        return None
    return int(value)
```

### OCR Error Correction

**Common OCR mistakes**:
- `O` (letter O) → `0` (zero)
- `l` (lowercase L) → `1` (one)
- `I` (uppercase I) → `1` (one)
- `S` → `5` (sometimes)
- `B` → `8` (sometimes)
- `.` (period) → `,` (comma) or missing
- `"` (inch symbol) → `'` (foot) or missing

```python
def ocr_error_correction(text):
    """
    Apply common OCR error corrections.
    """
    corrections = {
        # Armor values commonly misread
        r'Armour: Front O': 'Armour: Front 0',  # O → 0
        r'Front l,': 'Front 1,',  # l → 1
        r'Side l,': 'Side 1,',
        r'Rear l,': 'Rear 1,',

        # Speed misreads
        r'Speed: l2': 'Speed: 12',  # l → 1
        r'Speed: lB': 'Speed: 18',  # l → 1, B → 8

        # Points/BR misreads
        r'Points: O': 'Points: 0',  # O → 0
        r'BR: O': 'BR: 0',
    }

    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text)

    return text
```

---

## Stage 3: Database Import

### Validation Integration

**Reuse existing validation logic** from `GUN_IMPORT_VALIDATION_SPEC.md`:

```python
from import_british_datacards_guns import (
    parse_numeric_field,
    normalize_nation,
    validate_critical_fields,
    auto_detect_weapon_category
)

def import_ocr_extracted_gun(gun_json):
    """
    Import gun extracted from OCR.
    Uses same validation as manual CSV import.
    """
    # Normalize fields
    gun = {
        'name': gun_json['name'],
        'nation': normalize_nation(gun_json.get('nation', 'british')),
        'caliber_mm': parse_numeric_field(gun_json['caliber_mm'], 'caliber_mm'),
        'he_dice': parse_numeric_field(gun_json['he_dice'], 'he_dice'),
        'ap_0_10': parse_numeric_field(gun_json['ap_0_10'], 'ap_0_10'),
        # ... other fields
    }

    # Validate critical fields
    errors = validate_critical_fields(gun)
    if errors:
        log_error(f"OCR_VALIDATION_FAILED: {gun['name']}, errors={errors}")
        return False

    # Auto-detect weapon category
    gun['weapon_category'] = auto_detect_weapon_category(gun)

    # Insert to database
    insert_gun_to_database(gun)

    return True
```

### Quality Assurance

**OCR confidence scoring**:
```python
def assess_ocr_quality(ocr_text, parsed_data):
    """
    Score OCR extraction quality (0-100).
    """
    score = 100

    # Deduct for missing critical fields
    if not parsed_data.get('name'):
        score -= 50  # CRITICAL
    if not parsed_data.get('caliber_mm'):
        score -= 30  # CRITICAL
    if not parsed_data.get('nation'):
        score -= 20

    # Deduct for suspicious patterns
    if 'O' in ocr_text and '0' in str(parsed_data.get('armor_front', '')):
        score -= 5  # Possible O/0 confusion
    if re.search(r'[^a-zA-Z0-9\s\.,\-\+/"\']', ocr_text):
        score -= 10  # Garbage characters

    # Deduct for partial data
    armor_fields = [parsed_data.get(f'armor_{side}') for side in ['front', 'side', 'rear', 'top']]
    if None in armor_fields:
        score -= 15  # Missing armor values

    return max(0, score)  # Clamp to 0-100
```

**Post-import review**:
```python
def flag_for_manual_review(vehicle):
    """
    Determine if OCR extraction needs human verification.
    """
    review_reasons = []

    # Check OCR quality score
    if vehicle['ocr_quality_score'] < 70:
        review_reasons.append("Low OCR quality")

    # Check for unusual values
    if vehicle.get('points_cost', 0) > 500:
        review_reasons.append("Unusually high points cost")

    if vehicle.get('armor_front', 0) > 15:
        review_reasons.append("Unusually high armor (possible OCR error)")

    # Check for missing critical data
    if not vehicle.get('weapons'):
        review_reasons.append("No weapons extracted")

    return review_reasons  # Empty list = no review needed
```

---

## Full Pipeline Script

### Main Execution Flow

```python
import sys
import sqlite3
from pdf2image import convert_from_path
import pytesseract
import json

def extract_datacards_from_pdf(pdf_path, nation='british'):
    """
    Complete pipeline: PDF → OCR → Parse → Validate → Import
    """
    print(f"[*] Processing PDF: {pdf_path}")

    # Stage 1: Convert PDF to images
    print("[*] Converting PDF pages to images...")
    pages = convert_from_path(pdf_path, dpi=300)
    print(f"[+] Extracted {len(pages)} pages")

    all_vehicles = []
    all_guns = []

    # Process each page
    for page_num, page_image in enumerate(pages, start=1):
        print(f"\n[*] Processing page {page_num}/{len(pages)}")

        # Segment page into 3x2 grid
        cards = segment_datacard_page(page_image)

        # Process each card
        for card_num, card_image in enumerate(cards, start=1):
            print(f"  [*] Card {card_num}/6")

            # Run OCR
            ocr_text = extract_text_from_card(card_image)

            # Apply error correction
            corrected_text = ocr_error_correction(ocr_text)

            # Determine card type (vehicle vs gun)
            if is_vehicle_card(corrected_text):
                vehicle = parse_vehicle_datacard(corrected_text)
                vehicle['nation'] = nation
                vehicle['ocr_text'] = corrected_text
                vehicle['ocr_quality_score'] = assess_ocr_quality(corrected_text, vehicle)
                all_vehicles.append(vehicle)
                print(f"    [+] Vehicle: {vehicle.get('name', 'UNKNOWN')}")
            else:
                gun = parse_gun_datacard(corrected_text)
                gun['nation'] = nation
                gun['ocr_text'] = corrected_text
                gun['ocr_quality_score'] = assess_ocr_quality(corrected_text, gun)
                all_guns.append(gun)
                print(f"    [+] Gun: {gun.get('name', 'UNKNOWN')}")

    # Stage 3: Import to database
    print(f"\n[*] Importing {len(all_vehicles)} vehicles and {len(all_guns)} guns...")

    success_count = 0
    review_count = 0

    for vehicle in all_vehicles:
        if import_ocr_extracted_vehicle(vehicle):
            success_count += 1

            # Check if review needed
            review_reasons = flag_for_manual_review(vehicle)
            if review_reasons:
                review_count += 1
                print(f"[!] REVIEW: {vehicle['name']} - {', '.join(review_reasons)}")

    for gun in all_guns:
        if import_ocr_extracted_gun(gun):
            success_count += 1

            review_reasons = flag_for_manual_review(gun)
            if review_reasons:
                review_count += 1
                print(f"[!] REVIEW: {gun['name']} - {', '.join(review_reasons)}")

    print(f"\n[+] Import complete: {success_count} items imported")
    print(f"[!] Manual review required: {review_count} items")

    # Export flagged items to JSON
    if review_count > 0:
        export_for_review(all_vehicles + all_guns, 'ocr_review_needed.json')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ocr_extract_datacards.py <pdf_path> [nation]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    nation = sys.argv[2] if len(sys.argv) > 2 else 'british'

    extract_datacards_from_pdf(pdf_path, nation)
```

---

## Testing Strategy

### Validation Against Manual CSV

**Process**:
1. Run OCR extraction on British DataCards PDF
2. Run manual CSV import on british_datacards_ALL_VEHICLES.csv
3. Compare results field-by-field

**Metrics**:
- **Accuracy**: % of fields matching exactly
- **Recall**: % of cards successfully extracted
- **Precision**: % of extracted data correct

**Expected Results** (based on similar OCR projects):
- Name accuracy: 95%+ (high confidence)
- Numeric fields: 90%+ (armor, points, BR)
- Weapons: 85%+ (complex multi-line parsing)
- Special rules: 80%+ (free-text, variable formatting)

### Iterative Improvement

**Feedback loop**:
1. Run OCR extraction
2. Manual review of flagged items
3. Identify common error patterns
4. Update regex patterns or error correction rules
5. Re-run extraction
6. Measure improvement

**Example improvement cycle**:
- **Iteration 1**: 80% accuracy, 30% flagged for review
- **Update**: Add "Armour:" → "Armor:" normalization
- **Iteration 2**: 85% accuracy, 20% flagged
- **Update**: Fix AP value parsing ("-" handling)
- **Iteration 3**: 90% accuracy, 10% flagged (acceptable)

---

## Scalability Considerations

### Batch Processing

**Process multiple nations**:
```bash
python ocr_extract_datacards.py "Resource Documents/Battlegroup Game/British DataCards.pdf" british
python ocr_extract_datacards.py "Resource Documents/Battlegroup Game/German DataCards.pdf" german
python ocr_extract_datacards.py "Resource Documents/Battlegroup Game/Italian DataCards.pdf" italian
python ocr_extract_datacards.py "Resource Documents/Battlegroup Game/American DataCards.pdf" american
```

**Expected processing time** (per nation):
- PDF pages: 10-20 pages
- Cards per page: 6
- Total cards: 60-120
- OCR time: ~2-3 seconds per card
- Total time: 3-6 minutes per nation
- All 4 nations: 15-25 minutes (vs 4-8 hours manual entry)

### Parallelization

**Speed improvement** (multi-core processing):
```python
from multiprocessing import Pool

def process_card_parallel(card_data):
    """Process single card (OCR + parse)."""
    card_image, card_id = card_data
    ocr_text = extract_text_from_card(card_image)
    parsed = parse_vehicle_datacard(ocr_text)
    return parsed

def extract_datacards_parallel(pdf_path):
    """Process all cards in parallel."""
    pages = convert_from_path(pdf_path, dpi=300)

    all_cards = []
    for page in pages:
        cards = segment_datacard_page(page)
        all_cards.extend([(card, idx) for idx, card in enumerate(cards)])

    # Process cards in parallel (4-8 workers)
    with Pool(processes=4) as pool:
        results = pool.map(process_card_parallel, all_cards)

    return results  # All parsed datacards
```

**Expected speedup**: 3-4x faster (2-4 minutes per nation)

---

## Future Enhancements

### Machine Learning-Based OCR

**If accuracy < 90%**:
- Train custom Tesseract model on BattleGroup datacard font
- Use Azure Computer Vision API (99%+ accuracy, but costs $1-2 per 1000 images)
- Fine-tune BERT model on BattleGroup text patterns

### Layout Detection

**Current approach**: Fixed 3x2 grid assumption
**Enhanced approach**: Dynamic layout detection
- Detect card boundaries using contour detection
- Handle variable page layouts (some supplements have 2x2 or 4x2 grids)
- Detect section headers (ARMAMENT, SPECIAL RULES) automatically

### Multi-Language Support

**German datacards** (different text patterns):
- "Panzerung:" instead of "Armour:"
- "Geschwindigkeit:" instead of "Speed:"
- Metric values (km/h instead of inches)

**Solution**: Language-specific regex patterns, auto-detect language

---

**Status**: Architecture designed, ready for implementation
**Estimated Effort**: 8-12 hours (implementation + testing)
**ROI**: Saves 20-40 hours of manual entry across all nations
