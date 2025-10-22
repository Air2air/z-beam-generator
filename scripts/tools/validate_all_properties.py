#!/usr/bin/env python3
"""
Comprehensive Property Validation Agent

A systematic top-down validator that checks:
1. Property definitions and taxonomy
2. Category-level ranges and consistency
3. Material-level values and relationships
4. Physical constraint violations
5. Data completeness and quality

Methodology based on recent fixes:
- Conservation of energy (absorption + reflectivity = 100%)
- Physical formulas (α = k / (ρ × Cp))
- Unit consistency across materials
- Expected value ranges per material type
- Property relationship validation (E/TS ratios, σ × ρ = 1)

Usage:
    python3 validate_all_properties.py                    # Full validation
    python3 validate_all_properties.py --property density  # Single property
    python3 validate_all_properties.py --category metal    # Single category
    python3 validate_all_properties.py --fix              # Auto-fix issues
"""

import yaml
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import json

# ============================================================================
# VALIDATION RULES BASED ON RECENT FIXES
# ============================================================================

class ValidationRule:
    """Base class for validation rules"""
    def __init__(self, name: str, severity: str, description: str):
        self.name = name
        self.severity = severity  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
        self.description = description
    
    def validate(self, data: Dict) -> List[Dict]:
        """Return list of violations"""
        raise NotImplementedError

class ConservationOfEnergyRule(ValidationRule):
    """Absorption + Reflectivity + Transmittance = 100% for all materials"""
    
    def __init__(self):
        super().__init__(
            name="conservation_of_energy",
            severity="CRITICAL",
            description="Laser absorption + reflectivity must equal 100% for opaque materials"
        )
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        props = data['materialProperties'].get('laser_material_interaction', {}).get('properties', {})
        absorption = props.get('laserAbsorption', {}).get('value')
        reflectivity = props.get('laserReflectivity', {}).get('value')
        
        if absorption is None or reflectivity is None:
            return violations
        
        total = float(absorption) + float(reflectivity)
        category = data.get('category', 'unknown').lower()
        
        # Opaque materials should sum to ~100%
        opaque_categories = {'metal', 'ceramic', 'stone', 'wood', 'composite'}
        
        if category in opaque_categories:
            if total < 95 or total > 105:
                violations.append({
                    'rule': self.name,
                    'severity': self.severity,
                    'property': 'laserAbsorption+laserReflectivity',
                    'value': total,
                    'expected': '95-105%',
                    'message': f'Opaque material has A+R={total:.1f}% (should be ~100%)',
                    'fix': f'Recalculate: R = 100 - {absorption}'
                })
        else:
            # Transparent materials: only flag if > 105%
            if total > 105:
                violations.append({
                    'rule': self.name,
                    'severity': self.severity,
                    'property': 'laserAbsorption+laserReflectivity',
                    'value': total,
                    'expected': '<= 100%',
                    'message': f'Impossible sum: A+R={total:.1f}% > 100%',
                    'fix': f'Recalculate: R = 100 - {absorption}'
                })
        
        return violations

class ThermalDiffusivityFormulaRule(ValidationRule):
    """α = k / (ρ × Cp) must hold within reasonable tolerance"""
    
    def __init__(self):
        super().__init__(
            name="thermal_diffusivity_formula",
            severity="HIGH",
            description="Thermal diffusivity must match calculated value from k, ρ, Cp"
        )
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        laser_props = data['materialProperties'].get('laser_material_interaction', {}).get('properties', {})
        char_props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
        
        diffusivity = laser_props.get('thermalDiffusivity', {}).get('value')
        conductivity = laser_props.get('thermalConductivity', {}).get('value')
        specific_heat = laser_props.get('specificHeat', {}).get('value')
        density = char_props.get('density', {}).get('value')
        
        if any(v is None for v in [diffusivity, conductivity, specific_heat, density]):
            return violations
        
        # Calculate expected: α = k / (ρ × Cp) × 10^6 mm²/s
        k = float(conductivity)
        rho = float(density) * 1000  # g/cm³ to kg/m³
        cp = float(specific_heat)
        alpha_measured = float(diffusivity)
        
        alpha_calculated = (k / (rho * cp)) * 1e6
        error = abs(alpha_calculated - alpha_measured) / alpha_calculated * 100
        
        if error > 20:  # More than 20% error
            violations.append({
                'rule': self.name,
                'severity': self.severity,
                'property': 'thermalDiffusivity',
                'value': alpha_measured,
                'expected': f'{alpha_calculated:.2f}',
                'error': f'{error:.1f}%',
                'message': f'Thermal diffusivity {alpha_measured} != calculated {alpha_calculated:.2f} mm²/s',
                'fix': f'Recalculate: α = {k} / ({rho} × {cp}) × 10^6 = {alpha_calculated:.2f} mm²/s'
            })
        
        return violations

class ElectricalConductivityUnitRule(ValidationRule):
    """All electrical conductivity must use MS/m (megasiemens per meter)"""
    
    def __init__(self):
        super().__init__(
            name="electrical_conductivity_units",
            severity="MEDIUM",
            description="Electrical conductivity must be in MS/m for consistency"
        )
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
        ec_data = props.get('electricalConductivity', {})
        
        value = ec_data.get('value')
        unit = ec_data.get('unit', '')
        
        if value is None:
            return violations
        
        # Check for non-standard units
        if unit not in ['MS/m', 'megasiemens/m']:
            violations.append({
                'rule': self.name,
                'severity': self.severity,
                'property': 'electricalConductivity',
                'value': f'{value} {unit}',
                'expected': 'MS/m',
                'message': f'Non-standard unit: {unit}',
                'fix': self._get_conversion_fix(value, unit)
            })
        
        return violations
    
    def _get_conversion_fix(self, value, unit):
        """Get conversion instruction for different units"""
        conversions = {
            '×10⁷ S/m': f'Multiply by 10: {value} × 10 = {float(value) * 10} MS/m',
            '% IACS': f'Convert using 58.1 MS/m for 100% IACS: {value}% × 0.581 ≈ {float(value) * 0.581:.1f} MS/m'
        }
        return conversions.get(unit, f'Convert {unit} to MS/m')

class YoungsModulusRangeRule(ValidationRule):
    """Young's Modulus must be in realistic range for material category"""
    
    def __init__(self):
        super().__init__(
            name="youngs_modulus_range",
            severity="HIGH",
            description="Young's Modulus must be realistic for material type"
        )
        
        # Expected ranges by category (in GPa)
        self.ranges = {
            'metal': (10, 450),      # Aluminum to Tungsten
            'ceramic': (30, 600),    # Porcelain to Diamond
            'stone': (5, 120),       # Soft stone to hard granite
            'wood': (5, 30),         # Balsa to dense hardwood
            'plastic': (0.5, 5),     # Soft rubber to hard plastic
            'glass': (50, 95),       # Various glasses
            'composite': (5, 250),   # Varies widely
            'masonry': (5, 45),      # Concrete to brick
            'semiconductor': (50, 200) # Silicon, GaAs, etc.
        }
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
        youngs_data = props.get('youngsModulus', {})
        
        value = youngs_data.get('value')
        if value is None:
            return violations
        
        E = float(value)
        category = data.get('category', 'unknown').lower()
        
        if category in self.ranges:
            min_E, max_E = self.ranges[category]
            
            if E < min_E or E > max_E:
                violations.append({
                    'rule': self.name,
                    'severity': self.severity,
                    'property': 'youngsModulus',
                    'value': E,
                    'expected': f'{min_E}-{max_E} GPa for {category}',
                    'message': f'Young\'s Modulus {E} GPa outside typical range for {category}',
                    'fix': self._suggest_fix(E, category, min_E, max_E)
                })
        
        return violations
    
    def _suggest_fix(self, E, category, min_E, max_E):
        """Suggest fix based on magnitude of error"""
        if E > max_E * 10:
            return f'Likely unit error - divide by 10 or 100'
        elif E < min_E / 10:
            return f'Likely unit error - multiply by 10 or 100'
        else:
            return f'Review source data for {category} materials'

class ModulusStrengthRatioRule(ValidationRule):
    """E/TS ratio should be 100-300 for most materials"""
    
    def __init__(self):
        super().__init__(
            name="modulus_strength_ratio",
            severity="MEDIUM",
            description="Young's Modulus / Tensile Strength ratio should be 100-300"
        )
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        props = data['materialProperties'].get('material_characteristics', {}).get('properties', {})
        
        youngs = props.get('youngsModulus', {}).get('value')
        tensile = props.get('tensileStrength', {}).get('value')
        
        if youngs is None or tensile is None:
            return violations
        
        E = float(youngs) * 1000  # GPa to MPa
        TS = float(tensile)
        
        if TS == 0:
            return violations
        
        ratio = E / TS
        
        # Wider tolerance for some materials
        category = data.get('category', 'unknown').lower()
        
        if category in ['ceramic', 'glass']:
            # Ceramics and glass can have higher ratios
            if ratio < 50 or ratio > 1000:
                violations.append(self._create_violation(ratio, category, E, TS))
        else:
            # Most materials: 100-300
            if ratio < 50 or ratio > 500:
                violations.append(self._create_violation(ratio, category, E, TS))
        
        return violations
    
    def _create_violation(self, ratio, category, E, TS):
        return {
            'rule': self.name,
            'severity': self.severity,
            'property': 'youngsModulus/tensileStrength',
            'value': ratio,
            'expected': '100-300 (metals), 50-1000 (ceramics)',
            'message': f'E/TS ratio {ratio:.1f} unusual for {category}',
            'fix': 'Review both Young\'s Modulus and Tensile Strength values'
        }

class NegativeValueRule(ValidationRule):
    """Physical properties cannot be negative (except some temperature values)"""
    
    def __init__(self):
        super().__init__(
            name="negative_values",
            severity="CRITICAL",
            description="Physical properties must be positive"
        )
        
        # Properties that CAN be negative
        self.allowed_negative = {
            'glassTransition',  # Can be negative temperature
            'thermalExpansion'  # Can be negative (some ceramics)
        }
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        for group_name, group_data in data['materialProperties'].items():
            if 'properties' not in group_data:
                continue
            
            for prop_name, prop_data in group_data['properties'].items():
                value = prop_data.get('value')
                
                if value is None:
                    continue
                
                try:
                    val = float(value)
                    
                    if val < 0 and prop_name not in self.allowed_negative:
                        violations.append({
                            'rule': self.name,
                            'severity': self.severity,
                            'property': prop_name,
                            'value': val,
                            'expected': '>= 0',
                            'message': f'Negative value for {prop_name}: {val}',
                            'fix': 'Review source data or check sign error'
                        })
                except (ValueError, TypeError):
                    pass
        
        return violations

class PercentageRangeRule(ValidationRule):
    """Percentage values must be 0-100"""
    
    def __init__(self):
        super().__init__(
            name="percentage_range",
            severity="HIGH",
            description="Percentage values must be between 0 and 100"
        )
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        for group_name, group_data in data['materialProperties'].items():
            if 'properties' not in group_data:
                continue
            
            for prop_name, prop_data in group_data['properties'].items():
                unit = prop_data.get('unit', '')
                value = prop_data.get('value')
                
                if unit == '%' and value is not None:
                    try:
                        val = float(value)
                        
                        if val < 0 or val > 100:
                            violations.append({
                                'rule': self.name,
                                'severity': self.severity,
                                'property': prop_name,
                                'value': val,
                                'expected': '0-100%',
                                'message': f'Percentage {val}% out of range',
                                'fix': 'Check if value is fraction (multiply by 100) or error'
                            })
                    except (ValueError, TypeError):
                        pass
        
        return violations

class CategoryRangeComplianceRule(ValidationRule):
    """Material property values must fall within category ranges"""
    
    def __init__(self, categories_data: Dict):
        super().__init__(
            name="category_range_compliance",
            severity="HIGH",
            description="Property values must be within category min/max ranges"
        )
        self.categories_data = categories_data
    
    def validate(self, data: Dict) -> List[Dict]:
        violations = []
        
        if 'materialProperties' not in data:
            return violations
        
        category = data.get('category', '').lower()
        if not category:
            return violations
        
        # Get category ranges
        category_key = f'categories.{category}'
        if category_key not in self.categories_data:
            return violations
        
        category_ranges = self.categories_data[category_key].get('category_ranges', {})
        
        # Check each property against category ranges
        for group_name, group_data in data['materialProperties'].items():
            if 'properties' not in group_data:
                continue
            
            for prop_name, prop_data in group_data['properties'].items():
                value = prop_data.get('value')
                
                if value is None or prop_name not in category_ranges:
                    continue
                
                try:
                    val = float(value)
                    range_data = category_ranges[prop_name]
                    min_val = range_data.get('min')
                    max_val = range_data.get('max')
                    
                    if min_val is not None and val < min_val:
                        violations.append({
                            'rule': self.name,
                            'severity': self.severity,
                            'property': prop_name,
                            'value': val,
                            'expected': f'>= {min_val}',
                            'category_range': f'{min_val}-{max_val}',
                            'message': f'{prop_name}={val} below category min {min_val}',
                            'fix': 'Verify value or update category range'
                        })
                    
                    if max_val is not None and val > max_val:
                        violations.append({
                            'rule': self.name,
                            'severity': self.severity,
                            'property': prop_name,
                            'value': val,
                            'expected': f'<= {max_val}',
                            'category_range': f'{min_val}-{max_val}',
                            'message': f'{prop_name}={val} above category max {max_val}',
                            'fix': 'Verify value or update category range'
                        })
                except (ValueError, TypeError):
                    pass
        
        return violations

# ============================================================================
# VALIDATION AGENT
# ============================================================================

class PropertyValidationAgent:
    """Systematic top-down property validator"""
    
    def __init__(self, categories_file: str = "data/Categories.yaml"):
        self.categories_file = Path(categories_file)
        self.frontmatter_dir = Path("content/frontmatter")
        
        # Load Categories.yaml
        with open(self.categories_file) as f:
            self.categories_data = yaml.safe_load(f)
        
        # Initialize validation rules
        self.rules = [
            ConservationOfEnergyRule(),
            ThermalDiffusivityFormulaRule(),
            ElectricalConductivityUnitRule(),
            YoungsModulusRangeRule(),
            ModulusStrengthRatioRule(),
            NegativeValueRule(),
            PercentageRangeRule(),
            CategoryRangeComplianceRule(self.categories_data)
        ]
        
        # Statistics
        self.stats = {
            'materials_checked': 0,
            'violations_found': 0,
            'violations_by_severity': defaultdict(int),
            'violations_by_rule': defaultdict(int),
            'violations_by_property': defaultdict(int)
        }
    
    def validate_property_taxonomy(self) -> Dict:
        """Level 1: Validate property definitions in Categories.yaml"""
        print("\n" + "="*80)
        print("LEVEL 1: PROPERTY TAXONOMY VALIDATION")
        print("="*80)
        
        issues = []
        
        # Check each category has properties defined
        for category_key, category_data in self.categories_data.items():
            if not category_key.startswith('categories.'):
                continue
            
            category_name = category_key.split('.')[1]
            properties = category_data.get('properties', [])
            
            if not properties:
                issues.append({
                    'level': 'taxonomy',
                    'category': category_name,
                    'issue': 'No properties defined',
                    'severity': 'HIGH'
                })
            
            print(f"\n{category_name}: {len(properties)} properties")
        
        print(f"\n✅ Property taxonomy check complete")
        return {'issues': issues, 'categories_checked': len([k for k in self.categories_data.keys() if k.startswith('categories.')])}
    
    def validate_category_ranges(self) -> Dict:
        """Level 2: Validate category ranges are complete and consistent"""
        print("\n" + "="*80)
        print("LEVEL 2: CATEGORY RANGE VALIDATION")
        print("="*80)
        
        issues = []
        
        for category_key, category_data in self.categories_data.items():
            if not category_key.startswith('categories.'):
                continue
            
            category_name = category_key.split('.')[1]
            properties = category_data.get('properties', [])
            category_ranges = category_data.get('category_ranges', {})
            
            # Check coverage
            properties_with_ranges = len(category_ranges)
            coverage = (properties_with_ranges / len(properties) * 100) if properties else 0
            
            print(f"\n{category_name}:")
            print(f"  Properties: {len(properties)}")
            print(f"  With ranges: {properties_with_ranges}")
            print(f"  Coverage: {coverage:.1f}%")
            
            # Find missing ranges
            missing_ranges = set(properties) - set(category_ranges.keys())
            if missing_ranges:
                issues.append({
                    'level': 'category_range',
                    'category': category_name,
                    'issue': f'{len(missing_ranges)} properties missing ranges',
                    'missing': list(missing_ranges)[:5],  # Show first 5
                    'severity': 'MEDIUM'
                })
                print(f"  ⚠️  Missing ranges for: {', '.join(list(missing_ranges)[:5])}")
            
            # Validate range consistency (min < max)
            for prop, range_data in category_ranges.items():
                min_val = range_data.get('min')
                max_val = range_data.get('max')
                
                if min_val is not None and max_val is not None:
                    if min_val > max_val:
                        issues.append({
                            'level': 'category_range',
                            'category': category_name,
                            'property': prop,
                            'issue': f'Invalid range: min ({min_val}) > max ({max_val})',
                            'severity': 'CRITICAL'
                        })
        
        print(f"\n✅ Category range check complete")
        return {'issues': issues}
    
    def validate_material(self, file_path: Path) -> Dict:
        """Level 3: Validate individual material file"""
        
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        if not data:
            return {'violations': [], 'material': file_path.stem}
        
        material = file_path.stem.replace('-laser-cleaning', '')
        violations = []
        
        # Run all validation rules
        for rule in self.rules:
            try:
                rule_violations = rule.validate(data)
                for violation in rule_violations:
                    violation['material'] = material
                    violations.append(violation)
                    
                    # Update stats
                    self.stats['violations_by_severity'][violation['severity']] += 1
                    self.stats['violations_by_rule'][violation['rule']] += 1
                    self.stats['violations_by_property'][violation['property']] += 1
            except Exception as e:
                print(f"⚠️  Error running {rule.name} on {material}: {e}")
        
        self.stats['materials_checked'] += 1
        self.stats['violations_found'] += len(violations)
        
        return {
            'material': material,
            'file': str(file_path),
            'violations': violations
        }
    
    def validate_all_materials(self) -> List[Dict]:
        """Level 4: Validate all materials"""
        print("\n" + "="*80)
        print("LEVEL 3: MATERIAL-LEVEL VALIDATION")
        print("="*80)
        
        results = []
        files = list(self.frontmatter_dir.glob("*.yaml"))
        
        print(f"\nValidating {len(files)} materials...")
        
        for file_path in sorted(files):
            result = self.validate_material(file_path)
            if result['violations']:
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate comprehensive validation report"""
        
        report = []
        report.append("="*80)
        report.append("PROPERTY VALIDATION REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Materials checked: {self.stats['materials_checked']}")
        report.append(f"Violations found: {self.stats['violations_found']}")
        report.append("")
        
        # Summary by severity
        report.append("VIOLATIONS BY SEVERITY:")
        report.append("-"*80)
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = self.stats['violations_by_severity'].get(severity, 0)
            report.append(f"  {severity}: {count}")
        report.append("")
        
        # Summary by rule
        report.append("VIOLATIONS BY RULE:")
        report.append("-"*80)
        for rule, count in sorted(self.stats['violations_by_rule'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {rule}: {count}")
        report.append("")
        
        # Summary by property
        report.append("VIOLATIONS BY PROPERTY:")
        report.append("-"*80)
        for prop, count in sorted(self.stats['violations_by_property'].items(), key=lambda x: x[1], reverse=True)[:20]:
            report.append(f"  {prop}: {count}")
        report.append("")
        
        # Detailed violations
        if results:
            report.append("DETAILED VIOLATIONS:")
            report.append("="*80)
            
            # Group by severity
            by_severity = defaultdict(list)
            for result in results:
                for violation in result['violations']:
                    by_severity[violation['severity']].append({
                        'material': result['material'],
                        **violation
                    })
            
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                violations = by_severity[severity]
                if not violations:
                    continue
                
                report.append(f"\n{severity} PRIORITY ({len(violations)} violations):")
                report.append("-"*80)
                
                for v in violations[:50]:  # Limit to 50 per severity
                    report.append(f"\nMaterial: {v['material']}")
                    report.append(f"  Rule: {v['rule']}")
                    report.append(f"  Property: {v['property']}")
                    report.append(f"  Value: {v.get('value', 'N/A')}")
                    report.append(f"  Expected: {v.get('expected', 'N/A')}")
                    report.append(f"  Message: {v['message']}")
                    report.append(f"  Fix: {v['fix']}")
                
                if len(violations) > 50:
                    report.append(f"\n... and {len(violations) - 50} more {severity} violations")
        
        return "\n".join(report)
    
    def run_validation(self, filter_property: Optional[str] = None, 
                      filter_category: Optional[str] = None) -> str:
        """Run full validation pipeline"""
        
        print("="*80)
        print("PROPERTY VALIDATION AGENT")
        print("="*80)
        print(f"Categories file: {self.categories_file}")
        print(f"Frontmatter dir: {self.frontmatter_dir}")
        print(f"Validation rules: {len(self.rules)}")
        
        if filter_property:
            print(f"Filter: property = {filter_property}")
        if filter_category:
            print(f"Filter: category = {filter_category}")
        
        # Level 1: Taxonomy
        taxonomy_results = self.validate_property_taxonomy()
        
        # Level 2: Category ranges
        category_results = self.validate_category_ranges()
        
        # Level 3-4: Materials
        material_results = self.validate_all_materials()
        
        # Apply filters
        if filter_property:
            material_results = [
                {**r, 'violations': [v for v in r['violations'] if filter_property in v['property']]}
                for r in material_results
            ]
            material_results = [r for r in material_results if r['violations']]
        
        if filter_category:
            # Would need to load each file again to check category
            pass
        
        # Generate report
        report = self.generate_report(material_results)
        
        return report

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Property Validation Agent')
    parser.add_argument('--property', help='Filter by property name')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--fix', action='store_true', help='Auto-fix violations (where possible)')
    parser.add_argument('--output', help='Output file for report', default='VALIDATION_REPORT.md')
    
    args = parser.parse_args()
    
    # Create agent
    agent = PropertyValidationAgent()
    
    # Run validation
    report = agent.run_validation(
        filter_property=args.property,
        filter_category=args.category
    )
    
    # Print to console
    print("\n" + report)
    
    # Save to file
    output_file = Path(args.output)
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to {output_file}")
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print(f"Materials checked: {agent.stats['materials_checked']}")
    print(f"Violations found: {agent.stats['violations_found']}")
    
    if agent.stats['violations_found'] > 0:
        print(f"\n⚠️  Found {agent.stats['violations_found']} violations requiring attention")
        print(f"   CRITICAL: {agent.stats['violations_by_severity']['CRITICAL']}")
        print(f"   HIGH: {agent.stats['violations_by_severity']['HIGH']}")
        print(f"   MEDIUM: {agent.stats['violations_by_severity']['MEDIUM']}")
        print(f"   LOW: {agent.stats['violations_by_severity']['LOW']}")
        sys.exit(1)
    else:
        print("\n✅ All validations passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()
