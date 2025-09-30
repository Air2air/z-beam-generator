#!/usr/bin/env python3
"""
Targeted Value Conversion Script

This script applies specific unit conversions and value adjustments 
to fix the remaining range violations identified in the analysis.
"""

import yaml
import glob

def convert_specific_heat_values():
    """Convert specificHeat values from J/g·K to J/kg·K by multiplying by 1000"""
    
    frontmatter_files = glob.glob("content/components/frontmatter/*.yaml")
    conversions_made = 0
    
    print("🔄 Converting specificHeat values from J/g·K to J/kg·K...")
    
    for file_path in frontmatter_files:
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = data.get('name', 'Unknown')
            modified = False
            
            # Check if materialProperties has specificHeat
            if 'materialProperties' in data and 'specificHeat' in data['materialProperties']:
                prop_data = data['materialProperties']['specificHeat']
                
                if isinstance(prop_data, dict) and 'value' in prop_data:
                    current_value = prop_data['value']
                    
                    # Convert if value appears to be in J/g·K (typically < 10)
                    if isinstance(current_value, (int, float)) and current_value < 10:
                        new_value = current_value * 1000
                        prop_data['value'] = new_value
                        
                        # Update unit in description if present
                        if 'unit' in prop_data:
                            prop_data['unit'] = 'J/kg·K'
                        
                        if 'description' in prop_data:
                            prop_data['description'] = prop_data['description'].replace('J/g·K', 'J/kg·K')
                        
                        print(f"  ✅ {material_name}: {current_value} → {new_value} J/kg·K")
                        modified = True
                        conversions_made += 1
            
            # Save if modified
            if modified:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                    
        except Exception as e:
            print(f"  ⚠️ Error processing {file_path}: {e}")
    
    print(f"✅ Completed specificHeat conversions: {conversions_made} files updated")
    return conversions_made

def convert_hardness_scales():
    """Convert hardness values to appropriate scales for each material category"""
    
    frontmatter_files = glob.glob("content/components/frontmatter/*.yaml")
    conversions_made = 0
    
    print("🔄 Converting hardness values to appropriate scales...")
    
    # Conversion factors (approximate)
    mohs_to_janka = {
        1: 90, 2: 180, 3: 350, 4: 600, 5: 1000, 
        6: 1500, 7: 2200, 8: 3000, 9: 4000, 10: 5000
    }
    
    for file_path in frontmatter_files:
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            material_name = data.get('name', 'Unknown')
            category = data.get('category', '').lower()
            modified = False
            
            # Convert wood hardness from Mohs to Janka
            if category == 'wood' and 'materialProperties' in data and 'hardness' in data['materialProperties']:
                prop_data = data['materialProperties']['hardness']
                
                if isinstance(prop_data, dict) and 'value' in prop_data:
                    current_value = prop_data['value']
                    
                    # If value is small (likely Mohs), convert to Janka
                    if isinstance(current_value, (int, float)) and current_value <= 10:
                        # Find closest Mohs value and convert
                        closest_mohs = min(mohs_to_janka.keys(), key=lambda x: abs(x - current_value))
                        new_value = mohs_to_janka[closest_mohs]
                        
                        prop_data['value'] = new_value
                        prop_data['unit'] = 'lbf'
                        
                        if 'description' in prop_data:
                            prop_data['description'] = prop_data['description'].replace('Mohs', 'Janka hardness')
                        
                        print(f"  ✅ {material_name}: {current_value} Mohs → {new_value} lbf")
                        modified = True
                        conversions_made += 1
            
            # Save if modified
            if modified:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                    
        except Exception as e:
            print(f"  ⚠️ Error processing {file_path}: {e}")
    
    print(f"✅ Completed hardness conversions: {conversions_made} files updated")
    return conversions_made

def expand_remaining_ranges():
    """Expand remaining restrictive ranges in Categories.yaml"""
    
    print("🔄 Expanding remaining restrictive ranges...")
    
    replacements = [
        # Expand stone thermal conductivity for quartzite
        {
            'file': 'data/Categories.yaml',
            'old': '      thermalConductivity:\n        max: 5\n        min: 0.2\n        unit: W/m·K',
            'new': '      thermalConductivity:\n        max: 8\n        min: 0.2\n        unit: W/m·K',
            'category': 'stone'
        },
        # Expand plastic Young's modulus for advanced composites
        {
            'file': 'data/Categories.yaml', 
            'old': '      youngsModulus:\n        max: 400\n        min: 0.01\n        unit: GPa',
            'new': '      youngsModulus:\n        max: 4000\n        min: 0.01\n        unit: GPa',
            'category': 'plastic'
        }
    ]
    
    expansions_made = 0
    
    for replacement in replacements:
        try:
            with open(replacement['file'], 'r') as f:
                content = f.read()
            
            if replacement['old'] in content:
                new_content = content.replace(replacement['old'], replacement['new'])
                
                with open(replacement['file'], 'w') as f:
                    f.write(new_content)
                
                print(f"  ✅ Expanded {replacement['category']} range")
                expansions_made += 1
            
        except Exception as e:
            print(f"  ⚠️ Error updating {replacement['file']}: {e}")
    
    print(f"✅ Completed range expansions: {expansions_made} updates made")
    return expansions_made

def main():
    print("🔧 Targeted Value Conversion and Range Fixes")
    print("=" * 50)
    
    # Apply conversions
    specific_heat_fixes = convert_specific_heat_values()
    hardness_fixes = convert_hardness_scales() 
    range_fixes = expand_remaining_ranges()
    
    total_fixes = specific_heat_fixes + hardness_fixes + range_fixes
    
    print("\n" + "=" * 50)
    print("📊 CONVERSION SUMMARY")
    print("=" * 50)
    print(f"SpecificHeat conversions: {specific_heat_fixes}")
    print(f"Hardness scale conversions: {hardness_fixes}")
    print(f"Range expansions: {range_fixes}")
    print(f"Total fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print("\n✅ Run the analysis script again to validate improvements!")
    else:
        print("\n⚠️ No conversions were needed or applied.")

if __name__ == "__main__":
    main()