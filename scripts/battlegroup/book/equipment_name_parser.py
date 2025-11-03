#!/usr/bin/env python3
"""
Equipment Name Parser with Metadata Extraction.

Parses equipment names from Phase 6 unit JSONs to extract:
- Base name (for database matching)
- Weight class (Light/Medium/Heavy Tank, Infantry/Cruiser Tank)
- Gun designation (5cm L/42, 2cm KwK 30, etc.)
- Role (Command, Assault Gun, Self-Propelled, etc.)

This preserves valuable metadata that was previously discarded during
normalization, and uses it to enrich both matching and database records.
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedEquipment:
    """Structured equipment metadata extracted from name."""
    original_name: str
    base_name: str  # For matching
    weight_class: Optional[str] = None  # "Light Tank", "Medium Tank", "Heavy Tank", etc.
    gun: Optional[str] = None  # "5cm L/42", "2cm KwK 30", etc.
    role: Optional[str] = None  # "Command", "Assault Gun", "Self-Propelled", etc.
    variant: Optional[str] = None  # "Ausf H", "Mk VI", etc.
    nation_suffix: Optional[str] = None  # "(German)", "(Italian)", etc.


class EquipmentNameParser:
    """Parse equipment names to extract metadata."""

    # Tank weight class patterns
    WEIGHT_CLASS_PATTERNS = [
        (r'\b(Light Tank|light tank)\b', 'Light Tank'),
        (r'\b(Medium Tank|medium tank)\b', 'Medium Tank'),
        (r'\b(Heavy Tank|heavy tank)\b', 'Heavy Tank'),
        (r'\b(Infantry Tank|infantry tank)\b', 'Infantry Tank'),
        (r'\b(Cruiser Tank|cruiser tank)\b', 'Cruiser Tank'),
        (r'\b(Command Tank|Command Tanks|command tanks)\b', 'Command Tank'),
        (r'\b(Tankette|tankette)\b', 'Tankette'),
    ]

    # Role patterns
    ROLE_PATTERNS = [
        (r'\b(Self-Propelled|self-propelled)\b', 'Self-Propelled'),
        (r'\b(Assault Gun|assault gun)\b', 'Assault Gun'),
        (r'\b(Befehlspanzer|Command tank|command tank)\b', 'Command'),
        (r'\b(Reconnaissance|reconnaissance)\b', 'Reconnaissance'),
        (r'\b(Lanciafiamme|Flamethrower|flamethrower)\b', 'Flamethrower'),
        (r'\b(Carro Commando)\b', 'Command'),
        (r'\b(Semovente)\b', 'Self-Propelled'),
    ]

    # Gun designation patterns
    GUN_PATTERNS = [
        # German guns: "5cm L/42", "7.5cm KwK 37 L/24", "2cm KwK 30"
        r'\b(\d+\.?\d*\s*cm\s+(?:KwK|PaK|L)/?\s*\d+(?:/\d+)?)\b',
        # British guns: "6-pounder", "2-pounder"
        r'\b(\d+-pounder)\b',
        # Italian/American: "75mm", "37mm"
        r'\b(\d+\s*mm)\b',
    ]

    # Variant patterns
    VARIANT_PATTERNS = [
        # German: "Ausf A", "Ausf. H"
        r'\b(Ausf\.?\s*[A-Z])\b',
        # British: "Mk I", "Mk VI", "Mark II"
        r'\b(Mk\.?\s*[IVX]+[A-C]?|Mark\s*[IVX]+)\b',
        # Italian: "Mod. 1940", "Modello 35"
        r'\b(Mod\.?\s*\d+|Modello\s*\d+)\b',
    ]

    # Nation suffix patterns
    NATION_PATTERNS = [
        (r'\(German\)', 'German'),
        (r'\(Italian\)', 'Italian'),
        (r'\(British\)', 'British'),
        (r'\(American\)', 'American'),
    ]

    def parse(self, equipment_name: str) -> ParsedEquipment:
        """Parse equipment name and extract metadata."""
        if not equipment_name:
            return ParsedEquipment(
                original_name='',
                base_name=''
            )

        original = equipment_name
        remaining = equipment_name

        # Extract weight class
        weight_class = None
        for pattern, class_name in self.WEIGHT_CLASS_PATTERNS:
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                weight_class = class_name
                # Remove from remaining text
                remaining = remaining[:match.start()] + remaining[match.end():]
                break

        # Extract role
        role = None
        for pattern, role_name in self.ROLE_PATTERNS:
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                role = role_name
                remaining = remaining[:match.start()] + remaining[match.end():]
                break

        # Extract gun designation
        gun = None
        for pattern in self.GUN_PATTERNS:
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                gun = match.group(1)
                remaining = remaining[:match.start()] + remaining[match.end():]
                break

        # Extract variant
        variant = None
        for pattern in self.VARIANT_PATTERNS:
            match = re.search(pattern, remaining, re.IGNORECASE)
            if match:
                variant = match.group(1)
                # Don't remove variant from base name - it's part of identity
                # Just capture it
                break

        # Extract nation suffix
        nation_suffix = None
        for pattern, nation in self.NATION_PATTERNS:
            match = re.search(pattern, remaining)
            if match:
                nation_suffix = nation
                remaining = remaining[:match.start()] + remaining[match.end():]
                break

        # Clean up base name
        base_name = self._clean_base_name(remaining)

        return ParsedEquipment(
            original_name=original,
            base_name=base_name,
            weight_class=weight_class,
            gun=gun,
            role=role,
            variant=variant,
            nation_suffix=nation_suffix
        )

    def _clean_base_name(self, text: str) -> str:
        """Clean up base name after extraction."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()

        # Remove trailing punctuation
        cleaned = re.sub(r'[,\.\-\s]+$', '', cleaned)

        # Common vehicle name normalizations
        normalizations = {
            'Carro Armato': '',  # Remove Italian prefix
            'Panzerbefehlswagen': 'Befehlspanzer',  # Standardize command tank names
        }

        for old, new in normalizations.items():
            if old in cleaned:
                cleaned = cleaned.replace(old, new).strip()

        return cleaned

    def get_database_match_key(self, equipment_name: str) -> str:
        """
        Get normalized key for database matching.

        This is the clean base name that should match database records.
        """
        parsed = self.parse(equipment_name)
        return self._normalize_for_matching(parsed.base_name)

    def _normalize_for_matching(self, name: str) -> str:
        """Normalize name for fuzzy matching."""
        # Lowercase
        normalized = name.lower()

        # Remove punctuation except /
        normalized = re.sub(r'[^\w\s/]', '', normalized)

        # Collapse whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def extract_metadata_dict(self, equipment_name: str) -> Dict[str, Optional[str]]:
        """Extract metadata as dictionary for database enrichment."""
        parsed = self.parse(equipment_name)

        metadata = {}
        if parsed.weight_class:
            metadata['weight_class'] = parsed.weight_class
        if parsed.gun:
            metadata['gun'] = parsed.gun
        if parsed.role:
            metadata['role'] = parsed.role
        if parsed.variant:
            metadata['variant'] = parsed.variant
        if parsed.nation_suffix:
            metadata['nation'] = parsed.nation_suffix

        return metadata


def test_parser():
    """Test the parser with example equipment names."""
    parser = EquipmentNameParser()

    test_cases = [
        # Italian tanks
        "M13/40 Medium Tank",
        "M14/41 Medium Tank",
        "L6/40 Light Tank",
        "L3/35 Tankette",
        "Carro Armato L3/35 Tankette",
        "L3/35 Lanciafiamme",
        "L3/35 Carro Commando",
        "75/18 Semovente on M13/40 chassis",

        # German tanks
        "Panzer III Ausf H",
        "Pz.Kpfw.III Ausf H (5cm L/42)",
        "Panzer IV Ausf D/E",
        "Panzer II",
        "Befehlspanzer (German command tanks)",
        "Befehlspanzer",
        "Panzer-Befehlswagen",
        "StuG III Ausf D",

        # British tanks
        "Matilda II Infantry Tank",
        "Matilda II (Infantry Tank)",
        "Crusader Mk I",
        "Light Tank Mk VI",
        "Vickers Light Tank Mk VI",
        "Valentine Mk III",

        # Edge cases
        "M13/40 (Italian)",
        "Panzer I (German)",
        "75/18 Self-Propelled (on M13/40 chassis)",
    ]

    print("Equipment Name Parser - Test Results\n" + "=" * 80)

    for name in test_cases:
        parsed = parser.parse(name)
        match_key = parser.get_database_match_key(name)
        metadata = parser.extract_metadata_dict(name)

        print(f"\nOriginal:     {parsed.original_name}")
        print(f"Base Name:    {parsed.base_name}")
        print(f"Match Key:    {match_key}")
        if parsed.weight_class:
            print(f"Weight Class: {parsed.weight_class}")
        if parsed.gun:
            print(f"Gun:          {parsed.gun}")
        if parsed.role:
            print(f"Role:         {parsed.role}")
        if parsed.variant:
            print(f"Variant:      {parsed.variant}")
        if parsed.nation_suffix:
            print(f"Nation:       {parsed.nation_suffix}")
        if metadata:
            print(f"Metadata:     {metadata}")


if __name__ == '__main__':
    test_parser()
