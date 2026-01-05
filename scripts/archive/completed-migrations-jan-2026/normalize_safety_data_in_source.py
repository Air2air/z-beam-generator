#!/usr/bin/env python3
"""
Safety Data In-Source Normalization Script
Author: AI Assistant
Date: December 23, 2025

Purpose: Move nested safety_data objects to relationships section WITHIN Contaminants.yaml
Approach: Normalize data IN SOURCE, not in exporters

Current State:
  contamination_patterns:
    adhesive-residue-contamination:
      # safety_data is nested in laser_properties/removal_by_material items
      laser_properties:
        items:
          - material_category: ceramic
            safety_data:
              fire_explosion_risk: {...}
              fumes_generated: [...]
              ppe_requirements: {...}

Target State:
  contamination_patterns:
    adhesive-residue-contamination:
      relationships:
        safety_requirements:
          presentation: card
          items:
            - material_category: ceramic
              fire_explosion_risk: {...}
              fumes_generated: [...]
              ppe_requirements: {...}
          _section:
            title: "Safety Requirements"
            description: "PPE, hazard warnings, and exposure limits"
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
import copy

class SafetyDataNormalizer:
    """Normalizes safety_data from nested to relationships."""
    
    def __init__(self):
        self.source_file = 'data/contaminants/Contaminants.yaml'
        self.stats = {
            'contaminants_processed': 0,
            'safety_data_moved': 0,
            'errors': []
        }
    
    def load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML file."""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, path: str, data: Dict[str, Any]) -> None:
        """Save YAML file with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
    
    def extract_safety_from_laser_properties(self, laser_props: Dict) -> List[Dict]:
        """Extract safety_data from laser_properties items."""
        safety_items = []
        
        if 'items' not in laser_props:
            return safety_items
        
        for item in laser_props['items']:
            if 'safety_data' in item:
                # Create a new item with material_category and safety data
                safety_item = {}
                
                # Preserve material context
                if 'material_category' in item:
                    safety_item['material_category'] = item['material_category']
                if 'material_name' in item:
                    safety_item['material_name'] = item['material_name']
                
                # Copy all safety_data fields to top level of item
                safety_data = item['safety_data']
                for key, value in safety_data.items():
                    safety_item[key] = value
                
                safety_items.append(safety_item)
                
                # Remove safety_data from laser_properties item
                del item['safety_data']
        
        return safety_items
    
    def normalize_contaminant(self, cont_data: Dict) -> bool:
        """Normalize a single contaminant. Returns True if changes made."""
        changed = False
        
        # Extract safety_data from laser_properties
        if 'laser_properties' in cont_data:
            safety_items = self.extract_safety_from_laser_properties(cont_data['laser_properties'])
            
            if safety_items:
                # Ensure relationships section exists
                if 'relationships' not in cont_data:
                    cont_data['relationships'] = {}
                
                # Add safety_requirements relationship
                cont_data['relationships']['safety_requirements'] = {
                    'presentation': 'card',
                    'items': safety_items,
                    '_section': {
                        'title': 'Safety Requirements',
                        'description': 'Personal protective equipment, hazard warnings, and exposure limits for laser removal',
                        'icon': 'shield-check'
                    }
                }
                
                changed = True
                self.stats['safety_data_moved'] += len(safety_items)
        
        return changed
    
    def run(self, dry_run: bool = False) -> None:
        """Run normalization on Contaminants.yaml."""
        print("="*70)
        print("SAFETY DATA IN-SOURCE NORMALIZATION")
        print("="*70)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"File: {self.source_file}")
        print()
        
        # Load data
        try:
            data = self.load_yaml(self.source_file)
        except Exception as e:
            print(f"❌ Failed to load: {e}")
            return
        
        contaminants = data.get('contamination_patterns', {})
        print(f"Total contaminants: {len(contaminants)}")
        print()
        
        # Process each contaminant
        for cont_id, cont_data in contaminants.items():
            if self.normalize_contaminant(cont_data):
                self.stats['contaminants_processed'] += 1
                if dry_run:
                    print(f"  📝 {cont_id}: Would normalize safety_data")
        
        # Save if not dry run
        if not dry_run and self.stats['contaminants_processed'] > 0:
            try:
                # Create backup
                backup_path = f"{self.source_file}.backup_safety_normalized"
                with open(self.source_file, 'r') as f:
                    with open(backup_path, 'w') as b:
                        b.write(f.read())
                print(f"📁 Backup created: {backup_path}")
                
                # Save normalized data
                self.save_yaml(self.source_file, data)
                print(f"✅ Saved {self.source_file}")
            except Exception as e:
                print(f"❌ Failed to save: {e}")
                return
        
        # Print summary
        print("\n" + "="*70)
        print("NORMALIZATION SUMMARY")
        print("="*70)
        print(f"Contaminants processed: {self.stats['contaminants_processed']}")
        print(f"Safety data items moved: {self.stats['safety_data_moved']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print(f"\n✅ No errors")
        
        if not dry_run and self.stats['contaminants_processed'] > 0:
            print(f"\n✅ Normalization complete!")
            print(f"   Next: Re-export contaminants to update frontmatter")
        elif dry_run:
            print(f"\n🔍 Dry run complete - no changes saved")
        else:
            print(f"\n⚠️  No safety_data found to normalize")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Normalize safety_data from nested to relationships IN SOURCE'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    normalizer = SafetyDataNormalizer()
    normalizer.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
