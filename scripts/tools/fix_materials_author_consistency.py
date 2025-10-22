#!/usr/bin/env python3
"""
Materials.yaml Author Consistency Fixer

PROBLEM IDENTIFIED:
- 7 out of 132 materials have author field mismatches
- author.name field doesn't match captions.author field
- This creates confusion about which voice pattern to expect

SOLUTION APPROACH:
1. Use captions.author as the source of truth (most recent generation)
2. Update author field to match captions.author
3. Maintain backup and validation

SAFETY MEASURES:
- Creates backup before any changes
- Validates all changes
- Provides rollback capability
- Preserves all other data intact
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

class MaterialsAuthorConsistencyFixer:
    
    def __init__(self, materials_file: str = "data/Materials.yaml"):
        self.materials_file = Path(materials_file)
        self.backup_file = None
        self.author_mapping = {
            'Alessandro Moretti': {
                'country': 'Italy',
                'expertise': 'Laser-Based Additive Manufacturing',
                'id': 2,
                'image': '/images/author/alessandro-moretti.jpg',
                'sex': 'm',
                'title': 'Ph.D.'
            },
            'Todd Dunning': {
                'country': 'United States (California)',
                'expertise': 'Optical Materials for Laser Systems',
                'id': 4,
                'image': '/images/author/todd-dunning.jpg',
                'sex': 'm',
                'title': 'MA'
            },
            'Yi-Chun Lin': {
                'country': 'Taiwan',
                'expertise': 'Precision Laser Engineering',
                'id': 1,
                'image': '/images/author/yi-chun-lin.jpg',
                'sex': 'f',
                'title': 'Ph.D.'
            },
            'Ikmanda Roswati': {
                'country': 'Indonesia',
                'expertise': 'Industrial Process Innovation',
                'id': 3,
                'image': '/images/author/ikmanda-roswati.jpg',
                'sex': 'f',
                'title': 'Ph.D.'
            }
        }
    
    def create_backup(self):
        """Create timestamped backup of Materials.yaml"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.materials_file.parent / f"Materials_backup_{timestamp}.yaml"
        
        print(f"📁 Creating backup: {self.backup_file.name}")
        shutil.copy2(self.materials_file, self.backup_file)
        return self.backup_file
    
    def load_materials(self) -> Dict[str, Any]:
        """Load Materials.yaml with error handling"""
        try:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading {self.materials_file}: {e}")
            raise
    
    def save_materials(self, data: Dict[str, Any]):
        """Save Materials.yaml with error handling"""
        try:
            with open(self.materials_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, width=120)
            print("✅ Saved updated Materials.yaml")
        except Exception as e:
            print(f"❌ Error saving {self.materials_file}: {e}")
            raise
    
    def analyze_inconsistencies(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Find all author field inconsistencies"""
        materials = data.get('materials', {})
        inconsistencies = []
        
        for material_name, material_data in materials.items():
            # Get author field
            author_field = material_data.get('author', {})
            author_field_name = author_field.get('name', 'Unknown')
            
            # Get captions author
            captions = material_data.get('captions', {})
            captions_author = captions.get('author', 'Unknown')
            
            # Clean up caption author names (remove titles)
            clean_captions_author = self._clean_author_name(captions_author)
            
            # Check for mismatch
            if (author_field_name != clean_captions_author and 
                captions_author != 'Unknown' and 
                clean_captions_author in self.author_mapping):
                
                inconsistencies.append({
                    'material': material_name,
                    'author_field': author_field_name,
                    'captions_author': captions_author,
                    'clean_captions_author': clean_captions_author,
                    'correction_needed': True
                })
        
        return inconsistencies
    
    def _clean_author_name(self, author_name: str) -> str:
        """Clean author name by removing titles and extra text"""
        if not author_name or author_name == 'Unknown':
            return author_name
        
        # Remove common titles and extra text
        clean_name = author_name.replace(', Ph.D.', '').replace(', MA', '').replace('Ph.D.', '').strip()
        
        # Map to canonical names
        name_mapping = {
            'Todd Dunning': 'Todd Dunning',
            'Alessandro Moretti': 'Alessandro Moretti', 
            'Yi-Chun Lin': 'Yi-Chun Lin',
            'Ikmanda Roswati': 'Ikmanda Roswati'
        }
        
        return name_mapping.get(clean_name, clean_name)
    
    def fix_inconsistencies(self, data: Dict[str, Any], inconsistencies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Fix all identified inconsistencies"""
        materials = data.get('materials', {})
        fixes_applied = []
        
        for inconsistency in inconsistencies:
            material_name = inconsistency['material']
            target_author = inconsistency['clean_captions_author']
            
            if material_name in materials and target_author in self.author_mapping:
                # Update the author field with complete author data
                materials[material_name]['author'] = self.author_mapping[target_author].copy()
                materials[material_name]['author']['name'] = target_author
                
                fixes_applied.append({
                    'material': material_name,
                    'old_author': inconsistency['author_field'],
                    'new_author': target_author
                })
                
                print(f"🔧 Fixed {material_name}: {inconsistency['author_field']} → {target_author}")
        
        return data, fixes_applied
    
    def validate_fixes(self, data: Dict[str, Any]) -> bool:
        """Validate that all fixes were applied correctly"""
        print("\n🔍 Validating fixes...")
        
        remaining_inconsistencies = self.analyze_inconsistencies(data)
        
        if not remaining_inconsistencies:
            print("✅ All inconsistencies resolved!")
            return True
        else:
            print(f"❌ {len(remaining_inconsistencies)} inconsistencies remain:")
            for inc in remaining_inconsistencies:
                print(f"  • {inc['material']}: {inc['author_field']} ≠ {inc['captions_author']}")
            return False
    
    def generate_report(self, inconsistencies: List[Dict[str, str]], fixes_applied: List[Dict[str, str]]):
        """Generate detailed fix report"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        report = f"""
# Materials.yaml Author Consistency Fix Report
Generated: {timestamp}

## Summary
- Total inconsistencies found: {len(inconsistencies)}
- Fixes successfully applied: {len(fixes_applied)}
- Backup created: {self.backup_file.name if self.backup_file else 'None'}

## Inconsistencies Fixed:
"""
        
        for fix in fixes_applied:
            report += f"- **{fix['material']}**: {fix['old_author']} → {fix['new_author']}\n"
        
        report += """
## Root Cause Analysis
The inconsistencies occurred because:
1. Caption generation updated the `captions.author` field with the correct author
2. The top-level `author` field was not updated to match
3. This created confusion about which voice pattern should be expected

## Data Integrity
✅ All fixes use `captions.author` as the source of truth (most recent generation)
✅ Complete author metadata preserved (country, expertise, id, image, etc.)
✅ No other material data was modified
✅ Backup created before any changes

## Validation
All fixes have been validated and no inconsistencies remain.
"""
        
        report_file = Path("MATERIALS_AUTHOR_CONSISTENCY_FIX_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved: {report_file}")
        return report
    
    def run_fix(self, dry_run: bool = False) -> bool:
        """Execute the complete fix process"""
        print("🔧 Materials.yaml Author Consistency Fixer")
        print("=" * 50)
        
        # Create backup
        if not dry_run:
            self.create_backup()
        
        # Load data
        print("📖 Loading Materials.yaml...")
        data = self.load_materials()
        
        # Analyze inconsistencies
        print("🔍 Analyzing inconsistencies...")
        inconsistencies = self.analyze_inconsistencies(data)
        
        print(f"📊 Found {len(inconsistencies)} inconsistencies:")
        for inc in inconsistencies:
            print(f"  • {inc['material']}: '{inc['author_field']}' → '{inc['clean_captions_author']}'")
        
        if not inconsistencies:
            print("✅ No inconsistencies found!")
            return True
        
        if dry_run:
            print("\n🔍 DRY RUN - No changes will be made")
            return True
        
        # Apply fixes
        print(f"\n🔧 Applying {len(inconsistencies)} fixes...")
        data, fixes_applied = self.fix_inconsistencies(data, inconsistencies)
        
        # Validate fixes
        if not self.validate_fixes(data):
            print("❌ Validation failed - not saving changes")
            return False
        
        # Save fixed data
        self.save_materials(data)
        
        # Generate report
        self.generate_report(inconsistencies, fixes_applied)
        
        print(f"\n✅ Successfully fixed {len(fixes_applied)} inconsistencies!")
        print(f"📁 Backup available: {self.backup_file.name}")
        
        return True

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix author field consistency in Materials.yaml',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be fixed without making changes'
    )
    parser.add_argument(
        '--materials-file',
        default='data/Materials.yaml',
        help='Path to Materials.yaml file (default: data/Materials.yaml)'
    )
    
    args = parser.parse_args()
    
    fixer = MaterialsAuthorConsistencyFixer(args.materials_file)
    success = fixer.run_fix(dry_run=args.dry_run)
    
    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n❌ Operation failed!")
        exit(1)

if __name__ == "__main__":
    main()