# 1941-Q2 Showcase - MDBook Structure

**Created**: 2025-10-12
**Purpose**: Proper MDBook structure for 1941-Q2 North Africa Campaign TO&E data

---

## What This Is

This directory contains the **proper MDBook structure** for showcasing the North Africa TO&E Builder project using completed 1941-Q2 units as a demonstration.

### What's Complete

✅ **MDBook Framework** - All structure files created:
- `book.toml` - MDBook configuration
- `src/SUMMARY.md` - Table of contents (17 unit chapters organized by nation)
- `src/introduction.md` - Project introduction
- `src/1941-q2/overview.md` - Quarter overview and historical context
- `src/methodology/` - Research methodology (4 pages)
- `src/appendices/` - Glossary, bibliography, unit index (3 pages)

### What's Needed

❌ **Unit Chapters** - The 17 individual unit chapters need to be generated from JSON files:
- `src/1941-q2/british/` - 7 British/Commonwealth chapters
- `src/1941-q2/german/` - 3 German chapters
- `src/1941-q2/italian/` - 7-8 Italian chapters

---

## Directory Structure

```
1941-q2-showcase/
├── README.md (this file)
└── north-africa-toe-book/
    ├── book.toml (MDBook configuration)
    ├── book/ (generated HTML - created by mdbook build)
    └── src/
        ├── SUMMARY.md (table of contents)
        ├── introduction.md (project overview)
        ├── 1941-q2/
        │   ├── overview.md (quarter overview)
        │   ├── british/ (7 chapter files - TO BE GENERATED)
        │   ├── german/ (3 chapter files - TO BE GENERATED)
        │   └── italian/ (7-8 chapter files - TO BE GENERATED)
        ├── methodology/
        │   ├── research-methodology.md ✅
        │   ├── source-hierarchy.md ✅
        │   ├── data-quality.md ✅
        │   └── validation.md ✅
        └── appendices/
            ├── glossary.md ✅
            ├── bibliography.md ✅
            └── unit-index.md ✅
```

---

## Next Steps

### Option 1: Generate Chapters from Existing JSON Files

1. **Consolidate Unit JSONs** - Gather the 17 completed 1941-Q2 unit JSON files into one location
2. **Generate MDBook Chapters** - Use `book_chapter_generator` agent to create chapters following template v2.0
3. **Place in correct directories** - Organize by nation (british/, german/, italian/)
4. **Build the book** - Run `mdbook build` to generate HTML

### Option 2: Use Existing Chapters (If Available)

1. **Locate existing chapters** - Search for already-generated chapters in previous sessions
2. **Validate template compliance** - Ensure they follow template v2.0 (16 required sections)
3. **Copy to structure** - Place in appropriate nation directories
4. **Build the book** - Run `mdbook build`

---

## 17 Units to be Documented

### British & Commonwealth (7)
1. 7th Armoured Division "Desert Rats"
2. 50th (Northumbrian) Infantry Division
3. 2nd New Zealand Division
4. 4th Indian Infantry Division
5. 5th Indian Infantry Division
6. 9th Australian Division "Rats of Tobruk"
7. 1st South African Infantry Division

### German (3)
1. Deutsches Afrikakorps (Corps HQ)
2. 15. Panzer-Division
3. 5. leichte Division

### Italian (7-8)
1. 132ª Divisione corazzata "Ariete"
2. 17ª Divisione di fanteria "Pavia"
3. 27ª Divisione di fanteria "Brescia"
4. 55ª Divisione motorizzata "Trento"
5. 60ª Divisione di fanteria "Sabratha"
6. 101ª Divisione motorizzata "Trieste"
7. 25ª Divisione di Fanteria "Bologna"
8. 55ª Divisione di Fanteria "Savona"

---

## Chapter Template Requirements

Each chapter must follow **MDBOOK_CHAPTER_TEMPLATE.md v2.0** with **16 required sections**:

1. Header
2. Division/Unit Overview
3. Command (commander, HQ, staff)
4. Personnel Strength
5. Armoured Strength (with variant breakdowns)
6. Artillery Strength (with variant breakdowns + detail sections)
7. Armoured Cars (separate section)
8. Transport & Vehicles (NO tanks/armored cars)
9. Organizational Structure
10. Supply Status
11. Tactical Doctrine & Capabilities
12. Critical Equipment Shortages (Priority 1/2/3)
13. Historical Context
14. Wargaming Data
15. Data Quality & Known Gaps (confidence, sources, gaps)
16. Conclusion (with data source footer)

---

## Building the Book

### Prerequisites

Install MDBook:
```bash
cargo install mdbook
```

### Build Commands

```bash
cd north-africa-toe-book

# Build HTML book
mdbook build

# Serve locally for preview
mdbook serve

# Clean build directory
mdbook clean
```

### Output

Built book appears in `north-africa-toe-book/book/` directory.

Open `book/index.html` in browser to view.

---

## Quality Standards

All chapters must meet:
- ✅ **Confidence Score**: ≥ 75%
- ✅ **Schema Compliance**: 100% (JSON validation passes)
- ✅ **Template Compliance**: All 16 sections present
- ✅ **Variant Details**: Every variant in tables has detail section
- ✅ **Source Citations**: Minimum 2 sources for critical facts
- ✅ **Gap Documentation**: All gaps explicitly documented in Section 15

---

## This is NOT Repackaging

**This is the CORRECT approach**:
- ✅ Using completed unit JSONs (already extracted from primary sources)
- ✅ Generating professional MDBook chapters following template v2.0
- ✅ Creating a showcase of what the final project deliverable looks like
- ✅ Demonstrating the proper workflow output format

**This is NOT**:
- ❌ Repackaging existing data without purpose
- ❌ Inventing extra workflow phases (only Phases 1-7)
- ❌ Building aircraft databases (not current priority)
- ❌ Creating work that defeats the project's core purpose

---

## Showcase Purpose

This 1941-Q2 showcase demonstrates:
1. **Complete quarter coverage** (17/17 units)
2. **Multi-nation data** (British, German, Italian)
3. **Variant-level equipment tracking**
4. **MDBook professional presentation**
5. **Historical accuracy with source citations**
6. **Schema compliance** (unified_toe_schema.json v1.0.0)
7. **Template compliance** (MDBOOK_CHAPTER_TEMPLATE.md v2.0)

**This proves the project can deliver historically accurate, schema-compliant, professionally presented TO&E data at scale.**

---

## Project Context

See project root documentation:
- `CLAUDE.md` - Project instructions
- `docs/MDBOOK_CHAPTER_TEMPLATE.md` - Chapter template v2.0
- `docs/project_context.md` - Architecture and design
- `schemas/unified_toe_schema.json` - Data schema
- `1941_Q2_SHOWCASE_PLAN.md` - Original showcase plan

---

**Status**: Structure Complete, Chapters Pending
**Next Action**: Generate 17 unit chapters from JSON files
**Build Tool**: mdbook (install with cargo)
