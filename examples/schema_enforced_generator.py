#!/usr/bin/env python3
"""
Schema-Enforced Frontmatter Generator - Implementation Example

Demonstrates the recommended schema-as-single-source-of-truth architecture:
1. Enhanced schema with nested property validation
2. Mandatory schema compliance in generation
3. Eliminated data redundancy between materials.yaml and generated content
4. Research validation metadata integration

This is a proof-of-concept showing how the new architecture would work.
"""

import json
import jsonschema
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class SchemaComplianceError(Exception):
    """Raised when generated content violates schema"""
    pass


class EnhancedSchemaValidator:
    """Schema validator with comprehensive validation and error reporting"""
    
    def __init__(self, schema_path: str):
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        self.validator = jsonschema.Draft7Validator(self.schema)
    
    def validate(self, data: Dict[str, Any]) -> SchemaValidationResult:
        """Comprehensive schema validation with detailed error reporting"""
        errors = []
        warnings = []
        
        # Standard JSON schema validation
        validation_errors = list(self.validator.iter_errors(data))
        
        for error in validation_errors:
            error_path = " → ".join([str(part) for part in error.absolute_path])
            error_message = f"{error_path}: {error.message}"
            errors.append(error_message)
        
        # Additional validation rules
        self._validate_research_metadata(data, errors, warnings)
        self._validate_property_completeness(data, errors, warnings)
        
        return SchemaValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_research_metadata(self, data: Dict, errors: List[str], warnings: List[str]):
        """Validate research validation metadata requirements"""
        properties = data.get('properties', {})
        
        # Check for validation metadata in critical properties
        critical_properties = ['density', 'melting_point', 'thermal_conductivity']
        
        for prop_name in critical_properties:
            if prop_name in properties:
                prop_data = properties[prop_name]
                if isinstance(prop_data, dict):
                    validation = prop_data.get('validation', {})
                    
                    # Check required validation fields
                    if 'confidence_score' not in validation:
                        errors.append(f"properties.{prop_name}.validation: Missing required confidence_score")
                    
                    if 'sources_validated' not in validation:
                        errors.append(f"properties.{prop_name}.validation: Missing required sources_validated")
                    
                    # Check validation quality
                    confidence = validation.get('confidence_score', 0)
                    if confidence < 0.8:
                        warnings.append(f"properties.{prop_name}: Low confidence score ({confidence})")
    
    def _validate_property_completeness(self, data: Dict, errors: List[str], warnings: List[str]):
        """Validate property data completeness and quality"""
        properties = data.get('properties', {})
        
        for prop_name, prop_data in properties.items():
            if isinstance(prop_data, dict):
                # Check for required nested fields
                if 'value' not in prop_data:
                    errors.append(f"properties.{prop_name}: Missing required 'value' field")
                
                if 'unit' not in prop_data:
                    errors.append(f"properties.{prop_name}: Missing required 'unit' field")
                
                # Check for recommended fields
                if 'description' not in prop_data:
                    warnings.append(f"properties.{prop_name}: Missing recommended 'description' field")


class SchemaEnforcedFrontmatterGenerator:
    """Frontmatter generator with mandatory schema compliance"""
    
    def __init__(self, schema_path: str):
        self.validator = EnhancedSchemaValidator(schema_path)
        self.project_root = Path(__file__).parent.parent.parent
    
    def generate_frontmatter(self, material_id: str) -> Dict[str, Any]:
        """
        Generate schema-compliant frontmatter with mandatory validation.
        
        This demonstrates the new architecture where:
        1. materials.yaml contains only metadata
        2. All properties are generated fresh with research validation
        3. Schema compliance is mandatory (fail-fast)
        """
        
        # 1. Load minimal material metadata
        material_metadata = self._load_material_metadata(material_id)
        
        # 2. Generate comprehensive properties with research validation
        # (In practice, this would use AI with schema-aware prompts)
        generated_frontmatter = self._generate_schema_compliant_data(material_metadata)
        
        # 3. MANDATORY schema validation (fail-fast)
        validation_result = self.validator.validate(generated_frontmatter)
        
        if not validation_result.is_valid:
            error_details = '\n'.join(validation_result.errors)
            raise SchemaComplianceError(
                f"Generated frontmatter violates schema for {material_id}:\n{error_details}"
            )
        
        # 4. Log warnings for quality improvement
        if validation_result.warnings:
            warning_details = '\n'.join(validation_result.warnings)
            print(f"⚠️  Quality warnings for {material_id}:\n{warning_details}")
        
        return generated_frontmatter
    
    def _load_material_metadata(self, material_id: str) -> Dict[str, Any]:
        """Load minimal metadata from materials.yaml (new simplified structure)"""
        
        # Simulated simplified materials.yaml structure
        simplified_materials = {
            "aluminum": {
                "category": "metal",
                "subcategory": "aerospace", 
                "complexity": "high",
                "author_id": 4,
                "generation_profile": {
                    "research_priority": ["density", "melting_point", "thermal_conductivity"],
                    "machine_settings_focus": ["wavelength", "power_range", "fluence"],
                    "validation_requirements": ["confidence_score", "sources_validated"]
                }
            }
        }
        
        if material_id not in simplified_materials:
            raise ValueError(f"Material {material_id} not found in metadata")
        
        return simplified_materials[material_id]
    
    def _generate_schema_compliant_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive frontmatter data that complies with enhanced schema.
        
        In production, this would use AI with schema-aware prompts.
        This example shows the expected structure.
        """
        
        return {
            "name": "aluminum",
            "category": metadata["category"],
            "subcategory": metadata["subcategory"],
            "title": "Laser Cleaning aluminum",
            "description": "Technical overview of aluminum laser cleaning applications and parameters",
            
            # Enhanced properties with nested validation metadata
            "properties": {
                "density": {
                    "value": 4.43,
                    "unit": "g/cm³",
                    "min": 4.40,
                    "max": 4.45,
                    "description": "Material density - critical for laser absorption calculations",
                    "validation": {
                        "confidence_score": 0.95,
                        "sources_validated": 3,
                        "research_sources": [
                            "ASM Aerospace Materials Handbook",
                            "NIST Materials Database", 
                            "Titanium Industry Association Data"
                        ],
                        "accuracy_class": "validated",
                        "material_specific": True
                    },
                    "processing_impact": "Higher density materials require increased laser power for effective cleaning"
                },
                "melting_point": {
                    "value": 1660,
                    "unit": "°C", 
                    "min": 1655,
                    "max": 1665,
                    "description": "Melting point - critical threshold for laser processing",
                    "validation": {
                        "confidence_score": 0.98,
                        "sources_validated": 4,
                        "research_sources": [
                            "ASM Materials Handbook",
                            "NIST Phase Diagram Database",
                            "Materials Science Textbook",
                            "Titanium Processing Handbook"
                        ],
                        "accuracy_class": "verified",
                        "material_specific": True
                    },
                    "processing_impact": "Sets maximum processing temperature - avoid exceeding 1500°C during cleaning"
                },
                "thermal_conductivity": {
                    "value": 6.7,
                    "unit": "W/m·K",
                    "min": 6.5,
                    "max": 7.0,
                    "description": "Thermal conductivity - affects heat dissipation during laser processing",
                    "validation": {
                        "confidence_score": 0.93,
                        "sources_validated": 3,
                        "research_sources": [
                            "Materials Property Database",
                            "Thermal Properties Handbook",
                            "ASM Aerospace Materials"
                        ],
                        "accuracy_class": "validated",
                        "material_specific": True
                    },
                    "processing_impact": "Low thermal conductivity requires careful heat management to prevent thermal damage"
                }
            },
            
            # Enhanced machine settings with validation
            "machineSettings": {
                "wavelength": {
                    "value": 1064,
                    "unit": "nm",
                    "description": "Optimal laser wavelength for titanium - Nd:YAG fundamental",
                    "validation": {
                        "confidence_score": 0.92,
                        "sources_validated": 2,
                        "research_sources": [
                            "Laser Processing Handbook",
                            "Titanium Laser Processing Guide"
                        ]
                    },
                    "optimization_notes": "Ti-6Al-4V shows excellent absorption at 1064nm wavelength"
                },
                "power_range": {
                    "min": 150,
                    "max": 300,
                    "value": 225,  # Average of range for demonstration
                    "unit": "W",
                    "description": "Optimal laser power range for titanium cleaning",
                    "validation": {
                        "confidence_score": 0.88,
                        "sources_validated": 3,
                        "research_sources": [
                            "Industrial Laser Processing Guide",
                            "Titanium Cleaning Parameters Study",
                            "Aerospace Material Processing Standards"
                        ]
                    },
                    "optimization_notes": "Power range optimized for contamination removal without substrate damage"
                }
            },
            
            # Applications with research backing
            "applications": [
                "Aerospace: Removal of oxidation and surface contaminants from Ti-6Al-4V components",
                "Medical: Cleaning of titanium alloy implants and surgical instruments", 
                "Marine: Corrosion-resistant components for ships and offshore platforms",
                "Chemical Processing: Heat exchangers and pressure vessels",
                "Automotive: Performance components and exhaust systems",
                "Sports Equipment: High-performance bicycle frames and golf clubs"
            ],
            
            # Author assignment
            "author_id": metadata["author_id"]
        }


def demonstrate_schema_enforcement():
    """Demonstrate the schema-enforced generation process"""
    
    print("🔍 SCHEMA-ENFORCED FRONTMATTER GENERATION DEMO")
    print("=" * 60)
    
    # Use enhanced schema for demo
    schema_path = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/schemas/enhanced_frontmatter.json"
    
    try:
        generator = SchemaEnforcedFrontmatterGenerator(schema_path)
        
        print("📊 Generating schema-compliant frontmatter for aluminum...")
        
        # Generate with mandatory schema validation
        frontmatter = generator.generate_frontmatter("aluminum")
        
        print("✅ Generation successful - schema compliance verified")
        print(f"📋 Generated {len(frontmatter)} top-level fields")
        print(f"🔬 Properties generated: {len(frontmatter.get('properties', {}))}")
        print(f"⚙️  Machine settings: {len(frontmatter.get('machineSettings', {}))}")
        
        # Display validation metadata coverage
        properties_with_validation = 0
        for prop_name, prop_data in frontmatter.get('properties', {}).items():
            if isinstance(prop_data, dict) and 'validation' in prop_data:
                properties_with_validation += 1
        
        print(f"🔬 Research validation coverage: {properties_with_validation}/{len(frontmatter.get('properties', {}))}")
        
        return frontmatter
        
    except SchemaComplianceError as e:
        print(f"❌ Schema compliance error: {e}")
        return None
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None


if __name__ == "__main__":
    demonstrate_schema_enforcement()