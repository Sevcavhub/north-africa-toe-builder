# BattleGroup Game Mechanics Reference
## For Scenario Generation System

**Document Version**: 1.0
**Source**: BattleGroup Rules PDF (Core Rulebook)
**Extracted Pages**: 1-10, 11-20, 21-30, 31-40, 51-60, 61-66
**Purpose**: Reference document for implementing scenario slicer

---

## Table of Contents

1. [Game Size and Points](#game-size-and-points)
2. [Force Selection Rules](#force-selection-rules)
3. [Battle Rating System](#battle-rating-system)
4. [Scenario Structure](#scenario-structure)
5. [Scenario Examples](#scenario-examples)
6. [Orders and Activation](#orders-and-activation)
7. [Key Game Mechanics](#key-game-mechanics)

---

## Game Size and Points

### Standard Game Sizes

BattleGroup uses four game size categories, each with corresponding points ranges and recommended table sizes:

| Game Size | Minimum Points | Maximum Points | Standard Points | 20mm Table | 15mm Table |
|-----------|---------------|----------------|-----------------|------------|------------|
| **Squad** | 100 | 350 | 250 | 6' x 4' | 4' x 4' |
| **Platoon** | 351 | 750 | 500 | 6' x 6' | 6' x 4' |
| **Company** | 751 | 1,250 | 1,000 | 6' x 8' | 6' x 6' |
| **Battalion** | 1,251 | 2,000+ | 1,500 | 6' x 10'+ | 6' x 8'+ |

**Source**: Page 10

### Points Value Concept

From page 10:
> "Points values are how you pick a force. In simplistic terms, the higher the points value, the 'better' the unit. A powerful tank with a big gun is worth more than an infantryman with a mere rifle. Heavy artillery is worth more than light artillery."

**Key principle**: Equal points = theoretically even game, though tactics, luck, and national advantages will affect outcomes.

---

## Force Selection Rules

### Army List Structure

Forces are built from **Theatre Supplements** which provide:
- Army lists with unit types
- Points values for each unit
- Battle Rating values for each unit
- Special rules per theatre/nation

### Force Categories

From page 10-11, forces include:

**Core Categories**:
- **Infantry**: Squads, teams, support weapons
- **Tanks**: Armored fighting vehicles
- **Artillery**: On-table guns, mortars, off-table support
- **Reconnaissance Units**: Scout vehicles, cavalry
- **Command Units**: Officers, signals teams
- **Support Assets**: Medics, engineers, supply units
- **Logistics Units**: Transport, supply trucks
- **Defenses**: Bunkers, trenches, minefields

### Minimum Requirements

**From page 12-13 (Officers):**
> "As well as the dice roll, the player also adds to this score his battlegroup's total number of officers. These are the men running the battle and passing on the orders, so the more officers in a battlegroup, the more effective a fighting force will be."

**Required Tracking**:
- Number of officers (affects orders per turn)
- Number of scout units (affects deployment, initiative)
- Battle Rating total (determines defeat threshold)

### Organization Principle

From page 60, forces use a **Battlegroup Organization Chart** with these sections:

1. **Forward Headquarters** (pts/BR)
2. **Infantry** (pts/BR)
3. **Tanks** (pts/BR)
4. **Artillery** (pts/BR)
5. **Reconnaissance Units** (pts/BR)
6. **Support Assets** (pts/BR)
7. **Logistics Units** (pts/BR)
8. **Engineer Units** (pts/BR)
9. **Special Units** (pts/BR)
10. **Defenses** (pts/BR)
11. **Additional Fire Support** (priority-based)

---

## Battle Rating System

### Core Concept

From page 43 (referenced multiple times):
> "Units also have a battle rating. This is discussed in detail later, but a unit's battle rating is a gauge of the effectiveness and importance of your battlegroup, and will be very important in deciding whether you win or lose a game."

### Battle Counter Mechanics

**Battle Counters are drawn when**:

1. **Unit Destroyed** (page 43)
   - Any unit destroyed, routs, or abandoned gun/vehicle

2. **Rally Phase** (page 15)
   - Remove D6 pinning markers per counter drawn

3. **Under Air Attack** (page 51-52)
   - First time any unit is attacked by aircraft

4. **Under Flamethrower Attack** (page 28-29)
   - First time attacked by flamethrowers

5. **Senior Officer Destroyed** (page 43)
   - Extra counter if destroyed unit was senior officer

6. **Out-Scouted** (page 43)
   - If enemy has more scout units

7. **Enemy Captures Objective** (page 43)
   - When opponent claims an objective

8. **Tactical Co-ordination** (page 15)
   - Senior officer uses special order to rally pinned unit

### Battle Counter Values

From page 63 (Battle Counters sheet):
- Counters numbered **1-5**
- **Special counters**:
  - "Air Attack" (multiple)
  - "Mine Strike"
  - "Confusion"
  - "Ammo Low"
  - "Break Down"
  - "Beyond the Call of Duty"

### Defeat Condition

**Victory condition** (repeated in all scenarios, pages 57-60):
> "The first battlegroup to exceed its total Battle Rating must withdraw and loses the battle. Their opponent is the winner."

---

## Scenario Structure

### Required Scenario Elements

Based on scenarios on pages 57-60, all scenarios need:

#### 1. Scenario Header
- **Title**: Descriptive name
- **Scenario Type**: Meeting Engagement, Attack/Defence
- **Situation Report**: Historical/narrative context

#### 2. Terrain Setup
**Standard instruction** (all scenarios):
> "Set up the terrain in any mutually agreed manner."

**Special terrain requirements** vary per scenario (see examples below)

#### 3. Victory Conditions
**Standard format**:
> "The first battlegroup to exceed its total Battle Rating must withdraw and loses the battle."

**Alternative conditions**:
- Objective capture (multiple objectives)
- Time limits (not shown in extracted pages)

#### 4. Deployment Sequence

**Standard deployment steps** (from page 57-60):

1. **Determine Forces**
   - Initial forces vs reserves
   - Reconnaissance forces
   - Main forces

2. **Determine Table Edges/Zones**
   - Roll-off using scouts
   - Fixed zones for attacker/defender

3. **Place Objectives**
   - Number varies (D3+2, or fixed 3-4)
   - Distance restrictions (10" from edges/each other)

4. **Weather Conditions**
   - Roll D6: 1 = thunderstorm (grounds aircraft)

5. **Deploy Units**
   - Scouts first (usually)
   - Ambush fire orders (limited number)
   - Initial bombardment effects (defender scenarios)

6. **Determine First Turn**
   - Usually roll-off + scout bonus

#### 5. Reinforcement Rules

**Arrival mechanics** (pages 57-59):

**Squad/Platoon games**: D6 units per turn
**Company games**: 2D6 units per turn
**Battalion games**: 3D6 units per turn

**Typical arrival timing**:
- Turn 2+ for main forces
- Turn 4-5 for second wave/reserves

---

## Scenario Examples

### Scenario 1: Attack/Counter-Attack (Page 57)

**Type**: Meeting Engagement

**Situation**:
> "An enemy attack has broken through and is threatening to penetrate deeper into your division's rear echelons. Your battlegroup has been held in reserve to counter just such an eventuality. Both sides are on the march."

**Key Mechanics**:

1. **Terrain**: Mutually agreed
2. **Victory**: Battle Rating exceeded
3. **Deployment**:
   - Roll D6 + scout units → highest chooses corner
   - Place 4 objectives (scout advantage places first)
   - No objective within 10" of another or table edge
4. **Weather**: Roll D6, 1 = thunderstorm (no aircraft)
5. **Scouts Deploy First**:
   - Anywhere in own half
   - Not within 10" of center line
   - Side with NO scouts: opponent scouts can deploy anywhere + start on Ambush Fire
6. **First Turn**: Roll D6 + scouts, highest goes first
7. **Reinforcements**: Turn 2+, D6* units arrive per turn at table edge (within 20" of corner)

**Deployment Zones**: 20" from each table corner

---

### Scenario 2: Flanking Attack (Page 58)

**Type**: Meeting Engagement

**Situation**:
> "The vanguard of your battlegroup has sighted the enemy. You have recalled your forward reconnaissance units to assist as a flanking force."

**Key Mechanics**:

1. **Initial Forces**: D6 units (NO scouts), rest arrive as reinforcements
2. **Objectives**: D3+2, center of table must be first
3. **Deployment Zones**: Two zones, 20" from opposite corners
4. **Flanking Zones**: Other two corners, determined by roll + scouts
5. **Scout Deployment**: ALL scouts deploy in flanking zone (20" from corner)
6. **Reinforcements**: Turn 2+, D6* units at main deployment zone

**Special Rule**: Creates classic pincer/flanking dynamic

---

### Scenario 3: Defence Line (Page 59)

**Type**: Attack/Defence

**Situation**:
> "Your battlegroup's objective is to advance and smash through an enemy defence line. The enemy lines have already been under heavy artillery fire. Be aware that reinforcements will be closing in."

**Key Mechanics**:

1. **Defender Chooses Table Edge**: Attacker deploys opposite
2. **Attacker Forces**:
   - **Probing Force**: ALL scouts + up to 3 other units (deploy turn 1)
   - **Main Force**: Rest arrive turn 3+ (D6* per turn)
3. **Defender Forces**:
   - **Initial**: ALL defenses + 2D6 units in "Front Line Zone" (central third of table)
   - **Reinforcements**: Turn 5+, D6* per turn
4. **Objectives**: 3 total (defender places 2 in front line, 1 elsewhere, 10" restrictions)
5. **Ambush Fire**: D3 defender units start on Ambush
6. **Preparatory Bombardment**: D3 defender units start pinned
7. **First Turn**: Attacker goes first

**Front Line Zone**: Central third of table (lengthwise)

**Special Rule**: Defender CANNOT claim "all objectives secured" victory

---

### Scenario 4: High Ground (Page 60)

**Type**: Attack/Defence

**Situation**:
> "Your battlegroup's objective is to clear and capture high ground along the division's route of advance. Attack will be unleashed in two waves."

**Key Mechanics**:

1. **Terrain Requirement**: Hill in defender's half
2. **Attacker Forces**:
   - **First Assault Wave**: Half of battlegroup (deploy turn 1, within 10" of edge)
   - **Second Assault Wave**: Half of battlegroup (arrive turn 4, all at once)
3. **Defender Forces**:
   - **Initial**: Half of battlegroup + 3 FREE defenses on/near hill
   - **Reserves**: Turn 4+, D6 units per turn
4. **Free Defenses**: Always included:
   - 1x MMG Bunker
   - 10" Trench
   - 1x Minefield
5. **Objectives**: 3 total (first on hill, then alternating placement, 10" restrictions)
6. **Ambush Fire**: D6 defender units can start on Ambush
7. **First Turn**: Attacker goes first

**Special Rule**: Defender gets significant defensive advantage with free defenses

---

## Orders and Activation

### Orders Per Turn (Page 12-13)

**Orders Dice**:
- Squad game: 1D6 + officers
- Platoon game: 2D6 + officers
- Company game: 3D6 + officers
- Battalion game: 4D6 + officers

**Example from page 13**:
> "Company-level game, with four officers on player A's side and three on player B's side. Player A rolls 3D6 and add 4 for his orders total. He rolls 2, 3 and 5. So he will have (2+3+5+4 officers) or 14 orders to issue."

### Standard Orders (Page 14-15)

1. **Manoeuvre and Fire**: Move up to full distance, then fire once
2. **Fire and Manoeuvre**: Fire once, then move up to full distance
3. **Top Speed**: Move up to 2x distance, no firing
4. **Open Fire!**: Stationary, fire twice (same or different targets)
5. **Disembark/Embark**: Transport moves, then passengers exit/enter (within 4")
6. **Unlimber/Limber**: Towed gun deployment/pickup (within 4")
7. **Infantry Close Assault**: Move + assault (requires experience test)
8. **Request Artillery Fire**: Spotter calls indirect fire
9. **Tactical Co-ordination**: Senior officer rallies pinned unit (costs Battle Counter)
10. **Re-arm**: Re-supply unit provides ammunition
11. **Engineering**: Place charges, clear mines
12. **Repair**: Attempt to fix immobilized/destroyed vehicle
13. **Recover**: Tow damaged vehicle

### Reaction Orders (Page 13-14)

**Ambush Fire** (Reaction Order):
- Unit waits, interrupts enemy turn
- Uses "Open Fire!" order (fire twice)
- Can target two separate units
- Cannot use indirect artillery/mortars

**Reserve Move** (Reaction Order):
- Unit waits, interrupts enemy turn
- Uses "Top Speed" order (move 2x distance)
- Can withdraw off table edge (within 10")

---

## Key Game Mechanics

### Unit Experience Levels (Page 50)

Used for morale tests, close assaults, tactical coordination:

| Experience | Test Required |
|------------|---------------|
| Inexperienced | 4+ |
| Regular | 3+ |
| Veteran | 2+ |
| Elite | 2+ |

### Pinning Mechanic

**Pinned units** (page 21):
> "A pinned unit (be it an infantry squad, deployed gun, tank, or anything else) is one that is under so much fire that it can do little else except look to its own survival. A pinned unit cannot be given any orders."

**Rally Phase** (page 15):
- Take Battle Counters to remove D6 pinning markers per counter
- Removes at end of own turn

### Observation Rules (Page 24)

Units must observe targets before firing (Aimed Fire):

| Target Type | Condition | Roll Needed |
|-------------|-----------|-------------|
| Infantry in Open | Firing | 2+ |
| Infantry in Open | Not firing | 3+ |
| Obscured Infantry | Firing | 3+ |
| Obscured Infantry | Not firing | 4+ |
| Gun in Open | Firing | Automatic |
| Gun in Open | Not firing | 2+ |
| Vehicle in Open | Firing | Automatic |
| Vehicle in Open | Not firing | 2+ |
| Aircraft | Any | Automatic |

**Modifiers**:
- +1 if observer has Scout special rule
- -1 if target is 3-man team or smaller

### Movement Ranges (Page 17-18)

| Unit Type | Off-Road | On-Road |
|-----------|----------|---------|
| Infantry | 5" | 5" |
| Cavalry | 8" | 10" (12" charge once per game) |
| Bicycle | 3" | 10" |
| Horse-towed gun | 4" | 6" |
| Vehicles | See profile | See profile |
| Aircraft | Anywhere | Anywhere |

**Manhandled Guns**:
- Very Light: 3" off-road, 4" on-road
- Light: 2" off-road, 3" on-road
- Medium: 1" off-road, 2" on-road
- Heavy: Cannot be manhandled

### Fire Types

**Area Fire** (Page 22-23):
- Primary purpose: Pin enemy
- Uses Rate of Fire (RoF) or HE rating
- Roll to pin → Cover save
- On cover save of 1: also causes 1 casualty

**Aimed Fire** (Page 24-25, 30-34):
- Primary purpose: Destroy enemy
- Requires observation test
- Roll to hit → Cover save (or penetration for armor)
- Causes casualties/destruction

**Indirect Artillery Fire** (Page 35-40):
- Spotter places marker
- Roll for deviation (D6 or 2D6 or 4D6)
- Fire for Effect: each gun fires 2 shots
- Direct hits (6s) vs Pinning (2-5) vs Miss (1)
- Affects all units within 10" of marker

### Special Weapon Notes (Page 28-29)

**Flamethrowers**:
- Man-pack: RoF 10, 5" range, ONE SHOT only
- Vehicle-mounted: RoF 10, 10" range, limited ammo
- Target must be stationary
- Always counts as "in the Open" for saves
- **First use**: Opponent takes Battle Counter (terror effect)

**Mortars**:
- Light (50mm/2"): 5"-20" range, cannot use indirect fire
- Medium (81mm/3"): 10"-90" range, HE 4/4+
- Heavy (120mm/4.2"): 15"-240" range, HE 6/4+

---

## Additional Fire Support System (Page 39-40)

### Priority Requests

Forces can include off-table artillery with priority levels:

**1st Priority**: 2+ to get guns
**2nd Priority**: Higher threshold (see theatre supplements)
**3rd Priority**: Highest threshold (see theatre supplements)

### Communication Checks

After priority succeeds, roll for communication level:

- **Battalion**: Easier roll, smaller guns
- **Regiment**: Medium roll, medium guns
- **Division**: Harder roll, larger guns
- **Corps/Army**: Hardest roll, heaviest guns

**Special units affect communications**:
- Forward Signals Unit: Re-roll one failed check per turn
- Wire Team: +1 to check (removed after use)
- Dispatch Rider: Auto-pass (removed after use)

### Pre-Registered Targets

From page 39:
> "A Pre-Registered Target should be positioned using a sketch map, noting its location anywhere on the table-top before deployment. To fire guns at the Pre-Registered Target, no observer is required. Do not roll for spotter round accuracy or Communications, the barrage will automatically be centred on that point."

### Timed Barrages

From page 39:
> "The battlegroup commander must write down which turn his Timed Barrage will arrive on, after deployment but before the game begins. He must also mark the point on a map of the table that his barrage is aimed at, just as if it was a Pre-Registered Target."

**Characteristics**:
- Arrives automatically on specified turn
- Uses NO orders
- Cannot be cancelled
- One-use only

### Counter-Battery Fire

From page 39:
> "Counter-battery fire missions can only be used against enemy off-table batteries; they cannot be used against enemy guns on the tabletop. If the enemy is going to open fire with off-table guns, simply interrupt him and declare a counter battery mission. Roll a D6; if the result is greater than the required score (see the Army Lists) the off-table battery cannot fire, and no orders are used."

**Key features**:
- Interrupt enemy artillery
- No orders used
- Can attempt repeatedly until successful
- Multiple missions allowed per turn

---

## Unit Morale Table (Page 50, 62)

| D6 Roll | Infantry | Gun Crew | Vehicle | Aircraft |
|---------|----------|----------|---------|----------|
| 1 | Pinned/Rout | Abandoned | Abandoned¹ | Return to Base |
| 2 | Pinned/Rout | Abandoned | Pinned | OK |
| 3 | Pinned² | Pinned² | OK | OK |
| 4 | OK | OK | OK | OK |
| 5 | OK | OK | OK | OK |
| 6 | OK³ | OK³ | OK³ | OK³ |

**Notes**:
1. Vehicle only abandoned if: already pinned, OR immobilized, OR soft-skinned, OR enemy infantry within 10" with no friendly infantry within 10"
2. Veteran and Elite infantry treat Pinned as OK
3. Roll of 6: Unit may attempt "Beyond the Call of Duty" test (free immediate order)

---

## Weather Effects (Page 57-60)

**Standard weather roll** (all scenarios):
> "Roll a D6. On a roll of 1 there is a sudden thunderstorm, grounding all air cover. Any aircraft counters drawn from the pot automatically fail to arrive. The counters are treated as 1s instead."

**Implementation**:
- Roll once at scenario start
- Affects entire game
- Only shown effect: grounds aircraft

---

## Critical Scenario Design Notes

### For Scenario Slicer Implementation

**Minimum Required Data**:
1. Points total (determines game size)
2. Number of officers (affects orders)
3. Number of scouts (affects deployment/initiative)
4. Total Battle Rating (defeat threshold)
5. Unit types and categories
6. Force composition (infantry, tanks, artillery, etc.)

**Scenario Selection Factors**:
- **Meeting Engagements**: Equal/similar forces, mobile, scouts important
- **Attack/Defence**: Asymmetric forces, attackers need mobility, defenders need defenses
- **Flanking scenarios**: Require reconnaissance units
- **Assault scenarios**: Favor attacking force, require infantry

**Force Balance Considerations**:
- Theatre supplements provide national characteristics
- Points balance ≠ capability balance
- Doctrine and special rules matter (not in extracted pages)

**Objective Placement Rules**:
- Always 10" from table edges
- Always 10" from each other
- Number varies: D3+2 (3-5), or fixed 3-4
- Central objectives common in meeting engagements
- Hill/terrain objectives in defensive scenarios

**Deployment Zone Sizing**:
- Standard: 20" from table corner
- Front Line: Central third of table (lengthwise)
- Reserves arrive at table edge (usually within 20" of corner)

---

## Glossary of Key Terms

**Battle Rating (BR)**: Total morale capacity of force; when exceeded, force withdraws (defeats)

**Battle Counter**: Random numbered/special token drawn when events occur; sum compared to BR

**Pinned**: Unit under heavy fire, cannot take orders until rallied

**Scout Unit**: Special reconnaissance unit; affects deployment, initiative, observation

**Officer**: Command unit; adds to orders available per turn

**Observation**: Test to spot target before Aimed Fire

**Aimed Fire**: Precise shooting to destroy targets

**Area Fire**: Suppressive fire to pin targets

**Indirect Fire**: Off-table artillery or mortar fire via spotter

**Reaction Order**: Order taken in opponent's turn (Ambush Fire or Reserve Move)

**Close Assault**: Infantry attack within 5" with grenades, bayonets, SMGs

**Spotter**: Unit that directs indirect artillery fire

**Pre-Registered Target**: Pre-planned artillery target (no deviation)

**Timed Barrage**: Pre-scheduled artillery arriving on specific turn

**Counter-Battery Fire**: Disrupting enemy off-table artillery

**ROF (Rate of Fire)**: Number of dice rolled for small arms/MG firing

**HE (High Explosive)**: Shell type for anti-personnel/area fire

**AP (Armour Piercing)**: Shell type for anti-tank fire

**Beyond the Call of Duty**: Special free action on morale roll of 6

**Reinforcements**: Units arriving after initial deployment

**Probing Force**: Initial small force (attacker in Defence Line scenario)

**Front Line Zone**: Central third of table (Defence Line scenario)

---

## Implementation Priorities for Scenario Slicer

### Phase 1: Core Scenario Structure
- Generate scenario header (title, type, situation)
- Calculate game size from points
- Select appropriate scenario template
- Place objectives with proper spacing

### Phase 2: Force Allocation
- Split forces into initial/reserves based on scenario
- Calculate orders dice (officers)
- Track scout count for deployment bonuses
- Validate BR totals

### Phase 3: Deployment Rules
- Generate deployment zones
- Determine first turn
- Handle weather roll
- Apply ambush fire limits

### Phase 4: Special Rules
- Artillery support options
- Reinforcement schedules
- Scenario-specific conditions
- Victory conditions

### Phase 5: Historical Narrative
- Match historical TO&E data to scenario type
- Generate situation report from historical context
- Suggest terrain based on location/date
- Recommend force compositions

---

**End of Reference Document**

*This document extracted and organized information from BattleGroup Rules core rulebook pages 1-66 (excluding pages 41-50 which failed extraction). Theatre-specific rules, army lists, unit profiles, and detailed special rules are found in separate theatre supplements.*
