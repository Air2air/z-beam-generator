"""
Modular Frontmatter Generation Components

This package contains specialized modules for generating different sections
of frontmatter YAML files. Each module handles one domain independently.

Architecture:
- MetadataModule: name, title, subtitle, description, category, subcategory
- AuthorModule: author metadata extraction
- ApplicationsModule: applications list extraction
- PropertiesModule: materialProperties with ranges
- SettingsModule: machineSettings with ranges
- ComplianceModule: regulatoryStandards extraction
- ImpactModule: environmentalImpact, outcomeMetrics
- MediaModule: images, caption
- CharacteristicsModule: materialCharacteristics (qualitative)

Design Principles:
1. Single Responsibility: Each module handles ONE domain
2. Data-First: All modules read from Materials.yaml (100% complete)
3. Fail-Fast: Validate inputs immediately, no fallbacks
4. Pure Extraction: NO AI calls, NO API dependencies
5. Testable: Each module can be tested in isolation
"""

from .metadata_module import MetadataModule
from .author_module import AuthorModule
from .applications_module import ApplicationsModule

__all__ = [
    'MetadataModule',
    'AuthorModule',
    'ApplicationsModule',
]

__version__ = '1.0.0'
