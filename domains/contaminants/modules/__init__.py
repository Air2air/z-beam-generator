"""
Contaminant Export Modules

Modular components for contaminant frontmatter export following
the same architecture as materials domain.

Per CONTAMINATION_FRONTMATTER_SPEC.md
"""

from .appearance_module import AppearanceModule
from .author_module import AuthorModule
from .industries_module import IndustriesModule
from .laser_module import LaserModule
from .metadata_module import MetadataModule
from .modules import (
    EEATModule,
    MediaModule,
    OpticalModule,
    RemovalModule,
    SafetyModule,
)
from .quick_facts_module import QuickFactsModule
from .seo_module import SEOModule

__all__ = [
    # Basic modules (v1.0)
    'MetadataModule',
    'LaserModule',
    'MediaModule',
    'EEATModule',
    'OpticalModule',
    'RemovalModule',
    'SafetyModule',
    # Enhanced modules (v2.0 - Spec compliant)
    'SEOModule',
    'QuickFactsModule',
    'IndustriesModule',
    'AppearanceModule',
    'AuthorModule',
]
