#!/usr/bin/env python3
"""
Check data completeness across all domains.
Reports which fields are populated and which are still empty.
"""

import yaml
from pathlib import Path
from collections import defaultdict


def check_domain_completeness(data_file: Path, fields: list, domain_key: str) -> dict:
    """Check completeness for a single domain"""
    
    with open(data_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Get items from specified domain key
    items = data.get(domain_key, {})
    
    if not items:
        return {
            'total_items': 0,
            'field_stats': {}
        }
    
    total_items = len(items)
    field_stats = defaultdict(lambda: {'populated': 0, 'empty': 0})
    
    for item_id, item_data in items.items():
        if not isinstance(item_data, dict):
            continue
            
        for field in fields:
            # Navigate nested fields (e.g., "author.id")
            value = item_data
            for part in field.split('.'):
                value = value.get(part, None) if isinstance(value, dict) else None
            
            if value and value != 'null' and value != '':
                field_stats[field]['populated'] += 1
            else:
                field_stats[field]['empty'] += 1
    
    return {
        'total_items': total_items,
        'field_stats': dict(field_stats)
    }


def main():
    """Check completeness for all domains"""
    
    print("════════════════════════════════════════════════════════════════════════════════")
    print("📊 DATA COMPLETENESS CHECK - ALL DOMAINS")
    print("════════════════════════════════════════════════════════════════════════════════")
    print("")
    
    # Define domains and their fields to check
    domains = {
        'materials': {
            'file': Path('data/materials/Materials.yaml'),
            'key': 'materials',
            'fields': ['description', 'power_intensity', 'context', 'micro', 'faq']
        },
        'contaminants': {
            'file': Path('data/contaminants/Contaminants.yaml'),
            'key': 'contamination_patterns',
            'fields': ['description', 'micro', 'compounds', 'appearance', 'context']
        },
        'compounds': {
            'file': Path('data/compounds/Compounds.yaml'),
            'key': 'compounds',
            'fields': ['description', 'health_effects', 'exposure_guidelines']
        },
        'settings': {
            'file': Path('data/settings/Settings.yaml'),
            'key': 'settings',
            'fields': ['settings_description', 'recommendations', 'challenges']
        }
    }
    
    for domain_name, domain_config in domains.items():
        print(f"{'='*80}")
        print(f"📦 {domain_name.upper()}")
        print(f"{'='*80}")
        
        stats = check_domain_completeness(
            domain_config['file'], 
            domain_config['fields'],
            domain_config['key']
        )
        total = stats['total_items']
        
        for field, counts in stats['field_stats'].items():
            populated = counts['populated']
            empty = counts['empty']
            pct = (populated / total * 100) if total > 0 else 0
            
            status = "✅" if empty == 0 else "⚠️ " if populated > 0 else "❌"
            print(f"{status} {field:25} {populated:3}/{total:3} ({pct:5.1f}%) populated, {empty:3} empty")
        
        print("")
    
    print("════════════════════════════════════════════════════════════════════════════════")
    print("✅ COMPLETENESS CHECK COMPLETE")
    print("════════════════════════════════════════════════════════════════════════════════")


if __name__ == '__main__':
    main()
