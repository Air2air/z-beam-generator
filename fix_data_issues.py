#!/usr/bin/env python3
"""
Comprehensive Data Issues Fixer
Fixes subcategory issues, adds missing fields, and ensures compliance
"""

import yaml
from pathlib import Path

class DataIssuesFixer:
    def __init__(self):
        self.materials_yaml_path = Path("data/materials.yaml")
        self.frontmatter_dir = Path("content/components/frontmatter")
        
        # Schema-compliant subcategories
        self.valid_subcategories = {
            'metal': ['precious', 'ferrous', 'non-ferrous', 'refractory', 'reactive', 'specialty'],
            'stone': ['igneous', 'metamorphic', 'sedimentary', 'architectural', 'composite'],
            'ceramic': ['oxide', 'nitride', 'carbide', 'traditional'],
            'semiconductor': ['intrinsic', 'doped', 'compound'],
            'plastic': ['thermoplastic', 'thermoset', 'engineering', 'biodegradable'],
            'glass': ['borosilicate', 'soda-lime', 'lead', 'specialty-glass'],
            'wood': ['hardwood', 'softwood', 'engineered', 'grass'],
            'composite': ['fiber-reinforced', 'matrix', 'resin', 'elastomeric'],
            'masonry': ['fired', 'concrete', 'natural']
        }
        
        # Subcategory mapping for common corrections
        self.subcategory_corrections = {
            'stone': {
                'soft': 'sedimentary',
                'mineral': 'sedimentary',
                'crystal': 'metamorphic'
            },
            'ceramic': {
                'general': 'oxide'
            },
            'semiconductor': {
                'elemental': 'intrinsic'
            },
            'plastic': {
                'general': 'thermoplastic'
            },
            'glass': {
                'general': 'soda-lime',
                'silicate': 'soda-lime',
                'crystal': 'lead',
                'specialty': 'specialty-glass',
                'treated': 'specialty-glass'
            },
            'wood': {
                'flexible': 'softwood'
            },
            'composite': {
                'structural': 'fiber-reinforced'
            },
            'masonry': {
                'cementitious': 'concrete',
                'surface': 'fired'
            }
        }
    
    def fix_materials_yaml_subcategories(self):
        """Fix invalid subcategories in materials.yaml material_index"""
        print("🔧 Fixing materials.yaml subcategories...")
        
        with open(self.materials_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        fixes_applied = 0
        
        if 'material_index' in data:
            for material_name, material_info in data['material_index'].items():
                category = material_info.get('category')
                current_subcategory = material_info.get('subcategory')
                
                if category in self.valid_subcategories:
                    if current_subcategory not in self.valid_subcategories[category]:
                        # Try to find a correction
                        if category in self.subcategory_corrections and current_subcategory in self.subcategory_corrections[category]:
                            new_subcategory = self.subcategory_corrections[category][current_subcategory]
                            material_info['subcategory'] = new_subcategory
                            print(f"  ✅ {material_name}: '{current_subcategory}' → '{new_subcategory}'")
                            fixes_applied += 1
                        else:
                            # Use the first valid subcategory as default
                            default_subcategory = self.valid_subcategories[category][0]
                            material_info['subcategory'] = default_subcategory
                            print(f"  ⚠️  {material_name}: '{current_subcategory}' → '{default_subcategory}' (default)")
                            fixes_applied += 1
        
        # Save the fixed materials.yaml
        with open(self.materials_yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120, indent=2)
        
        print(f"✅ Fixed {fixes_applied} subcategories in materials.yaml")
        return fixes_applied
    
    def fix_frontmatter_subcategories(self):
        """Fix invalid subcategories in frontmatter files"""
        print("🔧 Fixing frontmatter subcategories...")
        
        if not self.frontmatter_dir.exists():
            print("❌ Frontmatter directory not found")
            return 0
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        fixes_applied = 0
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    yaml_start = content.find('---') + 3
                    yaml_end = content.find('---', yaml_start)
                    if yaml_end == -1:
                        yaml_content = content[yaml_start:].strip()
                        after_yaml = ""
                    else:
                        yaml_content = content[yaml_start:yaml_end].strip()
                        after_yaml = content[yaml_end:]
                
                    # Parse YAML
                    data = yaml.safe_load(yaml_content)
                    
                    if data:
                        category = data.get('category')
                        current_subcategory = data.get('subcategory')
                        
                        if category in self.valid_subcategories and current_subcategory not in self.valid_subcategories[category]:
                            # Try to find a correction
                            if category in self.subcategory_corrections and current_subcategory in self.subcategory_corrections[category]:
                                new_subcategory = self.subcategory_corrections[category][current_subcategory]
                            else:
                                new_subcategory = self.valid_subcategories[category][0]
                            
                            data['subcategory'] = new_subcategory
                            
                            # Rebuild the file
                            new_yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, width=120, indent=2)
                            new_content = f"---\n{new_yaml_content.strip()}\n{after_yaml}"
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            print(f"  ✅ {file_path.name}: '{current_subcategory}' → '{new_subcategory}'")
                            fixes_applied += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
        
        print(f"✅ Fixed {fixes_applied} subcategories in frontmatter files")
        return fixes_applied
    
    def add_missing_wavelength_ranges(self):
        """Add missing wavelengthMin and wavelengthMax to all frontmatter files"""
        print("🔧 Adding missing wavelength ranges...")
        
        if not self.frontmatter_dir.exists():
            print("❌ Frontmatter directory not found")
            return 0
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        fixes_applied = 0
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    yaml_start = content.find('---') + 3
                    yaml_end = content.find('---', yaml_start)
                    if yaml_end == -1:
                        yaml_content = content[yaml_start:].strip()
                        after_yaml = ""
                    else:
                        yaml_content = content[yaml_start:yaml_end].strip()
                        after_yaml = content[yaml_end:]
                
                    # Parse YAML
                    data = yaml.safe_load(yaml_content)
                    
                    if data and 'machineSettings' in data:
                        machine_settings = data['machineSettings']
                        wavelength = machine_settings.get('wavelength')
                        
                        # Add wavelengthMin and wavelengthMax if missing
                        if wavelength and ('wavelengthMin' not in machine_settings or 'wavelengthMax' not in machine_settings):
                            machine_settings['wavelengthMin'] = wavelength
                            machine_settings['wavelengthMax'] = wavelength
                            
                            # Rebuild the file
                            new_yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, width=120, indent=2)
                            new_content = f"---\n{new_yaml_content.strip()}\n{after_yaml}"
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            fixes_applied += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
        
        print(f"✅ Added wavelength ranges to {fixes_applied} files")
        return fixes_applied
    
    def add_missing_unit_fields(self):
        """Add missing unit fields to frontmatter files"""
        print("🔧 Adding missing unit fields...")
        
        if not self.frontmatter_dir.exists():
            print("❌ Frontmatter directory not found")
            return 0
        
        md_files = list(self.frontmatter_dir.glob("*.md"))
        fixes_applied = 0
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    yaml_start = content.find('---') + 3
                    yaml_end = content.find('---', yaml_start)
                    if yaml_end == -1:
                        yaml_content = content[yaml_start:].strip()
                        after_yaml = ""
                    else:
                        yaml_content = content[yaml_start:yaml_end].strip()
                        after_yaml = content[yaml_end:]
                
                    # Parse YAML
                    data = yaml.safe_load(yaml_content)
                    
                    if data and 'properties' in data:
                        properties = data['properties']
                        modified = False
                        
                        # Check for missing thermalConductivityUnit
                        if 'thermalConductivity' in properties and 'thermalConductivityUnit' not in properties:
                            properties['thermalConductivityUnit'] = 'W/m·K'
                            modified = True
                        
                        if modified:
                            # Rebuild the file
                            new_yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, width=120, indent=2)
                            new_content = f"---\n{new_yaml_content.strip()}\n{after_yaml}"
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            fixes_applied += 1
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
        
        print(f"✅ Added unit fields to {fixes_applied} files")
        return fixes_applied
    
    def run_all_fixes(self):
        """Run all data fixes"""
        print("🚀 STARTING COMPREHENSIVE DATA FIXES")
        print("=" * 50)
        
        total_fixes = 0
        
        # Fix materials.yaml subcategories
        total_fixes += self.fix_materials_yaml_subcategories()
        print()
        
        # Fix frontmatter subcategories
        total_fixes += self.fix_frontmatter_subcategories()
        print()
        
        # Add missing wavelength ranges
        total_fixes += self.add_missing_wavelength_ranges()
        print()
        
        # Add missing unit fields
        total_fixes += self.add_missing_unit_fields()
        print()
        
        print("=" * 50)
        print(f"🎉 COMPLETED: Applied {total_fixes} fixes total")
        print("=" * 50)
        
        return total_fixes


def main():
    fixer = DataIssuesFixer()
    return fixer.run_all_fixes()


if __name__ == "__main__":
    fixes_applied = main()
    exit(0 if fixes_applied > 0 else 1)