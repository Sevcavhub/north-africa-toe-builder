# Source Hierarchy

## 3-Tier Source Prioritization System

This project uses a **3-tier waterfall system** to prioritize source quality and maximize data confidence. Sources are automatically selected from the highest available tier, escalating to lower tiers only when necessary.

---

## Tier 1: Primary Sources (90-95% Confidence)

### Definition

**Official military documents** and **authoritative reference works** compiled from primary records.

### German Units

**Georg Tessin: *Verbände und Truppen der deutschen Wehrmacht und Waffen-SS im Zweiten Weltkrieg 1939-1945***
- 17-volume Wehrmacht encyclopedia
- Compiled from German military archives (Bundesarchiv)
- Unit-by-unit detail with commanders, composition, equipment
- **Location**: `Resource Documents/tessin-georg-verbande.../`
- **Confidence**: 95%

**German War Diaries (Kriegstagebuch)**
- Original operational records
- Daily entries on strength, operations, losses
- **Confidence**: 95%

### British & Commonwealth Units

**British Army Lists (Quarterly Publications 1941-1943)**
- Official War Office publications
- Commander appointments, unit locations, organizational changes
- Published quarterly
- **Location**: `Resource Documents/Great Britain Ministry of Defense Books/`
- **Confidence**: 95%

**War Office Establishment Tables**
- Authorized strength and equipment for each unit type
- Official TO&E standards
- **Confidence**: 90%

**Commonwealth War Diaries**
- Australian, New Zealand, South African, Indian official records
- Unit-level operational records
- **Confidence**: 95%

### American Units

**US Army Field Manuals (FM series)**
- Official doctrine and organization
- Equipment specifications
- TO&E tables
- **Location**: `Resource Documents/`
- **Confidence**: 95%

**US War Department Records**
- Official unit histories
- Personnel and equipment records
- **Confidence**: 95%

### Italian Units

**Italian Army Official Records**
- Regio Esercito organizational documents
- Divisional war diaries (Diari storici)
- **Confidence**: 90%

**Published Italian OOB Archives**
- Compiled from Stato Maggiore archives
- Niehorster database Italian section
- **Confidence**: 85%

---

## Tier 2: Curated Secondary Sources (75-85% Confidence)

### Definition

**Reputable historical databases** and **specialist websites** maintained by recognized military historians.

### Curated Websites

**Feldgrau.com** (German military research)
- Jason Pipes, editor
- German unit histories and organizational data
- Cross-referenced to primary sources
- **Confidence**: 80%

**Dr. Leo Niehorster's World War II Armed Forces Orders of Battle**
- Comprehensive OOB database
- Multi-national coverage
- Compiled from official records
- **Confidence**: 80%

**desertrats.org.uk** (British 7th Armoured Division)
- Specialist site for 7th Armoured Division
- Veteran accounts and official records
- **Confidence**: 80%

**The Long, Long Trail** (British Army 1914-1918, some WWII)
- Chris Baker, editor
- British Army organizational data
- **Confidence**: 75%

**Operation Battleaxe OOB**
- Specialist research on June 1941 battle
- Cross-referenced multiple sources
- **Confidence**: 80%

### Published Divisional Histories

**Examples**:
- *The Tanks* by B.H. Liddell Hart (British armor)
- *Achtung-Panzer!* by Heinz Guderian (German armor)
- *The Desert Rats* by Robin Neillands (7th Armoured Division)

**Confidence**: 75-80% depending on author credentials and source citations

### Academic Publications

**Peer-reviewed journals**:
- *The Journal of Military History*
- *War in History*
- *The RUSI Journal*

**Confidence**: 80-85% (varies by article)

---

## Tier 3: General Secondary Sources (60-75% Confidence)

### Definition

**General military history** sources without specialized focus or direct primary source access.

### General Websites

**Axis History Forum**
- Community-contributed research
- Variable quality (some excellent, some poor)
- **Confidence**: 60-70%

**Wikipedia** (EXCLUDED)
- Not used as a source
- Too variable in quality
- Not cited in this project

### Popular Histories

**Mass-market books**:
- Good narrative, less detailed TO&E data
- Often lack source citations
- **Confidence**: 65%

**Examples**:
- *Rommel: The Desert Fox* by Desmond Young
- *The Desert War* by Alan Moorehead

### Wargaming Reference Books

**Examples**:
- *Africa Orientale Italiana* (Compass Games)
- Various Osprey Publishing titles

**Confidence**: 65-70% (good for equipment specs, less for exact unit compositions)

---

## Source Waterfall Process

### Automatic Escalation

The system automatically escalates through tiers:

1. **Search Tier 1**: Check local primary sources (Tessin, Army Lists, Field Manuals)
2. **If insufficient**: Escalate to Tier 2 (Feldgrau, Niehorster, specialist sites)
3. **If still insufficient**: Escalate to Tier 3 (general sources)
4. **If data unavailable**: Mark as "Unknown" with documented search effort

### Example: German 15. Panzer-Division, 1941-Q2

**Step 1: Tier 1 Search**
- Search Tessin Volume 3 (Panzer divisions)
- **Result**: Commander (von Prittwitz), composition, approximate strength
- **Confidence**: 95%

**Step 2: Tier 2 Supplement**
- Feldgrau.com for equipment details
- **Result**: Panzer III/IV variant breakdown
- **Confidence**: 80%

**Step 3: Cross-Reference**
- Niehorster database
- **Result**: Confirms Tessin data
- **Final Confidence**: 90% (Tier 1 + Tier 2 corroboration)

---

## Confidence Scoring by Tier Mix

### Pure Tier 1 (90-95%)
- All data from primary sources
- Multiple primary sources corroborate
- Minimal gaps

### Tier 1 + Tier 2 (80-89%)
- Core data from Tier 1
- Details supplemented from Tier 2
- Cross-referenced for consistency

### Tier 2 Heavy (75-79%)
- Primary data from Tier 2 sources
- Some Tier 1 corroboration
- Known gaps documented

### Tier 2 + Tier 3 (70-74%)
- Mix of Tier 2 and Tier 3
- Core facts verified
- Multiple gaps

### Below 70%
- Insufficient quality
- Requires additional research
- Not published until improved

---

## Source Documentation

### Citation Format

All sources documented with:
- **Source name**: Full title/website
- **Specific location**: Page number, URL, archive reference
- **Access date**: When source was consulted
- **Confidence**: Tier assignment

**Example**:
```json
{
  "source": "Tessin, Georg. Verbände und Truppen der deutschen Wehrmacht, Volume 3",
  "page": 127,
  "confidence_tier": 1,
  "confidence_score": 95,
  "date_accessed": "2025-10-10"
}
```

### Multiple Sources

When multiple sources used:
- List all sources
- Note primary source used for each fact
- Document conflicts and resolution

---

## Source Quality Evaluation

### Criteria for Tier 1

- ✅ Official military records
- ✅ Contemporary documents (created during war)
- ✅ Authoritative compilations from archives
- ✅ Published by government or recognized institution

### Criteria for Tier 2

- ✅ Compiled by recognized military historian
- ✅ Citations to primary sources
- ✅ Peer review or editorial oversight
- ✅ Specialized expertise

### Criteria for Tier 3

- ⚠️ General military history
- ⚠️ May lack detailed citations
- ⚠️ Narrative focus over data precision
- ⚠️ Community-contributed (variable quality)

---

## Handling Source Conflicts

### When Sources Disagree

**Priority Order**:
1. Tier 1 sources override lower tiers
2. More specific source (divisional history > general OOB)
3. More recent scholarship (if equally authoritative)
4. Multiple sources agreeing override single source

**Documentation**:
- Note all conflicting values
- Explain resolution reasoning
- Include in "Data Quality & Known Gaps" section

**Example**:
- Tessin: "15. Panzer had 120 tanks"
- Feldgrau: "15. Panzer had 142 tanks"
- **Resolution**: Use Tessin (Tier 1 > Tier 2)
- **Documentation**: "Tank count varies (120-142), Tessin used as authoritative Tier 1 source"

---

## Local vs. Web Sources

### Local Primary Sources (Preferred)

**Advantages**:
- No internet dependency
- Direct access to PDFs
- Searchable text
- Faster processing

**Coverage**:
- **German**: Tessin (comprehensive)
- **British**: Army Lists (good for 1941-1943)
- **US**: Field Manuals (doctrine and TO&E)

### Web Sources (Supplementary)

**When Used**:
- Local sources lack detail
- Equipment variant specifications
- Cross-referencing and verification
- Commonwealth units (Australian, New Zealand, South African, Indian)

**Limitations**:
- Internet required
- Variable availability
- Link rot over time

---

## Future Source Expansion

### Planned Tier 1 Additions

- **Italian**: Stato Maggiore official records (if accessible)
- **British**: WO (War Office) files from National Archives
- **US**: NARA (National Archives) records for US units
- **Australian**: AWM (Australian War Memorial) unit records

### Planned Tier 2 Additions

- **Osprey Elite series**: Detailed unit studies
- **Squadron/Signal Publications**: Equipment references
- **Academic dissertations**: Specialist research

---

## Source Access

### Local Sources

**Location**: `Resource Documents/`
- Tessin volumes (German)
- British Army Lists (British)
- Field Manuals (US)

**Format**: PDF (searchable)

### Web Sources

**Bookmarked URLs**:
- Feldgrau.com (German)
- Niehorster database (all nations)
- desertrats.org.uk (British 7th Armoured)
- Commonwealth war diaries (Australian, NZ, South African archives)

---

## Quality Assurance

### Source Verification

Before using any source:
1. **Verify authority**: Is author/institution credible?
2. **Check citations**: Does source cite primary records?
3. **Assess specificity**: Does source provide detail needed?
4. **Tier assignment**: Which tier does source belong to?

### Continuous Evaluation

- **Monitor source quality** over time
- **Reclassify** if errors discovered
- **Add new sources** as found
- **Remove sources** if proven unreliable

---

## Further Reading

- [Research Methodology](./research-methodology.md) - Overall research process
- [Data Quality Standards](./data-quality.md) - Quality requirements
- [Source Bibliography](../appendices/bibliography.md) - Complete source list

---

**Last Updated**: 2025-10-12
**Tier 1 Sources**: 7+ major references
**Tier 2 Sources**: 10+ curated databases
**Minimum Confidence**: 75% required for publication
