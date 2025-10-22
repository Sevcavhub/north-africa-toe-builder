# Re-Extraction Guide: 39 Weak-Source Units

**Date Created**: October 22, 2025
**Reason**: Wikipedia-only sources (27 units) + No sources (12 units)
**Total Units**: 39

## 🎯 Objective

Re-extract 39 units with **strict primary source requirements**:
- ❌ **NO Wikipedia sources allowed**
- ✅ **Minimum 2 primary sources per unit**
- ✅ **85%+ confidence for divisions, 80%+ for brigades**
- ✅ **Cross-referenced data points**

---

## 📊 Units Breakdown

| Quarter | Wikipedia-Only | No Sources | Total |
|---------|----------------|------------|-------|
| 1940-Q3 | 3 | 0 | 3 |
| 1940-Q4 | 4 | 0 | 4 |
| **1941-Q1** | **6** | **3** | **9** ⚠️ High priority |
| 1941-Q2 | 1 | 0 | 1 |
| **1941-Q3** | **4** | **5** | **9** ⚠️ High priority |
| 1941-Q4 | 2 | 3 | 5 |
| 1942-Q1 | 1 | 1 | 2 |
| 1942-Q3 | 1 | 0 | 1 |
| 1942-Q4 | 2 | 0 | 2 |
| 1943-Q1 | 3 | 0 | 3 |
| **TOTAL** | **27** | **12** | **39** |

### Critical No-Source Units (Need Immediate Attention)

**1941-Q1 German Units** (All 3 have Tessin coverage available):
1. 21. Panzer-Division
2. 5. leichte Division (5th Light Division)
3. 90. leichte Afrika-Division

**1941-Q3 Italian Units** (5 units, many naming variants):
4. 101ª Divisione Motorizzata 'Trieste'
5. 102ª Divisione motorizzata Trento
6. 132ª Divisione Corazzata Ariete
7. 25ª Divisione di Fanteria 'Bologna'

---

## 🚀 Execution Steps

### Step 1: Archive Current Units

```bash
node scripts/archive_weak_source_units.js
```

**What this does:**
- Moves 39 unit files to `data/output/archive/weak_sources_[timestamp]/`
- Creates ARCHIVE_MANIFEST.json with metadata
- Updates WORKFLOW_STATE.json (removes from completed count)
- Creates backup of WORKFLOW_STATE.json

**Expected Output:**
```
✅ Archived: 39 units
📁 Location: data/output/archive/weak_sources_1729558800000/
📝 Manifest created: ARCHIVE_MANIFEST.json
✅ WORKFLOW_STATE updated:
   - Removed 39 units from completed array
   - New completion: 190/420 (45.2%)
```

### Step 2: Generate Re-Extraction Batches

```bash
node scripts/generate_reextraction_batch.js
```

**What this does:**
- Creates 13 batches of 3 units each
- Prioritizes by unit type (divisions first)
- Generates re-extraction manifest
- Creates session:start prompt with strict source requirements

**Expected Output:**
```
✅ Manifest saved: data/output/reextraction_batches/REEXTRACTION_MANIFEST.json
✅ Prompt saved: data/output/reextraction_batches/SESSION_START_PROMPT.txt
```

### Step 3: Review the Prompt

```bash
cat data/output/reextraction_batches/SESSION_START_PROMPT.txt
```

**Review checklist:**
- [ ] Batch 1 units are correct
- [ ] Source requirements match nation
- [ ] Quality standards are clear
- [ ] Wikipedia prohibition is explicit

### Step 4: Start Re-Extraction Session

```bash
npm run session:start
```

When prompted for strategy, choose **"specific units"** and paste the prompt from `SESSION_START_PROMPT.txt`.

**Or use autonomous mode:**
```bash
npm run start:autonomous
```

Then paste the prompt into the Claude Code chat.

---

## 📚 Approved Primary Sources

### German Units (Tessin MANDATORY)

**Tier 1 (90%+):**
- Tessin, Georg - Verbände und Truppen der deutschen Wehrmacht und Waffen-SS (17 volumes)
  - Location: `Resource Documents/tessin-georg-verbande.../`
- Nafziger Collection - German OOB files
  - Location: `Resource Documents/Nafziger Collection/WWII/`

**Tier 2 (75-89%):**
- Feldgrau.net (curated articles only, verify author credentials)

**REJECTED:**
- Wikipedia
- Axis History Forum (general posts)
- Unsourced websites

### Italian Units

**Tier 1 (90%+):**
- TM E 30-420: Handbook on Italian Military Forces (August 1943)
  - Location: `Resource Documents/`
- Order of Battle of the Italian Army - USA HQ G-2 (July 1943)
  - Location: `Resource Documents/`
- Nafziger Collection - Italian OOB files

**Tier 2 (75-89%):**
- Italian official histories (if available)

**REJECTED:**
- Wikipedia
- Regio Esercito fan sites

### British/Commonwealth Units

**Tier 1 (90%+):**
- British Army Lists (quarterly 1940-1943)
  - Location: `Resource Documents/Great Britain Ministery of Defense Books/`
- Playfair - History of the Second World War: Mediterranean and Middle East (Vols I-IV)
- Prasad - Official History of the Indian Armed Forces in WWII
- Nafziger Collection - British OOB files

**Tier 2 (75-89%):**
- Unit histories from official regimental museums
- National Archives documents

**REJECTED:**
- Wikipedia
- Generic military history websites

### American Units

**Tier 1 (90%+):**
- US Field Manuals (FM 101-10, TO&E documents)
  - Location: `Resource Documents/`
- US Army organizational records
- Nafziger Collection - US OOB files

**Tier 2 (75-89%):**
- US Army Center of Military History publications

**REJECTED:**
- Wikipedia
- Commercial histories without primary source citations

### French Units

**Tier 1 (90%+):**
- Free French Brigade/Division official records
- Nafziger Collection - French OOB files
- Playfair Official History (for Free French in British formations)

**Tier 2 (75-89%):**
- French Ministry of Defense archives

**REJECTED:**
- Wikipedia
- Commercial Free French histories without citations

---

## ✅ Quality Control Checklist

For each extracted unit, verify:

### Source Documentation
- [ ] **NO Wikipedia** citations anywhere in validation.source array
- [ ] **Minimum 2 primary sources** cited
- [ ] Each source has **full citation** (book/volume/page or document ID)
- [ ] Each source has **confidence percentage** (85%+ for divisions)
- [ ] Each source has **tier classification** (Tier 1 or Tier 2)

### Data Cross-Reference
- [ ] Equipment counts verified from **2+ sources**
- [ ] Commander name verified from **2+ sources**
- [ ] Unit structure verified from **2+ sources**
- [ ] Conflicts documented with **resolution reasoning**

### Validation
- [ ] File passes `npm run validate` (no schema errors)
- [ ] Overall confidence ≥85% (divisions) or ≥80% (brigades/corps)
- [ ] All data_quality.notes explain estimation methods

### Example Good Entry

```json
{
  "validation": {
    "source": [
      "Tessin, Georg - Verbände und Truppen Band 06, pages 140-141 - 90. leichte Division organizational structure, commanders, regiment assignments (Tier 1, 95% confidence)",
      "Nafziger Collection OOB 941JKOC - 90. leichte Division 1 November 1941 - Equipment counts (60x PzKpfw III, 17x PzKpfw II) cross-referenced with Tessin (Tier 1, 92% confidence)",
      "Feldgrau.net: 90. leichte Division history - Theodor Graf von Sponeck command verified against Tessin dates (Tier 1, 88% confidence)"
    ],
    "confidence": 92,
    "last_updated": "2025-10-22",
    "known_gaps": [
      "Exact anti-aircraft battery strength estimated from divisional establishment tables",
      "Operational readiness percentages estimated from supply reports"
    ]
  }
}
```

---

## 📈 Progress Tracking

### Batch Processing

- **Batch 1** (Units 1-3): ⏳ Pending
- **Batch 2** (Units 4-6): ⏳ Pending
- **Batch 3** (Units 7-9): ⏳ Pending
- ... (13 batches total)

### Completion Milestones

| Batches | Units | Completion % |
|---------|-------|--------------|
| 1-3 | 9 | 23% |
| 4-6 | 18 | 46% |
| 7-9 | 27 | 69% |
| 10-13 | 39 | 100% |

**Target**: Complete all 13 batches within 2-3 sessions (3-5 days)

---

## 🔄 Workflow Per Batch

**Time per batch**: 30-45 minutes (thorough cross-referencing)

1. **Source Gathering** (10 min)
   - Locate Tessin/Army Lists/TM30 pages
   - Locate Nafziger OOB files
   - Verify document dates match quarter

2. **Extraction** (15-20 min)
   - Extract from Source A
   - Extract from Source B
   - Cross-reference and reconcile

3. **Validation** (5-10 min)
   - Run `npm run validate`
   - Check for Wikipedia citations
   - Verify confidence levels

4. **Checkpoint** (5 min)
   - Run `npm run checkpoint`
   - Verify WORKFLOW_STATE update
   - Git commit progress

---

## 🚨 Common Issues & Solutions

### Issue: "Can't find Tessin volume for German unit"

**Solution**: Check volume mapping:
- 21. Panzer-Division → Tessin Band 3 or 6
- 5. leichte Division → Tessin Band 6
- 90. leichte Division → Tessin Band 6

All volumes in: `Resource Documents/tessin-georg-verbande.../`

### Issue: "Two sources conflict on equipment count"

**Solution**: Document both and explain resolution:
```json
"validation": {
  "source": [
    "Source A says 60 tanks...",
    "Source B says 72 tanks...",
    "Cross-referenced: Source A is post-losses report, Source B is authorized strength. Using Source A actual count (60) with note."
  ],
  "data_quality_notes": "Equipment count shows actual (60) vs authorized (72) - 12 tanks under strength due to combat losses."
}
```

### Issue: "Wikipedia has better detail than primary sources"

**Solution**: **DO NOT USE IT**. Find alternative:
- Check Nafziger Collection for detailed OOB
- Check unit regimental histories
- Estimate from TO&E if necessary, document as estimated

---

## 📝 Post-Re-Extraction

After completing all 13 batches:

1. **Final Validation**
   ```bash
   npm run validate
   ```
   Expected: 39/39 units passing validation

2. **Update Matching Report**
   ```bash
   node scripts/canonical_master_matcher.js
   ```
   Expected: 39 units now matched to seed with primary sources

3. **Rebuild WORKFLOW_STATE**
   ```bash
   node scripts/rebuild_workflow_state.js
   ```
   Expected: Completion ~54% → ~63% (39 units added back)

4. **Git Commit**
   ```bash
   git add .
   git commit -m "fix: Re-extract 39 units with strict primary sources (no Wikipedia)

   - Replaced 27 Wikipedia-only units with primary source extractions
   - Added sources to 12 no-source units
   - All units now have 2+ primary sources, 85%+ confidence
   - Tessin mandatory for all German units
   - TM30/Army Lists for Italian/British units

   See REEXTRACTION_GUIDE.md for methodology"
   ```

---

## 📌 Notes

- **No Wikipedia rule is absolute** - even for general context or background
- German units WITHOUT Tessin sources should be rejected (it's mandatory)
- Italian division names: Use full Italian official designation (e.g., "132ª Divisione Corazzata 'Ariete'")
- Confidence levels below 85% (divisions) require justification or re-extraction

---

**Questions?** Review this guide or check `data/output/reextraction_batches/REEXTRACTION_MANIFEST.json` for detailed batch breakdown.
