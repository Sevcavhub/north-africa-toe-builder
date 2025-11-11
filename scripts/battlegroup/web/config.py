#!/usr/bin/env python3
"""
Configuration for Flask REST API
Phase 9B: BattleGroup Web Services

Environment-based configuration for development and production.
"""

import os
from pathlib import Path

class Config:
    """Base configuration."""

    # Project root directory
    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    # Database configuration
    DATABASE_PATH = PROJECT_ROOT / "database" / "master_database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # API configuration
    API_TITLE = "North Africa TO&E Builder API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "BattleGroup scenario and army list generation services"

    # File paths
    SCENARIOS_DIR = PROJECT_ROOT / "data" / "output" / "bg_builder_scenarios"
    OUTPUT_DIR = PROJECT_ROOT / "books"
    UNITS_DIR = PROJECT_ROOT / "data" / "output" / "units"

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


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

    # Allow all origins in development
    CORS_ORIGINS = ["*"]


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Restrict to GitHub Pages origin in production
    CORS_ORIGINS = [
        os.getenv("GITHUB_PAGES_URL", "https://github.io"),
        "https://*.github.io"
    ]


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None) -> Config:
    """
    Get configuration based on environment.

    Args:
        env: Environment name (development, production, testing)

    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    return config.get(env, config['default'])
