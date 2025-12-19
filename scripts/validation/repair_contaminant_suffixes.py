#!/usr/bin/env python3
"""
Repair Contaminant Suffix References

Ensures all contaminant references across all data files use the correct
'-contamination' suffix to match how they're stored in contaminants.yaml.

Usage:
    python3 scripts/validation/repair_contaminant_suffixes.py [--dry-run]
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RepairStats:
    """Track repair statistics"""
    files_checked: int = 0
    files_modified: int = 0
    references_fixed: int = 0
    backups_created: int = 0

class ContaminantSuffixRepairer:
    """Repairs contaminant references to include proper suffix"""
    
    # Files that may contain contaminant references
    DATA_FILES = {
        'materials': 'data/materials/Materials.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'settings': 'data/settings/Settings.yaml',
    }
    
    # Relationship fields that reference contaminants
    CONTAMINANT_FIELDS = {
        'materials': ['related_contaminants'],
        'compounds': ['produced_by_contaminants'],
        'settings': ['effective_contaminants'],
    }
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.stats = RepairStats()
        self.contaminant_ids = self._load_contaminant_ids()
    
    def _load_contaminant_ids(self) -> set:
        """Load all valid contaminant IDs from contaminants.yaml"""
        contaminants_path = self.project_root / 'data/contaminants/contaminants.yaml'
        
        if not contaminants_path.exists():
            print(f"❌ Contaminants file not found: {contaminants_path}")
            return set()
        
        try:
            with open(contaminants_path, 'r') as f:
                data = yaml.safe_load(f)
            
            patterns = data.get('contamination_patterns', {})
            ids = set(patterns.keys())
            
            print(f"✅ Loaded {len(ids)} contaminant IDs from source")
            return ids
            
        except Exception as e:
            print(f"❌ Error loading contaminants: {e}")
            return set()
    
    def _fix_contaminant_references(self, items: Dict, domain: str) -> int:
        """Fix contaminant references in a domain's items"""
        fixed_count = 0
        
        if not isinstance(items, dict):
            return 0
        
        for item_id, item_data in items.items():
            if not isinstance(item_data, dict):
                continue
            
            if 'relationships' not in item_data:
                continue
            
            relationships = item_data['relationships']
            
            # Check each field that might contain contaminant references
            for field in self.CONTAMINANT_FIELDS.get(domain, []):
                if field not in relationships:
                    continue
                
                contaminants = relationships[field]
                if not isinstance(contaminants, list):
                    continue
                
                for cont_ref in contaminants:
                    if not isinstance(cont_ref, dict) or 'id' not in cont_ref:
                        continue
                    
                    original_id = cont_ref['id']
                    
                    # Skip if already has suffix
                    if original_id.endswith('-contamination'):
                        continue
                    
                    # Check if adding suffix creates a valid ID
                    new_id = f"{original_id}-contamination"
                    
                    if new_id in self.contaminant_ids:
                        cont_ref['id'] = new_id
                        fixed_count += 1
                        if not self.dry_run:
                            print(f"   Fixed: {item_id} → {field} → {original_id} → {new_id}")
        
        return fixed_count
    
    def repair_all(self) -> RepairStats:
        """Repair all data files"""
        print(f"\n{'='*80}")
        print(f"🔧 CONTAMINANT SUFFIX REPAIR")
        print(f"{'='*80}")
        print(f"Mode: {'DRY RUN (no changes will be saved)' if self.dry_run else 'LIVE (files will be modified)'}")
        print(f"{'='*80}\n")
        
        for domain, file_path in self.DATA_FILES.items():
            self._repair_file(domain, file_path)
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 REPAIR SUMMARY")
        print(f"{'='*80}")
        print(f"Files Checked: {self.stats.files_checked}")
        print(f"Files Modified: {self.stats.files_modified}")
        print(f"References Fixed: {self.stats.references_fixed}")
        print(f"Backups Created: {self.stats.backups_created}")
        print(f"{'='*80}\n")
        
        if self.dry_run:
            print("⚠️  DRY RUN - No files were actually modified")
            print("   Run without --dry-run to apply changes")
        elif self.stats.references_fixed > 0:
            print("✅ Repairs complete! Run validation to verify:")
            print("   python3 scripts/validation/verify_data_integrity.py")
        else:
            print("✅ No repairs needed - all references already correct")
        
        return self.stats
    
    def _repair_file(self, domain: str, file_path: str):
        """Repair a single data file"""
        full_path = self.project_root / file_path
        self.stats.files_checked += 1
        
        print(f"\n📂 Checking {domain}: {file_path}")
        
        if not full_path.exists():
            print(f"   ⚠️  File not found")
            return
        
        try:
            # Load file
            with open(full_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Get items based on domain structure
            if domain in data:
                items = data[domain]
            else:
                print(f"   ⚠️  No '{domain}' key found in file")
                return
            
            # Fix references
            fixed_count = self._fix_contaminant_references(items, domain)
            
            if fixed_count > 0:
                self.stats.files_modified += 1
                self.stats.references_fixed += fixed_count
                
                if not self.dry_run:
                    # Create backup
                    backup_path = full_path.parent / f"{full_path.name}.backup"
                    with open(backup_path, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                                sort_keys=False, width=1000)
                    self.stats.backups_created += 1
                    print(f"   💾 Backup saved: {backup_path}")
                    
                    # Save fixed version
                    with open(full_path, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                                sort_keys=False, width=1000)
                    print(f"   ✅ Fixed {fixed_count} references")
                else:
                    print(f"   🔍 Would fix {fixed_count} references (dry run)")
            else:
                print(f"   ✅ No repairs needed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Repair contaminant suffix references in data files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be fixed without making changes')
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent.parent
    
    # Run repair
    repairer = ContaminantSuffixRepairer(project_root, dry_run=args.dry_run)
    stats = repairer.repair_all()
    
    # Exit with error if repairs were needed but not applied
    if args.dry_run and stats.references_fixed > 0:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
