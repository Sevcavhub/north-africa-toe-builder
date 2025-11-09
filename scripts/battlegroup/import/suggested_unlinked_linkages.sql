-- Suggested linkages for 18 unlinked vehicles
-- Based on BG Builder search results
-- Review each before executing!

-- CLEAR MATCHES (High Confidence)

-- A10 → A10 Cruiser Mk.II (ID: 334)
UPDATE bg_reference_vehicles SET bg_builder_id = 334 WHERE id = 101;
-- Manual: A10, M/N/O, 5"/8", 2 pdr
-- BG Builder: A10 Cruiser Mk.II, M, 2 pdr

-- A13 MkII → A13 Mark II Cruiser Mk.IV (ID: 321)
UPDATE bg_reference_vehicles SET bg_builder_id = 321 WHERE id = 103;
-- Manual: A13 MkII, L/M/O, 9"/15", 2 pdr
-- BG Builder: A13 Mark II Cruiser Mk.IV, L, 2 pdr

-- A9 → A9 Cruiser Mk.I (ID: 332)
UPDATE bg_reference_vehicles SET bg_builder_id = 332 WHERE id = 99;
-- Manual: A9, N/O/O, 8"/12", 2 pdr
-- BG Builder: A9 Cruiser Mk.I, N, 2 pdr

-- Dingo Scout Car → Daimler Dingo (ID: 136)
UPDATE bg_reference_vehicles SET bg_builder_id = 136 WHERE id = 6;
-- Manual: Dingo Scout Car, N/O/O, 9"/14", MG (canadian)
-- BG Builder: Daimler Dingo, N (already linked to manual ID 226 as Daimler Dingo)
-- Note: This is a duplicate - same vehicle, different nation designation

-- M4 Sherman DD → M4 DD Sherman (ID: 106)
UPDATE bg_reference_vehicles SET bg_builder_id = 106 WHERE id = 127;
-- Manual: M4 Sherman DD, K/L/N, 9"/14", 75mmL40
-- BG Builder: M4 DD Sherman, K, 75mmL40

-- Van (Italian) → Radio Van (ID: 92)
UPDATE bg_reference_vehicles SET bg_builder_id = 92 WHERE id = 189;
-- Manual: Van, SS/SS/SS, 6"/24", None (italian, Tobruk)
-- BG Builder: Radio Van, ?, 2 hits
-- Note: User said "Italian separate vehicle but same stats as Light Truck"


-- PROBABLE MATCHES (Medium Confidence - Review Required)

-- Crusader AA MkII (2x 20mm) → Crusader AA II (ID: 130)
-- UPDATE bg_reference_vehicles SET bg_builder_id = 130 WHERE id = 132;
-- Manual: Crusader AA MkII (2x 20mm), L/N/O, 8"/12", 2x 20mm
-- BG Builder: Crusader AA II, L, 20mmL55
-- Note: BG Builder doesn't specify mount count, but likely same vehicle

-- Crusader AA MkII (3x 20mm) → Crusader AA 'Triple' (ID: 233)
-- UPDATE bg_reference_vehicles SET bg_builder_id = 233 WHERE id = 133;
-- Manual: Crusader AA MkII (3x 20mm), L/N/O, 8"/12", 3x 20mm
-- BG Builder: Crusader AA 'Triple', L, 20mmL55
-- Note: "Triple" suggests 3 mounts


-- NO CLEAR MATCH (Manual Entry or Research Required)

-- 20mm Flak Truck (ID: 220) - German improvised AA truck, not standardized
-- 37mm Flak Truck (ID: 221) - German improvised AA truck, not standardized
-- CMP (ID: 11) - User flagged as "Data entry error, can delete"
-- Centaur Bulldozer (ID: 135) - User said "Was not in Africa"
-- M3 Scout Car (ID: 143) - User said "Could be 84 or 577 but need more BG builder stats"
-- M5 Ambulance (ID: 15) - User said "Not in Africa"
-- M5 Recce (ID: 121) - User said "not in africa"
-- Marmon-Herrington II A (20mm) (ID: 230) - User said "Need gun from bg builder to match"
-- Marmon-Herrington II A (37mm) (ID: 231) - User said "Need gun from bg builder to match"
-- Panzer III H Pz. Bef. Wg (ID: 209) - Command variant, may need research


-- EXECUTION NOTES:
-- 1. Review each suggested linkage above
-- 2. Uncomment the UPDATEs you want to execute
-- 3. Run this script: sqlite3 database/master_database.db < suggested_unlinked_linkages.sql
-- 4. Or execute selectively via Python script


-- STATISTICS AFTER EXECUTION (if all clear matches applied):
-- Before: 197/215 linked (91.6%)
-- After: 203/215 linked (94.4%) - if applying 6 clear matches
-- Remaining: 12 vehicles (CMP deletable, 4 not in Africa, 2 Marmon-Herrington weapon variants, 2 Flak trucks, 1 command variant, 2 Crusader AA if not applied)
