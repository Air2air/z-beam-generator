#!/usr/bin/env python3
"""
Comprehensive Frontmatter Data Validation System

Provides multi-layer validation for frontmatter data values:
1. Schema validation against material.json
2. Cross-field consistency validation
3. Numeric value validation
4. Unit validation
5. Range validation
6. Component compatibility validation
"""

import json
import logging
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class DataValueValidator:
    """Validates actual data values in frontmatter"""
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path or Path(__file__).parent.parent.parent / "schemas" / "material.json"
        self.schema = self._load_schema()
        
        # Expected value ranges for validation
        self.value_ranges = {
            'density': {'min': 0.1, 'max': 25.0, 'unit': 'g/cm³'},
            'meltingPoint': {'min': -300, 'max': 4000, 'unit': '°C'},
            'thermalConductivity': {'min': 0.1, 'max': 500, 'unit': 'W/m·K'},
            'tensileStrength': {'min': 1, 'max': 5000, 'unit': 'MPa'},
            'hardness': {'min': 0.1, 'max': 1000, 'unit': 'HB'},
            'youngsModulus': {'min': 0.1, 'max': 1000, 'unit': 'GPa'}
        }
        
        # Required field patterns
        self.required_patterns = {
            'email_pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'url_pattern': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            'wavelength_pattern': r'^\d+(\.\d+)?\s*nm',
            'power_pattern': r'^\d+(\.\d+)?-\d+(\.\d+)?\s*W$',
            'fluence_pattern': r'^\d+(\.\d+)?[–-]\d+(\.\d+)?\s*J/cm²$'
        }
    
    def _load_schema(self) -> Dict:
        """Load material schema for validation"""
        try:
            with open(self.schema_path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load schema from {self.schema_path}: {e}")
            return {}
    
    def validate_numeric_consistency(self, frontmatter: Dict) -> List[str]:
        """Validate numeric field consistency"""
        errors = []
        
        if 'properties' not in frontmatter:
            return errors
            
        props = frontmatter['properties']
        
        # Check density consistency
        if self._has_field_set(props, 'density'):
            errors.extend(self._validate_numeric_field_set(props, 'density'))
        
        # Check melting point consistency  
        if self._has_field_set(props, 'meltingPoint'):
            errors.extend(self._validate_numeric_field_set(props, 'meltingPoint'))
        
        # Check thermal conductivity consistency
        if self._has_field_set(props, 'thermalConductivity'):
            errors.extend(self._validate_numeric_field_set(props, 'thermalConductivity'))
        
        # Check tensile strength consistency
        if self._has_field_set(props, 'tensileStrength'):
            errors.extend(self._validate_numeric_field_set(props, 'tensileStrength'))
        
        # Check hardness consistency
        if self._has_field_set(props, 'hardness'):
            errors.extend(self._validate_numeric_field_set(props, 'hardness'))
        
        # Check Young's modulus consistency
        if self._has_field_set(props, 'youngsModulus'):
            errors.extend(self._validate_numeric_field_set(props, 'youngsModulus'))
        
        return errors
    
    def _has_field_set(self, props: Dict, field: str) -> bool:
        """Check if a complete field set exists"""
        return (field in props and 
                f"{field}Numeric" in props and 
                f"{field}Unit" in props)
    
    def _validate_numeric_field_set(self, props: Dict, field: str) -> List[str]:
        """Validate a complete numeric field set"""
        errors = []
        
        display_value = props.get(field)
        numeric_value = props.get(f"{field}Numeric")
        unit_value = props.get(f"{field}Unit")
        
        # Extract numeric from display value for comparison
        try:
            extracted_numeric = self._extract_numeric_from_display(display_value)
            
            # Check consistency between display and numeric
            if abs(float(numeric_value) - extracted_numeric) > 0.01:
                errors.append(f"{field}: Numeric value {numeric_value} doesn't match display value {display_value}")
        
        except Exception as e:
            errors.append(f"{field}: Could not validate consistency - {e}")
        
        # Validate value ranges
        if field in self.value_ranges:
            value_range = self.value_ranges[field]
            if not (value_range['min'] <= float(numeric_value) <= value_range['max']):
                errors.append(f"{field}: Value {numeric_value} outside expected range {value_range['min']}-{value_range['max']}")
        
        # Validate units
        expected_unit = self.value_ranges.get(field, {}).get('unit')
        if expected_unit and unit_value != expected_unit:
            errors.append(f"{field}: Unit '{unit_value}' doesn't match expected '{expected_unit}'")
        
        return errors
    
    def _extract_numeric_from_display(self, display_value: str) -> float:
        """Extract numeric value from display string"""
        if not display_value:
            return 0.0
        
        # Handle ranges by taking first value
        if '-' in str(display_value):
            parts = str(display_value).split('-')
            value_str = parts[0].strip()
        else:
            value_str = str(display_value)
        
        # Extract numeric part
        numeric_match = re.search(r'(\d+(?:\.\d+)?)', value_str)
        if numeric_match:
            return float(numeric_match.group(1))
        
        return 0.0
    
    def validate_range_consistency(self, frontmatter: Dict) -> List[str]:
        """Validate min/max range consistency"""
        errors = []
        
        if 'properties' not in frontmatter:
            return errors
            
        props = frontmatter['properties']
        
        # Check each field with min/max values
        range_fields = ['density', 'meltingPoint', 'thermalConductivity', 'tensileStrength', 'hardness', 'youngsModulus']
        
        for field in range_fields:
            min_numeric = props.get(f"{field}MinNumeric")
            max_numeric = props.get(f"{field}MaxNumeric")
            
            if min_numeric is not None and max_numeric is not None:
                if float(min_numeric) >= float(max_numeric):
                    errors.append(f"{field}: Min value {min_numeric} should be less than max value {max_numeric}")
                
                # Check if main value is within range
                main_numeric = props.get(f"{field}Numeric")
                if main_numeric is not None:
                    if not (float(min_numeric) <= float(main_numeric) <= float(max_numeric)):
                        errors.append(f"{field}: Value {main_numeric} outside min-max range {min_numeric}-{max_numeric}")
        
        return errors
    
    def validate_technical_specifications(self, frontmatter: Dict) -> List[str]:
        """Validate machine settings format and values (renamed from technicalSpecifications)"""
        errors = []
        
        # Check for machineSettings (new) or technicalSpecifications (backward compatibility)
        if 'machineSettings' not in frontmatter and 'technicalSpecifications' not in frontmatter:
            errors.append("Missing required machineSettings section")
            return errors
        
        # Use machineSettings or fallback to technicalSpecifications
        machine_settings = frontmatter.get('machineSettings', frontmatter.get('technicalSpecifications', {}))
        
        # Required machine setting fields
        required_machine_fields = [
            'powerRange', 'pulseDuration', 'wavelength', 'fluenceRange',
            'spotSize', 'repetitionRate', 'scanningSpeed', 'beamProfile', 'safetyClass'
        ]
        
        for field in required_machine_fields:
            if field not in machine_settings:
                errors.append(f"Missing required machine setting: {field}")
        
        # Validate specific field formats
        if 'wavelength' in machine_settings:
            wavelength = machine_settings['wavelength']
            if not re.match(self.required_patterns['wavelength_pattern'], wavelength):
                errors.append(f"Invalid wavelength format: {wavelength}")
        
        if 'powerRange' in machine_settings:
            power_range = machine_settings['powerRange']
            if not re.match(self.required_patterns['power_pattern'], power_range):
                errors.append(f"Invalid power range format: {power_range}")
        
        if 'fluenceRange' in machine_settings:
            fluence_range = machine_settings['fluenceRange']
            if not re.match(self.required_patterns['fluence_pattern'], fluence_range):
                errors.append(f"Invalid fluence range format: {fluence_range}")
        
        return errors
    
    def validate_author_data(self, frontmatter: Dict) -> List[str]:
        """Validate author data completeness and format"""
        errors = []
        
        if 'author_object' not in frontmatter:
            errors.append("Missing author_object section")
            return errors
        
        author = frontmatter['author_object']
        
        # Required author fields
        required_author_fields = ['id', 'name', 'country', 'expertise']
        for field in required_author_fields:
            if field not in author:
                errors.append(f"Missing required author field: {field}")
        
        # Validate author ID is numeric
        if 'id' in author:
            try:
                author_id = int(author['id'])
                if not (1 <= author_id <= 4):
                    errors.append(f"Author ID {author_id} should be between 1-4")
            except ValueError:
                errors.append(f"Author ID should be numeric: {author['id']}")
        
        return errors
    
    def validate_applications(self, frontmatter: Dict) -> List[str]:
        """Validate applications structure"""
        errors = []
        
        if 'applications' not in frontmatter:
            errors.append("Missing applications section")
            return errors
        
        applications = frontmatter['applications']
        
        if not isinstance(applications, list) or len(applications) == 0:
            errors.append("Applications should be a non-empty list")
            return errors
        
        for i, app in enumerate(applications):
            if not isinstance(app, dict):
                errors.append(f"Application {i} should be a dictionary")
                continue
                
            if 'industry' not in app:
                errors.append(f"Application {i} missing 'industry' field")
            
            if 'detail' not in app:
                errors.append(f"Application {i} missing 'detail' field")
        
        return errors
    
    def validate_complete_frontmatter(self, content: str) -> Tuple[bool, List[str]]:
        """Comprehensive validation of frontmatter data"""
        errors = []
        
        try:
            # Parse frontmatter
            if not content.startswith('---'):
                errors.append("Content doesn't start with YAML frontmatter")
                return False, errors
            
            yaml_end = content.find('---', 3)
            if yaml_end == -1:
                errors.append("YAML frontmatter not properly closed")
                return False, errors
            
            yaml_content = content[3:yaml_end].strip()
            frontmatter = yaml.safe_load(yaml_content)
            
            if not frontmatter:
                errors.append("Empty frontmatter")
                return False, errors
            
            # Run all validation checks
            errors.extend(self.validate_numeric_consistency(frontmatter))
            errors.extend(self.validate_range_consistency(frontmatter))
            errors.extend(self.validate_technical_specifications(frontmatter))
            errors.extend(self.validate_author_data(frontmatter))
            errors.extend(self.validate_applications(frontmatter))
            
            return len(errors) == 0, errors
            
        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors


class CrossComponentValidator:
    """Validates frontmatter works across all components"""
    
    def __init__(self):
        self.test_components = ['caption', 'metatags', 'jsonld', 'table']
    
    def validate_component_compatibility(self, material: str, frontmatter_content: str) -> Tuple[bool, List[str]]:
        """Test frontmatter with all components"""
        errors = []
        
        # Save temporary frontmatter file
        temp_file = Path(f"/tmp/{material}-test-frontmatter.md")
        temp_file.write_text(frontmatter_content)
        
        try:
            for component in self.test_components:
                try:
                    # Test component generation (would need to import run.py properly)
                    # For now, simulate the test
                    if component == 'table':
                        # Check if numeric fields are present for table component
                        if 'densityNumeric' not in frontmatter_content:
                            errors.append(f"Table component requires densityNumeric field")
                    
                    elif component == 'caption':
                        # Check if machine settings are present (new) or technicalSpecifications (backward compatibility)
                        if 'machineSettings' not in frontmatter_content and 'technicalSpecifications' not in frontmatter_content:
                            errors.append("Caption component requires machineSettings or technicalSpecifications")
                    
                    # Add more component-specific checks as needed
                    
                except Exception as e:
                    errors.append(f"{component} component failed: {e}")
        
        finally:
            if temp_file.exists():
                temp_file.unlink()
        
        return len(errors) == 0, errors


def validate_material_frontmatter(material: str, frontmatter_path: Path) -> Tuple[bool, List[str]]:
    """Main validation function for a material's frontmatter"""
    
    if not frontmatter_path.exists():
        return False, [f"Frontmatter file not found: {frontmatter_path}"]
    
    content = frontmatter_path.read_text()
    
    # Data value validation
    data_validator = DataValueValidator()
    data_valid, data_errors = data_validator.validate_complete_frontmatter(content)
    
    # Component compatibility validation
    component_validator = CrossComponentValidator()
    comp_valid, comp_errors = component_validator.validate_component_compatibility(material, content)
    
    all_errors = data_errors + comp_errors
    overall_valid = data_valid and comp_valid
    
    return overall_valid, all_errors


if __name__ == "__main__":
    """Test the validation system"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python3 data_validation.py <material_name>")
        sys.exit(1)
    
    material = sys.argv[1]
    frontmatter_path = Path(f"frontmatter/materials/{material}-laser-cleaning.md")
    
    valid, errors = validate_material_frontmatter(material, frontmatter_path)
    
    if valid:
        print(f"✅ {material} frontmatter validation passed!")
    else:
        print(f"❌ {material} frontmatter validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
