#!/usr/bin/env python3
"""
Fix compound category/subcategory to match fullPath (source of truth).

POLICY COMPLIANCE: Core Principle 0.5 and 0.6
- Modifies SOURCE data (data/compounds/Compounds.yaml)
- NOT generated frontmatter
- Export automatically propagates fixes

PROBLEM:
- fullPath: /compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound
- But category: toxic_gas_oxidizing (MISMATCH)
- Next.js routing fails → 404 errors

SOLUTION:
- Parse fullPath to extract category/subcategory
- Update source data fields to match
- Re-export → frontmatter inherits correct values
"""

import yaml
import sys
from pathlib import Path
from typing import Dict

class CompoundPathFixer:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.compounds_file = base_path / 'data' / 'compounds' / 'Compounds.yaml'
        
        # Statistics
        self.stats = {
            'compounds_processed': 0,
            'compounds_updated': 0,
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
    
    def parse_fullpath(self, fullpath: str) -> tuple:
        """
        Parse fullPath to extract category and subcategory.
        
        Format: /compounds/{category}/{subcategory}/{slug}
        Example: /compounds/toxic_gas/oxidizing_gas/nitrogen-oxides-compound
        Returns: (category, subcategory, slug)
        """
        parts = fullpath.split('/')
        if len(parts) < 5 or parts[1] != 'compounds':
            raise ValueError(f"Invalid fullPath format: {fullpath}")
        
        return (parts[2], parts[3], parts[4])
    
    def fix_compound(self, compound_id: str, compound_data: Dict) -> bool:
        """
        Fix category/subcategory in compound to match fullPath.
        Returns True if changes were made.
        """
        self.stats['compounds_processed'] += 1
        
        # Get fullPath
        fullpath = compound_data.get('fullPath')
        if not fullpath:
            self.stats['errors'].append(f"{compound_id}: Missing fullPath")
            return False
        
        try:
            # Parse fullPath to get expected values
            expected_category, expected_subcategory, expected_slug = self.parse_fullpath(fullpath)
        except ValueError as e:
            self.stats['errors'].append(f"{compound_id}: {e}")
            return False
        
        # Get current values
        current_category = compound_data.get('category', '')
        current_subcategory = compound_data.get('subcategory', '')
        
        # Check for mismatches
        category_mismatch = current_category != expected_category
        subcategory_mismatch = current_subcategory != expected_subcategory
        
        if category_mismatch or subcategory_mismatch:
            self.stats['mismatches_found'] += 1
            
            print(f"\n🔧 Fixing: {compound_id}")
            print(f"   fullPath: {fullpath}")
            
            if category_mismatch:
                print(f"   ❌ category: '{current_category}' → ✅ '{expected_category}'")
                compound_data['category'] = expected_category
            
            if subcategory_mismatch:
                print(f"   ❌ subcategory: '{current_subcategory}' → ✅ '{expected_subcategory}'")
                compound_data['subcategory'] = expected_subcategory
            
            return True
        else:
            print(f"✓ {compound_id}: Already correct")
            return False
    
    def fix_all_compounds(self):
        """Process all compounds in source data"""
        print(f"📂 Loading: {self.compounds_file}")
        data = self.load_yaml(self.compounds_file)
        
        compounds = data.get('compounds', {})
        print(f"\n🔍 Found {len(compounds)} compounds")
        print("="*80)
        
        for compound_id, compound_data in compounds.items():
            if self.fix_compound(compound_id, compound_data):
                self.stats['compounds_updated'] += 1
        
        # Save if any updates were made
        if self.stats['compounds_updated'] > 0:
            print(f"\n💾 Saving changes to {self.compounds_file}...")
            self.save_yaml(self.compounds_file, data)
            print("   ✅ Saved successfully")
        else:
            print("\n✓ No changes needed - all compounds already correct")
        
        self.print_report()
    
    def print_report(self):
        """Print fix statistics"""
        print("\n" + "="*80)
        print("📊 COMPOUND PATH FIX COMPLETE")
        print("="*80)
        print(f"\n✅ Compounds processed: {self.stats['compounds_processed']}")
        print(f"🔧 Mismatches found: {self.stats['mismatches_found']}")
        print(f"✅ Compounds updated: {self.stats['compounds_updated']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"   • {error}")
        else:
            print("\n✅ No errors encountered")
        
        if self.stats['compounds_updated'] > 0:
            print("\n" + "="*80)
            print("📋 NEXT STEPS:")
            print("="*80)
            print("1. Re-export compounds domain:")
            print("   python3 run.py --export --domain compounds")
            print("\n2. Verify frontmatter has correct category/subcategory:")
            print("   cat ../z-beam/frontmatter/compounds/nitrogen-oxides-compound.yaml")
            print("\n3. Commit source data changes:")
            print("   git add data/compounds/Compounds.yaml")
            print("   git commit -m 'fix: Align compound category/subcategory with fullPath'")
            print("\n4. Rebuild Next.js (on frontend):")
            print("   rm -rf .next && npm run build")

if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent  # scripts/tools/ -> scripts/ -> root
    
    print(f"📁 Working directory: {base_path}")
    print(f"📂 Source data: {base_path / 'data' / 'compounds'}")
    
    fixer = CompoundPathFixer(base_path)
    fixer.fix_all_compounds()
