#!/usr/bin/env python3
"""
Comprehensive Materials.yaml Validation Framework

This script systematically validates every field, value, and relationship
in the materials.yaml file against known standards and scientific data.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
import requests
import json

class MaterialsValidator:
    def __init__(self, materials_path: str = "data/materials.yaml"):
        self.materials_path = materials_path
        self.data = self._load_materials()
        self.validation_results = {
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'statistics': {}
        }
        
        # Reference data for validation
        self.known_chemical_symbols = self._load_periodic_table()
        self.standard_complexity_levels = ['low', 'medium', 'high']
        self.standard_difficulty_range = (1, 5)
        self.laser_wavelengths = [355, 532, 1064, 1550, 10600]  # Common nm values
        
    def _load_materials(self) -> Dict:
        """Load materials.yaml file."""
        try:
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load {self.materials_path}: {e}")
    
    def _load_periodic_table(self) -> Dict[str, Dict]:
        """Load periodic table data for chemical validation."""
        # Basic periodic table for validation
        return {
            'H': {'name': 'Hydrogen', 'atomic_number': 1},
            'He': {'name': 'Helium', 'atomic_number': 2},
            'Li': {'name': 'Lithium', 'atomic_number': 3},
            'Be': {'name': 'Beryllium', 'atomic_number': 4},
            'B': {'name': 'Boron', 'atomic_number': 5},
            'C': {'name': 'Carbon', 'atomic_number': 6},
            'N': {'name': 'Nitrogen', 'atomic_number': 7},
            'O': {'name': 'Oxygen', 'atomic_number': 8},
            'F': {'name': 'Fluorine', 'atomic_number': 9},
            'Ne': {'name': 'Neon', 'atomic_number': 10},
            'Na': {'name': 'Sodium', 'atomic_number': 11},
            'Mg': {'name': 'Magnesium', 'atomic_number': 12},
            'Al': {'name': 'Aluminum', 'atomic_number': 13},
            'Si': {'name': 'Silicon', 'atomic_number': 14},
            'P': {'name': 'Phosphorus', 'atomic_number': 15},
            'S': {'name': 'Sulfur', 'atomic_number': 16},
            'Cl': {'name': 'Chlorine', 'atomic_number': 17},
            'Ar': {'name': 'Argon', 'atomic_number': 18},
            'K': {'name': 'Potassium', 'atomic_number': 19},
            'Ca': {'name': 'Calcium', 'atomic_number': 20},
            'Sc': {'name': 'Scandium', 'atomic_number': 21},
            'Ti': {'name': 'Titanium', 'atomic_number': 22},
            'V': {'name': 'Vanadium', 'atomic_number': 23},
            'Cr': {'name': 'Chromium', 'atomic_number': 24},
            'Mn': {'name': 'Manganese', 'atomic_number': 25},
            'Fe': {'name': 'Iron', 'atomic_number': 26},
            'Co': {'name': 'Cobalt', 'atomic_number': 27},
            'Ni': {'name': 'Nickel', 'atomic_number': 28},
            'Cu': {'name': 'Copper', 'atomic_number': 29},
            'Zn': {'name': 'Zinc', 'atomic_number': 30},
            'Ga': {'name': 'Gallium', 'atomic_number': 31},
            'Ge': {'name': 'Germanium', 'atomic_number': 32},
            'As': {'name': 'Arsenic', 'atomic_number': 33},
            'Se': {'name': 'Selenium', 'atomic_number': 34},
            'Br': {'name': 'Bromine', 'atomic_number': 35},
            'Kr': {'name': 'Krypton', 'atomic_number': 36},
            'Rb': {'name': 'Rubidium', 'atomic_number': 37},
            'Sr': {'name': 'Strontium', 'atomic_number': 38},
            'Y': {'name': 'Yttrium', 'atomic_number': 39},
            'Zr': {'name': 'Zirconium', 'atomic_number': 40},
            'Nb': {'name': 'Niobium', 'atomic_number': 41},
            'Mo': {'name': 'Molybdenum', 'atomic_number': 42},
            'Tc': {'name': 'Technetium', 'atomic_number': 43},
            'Ru': {'name': 'Ruthenium', 'atomic_number': 44},
            'Rh': {'name': 'Rhodium', 'atomic_number': 45},
            'Pd': {'name': 'Palladium', 'atomic_number': 46},
            'Ag': {'name': 'Silver', 'atomic_number': 47},
            'Cd': {'name': 'Cadmium', 'atomic_number': 48},
            'In': {'name': 'Indium', 'atomic_number': 49},
            'Sn': {'name': 'Tin', 'atomic_number': 50},
            'Sb': {'name': 'Antimony', 'atomic_number': 51},
            'Te': {'name': 'Tellurium', 'atomic_number': 52},
            'I': {'name': 'Iodine', 'atomic_number': 53},
            'Xe': {'name': 'Xenon', 'atomic_number': 54},
            'Cs': {'name': 'Cesium', 'atomic_number': 55},
            'Ba': {'name': 'Barium', 'atomic_number': 56},
            'La': {'name': 'Lanthanum', 'atomic_number': 57},
            'Ce': {'name': 'Cerium', 'atomic_number': 58},
            'Pr': {'name': 'Praseodymium', 'atomic_number': 59},
            'Nd': {'name': 'Neodymium', 'atomic_number': 60},
            'Pm': {'name': 'Promethium', 'atomic_number': 61},
            'Sm': {'name': 'Samarium', 'atomic_number': 62},
            'Eu': {'name': 'Europium', 'atomic_number': 63},
            'Gd': {'name': 'Gadolinium', 'atomic_number': 64},
            'Tb': {'name': 'Terbium', 'atomic_number': 65},
            'Dy': {'name': 'Dysprosium', 'atomic_number': 66},
            'Ho': {'name': 'Holmium', 'atomic_number': 67},
            'Er': {'name': 'Erbium', 'atomic_number': 68},
            'Tm': {'name': 'Thulium', 'atomic_number': 69},
            'Yb': {'name': 'Ytterbium', 'atomic_number': 70},
            'Lu': {'name': 'Lutetium', 'atomic_number': 71},
            'Hf': {'name': 'Hafnium', 'atomic_number': 72},
            'Ta': {'name': 'Tantalum', 'atomic_number': 73},
            'W': {'name': 'Tungsten', 'atomic_number': 74},
            'Re': {'name': 'Rhenium', 'atomic_number': 75},
            'Os': {'name': 'Osmium', 'atomic_number': 76},
            'Ir': {'name': 'Iridium', 'atomic_number': 77},
            'Pt': {'name': 'Platinum', 'atomic_number': 78},
            'Au': {'name': 'Gold', 'atomic_number': 79},
            'Hg': {'name': 'Mercury', 'atomic_number': 80},
            'Tl': {'name': 'Thallium', 'atomic_number': 81},
            'Pb': {'name': 'Lead', 'atomic_number': 82},
            'Bi': {'name': 'Bismuth', 'atomic_number': 83},
            'Po': {'name': 'Polonium', 'atomic_number': 84},
            'At': {'name': 'Astatine', 'atomic_number': 85},
            'Rn': {'name': 'Radon', 'atomic_number': 86},
            'Fr': {'name': 'Francium', 'atomic_number': 87},
            'Ra': {'name': 'Radium', 'atomic_number': 88},
            'Ac': {'name': 'Actinium', 'atomic_number': 89},
            'Th': {'name': 'Thorium', 'atomic_number': 90},
            'Pa': {'name': 'Protactinium', 'atomic_number': 91},
            'U': {'name': 'Uranium', 'atomic_number': 92}
        }
    
    def validate_structure(self) -> None:
        """Validate overall YAML structure."""
        required_sections = ['material_index', 'materials', 'parameter_templates']
        
        for section in required_sections:
            if section not in self.data:
                self.validation_results['errors'].append(
                    f"Missing required section: {section}"
                )
        
        # Validate material_index consistency
        if 'material_index' in self.data and 'materials' in self.data:
            self._validate_index_consistency()
    
    def _validate_index_consistency(self) -> None:
        """Ensure material_index matches materials items."""
        index = self.data['material_index']
        materials = self.data['materials']
        
        for name, index_info in index.items():
            category = index_info['category']
            item_index = index_info['index']
            
            if category not in materials:
                self.validation_results['errors'].append(
                    f"Material '{name}' references non-existent category '{category}'"
                )
                continue
            
            items = materials[category].get('items', [])
            if item_index >= len(items):
                self.validation_results['errors'].append(
                    f"Material '{name}' index {item_index} out of range for category '{category}'"
                )
                continue
            
            actual_item = items[item_index]
            if actual_item.get('name') != name:
                self.validation_results['errors'].append(
                    f"Index mismatch: '{name}' points to '{actual_item.get('name')}'"
                )
    
    def validate_chemical_formulas(self) -> None:
        """Validate chemical formulas and symbols."""
        for category, cat_data in self.data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                name = item.get('name', 'Unknown')
                
                # Validate symbol field
                if 'symbol' in item:
                    symbol = item['symbol']
                    self._validate_chemical_symbol(name, symbol)
                
                # Validate formula field
                if 'formula' in item:
                    formula = item['formula']
                    self._validate_chemical_formula(name, formula)
                
                # Check consistency between symbol and formula for pure elements
                if 'symbol' in item and 'formula' in item:
                    self._validate_symbol_formula_consistency(name, item['symbol'], item['formula'])
    
    def _validate_chemical_symbol(self, material_name: str, symbol: str) -> None:
        """Validate a chemical symbol."""
        # Check for pure elements
        if symbol in self.known_chemical_symbols:
            return  # Valid element symbol
        
        # Check for common alloy abbreviations
        alloy_symbols = {
            'SS': 'Stainless Steel',
            'CS': 'Carbon Steel',
            'HSS': 'High Speed Steel',
            'Al': 'Aluminum',  # Sometimes used as symbol and formula
        }
        
        if symbol in alloy_symbols:
            return  # Valid alloy symbol
        
        # Pattern validation for complex symbols
        if re.match(r'^[A-Z][a-z]?(-[A-Z][a-z]?)*$', symbol):
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Unrecognized symbol '{symbol}' - verify against standards"
            )
        else:
            self.validation_results['errors'].append(
                f"Material '{material_name}': Invalid symbol format '{symbol}'"
            )
    
    def _validate_chemical_formula(self, material_name: str, formula: str) -> None:
        """Validate a chemical formula."""
        # Simple element formulas
        if formula in self.known_chemical_symbols:
            return  # Valid element
        
        # Complex formula patterns
        complex_patterns = [
            r'^[A-Z][a-z]?(\d+)?([A-Z][a-z]?(\d+)?)*$',  # Standard chemical formula
            r'^[A-Z][a-z]?(-[A-Z][a-z]?)*(-[A-Z][a-z]?)*$',  # Alloy notation (Fe-Cr-Ni)
            r'^[A-Z][a-z]?\d*[A-Z][a-z]?\d*$',  # Binary compounds
        ]
        
        valid_formula = any(re.match(pattern, formula) for pattern in complex_patterns)
        
        if not valid_formula:
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Formula '{formula}' has unusual format - verify correctness"
            )
    
    def _validate_symbol_formula_consistency(self, material_name: str, symbol: str, formula: str) -> None:
        """Check if symbol and formula are consistent for pure elements."""
        if symbol == formula and symbol in self.known_chemical_symbols:
            return  # Perfect consistency for pure element
        
        if symbol != formula:
            # For alloys and compounds, this is expected
            if '-' in formula or len(formula) > 3:
                return  # Likely an alloy or compound
            
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Symbol '{symbol}' and formula '{formula}' differ - verify if intentional"
            )
    
    def validate_laser_parameters(self) -> None:
        """Validate laser parameters for technical accuracy."""
        for category, cat_data in self.data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                name = item.get('name', 'Unknown')
                
                if 'laser_parameters' in item:
                    params = item['laser_parameters']
                    self._validate_laser_param_set(name, params)
    
    def _validate_laser_param_set(self, material_name: str, params: Dict) -> None:
        """Validate a set of laser parameters."""
        required_params = [
            'fluence_threshold', 'pulse_duration', 'wavelength_optimal',
            'power_range', 'repetition_rate', 'spot_size'
        ]
        
        for param in required_params:
            if param not in params:
                self.validation_results['warnings'].append(
                    f"Material '{material_name}': Missing laser parameter '{param}'"
                )
        
        # Validate specific parameter formats and ranges
        if 'wavelength_optimal' in params:
            self._validate_wavelength(material_name, params['wavelength_optimal'])
        
        if 'power_range' in params:
            self._validate_power_range(material_name, params['power_range'])
        
        if 'fluence_threshold' in params:
            self._validate_fluence_threshold(material_name, params['fluence_threshold'])
    
    def _validate_wavelength(self, material_name: str, wavelength: str) -> None:
        """Validate laser wavelength values."""
        # Extract numeric value
        match = re.search(r'(\d+)', wavelength)
        if not match:
            self.validation_results['errors'].append(
                f"Material '{material_name}': Invalid wavelength format '{wavelength}'"
            )
            return
        
        value = int(match.group(1))
        if value not in self.laser_wavelengths:
            self.validation_results['suggestions'].append(
                f"Material '{material_name}': Wavelength {value}nm is uncommon. Standard wavelengths: {self.laser_wavelengths}"
            )
    
    def _validate_power_range(self, material_name: str, power_range: str) -> None:
        """Validate power range format and values."""
        # Pattern: "20-100W" or "50W"
        pattern = r'(\d+)-(\d+)W|(\d+)W'
        match = re.match(pattern, power_range)
        
        if not match:
            self.validation_results['errors'].append(
                f"Material '{material_name}': Invalid power range format '{power_range}'"
            )
            return
        
        if match.group(1) and match.group(2):  # Range format
            min_power = int(match.group(1))
            max_power = int(match.group(2))
            
            if min_power >= max_power:
                self.validation_results['errors'].append(
                    f"Material '{material_name}': Invalid power range '{power_range}' - min >= max"
                )
            
            if max_power > 10000:  # 10kW is very high for cleaning
                self.validation_results['warnings'].append(
                    f"Material '{material_name}': Very high power range '{power_range}' - verify if realistic"
                )
    
    def _validate_fluence_threshold(self, material_name: str, fluence: str) -> None:
        """Validate fluence threshold format and values."""
        # Pattern: "0.5–5 J/cm²" or "1.0-10 J/cm²"
        pattern = r'([\d.]+)[–-]([\d.]+)\s*J/cm²'
        match = re.match(pattern, fluence)
        
        if not match:
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Unusual fluence format '{fluence}' - verify units"
            )
            return
        
        min_fluence = float(match.group(1))
        max_fluence = float(match.group(2))
        
        if min_fluence >= max_fluence:
            self.validation_results['errors'].append(
                f"Material '{material_name}': Invalid fluence range '{fluence}' - min >= max"
            )
        
        if max_fluence > 100:  # Very high fluence
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Very high fluence '{fluence}' - verify if realistic for cleaning"
            )
    
    def validate_difficulty_scores(self) -> None:
        """Validate difficulty scores and complexity levels."""
        for category, cat_data in self.data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                name = item.get('name', 'Unknown')
                
                # Validate difficulty score
                if 'difficulty_score' in item:
                    score = item['difficulty_score']
                    if not isinstance(score, int) or not (self.standard_difficulty_range[0] <= score <= self.standard_difficulty_range[1]):
                        self.validation_results['errors'].append(
                            f"Material '{name}': Difficulty score {score} outside valid range {self.standard_difficulty_range}"
                        )
                
                # Validate complexity level
                if 'complexity' in item:
                    complexity = item['complexity']
                    if complexity not in self.standard_complexity_levels:
                        self.validation_results['errors'].append(
                            f"Material '{name}': Invalid complexity '{complexity}'. Valid: {self.standard_complexity_levels}"
                        )
                
                # Check consistency between difficulty and complexity
                if 'difficulty_score' in item and 'complexity' in item:
                    self._validate_difficulty_complexity_consistency(name, item['difficulty_score'], item['complexity'])
    
    def _validate_difficulty_complexity_consistency(self, name: str, score: int, complexity: str) -> None:
        """Check if difficulty score matches complexity level."""
        expected_mappings = {
            'low': [1, 2],
            'medium': [2, 3, 4],
            'high': [4, 5]
        }
        
        if complexity in expected_mappings:
            if score not in expected_mappings[complexity]:
                self.validation_results['warnings'].append(
                    f"Material '{name}': Difficulty score {score} may not match complexity '{complexity}'"
                )
    
    def validate_author_ids(self) -> None:
        """Validate author ID assignments."""
        author_ids = set()
        
        for category, cat_data in self.data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                name = item.get('name', 'Unknown')
                
                if 'author_id' in item:
                    author_id = item['author_id']
                    author_ids.add(author_id)
                    
                    if not isinstance(author_id, int) or author_id < 1 or author_id > 10:
                        self.validation_results['warnings'].append(
                            f"Material '{name}': Unusual author_id {author_id} - verify if valid"
                        )
        
        self.validation_results['statistics']['unique_authors'] = len(author_ids)
        self.validation_results['statistics']['author_ids_used'] = sorted(list(author_ids))
    
    def validate_applications(self) -> None:
        """Validate application descriptions for consistency and completeness."""
        for category, cat_data in self.data.get('materials', {}).items():
            for item in cat_data.get('items', []):
                name = item.get('name', 'Unknown')
                
                if 'applications' in item:
                    applications = item['applications']
                    
                    if not isinstance(applications, list):
                        self.validation_results['errors'].append(
                            f"Material '{name}': Applications should be a list, got {type(applications)}"
                        )
                        continue
                    
                    if len(applications) < 2:
                        self.validation_results['suggestions'].append(
                            f"Material '{name}': Only {len(applications)} application(s) listed - consider adding more"
                        )
                    
                    for app in applications:
                        self._validate_application_format(name, app)
    
    def _validate_application_format(self, material_name: str, application: str) -> None:
        """Validate individual application format."""
        # Expected format: "Industry: Description"
        if ':' not in application:
            self.validation_results['warnings'].append(
                f"Material '{material_name}': Application '{application}' missing industry prefix"
            )
            return
        
        industry, description = application.split(':', 1)
        industry = industry.strip()
        description = description.strip()
        
        if len(description) < 20:
            self.validation_results['suggestions'].append(
                f"Material '{material_name}': Application description very short: '{description}'"
            )
        
        # Check for common industries
        common_industries = [
            'Automotive', 'Aerospace', 'Electronics', 'Medical', 'Manufacturing',
            'Construction', 'Marine', 'Energy', 'Jewelry', 'Art Restoration'
        ]
        
        if industry not in common_industries:
            self.validation_results['suggestions'].append(
                f"Material '{material_name}': Uncommon industry '{industry}' - verify spelling"
            )
    
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report."""
        # Run all validations
        self.validate_structure()
        self.validate_chemical_formulas()
        self.validate_laser_parameters()
        self.validate_difficulty_scores()
        self.validate_author_ids()
        self.validate_applications()
        
        # Add summary statistics
        self.validation_results['statistics'].update({
            'total_materials': len(self.data.get('material_index', {})),
            'total_errors': len(self.validation_results['errors']),
            'total_warnings': len(self.validation_results['warnings']),
            'total_suggestions': len(self.validation_results['suggestions'])
        })
        
        return self.validation_results
    
    def save_report(self, output_path: str = "materials_validation_report.json") -> None:
        """Save validation report to file."""
        report = self.generate_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Validation report saved to: {output_path}")


def main():
    """Run materials validation."""
    print("🔍 Starting comprehensive materials.yaml validation...")
    
    validator = MaterialsValidator()
    report = validator.generate_report()
    
    # Print summary
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"  Total Materials: {report['statistics']['total_materials']}")
    print(f"  ❌ Errors: {report['statistics']['total_errors']}")
    print(f"  ⚠️  Warnings: {report['statistics']['total_warnings']}")
    print(f"  💡 Suggestions: {report['statistics']['total_suggestions']}")
    
    # Show first few issues of each type
    if report['errors']:
        print(f"\n❌ CRITICAL ERRORS (showing first 5):")
        for error in report['errors'][:5]:
            print(f"  • {error}")
    
    if report['warnings']:
        print(f"\n⚠️  WARNINGS (showing first 5):")
        for warning in report['warnings'][:5]:
            print(f"  • {warning}")
    
    if report['suggestions']:
        print(f"\n💡 SUGGESTIONS (showing first 5):")
        for suggestion in report['suggestions'][:5]:
            print(f"  • {suggestion}")
    
    # Save detailed report
    validator.save_report("scripts/validation/materials_validation_report.json")
    
    print(f"\n✅ Validation complete. See full report in materials_validation_report.json")


if __name__ == "__main__":
    main()
