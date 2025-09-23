#!/usr/bin/env python3
"""
Material-Specific Value Accuracy Checker
Analyzes materials.yaml to identify generic/non-specific values and missing fields.
"""

import yaml
import re
from collections import defaultdict
from pathlib import Path


def load_materials():
    """Load materials.yaml data."""
    materials_file = Path('data/materials.yaml')
    with open(materials_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def analyze_field_specificity(data):
    """Analyze field values for material specificity."""
    
    # Track duplicate/generic values across materials
    field_values = defaultdict(lambda: defaultdict(list))
    missing_fields = []
    
    print("🔍 MATERIAL-SPECIFIC VALUE ANALYSIS")
    print("=" * 60)
    
    total_materials = 0
    
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        for material in items:
            total_materials += 1
            material_name = material.get('name', 'Unknown')
            
            # Check for missing fields
            required_fields = [
                'name', 'author_id', 'complexity', 'difficulty_score', 'category',
                'machine_settings', 'applications', 'regulatory_standards', 'compatibility'
            ]
            
            for field in required_fields:
                if field not in material:
                    missing_fields.append(f"{category_name}.{material_name}.{field}")
            
            # Analyze machine_settings specificity
            machine_settings = material.get('machine_settings', {})
            for setting, value in machine_settings.items():
                field_values[f'machine_settings.{setting}'][str(value)].append(f"{category_name}.{material_name}")
            
            # Analyze applications specificity
            applications = material.get('applications', [])
            for app in applications:
                field_values['applications'][app].append(f"{category_name}.{material_name}")
            
            # Note: environmental_impact and outcomes fields have been removed
            # as they contained generic values across all materials
    
    print(f"📊 Analyzed {total_materials} materials across {len(data['materials'])} categories")
    print()
    
    # Report missing fields
    if missing_fields:
        print("❌ MISSING FIELDS:")
        for field in missing_fields:
            print(f"   - {field}")
        print()
    else:
        print("✅ No missing required fields found")
        print()
    
    # Find generic/duplicate values
    print("🔍 GENERIC VALUE ANALYSIS:")
    print("-" * 30)
    
    generic_issues = []
    
    for field_name, value_dict in field_values.items():
        for value, materials_list in value_dict.items():
            if len(materials_list) > 3:  # Value used by more than 3 materials
                generic_issues.append({
                    'field': field_name,
                    'value': value,
                    'materials': materials_list,
                    'count': len(materials_list)
                })
    
    # Sort by most generic (most materials using same value)
    generic_issues.sort(key=lambda x: x['count'], reverse=True)
    
    if generic_issues:
        print(f"Found {len(generic_issues)} potentially generic values:")
        print()
        
        for issue in generic_issues[:20]:  # Show top 20 most generic
            print(f"⚠️  Field: {issue['field']}")
            print(f"   Value: {issue['value']}")
            print(f"   Used by {issue['count']} materials:")
            for material in issue['materials'][:5]:  # Show first 5
                print(f"     - {material}")
            if len(issue['materials']) > 5:
                print(f"     ... and {len(issue['materials']) - 5} more")
            print()
    else:
        print("✅ No overly generic values found")
    
    return generic_issues, missing_fields


def analyze_material_specific_patterns(data):
    """Analyze patterns that should be material-specific."""
    
    print("🎯 MATERIAL-SPECIFIC PATTERN ANALYSIS")
    print("=" * 60)
    
    issues = []
    
    # Check for materials that should have different wavelengths
    wavelength_groups = defaultdict(list)
    
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        for material in items:
            material_name = material.get('name', 'Unknown')
            machine_settings = material.get('machine_settings', {})
            
            wavelength = machine_settings.get('wavelength_optimal', 'unknown')
            wavelength_groups[wavelength].append(f"{category_name}.{material_name}")
    
    print("📡 WAVELENGTH ANALYSIS:")
    print("-" * 25)
    
    for wavelength, materials_list in wavelength_groups.items():
        if len(materials_list) > 10:  # Too many materials with same wavelength
            print(f"⚠️  Wavelength {wavelength} used by {len(materials_list)} materials:")
            for material in materials_list[:8]:
                print(f"     - {material}")
            if len(materials_list) > 8:
                print(f"     ... and {len(materials_list) - 8} more")
            print()
    
    # Check for identical machine settings across different materials
    print("⚙️  MACHINE SETTINGS ANALYSIS:")
    print("-" * 30)
    
    settings_signatures = defaultdict(list)
    
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        for material in items:
            material_name = material.get('name', 'Unknown')
            machine_settings = material.get('machine_settings', {})
            
            # Create signature from key settings
            signature = (
                machine_settings.get('wavelength_optimal'),
                machine_settings.get('power_range'),
                machine_settings.get('fluence_threshold'),
                machine_settings.get('pulse_duration')
            )
            
            settings_signatures[signature].append(f"{category_name}.{material_name}")
    
    identical_settings = 0
    for signature, materials_list in settings_signatures.items():
        if len(materials_list) > 1:
            identical_settings += 1
            print(f"⚠️  Identical settings signature used by {len(materials_list)} materials:")
            print(f"     Wavelength: {signature[0]}, Power: {signature[1]}")
            print(f"     Fluence: {signature[2]}, Pulse: {signature[3]}")
            for material in materials_list:
                print(f"       - {material}")
            print()
    
    if identical_settings == 0:
        print("✅ All materials have unique machine settings")
    
    return issues


def check_technical_accuracy(data):
    """Check technical accuracy of values."""
    
    print("🔬 TECHNICAL ACCURACY ANALYSIS")
    print("=" * 60)
    
    technical_issues = []
    
    # Define material-specific expected ranges
    material_wavelength_expectations = {
        # Metals typically use near-IR lasers
        'Aluminum': ['1064nm', '532nm'],
        'Steel': ['1064nm', '1070nm'],
        'Stainless Steel': ['1064nm', '1070nm'],
        'Copper': ['532nm', '355nm'],  # Copper absorbs green/UV better
        'Brass': ['532nm', '1064nm'],
        'Iron': ['1064nm'],
        'Titanium': ['1064nm', '532nm'],
        
        # Polymers often use UV or CO2
        'Polycarbonate': ['355nm', '266nm', '10600nm'],
        'Acrylic': ['355nm', '266nm', '10600nm'],
        'Polyethylene': ['10600nm', '355nm'],
        'PVC': ['355nm', '266nm'],
        
        # Ceramics
        'Alumina': ['1064nm', '532nm'],
        'Zirconia': ['1064nm', '532nm'],
        
        # Semiconductors
        'Silicon': ['1064nm', '532nm', '355nm'],
        'Gallium Arsenide': ['1064nm', '532nm'],
        
        # Glass typically uses UV
        'Borosilicate Glass': ['355nm', '266nm'],
        'Soda-lime Glass': ['355nm', '266nm'],
    }
    
    print("🎯 WAVELENGTH APPROPRIATENESS:")
    print("-" * 35)
    
    wavelength_issues = 0
    
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        for material in items:
            material_name = material.get('name', 'Unknown')
            machine_settings = material.get('machine_settings', {})
            
            actual_wavelength = machine_settings.get('wavelength_optimal', '')
            expected_wavelengths = material_wavelength_expectations.get(material_name, [])
            
            if expected_wavelengths and actual_wavelength not in expected_wavelengths:
                wavelength_issues += 1
                print(f"⚠️  {category_name}.{material_name}:")
                print(f"     Current: {actual_wavelength}")
                print(f"     Expected: {' or '.join(expected_wavelengths)}")
                print()
    
    if wavelength_issues == 0:
        print("✅ No obvious wavelength mismatches found")
    else:
        print(f"Found {wavelength_issues} potential wavelength issues")
    
    print()
    
    # Check power ranges for material appropriateness
    print("⚡ POWER RANGE ANALYSIS:")
    print("-" * 25)
    
    power_issues = 0
    
    for category_name, category_data in data['materials'].items():
        items = category_data.get('items', [])
        
        for material in items:
            material_name = material.get('name', 'Unknown')
            machine_settings = material.get('machine_settings', {})
            
            power_range = machine_settings.get('power_range', '')
            
            # Extract power values
            power_match = re.search(r'(\d+)-(\d+)W', power_range)
            if power_match:
                min_power = int(power_match.group(1))
                max_power = int(power_match.group(2))
                
                # Check for unrealistic power ranges
                if min_power == max_power:
                    power_issues += 1
                    print(f"⚠️  {category_name}.{material_name}: Single power value {power_range}")
                elif max_power - min_power < 10:
                    power_issues += 1
                    print(f"⚠️  {category_name}.{material_name}: Very narrow power range {power_range}")
    
    if power_issues == 0:
        print("✅ Power ranges appear reasonable")
    else:
        print(f"Found {power_issues} potential power range issues")
    
    return technical_issues


def main():
    """Run comprehensive material specificity analysis."""
    
    data = load_materials()
    
    print("🔍 MATERIALS.YAML ACCURACY & SPECIFICITY ANALYSIS")
    print("=" * 70)
    print("Checking for generic values, missing fields, and technical accuracy")
    print()
    
    # Check field specificity
    generic_issues, missing_fields = analyze_field_specificity(data)
    
    # Check material-specific patterns
    analyze_material_specific_patterns(data)
    
    # Check technical accuracy
    technical_issues = check_technical_accuracy(data)
    
    # Summary
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Missing fields: {len(missing_fields)}")
    print(f"Generic value issues: {len(generic_issues)}")
    print(f"Technical accuracy issues: {len(technical_issues)}")
    
    if missing_fields or generic_issues:
        print("\n❌ Issues found - materials.yaml needs specificity improvements")
        return False
    else:
        print("\n✅ All values appear material-specific and accurate")
        return True


if __name__ == "__main__":
    success = main()
