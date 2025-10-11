# Structured TO&E Extraction Workflow

## Phase 1: Source Identification & Search

### Step 1.1: Determine Source Type
Based on nation, select appropriate source:
- **German units** → Tessin Wehrmacht Encyclopedia (17 volumes, gzipped text)
- **British/Commonwealth** → British Army Lists (quarterly, gzipped text)
- **Italian units** → TME 30-420 Italian Military Forces Handbook
- **US units** → US Field Manuals (FM 7-20, FM 17-10, etc.)
- **French units** → Web search (Tier 2/3) - no local sources yet

### Step 1.2: Search Pattern
```bash
# German units - search Tessin volumes
cd "Resource Documents/tessin-georg-verbande..."
zgrep -i "[unit designation]" *.gz

# British units - search Army Lists for specific quarter
cd "Resource Documents/Great Britain Ministery of Defense Books"
zgrep -i "[unit designation]" armylist[quarter]*.gz

# Italian units - search TME 30-420
cd "Resource Documents"
zgrep -i "[unit designation]" TME_30_420*.gz
```

### Step 1.3: Extract Relevant Sections
Once found, extract with context:
```bash
zgrep -B10 -A100 "^[Unit Designation]" [source_file.gz] > temp_extract.txt
```

## Phase 2: Data Extraction & Interpretation

### Step 2.1: Parse Tessin Entry Format
Standard Tessin entry structure:
```
[Unit Name] * [Date] [Location] [WK]
[Historical narrative]
G: [Gliederung - Organization]
U: [Unterstellung - Chain of Command by date]
E: [Ersatzgestellung - Replacement station]
```

### Step 2.2: Extract Key Data Points

**Required Fields:**
1. **Unit Designation** (preserve original language)
2. **Formation Date** & **Disbandment/Redesignation Date**
3. **Commander Name & Rank** (from narrative)
4. **Parent Unit** (from U: section)
5. **Subordinate Units** (from G: section)
6. **Time Period** (match to quarter: Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)

**Personnel & Equipment:**
- Extract from narrative or cross-reference with Band 01 (organizational tables)
- Look for phrases like "zu X Btl." (with X battalions)
- Equipment numbers often in parentheses or specific sections

### Step 2.3: Abbreviation Decoding
Use `data/tessin_abbreviations.md` to decode:
- Inf.Rgt. → Infantry Regiment
- Pz.Abt. → Panzer Battalion
- Art.Rgt. → Artillery Regiment
- Etc.

## Phase 3: Data Structuring

### Step 3.1: Map to Unified TO&E Schema
```json
{
  "nation": "Germany|Italy|Britain|USA|France",
  "quarter": "YYYY-QN",
  "unit_designation": "[Original language]",
  "organization_level": "Theater|Corps|Division|Regiment|Battalion|Company|Platoon|Squad",
  "commander": {
    "name": "...",
    "rank": "..."
  },
  "parent_unit": "...",
  "subordinate_units": [...],
  "personnel": {
    "total": 0,
    "officers": 0,
    "ncos": 0,
    "enlisted": 0
  },
  "equipment": {
    "tanks": {"total": 0, "heavy": 0, "medium": 0, "light": 0},
    "artillery": {"total": 0, "field": 0, "anti_tank": 0, "anti_aircraft": 0},
    "ground_vehicles": {"total": 0, "trucks": 0, "cars": 0, "motorcycles": 0},
    "aircraft": {"total": 0}
  },
  "metadata": {
    "confidence_score": 0-100,
    "source_tier": 1|2|3,
    "primary_source": "Tessin Band X",
    "extraction_date": "YYYY-MM-DD",
    "notes": "..."
  }
}
```

### Step 3.2: Calculate Totals
- **Bottom-up aggregation**: Squad → Platoon → Company → Battalion → Regiment → Division → Corps → Theater
- Validate: Parent total ≈ sum of children (±5%)
- If equipment data missing at subordinate level, estimate from known TO&E tables

### Step 3.3: Assign Confidence Scores
- **90-100%**: Primary source with complete data (Tessin, Army Lists)
- **75-89%**: Primary source with some gaps filled by estimation
- **60-74%**: Secondary web sources (Feldgrau, Niehorster)
- **<60%**: Tertiary sources or heavy estimation

## Phase 4: Validation

### Step 4.1: Schema Validation
Check against `schemas/unified_toe_schema.json`:
- All required fields present
- Data types correct
- Relationships valid (parent/child)

### Step 4.2: Historical Accuracy
- Commander name/rank matches time period
- Unit location matches known campaigns
- Equipment types available in that time period
- Cross-reference multiple sources when possible

### Step 4.3: Mathematical Validation
- `tanks.total = heavy + medium + light`
- `total_personnel ≈ officers + ncos + enlisted (±5%)`
- `parent_total ≈ sum(all_children_totals) (±5%)`

## Phase 5: Output Generation

### Step 5.1: Save JSON File
```
data/output/units/[nation]_[quarter]_[unit_designation]_toe.json
```

### Step 5.2: Insert into SQLite
```sql
INSERT INTO units (nation, quarter, unit_designation, unit_type, ...)
VALUES (...);

INSERT INTO extraction_log (unit_id, phase, agent_id, status, ...)
VALUES (...);

INSERT INTO source_citations (unit_id, fact_type, fact_value, source_name, ...)
VALUES (...);
```

### Step 5.3: Git Commit
Every 10 units processed:
```bash
git add data/output/units/*.json
git commit -m "Extract [N] units: [list]"
```

## Example: Processing 5. leichte Division 1941-Q1

### Search
```bash
zgrep -i "5.*leichte.*Division" tessin-band-*.gz
```

### Extract
Found in Band 05, search for:
- Formation date: 15.1.1941 (January 15, 1941 = 1941-Q1 ✓)
- Renamed: 1.8.1941 to 21. Panzer-Division (August 1, 1941 = 1941-Q3)
- Location: Libya/North Africa
- Parent: Deutsches Afrikakorps

### Parse
- G: section lists subordinate regiments/battalions
- U: section shows chain of command (Dt. Afrika-Korps)
- Commander: Extract from narrative (likely Rommel at corps level)

### Structure
- Map to unified schema
- Fill equipment from known light division TO&E (Band 01)
- Calculate totals

### Validate
- Cross-reference with 21. Panzer-Division entry (should show "formerly 5. leichte")
- Check Band 01 for light division standard organization

### Save
- JSON to `germany_1941q1_5_leichte_division_toe.json`
- SQLite insert
- Git commit

## Common Challenges & Solutions

### Challenge: Data Scattered Across Volumes
**Solution**: Search all volumes, cross-reference Band 01 for organizational structure

### Challenge: Equipment Numbers Not Explicit
**Solution**:
1. Check Band 01 for standard TO&E tables for that division type
2. Cross-reference subordinate unit entries
3. Use known equipment allocations from that time period
4. Mark as "estimated" in metadata

### Challenge: Abbreviations Unclear
**Solution**: Use `data/tessin_abbreviations.md` + context clues

### Challenge: Date Ranges Span Multiple Quarters
**Solution**: Create separate entries for each quarter the unit existed

### Challenge: Commander Names Missing
**Solution**:
1. Search parent/child unit entries
2. Check historical databases (Lexikon der Wehrmacht online)
3. Mark as "Unknown" if not found

## Quality Checklist

Before finalizing each unit, verify:
- [ ] Unit designation in original language
- [ ] Date matches quarter (Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec)
- [ ] Parent unit identified
- [ ] Subordinate units listed
- [ ] Commander name & rank (or marked "Unknown")
- [ ] Personnel totals reasonable for unit type
- [ ] Equipment totals sum correctly
- [ ] Confidence score assigned based on source quality
- [ ] Source citations recorded
- [ ] JSON validates against schema
- [ ] SQLite insert successful
- [ ] File saved with correct naming convention
