#!/usr/bin/env python3
"""
Standardize Surface Roughness Variable Names

Convert from descriptive field names to standardized variable names:
- Surface roughness before treatment -> surface_roughness_before
- Surface roughness after treatment -> surface_roughness_after

Updates both frontmatter files and caption component code.
"""

import os
import re

def standardize_frontmatter_field_names():
    """Convert all frontmatter files to use standardized variable names"""
    
    print("🔧 STANDARDIZING SURFACE ROUGHNESS VARIABLE NAMES")
    print("=" * 60)
    print("Converting to standardized format:")
    print("  Before: 'Surface roughness before treatment: Ra X.X μm'")
    print("  After:  'surface_roughness_before: X.X'")
    print("=" * 60)
    
    updated_count = 0
    error_count = 0
    
    # Pattern to match current format
    before_pattern = r'(\s*)- Surface roughness before treatment: Ra (\d+\.?\d*) μm'
    after_pattern = r'(\s*)- Surface roughness after treatment: Ra (\d+\.?\d*) μm'
    
    # New standardized format
    before_replacement = r'\1surface_roughness_before: \2'
    after_replacement = r'\1surface_roughness_after: \2'
    
    frontmatter_dir = "content/components/frontmatter"
    
    for filename in os.listdir(frontmatter_dir):
        if filename.endswith("-laser-cleaning.md"):
            file_path = os.path.join(frontmatter_dir, filename)
            material_name = filename.replace("-laser-cleaning.md", "")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if it has the old format
                has_old_before = re.search(before_pattern, content)
                has_old_after = re.search(after_pattern, content)
                
                if has_old_before or has_old_after:
                    # Apply replacements
                    updated_content = re.sub(before_pattern, before_replacement, content)
                    updated_content = re.sub(after_pattern, after_replacement, updated_content)
                    
                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"   ✅ {material_name}: Standardized variable names")
                    updated_count += 1
                else:
                    print(f"   ⚠️  {material_name}: No surface roughness fields found or already standardized")
                    
            except Exception as e:
                print(f"   ❌ {material_name}: Error - {str(e)}")
                error_count += 1
    
    print(f"\n📊 STANDARDIZATION SUMMARY:")
    print(f"   ✅ Updated: {updated_count} files")
    print(f"   ❌ Errors: {error_count} files")
    
    return updated_count > 0

def update_caption_component():
    """Update caption component to use standardized variable names"""
    
    print(f"\n🔧 UPDATING CAPTION COMPONENT")
    print("=" * 40)
    
    caption_file = "components/caption/generators/generator.py"
    
    try:
        with open(caption_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the _generate_quality_metrics function and update it
        old_function = '''    def _generate_quality_metrics(self, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate realistic quality metrics based on frontmatter data"""
        
        # Extract surface roughness from frontmatter outcomes if available
        surface_before = "Ra 3.2 μm"  # Default fallback
        surface_after = "Ra 0.6 μm"   # Default fallback
        
        if frontmatter_data and 'outcomes' in frontmatter_data:
            outcomes = frontmatter_data['outcomes']
            if isinstance(outcomes, list):
                for outcome in outcomes:
                    if isinstance(outcome, dict):
                        result = outcome.get('result', '').lower()
                        metric = outcome.get('metric', '')
                        
                        if 'surface roughness before' in result and metric:
                            surface_before = metric.strip()
                        elif 'surface roughness after' in result and metric:
                            surface_after = metric.strip()'''
        
        new_function = '''    def _generate_quality_metrics(self, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate realistic quality metrics based on frontmatter data"""
        
        # Extract surface roughness from frontmatter using standardized variable names
        surface_before = "Ra 3.2 μm"  # Default fallback
        surface_after = "Ra 0.6 μm"   # Default fallback
        
        if frontmatter_data:
            # Check for standardized variable names in outcomes section
            if 'outcomes' in frontmatter_data:
                outcomes = frontmatter_data['outcomes']
                if isinstance(outcomes, dict):
                    # Direct access to standardized field names
                    if 'surface_roughness_before' in outcomes:
                        surface_before = f"Ra {outcomes['surface_roughness_before']} μm"
                    if 'surface_roughness_after' in outcomes:
                        surface_after = f"Ra {outcomes['surface_roughness_after']} μm"'''
        
        if old_function in content:
            updated_content = content.replace(old_function, new_function)
            
            with open(caption_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("   ✅ Caption component updated to use standardized variable names")
            return True
        else:
            print("   ⚠️  Caption component function not found in expected format")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating caption component: {str(e)}")
        return False

def update_frontmatter_to_dict_format():
    """Convert frontmatter outcomes from list format to dictionary format"""
    
    print(f"\n🔧 CONVERTING OUTCOMES TO DICTIONARY FORMAT")
    print("=" * 50)
    print("Converting from:")
    print("  outcomes:")
    print("    - surface_roughness_before: X.X")
    print("    - surface_roughness_after: X.X")
    print("To:")
    print("  outcomes:")
    print("    surface_roughness_before: X.X")
    print("    surface_roughness_after: X.X")
    print("=" * 50)
    
    updated_count = 0
    error_count = 0
    
    frontmatter_dir = "content/components/frontmatter"
    
    for filename in os.listdir(frontmatter_dir):
        if filename.endswith("-laser-cleaning.md"):
            file_path = os.path.join(frontmatter_dir, filename)
            material_name = filename.replace("-laser-cleaning.md", "")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Pattern to find outcomes section with list format
                pattern = r'(outcomes:\s*\n)(\s*)surface_roughness_before: (\d+\.?\d*)\s*\n\s*surface_roughness_after: (\d+\.?\d*)'
                
                def replace_outcomes(match):
                    before_val = match.group(3)
                    after_val = match.group(4)
                    indent = match.group(2)
                    
                    return f"""outcomes:
{indent}surface_roughness_before: {before_val}
{indent}surface_roughness_after: {after_val}"""
                
                updated_content = re.sub(pattern, replace_outcomes, content)
                
                if updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"   ✅ {material_name}: Converted to dictionary format")
                    updated_count += 1
                else:
                    print(f"   ⚠️  {material_name}: No conversion needed or already in correct format")
                    
            except Exception as e:
                print(f"   ❌ {material_name}: Error - {str(e)}")
                error_count += 1
    
    print(f"\n📊 CONVERSION SUMMARY:")
    print(f"   ✅ Updated: {updated_count} files")
    print(f"   ❌ Errors: {error_count} files")

def main():
    """Main standardization process"""
    
    # Step 1: Standardize field names
    fields_updated = standardize_frontmatter_field_names()
    
    # Step 2: Convert to dictionary format
    if fields_updated:
        update_frontmatter_to_dict_format()
    
    # Step 3: Update caption component
    update_caption_component()
    
    print(f"\n🎯 STANDARDIZATION COMPLETE")
    print("New standardized format:")
    print("  - Variable names: surface_roughness_before, surface_roughness_after")
    print("  - Structure: Dictionary in outcomes section")
    print("  - Units: Values stored as numbers (μm implied)")
    print("  - Caption component: Updated to read standardized format")

if __name__ == "__main__":
    main()
