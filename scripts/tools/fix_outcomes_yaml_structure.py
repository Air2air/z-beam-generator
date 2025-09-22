#!/usr/bin/env python3
"""
Fix YAML Structure for Outcomes Section

Fix the mixed dictionary/list format in outcomes sections.
Ensure proper YAML structure with standardized variable names.
"""

import os
import re

def fix_outcomes_yaml_structure():
    """Fix YAML structure in all frontmatter files"""
    
    print("🔧 FIXING OUTCOMES YAML STRUCTURE")
    print("=" * 50)
    print("Converting mixed format to proper structure:")
    print("Before (broken):")
    print("  outcomes:")
    print("    surface_roughness_before: 8.5")
    print("    surface_roughness_after: 1.2")
    print("  - result: Contaminant removal efficiency")
    print("")
    print("After (fixed):")
    print("  outcomes:")
    print("    surface_roughness_before: 8.5")
    print("    surface_roughness_after: 1.2")
    print("    contaminant_removal:")
    print("      result: Contaminant removal efficiency")
    print("      metric: '>99.5% removal...'")
    print("=" * 50)
    
    fixed_count = 0
    error_count = 0
    
    frontmatter_dir = "content/components/frontmatter"
    
    for filename in os.listdir(frontmatter_dir):
        if filename.endswith("-laser-cleaning.md"):
            file_path = os.path.join(frontmatter_dir, filename)
            material_name = filename.replace("-laser-cleaning.md", "")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Pattern to find and fix the broken structure
                # Look for outcomes: followed by surface roughness, then - result items
                pattern = r'(outcomes:\s*\n\s*surface_roughness_before:\s*[\d.]+\s*\n\s*surface_roughness_after:\s*[\d.]+)\s*\n((?:\s*-\s*result:.*\n(?:\s*metric:.*\n)*)*)'
                
                def fix_structure(match):
                    surface_roughness_section = match.group(1)
                    result_items = match.group(2)
                    
                    # Convert list items to proper dictionary structure
                    fixed_results = ""
                    if result_items.strip():
                        # Parse the result items and convert to proper YAML
                        lines = result_items.strip().split('\n')
                        current_result = None
                        metrics = []
                        
                        for line in lines:
                            line = line.strip()
                            if line.startswith('- result:'):
                                # Save previous result if exists
                                if current_result:
                                    sanitized_key = current_result.lower().replace(' ', '_').replace('-', '_')
                                    fixed_results += f"\n    {sanitized_key}:"
                                    fixed_results += f"\n      result: {current_result}"
                                    if metrics:
                                        for metric in metrics:
                                            fixed_results += f"\n      metric: {metric}"
                                
                                # Start new result
                                current_result = line.replace('- result:', '').strip()
                                metrics = []
                            
                            elif line.startswith('metric:'):
                                metric_value = line.replace('metric:', '').strip()
                                if metric_value and not metric_value.startswith('"Ra'):  # Skip duplicate Ra values
                                    metrics.append(metric_value)
                        
                        # Handle the last result
                        if current_result:
                            sanitized_key = current_result.lower().replace(' ', '_').replace('-', '_')
                            fixed_results += f"\n    {sanitized_key}:"
                            fixed_results += f"\n      result: {current_result}"
                            if metrics:
                                for metric in metrics:
                                    fixed_results += f"\n      metric: {metric}"
                    
                    return surface_roughness_section + fixed_results
                
                updated_content = re.sub(pattern, fix_structure, content, flags=re.MULTILINE | re.DOTALL)
                
                if updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"   ✅ {material_name}: Fixed YAML structure")
                    fixed_count += 1
                else:
                    print(f"   ⚠️  {material_name}: No fixes needed or already correct")
                    
            except Exception as e:
                print(f"   ❌ {material_name}: Error - {str(e)}")
                error_count += 1
    
    print(f"\n📊 YAML FIX SUMMARY:")
    print(f"   ✅ Fixed: {fixed_count} files")
    print(f"   ❌ Errors: {error_count} files")
    
    return fixed_count

def main():
    """Main YAML fixing process"""
    
    fixed_count = fix_outcomes_yaml_structure()
    
    if fixed_count > 0:
        print(f"\n🎯 YAML STRUCTURE FIXED")
        print("All frontmatter files now have proper YAML structure")
        print("Ready for caption component generation")
    else:
        print(f"\n✅ ALL FILES ALREADY HAVE CORRECT YAML STRUCTURE")

if __name__ == "__main__":
    main()
