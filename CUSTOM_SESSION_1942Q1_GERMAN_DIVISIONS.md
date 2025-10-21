# Custom Session Start - German 1942-Q1 Divisions

Start autonomous orchestration session.

**CURRENT PROGRESS:**
- Overall: 118/420 units (28.1%)
- Target: German Divisions, 1942-Q1
- Last scan: 2025-10-21

**STRATEGY: CUSTOM UNIT SELECTION**
Target Quarter: 1942-Q1
Focus: Complete German panzer and light divisions

**NEXT BATCH (3 units):**
1. german - 15. Panzer-Division (1942q1)
2. german - 21. Panzer-Division (1942q1)
3. german - 90. leichte Division (1942q1)

**SESSION PROTOCOL (Ken's 3-3-3 Rule):**
✅ Session started (progress loaded above)
🔄 Process these 3 units in parallel (batch of 3)
💾 After batch complete: Bash('npm run checkpoint')
📊 Check validation: Review SESSION_CHECKPOINT.md for chapter status
🏁 When done: Bash('npm run session:end')

**UNIFIED SCHEMA COMPLIANCE (schemas/UNIFIED_SCHEMA_EXAMPLES.md):**
- **CRITICAL**: Use top-level fields (nation, quarter, organization_level)
- **NEVER** nest unit_identification, personnel_summary, equipment_summary
- Commander MUST be nested object: commander.name, commander.rank
- Nation values lowercase only: german, italian, british, american, french
- Tank totals MUST match: total = heavy + medium + light
- **Validation**: Run scripts/lib/validator.js before saving
- **Examples**: See schemas/UNIFIED_SCHEMA_EXAMPLES.md for correct/incorrect structures

**TEMPLATE COMPLIANCE (v2.0 - 16 Sections from MDBOOK_CHAPTER_TEMPLATE.md):**
- Section 3: Command (commander, HQ, staff) - REQUIRED
- Section 5: Artillery (summary + detail for EVERY variant)
- Section 6: Armored Cars (separate section with details, NOT in transport)
- Section 7: Transport (NO tanks/armored cars, all variants detailed)
- Section 12: Critical Equipment Shortages (Priority 1/2/3)
- Section 15: Data Quality & Known Gaps (honest assessment)
- **Confidence threshold**: ≥ 75%

**OUTPUT PATH (Architecture v4.0 - Canonical Locations):**
✅ Units: data/output/units/
✅ Chapters: data/output/chapters/

⚠️  **MANDATORY**: Save ALL files to CANONICAL locations:
   - Unit JSON: data/output/units/[unit_file].json
   - MDBook chapters: data/output/chapters/[chapter_file].md

   **NEVER** create session folders (data/output/autonomous_*/ or data/output/session_*/)

**STOP CONDITIONS:**
- Validation fails after 2 regeneration attempts
- Confidence score < 75% for any unit
- Critical gaps cannot be resolved (missing commander, no equipment data)
- Template violations detected in generated chapters
- Source documents unavailable for nation/quarter

**GENERAL AGENT WORKFLOW:**
1. ✅ CONFIRM these units with user (or allow adjustments)
2. ✅ ONLY AFTER confirmation → Launch Task tool with autonomous orchestrator
3. ✅ Specialized agents do ALL extraction, validation, chapter generation
4. ❌ DO NOT perform extraction yourself as general agent

**When user confirms, launch autonomous orchestrator with:**
- Task tool (subagent_type='general-purpose')
- Prompt: "Run autonomous orchestration for these 3 units using specialized sub-agents"
- Extended thinking for complex source analysis
- TodoWrite to track progress
- Automatic checkpoint after batch completion

---

## Historical Context - 1942-Q1 German Divisions

**15. Panzer-Division**
- Status: Active in North Africa since Q2 1941
- Quarter: 1942-Q1 (January-March 1942)
- Period Context: Between Operation Crusader and Battle of Gazala
- Primary Source: Tessin Band 08 (Panzer divisions)
- Expected Strength: ~12,000-14,000 personnel, ~120-150 tanks
- Commander: Generalmajor Gustav von Vaerst (Jan 1942 - Jun 1942)

**21. Panzer-Division**
- Status: Renamed from 5. leichte Division in October 1941
- Quarter: 1942-Q1 (January-March 1942)
- Period Context: Reorganization after Crusader losses
- Primary Source: Tessin Band 08 (Panzer divisions)
- Expected Strength: ~12,000-14,000 personnel, ~100-130 tanks
- Commander: Generalmajor Georg von Bismarck (Jan 1942 - Aug 1942)

**90. leichte Division**
- Status: Also known as "Division z.b.V. Afrika" or "90. leichte Afrika-Division"
- Quarter: 1942-Q1 (January-March 1942)
- Period Context: Light division with motorized infantry, limited armor
- Primary Source: Tessin Band 03 (Afrika formations)
- Expected Strength: ~10,000-12,000 personnel, ~30-40 tanks/assault guns
- Commander: Generalmajor Richard Veith (Dec 1941 - May 1942)

---

## Source Documents Available

**Primary Sources (Tessin):**
- Tessin Band 03: Deutsche Afrikadivisionen
- Tessin Band 08: Panzer-Divisionen (15. + 21. PzDiv)
- Tessin Band 12: Panzer-Divisionen (additional detail)

**Location:**
`Resource Documents/tessin-georg-verbande.../`

**Extraction Strategy:**
1. Search Tessin Band 08 for "15. Panzer-Division" and "21. Panzer-Division" (1942 sections)
2. Search Tessin Band 03 for "90. leichte" or "Division z.b.V. Afrika"
3. Cross-reference with Rommel's reports (if available in secondary sources)
4. Use 3-tier waterfall: Local docs → Feldgrau.com → General search (no Wikipedia)

---

## Expected Outputs (per unit)

**For each division, generate:**

1. **Unit TO&E JSON** (`data/output/units/`)
   - german_1942q1_15_panzer_division_toe.json
   - german_1942q1_21_panzer_division_toe.json
   - german_1942q1_90_leichte_division_toe.json

2. **MDBook Chapter** (`data/output/chapters/`)
   - chapter_german_1942q1_15_panzer_division.md
   - chapter_german_1942q1_21_panzer_division.md
   - chapter_german_1942q1_90_leichte_division.md

3. **Validation Report** (automatic)
   - Schema compliance check
   - Historical accuracy verification
   - Template compliance (16 sections)
   - Confidence score ≥ 75%

---

## Ready to Proceed?

📋 **USER**: Review the 3 units above. Reply with:
   • **"Proceed"** → Start autonomous orchestration for these units
   • **"Change to [different units]"** → Adjust selection first
   • **"Add [unit]"** → Include additional units in batch
