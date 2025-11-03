"""
Modular Frontmatter Generation Components - Consolidated

PHASE 2 CONSOLIDATION:
Previously 7 small files (author, properties, settings, applications, simple_modules).
Now 2 focused files:
- core_modules.py: Author, Properties, Settings, Applications, Compliance, Media, Characteristics
- metadata_module.py: Metadata (complex logic, kept separate)

Architecture:
- MetadataModule: name, title, subtitle, description, category, subcategory
- AuthorModule: author metadata extraction
- ApplicationsModule: applications list extraction
- PropertiesModule: materialProperties with GROUPED structure
- SettingsModule: machineSettings with ranges
- ComplianceModule: regulatoryStandards extraction
- MediaModule: images, caption
- CharacteristicsModule: materialCharacteristics (qualitative)

Design Principles:
1. Single Responsibility: Each module handles ONE domain
2. Data-First: All modules read from Materials.yaml (100% complete)
3. Fail-Fast: Validate inputs immediately, no fallbacks
4. Pure Extraction: NO AI calls, NO API dependencies
5. Testable: Each module can be tested in isolation
"""

# Consolidated core modules
from .core_modules import (
    AuthorModule,
    PropertiesModule,
    SettingsModule,
    ApplicationsModule,
    ComplianceModule,
    MediaModule,
    CharacteristicsModule,
    # Backward compatibility aliases
    AuthorGenerator,
    PropertiesGenerator,
    SettingsGenerator,
    ApplicationsGenerator,
    ComplianceGenerator,
    MediaGenerator,
    CharacteristicsGenerator,
)

# Metadata module (kept separate - complex logic)
from .metadata_module import MetadataModule, MetadataGenerator

__all__ = [
    # Core modules
    'AuthorModule',
    'PropertiesModule',
    'SettingsModule',
    'ApplicationsModule',
    'ComplianceModule',
    'MediaModule',
    'CharacteristicsModule',
    # Metadata module
    'MetadataModule',
    # Backward compatibility
    'AuthorGenerator',
    'PropertiesGenerator',
    'SettingsGenerator',
    'ApplicationsGenerator',
    'ComplianceGenerator',
    'MediaGenerator',
    'CharacteristicsGenerator',
    'MetadataGenerator',
]

__version__ = '2.0.0'  # Phase 2: Consolidated structure
