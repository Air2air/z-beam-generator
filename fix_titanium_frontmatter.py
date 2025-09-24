#!/usr/bin/env python3
"""
Fix Titanium Frontmatter Issues

Issues to fix:
1. Missing category ranges - properties should include Min/Max/Unit from metal category ranges
2. Unorganized machineSettings - should use proper field ordering structure

This script demonstrates the fixes and regenerates the titanium frontmatter correctly.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.materials import get_material_by_name
from components.frontmatter.generator import FrontmatterComponentGenerator
import re


def analyze_current_issues():
    """Analyze the current titanium frontmatter to identify specific issues"""
    print("=== ANALYZING CURRENT TITANIUM FRONTMATTER ISSUES ===")
    
    # Read current file
    try:
        with open('content/components/frontmatter/titanium-laser-cleaning.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Titanium frontmatter file not found")
        return
    
    # Check for category ranges (should have Min/Max/Unit fields for properties)
    properties_section = re.search(r'technicalProperties:(.*?)(?=\w+:|$)', content, re.DOTALL)
    if properties_section:
        props_content = properties_section.group(1)
        min_fields = re.findall(r'(\w+Min):', props_content)
        max_fields = re.findall(r'(\w+Max):', props_content)
        unit_fields = re.findall(r'(\w+Unit):', props_content)
        
        print(f"🔍 Current properties section: technicalProperties (should be 'properties')")
        print(f"🔍 Min fields found: {len(min_fields)} ({min_fields[:3]}{'...' if len(min_fields) > 3 else ''})")
        print(f"🔍 Max fields found: {len(max_fields)} ({max_fields[:3]}{'...' if len(max_fields) > 3 else ''})")
        print(f"🔍 Unit fields found: {len(unit_fields)} ({unit_fields[:3]}{'...' if len(unit_fields) > 3 else ''})")
        
        if len(min_fields) == 0 or len(max_fields) == 0:
            print("❌ ISSUE 1: Missing category ranges (no Min/Max fields found)")
        else:
            print("✅ Category ranges appear to be present")
    else:
        print("❌ No properties section found")
    
    # Check machineSettings organization
    machine_section = re.search(r'machineSettings:(.*?)(?=\w+:|$)', content, re.DOTALL)
    if machine_section:
        machine_content = machine_section.group(1)
        lines = [line.strip() for line in machine_content.split('\n') if line.strip()]
        
        print(f"\n🔍 Machine settings organization:")
        print(f"   Total settings lines: {len(lines)}")
        
        # Check for proper grouping (each setting should have its main value, then Unit, then Min/Max)
        settings_groups = {}
        for line in lines:
            if ':' in line:
                field = line.split(':')[0].strip()
                base_field = field.replace('Unit', '').replace('Min', '').replace('Max', '')
                if base_field not in settings_groups:
                    settings_groups[base_field] = []
                settings_groups[base_field].append(field)
        
        print(f"   Settings groups found: {len(settings_groups)}")
        organized_groups = 0
        for group, fields in settings_groups.items():
            if len(fields) >= 3:  # Should have at least main, Unit, Min, Max
                organized_groups += 1
            print(f"   {group}: {fields}")
        
        if organized_groups < 4:  # Should have at least powerRange, pulseDuration, spotSize, repetitionRate groups
            print("❌ ISSUE 2: Machine settings are unorganized")
        else:
            print("✅ Machine settings appear to be properly organized")
    else:
        print("❌ No machineSettings section found")


def test_category_ranges_loading():
    """Test if category ranges are loading correctly"""
    print("\n=== TESTING CATEGORY RANGES LOADING ===")
    
    generator = FrontmatterComponentGenerator()
    
    # Check if category ranges loaded
    if hasattr(generator, 'category_ranges') and generator.category_ranges:
        print(f"✅ Category ranges loaded: {len(generator.category_ranges)} categories")
        
        if 'metal' in generator.category_ranges:
            metal_ranges = generator.category_ranges['metal']
            print(f"✅ Metal category ranges: {len(metal_ranges)} properties")
            
            # Check key properties
            key_props = ['density', 'tensileStrength', 'thermalConductivity', 'thermalDestructionPoint']
            for prop in key_props:
                if prop in metal_ranges:
                    range_data = metal_ranges[prop]
                    print(f"   {prop}: {range_data.get('min', 'N/A')} - {range_data.get('max', 'N/A')}")
                else:
                    print(f"   {prop}: ❌ Not found")
        else:
            print("❌ Metal category not found in ranges")
    else:
        print("❌ Category ranges not loaded")


def regenerate_with_fixes():
    """Regenerate titanium frontmatter with both fixes applied"""
    print("\n=== REGENERATING TITANIUM FRONTMATTER WITH FIXES ===")
    
    # Get titanium data
    titanium_data = get_material_by_name('Titanium')
    if not titanium_data:
        print('❌ Could not find Titanium material data')
        return False
    
    print(f'✅ Found Titanium data with {len(titanium_data)} fields')
    print(f'   Category: {titanium_data.get("category", "N/A")}')
    print(f'   Has density: {bool(titanium_data.get("density"))}')
    print(f'   Has thermal_conductivity: {bool(titanium_data.get("thermal_conductivity"))}')
    print(f'   Has tensile_strength: {bool(titanium_data.get("tensile_strength"))}')
    print(f'   Has machine_settings: {bool(titanium_data.get("machine_settings"))}')
    
    # Generate with enhanced debugging
    generator = FrontmatterComponentGenerator()
    result = generator.generate('Titanium', titanium_data)
    
    if result.success:
        # Save to file
        with open('content/components/frontmatter/titanium-laser-cleaning-fixed.md', 'w') as f:
            f.write(result.content)
        
        print('✅ Regenerated titanium frontmatter successfully')
        print('📄 Saved to: content/components/frontmatter/titanium-laser-cleaning-fixed.md')
        
        # Analyze the fixed version
        content = result.content
        
        # Check for properties section (not technicalProperties)
        if 'properties:' in content and 'technicalProperties:' not in content:
            print('✅ FIX 1: Properties section correctly generated (not technicalProperties)')
        elif 'properties:' in content:
            print('⚠️  Properties section found, but technicalProperties also present')
        else:
            print('❌ Properties section still not generated correctly')
        
        # Check for category ranges in properties
        props_section = re.search(r'properties:(.*?)(?=\w+:|$)', content, re.DOTALL)
        if props_section:
            props_content = props_section.group(1)
            min_fields = re.findall(r'(\w+Min):', props_content)
            max_fields = re.findall(r'(\w+Max):', props_content)
            unit_fields = re.findall(r'(\w+Unit):', props_content)
            
            print(f'   Properties Min fields: {len(min_fields)} ({min_fields})')
            print(f'   Properties Max fields: {len(max_fields)} ({max_fields})')
            print(f'   Properties Unit fields: {len(unit_fields)} ({unit_fields})')
            
            if len(min_fields) >= 3 and len(max_fields) >= 3:
                print('✅ FIX 1 SUCCESS: Category ranges properly applied to properties')
            else:
                print('❌ FIX 1 FAILED: Category ranges not properly applied')
        
        # Check machineSettings organization
        machine_section = re.search(r'machineSettings:(.*?)(?=\w+:|$)', content, re.DOTALL)
        if machine_section:
            machine_content = machine_section.group(1)
            lines = [line.strip() for line in machine_content.split('\n') if line.strip()]
            
            # Check for proper field ordering
            setting_order = []
            for line in lines:
                if ':' in line:
                    field = line.split(':')[0].strip()
                    setting_order.append(field)
            
            print(f'   Machine settings order: {setting_order[:10]}{"..." if len(setting_order) > 10 else ""}')
            
            # Check if main settings come before their Unit/Min/Max variants
            organized = True
            for main_setting in ['powerRange', 'pulseDuration', 'spotSize', 'repetitionRate']:
                if main_setting in setting_order:
                    main_idx = setting_order.index(main_setting)
                    unit_field = f'{main_setting}Unit'
                    min_field = f'{main_setting}Min'
                    max_field = f'{main_setting}Max'
                    
                    if unit_field in setting_order:
                        unit_idx = setting_order.index(unit_field)
                        if unit_idx < main_idx:
                            organized = False
                            break
                    if min_field in setting_order:
                        min_idx = setting_order.index(min_field)
                        if min_idx < main_idx:
                            organized = False
                            break
            
            if organized:
                print('✅ FIX 2 SUCCESS: Machine settings properly organized')
            else:
                print('❌ FIX 2 FAILED: Machine settings not properly organized')
        
        # Show file size and key metrics
        file_size = len(result.content)
        print(f'\n📊 Generated file: {file_size} bytes')
        
        return True
    else:
        print(f'❌ Generation failed: {result.error_message}')
        return False


def compare_before_after():
    """Compare original vs fixed versions"""
    print("\n=== COMPARING BEFORE AND AFTER ===")
    
    try:
        with open('content/components/frontmatter/titanium-laser-cleaning.md', 'r') as f:
            original = f.read()
    except FileNotFoundError:
        print("❌ Original file not found")
        return
    
    try:
        with open('content/components/frontmatter/titanium-laser-cleaning-fixed.md', 'r') as f:
            fixed = f.read()
    except FileNotFoundError:
        print("❌ Fixed file not found")
        return
    
    print(f"Original file size: {len(original)} bytes")
    print(f"Fixed file size: {len(fixed)} bytes")
    
    # Count key sections
    for name, content in [("Original", original), ("Fixed", fixed)]:
        properties_matches = len(re.findall(r'properties:', content))
        technical_matches = len(re.findall(r'technicalProperties:', content))
        min_fields = len(re.findall(r'\w+Min:', content))
        max_fields = len(re.findall(r'\w+Max:', content))
        unit_fields = len(re.findall(r'\w+Unit:', content))
        
        print(f"\n{name} structure:")
        print(f"  properties sections: {properties_matches}")
        print(f"  technicalProperties sections: {technical_matches}")
        print(f"  Min fields: {min_fields}")
        print(f"  Max fields: {max_fields}")
        print(f"  Unit fields: {unit_fields}")


if __name__ == "__main__":
    print("🔧 TITANIUM FRONTMATTER DIAGNOSTIC AND FIX TOOL")
    print("=" * 60)
    
    # Step 1: Analyze current issues
    analyze_current_issues()
    
    # Step 2: Test category ranges loading
    test_category_ranges_loading()
    
    # Step 3: Apply fixes and regenerate
    success = regenerate_with_fixes()
    
    # Step 4: Compare results
    if success:
        compare_before_after()
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY OF PROPOSED FIXES:")
        print("=" * 60)
        print("1. CATEGORY RANGES FIX:")
        print("   - Properties section should use 'properties:' not 'technicalProperties:'")
        print("   - Each property should have Min/Max/Unit fields from metal category ranges")
        print("   - Example: densityMin: '0.53 g/cm³', densityMax: '22.59 g/cm³', densityUnit: 'g/cm³'")
        print("\n2. MACHINE SETTINGS ORGANIZATION FIX:")
        print("   - Group related fields together (main value, Unit, Min, Max)")
        print("   - Use proper field ordering: powerRange -> powerRangeUnit -> powerRangeMin -> powerRangeMax")
        print("   - Apply FieldOrderingService._create_clean_machine_settings_structure()")
        print("\n3. IMPLEMENTATION:")
        print("   - Generator already has the methods, just need to ensure they're called correctly")
        print("   - Check if _add_property_with_ranges() is working for all properties")
        print("   - Ensure FieldOrderingService is applied to final output")
    
    print("\nDiagnostic complete! Check the generated -fixed.md file for results.")
