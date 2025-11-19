#!/usr/bin/env python3
"""
Text Field Classifier for Frontmatter Generation

Separates frontmatter fields into:
- Text fields (need AI generation with Grok)
- Data fields (populate from Materials.yaml directly)
- Hybrid fields (structured data with text descriptions)

This enables efficient generation modes:
1. Data-only mode: Refresh non-text data without AI calls
2. Text-only mode: Update text fields with optimized AI (Grok)
3. Full mode: Generate everything (existing behavior)
"""

from typing import Dict, Tuple, Any
from enum import Enum

class FieldType(Enum):
    """Classification of frontmatter field types"""
    TEXT = "text"           # Pure text content requiring AI generation
    DATA = "data"           # Structured data from Materials.yaml
    HYBRID = "hybrid"       # Data with text descriptions
    METADATA = "metadata"   # System metadata (dates, IDs, etc.)

class TextFieldClassifier:
    """Classifies frontmatter fields for optimized generation"""
    
    # Pure text fields that benefit from AI generation (Grok)
    TEXT_FIELDS = {
        'subtitle',
        'description', 
        'research_basis',
        'validation_method',
        'safety_notes',
        'application_notes',
        'performance_notes',
        'limitations',
        'recommendations',
        'technical_notes'
    }
    
    # Nested text fields within data structures
    NESTED_TEXT_FIELDS = {
        'description',
        'notes', 
        'explanation',
        'methodology',
        'basis',
        'rationale',
        'summary'
    }
    
    # Data fields populated directly from Materials.yaml
    DATA_FIELDS = {
        'name',
        'title', 
        'category',
        'subcategory',
        'formula',
        'density',
        'melting_point',
        'boiling_point',
        'thermal_conductivity',
        'electrical_conductivity',
        'hardness',
        'young_modulus',
        'poisson_ratio',
        'tensile_strength',
        'yield_strength',
        'applications',  # From industryTags in Materials.yaml
        'industries'
    }
    
    # Metadata fields (system-generated)
    METADATA_FIELDS = {
        'id',
        'created_at', 
        'updated_at',
        'version',
        'source',
        'research_date',
        'verification_date',
        'last_modified'
    }
    
    # Hybrid fields (data + descriptions)
    HYBRID_FIELDS = {
        'properties',           # Numeric values + descriptions
        'machineSettings',      # Numeric ranges + explanations
        'materialProperties',   # Values + validation methods
        'laserProcessing',      # Settings + application notes
        'safetyConsiderations', # Data + detailed explanations
        'qualityMetrics'        # Metrics + methodology descriptions
    }

    @classmethod
    def classify_field(cls, field_name: str, field_value: Any, parent_path: str = '') -> FieldType:
        """
        Classify a single field based on name and structure
        
        Args:
            field_name: Name of the field
            field_value: Value of the field
            parent_path: Path to parent field (for nested analysis)
            
        Returns:
            FieldType classification
        """
        # full_path = f"{parent_path}.{field_name}" if parent_path else field_name
        
        # Direct text field classification
        if field_name in cls.TEXT_FIELDS:
            return FieldType.TEXT
            
        # Nested text field classification
        if field_name in cls.NESTED_TEXT_FIELDS:
            return FieldType.TEXT
            
        # Data field classification
        if field_name in cls.DATA_FIELDS:
            return FieldType.DATA
            
        # Metadata field classification  
        if field_name in cls.METADATA_FIELDS:
            return FieldType.METADATA
            
        # Hybrid field classification
        if field_name in cls.HYBRID_FIELDS:
            return FieldType.HYBRID
            
        # Dynamic classification based on value type and content
        if isinstance(field_value, str):
            # Long strings are likely text content
            if len(field_value) > 100:
                return FieldType.TEXT
            # Short strings are likely identifiers/metadata
            elif len(field_value) < 20:
                return FieldType.METADATA
            else:
                return FieldType.TEXT
                
        elif isinstance(field_value, (int, float)):
            return FieldType.DATA
            
        elif isinstance(field_value, dict):
            return FieldType.HYBRID
            
        elif isinstance(field_value, list):
            # List of strings might be applications/tags
            if field_value and isinstance(field_value[0], str):
                return FieldType.DATA
            else:
                return FieldType.HYBRID
                
        else:
            return FieldType.METADATA

    @classmethod
    def classify_frontmatter_structure(cls, frontmatter: Dict) -> Dict[str, FieldType]:
        """
        Classify all fields in a frontmatter structure
        
        Args:
            frontmatter: Complete frontmatter dictionary
            
        Returns:
            Dictionary mapping field paths to FieldType classifications
        """
        classifications = {}
        
        def classify_recursive(obj: Any, path: str = '') -> None:
            """Recursively classify all fields"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    field_type = cls.classify_field(key, value, path)
                    classifications[current_path] = field_type
                    
                    # Recurse into nested structures
                    if isinstance(value, dict):
                        classify_recursive(value, current_path)
                    elif isinstance(value, list) and value and isinstance(value[0], dict):
                        for i, item in enumerate(value[:3]):  # Sample first 3 items
                            classify_recursive(item, f"{current_path}[{i}]")
                            
        classify_recursive(frontmatter)
        return classifications

    @classmethod
    def get_text_fields(cls, frontmatter: Dict) -> Dict[str, Any]:
        """
        Extract only text fields that need AI generation
        
        Args:
            frontmatter: Complete frontmatter dictionary
            
        Returns:
            Dictionary containing only text fields
        """
        classifications = cls.classify_frontmatter_structure(frontmatter)
        text_fields = {}
        
        for field_path, field_type in classifications.items():
            if field_type == FieldType.TEXT:
                # Extract the actual field value
                keys = field_path.split('.')
                value = frontmatter
                try:
                    for key in keys:
                        if '[' in key:  # Handle array indices
                            base_key = key.split('[')[0]
                            index = int(key.split('[')[1].rstrip(']'))
                            value = value[base_key][index]
                        else:
                            value = value[key]
                    text_fields[field_path] = value
                except (KeyError, IndexError, TypeError):
                    continue
                    
        return text_fields

    @classmethod
    def get_data_fields(cls, frontmatter: Dict) -> Dict[str, Any]:
        """
        Extract only data fields that can be populated from Materials.yaml
        
        Args:
            frontmatter: Complete frontmatter dictionary
            
        Returns:
            Dictionary containing only data fields
        """
        classifications = cls.classify_frontmatter_structure(frontmatter)
        data_fields = {}
        
        for field_path, field_type in classifications.items():
            if field_type == FieldType.DATA:
                # Extract the actual field value
                keys = field_path.split('.')
                value = frontmatter
                try:
                    for key in keys:
                        if '[' in key:  # Handle array indices
                            base_key = key.split('[')[0]
                            index = int(key.split('[')[1].rstrip(']'))
                            value = value[base_key][index]
                        else:
                            value = value[key]
                    data_fields[field_path] = value
                except (KeyError, IndexError, TypeError):
                    continue
                    
        return data_fields

    @classmethod
    def separate_fields_by_type(cls, frontmatter: Dict) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Separate frontmatter into text, data, hybrid, and metadata fields
        
        Args:
            frontmatter: Complete frontmatter dictionary
            
        Returns:
            Tuple of (text_fields, data_fields, hybrid_fields, metadata_fields)
        """
        classifications = cls.classify_frontmatter_structure(frontmatter)
        
        text_fields = {}
        data_fields = {}
        hybrid_fields = {}
        metadata_fields = {}
        
        for field_path, field_type in classifications.items():
            # Extract the actual field value
            keys = field_path.split('.')
            value = frontmatter
            try:
                for key in keys:
                    if '[' in key:  # Handle array indices
                        base_key = key.split('[')[0]
                        index = int(key.split('[')[1].rstrip(']'))
                        value = value[base_key][index]
                    else:
                        value = value[key]
                        
                # Assign to appropriate category
                if field_type == FieldType.TEXT:
                    text_fields[field_path] = value
                elif field_type == FieldType.DATA:
                    data_fields[field_path] = value
                elif field_type == FieldType.HYBRID:
                    hybrid_fields[field_path] = value
                elif field_type == FieldType.METADATA:
                    metadata_fields[field_path] = value
                    
            except (KeyError, IndexError, TypeError):
                continue
                
        return text_fields, data_fields, hybrid_fields, metadata_fields

    @classmethod
    def get_generation_summary(cls, frontmatter: Dict) -> Dict[str, int]:
        """
        Get summary statistics for generation requirements
        
        Args:
            frontmatter: Complete frontmatter dictionary
            
        Returns:
            Dictionary with field counts by type
        """
        classifications = cls.classify_frontmatter_structure(frontmatter)
        
        summary = {
            'text_fields': 0,
            'data_fields': 0, 
            'hybrid_fields': 0,
            'metadata_fields': 0,
            'total_fields': len(classifications)
        }
        
        for field_type in classifications.values():
            if field_type == FieldType.TEXT:
                summary['text_fields'] += 1
            elif field_type == FieldType.DATA:
                summary['data_fields'] += 1
            elif field_type == FieldType.HYBRID:
                summary['hybrid_fields'] += 1
            elif field_type == FieldType.METADATA:
                summary['metadata_fields'] += 1
                
        return summary


# Example usage for testing
if __name__ == "__main__":
    # Sample frontmatter structure for testing
    sample_frontmatter = {
        'name': 'Aluminum',
        'subtitle': 'Advanced laser cleaning parameters for aluminum surfaces',
        'description': 'Comprehensive guide to laser cleaning aluminum materials with optimal settings',
        'category': 'Metal',
        'density': 2.70,
        'melting_point': 660.3,
        'applications': ['Automotive', 'Aerospace'],
        'properties': {
            'thermal_conductivity': 205.0,
            'description': 'Excellent thermal conductor enabling efficient heat dissipation',
            'validation_method': 'Measured using ASTM E1461 standard methodology'
        },
        'machineSettings': {
            'power': {'min': 50, 'max': 200, 'unit': 'W'},
            'frequency': {'min': 10, 'max': 50, 'unit': 'kHz'},
            'notes': 'Adjust settings based on oxide layer thickness and surface condition'
        },
        'created_at': '2025-10-21T00:00:00Z'
    }
    
    # Test classification
    classifier = TextFieldClassifier()
    
    print("🔍 FIELD CLASSIFICATION TEST")
    print("=" * 50)
    
    classifications = classifier.classify_frontmatter_structure(sample_frontmatter)
    for field_path, field_type in classifications.items():
        print(f"{field_path:30s} → {field_type.value}")
    
    print("\n📊 GENERATION SUMMARY")
    print("=" * 50)
    
    summary = classifier.get_generation_summary(sample_frontmatter)
    for category, count in summary.items():
        percentage = (count / summary['total_fields'] * 100) if summary['total_fields'] > 0 else 0
        print(f"{category:20s}: {count:3d} ({percentage:5.1f}%)")
        
    print("\n🎯 FIELD SEPARATION")
    print("=" * 50)
    
    text_fields, data_fields, hybrid_fields, metadata_fields = classifier.separate_fields_by_type(sample_frontmatter)
    
    print(f"📝 Text fields requiring AI (Grok): {len(text_fields)}")
    for field in text_fields.keys():
        print(f"  • {field}")
        
    print(f"\n📊 Data fields from Materials.yaml: {len(data_fields)}")
    for field in data_fields.keys():
        print(f"  • {field}")
        
    print(f"\n🔄 Hybrid fields (data + text): {len(hybrid_fields)}")
    for field in hybrid_fields.keys():
        print(f"  • {field}")