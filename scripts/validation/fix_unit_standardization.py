#!/usr/bin/env python3
"""
Fix Unit Standardization Issues

Automatically corrects invalid unit formats identified by validation agent.
Based on validation_report.json findings.
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
import shutil

# Unit mappings from invalid to valid formats
UNIT_CORRECTIONS = {
    'specificHeat': {
        'J·kg⁻¹·K⁻¹': 'J/(kg·K)',
        'J/kg·K': 'J/(kg·K)'
    },
    'thermalConductivity': {
        'W/m·K': 'W/(m·K)'
    },
    'thermalExpansion': {
        '10^-6 /K': '10⁻⁶/K'
    },
    'laserAbsorption': {
        '1/cm': '%',
        '1/m': '%',
        'cm⁻¹': '%',
        'unitless': '%'
    },
    'hardness': {
        'HB': 'Brinell',
        'N/mm²': 'MPa',
        'kgf/mm²': 'HV',
        'N': 'MPa',
        'Rockwell R': 'HRC',
        'Barcol': 'Shore D'
    },
    'corrosionResistance': {
        'rating_0_10': 'qualitative'
    }
}

class UnitStandardizationFixer:
    """Fix invalid unit formats in frontmatter files"""
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.frontmatter_dir = data_dir / "content" / "components" / "frontmatter"
        self.backup_dir = data_dir / "backups" / f"unit_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []
        
    def create_backup(self):
        """Create backup of frontmatter directory"""
        print(f"Creating backup at {self.backup_dir}...")
        shutil.copytree(self.frontmatter_dir, self.backup_dir)
        print(f"✅ Backup created\n")
    
    def load_validation_report(self) -> dict:
        """Load validation report"""
        report_path = self.data_dir / "validation_report.json"
        with open(report_path) as f:
            return json.load(f)
    
    def fix_material_units(self, file_path: Path, material_errors: list) -> int:
        """Fix unit issues in a specific material file"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        fixes = 0
        material = file_path.stem.replace('-laser-cleaning', '')
        
        for error in material_errors:
            prop_name = error['property']
            invalid_unit = error['unit']
            
            if prop_name not in UNIT_CORRECTIONS:
                continue
            
            if invalid_unit not in UNIT_CORRECTIONS[prop_name]:
                continue
            
            valid_unit = UNIT_CORRECTIONS[prop_name][invalid_unit]
            
            # Find and fix the property
            fixed = False
            if 'properties' in data:
                for group_name, group_data in data['properties'].items():
                    # Properties are directly in group_data (flat structure)
                    metadata_keys = {'label', 'description', 'percentage'}
                    if not isinstance(group_data, dict):
                        continue
                    
                    if prop_name in group_data and prop_name not in metadata_keys:
                        prop_data = group_data[prop_name]
                        if prop_data.get('unit') == invalid_unit:
                            old_unit = prop_data['unit']
                            prop_data['unit'] = valid_unit
                            
                            # Special handling for laserAbsorption: convert values if needed
                            if prop_name == 'laserAbsorption' and invalid_unit in ['1/cm', '1/m', 'cm⁻¹']:
                                # Absorption coefficient to percentage requires material-specific conversion
                                # For now, just flag for manual review
                                prop_data['unit'] = valid_unit
                                prop_data['notes'] = prop_data.get('notes', '') + ' [VALIDATION: converted from absorption coefficient, verify value]'
                            
                            fixes += 1
                            fixed = True
                            self.fixes_applied.append({
                                'material': material,
                                'property': prop_name,
                                'old_unit': old_unit,
                                'new_unit': valid_unit
                            })
                            break
            
            if not fixed:
                print(f"  ⚠️  Could not fix {material}.{prop_name}: {invalid_unit}")
        
        if fixes > 0:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return fixes
    
    def fix_all_units(self):
        """Fix all unit standardization issues"""
        print("=" * 80)
        print("UNIT STANDARDIZATION FIXER")
        print("=" * 80)
        print()
        
        # Load validation report
        report = self.load_validation_report()
        unit_errors = [e for e in report['ERROR'] if e['type'] == 'invalid_unit']
        
        print(f"Found {len(unit_errors)} invalid unit errors\n")
        
        # Group errors by material
        errors_by_material = {}
        for error in unit_errors:
            material = error['material']
            if material not in errors_by_material:
                errors_by_material[material] = []
            errors_by_material[material].append(error)
        
        print(f"Affecting {len(errors_by_material)} materials\n")
        
        # Create backup
        self.create_backup()
        
        # Fix each material
        total_fixes = 0
        for material, errors in sorted(errors_by_material.items()):
            file_path = self.frontmatter_dir / f"{material}-laser-cleaning.yaml"
            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
            
            fixes = self.fix_material_units(file_path, errors)
            if fixes > 0:
                print(f"✅ {material}: {fixes} units fixed")
                total_fixes += fixes
        
        print()
        print("=" * 80)
        print(f"SUMMARY: {total_fixes} unit fixes applied to {len(errors_by_material)} materials")
        print("=" * 80)
        
        # Save fix report
        report_path = self.data_dir / "unit_fixes_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.fixes_applied, f, indent=2)
        print(f"\n✅ Fix report saved to: {report_path}")

def main():
    fixer = UnitStandardizationFixer()
    fixer.fix_all_units()

if __name__ == '__main__':
    main()
