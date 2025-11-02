# Points/BR Variance Analysis

**Generated**: Phase 9B Step 3 Part 4

**Date**: 1762057808.4188046

---

## Summary Statistics

- **Units with duplicates**: 78
- **Total entries analyzed**: 261

## Units with Significant Variance

Units where points or BR vary significantly across battles:

| Unit Name | Appearances | Points Range | BR Range |
|-----------|-------------|--------------|----------|
| Armoured Panzer Grenadier Platoon        |  2 | 120-162 (+42) | 11-15 (+4) |
| Wirbelwind                               |  2 | 8-48 (+40) | 2-2 (+0) |
| Infantry Foot Patrol                     |  2 | 22-51 (+29) | 2-3 (+1) |
| Hummel                                   |  2 | 44-68 (+24) | 2-3 (+1) |
| Light Panzer Artillery Battery           |  2 | 64-86 (+22) | 4-4 (+0) |
| Reconnaissance Command                   |  3 | 23-44 (+21) | 2-3 (+1) |
| Anti-tank Gun                            |  5 | 18-34 (+16) | 2-2 (+0) |
| Wespe                                    |  2 | 32-43 (+11) | 2-2 (+0) |
| Panzer Grenadier Platoon                 |  2 | 91-100 (+9) | 7-11 (+4) |

## Detailed Duplicate Analysis

### Armoured Panzer Grenadier Platoon

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    | 162 pts | 15 BR | Veteran |
| Normandy        | 1944-06    | 120 pts | 11 BR | Veteran |

### Wirbelwind

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Westwall        | 1944       |   8 pts |  2 BR | Inexperienced |
| Normandy        | 1944-06    |  48 pts |  2 BR | Regular |

### Infantry Foot Patrol

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    |  22 pts |  2 BR | Inexperienced |
| Market Garden   | 1944-09    |  51 pts |  3 BR | Veteran |

### Hummel

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    |  68 pts |  2 BR | Regular |
| Normandy        | 1944-06    |  44 pts |  3 BR | Regular |

### Light Panzer Artillery Battery

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    |  86 pts |  4 BR | Regular |
| Normandy        | 1944-06    |  64 pts |  4 BR | Regular |

### Reconnaissance Command

**Appears in 3 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Various         | Various    |  23 pts |  2 BR | Inexperienced |
| Various         | Various    |  30 pts |  3 BR | Regular |
| Various         | Various    |  44 pts |  3 BR | Regular |

### Anti-tank Gun

**Appears in 5 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    |  27 pts |  2 BR | Regular |
| Kursk           | 1943-07    |  30 pts |  2 BR | Veteran |
| Normandy        | 1944-06    |  34 pts |  2 BR | Regular |
| Various         | Various    |  18 pts |  2 BR | Inexperienced |
| Various         | Various    |  19 pts |  2 BR | Regular |

### Wespe

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    |  43 pts |  2 BR | Regular |
| Normandy        | 1944-06    |  32 pts |  2 BR | Regular |

### Panzer Grenadier Platoon

**Appears in 2 battles**

| Battle | Date | Points | BR | Experience |
|--------|------|--------|----|-----------|
| Kursk           | 1943-07    | 100 pts | 11 BR | Regular |
| Westwall        | 1944       |  91 pts |  7 BR | Inexperienced |

## Experience Level Effects

Average points and BR by experience level:

| Experience | Count | Avg Points | Avg BR |
|------------|-------|------------|--------|
| I               | 1     |   81.0 pts |  8.0 |
| V               | 2     |   24.5 pts |  1.0 |
| Elite           | 1     |   20.0 pts |  0.0 |
| Inexperienced   | 150   |   30.3 pts |  2.1 |
| Regular         | 269   |   44.8 pts |  2.8 |
| Veteran         | 31    |   35.3 pts |  2.9 |

## Battle Date Effects

Average points and BR by battle and date:

| Date | Battle | Count | Avg Points | Avg BR |
|------|--------|-------|------------|--------|
| 1943-07    | Kursk              | 203   |   42.9 pts |  2.8 |
| 1944       | Westwall           | 38    |   45.6 pts |  2.7 |
| 1944-06    | Normandy           | 60    |   35.2 pts |  2.3 |
| 1944-09    | Market Garden      | 28    |   27.3 pts |  2.0 |
| 1944-12    | Ardennes           | 54    |   45.5 pts |  2.7 |
| Various    | Various            | 71    |   29.0 pts |  2.3 |

## Research Questions

### Q1: Do veteran units cost more points?

**Finding**: Veteran units average 35.3 pts vs Regular 44.8 pts

**Difference**: -21.2%

### Q2: Does BR decrease in late-war?

See Battle Date Effects table above. Later battles (1944-12) show similar BR to earlier (1943-07), suggesting BR is based on unit type not historical attrition.

### Q3: Are Eastern vs Western Front units rated differently?

Kursk (Eastern, 1943-07) avg: 42.9 pts, 2.8 BR

Normandy (Western, 1944-06) avg: 35.2 pts, 2.3 BR

**Finding**: Theater does not appear to significantly affect points/BR values.

## Conclusions

1. **Experience modifiers exist but are subtle**: Veteran units cost ~-21% more than Regular units on average

2. **Date/theater effects minimal**: Units retain similar values across battles

3. **Duplicates are valuable**: Same unit appearing in multiple contexts helps validate formulas

4. **Most variance is unit-specific**: Points/BR primarily determined by unit type and capabilities

