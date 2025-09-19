#!/usr/bin/env python3
"""
Frontmatter Field Ordering Validation Tool

Validates that all frontmatter files follow the proposed field ordering structure.
"""

import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrontmatterOrderingValidator:
    """Validates frontmatter field ordering compliance"""
    
    def __init__(self):
        self.expected_order = [
            # === 1. BASIC IDENTIFICATION ===
            "name", "category",
            
            # === 2. CONTENT METADATA ===
            "title", "headline", "description", "keywords",
            
            # === 3. CHEMICAL CLASSIFICATION ===
            "chemicalProperties",
            
            # === 4. MATERIAL PROPERTIES (Grouped) ===
            "properties",
            
            # === 5. MATERIAL COMPOSITION ===
            "composition",
            
            # === 6. LASER MACHINE SETTINGS (Grouped) ===
            "machineSettings",
            
            # === 7. APPLICATIONS ===
            "applications",
            
            # === 8. COMPATIBILITY ===
            "compatibility",
            
            # === 9. REGULATORY STANDARDS ===
            "regulatoryStandards",
            
            # === 10. AUTHOR INFORMATION ===
            "author", "author_object",
            
            # === 11. VISUAL ASSETS ===
            "images",
            
            # === 12. IMPACT METRICS ===
            "environmentalImpact", "outcomes"
        ]
        
        self.property_groups = [
            "density", "meltingPoint", "thermalConductivity",
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        self.machine_setting_groups = [
            "powerRange", "pulseDuration", "wavelength", "spotSize",
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]

    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """Validate a single frontmatter file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract YAML content
            if content.startswith('---\n'):
                yaml_end = content.find('\n---', 4)
                if yaml_end != -1:
                    yaml_content = content[4:yaml_end]
                else:
                    yaml_content = content[4:]
            else:
                logger.error(f"Invalid frontmatter format in {filepath}")
                return {"valid": False, "errors": ["Invalid frontmatter format"]}
                
            # Parse YAML
            try:
                data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                return {"valid": False, "errors": [f"YAML parsing error: {e}"]}
                
            if not data:
                return {"valid": False, "errors": ["Empty YAML content"]}
                
            # Validate ordering
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "field_order_score": 0,
                "grouped_structure_score": 0
            }
            
            # Check top-level field ordering
            field_order_errors = self._validate_top_level_ordering(data)
            if field_order_errors:
                validation_result["errors"].extend(field_order_errors)
                validation_result["valid"] = False
            else:
                validation_result["field_order_score"] = 100
                
            # Check properties grouping
            if "properties" in data:
                properties_errors = self._validate_properties_grouping(data["properties"])
                if properties_errors:
                    validation_result["warnings"].extend(properties_errors)
                else:
                    validation_result["grouped_structure_score"] += 50
                    
            # Check machine settings grouping
            if "machineSettings" in data:
                machine_errors = self._validate_machine_settings_grouping(data["machineSettings"])
                if machine_errors:
                    validation_result["warnings"].extend(machine_errors)
                else:
                    validation_result["grouped_structure_score"] += 50
                    
            return validation_result
            
        except Exception as e:
            return {"valid": False, "errors": [f"Error reading file: {e}"]}

    def _validate_top_level_ordering(self, data: Dict) -> List[str]:
        """Validate top-level field ordering"""
        errors = []
        actual_fields = list(data.keys())
        
        # Check if fields appear in the expected order
        expected_positions = {field: i for i, field in enumerate(self.expected_order)}
        
        for i, field in enumerate(actual_fields):
            if field in expected_positions:
                expected_pos = expected_positions[field]
                
                # Check if any earlier expected field appears later
                for j in range(i + 1, len(actual_fields)):
                    later_field = actual_fields[j]
                    if later_field in expected_positions:
                        later_expected_pos = expected_positions[later_field]
                        if later_expected_pos < expected_pos:
                            errors.append(
                                f"Field '{later_field}' should appear before '{field}' "
                                f"(position {j} vs {i})"
                            )
                            
        return errors

    def _validate_properties_grouping(self, properties: Dict) -> List[str]:
        """Validate properties have proper grouped structure"""
        warnings = []
        
        for prop_group in self.property_groups:
            if prop_group in properties:
                # Check if the group has proper numeric/unit separation
                if f"{prop_group}Numeric" not in properties:
                    warnings.append(f"Property '{prop_group}' missing numeric component")
                if f"{prop_group}Unit" not in properties:
                    warnings.append(f"Property '{prop_group}' missing unit component")
                    
                # Check grouping order within the property
                prop_keys = list(properties.keys())
                base_idx = prop_keys.index(prop_group) if prop_group in prop_keys else -1
                
                if base_idx >= 0:
                    expected_order = [
                        prop_group,
                        f"{prop_group}Numeric",
                        f"{prop_group}Unit"
                    ]
                    
                    # Add min/max fields based on property type
                    if prop_group == "meltingPoint":
                        expected_order.extend([
                            "meltingMin", "meltingMinNumeric", "meltingMinUnit",
                            "meltingMax", "meltingMaxNumeric", "meltingMaxUnit",
                            "meltingPercentile"
                        ])
                    elif prop_group == "thermalConductivity":
                        expected_order.extend([
                            "thermalMin", "thermalMinNumeric", "thermalMinUnit",
                            "thermalMax", "thermalMaxNumeric", "thermalMaxUnit",
                            "thermalPercentile"
                        ])
                    elif prop_group == "tensileStrength":
                        expected_order.extend([
                            "tensileMin", "tensileMinNumeric", "tensileMinUnit",
                            "tensileMax", "tensileMaxNumeric", "tensileMaxUnit",
                            "tensilePercentile"
                        ])
                    elif prop_group == "hardness":
                        expected_order.extend([
                            "hardnessMin", "hardnessMinNumeric", "hardnessMinUnit",
                            "hardnessMax", "hardnessMaxNumeric", "hardnessMaxUnit",
                            "hardnessPercentile"
                        ])
                    elif prop_group == "youngsModulus":
                        expected_order.extend([
                            "modulusMin", "modulusMinNumeric", "modulusMinUnit",
                            "modulusMax", "modulusMaxNumeric", "modulusMaxUnit",
                            "modulusPercentile"
                        ])
                    else:
                        expected_order.extend([
                            f"{prop_group}Min", f"{prop_group}MinNumeric", f"{prop_group}MinUnit",
                            f"{prop_group}Max", f"{prop_group}MaxNumeric", f"{prop_group}MaxUnit",
                            f"{prop_group}Percentile"
                        ])
                    
                    # Check order within the group
                    for field in expected_order:
                        if field in prop_keys:
                            field_idx = prop_keys.index(field)
                            if field_idx < base_idx:
                                warnings.append(
                                    f"Property field '{field}' appears before its base property '{prop_group}'"
                                )
                                
        return warnings

    def _validate_machine_settings_grouping(self, machine_settings: Dict) -> List[str]:
        """Validate machine settings have proper grouped structure"""
        warnings = []
        
        for setting_group in self.machine_setting_groups:
            if setting_group in machine_settings:
                # Check if the group has proper numeric/unit separation
                if f"{setting_group}Numeric" not in machine_settings:
                    warnings.append(f"Machine setting '{setting_group}' missing numeric component")
                if f"{setting_group}Unit" not in machine_settings:
                    warnings.append(f"Machine setting '{setting_group}' missing unit component")
                    
        return warnings

    def validate_all_files(self) -> Dict[str, Any]:
        """Validate all frontmatter files"""
        frontmatter_dir = Path("content/components/frontmatter")
        
        if not frontmatter_dir.exists():
            return {"error": "Frontmatter directory not found"}
            
        files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
        if not files:
            return {"error": "No frontmatter files found"}
            
        results = {}
        total_valid = 0
        total_files = len(files)
        
        for file_path in files:
            material_name = file_path.stem.replace("-laser-cleaning", "")
            validation_result = self.validate_file(str(file_path))
            results[material_name] = validation_result
            
            if validation_result["valid"]:
                total_valid += 1
                
        # Generate summary
        summary = {
            "total_files": total_files,
            "valid_files": total_valid,
            "compliance_rate": (total_valid / total_files * 100) if total_files > 0 else 0,
            "results": results
        }
        
        return summary

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("# 📋 Frontmatter Field Ordering Validation Report")
        report.append("")
        report.append(f"**Generated:** {self._get_timestamp()}")
        report.append("")
        
        # Summary
        report.append("## 📊 Summary")
        report.append(f"- **Total Files:** {results['total_files']}")
        report.append(f"- **Valid Files:** {results['valid_files']}")
        report.append(f"- **Compliance Rate:** {results['compliance_rate']:.1f}%")
        report.append("")
        
        # Individual file results
        if "results" in results:
            report.append("## 📄 Individual File Results")
            report.append("")
            
            for material, result in results["results"].items():
                if result["valid"]:
                    report.append(f"### ✅ {material}")
                    report.append(f"- **Field Order Score:** {result.get('field_order_score', 0)}%")
                    report.append(f"- **Grouped Structure Score:** {result.get('grouped_structure_score', 0)}%")
                else:
                    report.append(f"### ❌ {material}")
                    
                if result.get("errors"):
                    report.append("**Errors:**")
                    for error in result["errors"]:
                        report.append(f"- {error}")
                        
                if result.get("warnings"):
                    report.append("**Warnings:**")
                    for warning in result["warnings"]:
                        report.append(f"- {warning}")
                        
                report.append("")
                
        return "\n".join(report)

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main validation function"""
    print("🔍 Validating frontmatter field ordering...")
    
    validator = FrontmatterOrderingValidator()
    results = validator.validate_all_files()
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return 1
        
    # Print summary
    print("\n📊 Validation Results:")
    print(f"Total files: {results['total_files']}")
    print(f"Valid files: {results['valid_files']}")
    print(f"Compliance rate: {results['compliance_rate']:.1f}%")
    
    # Generate and save report
    report = validator.generate_report(results)
    
    os.makedirs("logs/validation_reports", exist_ok=True)
    report_path = "logs/validation_reports/frontmatter_ordering_validation.md"
    
    with open(report_path, "w") as f:
        f.write(report)
        
    print(f"\n📄 Detailed report saved: {report_path}")
    
    # Return exit code based on compliance
    return 0 if results["compliance_rate"] == 100 else 1


if __name__ == "__main__":
    exit(main())
