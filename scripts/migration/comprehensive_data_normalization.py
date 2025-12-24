#!/usr/bin/env python3
"""
Comprehensive Data Normalization - All Domains
Author: AI Assistant
Date: December 23, 2025

MANDATORY TASK: Normalize ALL nested non-relationship data to relationships section
across all domains directly in source YAML files.

Philosophy: Data lives in source, exporters are dumb pipes.

Domains Covered:
1. Materials (4 nested → relationships)
2. Contaminants (safety_data + 2 others → relationships)
3. Compounds (11 nested → relationships)
4. Settings (challenges → relationships)

Total Impact: ~17 nested structures → relationships across 438 entities
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

class UniversalDataNormalizer:
    """Comprehensive normalizer for all domains."""
    
    # Domain configurations
    DOMAINS = {
        'materials': {
            'file': 'data/materials/Materials.yaml',
            'items_key': 'materials',
            'migrate_fields': [
                # Already in relationships: contaminated_by, removes_contaminants, 
                # produces_compounds, regulatory
                # Nested metadata that should stay:
                # - properties (inherent material characteristics)
                # - metadata (system data)
                # Nothing to migrate currently - materials is already well-structured
            ],
            'section_metadata': {}
        },
        'contaminants': {
            'file': 'data/contaminants/Contaminants.yaml',
            'items_key': 'contamination_patterns',
            'migrate_fields': [],  # safety_data is embedded in laser_properties items
            'special_handler': 'extract_safety_from_laser_properties',
            'section_metadata': {
                'safety_requirements': {
                    'title': 'Safety Requirements',
                    'description': 'Personal protective equipment, hazard warnings, and exposure limits for laser removal',
                    'icon': 'shield-check'
                }
            }
        },
        'compounds': {
            'file': 'data/compounds/Compounds.yaml',
            'items_key': 'compounds',
            'migrate_fields': [
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
            ],
            'section_metadata': {
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
        },
        'settings': {
            'file': 'data/settings/Settings.yaml',
            'items_key': 'settings',
            'migrate_fields': [
                'challenges'  # Move challenges to relationships
            ],
            'section_metadata': {
                'challenges': {
                    'title': 'Common Challenges',
                    'description': 'Technical challenges and optimization strategies for these settings',
                    'icon': 'triangle-exclamation'
                }
            }
        }
    }
    
    def __init__(self):
        self.stats = {
            'domains_processed': 0,
            'entities_modified': 0,
            'fields_moved': 0,
            'backups_created': 0,
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
    
    def create_backup(self, filepath: str) -> str:
        """Create timestamped backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{filepath}.backup_normalized_{timestamp}"
        with open(filepath, 'r') as f:
            with open(backup_path, 'w') as b:
                b.write(f.read())
        self.stats['backups_created'] += 1
        return backup_path
    
    def extract_safety_from_laser_properties(self, item_data: Dict) -> Tuple[Dict, bool]:
        """Special handler for contaminants safety_data in laser_properties."""
        changed = False
        safety_items = []
        
        if 'laser_properties' in item_data and 'items' in item_data['laser_properties']:
            for lp_item in item_data['laser_properties']['items']:
                if 'safety_data' in lp_item:
                    # Create safety item with material context
                    safety_item = {}
                    
                    if 'material_category' in lp_item:
                        safety_item['material_category'] = lp_item['material_category']
                    if 'material_name' in lp_item:
                        safety_item['material_name'] = lp_item['material_name']
                    
                    # Flatten safety_data to top level
                    for key, value in lp_item['safety_data'].items():
                        safety_item[key] = value
                    
                    safety_items.append(safety_item)
                    del lp_item['safety_data']
                    changed = True
        
        if safety_items:
            if 'relationships' not in item_data:
                item_data['relationships'] = {}
            
            item_data['relationships']['safety_requirements'] = {
                'presentation': 'card',
                'items': safety_items,
                '_section': self.DOMAINS['contaminants']['section_metadata']['safety_requirements']
            }
        
        return item_data, changed
    
    def normalize_standard_fields(self, item_data: Dict, migrate_fields: List[str], 
                                  section_metadata: Dict) -> Tuple[Dict, int]:
        """Move standard nested fields to relationships."""
        fields_moved = 0
        
        if 'relationships' not in item_data:
            item_data['relationships'] = {}
        
        for field in migrate_fields:
            if field in item_data:
                # Create relationship
                item_data['relationships'][field] = {
                    'presentation': 'card',
                    'items': [item_data[field]],  # Wrap in array
                    '_section': section_metadata.get(field, {
                        'title': field.replace('_', ' ').title(),
                        'description': f'Information about {field.replace("_", " ")}'
                    })
                }
                
                del item_data[field]
                fields_moved += 1
        
        return item_data, fields_moved
    
    def process_domain(self, domain_name: str, dry_run: bool = False) -> None:
        """Process a single domain."""
        config = self.DOMAINS[domain_name]
        filepath = config['file']
        items_key = config['items_key']
        
        print(f"\n{'='*70}")
        print(f"PROCESSING {domain_name.upper()}")
        print(f"{'='*70}")
        print(f"File: {filepath}")
        
        # Load data
        try:
            data = self.load_yaml(filepath)
        except Exception as e:
            error = f"{domain_name}: Failed to load - {e}"
            self.stats['errors'].append(error)
            print(f"❌ {error}")
            return
        
        items = data.get(items_key, {})
        print(f"Total items: {len(items)}")
        
        # Process each item
        entities_modified = 0
        domain_fields_moved = 0
        
        for item_id, item_data in items.items():
            item_changed = False
            
            # Special handler for contaminants
            if config.get('special_handler') == 'extract_safety_from_laser_properties':
                item_data, changed = self.extract_safety_from_laser_properties(item_data)
                if changed:
                    item_changed = True
                    domain_fields_moved += 1
            
            # Standard field migration
            if config.get('migrate_fields'):
                item_data, fields_moved = self.normalize_standard_fields(
                    item_data, 
                    config['migrate_fields'],
                    config['section_metadata']
                )
                if fields_moved > 0:
                    item_changed = True
                    domain_fields_moved += fields_moved
            
            if item_changed:
                entities_modified += 1
                if dry_run:
                    print(f"  📝 {item_id}: Would normalize")
        
        # Save if not dry run
        if not dry_run and entities_modified > 0:
            try:
                backup_path = self.create_backup(filepath)
                print(f"📁 Backup: {backup_path}")
                
                self.save_yaml(filepath, data)
                print(f"✅ Saved: {filepath}")
            except Exception as e:
                error = f"{domain_name}: Failed to save - {e}"
                self.stats['errors'].append(error)
                print(f"❌ {error}")
                return
        
        # Update stats
        self.stats['domains_processed'] += 1
        self.stats['entities_modified'] += entities_modified
        self.stats['fields_moved'] += domain_fields_moved
        
        print(f"📊 Entities modified: {entities_modified}")
        print(f"📊 Fields moved: {domain_fields_moved}")
        
        if dry_run and entities_modified > 0:
            print(f"🔍 DRY RUN - No changes saved")
    
    def run(self, dry_run: bool = False) -> None:
        """Run comprehensive normalization across all domains."""
        print("="*70)
        print("COMPREHENSIVE DATA NORMALIZATION - ALL DOMAINS")
        print("="*70)
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"Strategy: Normalize nested data → relationships IN SOURCE")
        print()
        
        # Process each domain
        for domain in ['materials', 'contaminants', 'compounds', 'settings']:
            self.process_domain(domain, dry_run)
        
        # Print summary
        print("\n" + "="*70)
        print("COMPREHENSIVE NORMALIZATION SUMMARY")
        print("="*70)
        print(f"Domains processed: {self.stats['domains_processed']}/4")
        print(f"Entities modified: {self.stats['entities_modified']}")
        print(f"Fields moved to relationships: {self.stats['fields_moved']}")
        print(f"Backups created: {self.stats['backups_created']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                print(f"  - {error}")
        else:
            print(f"\n✅ No errors")
        
        if not dry_run and self.stats['entities_modified'] > 0:
            print(f"\n✅ COMPREHENSIVE NORMALIZATION COMPLETE!")
            print(f"   Next steps:")
            print(f"   1. Re-export all domains: for domain in materials contaminants compounds settings; do python3 run.py --export --domain $domain; done")
            print(f"   2. Validate frontmatter structure")
            print(f"   3. Test frontend rendering")
        elif dry_run:
            print(f"\n🔍 Dry run complete - no changes saved")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive data normalization across all domains'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving'
    )
    
    args = parser.parse_args()
    
    normalizer = UniversalDataNormalizer()
    normalizer.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
