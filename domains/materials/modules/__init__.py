"""
Frontmatter Generation Modules

Active Modules (6):
- MetadataModule: name, title, description, category, subcategory
- AuthorModule: author metadata extraction
- PropertiesModule: materialProperties with GROUPED structure
- SettingsModule: machineSettings with ranges
- ComplianceModule: regulatoryStandards extraction
- MediaModule: images, micro

Removed Modules (Nov 2, 2025):
- ApplicationsModule: applications field removed from template
- ImpactModule: environmentalImpact/outcomeMetrics fields removed
- CharacteristicsModule: materialCharacteristics field removed

Architecture:
- Single Responsibility: Each module handles ONE domain
- Data-First: All modules read from Materials.yaml
- Fail-Fast: Validate inputs immediately, no fallbacks
- Pure Extraction: NO AI calls, NO API dependencies
- Single Source of Truth: Each module class defined in ONE file only
"""

# Individual module imports (matches orchestrator pattern)
from .metadata_module import MetadataModule
from .author_module import AuthorModule
from .properties_module import PropertiesModule
# SettingsModule moved to domains/settings/modules/ (Nov 26, 2025)
from .modules import ComplianceModule, MediaModule

__all__ = [
    # Active modules
    'MetadataModule',
    'AuthorModule',
    'PropertiesModule',
    # 'SettingsModule' moved to settings domain (Nov 26, 2025)
    'ComplianceModule',
    'MediaModule',
]

__version__ = '3.0.0'  # Post-cleanup: Single source of truth per module
