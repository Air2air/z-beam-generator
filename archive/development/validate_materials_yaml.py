#!/usr/bin/env python3
"""
Materials.yaml Schema Validation Script

This script validates the Materials.yaml file against the Materials_yaml.json schema.
It ensures data integrity, type consistency, and proper structure.

Usage:
    python3 scripts/validate_materials_yaml.py
    python3 scripts/validate_materials_yaml.py --verbose
    python3 scripts/validate_materials_yaml.py --fix-errors
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import validate, ValidationError, Draft7Validator
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class MaterialsYamlValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.materials_yaml_path = self.project_root / "data" / "Materials.yaml"
        self.schema_path = self.project_root / "schemas" / "Materials_yaml.json"
        self.errors = []
        self.warnings = []
        
    def load_schema(self) -> Dict[str, Any]:
        """Load the Materials_yaml.json schema."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
            
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_materials_yaml(self) -> Dict[str, Any]:
        """Load the Materials.yaml file."""
        if not self.materials_yaml_path.exists():
            raise FileNotFoundError(f"Materials file not found: {self.materials_yaml_path}")
            
        with open(self.materials_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_structure(self, verbose: bool = False) -> bool:
        """Validate Materials.yaml against the schema."""
        try:
            print("🔍 Loading schema and materials data...")
            schema = self.load_schema()
            materials_data = self.load_materials_yaml()
            
            if verbose:
                print(f"   Schema loaded from: {self.schema_path}")
                print(f"   Materials loaded from: {self.materials_yaml_path}")
                print(f"   Total categories in data: {len(materials_data.get('materials', {}))}")
            
            print("✅ Validating Materials.yaml structure...")
            
            # Create validator with detailed error reporting
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(materials_data))
            
            if not errors:
                print("✅ Materials.yaml is valid according to schema!")
                return True
            else:
                print(f"❌ Found {len(errors)} validation errors:")
                for i, error in enumerate(errors, 1):
                    path = " → ".join(str(p) for p in error.path) if error.path else "root"
                    print(f"   {i}. Path: {path}")
                    print(f"      Error: {error.message}")
                    if verbose and error.context:
                        for j, ctx_error in enumerate(error.context):
                            print(f"      Context {j+1}: {ctx_error.message}")
                    print()
                return False
                
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            return False
        except yaml.YAMLError as e:
            print(f"❌ YAML parsing error: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Schema JSON parsing error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def validate_business_rules(self, verbose: bool = False) -> bool:
        """Validate business logic and data consistency."""
        try:
            materials_data = self.load_materials_yaml()
            issues = []
            
            print("🔍 Validating business rules and data consistency...")
            
            # Check category ranges exist for all material categories
            category_ranges = materials_data.get('category_ranges', {})
            materials = materials_data.get('materials', {})
            
            for category in materials.keys():
                if category not in category_ranges:
                    issues.append(f"Missing category_ranges for '{category}'")
            
            # Check author IDs are within valid range (1-4)
            for category, category_data in materials.items():
                items = category_data.get('items', [])
                for item in items:
                    author_id = item.get('author_id')
                    if author_id and (author_id < 1 or author_id > 4):
                        material_name = item.get('name', 'Unknown')
                        issues.append(f"Invalid author_id {author_id} for material '{material_name}' in category '{category}'")
            
            # Check required fields in materials
            required_fields = ['name', 'author_id', 'complexity', 'difficulty_score', 'category', 'formula', 'symbol']
            for category, category_data in materials.items():
                items = category_data.get('items', [])
                for item in items:
                    material_name = item.get('name', 'Unknown')
                    for field in required_fields:
                        if field not in item:
                            issues.append(f"Missing required field '{field}' for material '{material_name}' in category '{category}'")
            
            if not issues:
                print("✅ Business rules validation passed!")
                return True
            else:
                print(f"⚠️  Found {len(issues)} business rule issues:")
                for issue in issues:
                    print(f"   • {issue}")
                return False
                
        except Exception as e:
            print(f"❌ Error during business rules validation: {e}")
            return False
    
    def generate_validation_report(self) -> str:
        """Generate a comprehensive validation report."""
        timestamp = datetime.now().isoformat()
        
        report = f"""# Materials.yaml Validation Report
Generated: {timestamp}
Schema: {self.schema_path}
Data File: {self.materials_yaml_path}

## Validation Results

### Schema Validation
"""
        
        schema_valid = self.validate_structure(verbose=False)
        report += f"Status: {'✅ PASS' if schema_valid else '❌ FAIL'}\n\n"
        
        report += "### Business Rules Validation\n"
        business_valid = self.validate_business_rules(verbose=False)
        report += f"Status: {'✅ PASS' if business_valid else '❌ FAIL'}\n\n"
        
        report += f"### Overall Status\n"
        overall_valid = schema_valid and business_valid
        report += f"Status: {'✅ VALID' if overall_valid else '❌ INVALID'}\n\n"
        
        return report

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Materials.yaml against schema')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--report', '-r', action='store_true', help='Generate validation report')
    parser.add_argument('--output', '-o', help='Output file for report')
    
    args = parser.parse_args()
    
    validator = MaterialsYamlValidator()
    
    print("🚀 Materials.yaml Schema Validation")
    print("=" * 50)
    
    # Run validations
    schema_valid = validator.validate_structure(verbose=args.verbose)
    business_valid = validator.validate_business_rules(verbose=args.verbose)
    
    # Overall result
    overall_valid = schema_valid and business_valid
    
    print("=" * 50)
    print(f"📊 OVERALL RESULT: {'✅ VALID' if overall_valid else '❌ INVALID'}")
    
    # Generate report if requested
    if args.report:
        report = validator.generate_validation_report()
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to: {args.output}")
        else:
            print("\n" + "=" * 50)
            print("📄 VALIDATION REPORT")
            print("=" * 50)
            print(report)
    
    # Exit with appropriate code
    sys.exit(0 if overall_valid else 1)

if __name__ == "__main__":
    main()
