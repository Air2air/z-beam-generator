#!/usr/bin/env python3
"""
Frontmatter Structure Fixes for Z-Beam
Addresses: Naming consistency, denormalization, deprecated fields, type safety

Date: January 8, 2026
Based on: docs/FRONTMATTER_FIXES_REQUIRED.md
"""

import yaml
import glob
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class FrontmatterFixer:
    """Fix frontmatter structure issues across all domains"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.contaminant_cache: Dict[str, Any] = {}
        self.compound_cache: Dict[str, Any] = {}
        self.stats = {
            'files_processed': 0,
            'naming_fixed': 0,
            'denormalized': 0,
            'metadata_removed': 0,
            'type_fixed': 0,
            'errors': 0
        }
    
    def load_contaminant(self, contaminant_id: str) -> Optional[Dict[str, Any]]:
        """Load contaminant data with caching"""
        if contaminant_id not in self.contaminant_cache:
            # Load from source data
            contaminant_path = Path(f'data/contaminants/Contaminants.yaml')
            if not contaminant_path.exists():
                print(f"  ⚠️  Contaminants file not found")
                return None
            
            with open(contaminant_path) as f:
                all_contaminants = yaml.safe_load(f)
                if 'contaminants' in all_contaminants and contaminant_id in all_contaminants['contaminants']:
                    self.contaminant_cache[contaminant_id] = all_contaminants['contaminants'][contaminant_id]
                else:
                    print(f"  ⚠️  Contaminant not found: {contaminant_id}")
                    return None
        
        return self.contaminant_cache[contaminant_id]
    
    def load_compound(self, compound_id: str) -> Optional[Dict[str, Any]]:
        """Load compound data with caching"""
        if compound_id not in self.compound_cache:
            # Load from source data
            compound_path = Path(f'data/compounds/Compounds.yaml')
            if not compound_path.exists():
                print(f"  ⚠️  Compounds file not found")
                return None
            
            with open(compound_path) as f:
                all_compounds = yaml.safe_load(f)
                if 'compounds' in all_compounds and compound_id in all_compounds['compounds']:
                    self.compound_cache[compound_id] = all_compounds['compounds'][compound_id]
                else:
                    print(f"  ⚠️  Compound not found: {compound_id}")
                    return None
        
        return self.compound_cache[compound_id]
    
    def fix_naming_consistency(self, data: Dict[str, Any]) -> bool:
        """Convert snake_case relationship keys to camelCase"""
        if 'relationships' not in data:
            return False
        
        fixed = False
        
        for category_name, category in data['relationships'].items():
            if not isinstance(category, dict):
                continue
            
            # Map of snake_case → camelCase
            naming_fixes = {
                'regulatory_standards': 'regulatoryStandards',
                'contaminated_by': 'contaminatedBy',
                'removed_by': 'removedBy',
                'industry_applications': 'industryApplications',
                'material_pairings': 'materialPairings',
                'compound_interactions': 'compoundInteractions',
                'safety_protocols': 'safetyProtocols',
                'environmental_impacts': 'environmentalImpacts'
            }
            
            for old_key, new_key in naming_fixes.items():
                if old_key in category:
                    category[new_key] = category.pop(old_key)
                    fixed = True
        
        return fixed
    
    def denormalize_contaminants(self, data: Dict[str, Any]) -> bool:
        """Add complete display data to contaminant references"""
        if 'relationships' not in data:
            return False
        
        fixed = False
        
        # Check contaminatedBy relationship
        contaminated_by = data['relationships'].get('interactions', {}).get('contaminatedBy')
        if contaminated_by and isinstance(contaminated_by, dict):
            items = contaminated_by.get('items', [])
            if not isinstance(items, list):
                # Fix type issue
                contaminated_by['items'] = []
                items = []
                fixed = True
            
            for item in items:
                if not isinstance(item, dict) or 'id' not in item:
                    continue
                
                contaminant_id = item['id']
                
                # Skip if already denormalized
                if 'name' in item and 'url' in item:
                    continue
                
                # Load contaminant data
                contaminant = self.load_contaminant(contaminant_id)
                if not contaminant:
                    continue
                
                # Extract display data
                category = contaminant.get('category', '')
                subcategory = contaminant.get('subcategory', '')
                
                # Get image URL
                image_url = ''
                if 'images' in contaminant and isinstance(contaminant['images'], dict):
                    hero = contaminant['images'].get('hero', {})
                    if isinstance(hero, dict):
                        image_url = hero.get('url', '')
                
                # Get description
                description = contaminant.get('pageDescription', '')
                if not description and 'card' in contaminant:
                    card = contaminant.get('card', {})
                    if isinstance(card, dict):
                        description = card.get('description', '')
                
                # Truncate description
                if description and len(description) > 200:
                    description = description[:197] + '...'
                
                # Enrich item with display data
                item.update({
                    'name': contaminant.get('name', ''),
                    'category': category,
                    'subcategory': subcategory,
                    'url': f"/contaminants/{category}/{subcategory}/{contaminant_id}",
                    'image': image_url,
                    'description': description
                })
                
                # Preserve frequency and severity if they exist
                if 'frequency' not in item:
                    item['frequency'] = 'moderate'
                if 'severity' not in item:
                    item['severity'] = 'moderate'
                
                fixed = True
        
        return fixed
    
    def denormalize_compounds(self, data: Dict[str, Any]) -> bool:
        """Add complete display data to compound references"""
        if 'relationships' not in data:
            return False
        
        fixed = False
        
        # Check compoundInteractions relationship
        compound_interactions = data['relationships'].get('interactions', {}).get('compoundInteractions')
        if compound_interactions and isinstance(compound_interactions, dict):
            items = compound_interactions.get('items', [])
            if not isinstance(items, list):
                # Fix type issue
                compound_interactions['items'] = []
                items = []
                fixed = True
            
            for item in items:
                if not isinstance(item, dict) or 'id' not in item:
                    continue
                
                compound_id = item['id']
                
                # Skip if already denormalized
                if 'name' in item and 'url' in item:
                    continue
                
                # Load compound data
                compound = self.load_compound(compound_id)
                if not compound:
                    continue
                
                # Extract display data
                category = compound.get('category', '')
                
                # Get image URL
                image_url = ''
                if 'images' in compound and isinstance(compound['images'], dict):
                    hero = compound['images'].get('hero', {})
                    if isinstance(hero, dict):
                        image_url = hero.get('url', '')
                
                # Get description
                description = compound.get('pageDescription', '')
                if not description and 'card' in compound:
                    card = compound.get('card', {})
                    if isinstance(card, dict):
                        description = card.get('description', '')
                
                # Truncate description
                if description and len(description) > 200:
                    description = description[:197] + '...'
                
                # Enrich item with display data
                item.update({
                    'name': compound.get('name', ''),
                    'category': category,
                    'url': f"/compounds/{category}/{compound_id}",
                    'image': image_url,
                    'description': description
                })
                
                fixed = True
        
        return fixed
    
    def remove_metadata_wrapper(self, data: Dict[str, Any]) -> bool:
        """Remove deprecated metadata wrapper"""
        if 'metadata' in data:
            del data['metadata']
            return True
        return False
    
    def ensure_type_safety(self, data: Dict[str, Any]) -> bool:
        """Ensure all relationship sections have items as arrays"""
        if 'relationships' not in data:
            return False
        
        fixed = False
        
        for category in data['relationships'].values():
            if not isinstance(category, dict):
                continue
            
            for section_name, section_data in category.items():
                # If section is not a dict, wrap it
                if not isinstance(section_data, dict):
                    category[section_name] = {
                        'items': [] if section_data is None else [section_data],
                        'presentation': 'card'
                    }
                    fixed = True
                    continue
                
                # Ensure items exists and is an array
                if 'items' not in section_data:
                    section_data['items'] = []
                    fixed = True
                elif not isinstance(section_data['items'], list):
                    # Convert to array
                    section_data['items'] = [section_data['items']] if section_data['items'] else []
                    fixed = True
                
                # Ensure presentation exists
                if 'presentation' not in section_data:
                    section_data['presentation'] = 'card'
                    fixed = True
        
        return fixed
    
    def process_file(self, filepath: Path) -> None:
        """Process a single YAML file"""
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
            
            if not data:
                print(f"  ⚠️  Empty file: {filepath}")
                return
            
            # Track changes
            changes = []
            
            # Apply fixes
            if self.fix_naming_consistency(data):
                changes.append('naming')
                self.stats['naming_fixed'] += 1
            
            if self.denormalize_contaminants(data):
                changes.append('contaminants')
                self.stats['denormalized'] += 1
            
            if self.denormalize_compounds(data):
                changes.append('compounds')
                self.stats['denormalized'] += 1
            
            if self.remove_metadata_wrapper(data):
                changes.append('metadata')
                self.stats['metadata_removed'] += 1
            
            if self.ensure_type_safety(data):
                changes.append('types')
                self.stats['type_fixed'] += 1
            
            # Write back if changes made
            if changes:
                if not self.dry_run:
                    with open(filepath, 'w') as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                
                change_str = ', '.join(changes)
                print(f"  ✅ Fixed ({change_str}): {filepath.name}")
            
            self.stats['files_processed'] += 1
            
        except Exception as e:
            print(f"  ❌ Error in {filepath}: {e}")
            self.stats['errors'] += 1
    
    def process_domain(self, domain: str) -> None:
        """Process source data file for a domain"""
        print(f"\n{'='*80}")
        print(f"Processing {domain.upper()} domain...")
        print(f"{'='*80}")
        
        # Map domain to source file
        source_files = {
            'materials': 'data/materials/Materials.yaml',
            'contaminants': 'data/contaminants/Contaminants.yaml',
            'compounds': 'data/compounds/Compounds.yaml',
            'settings': 'data/settings/Settings.yaml'
        }
        
        if domain not in source_files:
            print(f"  ⚠️  Unknown domain: {domain}")
            return
        
        filepath = Path(source_files[domain])
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            return
        
        print(f"Source file: {filepath}")
        
        # Load entire file
        with open(filepath) as f:
            data = yaml.safe_load(f)
        
        # Get root key (materials, contaminants, compounds, settings)
        root_key = domain
        if root_key not in data:
            print(f"  ⚠️  Root key '{root_key}' not found in {filepath}")
            return
        
        items = data[root_key]
        print(f"Found {len(items)} items")
        
        # Track changes
        total_changes = 0
        
        # Process each item
        for item_id, item_data in items.items():
            changes = []
            
            # Apply fixes
            if self.fix_naming_consistency(item_data):
                changes.append('naming')
                self.stats['naming_fixed'] += 1
            
            if self.denormalize_contaminants(item_data):
                changes.append('contaminants')
                self.stats['denormalized'] += 1
            
            if self.denormalize_compounds(item_data):
                changes.append('compounds')
                self.stats['denormalized'] += 1
            
            if self.remove_metadata_wrapper(item_data):
                changes.append('metadata')
                self.stats['metadata_removed'] += 1
            
            if self.ensure_type_safety(item_data):
                changes.append('types')
                self.stats['type_fixed'] += 1
            
            if changes:
                change_str = ', '.join(changes)
                if total_changes < 10:  # Only print first 10
                    print(f"  ✅ Fixed ({change_str}): {item_id}")
                total_changes += 1
            
            self.stats['files_processed'] += 1
        
        if total_changes > 10:
            print(f"  ✅ Fixed {total_changes - 10} more items...")
        
        # Write back if changes made
        if total_changes > 0 and not self.dry_run:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            print(f"\n  💾 Saved changes to {filepath}")
        elif total_changes > 0:
            print(f"\n  💡 Dry run - no changes saved")
    
    def print_summary(self) -> None:
        """Print summary statistics"""
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Naming fixed: {self.stats['naming_fixed']}")
        print(f"Denormalized: {self.stats['denormalized']}")
        print(f"Metadata removed: {self.stats['metadata_removed']}")
        print(f"Type safety fixed: {self.stats['type_fixed']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"{'='*80}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix frontmatter structure issues')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'applications', 'all'],
                        default='all', help='Domain to process')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    
    args = parser.parse_args()
    
    # Create fixer
    fixer = FrontmatterFixer(dry_run=not args.apply)
    
    # Print mode
    mode = "APPLYING CHANGES" if args.apply else "DRY RUN (use --apply to make changes)"
    print(f"\n{'='*80}")
    print(f"FRONTMATTER STRUCTURE FIXES - {mode}")
    print(f"{'='*80}")
    
    # Process domains
    if args.domain == 'all':
        for domain in ['materials', 'contaminants', 'compounds', 'settings', 'applications']:
            fixer.process_domain(domain)
    else:
        fixer.process_domain(args.domain)
    
    # Print summary
    fixer.print_summary()
    
    if not args.apply:
        print("\n💡 Run with --apply to make changes permanent")


if __name__ == '__main__':
    main()
