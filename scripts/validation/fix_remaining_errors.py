#!/usr/bin/env python3
"""
Fix Remaining Simple Errors

Addresses the final easy-to-fix validation errors:
1. corrosionResistance qualitative standardization (2 errors)
2. Out-of-range magnitude errors (4 errors)
"""

import yaml
from pathlib import Path
from datetime import datetime
import shutil

class RemainingErrorsFixer:
    """Fix remaining validation errors"""
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.frontmatter_dir = data_dir / "content" / "components" / "frontmatter"
        self.backup_dir = data_dir / "backups" / f"remaining_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []
        
    def create_backup(self):
        """Create backup of frontmatter directory"""
        print(f"Creating backup at {self.backup_dir}...")
        shutil.copytree(self.frontmatter_dir, self.backup_dir)
        print("✅ Backup created\n")
    
    def fix_material(self, material: str, fixes: dict) -> int:
        """Apply fixes to a specific material"""
        file_path = self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
        
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        changes = 0
        
        # Apply each fix
        for prop_name, fix_data in fixes.items():
            if 'materialProperties' in data:
                for group_name, group_data in data['materialProperties'].items():
                    # Properties are directly in group_data (flat structure)
                    metadata_keys = {'label', 'description', 'percentage'}
                    if not isinstance(group_data, dict):
                        continue
                    
                    if prop_name in group_data and prop_name not in metadata_keys:
                        prop_data = group_data[prop_name]
                        
                        # Apply fix
                        if 'value' in fix_data:
                            old_value = prop_data.get('value')
                            prop_data['value'] = fix_data['value']
                            changes += 1
                            self.fixes_applied.append({
                                'material': material,
                                'property': prop_name,
                                'old_value': old_value,
                                'new_value': fix_data['value'],
                                'reason': fix_data.get('reason', 'correction')
                            })
                        
                        if 'unit' in fix_data:
                            prop_data['unit'] = fix_data['unit']
                        
                        if 'notes' in fix_data:
                            prop_data['notes'] = fix_data['notes']
                        
                        if 'confidence' in fix_data:
                            prop_data['confidence'] = fix_data['confidence']
                        
                        break
        
        if changes > 0:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"✅ {material}: {changes} fixes applied")
        
        return changes
    
    def fix_all_remaining(self):
        """Fix all remaining simple errors"""
        print("=" * 80)
        print("REMAINING ERRORS FIXER")
        print("=" * 80)
        print()
        
        # Create backup
        self.create_backup()
        
        # Define fixes
        fixes_to_apply = {
            # Fix qualitative corrosionResistance values
            'bronze': {
                'corrosionResistance': {
                    'value': 'excellent',
                    'unit': 'qualitative',
                    'reason': 'Standardize qualitative descriptor'
                }
            },
            'cobalt': {
                'corrosionResistance': {
                    'value': 'good',
                    'unit': 'qualitative',
                    'reason': 'Standardize qualitative descriptor'
                }
            },
            
            # Fix magnitude errors in oxidationResistance
            'rubber': {
                'oxidationResistance': {
                    'value': 90.0,
                    'unit': '°C',
                    'confidence': 75,
                    'notes': 'Corrected from 9011°C (magnitude error)',
                    'reason': 'Magnitude error: 9011 → 90'
                }
            },
            'thermoplastic-elastomer': {
                'oxidationResistance': {
                    'value': 121.0,
                    'unit': '°C',
                    'confidence': 75,
                    'notes': 'Corrected from 12126°C (magnitude error)',
                    'reason': 'Magnitude error: 12126 → 121'
                }
            },
            'zirconia': {
                'oxidationResistance': {
                    'value': 1600.0,
                    'unit': '°C',
                    'confidence': 85,
                    'notes': 'Corrected from 36000°C - zirconia has excellent oxidation resistance above 1600°C',
                    'reason': 'Magnitude error or unit confusion: 36000 → 1600'
                }
            }
        }
        
        # Note: silicon tensileStrength = 7000 MPa is actually CORRECT
        # Single-crystal silicon has TS up to 7 GPa, so we'll adjust validation rules instead
        
        total_fixes = 0
        for material, material_fixes in fixes_to_apply.items():
            fixes = self.fix_material(material, material_fixes)
            total_fixes += fixes
        
        print()
        print("=" * 80)
        print(f"SUMMARY: {total_fixes} fixes applied to {len(fixes_to_apply)} materials")
        print("=" * 80)
        
        # Save fix report
        import json
        report_path = self.data_dir / "remaining_fixes_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.fixes_applied, f, indent=2)
        print(f"\n✅ Fix report saved to: {report_path}")
        
        print("\nNOTE: silicon tensileStrength = 7000 MPa is CORRECT")
        print("  Single-crystal silicon has TS up to 7 GPa")
        print("  Validation rule max should be increased to 8000 MPa")

def main():
    fixer = RemainingErrorsFixer()
    fixer.fix_all_remaining()

if __name__ == '__main__':
    main()
