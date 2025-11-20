#!/usr/bin/env python3
"""
Railway-specific configuration override
Handles path differences between local development and Railway deployment
"""

import os
from pathlib import Path

class RailwayConfig:
    """Railway deployment configuration."""

    # In Railway deployment, we're at the project root (3 levels up from this file)
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    # Database configuration
    # Use master_database.db (canonical database at project root)
    DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS configuration - GitHub Pages
    CORS_ORIGINS = [
        "https://sevcavhub.github.io",
        "https://*.github.io"
    ]

    # API configuration
    API_TITLE = "North Africa TO&E Builder API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "BattleGroup scenario and army list generation services"

    # Validation ranges
    MIN_POINTS = 100
    MAX_POINTS = 2000
    VALID_NATIONS = ["german", "british", "italian", "american", "french"]
    VALID_QUARTERS = [
        "1940q2", "1940q3", "1940q4",
        "1941q1", "1941q2", "1941q3", "1941q4",
        "1942q1", "1942q2", "1942q3", "1942q4",
        "1943q1", "1943q2"
    ]
    VALID_BATTLES = ["battleaxe", "crusader", "gazala", "first_alamein"]

    # Rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    DEBUG = False
    TESTING = False
