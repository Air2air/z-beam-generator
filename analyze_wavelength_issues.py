#!/usr/bin/env python3
"""
Wavelength Data Issues Analysis

This script analyzes machineSettings.wavelength data issues to identify
specific problems with wavelength configuration and validation.
"""

import yaml
import glob
from collections import defaultdict, Counter

def analyze_wavelength_issues():
    """Analyze wavelength data issues in frontmatter files."""
    
    print("🔍 Comprehensive Wavelength Data Issues Analysis")
    print("=" * 70)
    
    # Load system configuration
    with open('data/Categories.yaml', 'r') as f:
        categories_data = yaml.safe_load(f)
    
    with open('data/Materials.yaml', 'r') as f:
        materials_data = yaml.safe_load(f)
    
    machine_settings_ranges = materials_data.get('machineSettingsRanges', {})
    machine_descriptions = categories_data.get('machineSettingsDescriptions', {})
    
    # System-level issues
    print("🏗️ SYSTEM CONFIGURATION ISSUES:")
    wavelength_in_ranges = 'wavelength' in machine_settings_ranges
    wavelength_in_descriptions = 'wavelength' in machine_descriptions
    
    if wavelength_in_ranges:
        print(f"   ✅ wavelength FOUND in machineSettingsRanges")
    else:
        print(f"   ❌ wavelength NOT defined in machineSettingsRanges")
        
    if wavelength_in_descriptions:
        print(f"   ✅ wavelength FOUND in machineSettingsDescriptions")
    else:
        print(f"   ❌ wavelength NOT defined in machineSettingsDescriptions")
        
    print(f"   📋 Available ranges: {list(machine_settings_ranges.keys())}")
    print(f"   📋 Available descriptions: {list(machine_descriptions.keys())}")
    print()
    
    # Data analysis
    wavelength_values = []
    min_values = []
    max_values = []
    units = []
    value_range_issues = []
    null_range_files = []
    inconsistent_range_files = []
    
    files_processed = 0
    files_with_wavelength = 0
    
    # Process all frontmatter files
    for file_path in sorted(glob.glob('content/components/frontmatter/*.yaml')):
        files_processed += 1
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            machine_settings = data.get('machineSettings', {})
            if 'wavelength' not in machine_settings:
                continue
                
            files_with_wavelength += 1
            material_name = file_path.split('/')[-1].replace('-laser-cleaning.yaml', '')
            wavelength_data = machine_settings['wavelength']
            
            # Extract values
            value = wavelength_data.get('value')
            min_val = wavelength_data.get('min')
            max_val = wavelength_data.get('max')
            unit = wavelength_data.get('unit')
            
            # Collect data for analysis
            if value is not None:
                wavelength_values.append(value)
            if min_val is not None:
                min_values.append(min_val)
            if max_val is not None:
                max_values.append(max_val)
            if unit:
                units.append(unit)
            
            # Identify specific issues
            if min_val is None and max_val is None:
                null_range_files.append(material_name)
            
            elif min_val is not None and max_val is not None:
                if min_val != max_val:
                    if value == min_val or value == max_val:
                        issue_type = "value equals boundary"
                        value_range_issues.append({
                            'material': material_name,
                            'value': value,
                            'min': min_val,
                            'max': max_val,
                            'issue': issue_type
                        })
                    elif value < min_val or value > max_val:
                        issue_type = "value outside range"
                        value_range_issues.append({
                            'material': material_name,
                            'value': value,
                            'min': min_val,
                            'max': max_val,
                            'issue': issue_type
                        })
                        
            elif (min_val is None) != (max_val is None):
                inconsistent_range_files.append({
                    'material': material_name,
                    'min': min_val,
                    'max': max_val
                })
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    # Statistics
    print("📊 DATA STATISTICS:")
    print(f"   📁 Total frontmatter files: {files_processed}")
    print(f"   📄 Files with wavelength: {files_with_wavelength}")
    print(f"   🎯 Wavelength coverage: {files_with_wavelength/files_processed*100:.1f}%")
    print()
    
    # Value analysis
    print("📈 WAVELENGTH VALUES ANALYSIS:")
    if wavelength_values:
        value_counts = Counter(wavelength_values)
        print(f"   📊 Unique values: {len(value_counts)}")
        print(f"   📊 Most common values:")
        for value, count in value_counts.most_common(5):
            print(f"      {value} nm: {count} files ({count/files_with_wavelength*100:.1f}%)")
        print(f"   📊 Range: {min(wavelength_values)} - {max(wavelength_values)} nm")
    print()
    
    # Unit analysis
    print("📏 UNIT ANALYSIS:")
    if units:
        unit_counts = Counter(units)
        print(f"   📊 Unit distribution:")
        for unit, count in unit_counts.items():
            print(f"      {unit}: {count} files ({count/files_with_wavelength*100:.1f}%)")
    print()
    
    # Range analysis
    print("📐 RANGE ANALYSIS:")
    print(f"   ❌ Files with null ranges (min=null, max=null): {len(null_range_files)}")
    if null_range_files:
        print(f"      Examples: {', '.join(null_range_files[:5])}" + 
              (f" (+{len(null_range_files)-5} more)" if len(null_range_files) > 5 else ""))
    
    print(f"   ⚠️  Files with inconsistent null ranges: {len(inconsistent_range_files)}")
    if inconsistent_range_files:
        for item in inconsistent_range_files[:3]:
            print(f"      {item['material']}: min={item['min']}, max={item['max']}")
    
    print(f"   🎯 Files with value/range issues: {len(value_range_issues)}")
    if value_range_issues:
        for item in value_range_issues[:5]:
            print(f"      {item['material']}: value={item['value']}, range=[{item['min']}-{item['max']}] ({item['issue']})")
    print()
    
    # Min/Max range analysis
    if min_values and max_values:
        print("📊 RANGE BOUNDARIES ANALYSIS:")
        min_counts = Counter(min_values)
        max_counts = Counter(max_values)
        
        print(f"   📉 Min values distribution:")
        for val, count in min_counts.most_common(3):
            print(f"      {val} nm: {count} files")
            
        print(f"   📈 Max values distribution:")
        for val, count in max_counts.most_common(3):
            print(f"      {val} nm: {count} files")
        print()
    
    # Critical issues summary
    print("🚨 CRITICAL ISSUES SUMMARY:")
    issue_count = 1
    
    if not wavelength_in_ranges:
        print(f"   {issue_count}. ❌ NO VALIDATION: wavelength not in machineSettingsRanges")
        print(f"      📊 Impact: All {files_with_wavelength} files cannot be validated")
        issue_count += 1
    else:
        print(f"   ✅ FIXED: wavelength validation now available in machineSettingsRanges")
        
    if not wavelength_in_descriptions:
        print(f"   {issue_count}. ❌ NO DESCRIPTION: wavelength not in machineSettingsDescriptions")  
        print(f"      📊 Impact: No standardized guidance for wavelength selection")
        issue_count += 1
    else:
        print(f"   ✅ FIXED: wavelength descriptions now available in machineSettingsDescriptions")
        
    if value_range_issues:
        print(f"   {issue_count}. ⚠️  INCONSISTENT RANGES: {len(value_range_issues)} files with value/range issues")
        issue_count += 1
        
    if null_range_files:
        print(f"   {issue_count}. ⚠️  NULL RANGES: {len(null_range_files)} files with no range validation")
        issue_count += 1
        
    if inconsistent_range_files:
        print(f"   {issue_count}. ⚠️  MIXED NULL RANGES: {len(inconsistent_range_files)} files with inconsistent nulls")
    print()
    
    # Recommendations
    print("💡 RECOMMENDED FIXES:")
    print("   1. 🔧 Add wavelength to machineSettingsRanges in Materials.yaml")
    print("      Example:")
    print("      wavelength:")
    print("        min: 355")
    print("        max: 10600") 
    print("        unit: nm")
    print("        description: Laser wavelength range for industrial cleaning")
    print("        research_basis: Common industrial lasers (UV 355nm to CO2 10.6μm)")
    print()
    print("   2. 📝 Add wavelength to machineSettingsDescriptions in Categories.yaml")
    print("      Example:")
    print("      wavelength:")
    print("        description: Laser wavelength for optimal material interaction")
    print("        unit: nm")
    print("        selection_criteria: Material absorption characteristics and cleaning requirements")
    print("        typical_range_guidance: 355nm (UV) for organics, 1064nm (NIR) for metals")
    print()
    print("   3. 🎯 Standardize existing wavelength ranges based on material categories")
    print("   4. ✅ Re-run validation after fixes to confirm resolution")

if __name__ == "__main__":
    analyze_wavelength_issues()