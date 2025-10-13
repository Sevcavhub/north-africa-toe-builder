# North Africa TO&E Builder - Complete Project Scope

**Version**: 1.0.0
**Last Updated**: 2025-10-13
**Status**: 🟢 LIVING DOCUMENT - Subject to updates
**Current Phase**: Phase 1-6 (Ground Forces)
**Overall Progress**: ~5.8% complete (18 of ~313-348 total units)

---

## 🎯 Project Vision

Build a **comprehensive North Africa Campaign TO&E database (1940-1943)** specifically designed for **wargame scenario and campaign generation**.

This is NOT just a static historical database - it's a **game-ready scenario generation system** with:
- Complete unit TO&E data (variant-level equipment detail)
- Supply/logistics modeling (fuel reserves, ammo stocks, operational radius)
- Weather/environmental factors (seasonal impacts on operations)
- Air-ground integration (complete air support assignments)
- Multi-format export (MDBook, wargaming scenarios, SQL database)

---

## 📊 Complete Project Scope

### Total Units Across All Phases:

| Component | Unit Count | Status |
|-----------|-----------|--------|
| **Ground Forces** | 213 | 18 complete (8.5%) - Phase 1-6 |
| **Air Force Units** | ~100-135 | Not started - Phase 7 |
| **Battle Scenarios** | 12+ | Planned - Phase 9 |
| **Campaign System** | 1 complete | Planned - Phase 10 |
| **TOTAL** | **~313-348 units** | **~5.8% complete** |

### Scope Clarifications:

**Ground Forces (213 units)**:
- Theater → Corps → Division → Regiment → Battalion → Company → Platoon → Squad
- All organizational levels with complete SCM detail
- Equipment: Ground vehicles, artillery, support weapons
- Aircraft section: Shows **air support AVAILABLE** to ground forces (not organic aircraft)

**Air Force Units (~100-135 units)**:
- Separate organizational structure (Geschwader → Gruppe → Staffel, etc.)
- Luftwaffe: ~30-40 units (JG 27, StG 2, etc.)
- RAF/Commonwealth: ~40-50 units (Desert Air Force squadrons)
- USAAF: ~10-15 units (9th/12th Air Force groups)
- Regia Aeronautica: ~20-30 units (5ª Squadra Aerea stormi)
- Complete TO&E: Pilots, ground crew, aircraft, ordnance, fuel bowsers

---

## 🗓️ Phased Approach

### **Phase 1-6: Ground Forces Extraction** (CURRENT FOCUS)

**Goal**: Complete all 213 ground combat units

**Status**: 18/213 complete (8.5%)

**Deliverables**:
- 213 unit JSON files (complete SCM detail at all organizational levels)
- 213 MDBook chapters (professional narrative with equipment tables)
- WITW-format exports (CSV for wargaming)
- SQL database schema (ground forces tables)

**Timeline**: ~80-120 hours of autonomous processing (195 units remaining)

**Current Priorities**:
1. Fix 9 showcase gaps (Wikipedia sources, missing Corps units, Infantry Weapons sections)
2. Add supply/logistics data to schema (fuel reserves, ammo stocks, operational radius)
3. Add weather/environmental data (seasonal factors, terrain impacts)
4. Resume autonomous extraction (195 remaining ground units)

---

### **Phase 7: Air Force Extraction** (AFTER GROUND COMPLETE)

**Goal**: Extract ~100-135 air force units (all nations)

**Status**: Not started (awaits completion of Phase 1-6)

**Organizational Structures**:

**Luftwaffe** (Fliegerführer Afrika):
```
Fliegerkorps X
  └─ Jagdgeschwader 27 (Fighter Wing)
      ├─ Stab/JG 27 (Wing Staff)
      ├─ I./JG 27 (1st Group - 35 Bf 109)
      │   ├─ 1. Staffel (12 aircraft)
      │   ├─ 2. Staffel (12 aircraft)
      │   └─ 3. Staffel (11 aircraft)
      └─ II./JG 27, III./JG 27 (additional groups)
```

**RAF Desert Air Force**:
```
No. 204 Group
  └─ No. 274 Squadron RAF
      ├─ A Flight (Hurricanes)
      ├─ B Flight (Hurricanes)
      └─ Ground crew, maintenance
```

**USAAF** (1942-1943):
```
9th Air Force
  └─ 57th Fighter Group
      ├─ 64th Fighter Squadron (P-40)
      ├─ 65th Fighter Squadron (P-40)
      └─ 66th Fighter Squadron (P-40)
```

**Deliverables**:
- ~100-135 air unit JSON files (separate schema with aircrew, ordnance, ground support)
- Air forces MDBook (separate publication or integrated)
- Air unit WITW exports (specialized format)
- SQL air forces tables

**Timeline**: ~60-80 hours of autonomous processing

---

### **Phase 8: Cross-Linking & Integration**

**Goal**: Connect ground and air units with assignment data

**Status**: Awaits completion of Phases 1-7

**What This Means**:

**BEFORE (Current - Basic air support)**:
```json
{
  "aircraft_total": 147,
  "fighters": {
    "total": 42,
    "breakdown": {"Bf 109E-7": 35, "Bf 109F-2": 7}
  }
}
```

**AFTER (Enhanced with cross-links)**:
```json
{
  "aircraft_total": 147,
  "fighters": {
    "total": 42,
    "assigned_units": [
      {
        "unit_id": "luftwaffe_1941q2_i_jg27",
        "unit_name": "I./Jagdgeschwader 27",
        "commander": "Hauptmann Eduard Neumann",
        "base": "Gazala",
        "aircraft": {"Bf 109E-7/Trop": 22, "Bf 109F-2/Trop": 13},
        "operational": 28,
        "sortie_rate": 2.5
      }
    ]
  }
}
```

**Deliverables**:
- Updated ground unit JSONs (with air unit cross-links)
- Assignment tables (which air units supported which ground units)
- Integrated scenario generation capability

**Timeline**: ~20-30 hours (mostly automated)

---

### **Phase 9: Scenario Generation**

**Goal**: Create 12+ playable historical battle scenarios

**Status**: Awaits completion of Phases 1-8

**Planned Scenarios**:
1. Operation Battleaxe (June 1941)
2. Operation Crusader (November 1941)
3. Gazala (May-June 1942)
4. First El Alamein (July 1942)
5. Alam Halfa (August-September 1942)
6. Second El Alamein (October-November 1942)
7. Operation Torch (November 1942)
8. Tunisia Campaign (December 1942 - May 1943)
9. Plus 4+ additional operations

**Scenario Contents**:
- Complete OOB (ground + air units)
- Supply states at battle start (fuel days, ammo days, water reserves)
- Weather conditions (temperature, visibility, storms)
- Air support assignments (which units available, sortie rates)
- Victory conditions
- Historical outcome for validation

**Timeline**: ~40-50 hours (scenario design + testing)

---

### **Phase 10: Campaign System**

**Goal**: Complete campaign framework for 1940-1943

**Status**: Awaits completion of Phases 1-9

**Campaign Elements**:
- Quarterly transitions (how units evolved Q to Q)
- Supply line modeling (Tripoli → Benghazi → Tobruk routes)
- Weather patterns (seasonal impacts by quarter)
- Unit evolution tracking (equipment upgrades, reorganizations)
- Airfield data (Luftwaffe/RAF base locations and capacity)

**Deliverables**:
- Campaign framework (complete 1940-1943 timeline)
- Supply route data (historical port capacities, distances)
- Weather database (seasonal conditions by month/quarter)
- Unit transition tracking (formation, reorganization, dissolution)

**Timeline**: ~30-40 hours

---

## 📋 Complete Data Schema

### Ground Forces Schema (Phases 1-6)

**Version**: 3.0 (Updated 2025-10-13)

**Based on**: `F:\Timeline_TOE_Reconstruction\PROCESSING\STRATEGIC_COMMAND_SUMMARY_SCHEMA.md` (Iteration 2)

#### Section 1: COMMAND (2 fields)
- `supreme_commander` - Full rank and name
- `headquarters_location` - Geographic location with operational context

#### Section 2: PERSONNEL (3 fields)
- `total_strength` - Complete theater strength
- `total_infantry_strength` - Infantry personnel only
- `top_3_weapons` - Three most numerous infantry weapons with counts

#### Section 3: GROUND VEHICLES (27+ fields - VARIABLE)
**Core**: `ground_vehicles_total` - Rollup sum

**Standard Categories** (with variant breakdowns - NO ROLLUPS):
- `tanks` - Medium/heavy tanks (Panzer III/IV, M13/40, Sherman, Crusader, etc.)
- `light_tanks` - Light tanks and tankettes (Panzer I/II, L3/35, Stuart, etc.)
- `armored_cars` - Reconnaissance armored cars (SdKfz 222, AB41, Daimler, M8, etc.)
- `motorcycles` - Military motorcycles (BMW R75, Zündapp KS750, BSA M20, etc.)
- `trucks` - Transport trucks (Opel Blitz, Bedford, CMP, GMC, FIAT, etc.)
- `halftracks` - Halftrack carriers (SdKfz 251, Universal Carrier, M3, etc.)
- `specialized_vehicles` - Recovery, engineering, SPGs

**Optional Nation-Specific**:
- `artillery_tractors` - If separate from halftracks (SdKfz 7, SdKfz 11)
- `apcs` - If separate from halftracks
- `captured_vehicles` - If significant numbers
- `carriers` - British Universal/Bren carriers (if separate)

**CRITICAL RULE**: Every category MUST have variant-level breakdown. NO rollup counts.

#### Section 4: ARTILLERY (4 fields)
- `artillery_total` - Rollup sum
- `field_artillery` - Howitzers, guns (10.5cm leFH, 25-pdr, M1 105mm, etc.) WITH VARIANTS
- `anti_tank` - Towed AT guns (PaK 36/38/40, 6-pdr, 57mm, etc.) WITH VARIANTS
- `anti_aircraft` - AA guns (FlaK 18/36, Bofors, 90mm, etc.) WITH VARIANTS

#### Section 5: AIRCRAFT (4 fields) - AIR SUPPORT AVAILABLE
**IMPORTANT**: This shows air support ASSIGNED to ground forces, NOT organic aircraft.

- `aircraft_total` - Rollup sum
- `fighters` - Fighter aircraft (Bf 109, Spitfire, P-40, Hurricane, etc.) WITH VARIANTS
- `bombers` - Bombers and dive bombers (Ju 87 Stuka, Ju 88, Wellington, B-25, etc.) WITH VARIANTS
- `reconnaissance` - Reconnaissance aircraft (Bf 110, Lysander, P-38, etc.) WITH VARIANTS

**After Phase 8**: Will include `assigned_units` array with cross-links to air force unit IDs.

#### Section 6: SUPPLY/LOGISTICS (5 fields) - CRITICAL FOR SCENARIOS
- `supply_status` - Qualitative assessment with operational context
- `operational_radius` - Distance from main supply depot (kilometers)
- `fuel_reserves` - Days at current consumption rate
- `ammunition` - Days of combat supply
- `water` - Liters per day capacity (critical for desert operations)

#### Section 7: WEATHER/ENVIRONMENT (5+ fields) - NEW FOR SCENARIOS
- `season_quarter` - Which quarter and seasonal conditions
- `temperature_range` - Daily min/max temperatures (Celsius)
- `terrain_type` - Primary terrain (sand, rocky desert, coastal plain, etc.)
- `storm_frequency` - Sandstorms, Ghibli winds (days per month)
- `daylight_hours` - Average daylight hours (affects operational tempo)

---

### Air Forces Schema (Phase 7)

**Version**: 1.0 (For future implementation)

**Different from ground forces** - separate organizational structure.

#### Core Fields:
- `unit_designation` - Full air unit name (e.g., "I./Jagdgeschwader 27")
- `unit_type` - Fighter Gruppe, Bomber Staffel, etc.
- `parent_formation` - Parent wing/group
- `nation` - Germany, Britain, USA, Italy
- `quarter` - Which quarter
- `assigned_to_ground` - Which ground formation supported

#### Command:
- `commander` - Gruppe Kommandeur, Squadron CO, etc.
- `base` - Airfield location

#### Personnel:
- `pilots` - Aircrew count
- `ground_crew` - Maintenance personnel
- `mechanics` - Specialized mechanics
- `armorers` - Ordnance handlers
- `signals` - Radio/communications
- `total` - Total personnel

#### Aircraft:
- `total` - Total aircraft on strength
- `operational` - Combat-ready aircraft
- `variants` - Specific aircraft variants with counts

#### Ordnance:
- `ammunition` - Gun ammunition (rounds)
- `cannon_shells` - Cannon ammunition
- `fuel_liters` - Aviation fuel stocks
- `bombs` - Bomb stocks by type
- `drop_tanks` - External fuel tanks

#### Ground Support Vehicles:
- `fuel_bowsers` - Fuel tankers
- `bomb_dollies` - Ordnance transport
- `trucks` - General transport
- `staff_cars` - Command vehicles

#### Supply:
- `fuel_reserves_days` - Days of aviation fuel
- `ammunition_reserves_days` - Days of ammunition
- `sortie_rate_per_day` - Average sorties per aircraft per day
- `operational_radius_km` - Maximum combat radius

#### Operations History:
- Array of combat operations with dates, sorties, claims, losses

---

## 🎮 Three Primary Outputs (All Units)

### 1. MDBook - Professional Military History Publication

**Purpose**: Human-readable historical reference and analysis

**Structure**:
```
north_africa_campaign_book/
├── SUMMARY.md (Unit Index - all 313-348 units)
├── Quarter Overviews (13 quarters 1940-Q2 through 1943-Q2)
│   ├── Strategic situation
│   ├── Major operations
│   ├── Weather/environmental conditions
│   └── Supply line status
├── Ground Forces Chapters (213 chapters)
│   ├── Division Overview
│   ├── Command Structure
│   ├── Equipment Tables (Ground Vehicles, Artillery)
│   ├── Aircraft Section (Available Air Support)
│   ├── Supply & Logistics (NEW - fuel, ammo, water, operational radius)
│   ├── Operational Environment (NEW - weather, terrain, seasonal impacts)
│   ├── Tactical Doctrine
│   ├── Historical Context
│   ├── Sources & Bibliography
│   └── Data Quality & Known Gaps
├── Air Forces Chapters (~100-135 chapters - Phase 7)
│   ├── Unit Overview
│   ├── Command Structure
│   ├── Personnel (pilots, ground crew)
│   ├── Aircraft & Ordnance
│   ├── Ground Support Equipment
│   ├── Operations History
│   ├── Assignment to Ground Units
│   └── Sources & Data Quality
├── Methodology Documentation
├── Complete Bibliography (Chicago style)
└── Appendices (Glossary, Abbreviations, Maps)
```

**Quality Standards**:
- Minimum 80% confidence per unit
- Tier 1/2 sources only (NO Wikipedia)
- ALL equipment variants detailed (NO rollup counts)
- Complete source citations for every data point
- Cross-references between ground and air units (Phase 8+)

---

### 2. Wargaming Scenarios - Multi-Format (PRIMARY PURPOSE)

**Purpose**: Game-ready scenario data for multiple wargaming systems

**Directory Structure**:
```
scenarios/
├── unit_exports/
│   ├── witw_format/               # War in the West CSV
│   │   ├── ground_units/
│   │   │   ├── germany_1941q2_deutsches_afrikakorps.csv
│   │   │   ├── britain_1941q2_western_desert_force.csv
│   │   │   └── ... (213 ground units)
│   │   └── air_units/             # Phase 7
│   │       ├── luftwaffe_1941q2_i_jg27.csv
│   │       ├── raf_1941q2_274_sqn.csv
│   │       └── ... (~100-135 air units)
│   ├── toaw_format/               # The Operational Art of War
│   │   └── ... (similar structure)
│   └── generic_json/              # Universal scenario format
│       ├── ground_units/
│       └── air_units/
│
├── battle_scenarios/              # Historical operations (Phase 9)
│   ├── operation_battleaxe_1941q2/
│   │   ├── oob_ground.json        # Ground order of battle
│   │   ├── oob_air.json           # Air order of battle (Phase 8+)
│   │   ├── supply_state.json      # Fuel, ammo, water at battle start
│   │   ├── weather.json           # Environmental conditions June 1941
│   │   ├── air_support.json       # Available aircraft, sortie rates
│   │   ├── map_data.json          # Terrain, positions
│   │   └── victory_conditions.json
│   ├── operation_crusader_1941q4/
│   ├── gazala_1942q2/
│   ├── el_alamein_1942q3/
│   └── ... (12+ major operations)
│
└── campaign_data/                 # Campaign system (Phase 10)
    ├── quarterly_transitions/     # How units evolved Q to Q
    ├── supply_routes/             # Tripoli → Benghazi → Tobruk
    ├── airfield_data/             # Luftwaffe/RAF base locations
    └── weather_patterns/          # Seasonal impacts by quarter
```

**Critical Scenario Elements**:
- **Operational state**: Fuel days, ammo days, water reserves at scenario start
- **Weather conditions**: Temperature, visibility, storm probability
- **Supply line status**: Benghazi operational? Tobruk besieged? Distance from Tripoli
- **Aircraft availability**: Fighters, bombers, recon with operational counts and sortie rates
- **Unit readiness**: Percentage operational tanks, artillery, vehicles
- **Air-ground coordination**: Which Luftwaffe/RAF units assigned to which ground formations

**Export Formats**:
1. **WITW CSV**: War in the West compatible format
2. **TOAW**: The Operational Art of War format
3. **Generic JSON**: Modding support for HoI4, Decisive Campaigns, etc.
4. **Custom**: Extensible for additional wargame systems

---

### 3. SQL Database - Queryable Campaign Database

**Purpose**: Complex queries, analysis, scenario generation

**Database Schema**:
```sql
-- Core TO&E tables
CREATE TABLE units (
    unit_id VARCHAR PRIMARY KEY,
    unit_designation VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    unit_type VARCHAR,  -- ground or air
    organizational_level VARCHAR,  -- division, gruppe, etc.
    total_strength INTEGER
);

CREATE TABLE personnel (...);
CREATE TABLE ground_vehicles (...);
CREATE TABLE artillery (...);
CREATE TABLE aircraft (...);

-- Logistics tables (NEW - Phase 1-6)
CREATE TABLE supply_state (
    unit_id VARCHAR REFERENCES units,
    supply_status TEXT,
    operational_radius_km INTEGER,
    fuel_reserves_days DECIMAL,
    ammunition_days DECIMAL,
    water_liters_per_day INTEGER
);

-- Environmental tables (NEW - Phase 1-6)
CREATE TABLE weather_conditions (
    quarter VARCHAR,
    month VARCHAR,
    temperature_min_c INTEGER,
    temperature_max_c INTEGER,
    terrain_type VARCHAR,
    storm_frequency_days INTEGER,
    daylight_hours DECIMAL
);

-- Air support tables (Phase 7-8)
CREATE TABLE air_units (
    unit_id VARCHAR PRIMARY KEY,
    unit_designation VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    unit_type VARCHAR,  -- fighter, bomber, recon
    pilots INTEGER,
    ground_crew INTEGER,
    aircraft_total INTEGER,
    aircraft_operational INTEGER
);

CREATE TABLE air_ground_assignments (
    air_unit_id VARCHAR REFERENCES air_units,
    ground_unit_id VARCHAR REFERENCES units,
    quarter VARCHAR,
    sortie_rate DECIMAL,
    assignment_start DATE,
    assignment_end DATE
);

-- Scenario support tables (Phase 9-10)
CREATE TABLE battle_scenarios (
    scenario_id VARCHAR PRIMARY KEY,
    scenario_name VARCHAR,
    battle_date DATE,
    quarter VARCHAR,
    location VARCHAR,
    weather_id VARCHAR,
    victory_conditions TEXT
);

CREATE TABLE scenario_oob (
    scenario_id VARCHAR REFERENCES battle_scenarios,
    unit_id VARCHAR REFERENCES units,
    fuel_reserves_days DECIMAL,
    ammo_reserves_days DECIMAL,
    operational_percentage DECIMAL
);

CREATE TABLE campaign_transitions (
    unit_id VARCHAR REFERENCES units,
    from_quarter VARCHAR,
    to_quarter VARCHAR,
    changes TEXT,  -- JSON of equipment changes, reorganizations
    disbanded BOOLEAN,
    formed_new BOOLEAN
);

CREATE TABLE supply_routes (
    route_id VARCHAR PRIMARY KEY,
    from_port VARCHAR,
    to_location VARCHAR,
    distance_km INTEGER,
    operational BOOLEAN,
    capacity_tons_per_day INTEGER,
    quarter VARCHAR
);

CREATE TABLE airfields (
    airfield_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    location VARCHAR,
    nation VARCHAR,
    quarter VARCHAR,
    capacity_aircraft INTEGER,
    runway_length_m INTEGER,
    fuel_storage_liters INTEGER
);
```

**Example Queries**:
```sql
-- What was German fuel state before Operation Battleaxe?
SELECT unit_designation, fuel_reserves_days, ammunition_days, operational_radius_km
FROM units u
JOIN supply_state s ON u.unit_id = s.unit_id
WHERE nation = 'Germany' AND quarter = '1941-Q2' AND unit_designation LIKE '%Afrika%';

-- How many operational Bf 109s available June 1941?
SELECT SUM(aircraft_operational) as operational_109s
FROM air_units
WHERE nation = 'Germany' AND quarter = '1941-Q2' AND unit_designation LIKE '%JG%';

-- What air units supported Deutsches Afrikakorps during Battleaxe?
SELECT a.unit_designation, a.unit_type, a.aircraft_operational, aga.sortie_rate
FROM air_units a
JOIN air_ground_assignments aga ON a.unit_id = aga.air_unit_id
WHERE aga.ground_unit_id = 'germany_1941q2_deutsches_afrikakorps';

-- Weather conditions during Operation Crusader?
SELECT * FROM weather_conditions
WHERE quarter = '1941-Q4' AND month = 'November';

-- Supply route capacity during Q2 1941?
SELECT * FROM supply_routes
WHERE quarter = '1941-Q2' AND operational = TRUE;
```

---

## ✅ Success Criteria

### Data Completeness (All 313-348 Units Must Have):

1. ✅ **Complete ground vehicle TO&E** (variant-level, NO rollups)
2. ✅ **Complete artillery breakdown** (field/AT/AA with variants)
3. ✅ **Complete aircraft data** (fighters/bombers/recon with variants)
4. ✅ **Complete logistics data** (supply status, fuel, ammo, water, operational radius)
5. ✅ **Environmental factors** (weather, terrain, seasonal impacts)
6. ✅ **Bottom-up aggregation validation** (parent = sum of children ±5%)
7. ✅ **Minimum 80% confidence** with Tier 1/2 sources only

### Output Quality:

8. ✅ **MDBook generates for all units** (professional quality, complete template)
9. ✅ **WITW scenarios export correctly** (CSV format validated)
10. ✅ **SQL database populated** with complete schema
11. ✅ **12+ battle scenarios** with OOB + supply + weather data
12. ✅ **Campaign transitions** documented quarter-to-quarter

### Scenario-Specific Requirements (Critical):

13. ✅ **Every ground unit has operational radius** (supply line constraints)
14. ✅ **Every ground unit has fuel/ammo reserves** (days at current consumption)
15. ✅ **Every quarter has weather data** (temperature, visibility, storms)
16. ✅ **Major battles have environmental conditions** documented
17. ✅ **Aircraft availability tracked** with operational counts
18. ✅ **Air-ground assignments** documented (which air units supported which ground)

### Quality Standards:

19. ✅ **NO Wikipedia sources** (Tier 1/2 only: Tessin, Army Lists, Field Manuals, Museums)
20. ✅ **ALL equipment variants detailed** (Sherman M4 vs M4A1, Panzer III Ausf F vs G)
21. ✅ **Complete source citations** (page numbers, archive references)
22. ✅ **Data quality sections** in all MDBook chapters (confidence scores, known gaps)

---

## 🚀 Current Status & Immediate Priorities

### Overall Progress:
- **Ground Units**: 18/213 complete (8.5%)
- **Air Force Units**: 0/~100-135 (Phase 7 pending)
- **Overall**: ~5.8% complete

### Current Phase: 1-6 (Ground Forces)

**Immediate Priorities** (Next 1-2 sessions):

1. **Fix 9 Showcase Gaps** (affects all 213 units):
   - Remove Wikipedia from 7 chapters (re-extract with Tier 1/2 sources)
   - Add Infantry Weapons sections to all 18 chapters (data exists, needs extraction)
   - Extract missing Corps units (British XIII Corps, WDF + Italian XX/XXI Corps)
   - Fix empty sections (Bologna, Trieste Division Overviews)
   - Implement QA audit system (pre-publication validation)

2. **Add Supply/Logistics Data** (NEW requirement):
   - Update `unified_toe_schema.json` with Section 6 (supply/logistics)
   - Add to MDBook template as Section 8
   - Extract for existing 18 units
   - Automate for remaining 195 units

3. **Add Weather/Environment Data** (NEW requirement):
   - Update schema with Section 7 (weather/environment)
   - Add to MDBook template as Section 9
   - Research quarterly weather patterns
   - Document seasonal impacts

4. **Resume Autonomous Extraction** (195 remaining):
   - Process ground units in priority order (Italian → British → German → American → French)
   - Run QA auditor every 20 units
   - Target: 80-120 hours autonomous processing

---

## 🎮 Kickstarter Commercial Product Definition

**"North Africa 1940-1943: The Complete Wargamer's Database"**

### Product Description:

The most comprehensive North Africa Campaign database ever created for historical wargaming, featuring:

**Core Content**:
- ✅ 313-348 complete unit TO&Es (ground + air forces)
- ✅ Variant-level equipment detail (NO generic "tanks: 50" - every variant specified)
- ✅ Supply/logistics modeling (fuel reserves, ammo stocks, operational radius)
- ✅ Weather/environmental factors (seasonal impacts on operations)
- ✅ Complete air-ground integration (which Luftwaffe/RAF units supported which formations)

**Scenarios & Campaigns**:
- ✅ 12+ historical battle scenarios (Battleaxe, Crusader, Gazala, El Alamein, etc.)
- ✅ Complete 1940-1943 campaign system (quarterly progression)
- ✅ Supply line modeling (Tripoli → Benghazi → Tobruk routes)
- ✅ Air operations modeling (sortie rates, base locations)

**Formats & Compatibility**:
- ✅ Professional 500+ page MDBook publication
- ✅ WITW-compatible scenario exports (CSV)
- ✅ SQL database (queryable for custom scenarios)
- ✅ JSON exports (modding support for HoI4, Decisive Campaigns, etc.)

**Quality Guarantee**:
- ✅ 80%+ confidence (professional-grade research)
- ✅ Tier 1/2 sources only (Tessin, Army Lists, Field Manuals, Archives)
- ✅ Complete source citations (Chicago style bibliography)
- ✅ Transparent data quality (confidence scores, known gaps documented)

### Target Audience:
- **Primary**: Historical wargamers (WITW, TOAW, board games)
- **Secondary**: Game developers (scenario packs, commercial mods)
- **Tertiary**: Military historians, researchers, educators

### Unique Selling Points:
1. **Most comprehensive**: 313-348 units across ALL nations and organizational levels
2. **Scenario-ready**: Supply states, weather conditions, air support assignments
3. **Multi-format**: Works with multiple wargaming systems
4. **Professionally sourced**: Tier 1/2 sources only, complete citations
5. **Complete air-ground integration**: First database to model air support comprehensively

**Kickstarter Viability**: ✅ HIGHLY VIABLE

This scope is achievable, professionally valuable, and commercially marketable.

---

## 📚 Related Documentation

### Core Project Files:
- **`PROJECT_SCOPE.md`** (this file) - Complete project vision and phased approach
- **`CLAUDE.md`** - Agent instructions and project overview
- **`docs/project_context.md`** - Technical architecture and design decisions
- **`SESSION_SUMMARY.md`** - Current session status and handoff

### Schema & Standards:
- **`schemas/unified_toe_schema.json`** - Ground forces data structure (v3.0 planned)
- **`docs/MDBOOK_CHAPTER_TEMPLATE.md`** - MDBook chapter template (v2.0)
- **`F:\Timeline_TOE_Reconstruction\PROCESSING\STRATEGIC_COMMAND_SUMMARY_SCHEMA.md`** - Iteration 2 baseline

### Agent Configuration:
- **`agents/agent_catalog.json`** - All 16 agent definitions
- **`src/orchestrator.js`** - Main orchestration engine
- **`src/single_session_orchestrator.js`** - Claude Code autonomous mode

### Progress Tracking:
- **`data/output/1941-q2-showcase/SHOWCASE_GAPS.md`** - Current issues identified
- **`data/output/autonomous_XXXXX/GAP_TRACKER.md`** - Data quality tracking
- **`WORKFLOW_STATE.json`** - Autonomous extraction progress

---

## 🔄 Version History

### v1.0.0 (2025-10-13) - Initial Comprehensive Scope Definition
- Defined complete project vision (ground + air forces + scenarios + campaign)
- Total scope: 313-348 units across all phases
- Established phased approach (Ground → Air → Integration → Scenarios → Campaign)
- Added supply/logistics requirements (fuel, ammo, water, operational radius)
- Added weather/environmental requirements (seasonal impacts, terrain effects)
- Clarified aircraft section purpose (air support AVAILABLE to ground units)
- Separated air force units (Phase 7 - own organizational structure)
- Defined scenario generation as primary purpose
- Established Kickstarter commercial product viability
- Created living document for ongoing updates

### Future Updates:
- **v1.1.0** (TBD): [Air forces schema finalization]
- **v1.2.0** (TBD): [Scenario generation specifications]
- **v1.3.0** (TBD): [Campaign system details]

---

## 📝 Update Procedure for This Living Document

When updating PROJECT_SCOPE.md:

1. **Update version number** (semantic versioning: major.minor.patch)
2. **Update "Last Updated" date** at top of file
3. **Add entry to Version History** section with changes
4. **Update relevant MCP memory** entities/observations if schema changes
5. **Git commit** with descriptive message: `docs: Update PROJECT_SCOPE to v1.1.0 - [changes]`
6. **Announce in session** if major changes affect current work

**Minor updates** (typos, clarifications): Patch version (v1.0.1)
**New sections/requirements**: Minor version (v1.1.0)
**Major scope changes**: Major version (v2.0.0)

---

**END OF PROJECT SCOPE v1.0.0**

**All agents, all sessions, all future work must reference this document.**

**For technical implementation details, see `docs/project_context.md`**
**For current session status, see `SESSION_SUMMARY.md`**
**For agent instructions, see `CLAUDE.md`**
