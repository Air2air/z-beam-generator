#!/usr/bin/env python3
"""
Data Completeness Validator

Enforces 100% data completeness for frontmatter generation:
1. Validates all essential properties are present and researched
2. Detects and re-categorizes legacy qualitative properties
3. Validates all property values (not just new discoveries)
4. Enforces comprehensive property coverage
5. Detects empty sections and triggers research

Author: October 17, 2025
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

from components.frontmatter.qualitative_properties import (
    is_qualitative_property,
    QUALITATIVE_PROPERTIES,
    MATERIAL_CHARACTERISTICS_CATEGORIES
)

logger = logging.getLogger(__name__)


@dataclass
class CompletenessResult:
    """Result of completeness validation."""
    is_complete: bool
    missing_properties: List[str]
    empty_sections: List[str]
    legacy_qualitative: Dict[str, List[str]]  # category -> [properties]
    unvalidated_values: List[str]
    error_messages: List[str]
    warnings: List[str]


class CompletenessValidator:
    """
    Validates 100% data completeness for frontmatter.
    
    Enforces:
    - All essential properties present
    - No empty sections (materialProperties, machineSettings)
    - Legacy qualitative properties re-categorized
    - All values validated and researched
    - Comprehensive property coverage
    """
    
    # Comprehensive essential properties per category
    # NOTE: All categories now use unified 'thermalDestruction' property
    # PropertyValueResearcher handles automatic alias resolution for legacy names:
    # - meltingPoint → thermalDestruction (type: melting)
    # - sinteringPoint → thermalDestruction (type: sintering)
    # - degradationPoint → thermalDestruction (type: degradation)
    # - thermalDegradationPoint → thermalDestruction (type: degradation)
    # - softeningPoint → thermalDestruction (type: softening)
    ESSENTIAL_PROPERTIES = {
        'metal': {
            # Thermal properties (unified thermalDestruction replaces meltingPoint)
            'thermalDestruction', 'thermalConductivity',
            # Physical properties
            'density', 'hardness', 'elasticModulus', 'tensileStrength',
            # Optical properties
            'reflectivity', 'absorptionCoefficient',
            # Surface properties
            'surfaceRoughness',
            # Laser interaction
            'ablationThreshold'
        },
        'ceramic': {
            'thermalDestruction', 'thermalConductivity', 'density', 'hardness',  # Changed sinteringPoint → thermalDestruction
            'elasticModulus', 'compressiveStrength', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'plastic': {
            'thermalDestruction', 'thermalConductivity', 'density',  # Changed degradationPoint/meltingPoint → thermalDestruction
            'tensileStrength', 'elasticModulus', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'composite': {
            'thermalDestruction', 'thermalConductivity', 'density',  # Changed degradationPoint → thermalDestruction
            'tensileStrength', 'elasticModulus', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'wood': {
            'thermalDestruction', 'density', 'thermalConductivity',
            'hardness', 'laserAbsorption', 'laserReflectivity'
        },
        'stone': {
            'thermalDestruction', 'density', 'hardness',  # Changed thermalDegradationPoint → thermalDestruction
            'compressiveStrength', 'thermalConductivity', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'glass': {
            'thermalDestruction', 'thermalConductivity', 'density',  # Changed softeningPoint → thermalDestruction
            'hardness', 'elasticModulus', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'semiconductor': {
            'thermalDestruction', 'thermalConductivity', 'density',
            'hardness', 'bandGap', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold', 'surfaceRoughness'
        },
        'masonry': {
            'thermalDestruction', 'density', 'hardness',  # Changed thermalDegradationPoint → thermalDestruction
            'compressiveStrength', 'thermalConductivity', 'reflectivity',
            'absorptionCoefficient', 'ablationThreshold'
        }
    }
    
    # Essential machine settings
    ESSENTIAL_MACHINE_SETTINGS = {
        'powerRange', 'wavelength', 'pulseWidth', 'repetitionRate',
        'scanSpeed', 'spotSize', 'fluenceThreshold'
    }
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize completeness validator.
        
        Args:
            strict_mode: If True, enforce 100% completeness (fail on any gap)
        """
        self.strict_mode = strict_mode
        self.logger = logger
    
    def validate_completeness(
        self,
        frontmatter: Dict,
        material_name: str,
        material_category: str
    ) -> CompletenessResult:
        """
        Validate complete data coverage in frontmatter.
        
        Args:
            frontmatter: Generated frontmatter content
            material_name: Material name
            material_category: Category (metal, plastic, etc.)
            
        Returns:
            CompletenessResult with validation details
        """
        errors = []
        warnings = []
        missing_props = []
        empty_sections = []
        legacy_qualitative = {}
        unvalidated = []
        
        # 1. Check for empty sections
        if not frontmatter.get('materialProperties'):
            empty_sections.append('materialProperties')
            errors.append(f"materialProperties section is empty for {material_name}")
        
        if not frontmatter.get('machineSettings'):
            empty_sections.append('machineSettings')
            errors.append(f"machineSettings section is empty for {material_name}")
        
        # 2. Validate essential properties present
        essential = self.ESSENTIAL_PROPERTIES.get(material_category, set())
        present_props = self._extract_all_properties(frontmatter.get('materialProperties', {}))
        
        missing = essential - present_props
        if missing:
            missing_props.extend(sorted(missing))
            errors.append(
                f"Missing {len(missing)} essential properties for {material_category}: "
                f"{', '.join(sorted(missing)[:5])}{'...' if len(missing) > 5 else ''}"
            )
        
        # 3. Detect legacy qualitative properties in wrong categories
        legacy_qual = self._detect_legacy_qualitative(
            frontmatter.get('materialProperties', {})
        )
        if legacy_qual:
            legacy_qualitative = legacy_qual
            warnings.append(
                f"Found {sum(len(v) for v in legacy_qual.values())} legacy qualitative "
                f"properties that should be re-categorized"
            )
        
        # 4. Validate all values have confidence and sources
        unvalidated = self._find_unvalidated_values(
            frontmatter.get('materialProperties', {})
        )
        if unvalidated:
            warnings.append(
                f"Found {len(unvalidated)} properties without confidence scores: "
                f"{', '.join(unvalidated[:3])}{'...' if len(unvalidated) > 3 else ''}"
            )
        
        # 5. Validate machine settings completeness
        present_settings = set(frontmatter.get('machineSettings', {}).keys())
        missing_settings = self.ESSENTIAL_MACHINE_SETTINGS - present_settings
        if missing_settings:
            missing_props.extend(sorted(missing_settings))
            errors.append(
                f"Missing {len(missing_settings)} essential machine settings: "
                f"{', '.join(sorted(missing_settings))}"
            )
        
        # Determine if complete
        is_complete = (
            len(errors) == 0 and
            len(empty_sections) == 0 and
            len(missing_props) == 0
        )
        
        # In strict mode, warnings also fail
        if self.strict_mode and warnings:
            is_complete = False
            errors.extend([f"STRICT MODE: {w}" for w in warnings])
        
        return CompletenessResult(
            is_complete=is_complete,
            missing_properties=missing_props,
            empty_sections=empty_sections,
            legacy_qualitative=legacy_qualitative,
            unvalidated_values=unvalidated,
            error_messages=errors,
            warnings=warnings
        )
    
    def _extract_all_properties(self, material_properties: Dict) -> Set[str]:
        """Extract all property names from categorized structure."""
        properties = set()
        
        for category_name, category_data in material_properties.items():
            if isinstance(category_data, dict) and 'properties' in category_data:
                for prop_name, prop_data in category_data['properties'].items():
                    properties.add(prop_name)
                    
                    # Handle nested thermalDestruction structure
                    # thermalDestruction: { point: {...}, type: 'melting' }
                    if prop_name == 'thermalDestruction' and isinstance(prop_data, dict):
                        if 'point' in prop_data and isinstance(prop_data['point'], dict):
                            # Valid nested structure - count as thermalDestruction present
                            pass
        
        return properties
    
    def _detect_legacy_qualitative(self, material_properties: Dict) -> Dict[str, List[str]]:
        """
        Detect qualitative properties in wrong categories.
        
        Returns:
            Dict mapping category -> [qualitative property names]
        """
        legacy = {}
        
        for category_name, category_data in material_properties.items():
            if not isinstance(category_data, dict) or 'properties' not in category_data:
                continue
            
            # Skip if already in material_characteristics
            if category_name == 'material_characteristics':
                continue
            
            qualitative_props = []
            for prop_name in category_data['properties'].keys():
                if is_qualitative_property(prop_name):
                    qualitative_props.append(prop_name)
            
            if qualitative_props:
                legacy[category_name] = qualitative_props
        
        return legacy
    
    def _find_unvalidated_values(self, material_properties: Dict) -> List[str]:
        """Find properties without confidence scores or validation."""
        unvalidated = []
        
        for category_name, category_data in material_properties.items():
            if not isinstance(category_data, dict) or 'properties' not in category_data:
                continue
            
            for prop_name, prop_data in category_data['properties'].items():
                if not isinstance(prop_data, dict):
                    continue
                
                # Handle nested thermalDestruction structure
                if prop_name == 'thermalDestruction':
                    if 'point' in prop_data and isinstance(prop_data['point'], dict):
                        # Check nested point has confidence
                        if 'confidence' not in prop_data['point']:
                            unvalidated.append(f"{category_name}.{prop_name}.point")
                            continue
                        confidence = prop_data['point'].get('confidence', 0)
                        if not isinstance(confidence, (int, float)) or confidence <= 0:
                            unvalidated.append(f"{category_name}.{prop_name}.point")
                    continue
                
                # Check for confidence score
                if 'confidence' not in prop_data:
                    unvalidated.append(f"{category_name}.{prop_name}")
                    continue
                
                # Check confidence is valid
                confidence = prop_data.get('confidence', 0)
                if not isinstance(confidence, (int, float)) or confidence <= 0:
                    unvalidated.append(f"{category_name}.{prop_name}")
        
        return unvalidated
    
    def migrate_legacy_qualitative(
        self,
        material_properties: Dict
    ) -> Tuple[Dict, List[str]]:
        """
        Migrate legacy qualitative properties to material_characteristics.
        # FLATTENED STRUCTURE - No nested 'properties' key
        
        Args:
            material_properties: Current materialProperties structure (flattened)
            
        Returns:
            Tuple of (updated_material_properties, migration_log)
        """
        migration_log = []
        updated = material_properties.copy()
        
        # Metadata fields to skip
        metadata_fields = {'label', 'description', 'percentage'}
        
        # Ensure material_characteristics category exists
        if 'material_characteristics' not in updated:
            updated['material_characteristics'] = {
                'label': 'Material Characteristics',
                'description': 'Intrinsic physical, mechanical, chemical, and structural properties',
                'percentage': 0
            }
        
        # Scan all categories for qualitative properties
        for category_name in list(updated.keys()):
            if category_name == 'material_characteristics':
                continue
            
            category_data = updated[category_name]
            if not isinstance(category_data, dict):
                continue
            
            # Find and move qualitative properties (FLATTENED: direct children of category)
            props_to_move = []
            for prop_name in list(category_data.keys()):
                # Skip metadata fields
                if prop_name in metadata_fields:
                    continue
                # Check if qualitative
                if is_qualitative_property(prop_name):
                    props_to_move.append(prop_name)
            
            for prop_name in props_to_move:
                prop_data = category_data.pop(prop_name)
                updated['material_characteristics'][prop_name] = prop_data
                migration_log.append(
                    f"Migrated {prop_name} from {category_name} to material_characteristics"
                )
        
        # Recalculate percentages
        updated = self._recalculate_percentages(updated)
        
        return updated, migration_log
    
    def _recalculate_percentages(self, material_properties: Dict) -> Dict:
        """Recalculate category percentages after migration (FLATTENED structure)."""
        # Metadata fields to skip when counting properties
        metadata_fields = {'label', 'description', 'percentage'}
        
        # Count total properties across all categories
        total_props = 0
        for cat_data in material_properties.values():
            if isinstance(cat_data, dict):
                # Count non-metadata fields as properties
                prop_count = sum(1 for key in cat_data.keys() if key not in metadata_fields)
                total_props += prop_count
        
        if total_props == 0:
            return material_properties
        
        # Recalculate percentages for each category
        for category_data in material_properties.values():
            if isinstance(category_data, dict):
                # Count non-metadata fields as properties
                prop_count = sum(1 for key in category_data.keys() if key not in metadata_fields)
                category_data['percentage'] = round((prop_count / total_props) * 100, 1)
        
        return material_properties
