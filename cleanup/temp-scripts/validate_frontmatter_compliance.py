#!/usr/bin/env python3
"""
Comprehensive Frontmatter Compliance Validator
Evaluates all frontmatter files for completeness and compliance with requirements
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any

class FrontmatterComplianceValidator:
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.schema_path = Path("schemas/frontmatter.json")
        self.required_fields = [
            'name', 'category', 'subcategory', 'title', 'headline', 'description', 
            'keywords', 'author_object', 'images', 'complexity', 'difficulty_score', 
            'author_id'
        ]
        self.validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "warnings": [],
            "missing_fields": {},
            "data_quality_issues": {},
            "yaml_errors": [],
            "enhanced_data_compliance": {}
        }
    
    def load_schema(self) -> Dict[str, Any]:
        """Load frontmatter schema for validation"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load schema: {e}")
            return {}
    
    def validate_yaml_syntax(self, file_path: Path) -> Dict[str, Any]:
        """Validate YAML syntax and structure"""
        result = {"valid": False, "data": None, "errors": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                yaml_start = content.find('---') + 3
                yaml_end = content.find('---', yaml_start)
                if yaml_end == -1:
                    # No closing ---, treat as pure YAML
                    yaml_content = content[yaml_start:].strip()
                else:
                    yaml_content = content[yaml_start:yaml_end].strip()
            else:
                result["errors"].append("File does not start with YAML frontmatter delimiter")
                return result
            
            # Parse YAML
            data = yaml.safe_load(yaml_content)
            if data is None:
                result["errors"].append("YAML content is empty or null")
                return result
            
            result["valid"] = True
            result["data"] = data
            
        except yaml.YAMLError as e:
            result["errors"].append(f"YAML syntax error: {e}")
        except Exception as e:
            result["errors"].append(f"File reading error: {e}")
        
        return result
    
    def validate_required_fields(self, data: Dict[str, Any], filename: str) -> List[str]:
        """Check for presence of all required fields"""
        missing = []
        
        for field in self.required_fields:
            if field not in data:
                missing.append(field)
        
        # Special validation for nested objects
        if 'author_object' in data:
            required_author_fields = ['id', 'name', 'sex', 'title', 'country', 'expertise', 'image']
            for field in required_author_fields:
                if field not in data['author_object']:
                    missing.append(f'author_object.{field}')
        
        if 'images' in data:
            if 'hero' not in data['images'] or 'micro' not in data['images']:
                missing.append('images.hero or images.micro')
            else:
                for img_type in ['hero', 'micro']:
                    if img_type in data['images']:
                        img_data = data['images'][img_type]
                        if 'alt' not in img_data or 'url' not in img_data:
                            missing.append(f'images.{img_type}.alt or images.{img_type}.url')
        
        return missing
    
    def validate_data_quality(self, data: Dict[str, Any], filename: str) -> List[str]:
        """Check data quality and consistency"""
        issues = []
        
        # Check category/subcategory consistency
        if 'category' in data and 'subcategory' in data:
            category = data['category']
            subcategory = data['subcategory']
            
            # Define valid subcategories per category
            valid_subcategories = {
                'metal': ['precious', 'ferrous', 'non-ferrous', 'refractory', 'reactive', 'specialty', 'general'],
                'ceramic': ['oxide', 'nitride', 'carbide', 'traditional'],
                'composite': ['fiber-reinforced', 'matrix', 'resin', 'elastomeric'],
                'glass': ['borosilicate', 'soda-lime', 'lead', 'specialty-glass'],
                'stone': ['igneous', 'metamorphic', 'sedimentary', 'architectural', 'composite'],
                'wood': ['hardwood', 'softwood', 'engineered', 'grass'],
                'plastic': ['thermoplastic', 'thermoset', 'engineering', 'biodegradable'],
                'semiconductor': ['intrinsic', 'doped', 'compound'],
                'masonry': ['fired', 'concrete', 'natural']
            }
            
            if category in valid_subcategories:
                if subcategory not in valid_subcategories[category]:
                    issues.append(f"Invalid subcategory '{subcategory}' for category '{category}'")
        
        # Check numeric values
        numeric_fields = ['complexity', 'difficulty_score']
        for field in numeric_fields:
            if field in data:
                if field == 'difficulty_score':
                    if not isinstance(data[field], int) or data[field] < 1 or data[field] > 5:
                        issues.append(f"difficulty_score must be integer 1-5, got: {data[field]}")
        
        # Check keywords format
        if 'keywords' in data:
            if not isinstance(data['keywords'], list) or len(data['keywords']) == 0:
                issues.append("Keywords must be a non-empty list")
        
        # Check applications format
        if 'applications' in data:
            if not isinstance(data['applications'], list) or len(data['applications']) == 0:
                issues.append("Applications must be a non-empty list")
        
        return issues
    
    def validate_enhanced_data(self, data: Dict[str, Any], filename: str) -> Dict[str, List[str]]:
        """Check for enhanced data features (min/max ranges, units, etc.)"""
        issues = {"missing": [], "inconsistent": []}
        
        # Check properties section
        if 'properties' in data:
            props = data['properties']
            
            # Check for numeric values with units
            numeric_props = ['density', 'thermalConductivity', 'tensileStrength', 'youngsModulus']
            for prop in numeric_props:
                if prop in props:
                    # Check for unit field
                    unit_field = f"{prop}Unit"
                    if unit_field not in props:
                        issues["missing"].append(f"Missing unit field: {unit_field}")
                    
                    # Check for min/max values where applicable
                    min_field = f"{prop}Min"
                    max_field = f"{prop}Max"
                    if min_field in props or max_field in props:
                        if min_field not in props:
                            issues["missing"].append(f"Missing min value: {min_field}")
                        if max_field not in props:
                            issues["missing"].append(f"Missing max value: {max_field}")
        
        # Check machine settings section
        if 'machineSettings' in data:
            settings = data['machineSettings']
            
            # Check for enhanced machine settings
            numeric_settings = ['powerRange', 'wavelength', 'pulseDuration', 'spotSize', 'repetitionRate', 'fluenceRange']
            for setting in numeric_settings:
                if setting in settings:
                    # Check for unit field
                    unit_field = f"{setting}Unit"
                    if unit_field not in settings:
                        issues["missing"].append(f"Missing unit field: {unit_field}")
                    
                    # Check for min/max values
                    min_field = f"{setting}Min"
                    max_field = f"{setting}Max"
                    if min_field not in settings:
                        issues["missing"].append(f"Missing min value: {min_field}")
                    if max_field not in settings:
                        issues["missing"].append(f"Missing max value: {max_field}")
        
        return issues
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single frontmatter file"""
        filename = file_path.name
        result = {
            "filename": filename,
            "valid": False,
            "errors": [],
            "warnings": [],
            "missing_fields": [],
            "data_quality_issues": [],
            "enhanced_data_issues": {}
        }
        
        # 1. YAML syntax validation
        yaml_result = self.validate_yaml_syntax(file_path)
        if not yaml_result["valid"]:
            result["errors"].extend(yaml_result["errors"])
            return result
        
        data = yaml_result["data"]
        
        # 2. Required fields validation
        missing_fields = self.validate_required_fields(data, filename)
        result["missing_fields"] = missing_fields
        if missing_fields:
            result["errors"].append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # 3. Data quality validation
        quality_issues = self.validate_data_quality(data, filename)
        result["data_quality_issues"] = quality_issues
        if quality_issues:
            result["warnings"].extend(quality_issues)
        
        # 4. Enhanced data validation
        enhanced_issues = self.validate_enhanced_data(data, filename)
        result["enhanced_data_issues"] = enhanced_issues
        if enhanced_issues["missing"]:
            result["warnings"].extend([f"Enhanced data missing: {issue}" for issue in enhanced_issues["missing"]])
        if enhanced_issues["inconsistent"]:
            result["warnings"].extend([f"Enhanced data inconsistent: {issue}" for issue in enhanced_issues["inconsistent"]])
        
        # Overall validity
        result["valid"] = len(result["errors"]) == 0
        
        return result
    
    def validate_all_files(self) -> Dict[str, Any]:
        """Validate all frontmatter files"""
        if not self.frontmatter_dir.exists():
            return {"error": f"Frontmatter directory not found: {self.frontmatter_dir}"}
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        self.validation_results["total_files"] = len(md_files)
        
        print(f"🔍 Validating {len(md_files)} frontmatter files...")
        
        file_results = []
        for file_path in md_files:
            result = self.validate_file(file_path)
            file_results.append(result)
            
            if result["valid"]:
                self.validation_results["valid_files"] += 1
            else:
                self.validation_results["invalid_files"] += 1
                self.validation_results["errors"].append({
                    "file": result["filename"],
                    "errors": result["errors"]
                })
            
            if result["warnings"]:
                self.validation_results["warnings"].append({
                    "file": result["filename"],
                    "warnings": result["warnings"]
                })
            
            # Aggregate missing fields
            for field in result["missing_fields"]:
                if field not in self.validation_results["missing_fields"]:
                    self.validation_results["missing_fields"][field] = 0
                self.validation_results["missing_fields"][field] += 1
        
        return {
            "summary": self.validation_results,
            "file_results": file_results
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive compliance report"""
        summary = results["summary"]
        
        report = []
        report.append("=" * 80)
        report.append("FRONTMATTER COMPLIANCE VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append("📊 SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Total files analyzed: {summary['total_files']}")
        report.append(f"Valid files: {summary['valid_files']}")
        report.append(f"Invalid files: {summary['invalid_files']}")
        report.append(f"Compliance rate: {(summary['valid_files']/summary['total_files']*100):.1f}%")
        report.append("")
        
        # Critical errors
        if summary["invalid_files"] > 0:
            report.append("❌ CRITICAL ERRORS")
            report.append("-" * 40)
            for error in summary["errors"]:
                report.append(f"File: {error['file']}")
                for err in error["errors"]:
                    report.append(f"  - {err}")
                report.append("")
        
        # Missing fields analysis
        if summary["missing_fields"]:
            report.append("🔍 MISSING FIELDS ANALYSIS")
            report.append("-" * 40)
            for field, count in sorted(summary["missing_fields"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"{field}: missing in {count} files ({count/summary['total_files']*100:.1f}%)")
            report.append("")
        
        # Warnings analysis
        if summary["warnings"]:
            report.append("⚠️  DATA QUALITY WARNINGS")
            report.append("-" * 40)
            warning_count = len(summary["warnings"])
            report.append(f"Files with warnings: {warning_count}")
            report.append("")
            
            # Show first few warnings as examples
            for i, warning in enumerate(summary["warnings"][:5]):
                report.append(f"File: {warning['file']}")
                for warn in warning["warnings"][:3]:  # Show max 3 warnings per file
                    report.append(f"  - {warn}")
                if len(warning["warnings"]) > 3:
                    report.append(f"  ... and {len(warning['warnings']) - 3} more warnings")
                report.append("")
                if i >= 4:  # Show max 5 files
                    report.append(f"... and {warning_count - 5} more files with warnings")
                    break
        
        # Compliance recommendations
        report.append("✅ COMPLIANCE STATUS")
        report.append("-" * 40)
        if summary["valid_files"] == summary["total_files"]:
            report.append("🎉 EXCELLENT: All frontmatter files are structurally valid!")
        elif summary["valid_files"] >= summary["total_files"] * 0.9:
            report.append("✅ GOOD: >90% of files are valid with minor issues to address")
        elif summary["valid_files"] >= summary["total_files"] * 0.8:
            report.append("⚠️  ACCEPTABLE: >80% of files are valid but improvements needed")
        else:
            report.append("❌ NEEDS ATTENTION: <80% of files are valid - immediate action required")
        
        report.append("")
        report.append("🔧 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if summary["missing_fields"]:
            most_missing = max(summary["missing_fields"].items(), key=lambda x: x[1])
            report.append(f"1. Address most common missing field: '{most_missing[0]}' (missing in {most_missing[1]} files)")
        
        if summary["warnings"]:
            report.append("2. Review and fix data quality warnings shown above")
        
        if summary["invalid_files"] > 0:
            report.append("3. Fix critical YAML syntax errors preventing file parsing")
        
        report.append("4. Consider implementing automated validation in CI/CD pipeline")
        report.append("")
        
        return "\n".join(report)


def main():
    """Main validation function"""
    print("🚀 Starting comprehensive frontmatter compliance validation...")
    
    validator = FrontmatterComplianceValidator()
    results = validator.validate_all_files()
    
    if "error" in results:
        print(f"❌ Validation failed: {results['error']}")
        return False
    
    # Generate and display report
    report = validator.generate_report(results)
    print(report)
    
    # Save detailed results to file
    output_file = "frontmatter_compliance_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Detailed results saved to: {output_file}")
    
    # Return success status
    return results["summary"]["invalid_files"] == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)