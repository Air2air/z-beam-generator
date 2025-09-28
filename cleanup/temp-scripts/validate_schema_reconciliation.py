#!/usr/bin/env python3
"""
Schema Reconciliation Validation Test
Tests updated schemas against existing data to ensure compatibility
"""

import json
import yaml
from pathlib import Path
from jsonschema import Draft7Validator

class SchemaReconciliationValidator:
    def __init__(self):
        self.schemas_dir = Path("schemas")
        self.data_dir = Path("data") 
        self.frontmatter_dir = Path("content/components/frontmatter")
        
        self.validation_results = {
            "materials_yaml": {"status": "not_tested", "errors": []},
            "material": {"status": "not_tested", "errors": []}, 
            "frontmatter": {"status": "not_tested", "errors": []},
            "base": {"status": "not_tested", "errors": []}
        }

    def load_schema(self, schema_name):
        """Load a JSON schema file"""
        schema_path = self.schemas_dir / f"{schema_name}.json"
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {schema_name}.json: {e}")
            return None

    def validate_materials_yaml_schema(self):
        """Validate Materials.yaml against updated Materials_yaml.json schema"""
        print("🔍 Validating Materials.yaml against Materials_yaml.json schema...")
        
        schema = self.load_schema("materials_yaml")
        if not schema:
            self.validation_results["materials_yaml"]["status"] = "schema_load_failed"
            return False

        try:
            # Load Materials.yaml 
            materials_path = self.data_dir / "Materials.yaml"
            with open(materials_path, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Validate against schema
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(materials_data))
            
            if errors:
                self.validation_results["materials_yaml"]["status"] = "validation_failed"
                self.validation_results["materials_yaml"]["errors"] = [
                    f"{error.json_path}: {error.message}" for error in errors[:10]  # Limit to first 10 errors
                ]
                print(f"❌ Found {len(errors)} validation errors in Materials.yaml")
                for i, error in enumerate(errors[:5]):  # Show first 5 errors
                    print(f"  {i+1}. {error.json_path}: {error.message}")
                if len(errors) > 5:
                    print(f"  ... and {len(errors) - 5} more errors")
                return False
            else:
                self.validation_results["materials_yaml"]["status"] = "passed"
                print("✅ Materials.yaml validates successfully against Materials_yaml.json")
                return True
                
        except Exception as e:
            self.validation_results["materials_yaml"]["status"] = "test_failed"
            self.validation_results["materials_yaml"]["errors"] = [str(e)]
            print(f"❌ Error validating Materials.yaml: {e}")
            return False

    def validate_frontmatter_samples(self):
        """Validate sample frontmatter files against frontmatter.json schema"""
        print("🔍 Validating frontmatter samples against frontmatter.json schema...")
        
        schema = self.load_schema("frontmatter")
        if not schema:
            self.validation_results["frontmatter"]["status"] = "schema_load_failed"
            return False

        try:
            # Get a few sample frontmatter files
            md_files = list(self.frontmatter_dir.glob("*.md"))[:5]  # Test first 5 files
            
            validation_errors = []
            successful_validations = 0
            
            for file_path in md_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract YAML frontmatter
                    if content.startswith('---'):
                        yaml_start = content.find('---') + 3
                        yaml_end = content.find('---', yaml_start)
                        if yaml_end != -1:
                            yaml_content = content[yaml_start:yaml_end].strip()
                            data = yaml.safe_load(yaml_content)
                            
                            # Validate against schema
                            validator = Draft7Validator(schema)
                            errors = list(validator.iter_errors(data))
                            
                            if errors:
                                validation_errors.extend([
                                    f"{file_path.name}: {error.json_path}: {error.message}" 
                                    for error in errors[:3]  # Limit errors per file
                                ])
                            else:
                                successful_validations += 1
                
                except Exception as e:
                    validation_errors.append(f"{file_path.name}: Error parsing - {e}")
            
            if validation_errors:
                self.validation_results["frontmatter"]["status"] = "validation_failed"
                self.validation_results["frontmatter"]["errors"] = validation_errors[:10]
                print(f"❌ Found validation errors in {len(validation_errors)} frontmatter files")
                for error in validation_errors[:5]:
                    print(f"  - {error}")
                print(f"✅ {successful_validations}/{len(md_files)} files validated successfully")
                return False
            else:
                self.validation_results["frontmatter"]["status"] = "passed"
                print(f"✅ All {len(md_files)} frontmatter samples validate successfully")
                return True
                
        except Exception as e:
            self.validation_results["frontmatter"]["status"] = "test_failed"
            self.validation_results["frontmatter"]["errors"] = [str(e)]
            print(f"❌ Error validating frontmatter files: {e}")
            return False

    def validate_schema_syntax(self):
        """Validate that all updated schemas have valid JSON syntax"""
        print("🔍 Validating schema JSON syntax...")
        
        schema_names = ["materials_yaml", "material", "frontmatter", "base"]
        syntax_valid = True
        
        for schema_name in schema_names:
            try:
                schema = self.load_schema(schema_name)
                if schema:
                    print(f"  ✅ {schema_name}.json - Valid JSON syntax")
                else:
                    print(f"  ❌ {schema_name}.json - Failed to load")
                    syntax_valid = False
            except Exception as e:
                print(f"  ❌ {schema_name}.json - Syntax error: {e}")
                syntax_valid = False
        
        return syntax_valid

    def generate_summary_report(self):
        """Generate a summary report of validation results"""
        print("\n" + "="*60)
        print("SCHEMA RECONCILIATION VALIDATION SUMMARY")
        print("="*60)
        
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results.values() if result["status"] == "passed")
        
        print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
        print()
        
        for schema_name, result in self.validation_results.items():
            status = result["status"]
            if status == "passed":
                print(f"✅ {schema_name}: PASSED")
            elif status == "validation_failed":
                print(f"❌ {schema_name}: VALIDATION FAILED")
                print(f"   Errors: {len(result['errors'])}")
            elif status == "schema_load_failed":
                print(f"❌ {schema_name}: SCHEMA LOAD FAILED") 
            elif status == "test_failed":
                print(f"❌ {schema_name}: TEST ERROR")
            else:
                print(f"⏸️  {schema_name}: NOT TESTED")
        
        print()
        if passed_tests == total_tests:
            print("🎉 ALL VALIDATIONS PASSED - Schema reconciliation successful!")
        else:
            print("⚠️  Some validations failed - Review errors above")
        
        return passed_tests == total_tests

    def run_all_validations(self):
        """Run all validation tests"""
        print("🚀 Starting Schema Reconciliation Validation Tests")
        print("="*60)
        
        # Test 1: Schema syntax validation
        syntax_valid = self.validate_schema_syntax()
        print()
        
        # Test 2: Materials.yaml validation
        if syntax_valid:
            self.validate_materials_yaml_schema()
            print()
        
        # Test 3: Frontmatter validation  
        if syntax_valid:
            self.validate_frontmatter_samples()
            print()
        
        # Generate summary
        return self.generate_summary_report()


def main():
    validator = SchemaReconciliationValidator()
    success = validator.run_all_validations()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())