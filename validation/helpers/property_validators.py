#!/usr/bin/env python3
"""
Property Validation Helpers

Extracted from PreGenerationValidationService to reduce code bloat.
Contains property field and value validation logic.
"""

from typing import Dict, List

# Qualitative-only properties that don't need numeric validation
QUALITATIVE_ONLY_PROPERTIES = {
    'oxidationResistance', 'corrosionResistance', 'chemicalStability',
    'waterSolubility', 'surfacePreparation', 'thermalDestructionType'
}


class PropertyValidators:
    """Static validation methods for property fields and values"""
    
    @staticmethod
    def validate_property_fields(material: str, prop_name: str, prop_data: Dict) -> List[Dict]:
        """
        Validate that a property has all required metadata fields.
        
        Required fields for all properties:
        - value: The actual property value
        - unit: Units of measurement
        - confidence: Confidence score (0-1)
        - source: Data source ('ai_research' for new materials)
        """
        issues = []
        
        required_fields = {
            'value': 'Property value',
            'unit': 'Units of measurement',
            'confidence': 'Confidence score',
            'source': 'Data source'
        }
        
        # Check for missing required fields
        for field, description in required_fields.items():
            if field not in prop_data or prop_data[field] is None:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'missing_property_field',
                    'material': material,
                    'property': prop_name,
                    'field': field,
                    'message': f"Property '{prop_name}' missing required field '{field}' ({description})"
                })
        
        # Validate confidence is between 0 and 1
        if 'confidence' in prop_data:
            try:
                conf = float(prop_data['confidence'])
                if not (0 <= conf <= 1):
                    issues.append({
                        'severity': 'ERROR',
                        'type': 'invalid_confidence',
                        'material': material,
                        'property': prop_name,
                        'confidence': conf,
                        'message': f"Property '{prop_name}' has invalid confidence {conf} (must be 0-1)"
                    })
            except (ValueError, TypeError):
                issues.append({
                    'severity': 'ERROR',
                    'type': 'invalid_confidence',
                    'material': material,
                    'property': prop_name,
                    'message': f"Property '{prop_name}' has non-numeric confidence value"
                })
        
        # Validate source
        if 'source' in prop_data:
            source = prop_data['source']
            if source not in ['ai_research', 'materials_science', 'published_data']:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'non_standard_source',
                    'material': material,
                    'property': prop_name,
                    'source': source,
                    'message': f"Property '{prop_name}' has non-standard source '{source}'"
                })
        
        return issues
    
    @staticmethod
    def validate_property_value(material: str, category: str, prop_name: str, 
                               prop_data: Dict, property_rule) -> List[Dict]:
        """Validate individual property value against rules"""
        issues = []
        
        value = prop_data.get('value')
        unit = prop_data.get('unit', '')
        
        if value is None:
            return issues
        
        # Skip numeric validation for qualitative-only properties
        if prop_name in QUALITATIVE_ONLY_PROPERTIES:
            return issues
        
        try:
            val = float(value)
            
            # Check unit
            if property_rule.allowed_units and unit not in property_rule.allowed_units:
                issues.append({
                    'severity': 'ERROR',
                    'type': 'invalid_unit',
                    'material': material,
                    'property': prop_name,
                    'value': val,
                    'unit': unit,
                    'expected_units': property_rule.allowed_units,
                    'message': f"Property '{prop_name}' has invalid unit '{unit}' (expected: {property_rule.allowed_units})"
                })
            
            # Check category-specific ranges
            if category in property_rule.category_specific_ranges:
                min_val, max_val = property_rule.category_specific_ranges[category]
                if not (min_val <= val <= max_val):
                    issues.append({
                        'severity': 'ERROR',
                        'type': 'out_of_range',
                        'material': material,
                        'category': category,
                        'property': prop_name,
                        'value': val,
                        'min': min_val,
                        'max': max_val,
                        'message': f"Property '{prop_name}' value {val} outside {category} range [{min_val}, {max_val}]"
                    })
            # Check general ranges
            elif property_rule.min_value is not None or property_rule.max_value is not None:
                min_val = property_rule.min_value if property_rule.min_value is not None else float('-inf')
                max_val = property_rule.max_value if property_rule.max_value is not None else float('inf')
                
                if not (min_val <= val <= max_val):
                    issues.append({
                        'severity': 'ERROR',
                        'type': 'out_of_range',
                        'material': material,
                        'property': prop_name,
                        'value': val,
                        'min': min_val if min_val != float('-inf') else None,
                        'max': max_val if max_val != float('inf') else None,
                        'message': f"Property '{prop_name}' value {val} outside valid range"
                    })
        
        except (ValueError, TypeError):
            # Value isn't numeric - might be qualitative
            if prop_name not in QUALITATIVE_ONLY_PROPERTIES:
                issues.append({
                    'severity': 'WARNING',
                    'type': 'non_numeric_value',
                    'material': material,
                    'property': prop_name,
                    'value': value,
                    'message': f"Property '{prop_name}' has non-numeric value: {value}"
                })
        
        return issues
