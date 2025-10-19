# Battlegroup Scenario Generation Guide
## From Historical TO&E to Wargame Scenarios

**Created**: October 19, 2025
**Source**: Battlegroup Rules (66-page PDF, 219,289 characters extracted)
**Purpose**: Convert historical TO&E data from North Africa campaign into playable Battlegroup scenarios

---

## Table of Contents

1. [Overview](#overview)
2. [Core Game Mechanics](#core-game-mechanics)
3. [Unit Statistics Required](#unit-statistics-required)
4. [Scenario Structure](#scenario-structure)
5. [Historical TO&E to Battlegroup Mapping](#historical-toe-to-battlegroup-mapping)
6. [Scenario Generation Workflow](#scenario-generation-workflow)
7. [Example Scenario Template](#example-scenario-template)

---

## Overview

**Battlegroup** is a 15mm/20mm WWII tabletop wargame system focused on **combined-arms battles** at the tactical level (squad to battalion). The game emphasizes:

- **Battle Rating System**: Attrition-based victory conditions
- **Theatre-Specific Character**: Different supplements for different theaters/periods
- **Points-Based Force Selection**: Balanced gameplay through points and BR
- **Detailed Unit Statistics**: Vehicle armor, gun penetration, morale, special rules

**Key Insight**: Battlegroup requires **theatre supplements** (not included in core rules) that provide:
- Army lists with points costs and BR values
- Vehicle/gun stat lines
- Theatre-specific special rules
- Historical scenarios

**Our Goal**: Create **North Africa theatre scenarios** using our detailed historical TO&E data, reverse-engineering the mechanics to provide historically accurate battles.

---

## Core Game Mechanics

### 1. Battle Rating (BR) System

**Most Critical Mechanic** - Determines victory/defeat:

- Each unit has a **BR value** (0-5) representing importance to the battlegroup
  - 0 = Unimportant (supply trucks, recon)
  - 1-2 = Minor unit (individual squads, light vehicles)
  - 3-4 = Important (tanks, heavy guns, command units)
  - 5 = Vital (HQ, senior commanders, heavy tanks)

- Units also have **experience level**:
  - `i` = Inexperienced
  - `r` = Regular
  - `v` = Veteran
  - `e` = Elite

- **Total Battlegroup BR** = Sum of all unit BR values

**During Game**:
- Players draw numbered counters (1-5) from shared pot when:
  - Unit destroyed/routed/abandoned
  - Rally (voluntary - remove D6 pinning for 1 counter)
  - Under air attack (first time)
  - Under flamethrower attack (first time)
  - Senior officer casualty

- When **total counters ≥ Battlegroup BR**, you lose (withdraw/retreat)

**Historical Mapping**:
- German units (1941-1942 North Africa): Mostly Veteran/Elite (v/e)
- Italian units (1940-1942): Mostly Regular/Inexperienced (r/i)
- British units (1940-1941): Mixed Regular/Veteran
- British units (1942-1943): Veteran/Elite (Desert Rats)
- American units (1942-1943): Inexperienced transitioning to Regular

---

### 2. Unit Statistics

**Infantry Units**:
- **Rate of Fire (ROF)**: Number of dice rolled when firing (usually 1 per man)
- **Morale**: Quality check (D6 + modifiers vs target number)
- **Movement**: Inches per turn (6" standard, 12" if running)
- **Special Rules**: Anti-tank grenades, flamethrower, engineer, etc.

**Armored Vehicles**:
- **Armour Values**: Front / Side / Rear (numbers 1-16 or letters A-L)
  - Higher = better armor
  - Light tanks: 1-4 or A-D
  - Medium tanks: 5-9 or E-I
  - Heavy tanks: 10-16 or J-P

- **Penetration Values**: Gun effectiveness (1-15+)
  - Anti-tank rifles: 1-3
  - 37mm-50mm guns: 4-7
  - 75mm-88mm guns: 8-12
  - 100mm+ guns: 13-15+

- **Rate of Fire (ROF)**: Shots per turn
  - Most tanks: 1-2 shots
  - Machine guns: 3-6 shots
  - Multiple rocket launchers: Special rules (6x shots, then 2-turn reload)

- **Movement**: Inches per turn
  - Slow tanks (Infantry tanks): 6-8"
  - Medium tanks: 10-12"
  - Fast tanks (Cruisers, light tanks): 14-18"

**Artillery/Guns**:
- **HE Size**: Very Light / Light / Medium / Heavy
  - Very Light: Mortars, 37mm
  - Light: 50mm-75mm
  - Medium: 76mm-105mm
  - Heavy: 120mm-155mm+

- **Penetration**: Same as tank guns
- **Range**: Up to 70" for indirect fire (via spotter)
- **Blast Radius**: 10" from spotter marker

---

### 3. Game Sizes

Four standard sizes based on **points**:

| Size | Min Points | Max Points | Standard | Table Size (20mm) | Table Size (15mm) |
|------|-----------|-----------|----------|-------------------|-------------------|
| **Squad** | 100 | 350 | 250 | 6' x 4' | 4' x 4' |
| **Platoon** | 351 | 750 | 500 | 6' x 6' | 6' x 4' |
| **Company** | 751 | 1250 | 1000 | 6' x 8' | 6' x 6' |
| **Battalion** | 1251 | 2000+ | 1500 | 6' x 10'+ | 6' x 8'+ |

**Recommendation**: Start with **Platoon** (500pts) for North Africa scenarios - represents a reinforced platoon with armor support.

---

### 4. Scenario Types

**Basic Scenarios** (Core Rules):
1. **Attack/Counter-Attack**: Both sides attacking, meeting engagement
2. **Flanking Attack**: Attacker deploys from corner, defender spreads across table
3. **Defence Line**: Defender holds line, attacker must break through
4. **High Ground**: Capture and hold elevated terrain

**Scenario Components**:
- **Deployment Zones**: Where units start
- **Objectives**: Victory conditions (hold objectives, destroy BR, control area)
- **Turn Limit**: Usually 8-12 turns
- **Reinforcements**: Units arriving during game
- **Special Rules**: Weather, night fighting, air support availability

---

## Unit Statistics Required

To create a Battlegroup scenario from our historical TO&E, we need:

###  1. **Infantry Squad Stats**

```
Unit: German Infantry Squad (1941, North Africa)
├─ Size: 10 men (1 NCO, 1 MG34 gunner, 8 riflemen)
├─ Points Cost: ~35-40pts
├─ Battle Rating: 2r (Regular)
├─ Rate of Fire: 10 (1 per man, MG34 has 3 ROF)
├─ Movement: 6" normal, 12" double-time
├─ Morale: 10+ (Veteran: 9+, Elite: 8+)
├─ Special Rules:
│   ├─ Anti-tank grenades (satchel charges)
│   ├─ MG34 (medium machine gun, 3 ROF, 36" range)
│   └─ Can ride in trucks/halftracks
└─ Equipment Notes:
    ├─ 1x MG34 machine gun
    ├─ 1x MP40 submachine gun (NCO)
    └─ 8x Kar98k rifles
```

###  2. **Tank Stats**

```
Vehicle: Panzer III Ausf F (1941)
├─ Points Cost: ~140-160pts
├─ Battle Rating: 3v (Veteran crew)
├─ Armour: Front 7 / Side 5 / Rear 3 (Medium tank)
├─ Gun: 50mm KwK 38 L/42
│   ├─ Penetration: 6 (AP), 8 (APCR special ammo)
│   ├─ HE: Light
│   └─ Range: 48" effective, 72" max
├─ Rate of Fire: 2 (well-trained crew)
├─ Movement: 12" road, 8" cross-country
├─ Crew: 5 (commander, gunner, loader, driver, radio operator)
├─ Special Rules:
│   ├─ Turret (360° firing arc)
│   ├─ Enclosed (protected from small arms)
│   ├─ Radio (can coordinate with other units)
│   └─ Smoke dischargers (once per game)
└─ Historical Notes:
    ├─ Main German medium tank in North Africa 1941-early 1942
    ├─ Outmatched by Matilda II frontally
    └─ Superior crew training gave tactical advantage
```

### 3. **Artillery Stats**

```
Gun: 88mm FlaK 36 (Dual-purpose AA/AT gun)
├─ Points Cost: ~180-220pts (very powerful)
├─ Battle Rating: 4v (Critical unit)
├─ Penetration: 12 (one of best AT guns in game)
├─ HE: Medium
├─ Range:
│   ├─ Direct fire: 72" (vs tanks)
│   ├─ Indirect fire: Via spotter, 70" from observer
│   └─ AA fire: 48" vs aircraft
├─ Rate of Fire: 1-2
├─ Crew: 6 men
├─ Movement: Towed (requires prime mover)
├─ Special Rules:
│   ├─ Heavy AT Gun (exceptional penetration)
│   ├─ Dual-purpose (AT and AA)
│   ├─ Large target (easy to spot, -1 Cover)
│   └─ Slow to redeploy (must limber/unlimber)
└─ Historical Notes:
    ├─ Feared by British tank crews
    ├─ Could defeat any Allied tank in North Africa frontally
    └─ Often used in direct fire role (against doctrine)
```

---

## Historical TO&E to Battlegroup Mapping

### Mapping Process

Our historical TO&E data provides **exact equipment counts** (e.g., "60x Panzer III Ausf F, 20x Panzer IV Ausf D"). Battlegroup scenarios need:

1. **Points-based selection** (not exact historical counts)
2. **Battle Rating values** (importance to force)
3. **Special rules** (historical doctrine, tactics)
4. **Scenario context** (date, location, objectives)

**Solution**: Create **historical scenarios** that use points to *approximate* historical forces, then add **scenario special rules** to enforce historical constraints.

### Example Mapping

**Historical**: 15th Panzer Division, 1941-Q2
**Historical Count**:
- 155x Panzer II
- 71x Panzer III
- 20x Panzer IV
- 10x Command tanks
- 3,000+ infantry (3 battalions)
- 12x 105mm howitzers
- 12x 88mm FlaK guns
- 200+ trucks/halftracks

**Battlegroup Scenario** (Platoon-size, 500pts):

**German Force** (~500pts total):
```
Panzer Platoon:
├─ 1x Panzer IV Ausf D (command tank)     ~180pts, BR 3v
├─ 3x Panzer III Ausf F                   ~450pts, BR 9v (3x3v)
├─ Total: ~630pts, BR 12

Adjust to 500pts:
├─ 1x Panzer IV Ausf D                    ~180pts, BR 3v
├─ 2x Panzer III Ausf F                   ~300pts, BR 6v
├─ 1x Infantry squad (riding in SdKfz 251) ~50pts, BR 2v
├─ Total: ~530pts, BR 11
```

**British Force** (~500pts total, June 1941 Battleaxe operation):
```
├─ 2x Matilda II                          ~400pts, BR 6v
├─ 1x Infantry section (8 men)            ~30pts, BR 1r
├─ 1x 2-pdr AT gun                        ~60pts, BR 3r
├─ Total: ~490pts, BR 10
```

**Scenario Special Rule**: *Historical Engagement Doctrine*
- German tanks may use "Feuer und Bewegung" (Fire and Movement) special rule: One tank fires to suppress, another advances
- British Matildas are slow (6" move) but heavily armored (Front 11, immune to 50mm guns frontally)
- German player gets first turn (historical aggressor)

---

## Scenario Generation Workflow

### Phase 1: Extract Historical Data

**Input**: Unit TO&E JSON from our database
**Extract**:
1. Unit composition (squads, vehicles, guns)
2. Equipment specifications (from master_database.db)
3. Date and location
4. Historical battle context

**Example**:
```json
{
  "unit": "15th Panzer Division",
  "quarter": "1941-Q2",
  "tanks": {
    "Panzer II": 155,
    "Panzer III Ausf F": 71,
    "Panzer IV Ausf D": 20
  },
  "infantry": {
    "rifle_companies": 9,
    "mg_companies": 3,
    "mortar_companies": 1
  },
  "artillery": {
    "105mm howitzers": 12,
    "88mm FlaK": 12
  },
  "historical_context": "Operation Battleaxe, June 1941, Halfaya Pass"
}
```

### Phase 2: Determine Scenario Size

Based on **player preference** and **historical battle scale**:

| Historical Scale | Scenario Size | Points | Units |
|-----------------|---------------|--------|-------|
| Skirmish (platoon vs platoon) | Squad | 250pts | 1-2 tanks, 1-2 squads per side |
| Company action | Platoon | 500pts | 3-5 tanks, 2-4 squads, 1-2 guns |
| Battalion attack | Company | 1000pts | 8-12 tanks, 5-8 squads, 2-4 guns |
| Full divisional battle | Battalion | 1500pts+ | 15+ tanks, 10+ squads, artillery support |

### Phase 3: Reverse-Engineer Points Costs

**We don't have official Battlegroup North Africa supplement**, so we must estimate:

**Method 1**: Use existing supplements as reference (Normandy, Eastern Front)
**Method 2**: Use **relative power** formula:

```
Points Cost Formula:

Tank Points = Base + Armor Bonus + Gun Bonus + Special Rules

Base = 80pts (light tank) to 200pts (heavy tank)

Armor Bonus:
  - Front armor 1-4: +0pts
  - Front armor 5-7: +20pts
  - Front armor 8-10: +40pts
  - Front armor 11-13: +60pts
  - Front armor 14-16: +100pts

Gun Bonus:
  - Penetration 1-4: +0pts
  - Penetration 5-7: +20pts
  - Penetration 8-10: +40pts
  - Penetration 11-13: +60pts
  - Penetration 14+: +80pts

Special Rules: +10-50pts each
  - Radio: +10pts
  - Smoke: +5pts
  - Fast: +15pts
  - Stabilized gun: +20pts
```

**Example**: Panzer III Ausf F (1941)
```
Base (Medium tank): 100pts
Armor (Front 7): +20pts
Gun (50mm Pen 6): +20pts
Special (Radio, Smoke): +15pts
Total: ~155pts
```

### Phase 4: Assign Battle Rating

**BR Assignment Rules**:

**Infantry**:
- Regular squad: BR 1-2
- Veteran squad: BR 2
- Elite squad: BR 2-3
- Command squad: BR 3

**Vehicles**:
- Light tanks/armored cars: BR 2-3
- Medium tanks: BR 3-4
- Heavy tanks: BR 4-5
- Command vehicles: BR 4-5

**Guns**:
- Light AT guns (37mm-50mm): BR 2-3
- Medium AT guns (57mm-75mm): BR 3-4
- Heavy AT guns (88mm, 17-pdr): BR 4-5
- Artillery (off-table): BR 0 (don't count)
- Artillery (on-table): BR 3-4

**Support**:
- Supply trucks: BR 0-1
- Command post: BR 3-4
- Medics: BR 2
- Observers: BR 1-2

**Experience Levels** (North Africa):

German:
- 1940-1941: Veteran/Elite (v/e)
- 1942-1943: Veteran (v)
- 1943 Late: Regular/Veteran (r/v)

Italian:
- 1940-1941: Regular/Inexperienced (r/i)
- 1942-1943: Regular (r)

British:
- 1940-1941: Regular (r)
- 1941-1942 (Desert Rats): Veteran/Elite (v/e)
- 1943: Veteran (v)

American:
- 1942-1943 Early: Inexperienced (i)
- 1943 Late: Regular/Veteran (r/v)

### Phase 5: Write Scenario Narrative

**Essential Components**:

1. **Title**: "Battle of Halfaya Pass, June 15, 1941"
2. **Historical Context** (2-3 paragraphs):
   - Strategic situation
   - Forces involved
   - Objectives of both sides
3. **Forces**:
   - Points allocation for each side
   - Unit lists with BR values
   - Total Battlegroup BR
4. **Deployment**:
   - Map with deployment zones
   - Terrain setup
   - Objectives marked
5. **Victory Conditions**:
   - Primary: Break enemy BR
   - Secondary: Hold objectives, destroy specific units
6. **Special Rules**:
   - Historical constraints
   - Weather/terrain effects
   - Reinforcement schedule
7. **Designer Notes**:
   - Historical accuracy notes
   - Balance considerations
   - Suggestions for variation

---

## Example Scenario Template

```markdown
# Battle of Halfaya Pass
## Operation Battleaxe, June 15, 1941

### Historical Context

In June 1941, the British launched Operation Battleaxe to relieve Tobruk
and drive Rommel's forces back across Cyrenaica. The 15th Panzer Division,
holding the critical Halfaya Pass (known to British soldiers as "Hellfire Pass"),
faced a determined assault by British Matilda infantry tanks and Cruiser tanks
of the 4th Armoured Brigade.

The Germans had fortified the pass with dug-in 88mm FlaK guns and infantry
positions. The British, unaware of the 88mm guns' lethality against armor,
advanced directly into a killing zone.

This scenario recreates the morning assault on June 15, 1941.

### Forces

**GERMAN BATTLEGROUP** (500 points, BR 15)

Headquarters:
- 1x Panzer III Ausf F (Command tank)          165pts, BR 4v

Panzer Platoon:
- 2x Panzer III Ausf F                         330pts, BR 6v

Anti-Tank Support:
- 1x 88mm FlaK 36 (dug in)                     220pts, BR 5v

Supporting Infantry:
- 1x Infantry squad (in positions)              40pts, BR 2r

**Total: 755pts, BR 17** (Reduce to 500pts by removing 1x Panzer III)

**Adjusted Force**:
- 1x Panzer III Ausf F (Command)               165pts, BR 4v
- 1x Panzer III Ausf F                         165pts, BR 3v
- 1x 88mm FlaK 36                              220pts, BR 5v
- 1x Infantry squad                             40pts, BR 2r
**Total: 590pts, BR 14**

Adjust further:
- 1x Panzer III Ausf F (Command)               165pts, BR 4v
- 1x 88mm FlaK 36                              220pts, BR 5v
- 2x Infantry squads                            80pts, BR 4r
**Total: 465pts, BR 13**

---

**BRITISH BATTLEGROUP** (500 points, BR 15)

Armored Platoon:
- 3x Matilda II                                540pts, BR 9v

Supporting Infantry:
- 1x Infantry section                           30pts, BR 1r

**Total: 570pts, BR 10** (Reduce to 500pts)

**Adjusted Force**:
- 2x Matilda II                                360pts, BR 6v
- 1x Crusader II                               120pts, BR 3v
- 1x Infantry section                           30pts, BR 1r
**Total: 510pts, BR 10**

Final adjustment:
- 2x Matilda II                                360pts, BR 6v
- 1x Infantry section (10 men)                  35pts, BR 1r
- 1x 2-pdr AT gun                               60pts, BR 3r
- 1x Universal Carrier (transport)              40pts, BR 1r
**Total: 495pts, BR 11**

### Table Setup

**Table Size**: 6' x 4' (suitable for 20mm miniatures)

**Terrain**:
- Halfaya Pass runs diagonally across table (rocky escarpment)
- German positions on high ground (East side)
- British advance from West
- Sparse desert scrub, a few wadis (dry riverbeds)

**Objectives**:
1. German HQ position (hilltop, East edge)
2. Pass entrance (center)
3. Southern ridge (South edge)

### Deployment

**German** (Defender):
- Deploy anywhere East of center line
- 88mm FlaK must be dug in (prepared position)
- Infantry must be in foxholes/sangars
- Tanks may start off-table (arrive Turn 2 on D6 roll of 3+)

**British** (Attacker):
- Deploy within 12" of West table edge
- Matildas must advance (cannot sit static Turn 1-3)
- Infantry may ride in carriers

### Victory Conditions

**Primary Objective**: Break enemy Battlegroup Rating

**Secondary Objectives** (each worth +5 BR to your starting total):
- Hold 2 of 3 objectives at game end
- Destroy enemy command unit
- Take fewer than 5 casualties (infantry/crew)

**Game Length**: 10 turns or until one side breaks

### Special Rules

1. **Dug-In 88mm**: The 88mm FlaK gun is in a prepared position
   - +2 Cover save
   - -2 to enemy spotting rolls
   - Cannot move without abandoning position

2. **Slow Matildas**:
   - 6" movement (cross-country)
   - 8" movement (road - none available!)
   - Heavily armored: Front 11, Side 8, Rear 7
   - Immune to 50mm Panzer III guns frontally (requires side/rear shots)

3. **88mm Surprise**:
   - British player does not know 88mm is present until it fires
   - First shot: If hits, British must take +1 BR counter (shock value)

4. **Desert Conditions**:
   - No aircraft (sandstorm grounded air support)
   - Visibility: 48" maximum
   - Difficult terrain: Wadis count as difficult (half movement)

### Historical Outcome

Historically, the 88mm guns devastated the British tank attack. Matildas,
advancing slowly across open ground, were picked off one by one. The British
lost 11 of 12 Matildas committed to the assault. The Germans held Halfaya Pass
for another six months.

### Designer Notes

This scenario is deliberately challenging for the British player:
- Matildas are slow, limiting tactical options
- 88mm FlaK gun can penetrate Matilda armor frontally
- Open terrain favors defender

**Historical Accuracy**:
- British underestimated 88mm threat (realistic in scenario)
- German combined-arms defense (infantry, AT guns, tanks in reserve)
- Points slightly favor British to compensate for defender advantage

**Balance Suggestions**:
- For more balanced game: Remove 88mm, replace with 50mm PaK 38 gun
- For British advantage: Add artillery spotter with 25-pdr battery support
- For historical accuracy: Play as written, British player needs clever tactics!

**Variations**:
1. **Night Attack**: British attack at dawn (reduced visibility, -1 to hit)
2. **Artillery Support**: British get 25-pdr battery (1st priority, 3+ comm check)
3. **Larger Battle**: Scale to 1000pts (Company-size) with more tanks, infantry

### Map

```
        NORTH
          ↑

WEST ←  [====================]  → EAST
          Halfaya Pass

German (Defender) East side:
  [88] = 88mm FlaK (dug in)
  [P3] = Panzer III
  [IN] = Infantry squad

British (Attacker) West side:
  [M2] = Matilda II
  [AT] = 2-pdr AT gun
  [IN] = Infantry section

Objectives:
  (1) = German HQ (hilltop)
  (2) = Pass entrance
  (3) = Southern ridge

+---------------------------EAST-------------------------+
|                                                        |
|  (1) [88]         [IN]                                |
|    Hilltop         Foxholes                           |
|                                                        |
|            (2)                                         |
|         Pass Center     [P3] (Reserve, arrives T2)    |
|                                                        |
|                 [IN]                                   |
|              Sangar                                    |
|                                                        |
|     (3)                                                |
|  Southern Ridge                                        |
|                                                        |
+---------------------------CENTER-----------------------+
|                                                        |
|                                                        |
| Wadi  (Difficult terrain)                            |
|  ≈≈≈                                                   |
|                                                        |
|  Scrub   Scrub                                        |
|   ∴      ∴                                             |
|                                                        |
| [M2] [M2]                                             |
| [IN] [AT]                                             |
| British Deployment Zone (within 12" of edge)          |
|                                                        |
+---------------------------WEST------------------------+
```

### Briefings

**German Commander**:

Your mission is to hold Halfaya Pass against the British assault. You have
prepared defensive positions and dug in your deadly 88mm anti-tank gun. The
enemy does not yet know of its presence - use this surprise to devastating effect.

Your Panzer III reserves will arrive on Turn 2 (roll 3+ on D6). Use them to
counterattack any British penetration or to protect your 88mm if it comes under
direct assault.

Your infantry are veterans of the French campaign. Trust them to hold their
positions under fire.

**Victory**: Break the British attack (reduce their BR to 0) while preserving
your own forces. Hold at least 2 objectives.

**British Commander**:

Intelligence reports minimal opposition at Halfaya Pass. Your slow but heavily
armored Matildas are immune to most German anti-tank weapons. Use your armor
superiority to overrun the German positions and seize the pass.

Beware: The pass is on high ground, giving the Germans good fields of fire. Use
wadis for cover where possible, but remember your Matildas are slow in difficult
terrain.

Your 2-pdr AT gun provides support but must be positioned carefully - it's
vulnerable to German return fire.

**Victory**: Seize the pass (hold 2 of 3 objectives) and break German resistance.
Your tanks are valuable - try to minimize losses.

---

**End of Scenario**
```

---

## Next Steps for Project

### 1. Create Battlegroup Equipment Database

Similar to our WITW/OnWar/WWIITANKS integration, create:

```
database/battlegroup_stats.db

Tables:
- bg_vehicles (vehicle_id, name, nation, front_armor, side_armor, rear_armor, gun_pen, he_size, rof, movement, points_cost, br_value)
- bg_guns (gun_id, name, caliber, pen, he_size, range, points_cost, br_value)
- bg_infantry (unit_id, name, nation, size, equipment, rof, points_cost, br_value, experience)
- bg_special_rules (rule_id, name, description, points_modifier)
```

### 2. Create Scenario Generator Script

```javascript
// scripts/generate_battlegroup_scenario.js

Input:
- Unit TO&E JSON (from Phase 6)
- Scenario size (squad/platoon/company/battalion)
- Date and historical context

Process:
1. Extract equipment counts from TO&E
2. Query battlegroup_stats.db for points costs and BR values
3. Scale forces to match scenario size
4. Generate balanced opposition (historical enemy force)
5. Create scenario narrative with deployment, objectives, special rules

Output:
- Markdown scenario file (ready to print/play)
- Tabletop Simulator mod (future enhancement)
```

### 3. Map Historical Battles to Scenarios

Use our extracted units to create:
- **Operation Battleaxe** (June 1941): British vs German/Italian
- **Operation Crusader** (November 1941):
- **Gazala** (May 1942)
- **El Alamein** (October-November 1942)
- **Operation Torch** (November 1942): American debut
- **Tunisia** (1942-1943): Final North Africa battles

Each operation becomes a **campaign book** with:
- 6-12 linked scenarios
- Campaign rules (carry-over units, replacements, experience gains)
- Historical maps and photos
- Designer notes on historical accuracy

---

## Technical Implementation Notes

### Equipment Matching

Our master_database.db already has penetration data for guns (wwiitanks_gun_data table).

**Mapping WWIITANKS Penetration to Battlegroup**:

WWIITANKS uses mm penetration at distances (100m, 500m, 1000m, 2000m).
Battlegroup uses abstract Penetration values (1-15+).

**Conversion Formula**:
```
Penetration at 500m (mm) → Battlegroup Pen Value

0-30mm   → Pen 1-2 (AT rifles, 20mm guns)
31-50mm  → Pen 3-4 (37mm guns)
51-70mm  → Pen 5-6 (50mm guns)
71-90mm  → Pen 7-8 (75mm guns short barrel)
91-110mm → Pen 9-10 (75mm guns long barrel, 76mm)
111-130mm → Pen 11-12 (88mm guns, 17-pdr)
131-150mm → Pen 13-14 (100mm+ guns)
151+mm   → Pen 15+ (Heavy AT guns, 122mm+)
```

Example:
```
50mm KwK 38 L/42 (Panzer III Ausf F):
- WWIITANKS: 61mm @ 500m
- Battlegroup: Pen 6
```

### Armor Mapping

WWIITANKS armor (mm) → Battlegroup Armor Value:

```
0-20mm   → Armor 1-2 (Light armor, armored cars)
21-30mm  → Armor 3-4 (Light tanks)
31-50mm  → Armor 5-6 (Medium tanks early)
51-70mm  → Armor 7-8 (Medium tanks mid)
71-90mm  → Armor 9-10 (Medium/Heavy tanks)
91-120mm → Armor 11-12 (Heavy tanks)
121-150mm → Armor 13-14 (Very heavy tanks)
151+mm   → Armor 15-16 (Superheavy tanks - rare)
```

---

## Summary

**Key Takeaways**:

1. **Battlegroup is perfect for our project**: Points-based, detailed stats, historical scenarios
2. **Battle Rating System** is brilliant: Abstracts morale/attrition without micro-management
3. **We can reverse-engineer scenarios** even without official North Africa supplement
4. **Our database integration** (WITW/OnWar/WWIITANKS) provides ALL data needed:
   - Armor values (WWIITANKS)
   - Penetration data (WWIITANKS guns table)
   - Production numbers (OnWar)
   - Historical organization (Tessin, Army Lists, Field Manuals)

5. **Scenario generation is feasible**:
   - Extract TO&E → Calculate points → Assign BR → Write narrative
   - Estimated 2-3 hours per scenario (with templates)
   - Can generate 50-100 scenarios from our North Africa data

**Next Session Goals**:
1. Create `battlegroup_stats.db` schema
2. Import sample vehicles/guns from master_database.db
3. Write `generate_battlegroup_scenario.js` script
4. Generate first test scenario (Operation Battleaxe platoon action)

---

**End of Guide**
