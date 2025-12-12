"""
Contaminant Export Modules

Modular components for contaminant frontmatter export following
the same architecture as materials domain.

Per CONTAMINATION_FRONTMATTER_SPEC.md
"""

from .metadata_module import MetadataModule
from .laser_module import LaserModule
from .simple_modules import (
    MediaModule,
    EEATModule,
    OpticalModule,
    RemovalModule,
    SafetyModule,
)
from .seo_module import SEOModule
from .quick_facts_module import QuickFactsModule
from .industries_module import IndustriesModule
from .appearance_module import AppearanceModule
from .crosslinking_module import CrosslinkingModule
from .author_module import AuthorModule

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
    'CrosslinkingModule',
    'AuthorModule',
]
