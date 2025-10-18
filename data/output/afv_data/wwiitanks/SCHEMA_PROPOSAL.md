# WWII Tanks UK Data Schema - AFVs, Guns, and Relationships

## Overview

The wwiitanks.co.uk site provides three types of data:
1. **AFV (Armored Fighting Vehicle) specifications**
2. **Gun/weapon specifications**
3. **Gun-to-AFV relationships** (which vehicles use which guns)

## Proposed Schema

### 1. AFV Table (`afvs`)

Primary table for all armored vehicles.

```json
{
  "afv_id": "unique-id",
  "country": "germany",
  "vehicle_name": "PzKpfw IV Ausf F",
  "common_name": "Panzer IV",
  "url": "https://wwiitanks.co.uk/FORM-Tank_Data.php?I=123",

  "general": {
    "operational_dates": "1941-1943",
    "ordnance_classification": "SdKfz 161",
    "quantity_produced": "462",
    "manufacturer": "Krupp, Vomag, Nibelungenwerk"
  },

  "dimensions": {
    "length_m": 5.92,
    "width_m": 2.88,
    "height_m": 2.68,
    "weight_tonnes": 22.3,
    "crew": 5
  },

  "performance": {
    "max_road_speed_kph": 42,
    "max_cross_country_speed_kph": 25,
    "range_road_km": 200,
    "range_cross_country_km": 130,
    "fuel_type": "Petrol",
    "fuel_capacity_liters": 470,
    "engine_hp": 300,
    "power_weight_ratio": 13.5
  },

  "armor": {
    "hull_front_mm": 50,
    "hull_side_mm": 30,
    "hull_rear_mm": 20,
    "hull_top_mm": 10,
    "turret_front_mm": 50,
    "turret_side_mm": 30,
    "turret_rear_mm": 30,
    "turret_top_mm": 10
  },

  "armament_text": "1 x 75mm KwK 40 L/43, 2 x 7.92mm MG 34",

  "indicators": {
    "has_photo": true,
    "has_scale_illustration": true,
    "has_vehicle_history": true,
    "has_weapon_details": true,
    "has_armour_details": true
  },

  "source": "wwiitanks.co.uk",
  "scraped_at": "2025-10-17T15:30:00Z"
}
```

### 2. Gun Table (`guns`)

Primary table for all weapons/guns.

```json
{
  "gun_id": "unique-id",
  "country": "germany",
  "gun_name": "75mm KwK 40 L/43",
  "gun_type": "Tank Gun",
  "url": "https://wwiitanks.co.uk/FORM-Gun_Data.php?I=456",

  "general": {
    "history": "Developed in 1942 as an upgrade...",
    "manufacturer": "Rheinmetall",
    "manufactured_dates": "1942-1945",
    "caliber_mm": 75,
    "length_calibers": 43,
    "rate_of_fire_rpm": 15
  },

  "ammunition": [
    {
      "ammo_type": "PzGr 39 APCBC-HE",
      "designation": "7.5cm 6.8Kg 750M/Sec",
      "projectile_weight_kg": 6.8,
      "muzzle_velocity_mps": 750,
      "explosive_content_kg": 0.018,

      "penetration_table_mm": {
        "100m": 106,
        "200m": 99,
        "400m": 87,
        "800m": 69,
        "1200m": 57,
        "1600m": 48,
        "2000m": 41,
        "2400m": 35
      },

      "penetration_at_30deg_mm": {
        "100m": 92,
        "200m": 86,
        "400m": 75,
        "800m": 60,
        "1200m": 49,
        "1600m": 42,
        "2000m": 35,
        "2400m": 30
      },

      "hit_probability_percent": {
        "100m": 98,
        "200m": 95,
        "400m": 88,
        "800m": 65,
        "1200m": 45,
        "1600m": 30,
        "2000m": 20,
        "2400m": 12
      }
    }
  ],

  "source": "wwiitanks.co.uk",
  "scraped_at": "2025-10-17T15:30:00Z"
}
```

### 3. AFV-Gun Relationship Table (`afv_gun_relationships`)

Many-to-many relationship between AFVs and guns.

```json
{
  "relationship_id": "unique-id",
  "afv_id": "afv-unique-id",
  "afv_name": "PzKpfw IV Ausf F",
  "gun_id": "gun-unique-id",
  "gun_name": "75mm KwK 40 L/43",
  "mount_type": "main_armament",
  "quantity": 1,
  "notes": "Primary turret weapon",
  "source": "wwiitanks.co.uk",
  "extracted_at": "2025-10-17T15:30:00Z"
}
```

**Relationship extracted from:**
- Gun detail pages have "Vehicles in our database using this gun" table
- AFV detail pages have armament text (can be parsed)

### 4. Mount Types

Standardized mount types for the relationship:
- `main_armament` - Primary gun (usually in turret)
- `secondary_armament` - Coaxial or hull-mounted gun
- `anti_aircraft` - AA machine gun
- `defensive` - Defensive machine guns

## Implementation Strategy

### Phase 1: Scrape Core Data
1. ✅ Scrape all AFVs (612 vehicles)
2. ✅ Scrape all guns (343 weapons)

### Phase 2: Extract Relationships
3. Extract gun-to-AFV relationships from gun detail pages
4. Parse AFV armament text to validate relationships
5. Create relationship records

### Phase 3: Normalize and Validate
6. Normalize field names and units
7. Validate relationships (ensure both AFV and gun exist)
8. Handle edge cases (captured equipment, variants)

## Database Schema (SQL)

```sql
-- AFVs table
CREATE TABLE afvs (
    afv_id TEXT PRIMARY KEY,
    country TEXT NOT NULL,
    vehicle_name TEXT NOT NULL,
    common_name TEXT,
    url TEXT UNIQUE,
    operational_dates TEXT,
    ordnance_classification TEXT,
    quantity_produced INTEGER,
    manufacturer TEXT,
    -- dimensions
    length_m REAL,
    width_m REAL,
    height_m REAL,
    weight_tonnes REAL,
    crew INTEGER,
    -- performance
    max_road_speed_kph INTEGER,
    max_cross_country_speed_kph INTEGER,
    range_road_km INTEGER,
    range_cross_country_km INTEGER,
    fuel_type TEXT,
    fuel_capacity_liters INTEGER,
    engine_hp INTEGER,
    power_weight_ratio REAL,
    -- armor
    hull_front_mm INTEGER,
    hull_side_mm INTEGER,
    hull_rear_mm INTEGER,
    hull_top_mm INTEGER,
    turret_front_mm INTEGER,
    turret_side_mm INTEGER,
    turret_rear_mm INTEGER,
    turret_top_mm INTEGER,
    -- metadata
    armament_text TEXT,
    source TEXT DEFAULT 'wwiitanks.co.uk',
    scraped_at TIMESTAMP,
    UNIQUE(country, vehicle_name)
);

-- Guns table
CREATE TABLE guns (
    gun_id TEXT PRIMARY KEY,
    country TEXT NOT NULL,
    gun_name TEXT NOT NULL,
    gun_type TEXT,
    url TEXT UNIQUE,
    history TEXT,
    manufacturer TEXT,
    manufactured_dates TEXT,
    caliber_mm REAL,
    length_calibers INTEGER,
    rate_of_fire_rpm INTEGER,
    ammunition_json TEXT, -- JSON array of ammo types
    source TEXT DEFAULT 'wwiitanks.co.uk',
    scraped_at TIMESTAMP,
    UNIQUE(country, gun_name)
);

-- AFV-Gun relationships
CREATE TABLE afv_gun_relationships (
    relationship_id TEXT PRIMARY KEY,
    afv_id TEXT NOT NULL,
    afv_name TEXT NOT NULL,
    gun_id TEXT NOT NULL,
    gun_name TEXT NOT NULL,
    mount_type TEXT,
    quantity INTEGER DEFAULT 1,
    notes TEXT,
    source TEXT DEFAULT 'wwiitanks.co.uk',
    extracted_at TIMESTAMP,
    FOREIGN KEY (afv_id) REFERENCES afvs(afv_id),
    FOREIGN KEY (gun_id) REFERENCES guns(gun_id),
    UNIQUE(afv_id, gun_id, mount_type)
);

-- Indexes for performance
CREATE INDEX idx_afvs_country ON afvs(country);
CREATE INDEX idx_afvs_name ON afvs(vehicle_name);
CREATE INDEX idx_guns_country ON guns(country);
CREATE INDEX idx_guns_caliber ON guns(caliber_mm);
CREATE INDEX idx_relationships_afv ON afv_gun_relationships(afv_id);
CREATE INDEX idx_relationships_gun ON afv_gun_relationships(gun_id);
```

## File Output Structure

```
data/output/afv_data/wwiitanks/
├── afvs/
│   ├── germany_afvs.json
│   ├── britain_afvs.json
│   └── ... (one per country)
├── guns/
│   ├── germany_guns.json
│   ├── britain_guns.json
│   └── ... (one per country)
├── relationships/
│   ├── germany_relationships.json
│   ├── britain_relationships.json
│   └── ... (one per country)
├── all_afvs.json
├── all_guns.json
├── all_relationships.json
├── all_afvs.csv
├── all_guns.csv
├── all_relationships.csv
└── wwiitanks.db (SQLite database)
```

## Query Examples

### Find all vehicles using a specific gun
```sql
SELECT a.vehicle_name, a.common_name, r.mount_type, r.quantity
FROM afvs a
JOIN afv_gun_relationships r ON a.afv_id = r.afv_id
JOIN guns g ON r.gun_id = g.gun_id
WHERE g.gun_name = '75mm KwK 40 L/43';
```

### Find all weapons on a specific vehicle
```sql
SELECT g.gun_name, g.caliber_mm, r.mount_type, r.quantity
FROM guns g
JOIN afv_gun_relationships r ON g.gun_id = r.gun_id
JOIN afvs a ON r.afv_id = a.afv_id
WHERE a.vehicle_name = 'PzKpfw IV Ausf F';
```

### Find vehicles by armor thickness
```sql
SELECT vehicle_name, hull_front_mm, turret_front_mm
FROM afvs
WHERE country = 'germany'
  AND hull_front_mm >= 50
ORDER BY hull_front_mm DESC;
```

## Integration with OnWar and WITW Data

When merging with existing data:
1. Use fuzzy matching on vehicle names
2. Normalize country names (germany vs Germany)
3. Prefer wwiitanks data for gun specifications (more detailed)
4. Prefer OnWar data for production numbers (more accurate)
5. Cross-validate armor values between sources

## Next Steps

1. ✅ Test AFV scraper
2. ✅ Test gun scraper
3. 🔄 Update gun scraper to extract full specifications
4. 🔄 Add relationship extraction to gun scraper
5. ⏸️ Run full scrape (1-2 hours)
6. ⏸️ Create merge script for OnWar + wwiitanks + WITW data
