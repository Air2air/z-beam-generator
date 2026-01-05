#!/usr/bin/env python3
"""
Add Entity ID Suffixes Migration

Ensures all entity IDs have their domain-specific suffixes:
- Materials: {slug}-laser-cleaning (already done)
- Contaminants: {slug}-contamination (already done)
- Compounds: {slug}-compound (needs to be added)
- Settings: {slug}-settings (needs to be added)

Also updates all relationship references to use the new IDs.

Usage:
    python3 scripts/migration/add_entity_id_suffixes.py
    python3 scripts/migration/add_entity_id_suffixes.py --dry-run
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict

# Domain configurations
DOMAINS = {
    'materials': {
        'file': Path('data/materials/Materials.yaml'),
        'key': 'materials',
        'suffix': '-laser-cleaning',
        'needs_migration': False,  # Already has suffix
    },
    'compounds': {
        'file': Path('data/compounds/Compounds.yaml'),
        'key': 'compounds',
        'suffix': '-compound',
        'needs_migration': True,
    },
    'contaminants': {
        'file': Path('data/contaminants/Contaminants.yaml'),
        'key': 'contamination_patterns',
        'suffix': '-contamination',
        'needs_migration': False,  # Already has suffix
    },
    'settings': {
        'file': Path('data/settings/Settings.yaml'),
        'key': 'settings',
        'suffix': '-settings',
        'needs_migration': True,
    },
}


class EntityIDSuffixMigrator:
    """Migrates entity IDs to include domain-specific suffixes."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.id_mappings: Dict[str, str] = {}  # old_id -> new_id
        self.stats = defaultdict(int)
    
    def add_suffix_to_entity_ids(self, domain_name: str) -> Dict[str, Any]:
        """
        Add suffix to all entity IDs in a domain.
        
        Returns:
            Updated domain data with new IDs
        """
        domain_config = DOMAINS[domain_name]
        
        if not domain_config['needs_migration']:
            print(f"   ✓ {domain_name}: Already has suffix, skipping")
            return None
        
        file_path = domain_config['file']
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        entities = data[domain_config['key']]
        suffix = domain_config['suffix']
        
        # Create new dict with updated IDs
        updated_entities = {}
        
        for old_id, entity_data in entities.items():
            # Check if already has suffix
            if old_id.endswith(suffix):
                updated_entities[old_id] = entity_data
                continue
            
            # Add suffix
            new_id = f"{old_id}{suffix}"
            updated_entities[new_id] = entity_data
            
            # Track mapping
            self.id_mappings[old_id] = new_id
            self.stats[f'{domain_name}_renamed'] += 1
            
            print(f"   • {old_id} → {new_id}")
        
        # Update the data structure
        data[domain_config['key']] = updated_entities
        
        return data
    
    def update_relationship_references(self, domain_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update all relationship item IDs to use new suffixed IDs.
        
        Args:
            domain_name: Domain being updated
            data: Domain data dict
        
        Returns:
            Updated data with fixed relationship references
        """
        domain_config = DOMAINS[domain_name]
        entities = data[domain_config['key']]
        
        updated_count = 0
        
        for entity_id, entity_data in entities.items():
            if 'relationships' not in entity_data:
                continue
            
            relationships = entity_data['relationships']
            
            for rel_name, rel_data in relationships.items():
                if not isinstance(rel_data, dict) or 'items' not in rel_data:
                    continue
                
                items = rel_data['items']
                if not isinstance(items, list):
                    continue
                
                for item in items:
                    if not isinstance(item, dict) or 'id' not in item:
                        continue
                    
                    old_ref_id = item['id']
                    
                    # Check if this ID was renamed
                    if old_ref_id in self.id_mappings:
                        new_ref_id = self.id_mappings[old_ref_id]
                        item['id'] = new_ref_id
                        updated_count += 1
                        self.stats[f'{domain_name}_refs_updated'] += 1
        
        if updated_count > 0:
            print(f"   • Updated {updated_count} relationship references")
        
        return data
    
    def migrate_all(self):
        """Execute full migration."""
        print("=" * 70)
        print("ENTITY ID SUFFIX MIGRATION")
        print("=" * 70)
        
        if self.dry_run:
            print("\n🔍 DRY-RUN MODE (no files will be modified)\n")
        
        # Phase 1: Rename entity IDs and track mappings
        print("\n📝 PHASE 1: Adding suffixes to entity IDs...\n")
        
        updated_data = {}
        for domain_name in DOMAINS.keys():
            print(f"🔄 Processing {domain_name}:")
            data = self.add_suffix_to_entity_ids(domain_name)
            if data:
                updated_data[domain_name] = data
        
        # Phase 2: Update all relationship references
        print("\n🔗 PHASE 2: Updating relationship references...\n")
        
        # Need to update ALL domains (even those not renamed) because they might reference renamed entities
        for domain_name in DOMAINS.keys():
            domain_config = DOMAINS[domain_name]
            
            # Load current data if not already loaded
            if domain_name not in updated_data:
                with open(domain_config['file'], 'r', encoding='utf-8') as f:
                    updated_data[domain_name] = yaml.safe_load(f)
            
            print(f"🔄 Updating references in {domain_name}:")
            updated_data[domain_name] = self.update_relationship_references(
                domain_name,
                updated_data[domain_name]
            )
        
        # Phase 3: Write updated files
        if not self.dry_run:
            print("\n💾 PHASE 3: Writing updated files...\n")
            
            for domain_name, data in updated_data.items():
                domain_config = DOMAINS[domain_name]
                file_path = domain_config['file']
                
                print(f"✍️  Writing {file_path}...")
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print migration summary."""
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        
        print(f"\n📊 ID Mappings Created: {len(self.id_mappings)}")
        
        if self.id_mappings:
            print("\n🔄 Entities Renamed:")
            for domain in ['compounds', 'settings']:
                renamed = self.stats.get(f'{domain}_renamed', 0)
                if renamed > 0:
                    print(f"   • {domain}: {renamed}")
        
        print("\n🔗 Relationship References Updated:")
        total_refs = 0
        for domain in DOMAINS.keys():
            refs = self.stats.get(f'{domain}_refs_updated', 0)
            if refs > 0:
                print(f"   • {domain}: {refs}")
                total_refs += refs
        print(f"   TOTAL: {total_refs}")
        
        if self.dry_run:
            print("\n🔍 DRY-RUN: No files were modified")
        else:
            print("\n✅ Migration complete! All files updated.")
        
        print("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add entity ID suffixes and update references')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    args = parser.parse_args()
    
    migrator = EntityIDSuffixMigrator(dry_run=args.dry_run)
    migrator.migrate_all()


if __name__ == '__main__':
    main()
