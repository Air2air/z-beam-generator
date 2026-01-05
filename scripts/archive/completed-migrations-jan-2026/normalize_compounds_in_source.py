#!/usr/bin/env python3
"""
Compounds In-Source Normalization Script
Author: AI Assistant
Date: December 23, 2025

Purpose: Move 11 nested objects to relationships section WITHIN Compounds.yaml
Approach: Normalize data IN SOURCE, not in exporters

Nested Objects to Migrate:
1. ppe_requirements
2. exposure_limits
3. physical_properties
4. emergency_response
5. storage_requirements
6. regulatory_classification
7. workplace_exposure
8. reactivity
9. environmental_impact
10. detection_monitoring
11. synonyms_identifiers

Current State:
  compounds:
    carbon-monoxide-compound:
      ppe_requirements:
        respiratory: "full-face SCBA"
        skin: "protective gloves"
      exposure_limits:
        osha_pel_ppm: 50
        niosh_rel_ppm: 35
      # ... 9 more nested objects

Target State:
  compounds:
    carbon-monoxide-compound:
      relationships:
        ppe_requirements:
          presentation: card
          items:
            - respiratory: "full-face SCBA"
              skin: "protective gloves"
          _section:
            title: "Personal Protective Equipment"
            description: "Required safety equipment"
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List

class CompoundsNormalizer:
    """Normalizes nested objects to relationships in Compounds.yaml."""
    
    # Fields to migrate to relationships
    MIGRATE_FIELDS = [
        'ppe_requirements',
        'exposure_limits', 
        'physical_properties',
        'emergency_response',
        'storage_requirements',
        'regulatory_classification',
        'workplace_exposure',
        'reactivity',
        'environmental_impact',
        'detection_monitoring',
        'synonyms_identifiers'
    ]
    
    # Section metadata for each relationship
    SECTION_METADATA = {
        'ppe_requirements': {
            'title': 'Personal Protective Equipment',
            'description': 'Required safety equipment for handling this compound',
            'icon': 'shield-check'
        },
        'exposure_limits': {
            'title': 'Exposure Limits',
            'description': 'OSHA, NIOSH, and ACGIH exposure thresholds',
            'icon': 'gauge'
        },
        'physical_properties': {
            'title': 'Physical Properties',
            'description': 'Chemical and physical characteristics',
            'icon': 'flask'
        },
        'emergency_response': {
            'title': 'Emergency Response',
            'description': 'Procedures for spills, exposure, and incidents',
            'icon': 'exclamation-triangle'
        },
        'storage_requirements': {
            'title': 'Storage Requirements',
            'description': 'Safe storage conditions and compatibility',
            'icon': 'warehouse'
        },
        'regulatory_classification': {
            'title': 'Regulatory Classification',
            'description': 'DOT, UN, and NFPA hazard classifications',
            'icon': 'book-law'
        },
        'workplace_exposure': {
            'title': 'Workplace Exposure',
            'description': 'Occupational exposure data and controls',
            'icon': 'hard-hat'
        },
        'reactivity': {
            'title': 'Reactivity',
            'description': 'Chemical reactivity and incompatibilities',
            'icon': 'atom'
        },
        'environmental_impact': {
            'title': 'Environmental Impact',
            'description': 'Toxicity, biodegradability, and environmental fate',
            'icon': 'leaf'
        },
        'detection_monitoring': {
            'title': 'Detection & Monitoring',
            'description': 'Methods for detecting and measuring this compound',
            'icon': 'radar'
        },
        'synonyms_identifiers': {
            'title': 'Alternative Names',
            'description': 'Synonyms and chemical identifiers',
            'icon': 'tag'
        }
    }
    
    def __init__(self):
        self.source_file = 'data/compounds/Compounds.yaml'
        self.stats = {
            'compounds_processed': 0,
            'fields_moved': 0,
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
    
    def normalize_compound(self, compound_data: Dict) -> bool:
        """Normalize a single compound. Returns True if changes made."""
        changed = False
        
        # Ensure relationships section exists
        if 'relationships' not in compound_data:
            compound_data['relationships'] = {}
        
        # Move each nested field to relationships
        for field in self.MIGRATE_FIELDS:
            if field in compound_data:
                # Create relationship entry
                compound_data['relationships'][field] = {
                    'presentation': 'card',
                    'items': [compound_data[field]],  # Wrap in array
                    '_section': self.SECTION_METADATA.get(field, {
                        'title': field.replace('_', ' ').title(),
                        'description': f'Information about {field.replace("_", " ")}'
                    })
                }
                
                # Remove from top level
                del compound_data[field]
                
                changed = True
                self.stats['fields_moved'] += 1
        
        return changed
    
    def run(self, dry_run: bool = False) -> None:
        """Run normalization on Compounds.yaml."""
        print("="*70)
        print("COMPOUNDS IN-SOURCE NORMALIZATION")
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
        
        compounds = data.get('compounds', {})
        print(f"Total compounds: {len(compounds)}")
        print(f"Fields to migrate: {', '.join(self.MIGRATE_FIELDS)}")
        print()
        
        # Process each compound
        for comp_id, comp_data in compounds.items():
            if self.normalize_compound(comp_data):
                self.stats['compounds_processed'] += 1
                if dry_run:
                    print(f"  📝 {comp_id}: Would normalize nested fields")
        
        # Save if not dry run
        if not dry_run and self.stats['compounds_processed'] > 0:
            try:
                # Create backup
                backup_path = f"{self.source_file}.backup_normalized"
                with open(self.source_file, 'r') as f:
                    with open(backup_path, 'w') as b:
                        b.write(f.read())
                print(f"\n📁 Backup created: {backup_path}")
                
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
        print(f"Compounds processed: {self.stats['compounds_processed']}")
        print(f"Fields moved to relationships: {self.stats['fields_moved']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print(f"\n✅ No errors")
        
        if not dry_run and self.stats['compounds_processed'] > 0:
            print(f"\n✅ Normalization complete!")
            print(f"   Next: Re-export compounds to update frontmatter")
        elif dry_run:
            print(f"\n🔍 Dry run complete - no changes saved")
        else:
            print(f"\n⚠️  No nested fields found to normalize")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Normalize nested objects to relationships IN SOURCE'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    normalizer = CompoundsNormalizer()
    normalizer.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
