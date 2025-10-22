#!/usr/bin/env python3
"""
Critical Materials.yaml Issues Analyzer & Fixer

Focuses on the most important data consistency issues found and provides fixes:

1. HARDNESS UNIT ISSUE (41 materials affected) - Most Critical
2. MISSING INDEX ENTRIES (4 rare-earth materials) - Easy Fix  
3. SPARSE PROPERTIES (8 rare-earth materials) - Research Needed

This script provides automated fixes for the fixable issues.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List

class CriticalIssuesFixer:
    
    def __init__(self, materials_file: str = "data/Materials.yaml"):
        self.materials_file = Path(materials_file)
        self.backup_file = None
    
    def create_backup(self):
        """Create backup before making changes"""
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.materials_file.parent / f"Materials_backup_critical_fixes_{timestamp}.yaml"
        
        import shutil
        shutil.copy2(self.materials_file, self.backup_file)
        print(f"📁 Backup created: {self.backup_file.name}")
        return self.backup_file
    
    def load_materials(self):
        """Load Materials.yaml"""
        with open(self.materials_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_materials(self, data):
        """Save Materials.yaml"""
        with open(self.materials_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120)
    
    def analyze_hardness_units(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze hardness unit inconsistencies"""
        materials = data.get('materials', {})
        hardness_issues = []
        
        for material_name, material_data in materials.items():
            if 'materialProperties' in material_data:
                mat_props = material_data['materialProperties']
                if isinstance(mat_props, dict):
                    for prop_group, group_data in mat_props.items():
                        if isinstance(group_data, dict) and 'properties' in group_data:
                            properties = group_data['properties']
                            
                            if 'hardness' in properties:
                                hardness_data = properties['hardness']
                                if isinstance(hardness_data, dict):
                                    value = hardness_data.get('value', 0)
                                    unit = hardness_data.get('unit', '')
                                    
                                    # Detect likely unit issues
                                    if isinstance(value, (int, float)):
                                        # Values > 100 in "GPa" are likely MPa or other units
                                        if unit == 'GPa' and value > 100:
                                            hardness_issues.append({
                                                'material': material_name,
                                                'current_value': value,
                                                'current_unit': unit,
                                                'likely_correct_unit': 'MPa' if value < 10000 else 'HV',
                                                'property_group': prop_group
                                            })
                                        # Values > 1000 are likely Vickers hardness (HV)
                                        elif unit == 'GPa' and value > 1000:
                                            hardness_issues.append({
                                                'material': material_name,
                                                'current_value': value,
                                                'current_unit': unit,
                                                'likely_correct_unit': 'HV',
                                                'property_group': prop_group
                                            })
        
        return hardness_issues
    
    def fix_hardness_units(self, data: Dict[str, Any], hardness_issues: List[Dict[str, Any]]) -> int:
        """Fix hardness unit inconsistencies"""
        materials = data.get('materials', {})
        fixes_applied = 0
        
        for issue in hardness_issues:
            material_name = issue['material']
            prop_group = issue['property_group']
            correct_unit = issue['likely_correct_unit']
            
            if material_name in materials:
                mat_props = materials[material_name]['materialProperties']
                if prop_group in mat_props and 'properties' in mat_props[prop_group]:
                    properties = mat_props[prop_group]['properties']
                    if 'hardness' in properties:
                        # Update the unit
                        old_unit = properties['hardness']['unit']
                        properties['hardness']['unit'] = correct_unit
                        
                        # Update description if it mentions the old unit
                        if 'description' in properties['hardness']:
                            desc = properties['hardness']['description']
                            if old_unit in desc:
                                properties['hardness']['description'] = desc.replace(old_unit, correct_unit)
                        
                        print(f"🔧 Fixed {material_name}: hardness unit {old_unit} → {correct_unit}")
                        fixes_applied += 1
        
        return fixes_applied
    
    def fix_missing_index_entries(self, data: Dict[str, Any]) -> int:
        """Fix missing material index entries"""
        materials = data.get('materials', {})
        material_index = data.get('material_index', {})
        fixes_applied = 0
        
        # Rare-earth materials that are missing from index
        missing_materials = ['Dysprosium', 'Neodymium', 'Praseodymium', 'Terbium']
        
        for material_name in missing_materials:
            if material_name in materials and material_name not in material_index:
                # Add to material index with rare-earth category
                material_index[material_name] = 'rare-earth'
                print(f"🔧 Added {material_name} to material_index as 'rare-earth'")
                fixes_applied += 1
        
        return fixes_applied
    
    def analyze_sparse_properties(self, data: Dict[str, Any]) -> List[str]:
        """Identify materials with sparse property data"""
        materials = data.get('materials', {})
        sparse_materials = []
        
        for material_name, material_data in materials.items():
            total_props = 0
            if 'materialProperties' in material_data:
                mat_props = material_data['materialProperties']
                if isinstance(mat_props, dict):
                    for group_data in mat_props.values():
                        if isinstance(group_data, dict) and 'properties' in group_data:
                            total_props += len(group_data['properties'])
            
            if total_props < 5:  # Arbitrary threshold
                sparse_materials.append(material_name)
        
        return sparse_materials
    
    def run_critical_fixes(self, dry_run: bool = False):
        """Run all critical fixes"""
        print("🔧 Critical Materials.yaml Issues Fixer")
        print("=" * 50)
        
        # Create backup if not dry run
        if not dry_run:
            self.create_backup()
        
        # Load data
        print("📖 Loading Materials.yaml...")
        data = self.load_materials()
        
        # Analyze issues
        print("🔍 Analyzing hardness unit issues...")
        hardness_issues = self.analyze_hardness_units(data)
        print(f"   Found {len(hardness_issues)} hardness unit issues")
        
        print("🔍 Checking missing index entries...")
        materials = data.get('materials', {})
        material_index = data.get('material_index', {})
        missing_count = sum(1 for mat in ['Dysprosium', 'Neodymium', 'Praseodymium', 'Terbium'] 
                           if mat in materials and mat not in material_index)
        print(f"   Found {missing_count} missing index entries")
        
        print("🔍 Identifying sparse properties...")
        sparse_materials = self.analyze_sparse_properties(data)
        print(f"   Found {len(sparse_materials)} materials with sparse properties")
        
        if dry_run:
            print("\\n🔍 DRY RUN - Changes that would be made:")
            print(f"   • Fix {len(hardness_issues)} hardness unit issues")
            print(f"   • Add {missing_count} missing index entries")
            print(f"   • {len(sparse_materials)} materials need property research")
            return
        
        # Apply fixes
        total_fixes = 0
        
        print("\\n🔧 Fixing hardness units...")
        hardness_fixes = self.fix_hardness_units(data, hardness_issues)
        total_fixes += hardness_fixes
        
        print("🔧 Adding missing index entries...")
        index_fixes = self.fix_missing_index_entries(data)
        total_fixes += index_fixes
        
        # Save if fixes were applied
        if total_fixes > 0:
            print("💾 Saving updated Materials.yaml...")
            self.save_materials(data)
            print(f"✅ Applied {total_fixes} fixes successfully!")
        else:
            print("ℹ️  No fixes needed")
        
        # Report on sparse properties (manual action needed)
        if sparse_materials:
            print(f"\\n📋 Materials needing property research ({len(sparse_materials)}):")
            for material in sparse_materials:
                print(f"   • {material}")
            print("   ⚠️  These require manual research - use AI research tools")
        
        return total_fixes

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix critical Materials.yaml data issues')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    args = parser.parse_args()
    
    fixer = CriticalIssuesFixer()
    fixes_applied = fixer.run_critical_fixes(dry_run=args.dry_run)
    
    if not args.dry_run:
        if fixes_applied > 0:
            print(f"\\n🎉 Successfully applied {fixes_applied} critical fixes!")
            print("💡 Re-run the comprehensive checker to verify all issues resolved")
        else:
            print("\\n✅ No critical fixes needed!")

if __name__ == "__main__":
    main()