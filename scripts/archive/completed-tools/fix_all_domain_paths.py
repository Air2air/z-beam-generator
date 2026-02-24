#!/usr/bin/env python3
"""
Fix category/subcategory to match fullPath (source of truth) across ALL domains.

POLICY COMPLIANCE: Core Principle 0.5 and 0.6
- Modifies SOURCE data (data/*/*)
- NOT generated frontmatter
- Export automatically propagates fixes

PROBLEM:
- fullPath: /materials/metal/ferrous/carbon-steel-laser-cleaning
- But category: metal_ferrous (MISMATCH)
- Next.js routing fails → 404 errors

SOLUTION:
- Parse fullPath to extract category/subcategory
- Update source data fields to match
- Re-export → frontmatter inherits correct values

DOMAINS:
- Materials (data/materials/Materials.yaml)
- Contaminants (data/contaminants/Contaminants.yaml)
- Compounds (data/compounds/Compounds.yaml)
- Settings (data/settings/Settings.yaml)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Tuple

class UniversalPathFixer:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.data_dir = base_path / 'data'
        
        # Domain configurations
        self.domains = {
            'materials': {
                'file': self.data_dir / 'materials' / 'Materials.yaml',
                'key': 'materials'
            },
            'contaminants': {
                'file': self.data_dir / 'contaminants' / 'Contaminants.yaml',
                'key': 'contaminants'
            },
            'compounds': {
                'file': self.data_dir / 'compounds' / 'Compounds.yaml',
                'key': 'compounds'
            },
            'settings': {
                'file': self.data_dir / 'settings' / 'Settings.yaml',
                'key': 'settings'
            }
        }
        
        # Statistics
        self.stats = {
            'domains_processed': 0,
            'items_processed': 0,
            'items_updated': 0,
            'mismatches_found': 0,
            'errors': []
        }
    
    def load_yaml(self, file_path: Path) -> Dict:
        """Load and parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Load error {file_path}: {e}")
            sys.exit(1)
    
    def save_yaml(self, file_path: Path, data: Dict):
        """Save updated data back to YAML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"❌ Save error {file_path}: {e}")
            sys.exit(1)
    
    def parse_fullpath(self, fullpath: str, domain: str) -> Tuple[str, str, str]:
        """
        Parse fullPath to extract category and subcategory.
        
        Format: /{domain}/{category}/{subcategory}/{slug}
        Example: /materials/metal/ferrous/carbon-steel-laser-cleaning
        Returns: (category, subcategory, slug)
        """
        parts = fullpath.split('/')
        if len(parts) < 5:
            raise ValueError(f"Invalid fullPath format (too short): {fullpath}")
        
        if parts[1] != domain:
            raise ValueError(f"fullPath domain mismatch: expected '{domain}', got '{parts[1]}' in {fullpath}")
        
        return (parts[2], parts[3], parts[4])
    
    def fix_item(self, item_id: str, item_data: Dict, domain: str) -> bool:
        """
        Fix category/subcategory in item to match fullPath.
        Returns True if changes were made.
        """
        self.stats['items_processed'] += 1
        
        # Get fullPath
        fullpath = item_data.get('fullPath')
        if not fullpath:
            self.stats['errors'].append(f"{domain}/{item_id}: Missing fullPath")
            return False
        
        try:
            # Parse fullPath to get expected values
            expected_category, expected_subcategory, expected_slug = self.parse_fullpath(fullpath, domain)
        except ValueError as e:
            self.stats['errors'].append(f"{domain}/{item_id}: {e}")
            return False
        
        # Get current values
        current_category = item_data.get('category', '')
        current_subcategory = item_data.get('subcategory', '')
        
        # Check for mismatches
        category_mismatch = current_category != expected_category
        subcategory_mismatch = current_subcategory != expected_subcategory
        
        if category_mismatch or subcategory_mismatch:
            self.stats['mismatches_found'] += 1
            
            print(f"\n🔧 Fixing: {item_id}")
            print(f"   fullPath: {fullpath}")
            
            if category_mismatch:
                print(f"   ❌ category: '{current_category}' → ✅ '{expected_category}'")
                item_data['category'] = expected_category
            
            if subcategory_mismatch:
                print(f"   ❌ subcategory: '{current_subcategory}' → ✅ '{expected_subcategory}'")
                item_data['subcategory'] = expected_subcategory
            
            return True
        else:
            return False
    
    def process_domain(self, domain_name: str) -> int:
        """Process single domain. Returns number of items updated."""
        config = self.domains[domain_name]
        file_path = config['file']
        data_key = config['key']
        
        if not file_path.exists():
            print(f"⚠️  Skipping {domain_name}: File not found: {file_path}")
            return 0
        
        print(f"\n{'='*80}")
        print(f"📦 PROCESSING DOMAIN: {domain_name.upper()}")
        print(f"{'='*80}")
        print(f"📂 File: {file_path}")
        
        # Load data
        data = self.load_yaml(file_path)
        items = data.get(data_key, {})
        
        if not items:
            print(f"⚠️  No items found in '{data_key}' key")
            return 0
        
        print(f"🔍 Found {len(items)} items\n")
        
        # Process each item
        items_updated = 0
        correct_count = 0
        
        for item_id, item_data in items.items():
            if self.fix_item(item_id, item_data, domain_name):
                items_updated += 1
            else:
                correct_count += 1
        
        # Save if any updates were made
        if items_updated > 0:
            print(f"\n💾 Saving changes to {file_path.name}...")
            self.save_yaml(file_path, data)
            print("   ✅ Saved successfully")
        else:
            print(f"\n✓ All {correct_count} items already correct - no changes needed")
        
        return items_updated
    
    def fix_all_domains(self):
        """Process all domains"""
        print(f"📁 Working directory: {self.base_path}")
        print(f"📂 Data directory: {self.data_dir}")
        
        total_updated = 0
        
        for domain_name in self.domains.keys():
            self.stats['domains_processed'] += 1
            updated = self.process_domain(domain_name)
            total_updated += updated
            self.stats['items_updated'] += updated
        
        self.print_report()
    
    def print_report(self):
        """Print fix statistics"""
        print("\n" + "="*80)
        print("📊 UNIVERSAL PATH FIX COMPLETE")
        print("="*80)
        print(f"\n✅ Domains processed: {self.stats['domains_processed']}")
        print(f"✅ Items processed: {self.stats['items_processed']}")
        print(f"🔧 Mismatches found: {self.stats['mismatches_found']}")
        print(f"✅ Items updated: {self.stats['items_updated']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:20]:
                print(f"   • {error}")
            if len(self.stats['errors']) > 20:
                print(f"   ... and {len(self.stats['errors']) - 20} more")
        else:
            print("\n✅ No errors encountered")
        
        if self.stats['items_updated'] > 0:
            print("\n" + "="*80)
            print("📋 NEXT STEPS:")
            print("="*80)
            print("1. Re-export ALL domains:")
            print("   python3 run.py --export --domain materials")
            print("   python3 run.py --export --domain contaminants")
            print("   python3 run.py --export --domain compounds")
            print("   python3 run.py --export --domain settings")
            print("\n2. Verify frontmatter has correct category/subcategory:")
            print("   cat ../z-beam/frontmatter/materials/aluminum-laser-cleaning.yaml")
            print("   cat ../z-beam/frontmatter/compounds/carbon-dioxide-compound.yaml")
            print("\n3. Commit source data changes:")
            print("   git add data/*/")
            print("   git commit -m 'fix: Align all domains category/subcategory with fullPath'")
            print("\n4. Rebuild Next.js (on frontend):")
            print("   rm -rf .next && npm run build")

if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent  # scripts/tools/ -> scripts/ -> root
    
    fixer = UniversalPathFixer(base_path)
    fixer.fix_all_domains()
