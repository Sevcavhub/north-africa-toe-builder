"""
SQLAlchemy models for BG Builder forces.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BGBuilderForce(Base):
    """BG Builder imported forces."""
    __tablename__ = 'bg_builder_forces'

    id = Column(Integer, primary_key=True)
    force_id = Column(String, unique=True, nullable=False)
    force_name = Column(String, nullable=False)
    nation = Column(String, nullable=False)
    quarter = Column(String)

    # Force composition
    total_points = Column(Integer)
    battle_rating = Column(Integer)

    # Metadata
    import_file = Column(String)
    import_date = Column(DateTime)
    source = Column(String)


class BGBuilderVehicle(Base):
    """BG Builder vehicles in forces."""
    __tablename__ = 'bg_builder_vehicles'

    id = Column(Integer, primary_key=True)
    force_id = Column(String, ForeignKey('bg_builder_forces.force_id'), nullable=False)

    name = Column(String, nullable=False)
    category = Column(String)
    quantity = Column(Integer, default=1)

    # Points/BR
    cost_per_unit = Column(Integer)
    br_per_unit = Column(Integer)

    # Link to master equipment
    equipment_id = Column(String, ForeignKey('equipment.equipment_id'))
