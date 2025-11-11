"""
SQLAlchemy models for equipment tables.
"""

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Equipment(Base):
    """Main equipment table."""
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    equipment_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String)
    witw_id = Column(Integer)
    wwiitanks_id = Column(Integer)
    onwar_id = Column(Integer)
    reference_vehicle_id = Column(Integer, ForeignKey('bg_reference_vehicles.id'))
    reference_gun_id = Column(Integer, ForeignKey('bg_reference_guns.id'))


class EquipmentBattlegroup(Base):
    """BattleGroup-specific equipment stats."""
    __tablename__ = 'equipment_battlegroup'

    id = Column(Integer, primary_key=True)
    equipment_id = Column(String, ForeignKey('equipment.equipment_id'), nullable=False)
    name = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Armor values
    armor_front = Column(String)
    armor_side = Column(String)
    armor_rear = Column(String)
    armor_modifier = Column(String)

    # Movement
    off_road = Column(Integer)
    road = Column(Integer)

    # Points costs
    points_regular = Column(Integer)
    points_veteran = Column(Integer)
    points_elite = Column(Integer)

    # Battle rating
    br_regular = Column(Integer)
    br_veteran = Column(Integer)
    br_elite = Column(Integer)

    # Weapons
    main_gun = Column(String)
    main_gun_ammo_ap = Column(Integer)
    main_gun_ammo_he = Column(Integer)
    secondary_gun = Column(String)
    secondary_gun_ammo_ap = Column(Integer)
    secondary_gun_ammo_he = Column(Integer)

    # Special rules
    special_rules = Column(Text)

    # Metadata
    generation_method = Column(String)
    quarter_from = Column(String)
    quarter_to = Column(String)


class BGReferenceVehicle(Base):
    """BattleGroup reference vehicles (manually extracted)."""
    __tablename__ = 'bg_reference_vehicles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    category = Column(String)

    # Armor
    armor_front = Column(String)
    armor_side = Column(String)
    armor_rear = Column(String)

    # Movement
    off_road = Column(Integer)
    road = Column(Integer)

    # Weapons
    weapon_1 = Column(String)
    ammo_1 = Column(String)
    weapon_2 = Column(String)
    ammo_2 = Column(String)
    weapon_3 = Column(String)
    ammo_3 = Column(String)
    weapon_4 = Column(String)
    ammo_4 = Column(String)

    # Points
    points_regular = Column(Integer)
    points_veteran = Column(Integer)
    points_elite = Column(Integer)

    # Battle rating
    br_regular = Column(Integer)
    br_veteran = Column(Integer)
    br_elite = Column(Integer)

    # Special rules
    special_rules = Column(Text)

    # Metadata
    source = Column(String)


class BGReferenceGun(Base):
    """BattleGroup reference guns (manually extracted)."""
    __tablename__ = 'bg_reference_guns'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    category = Column(String)

    # Performance
    he_rating = Column(String)
    ap_rating = Column(String)
    penetration = Column(String)
    range_short = Column(Integer)
    range_medium = Column(Integer)
    range_long = Column(Integer)

    # Points
    points_regular = Column(Integer)
    points_veteran = Column(Integer)
    points_elite = Column(Integer)

    # Battle rating
    br_regular = Column(Integer)
    br_veteran = Column(Integer)
    br_elite = Column(Integer)

    # Special rules
    special_rules = Column(Text)

    # Metadata
    source = Column(String)
