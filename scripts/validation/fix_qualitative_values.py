#!/usr/bin/env python3
"""
Fix Qualitative Values in Numeric Properties

Converts qualitative descriptors (Low, High, Excellent) to appropriate
numeric values or removes them if they should be qualitative properties.
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
import shutil

# Qualitative to numeric conversions (temperature in °C for oxidationResistance)
QUALITATIVE_CONVERSIONS = {
    'oxidationResistance': {
        'Low': 250.0,  # Similar to aluminum
        'moderate': 500.0,
        'High': 800.0,
        'Excellent': 1000.0
    }
}

# Properties that should remain qualitative
QUALITATIVE_PROPERTIES = {
    'corrosionResistance': {
        'good': 'good',
        'Excellent': 'excellent',
        'Poor': 'poor',
        'Fair': 'fair',
        'Good': 'good'
    }
}

class QualitativeValueFixer:
    """Fix invalid qualitative values in numeric properties"""
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.frontmatter_dir = data_dir / "content" / "components" / "frontmatter"
        self.backup_dir = data_dir / "backups" / f"qualitative_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    
    def fix_material_values(self, file_path: Path, material_errors: list) -> int:
        """Fix qualitative value issues in a specific material file"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        
        fixes = 0
        material = file_path.stem.replace('-laser-cleaning', '')
        
        for error in material_errors:
            prop_name = error['property']
            invalid_value = error['value']
            
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
                        
                        # Handle oxidationResistance (should be numeric)
                        if prop_name == 'oxidationResistance' and invalid_value in QUALITATIVE_CONVERSIONS[prop_name]:
                            old_value = prop_data['value']
                            new_value = QUALITATIVE_CONVERSIONS[prop_name][invalid_value]
                            prop_data['value'] = new_value
                            prop_data['unit'] = '°C'
                            prop_data['confidence'] = 70  # Lower confidence for converted values
                            prop_data['notes'] = f"Converted from qualitative '{old_value}' to estimated numeric value"
                            
                            fixes += 1
                            fixed = True
                            self.fixes_applied.append({
                                'material': material,
                                'property': prop_name,
                                'old_value': old_value,
                                'new_value': new_value,
                                'conversion': 'qualitative_to_numeric'
                            })
                        
                        # Handle corrosionResistance (should remain qualitative)
                        elif prop_name == 'corrosionResistance':
                            old_value = prop_data['value']
                            new_value = QUALITATIVE_PROPERTIES[prop_name].get(invalid_value, invalid_value.lower())
                            prop_data['value'] = new_value
                            prop_data['unit'] = 'qualitative'
                            
                            fixes += 1
                            fixed = True
                            self.fixes_applied.append({
                                'material': material,
                                'property': prop_name,
                                'old_value': old_value,
                                'new_value': new_value,
                                'conversion': 'qualitative_standardization'
                            })
                        
                        if fixed:
                            break
            
            if not fixed:
                print(f"  ⚠️  Could not fix {material}.{prop_name}: {invalid_value}")
        
        if fixes > 0:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        return fixes
    
    def fix_all_values(self):
        """Fix all qualitative value issues"""
        print("=" * 80)
        print("QUALITATIVE VALUE FIXER")
        print("=" * 80)
        print()
        
        # Load validation report
        report = self.load_validation_report()
        value_errors = [e for e in report['ERROR'] if e['type'] == 'invalid_value']
        
        print(f"Found {len(value_errors)} invalid value errors\n")
        
        # Group errors by material
        errors_by_material = {}
        for error in value_errors:
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
            
            fixes = self.fix_material_values(file_path, errors)
            if fixes > 0:
                print(f"✅ {material}: {fixes} values fixed")
                total_fixes += fixes
        
        print()
        print("=" * 80)
        print(f"SUMMARY: {total_fixes} value fixes applied to {len(errors_by_material)} materials")
        print("=" * 80)
        
        # Save fix report
        report_path = self.data_dir / "qualitative_fixes_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.fixes_applied, f, indent=2)
        print(f"\n✅ Fix report saved to: {report_path}")

def main():
    fixer = QualitativeValueFixer()
    fixer.fix_all_values()

if __name__ == '__main__':
    main()
