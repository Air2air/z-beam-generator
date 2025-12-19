#!/usr/bin/env python3
"""
Automated Link Repair Tool

Detects and repairs broken references across all data files.
Works in conjunction with verify_data_integrity.py validator.

Usage:
    python3 scripts/validation/repair_broken_links.py [--dry-run] [--domain DOMAIN]

Features:
    - Removes references to non-existent items
    - Adds missing suffixes (e.g., -contamination)
    - Reports all repairs with details
    - Creates backups before modifying files
    - Can target specific domain or repair all
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class RepairAction:
    """Represents a single repair action"""
    file: str
    item_id: str
    relationship_type: str
    reference_id: str
    action: str  # 'remove', 'add_suffix', 'fix_url'
    old_value: str
    new_value: str

@dataclass
class RepairStats:
    """Track repair statistics"""
    files_checked: int = 0
    files_modified: int = 0
    references_removed: int = 0
    references_fixed: int = 0
    backups_created: int = 0
    actions: List[RepairAction] = field(default_factory=list)

class LinkRepairer:
    """Repairs broken references in data files"""
    
    DATA_FILES = {
        'materials': 'data/materials/Materials.yaml',
        'contaminants': 'data/contaminants/contaminants.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'settings': 'data/settings/Settings.yaml',
    }
    
    RELATIONSHIP_FIELDS = {
        'materials': ['related_contaminants', 'related_compounds', 'related_settings'],
        'contaminants': ['related_materials', 'produces_compounds', 'recommended_settings'],
        'compounds': ['produced_by_contaminants', 'related_materials'],
        'settings': ['suitable_materials', 'effective_contaminants'],
    }
    
    # Map relationship field to target domain
    FIELD_TO_DOMAIN = {
        'related_contaminants': 'contaminants',
        'related_compounds': 'compounds',
        'related_settings': 'settings',
        'related_materials': 'materials',
        'produces_compounds': 'compounds',
        'produced_by_contaminants': 'contaminants',
        'recommended_settings': 'settings',
        'suitable_materials': 'materials',
        'effective_contaminants': 'contaminants',
    }
    
    def __init__(self, project_root: Path, dry_run: bool = False, target_domain: str = None):
        self.project_root = project_root
        self.dry_run = dry_run
        self.target_domain = target_domain
        self.stats = RepairStats()
        self.index = self._build_index()
    
    def _build_index(self) -> Dict[str, Set[str]]:
        """Build index of all valid IDs in each domain"""
        print("\n🔍 Building index of valid IDs...")
        index = defaultdict(set)
        
        for domain, file_path in self.DATA_FILES.items():
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r') as f:
                    content = yaml.safe_load(f)
                
                # Handle different YAML structures
                if domain == 'materials' and 'materials' in content:
                    items = content['materials']
                elif domain == 'contaminants' and 'contamination_patterns' in content:
                    items = content['contamination_patterns']
                elif domain == 'compounds' and 'compounds' in content:
                    items = content['compounds']
                elif domain == 'settings' and 'settings' in content:
                    items = content['settings']
                else:
                    items = content
                
                if isinstance(items, dict):
                    index[domain] = set(items.keys())
                
                print(f"   ✅ {domain}: {len(index[domain])} items")
                
            except Exception as e:
                print(f"   ❌ Error loading {domain}: {e}")
        
        return index
    
    def _try_fix_reference(self, ref_id: str, target_domain: str) -> Tuple[bool, str, str]:
        """
        Try to fix a broken reference
        
        Returns: (success, action, fixed_id)
        """
        # Check if already valid
        if ref_id in self.index[target_domain]:
            return (True, 'valid', ref_id)
        
        # Try adding -contamination suffix for contaminants
        if target_domain == 'contaminants' and not ref_id.endswith('-contamination'):
            candidate = f"{ref_id}-contamination"
            if candidate in self.index[target_domain]:
                return (True, 'add_suffix', candidate)
        
        # Try removing -contamination suffix
        if target_domain == 'contaminants' and ref_id.endswith('-contamination'):
            candidate = ref_id.replace('-contamination', '')
            if candidate in self.index[target_domain]:
                return (True, 'remove_suffix', candidate)
        
        # No fix found
        return (False, 'remove', ref_id)
    
    def _repair_references(self, domain: str, items: Dict) -> List[RepairAction]:
        """Repair references in a domain's items"""
        actions = []
        
        if not isinstance(items, dict):
            return actions
        
        for item_id, item_data in items.items():
            if not isinstance(item_data, dict):
                continue
            
            if 'relationships' not in item_data:
                continue
            
            relationships = item_data['relationships']
            
            for rel_field in self.RELATIONSHIP_FIELDS.get(domain, []):
                if rel_field not in relationships:
                    continue
                
                target_domain = self.FIELD_TO_DOMAIN.get(rel_field)
                if not target_domain:
                    continue
                
                refs = relationships[rel_field]
                if not isinstance(refs, list):
                    continue
                
                # Process references
                refs_to_remove = []
                
                for i, ref in enumerate(refs):
                    if not isinstance(ref, dict) or 'id' not in ref:
                        continue
                    
                    ref_id = ref['id']
                    success, action_type, fixed_id = self._try_fix_reference(ref_id, target_domain)
                    
                    if not success:
                        # Mark for removal
                        refs_to_remove.append(i)
                        actions.append(RepairAction(
                            file=self.DATA_FILES[domain],
                            item_id=item_id,
                            relationship_type=rel_field,
                            reference_id=ref_id,
                            action='remove',
                            old_value=ref_id,
                            new_value='<removed>'
                        ))
                    elif action_type in ['add_suffix', 'remove_suffix']:
                        # Fix the ID
                        ref['id'] = fixed_id
                        actions.append(RepairAction(
                            file=self.DATA_FILES[domain],
                            item_id=item_id,
                            relationship_type=rel_field,
                            reference_id=ref_id,
                            action=action_type,
                            old_value=ref_id,
                            new_value=fixed_id
                        ))
                
                # Remove broken references (in reverse order to maintain indices)
                for i in reversed(refs_to_remove):
                    del refs[i]
        
        return actions
    
    def repair_all(self) -> RepairStats:
        """Repair all data files"""
        print(f"\n{'='*80}")
        print(f"🔧 AUTOMATED LINK REPAIR")
        print(f"{'='*80}")
        print(f"Mode: {'DRY RUN (no changes will be saved)' if self.dry_run else 'LIVE (files will be modified)'}")
        if self.target_domain:
            print(f"Target: {self.target_domain} domain only")
        else:
            print(f"Target: All domains")
        print(f"{'='*80}\n")
        
        domains_to_repair = [self.target_domain] if self.target_domain else self.DATA_FILES.keys()
        
        for domain in domains_to_repair:
            if domain not in self.DATA_FILES:
                print(f"⚠️  Unknown domain: {domain}")
                continue
            
            self._repair_file(domain, self.DATA_FILES[domain])
        
        # Print detailed actions
        if self.stats.actions:
            print(f"\n{'='*80}")
            print(f"📋 REPAIR ACTIONS")
            print(f"{'='*80}")
            
            for action in self.stats.actions[:20]:  # Show first 20
                print(f"   {action.action.upper()}: {action.item_id} → {action.relationship_type}")
                print(f"      {action.old_value} → {action.new_value}")
            
            if len(self.stats.actions) > 20:
                print(f"   ... and {len(self.stats.actions) - 20} more")
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"📊 REPAIR SUMMARY")
        print(f"{'='*80}")
        print(f"Files Checked: {self.stats.files_checked}")
        print(f"Files Modified: {self.stats.files_modified}")
        print(f"References Removed: {self.stats.references_removed}")
        print(f"References Fixed: {self.stats.references_fixed}")
        print(f"Backups Created: {self.stats.backups_created}")
        print(f"{'='*80}\n")
        
        if self.dry_run:
            print("⚠️  DRY RUN - No files were actually modified")
            print("   Run without --dry-run to apply changes")
        elif self.stats.files_modified > 0:
            print("✅ Repairs complete! Run validation to verify:")
            print("   python3 scripts/validation/verify_data_integrity.py")
        else:
            print("✅ No repairs needed - all references already valid")
        
        return self.stats
    
    def _repair_file(self, domain: str, file_path: str):
        """Repair a single data file"""
        full_path = self.project_root / file_path
        self.stats.files_checked += 1
        
        print(f"\n📂 Repairing {domain}: {file_path}")
        
        if not full_path.exists():
            print(f"   ⚠️  File not found")
            return
        
        try:
            # Load file
            with open(full_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Get items based on domain structure
            if domain == 'materials' and 'materials' in data:
                items = data['materials']
            elif domain == 'contaminants' and 'contamination_patterns' in data:
                items = data['contamination_patterns']
            elif domain == 'compounds' and 'compounds' in data:
                items = data['compounds']
            elif domain == 'settings' and 'settings' in data:
                items = data['settings']
            else:
                print(f"   ⚠️  No expected key found in file")
                return
            
            # Repair references
            actions = self._repair_references(domain, items)
            
            if actions:
                self.stats.files_modified += 1
                self.stats.actions.extend(actions)
                
                # Count by type
                removed = sum(1 for a in actions if a.action == 'remove')
                fixed = sum(1 for a in actions if a.action != 'remove')
                self.stats.references_removed += removed
                self.stats.references_fixed += fixed
                
                if not self.dry_run:
                    # Create backup
                    backup_path = full_path.parent / f"{full_path.name}.backup"
                    with open(backup_path, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                                sort_keys=False, width=1000)
                    self.stats.backups_created += 1
                    print(f"   💾 Backup saved: {backup_path.name}")
                    
                    # Save repaired version
                    with open(full_path, 'w') as f:
                        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                                sort_keys=False, width=1000)
                    print(f"   ✅ Removed: {removed}, Fixed: {fixed}")
                else:
                    print(f"   🔍 Would remove {removed}, fix {fixed} (dry run)")
            else:
                print(f"   ✅ No repairs needed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatically repair broken links in data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (show what would be fixed):
  python3 scripts/validation/repair_broken_links.py --dry-run
  
  # Repair all domains:
  python3 scripts/validation/repair_broken_links.py
  
  # Repair specific domain only:
  python3 scripts/validation/repair_broken_links.py --domain materials
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be fixed without making changes')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                       help='Only repair specific domain')
    
    args = parser.parse_args()
    
    # Find project root
    project_root = Path(__file__).parent.parent.parent
    
    # Run repair
    repairer = LinkRepairer(project_root, dry_run=args.dry_run, target_domain=args.domain)
    stats = repairer.repair_all()
    
    # Exit with error if repairs were needed but not applied
    if args.dry_run and (stats.references_removed > 0 or stats.references_fixed > 0):
        sys.exit(1)
    
    sys.exit(0)

if __name__ == '__main__':
    main()
