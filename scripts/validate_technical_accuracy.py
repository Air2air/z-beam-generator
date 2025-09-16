#!/usr/bin/env python3
"""
Technical Accuracy Validation Script for Frontmatter Generation

This script validates that generated frontmatter contains material-specific,
scientifically accurate technical data rather than generic placeholder values.

Usage:
    python3 scripts/validate_technical_accuracy.py [frontmatter_directory]
    python3 scripts/validate_technical_accuracy.py content/components/frontmatter/
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import statistics


class TechnicalAccuracyValidator:
    """Validates technical accuracy of frontmatter files"""
    
    def __init__(self):
        self.validation_results = []
        self.material_database = self._load_material_database()
        
    def _load_material_database(self) -> Dict:
        """Load expected material properties for validation"""
        return {
            "Silicon Nitride": {
                "formula": "Si3N4",
                "density_range": (3.1, 3.5),
                "melting_range": (1850, 1950),  # Decomposition
                "material_type": "ceramic",
                "thermal_conductivity_range": (15, 120)
            },
            "Titanium Dioxide": {
                "formula": "TiO2", 
                "density_range": (3.8, 4.3),
                "melting_range": (1840, 1870),
                "material_type": "ceramic",
                "thermal_conductivity_range": (5, 12)
            },
            "Aluminum 6061": {
                "formula": "Al",
                "density_range": (2.6, 2.8),
                "melting_range": (580, 650),
                "material_type": "metal", 
                "thermal_conductivity_range": (150, 200)
            },
            "PTFE": {
                "formula": "C2F4",
                "density_range": (2.1, 2.3),
                "melting_range": (320, 340),
                "material_type": "polymer",
                "thermal_conductivity_range": (0.2, 0.3)
            },
            "Stainless Steel 316": {
                "formula": "Fe",
                "density_range": (7.9, 8.1),
                "melting_range": (1370, 1400),
                "material_type": "metal",
                "thermal_conductivity_range": (14, 18)
            }
        }

    def validate_frontmatter_file(self, file_path: Path) -> Dict:
        """Validate a single frontmatter file for technical accuracy"""
        
        results = {
            "file": str(file_path),
            "material_name": None,
            "validations": {},
            "errors": [],
            "warnings": [],
            "score": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                results["errors"].append("No YAML frontmatter found")
                return results
                
            yaml_content = yaml_match.group(1)
            try:
                data = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                results["errors"].append(f"YAML parsing error: {e}")
                return results
            
            # Extract material name
            material_name = data.get("name", "").strip()
            results["material_name"] = material_name
            
            # Run validation checks
            self._validate_density(data, material_name, results)
            self._validate_melting_point(data, material_name, results)
            self._validate_chemical_formula(data, material_name, results)
            self._validate_laser_parameters(data, material_name, results)
            self._validate_thermal_properties(data, material_name, results)
            self._check_for_generic_values(data, results)
            self._validate_applications_specificity(data, results)
            
            # Calculate overall score
            total_checks = len(results["validations"])
            passed_checks = sum(1 for v in results["validations"].values() if v.get("passed", False))
            results["score"] = (passed_checks / total_checks * 100) if total_checks > 0 else 0
            
        except Exception as e:
            results["errors"].append(f"File processing error: {e}")
            
        return results

    def _validate_density(self, data: Dict, material_name: str, results: Dict):
        """Validate density values are material-specific and realistic"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            properties = data.get("properties", {})
            density_str = properties.get("density", "")
            
            if not density_str:
                validation["message"] = "No density found"
                results["validations"]["density"] = validation
                return
            
            # Extract numerical density value
            density_match = re.search(r'([\d.]+)', str(density_str))
            if not density_match:
                validation["message"] = "Could not parse density value"
                results["validations"]["density"] = validation
                return
                
            density_value = float(density_match.group(1))
            validation["details"]["extracted_value"] = density_value
            
            # Check against material database
            if material_name in self.material_database:
                expected_range = self.material_database[material_name]["density_range"]
                min_density, max_density = expected_range
                
                if min_density <= density_value <= max_density:
                    validation["passed"] = True
                    validation["message"] = f"Density {density_value} g/cm³ within expected range {expected_range}"
                else:
                    validation["message"] = f"Density {density_value} g/cm³ outside expected range {expected_range}"
                    results["warnings"].append(f"Density potentially inaccurate for {material_name}")
            else:
                # General range check
                if 0.1 <= density_value <= 25.0:  # Realistic material density range
                    validation["passed"] = True
                    validation["message"] = f"Density {density_value} g/cm³ within realistic range"
                else:
                    validation["message"] = f"Density {density_value} g/cm³ outside realistic range (0.1-25.0)"
                    
        except Exception as e:
            validation["message"] = f"Density validation error: {e}"
            
        results["validations"]["density"] = validation

    def _validate_melting_point(self, data: Dict, material_name: str, results: Dict):
        """Validate melting point values are material-specific"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            properties = data.get("properties", {})
            melting_str = properties.get("meltingPoint", "")
            
            if not melting_str:
                validation["message"] = "No melting point found"
                results["validations"]["melting_point"] = validation
                return
            
            # Extract numerical melting point value
            melting_match = re.search(r'([\d.]+)', str(melting_str))
            if not melting_match:
                validation["message"] = "Could not parse melting point value"
                results["validations"]["melting_point"] = validation
                return
                
            melting_value = float(melting_match.group(1))
            validation["details"]["extracted_value"] = melting_value
            
            # Check against material database
            if material_name in self.material_database:
                expected_range = self.material_database[material_name]["melting_range"]
                min_temp, max_temp = expected_range
                
                if min_temp <= melting_value <= max_temp:
                    validation["passed"] = True
                    validation["message"] = f"Melting point {melting_value}°C within expected range {expected_range}"
                else:
                    validation["message"] = f"Melting point {melting_value}°C outside expected range {expected_range}"
                    results["warnings"].append(f"Melting point potentially inaccurate for {material_name}")
            else:
                # General range check
                if 0 <= melting_value <= 4000:  # Realistic melting point range
                    validation["passed"] = True
                    validation["message"] = f"Melting point {melting_value}°C within realistic range"
                else:
                    validation["message"] = f"Melting point {melting_value}°C outside realistic range (0-4000°C)"
                    
        except Exception as e:
            validation["message"] = f"Melting point validation error: {e}"
            
        results["validations"]["melting_point"] = validation

    def _validate_chemical_formula(self, data: Dict, material_name: str, results: Dict):
        """Validate chemical formula is scientifically correct"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            chemical_props = data.get("chemicalProperties", {})
            formula = chemical_props.get("formula", "") or chemical_props.get("symbol", "")
            
            if not formula:
                validation["message"] = "No chemical formula found"
                results["validations"]["chemical_formula"] = validation
                return
            
            validation["details"]["formula"] = formula
            
            # Check against material database
            if material_name in self.material_database:
                expected_formula = self.material_database[material_name]["formula"]
                if formula == expected_formula:
                    validation["passed"] = True
                    validation["message"] = f"Formula {formula} matches expected {expected_formula}"
                else:
                    validation["message"] = f"Formula {formula} doesn't match expected {expected_formula}"
                    results["warnings"].append(f"Chemical formula may be incorrect for {material_name}")
            else:
                # Basic format validation
                if re.match(r'^[A-Z][a-z]?(\d*[A-Z][a-z]?\d*)*$', formula):
                    validation["passed"] = True
                    validation["message"] = f"Formula {formula} has valid chemical format"
                else:
                    validation["message"] = f"Formula {formula} has invalid chemical format"
                    
        except Exception as e:
            validation["message"] = f"Chemical formula validation error: {e}"
            
        results["validations"]["chemical_formula"] = validation

    def _validate_laser_parameters(self, data: Dict, material_name: str, results: Dict):
        """Validate laser parameters are appropriate for material type"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            tech_specs = data.get("technicalSpecifications", {})
            wavelength = tech_specs.get("wavelength", "")
            fluence = tech_specs.get("fluenceRange", "")
            
            validation["details"]["wavelength"] = wavelength
            validation["details"]["fluence"] = fluence
            
            if not wavelength:
                validation["message"] = "No laser wavelength found"
                results["validations"]["laser_parameters"] = validation
                return
            
            # Extract wavelength values
            wavelength_numbers = re.findall(r'(\d+(?:\.\d+)?)', str(wavelength))
            
            if material_name in self.material_database:
                material_type = self.material_database[material_name]["material_type"]
                
                # Validate wavelength appropriateness
                if material_type == "polymer":
                    # Polymers typically use CO2 lasers (10.6μm = 10600nm)
                    if any(float(w) > 5000 for w in wavelength_numbers):
                        validation["passed"] = True
                        validation["message"] = f"Wavelength appropriate for polymer: {wavelength}"
                    else:
                        validation["message"] = f"Wavelength may not be optimal for polymer: {wavelength}"
                        
                elif material_type in ["metal", "ceramic"]:
                    # Metals/ceramics typically use shorter wavelengths
                    if any(200 <= float(w) <= 2000 for w in wavelength_numbers):
                        validation["passed"] = True
                        validation["message"] = f"Wavelength appropriate for {material_type}: {wavelength}"
                    else:
                        validation["message"] = f"Wavelength may not be optimal for {material_type}: {wavelength}"
            else:
                # General validation
                if wavelength_numbers:
                    validation["passed"] = True
                    validation["message"] = f"Laser wavelength specified: {wavelength}"
                else:
                    validation["message"] = "Could not parse laser wavelength"
                    
        except Exception as e:
            validation["message"] = f"Laser parameter validation error: {e}"
            
        results["validations"]["laser_parameters"] = validation

    def _validate_thermal_properties(self, data: Dict, material_name: str, results: Dict):
        """Validate thermal conductivity values are material-specific"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            properties = data.get("properties", {})
            thermal_str = properties.get("thermalConductivity", "")
            
            if not thermal_str:
                validation["message"] = "No thermal conductivity found"
                results["validations"]["thermal_properties"] = validation
                return
            
            # Extract numerical thermal conductivity value
            thermal_match = re.search(r'([\d.]+)', str(thermal_str))
            if not thermal_match:
                validation["message"] = "Could not parse thermal conductivity value"
                results["validations"]["thermal_properties"] = validation
                return
                
            thermal_value = float(thermal_match.group(1))
            validation["details"]["extracted_value"] = thermal_value
            
            # Check against material database
            if material_name in self.material_database:
                expected_range = self.material_database[material_name]["thermal_conductivity_range"]
                min_thermal, max_thermal = expected_range
                
                if min_thermal <= thermal_value <= max_thermal:
                    validation["passed"] = True
                    validation["message"] = f"Thermal conductivity {thermal_value} W/m·K within expected range {expected_range}"
                else:
                    validation["message"] = f"Thermal conductivity {thermal_value} W/m·K outside expected range {expected_range}"
                    results["warnings"].append(f"Thermal conductivity potentially inaccurate for {material_name}")
            else:
                # General range check
                if 0.01 <= thermal_value <= 500:  # Realistic thermal conductivity range
                    validation["passed"] = True
                    validation["message"] = f"Thermal conductivity {thermal_value} W/m·K within realistic range"
                else:
                    validation["message"] = f"Thermal conductivity {thermal_value} W/m·K outside realistic range"
                    
        except Exception as e:
            validation["message"] = f"Thermal properties validation error: {e}"
            
        results["validations"]["thermal_properties"] = validation

    def _check_for_generic_values(self, data: Dict, results: Dict):
        """Check for generic placeholder values that shouldn't be used"""
        
        validation = {"passed": True, "message": "No generic values detected", "details": {}}
        
        # Common generic values to avoid
        generic_values = [
            "7.85",    # Generic steel density
            "1500",    # Generic melting point
            "example", 
            "placeholder",
            "generic",
            "steel density for",
            "typical metal"
        ]
        
        content_str = str(data).lower()
        found_generic = []
        
        for generic in generic_values:
            if generic in content_str:
                found_generic.append(generic)
        
        if found_generic:
            validation["passed"] = False
            validation["message"] = f"Generic values detected: {found_generic}"
            validation["details"]["generic_values"] = found_generic
            results["errors"].append(f"Generic placeholder values found: {found_generic}")
        
        results["validations"]["generic_check"] = validation

    def _validate_applications_specificity(self, data: Dict, results: Dict):
        """Validate that applications are material-specific, not generic"""
        
        validation = {"passed": False, "message": "", "details": {}}
        
        try:
            applications = data.get("applications", [])
            
            if not applications:
                validation["message"] = "No applications found"
                results["validations"]["applications_specificity"] = validation
                return
            
            # Check for specific vs generic applications
            specific_indicators = [
                "semiconductor", "wafer", "precision", "ceramic", "bearing",
                "automotive", "aerospace", "medical", "photoresist", "etch mask"
            ]
            
            generic_indicators = [
                "general cleaning", "standard process", "typical use", 
                "common application", "basic cleaning"
            ]
            
            app_text = str(applications).lower()
            
            specific_found = sum(1 for indicator in specific_indicators if indicator in app_text)
            generic_found = sum(1 for indicator in generic_indicators if indicator in app_text)
            
            validation["details"]["specific_indicators"] = specific_found
            validation["details"]["generic_indicators"] = generic_found
            
            if specific_found > 0 and generic_found == 0:
                validation["passed"] = True
                validation["message"] = f"Applications appear material-specific ({specific_found} indicators)"
            elif generic_found > 0:
                validation["message"] = f"Generic applications detected ({generic_found} indicators)"
                results["warnings"].append("Applications may be too generic")
            else:
                validation["message"] = "Applications lack specific indicators"
                
        except Exception as e:
            validation["message"] = f"Applications validation error: {e}"
            
        results["validations"]["applications_specificity"] = validation

    def validate_directory(self, directory_path: Path) -> List[Dict]:
        """Validate all frontmatter files in a directory"""
        
        results = []
        
        if not directory_path.exists():
            print(f"Error: Directory {directory_path} does not exist")
            return results
        
        # Find all markdown files
        md_files = list(directory_path.glob("*.md"))
        
        if not md_files:
            print(f"No markdown files found in {directory_path}")
            return results
        
        print(f"Validating {len(md_files)} frontmatter files...")
        
        for md_file in md_files:
            print(f"  Validating: {md_file.name}")
            result = self.validate_frontmatter_file(md_file)
            results.append(result)
            
        return results

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a comprehensive validation report"""
        
        if not results:
            return "No files validated."
        
        total_files = len(results)
        successful_files = len([r for r in results if not r["errors"]])
        average_score = statistics.mean([r["score"] for r in results if r["score"] > 0])
        
        report = []
        report.append("="*80)
        report.append("FRONTMATTER TECHNICAL ACCURACY VALIDATION REPORT")
        report.append("="*80)
        report.append(f"Total files validated: {total_files}")
        report.append(f"Successfully processed: {successful_files}")
        report.append(f"Average accuracy score: {average_score:.1f}%")
        report.append("")
        
        # Summary by material
        materials = {}
        for result in results:
            if result["material_name"]:
                materials[result["material_name"]] = result
        
        if materials:
            report.append("MATERIAL-SPECIFIC RESULTS:")
            report.append("-" * 40)
            for material, result in materials.items():
                report.append(f"{material}: {result['score']:.1f}%")
                if result["errors"]:
                    report.append(f"  Errors: {len(result['errors'])}")
                if result["warnings"]:
                    report.append(f"  Warnings: {len(result['warnings'])}")
            report.append("")
        
        # Detailed results
        report.append("DETAILED VALIDATION RESULTS:")
        report.append("-" * 40)
        
        for result in results:
            report.append(f"\nFile: {result['file']}")
            report.append(f"Material: {result['material_name'] or 'Unknown'}")
            report.append(f"Score: {result['score']:.1f}%")
            
            # Validation details
            for check_name, validation in result["validations"].items():
                status = "✅ PASS" if validation["passed"] else "❌ FAIL"
                report.append(f"  {check_name}: {status} - {validation['message']}")
            
            # Errors and warnings
            if result["errors"]:
                report.append("  ERRORS:")
                for error in result["errors"]:
                    report.append(f"    - {error}")
            
            if result["warnings"]:
                report.append("  WARNINGS:")
                for warning in result["warnings"]:
                    report.append(f"    - {warning}")
        
        return "\n".join(report)


def main():
    """Main validation script"""
    
    parser = argparse.ArgumentParser(description="Validate frontmatter technical accuracy")
    parser.add_argument("directory", nargs="?", default="content/components/frontmatter/",
                       help="Directory containing frontmatter files to validate")
    parser.add_argument("--output", "-o", help="Output file for validation report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    directory_path = Path(args.directory)
    validator = TechnicalAccuracyValidator()
    
    # Run validation
    results = validator.validate_directory(directory_path)
    
    if not results:
        print("No files to validate.")
        return
    
    # Generate report
    report = validator.generate_report(results)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Validation report saved to: {args.output}")
    else:
        print(report)
    
    # Exit with error code if any critical issues found
    critical_issues = sum(len(r["errors"]) for r in results)
    if critical_issues > 0:
        print(f"\n⚠️  {critical_issues} critical issues found")
        exit(1)
    else:
        print(f"\n✅ Validation completed successfully")


if __name__ == "__main__":
    main()
