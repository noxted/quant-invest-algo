"""
Configuration Package
Exports portfolio profiles and utilities
"""

from .profiles import (
    CONSERVATIVE,
    INTERMEDIATE,
    AGGRESSIVE,
    PROFILES,
    PortfolioProfile,
    get_profile,
    validate_profile,
)

__all__ = [
    'CONSERVATIVE',
    'INTERMEDIATE',
    'AGGRESSIVE',
    'PROFILES',
    'PortfolioProfile',
    'get_profile',
    'validate_profile',
]

__version__ = '1.0.0'
