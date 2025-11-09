# Chapter Generator Usage Guide

**Script**: `scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py`

**Created**: November 9, 2025

## Overview

The hybrid chapter template generator automates creation of comprehensive MDBook chapters from Phase 6 unit JSON files. It combines:
- **Auto-populated sections**: Equipment, organization, personnel (from JSON data)
- **Manual placeholders**: Historical narrative, tactical analysis, combat assessment

This approach accelerates chapter expansion from stubs to publication-ready quality.

## Features

### Auto-Populated Sections
The script automatically populates from JSON data:
- Personnel strength (officers, NCOs, enlisted with percentages)
- Command structure (commander names, ranks, HQ locations)
- Organization (subordinate units with strengths)
- Equipment (weapons, vehicles, artillery with counts)
- Supply status (fuel, ammunition, water, operational radius)
- Weather/environment (climate, terrain, challenges)
- Data quality (sources, confidence, gaps)

### Manual Placeholders
Historical sections require manual research/writing:
- Overview (2-3 paragraphs historical context)
- Commander biography
- Personnel quality assessment
- Combat history and engagements
- Tactical doctrine analysis
- Historical significance

### Output Format
- 14-section comprehensive structure
- 400-500+ lines per chapter
- Matches publication-quality standard
- Clear `[MANUAL: ...]` markers for required work

## Usage

### List All Stub Chapters
Find chapters needing expansion (<50 lines):

```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py --list-stubs
```

**Output:**
```
Finding stub chapters (<50 lines)...

Found 127 stub chapters:

  chapter_american_1942q4_1st_armored_division.md (16 lines)
  chapter_british_1940q2_7th_armoured_division.md (16 lines)
  ...
```

### Generate Single Chapter
Create template for one specific unit:

```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py "british_1940q2_7th_armoured_division_toe.json"
```

**With overwrite** (replace existing):
```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py "british_1940q2_7th_armoured_division_toe.json" --overwrite
```

### Process All Units
Generate chapters for all 402 unit JSON files:

```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py --all
```

**Overwrite all existing chapters:**
```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py --all --overwrite
```

### Process Only Stubs
Expand only stub chapters (<50 lines), skip comprehensive chapters:

```bash
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py --stub-only
```

**This is the recommended approach** for the 114-127 stub chapters needing expansion.

## Workflow

### Recommended Process

**Phase 1**: Generate stub templates
```bash
# Generate templates for all stub chapters
python scripts/phase_6_ground_forces/content_generation/generate_comprehensive_chapter.py --stub-only --overwrite
```

**Output**: 127 chapters expanded from 16 lines to 400-500 lines with data and placeholders

**Phase 2**: Manual enhancement (prioritized)

1. **High-Value Divisions** (32 chapters):
   - 7th Armoured Division (Desert Rats)
   - 4th Indian Division
   - 2nd New Zealand Division
   - 15th Panzer Division
   - 21st Panzer Division
   - Ariete Division
   - Littorio Division
   - 1st Armored Division (US)
   - etc.

2. **Remaining Divisions** (70 chapters)

3. **Corps/Army Units** (8 chapters)

4. **Short Chapters** (7 chapters needing expansion)

5. **Brigade/Force Units** (4 chapters)

### Manual Enhancement Steps

For each generated chapter:

1. **Read source JSON** (`data/output/units/{nation}_{quarter}_{unit}_toe.json`)
2. **Search `[MANUAL:` markers** in generated chapter
3. **Research historical context**:
   - Formation history
   - Major battles/engagements
   - Commander biographies
   - Combat performance
4. **Write narrative sections**:
   - Overview (2-3 paragraphs)
   - Commander biography (1-2 paragraphs)
   - Personnel quality (2-3 paragraphs)
   - Combat history (major engagements with details)
   - Tactical doctrine (capabilities, limitations)
   - Historical significance (strategic impact, lessons learned)
5. **Remove `[MANUAL:` markers** when section complete
6. **Add specifications** for weapons/vehicles (from Resource Documents or online sources)

### Quality Check

Before considering a chapter complete:

- [ ] All `[MANUAL:` markers removed
- [ ] Historical narrative comprehensive (2-3 paragraphs per section minimum)
- [ ] Equipment specifications added (caliber, range, weight, etc.)
- [ ] Combat engagements described with dates, locations, outcomes
- [ ] Data quality section updated with actual sources and confidence
- [ ] No placeholder text remaining
- [ ] Matches comprehensive chapter quality (800-1,500 lines typical)

## Examples

### Generated vs. Manual Comparison

**Generated (auto-populated from JSON)**:
```markdown
### Field Artillery: 72 Guns

#### Ordnance QF 25-Pounder Gun-Howitzer
- **Count:** 72
- **Caliber:** 87.6mm

**[MANUAL: Add specifications:]**
- Range
- Shell weight
- Rate of fire
```

**Manual Enhancement (comprehensive)**:
```markdown
### Field Artillery: 72 Guns

#### Ordnance QF 25-Pounder Gun-Howitzer
- **Count:** 72 guns (70 operational)
- **Organization:** 3 regiments of 24 guns each (3 batteries per regiment)
- **Specifications:**
  - Caliber: 87.6mm (3.45 inches)
  - Range: 12,250 meters (normal), 13,400 meters (supercharge)
  - Shell Weight: 11.34 kg
  - Rate of Fire: 8 rounds/minute sustained
  - Muzzle Velocity: 518 m/s
  - Weight: 1,800 kg (firing)
  - Crew: 6

The 25-pounder was the British Army's primary field artillery piece, combining roles of field gun and howitzer. Its versatility and fire control system made it one of the war's best artillery pieces.

**Employment:** Divisional artillery support with concentrated bombardments or brigade support. Pre-registered defensive fire zones were highly effective in static positions.
```

## Script Architecture

### Key Functions

- `load_unit_json()` - Parse unit JSON files
- `generate_overview_section()` - Auto-populate overview with placeholders
- `generate_command_section()` - Command structure from JSON
- `generate_personnel_section()` - Personnel breakdown with percentages
- `generate_organization_section()` - Subordinate units list
- `generate_weapons_section()` - Infantry weapons with specifications
- `generate_vehicles_section()` - Vehicles and transport
- `generate_artillery_section()` - Artillery breakdown
- `generate_supply_section()` - Supply/logistics status
- `generate_environment_section()` - Weather and terrain
- `generate_combat_history_section()` - Combat history with placeholders
- `generate_tactical_doctrine_section()` - Doctrine and capabilities
- `generate_wargaming_section()` - Scenario suitability
- `generate_data_quality_section()` - Sources and confidence
- `generate_historical_significance_section()` - Legacy and lessons

### Data Sources

**Primary**: Phase 6 unit JSON files (`data/output/units/*_toe.json`)

**JSON Schema**: `schemas/unified_toe_schema.json` (v3.1.0)

**Key JSON Fields**:
- `unit_designation`, `nation`, `quarter`, `organization_level`
- `command` (commander, chief of staff, HQ location)
- `total_personnel`, `officers`, `ncos`, `enlisted`
- `subordinate_units` (array of unit objects)
- `top_3_infantry_weapons`, `trucks`, `motorcycles`, `armored_cars`
- `artillery_total`, `field_artillery`, `anti_tank`, `anti_aircraft`
- `supply_logistics`, `weather_environment`
- `combat_history`, `tactical_doctrine`, `wargaming_data`
- `validation` (sources, confidence, gaps)

## Output Structure

### 14-Section Format

1. **Overview** - Historical context + key statistics
2. **Command Structure** - Commander, staff, HQ
3. **Personnel Strength** - Officers/NCOs/enlisted breakdown
4. **Organization** - Subordinate units with composition
5. **Infantry Weapons** - Rifles, MGs, small arms
6. **Motor Vehicles** - Trucks, motorcycles, armored cars
7. **Artillery** - Field, AT, AA guns
8. **Supply & Logistics** - Fuel, ammo, water, operational radius
9. **Weather & Environment** - Climate, terrain, challenges
10. **Combat History** - Formation, deployment, major engagements
11. **Tactical Doctrine** - Role, capabilities, limitations
12. **Wargaming Data** - Morale, scenarios, special rules
13. **Data Quality** - Sources, confidence assessment
14. **Historical Significance** - Strategic importance, legacy

## Tips for Manual Enhancement

### Research Sources

**Online Resources**:
- Wikipedia (unit histories, battle articles)
- tanks-encyclopedia.com (vehicle specifications)
- militaryfactory.com (equipment data)
- wwiidatabase.com (battle summaries)

**Project Resources**:
- `Resource Documents/` - Historical references
- Phase 6 unit JSONs - source citations
- Database `master_database.db` - equipment specs

### Writing Style

**Concise but comprehensive**:
- 2-3 paragraphs per manual section minimum
- Focus on facts and historical accuracy
- Avoid speculation without evidence
- Use military terminology correctly
- Include specific dates, locations, outcomes

**Example Opening (Overview)**:
```markdown
The 7th Armoured Division, known as the "Desert Rats," was the British Army's premier armored formation in North Africa. Formed in Egypt in 1938, the division spearheaded Western Desert Force operations from the war's outset. During Q2 1940 (April-June), the division occupied defensive positions in the Western Desert, preparing for Italy's expected entry into the war.

Under the command of Major-General Michael O'Moore Creagh, the 7th Armoured was the only fully-equipped British armored division in theater. Its 228 tanks and high degree of motorization made it the cornerstone of British mobile defense doctrine. The division would soon face its first combat test when Italy declared war on June 10, 1940.
```

### Common Pitfalls

**Avoid**:
- Copying text from copyrighted sources
- Speculation without historical evidence
- Modern terminology for historical equipment
- Conflating different time periods
- Ignoring data quality gaps

**Do**:
- Cite sources in Data Quality section
- Acknowledge gaps in knowledge
- Use period-appropriate language
- Cross-reference multiple sources
- Document assumptions clearly

## Performance

### Speed
- Single chapter: <1 second
- All 402 units: ~60 seconds
- Stub-only (127 chapters): ~15 seconds

### File Sizes
- Input JSON: 10-50 KB typical
- Output chapter: 25-40 KB (400-500 lines)
- Comprehensive manual chapter: 80-150 KB (800-1,500 lines)

## Troubleshooting

### Script Errors

**"File not found"**:
- Ensure unit JSON exists in `data/output/units/`
- Use full filename: `{nation}_{quarter}_{unit}_toe.json`

**"Unicode error"** (Windows):
- Fixed in current version (uses ASCII output)

**"Permission denied"**:
- Check file isn't open in editor
- Use `--overwrite` flag if file exists

### Generated Chapter Issues

**Missing data sections**:
- Check if JSON field exists
- Some units have incomplete data (by design)
- Manual placeholders will appear where data missing

**Incorrect formatting**:
- Script follows JSON schema v3.1.0
- Older unit JSONs may have different field names
- Update unit JSON or edit generated chapter manually

## Next Steps

After generating templates:

1. **Review** generated chapters for data accuracy
2. **Prioritize** high-value divisions for manual enhancement
3. **Research** historical sources for each unit
4. **Write** comprehensive narrative sections
5. **QA** completed chapters against quality checklist
6. **Commit** completed chapters to git

**Estimated Effort**:
- Template generation: 15 seconds (automated)
- Manual enhancement per chapter: 3-6 hours
- Total for 127 stubs: ~380-760 hours

**Recommended Approach**:
- Focus on 32 high-value divisions first (160-320 hours)
- Assess quality and adjust process
- Complete remaining divisions in batches
- Final polish pass on all chapters

---

**Questions?** Check `PHASE_9B_NEXT_STEPS.md` for chapter completion strategy or `PROJECT_SCOPE.md` for overall project context.
