"""
Materials Data Loader

Centralized loader for materials data across multiple YAML files:
- Materials.yaml: Core material metadata (name, category, descriptions, etc.)
- MaterialProperties.yaml: Material properties with category metadata, ranges, and definitions
- CategoryMetadata.yaml: Templates, frameworks, and regulatory guidance

Note: Settings.yaml moved to domains/settings/ domain (Nov 26, 2025)

This module provides a unified interface to load complete material data
by merging data from all files based on material names, plus accessor
functions for category-level metadata.

Usage:
    from domains.materials.data_loader import load_materials_data, load_material
    
    # Load all materials (merged from all files)
    all_materials = load_materials_data()
    
    # Load specific material
    aluminum_data = load_material("Aluminum")
    
    # Access metadata sections
    prop_defs = get_property_definitions()
    param_ranges = get_parameter_ranges()
    safety_templates = get_safety_templates()
    
    # Load individual files
    materials_only = load_materials_yaml()
    properties_only = load_properties_yaml()
    metadata_only = load_category_metadata_yaml()
    
    # REMOVED (Nov 26, 2025): Use orchestrators.data_orchestrator.load_complete_materials_data() instead
    # Settings integration now handled at orchestrator layer to avoid cross-domain imports
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache


# File paths - Point to data/materials directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "materials"
MATERIALS_FILE = DATA_DIR / "Materials.yaml"
PROPERTIES_FILE = DATA_DIR / "MaterialProperties.yaml"
# SETTINGS_FILE moved to domains/settings/data_loader.py (Nov 26, 2025)
METADATA_FILE = DATA_DIR / "IndustryApplications.yaml"  # Renamed from CategoryMetadata.yaml
CATEGORIES_FILE = DATA_DIR / "CategoryTaxonomy.yaml"     # Renamed from Categories.yaml
PROPERTY_DEFS_FILE = DATA_DIR / "PropertyDefinitions.yaml"  # NEW - Normalized architecture
PARAMETER_DEFS_FILE = DATA_DIR / "ParameterDefinitions.yaml"  # NEW - Normalized architecture
REGULATORY_FILE = DATA_DIR / "RegulatoryStandards.yaml"  # NEW - Normalized architecture


class MaterialDataError(Exception):
    """Raised when material data cannot be loaded or merged"""
    pass


@lru_cache(maxsize=1)
def load_materials_yaml() -> Dict[str, Any]:
    """
    Load Materials.yaml (core metadata only)
    
    Returns:
        Dict with 'materials', 'category_metadata', 'material_index', etc.
    
    Raises:
        MaterialDataError: If file cannot be loaded
    """
    if not MATERIALS_FILE.exists():
        raise MaterialDataError(f"Materials.yaml not found at {MATERIALS_FILE}")
    
    try:
        with open(MATERIALS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MaterialDataError(f"Failed to load Materials.yaml: {e}")


@lru_cache(maxsize=1)
def load_properties_yaml() -> Dict[str, Dict[str, Any]]:
    """
    Load MaterialProperties.yaml
    
    Returns:
        Dict mapping material names to property data
        Format: { "Aluminum": { "density": {...}, "hardness": {...}, ... }, ... }
    
    Raises:
        MaterialDataError: If file cannot be loaded
    """
    if not PROPERTIES_FILE.exists():
        raise MaterialDataError(f"MaterialProperties.yaml not found at {PROPERTIES_FILE}")
    
    try:
        with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('properties', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load MaterialProperties.yaml: {e}")


# load_settings_yaml moved to domains/settings/data_loader.py (Nov 26, 2025)
# Import from there if needed:
# from domains.settings.data_loader import load_settings_yaml


@lru_cache(maxsize=1)
def load_category_metadata_yaml() -> Dict[str, Any]:
    """
    Load CategoryMetadata.yaml (templates, frameworks, regulatory guidance)
    
    Returns:
        Dict with industryGuidance, safetyTemplates, regulatoryTemplates, etc.
    
    Raises:
        MaterialDataError: If file cannot be loaded
    
    Note:
        This file is optional - returns empty dict if not found
    """
    if not METADATA_FILE.exists():
        return {}
    
    try:
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MaterialDataError(f"Failed to load CategoryMetadata.yaml: {e}")


def load_materials_data() -> Dict[str, Any]:
    """
    DEPRECATED: Use orchestrators.data_orchestrator.load_complete_materials_data() instead.
    
    This function is kept for backward compatibility but now delegates to the
    orchestrator layer to avoid cross-domain imports.
    
    Load complete materials data with properties and settings merged.
    
    Returns:
        Complete materials data with structure:
        {
            'materials': {
                'Aluminum': {
                    'name': 'Aluminum',
                    'category': 'metal',
                    'properties': { ... },  # Merged from MaterialProperties.yaml
                    'machine_settings': { ... },     # Merged from Settings.yaml (via orchestrator)
                    ...
                },
                ...
            },
            'category_metadata': { ... },
            'material_index': { ... },
            ...
        }
    
    Raises:
        MaterialDataError: If any file cannot be loaded or merging fails
    """
    # ✅ FIXED (Nov 26, 2025): Delegate to orchestrator to avoid cross-domain imports
    from domains.data_orchestrator import load_complete_materials_data
    return load_complete_materials_data()


def load_material(material_name: str) -> Optional[Dict[str, Any]]:
    """
    Load complete data for a specific material
    
    Args:
        material_name: Name of material (e.g., "Aluminum", "Steel")
    
    Returns:
        Complete material data dict with merged properties and settings,
        or None if material not found
    
    Raises:
        MaterialDataError: If data files cannot be loaded
    
    Example:
        >>> aluminum = load_material("Aluminum")
        >>> print(aluminum['properties']['density'])
        >>> print(aluminum['machine_settings']['powerRange'])
    """
    all_data = load_materials_data()
    materials = all_data.get('materials', {})
    return materials.get(material_name)


def get_material_names() -> list[str]:
    """
    Get list of all available material names
    
    Returns:
        Sorted list of material names
    
    Raises:
        MaterialDataError: If Materials.yaml cannot be loaded
    """
    materials_data = load_materials_yaml()
    materials = materials_data.get('materials', {})
    return sorted(materials.keys())


def get_category_metadata() -> Dict[str, Any]:
    """
    Get category metadata from Materials.yaml
    
    Returns:
        Dict with category information
    
    Raises:
        MaterialDataError: If Materials.yaml cannot be loaded
    """
    materials_data = load_materials_yaml()
    return materials_data.get('category_metadata', {})


def get_material_index() -> Dict[str, str]:
    """
    Get material index (material name -> category mapping)
    
    Returns:
        Dict mapping material names to categories
    
    Raises:
        MaterialDataError: If Materials.yaml cannot be loaded
    """
    materials_data = load_materials_yaml()
    return materials_data.get('material_index', {})


def clear_cache() -> None:
    """
    Clear the LRU cache for all loader functions
    
    Use this if YAML files are modified at runtime and need to be reloaded.
    """
    load_materials_yaml.cache_clear()
    load_properties_yaml.cache_clear()
    load_category_metadata_yaml.cache_clear()
    load_property_research_yaml.cache_clear()
    load_setting_research_yaml.cache_clear()
    # Settings cache is in settings domain (call separately if needed)


# Convenience function for backward compatibility
def load_data() -> Dict[str, Any]:
    """
    Alias for load_materials_data() for backward compatibility
    
    Returns:
        Complete materials data
    """
    return load_materials_data()


# ============================================================================
# New Metadata Accessor Functions (Schema v2.0)
# ============================================================================

def get_property_definitions() -> Dict[str, Any]:
    """
    Get property definitions from MaterialProperties.yaml
    
    Returns detailed descriptions, units, laser cleaning impact, and category
    ranges for all material properties.
    
    Returns:
        Dict mapping property names to definition metadata:
        {
            "density": {
                "description": "Mass per unit volume...",
                "unit": "g/cm³",
                "relevance": "Affects thermal mass...",
                "laser_cleaning_impact": "Influences heat diffusion...",
                "category_ranges": { "metal": {...}, "ceramic": {...}, ... }
            },
            ...
        }
    
    Raises:
        MaterialDataError: If MaterialProperties.yaml cannot be loaded
    
    Example:
        >>> defs = get_property_definitions()
        >>> print(defs['density']['unit'])
        'g/cm³'
    """
    if not PROPERTIES_FILE.exists():
        raise MaterialDataError("MaterialProperties.yaml not found")
    
    try:
        with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('propertyDefinitions', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load propertyDefinitions: {e}")


def get_property_categories() -> Dict[str, Any]:
    """
    Get property categories taxonomy from MaterialProperties.yaml
    
    Returns the two-category taxonomy (laser_material_interaction and
    material_characteristics) with property lists and metadata.
    
    Returns:
        Dict with category taxonomy:
        {
            "metadata": { "version": "5.0.0", "total_categories": 2, ... },
            "categories": {
                "laser_material_interaction": {
                    "id": "laser_material_interaction",
                    "label": "Laser-Material Interaction",
                    "properties": [...],
                    ...
                },
                "material_characteristics": { ... }
            }
        }
    
    Raises:
        MaterialDataError: If MaterialProperties.yaml cannot be loaded
    """
    if not PROPERTIES_FILE.exists():
        raise MaterialDataError("MaterialProperties.yaml not found")
    
    try:
        with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('propertyCategories', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load propertyCategories: {e}")


def get_usage_tiers() -> Dict[str, Any]:
    """
    Get property usage tiers from MaterialProperties.yaml
    
    Returns classification of properties by frequency of use across materials:
    - core: Present in >100 materials
    - common: Present in 30-100 materials  
    - specialized: Present in <30 materials
    
    Returns:
        Dict with usage tier definitions:
        {
            "core": {
                "description": "Present in >100 materials...",
                "threshold": 100,
                "property_count": 15,
                "properties": ["density", "thermalConductivity", ...]
            },
            ...
        }
    
    Raises:
        MaterialDataError: If MaterialProperties.yaml cannot be loaded
    """
    if not PROPERTIES_FILE.exists():
        raise MaterialDataError("MaterialProperties.yaml not found")
    
    try:
        with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('usageTiers', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load usageTiers: {e}")


def get_category_ranges() -> Dict[str, Any]:
    """
    Get category-specific property ranges from MaterialProperties.yaml
    
    Returns min/max ranges for properties across material categories.
    
    Returns:
        Dict mapping category names to property ranges:
        {
            "ceramic": {
                "name": "Ceramic Materials",
                "description": "Advanced ceramic materials...",
                "ranges": {
                    "density": {"min": 2.3, "max": 16.0, "unit": "g/cm³"},
                    "hardness": {"min": 6.0, "max": 2500, "unit": "Mohs"},
                    ...
                }
            },
            ...
        }
    
    Raises:
        MaterialDataError: If MaterialProperties.yaml cannot be loaded
    """
    if not PROPERTIES_FILE.exists():
        raise MaterialDataError("MaterialProperties.yaml not found")
    
    try:
        with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('categoryRanges', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load categoryRanges: {e}")


def get_parameter_ranges() -> Dict[str, Any]:
    """
    Get machine settings parameter ranges from Categories.yaml
    
    Returns min/max ranges for all laser parameters (global ranges).
    These are used to enrich Settings frontmatter with min/max fields.
    
    Source: data/materials/Categories.yaml -> machine_settingsRanges
    
    Returns:
        Dict mapping parameter names to range metadata:
        {
            "powerRange": {
                "min": 1.0,
                "max": 120,
                "unit": "W",
                "description": "Laser power range..."
            },
            "wavelength": {
                "min": 355,
                "max": 10640,
                "unit": "nm",
                "description": "Laser wavelength range..."
            },
            ...
        }
    
    Raises:
        MaterialDataError: If Categories.yaml cannot be loaded
    """
    categories_file = DATA_DIR / "Categories.yaml"
    if not categories_file.exists():
        raise MaterialDataError(f"Categories.yaml not found at {categories_file}")
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data.get('machine_settingsRanges', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load machine_settingsRanges: {e}")


def get_parameter_descriptions() -> Dict[str, Any]:
    """
    Get machine settings parameter descriptions from Settings.yaml
    
    Returns detailed descriptions, selection criteria, and optimization notes
    for all laser parameters.
    
    Returns:
        Dict mapping parameter names to descriptions:
        {
            "fluenceThreshold": {
                "description": "Energy density threshold...",
                "unit": "J/cm²",
                "selection_criteria": "Material damage threshold...",
                "optimization_note": "Critical for selective cleaning..."
            },
            ...
        }
    
    Raises:
        MaterialDataError: If Settings.yaml cannot be loaded
    """
    # Delegate to settings domain (Nov 26, 2025 migration)
    from domains.settings.data_loader import load_settings_yaml
    try:
        data = load_settings_yaml()
        return data.get('parameterDescriptions', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load parameterDescriptions: {e}")


def get_industry_guidance() -> Dict[str, Any]:
    """
    Get industry-specific guidance from CategoryMetadata.yaml
    
    Returns requirements, standards, and quality metrics for different industries
    (aerospace, automotive, medical, marine, etc.).
    
    Returns:
        Dict mapping industry names to guidance:
        {
            "aerospace": {
                "typical_materials": [...],
                "critical_requirements": [...],
                "standards_required": [...],
                "typical_applications": [...],
                "quality_metrics": {...}
            },
            ...
        }
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('industryGuidance', {})


def get_safety_templates() -> Dict[str, Any]:
    """
    Get safety templates from CategoryMetadata.yaml
    
    Returns safety protocols for different material hazard types
    (flammable metals, toxic dusts, reactive materials, etc.).
    
    Returns:
        Dict mapping hazard types to safety templates:
        {
            "flammable_metals": {
                "applicable_materials": [...],
                "primary_hazards": [...],
                "warnings": [...],
                "ppe_requirements": [...],
                "environmental_controls": [...],
                "emergency_procedures": [...]
            },
            ...
        }
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('safetyTemplates', {})


def get_regulatory_templates() -> Dict[str, Any]:
    """
    Get regulatory compliance templates from CategoryMetadata.yaml
    
    Returns regulatory frameworks for different application areas
    (aerospace cleaning, medical devices, automotive, food grade, etc.).
    
    Returns:
        Dict mapping application areas to regulatory templates:
        {
            "aerospace_cleaning": {
                "applicable_industries": [...],
                "primary_standards": [...],
                "documentation_requirements": [...],
                "inspection_requirements": [...],
                "certification_requirements": [...],
                "validation_protocol": {...}
            },
            ...
        }
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('regulatoryTemplates', {})


def get_environmental_impact_templates() -> Dict[str, Any]:
    """
    Get environmental impact templates from CategoryMetadata.yaml
    
    Returns:
        Dict with environmental benefit templates
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('environmentalImpactTemplates', {})


def get_application_type_definitions() -> Dict[str, Any]:
    """
    Get application type definitions from CategoryMetadata.yaml
    
    Returns:
        Dict with application type definitions and typical uses
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('applicationTypeDefinitions', {})


def get_category_definitions() -> Dict[str, Any]:
    """
    Get category definitions from CategoryMetadata.yaml
    
    Returns high-level category metadata (names, descriptions, subcategories,
    regulatory standards) without per-material data.
    
    Returns:
        Dict mapping category names to definitions:
        {
            "ceramic": {
                "name": "Ceramic Materials",
                "description": "Advanced ceramic materials...",
                "subcategories": {...},
                "common_applications": [...],
                "regulatory_standards": [...]
            },
            ...
        }
    
    Raises:
        MaterialDataError: If CategoryMetadata.yaml cannot be loaded
    """
    metadata = load_category_metadata_yaml()
    return metadata.get('categoryDefinitions', {})


@lru_cache(maxsize=1)
def load_categories_yaml() -> Dict[str, Any]:
    """
    Load Categories.yaml (complete category data with ranges and challenges)
    
    Returns:
        Dict with category data including challenges
    
    Raises:
        MaterialDataError: If Categories.yaml cannot be loaded
    """
    if not CATEGORIES_FILE.exists():
        raise MaterialDataError(f"Categories.yaml not found at {CATEGORIES_FILE}")
    
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('categories', {})
    except Exception as e:
        raise MaterialDataError(f"Failed to load Categories.yaml: {e}")


def get_challenges(category: str) -> Dict[str, Any]:
    """
    Get challenges for a specific category from Categories.yaml
    
    Args:
        category: Category name (e.g., 'wood', 'metal', 'ceramic')
    
    Returns:
        Dict with challenges structure:
        {
            "thermal_management": [...],
            "surface_characteristics": [...],
            "contamination_challenges": [...]
        }
        
        Returns empty dict if category not found or no challenges defined.
    """
    categories = load_categories_yaml()
    category_data = categories.get(category, {})
    return category_data.get('challenges', {})


# ============================================================================
# Deep Research Data Access Functions (Schema v3.0)
# ============================================================================

@lru_cache(maxsize=1)
def load_property_research_yaml() -> Dict[str, Any]:
    """
    Load PropertyResearch.yaml (deep research for material properties)
    
    Returns:
        Dict with multi-source property research data
    
    Note:
        This file is optional - returns empty dict if not found
    """
    research_file = DATA_DIR / "PropertyResearch.yaml"
    if not research_file.exists():
        return {}
    
    try:
        with open(research_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MaterialDataError(f"Failed to load PropertyResearch.yaml: {e}")


@lru_cache(maxsize=1)
def load_setting_research_yaml() -> Dict[str, Any]:
    """
    Load SettingResearch.yaml (deep research for machine settings)
    
    Returns:
        Dict with context-specific setting research data
    
    Note:
        This file is optional - returns empty dict if not found
    """
    research_file = DATA_DIR / "SettingResearch.yaml"
    if not research_file.exists():
        return {}
    
    try:
        with open(research_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MaterialDataError(f"Failed to load SettingResearch.yaml: {e}")


@lru_cache(maxsize=1)
def load_parameter_definitions_yaml() -> Dict[str, Any]:
    """
    Load ParameterDefinitions.yaml (universal parameter definitions with ranges)
    
    Returns:
        Dict with parameter ranges, definitions, relationships, safety parameters
    
    Raises:
        MaterialDataError: If ParameterDefinitions.yaml cannot be loaded
    """
    if not PARAMETER_DEFS_FILE.exists():
        raise MaterialDataError(f"ParameterDefinitions.yaml not found at {PARAMETER_DEFS_FILE}")
    
    try:
        with open(PARAMETER_DEFS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MaterialDataError(f"Failed to load ParameterDefinitions.yaml: {e}")


def get_property_research(material_name: str, property_name: str) -> Optional[Dict[str, Any]]:
    """
    Get deep research data for a specific material property.
    
    Returns multiple researched values from different sources with contexts,
    citations, and metadata for drill-down pages.
    
    Args:
        material_name: Name of material (e.g., "Aluminum")
        property_name: Name of property (e.g., "density", "thermalConductivity")
    
    Returns:
        Dict with research data:
        {
            "primary": {
                "value": 2.70,
                "unit": "g/cm³",
                "confidence": 100,
                "source": "ai_research"
            },
            "research": {
                "values": [
                    {
                        "value": 2.70,
                        "unit": "g/cm³",
                        "confidence": 100,
                        "source": "ASM Handbook",
                        "source_type": "handbook",
                        "purity": "99.99%",
                        ...
                    },
                    ...
                ],
                "metadata": {
                    "total_sources": 5,
                    "value_range": {"min": 2.699, "max": 2.81},
                    ...
                }
            }
        }
        
        Returns None if material or property not found in research data.
    
    Example:
        >>> research = get_property_research("Aluminum", "density")
        >>> print(f"Found {research['research']['metadata']['total_sources']} sources")
        Found 6 sources
    """
    research_data = load_property_research_yaml()
    
    if material_name not in research_data:
        return None
    
    material_research = research_data[material_name]
    return material_research.get(property_name)


def get_setting_research(material_name: str, setting_name: str) -> Optional[Dict[str, Any]]:
    """
    Get deep research data for a specific material setting.
    
    Returns context-specific variations (different wavelengths, powers, etc.)
    with performance metrics, advantages/disadvantages, and use cases.
    
    Args:
        material_name: Name of material (e.g., "Aluminum")
        setting_name: Name of setting (e.g., "wavelength", "powerRange")
    
    Returns:
        Dict with research data:
        {
            "primary": {
                "value": 1064,
                "unit": "nm",
                "description": "..."
            },
            "research": {
                "values": [
                    {
                        "value": 355,
                        "unit": "nm",
                        "confidence": 90,
                        "source": "Journal of Laser Applications",
                        "context": {
                            "application": "precision_cleaning",
                            "material_condition": "thin_oxide",
                            ...
                        },
                        "advantages": [...],
                        "disadvantages": [...],
                        "optimal_for": [...],
                        "performance": {...}
                    },
                    ...
                ],
                "metadata": {
                    "available_wavelengths": [355, 532, 1064, 10640],
                    "primary_wavelength": 1064,
                    ...
                }
            }
        }
        
        Returns None if material or setting not found in research data.
    
    Example:
        >>> research = get_setting_research("Aluminum", "wavelength")
        >>> wavelengths = research['research']['metadata']['available_wavelengths']
        >>> print(f"Available: {wavelengths}")
        Available: [355, 532, 1064, 2940, 10640]
    """
    research_data = load_setting_research_yaml()
    
    if material_name not in research_data:
        return None
    
    material_research = research_data[material_name]
    return material_research.get(setting_name)


def get_all_property_research(property_name: str) -> Dict[str, Any]:
    """
    Get research data across all materials for a specific property.
    
    Useful for property drill-down pages that compare the same property
    across different materials.
    
    Args:
        property_name: Name of property (e.g., "density", "thermalConductivity")
    
    Returns:
        Dict mapping material names to property research:
        {
            "Aluminum": {
                "primary": {...},
                "research": {...}
            },
            "Steel": {
                "primary": {...},
                "research": {...}
            },
            ...
        }
    
    Example:
        >>> all_density = get_all_property_research("density")
        >>> for material, data in all_density.items():
        >>>     print(f"{material}: {data['primary']['value']} {data['primary']['unit']}")
    """
    research_data = load_property_research_yaml()
    result = {}
    
    for material_name, material_research in research_data.items():
        if material_name.startswith('_'):  # Skip metadata keys
            continue
        if property_name in material_research:
            result[material_name] = material_research[property_name]
    
    return result


def get_all_setting_research(setting_name: str) -> Dict[str, Any]:
    """
    Get research data across all materials for a specific setting.
    
    Useful for setting drill-down pages that compare the same setting
    across different materials.
    
    Args:
        setting_name: Name of setting (e.g., "wavelength", "powerRange")
    
    Returns:
        Dict mapping material names to setting research:
        {
            "Aluminum": {
                "primary": {...},
                "research": {...}
            },
            "Steel": {
                "primary": {...},
                "research": {...}
            },
            ...
        }
    
    Example:
        >>> all_wavelength = get_all_setting_research("wavelength")
        >>> for material, data in all_wavelength.items():
        >>>     print(f"{material}: {data['primary']['value']} {data['primary']['unit']}")
    """
    research_data = load_setting_research_yaml()
    result = {}
    
    for material_name, material_research in research_data.items():
        if material_name.startswith('_'):  # Skip metadata keys
            continue
        if setting_name in material_research:
            result[material_name] = material_research[setting_name]
    
    return result


def get_material_variations(material_name: str) -> Dict[str, Any]:
    """
    Get alloy and composition variations for a material.
    
    Returns information about different alloys, purities, and compositions
    of the same base material (e.g., aluminum alloys 1100, 2024, 6061, 7075).
    
    Args:
        material_name: Base material name (e.g., "Aluminum")
    
    Returns:
        Dict with variation information:
        {
            "base_material": "Aluminum",
            "variations": [
                {
                    "name": "Pure Aluminum",
                    "designation": "99.99%",
                    "composition": "Al > 99.99%",
                    "properties": {...},
                    "applications": [...]
                },
                {
                    "name": "6061-T6",
                    "designation": "AA-6061",
                    "composition": "Al-Mg-Si",
                    "properties": {...},
                    "applications": [...]
                },
                ...
            ]
        }
        
        Returns None if no variation data available.
    
    Note:
        Variation data is extracted from PropertyResearch and SettingResearch
        files where alloy-specific values are present.
    """
    # Extract variations from property research
    property_research = load_property_research_yaml()
    
    variations = {
        "base_material": material_name,
        "variations": []
    }
    
    # Look for alloy variations in property research
    if material_name in property_research:
        material_props = property_research[material_name]
        alloys_seen = set()
        
        for prop_name, prop_data in material_props.items():
            if prop_name.startswith('_'):
                continue
            if 'research' not in prop_data:
                continue
            
            for value_entry in prop_data['research'].get('values', []):
                alloy = value_entry.get('alloy')
                if alloy and alloy not in alloys_seen:
                    alloys_seen.add(alloy)
                    variations['variations'].append({
                        'designation': alloy,
                        'composition': value_entry.get('composition'),
                        'purity': value_entry.get('purity'),
                        'notes': value_entry.get('notes')
                    })
    
    return variations if variations['variations'] else None
