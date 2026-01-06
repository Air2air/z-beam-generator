#!/usr/bin/env python3
"""
Normalize industry_applications in Materials.yaml

PROBLEM:
- Applications stored at top-level 'applications' field
- Should be at 'operational.industry_applications'
- Should be in card format (not simple list)

SOLUTION:
1. Move applications → operational.industry_applications
2. Convert to card format structure
3. Remove top-level applications field

COMPLIANCE:
- Core Principle 0.6: Generate complete data at source
- Eliminates need for normalize_applications export task
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any


def convert_to_card_format(applications: List[str]) -> Dict[str, Any]:
    """
    Convert simple list to card format.
    
    Input: ['Aerospace', 'Automotive', 'Medical']
    Output: {
        'presentation': 'card',
        'items': [
            {
                'title': 'Aerospace',
                'description': '...',
                'metadata': {...},
                'order': 1
            }
        ]
    }
    """
    if not isinstance(applications, list):
        return applications
    
    items = []
    for idx, app_name in enumerate(applications):
        if not isinstance(app_name, str):
            continue
        
        # Generate brief description
        description = f"{app_name} industry applications and manufacturing requirements for laser cleaning."
        
        items.append({
            'title': app_name,
            'description': description,
            'metadata': {
                'category': 'Industrial Applications',
                'commonality': 'common'
            },
            'order': idx + 1
        })
    
    return {
        'presentation': 'card',
        'items': items
    }


def normalize_materials(dry_run: bool = True) -> None:
    """Normalize all materials in Materials.yaml"""
    
    materials_file = Path('data/materials/Materials.yaml')
    
    if not materials_file.exists():
        print("❌ Materials.yaml not found")
        return
    
    # Load data
    with open(materials_file) as f:
        data = yaml.safe_load(f)
    
    materials_updated = 0
    
    for key, material in data['materials'].items():
        # Check if has top-level applications
        if 'applications' not in material:
            continue
        
        applications = material['applications']
        
        # Ensure operational section exists
        if 'operational' not in material:
            material['operational'] = {}
        
        # Convert to card format
        card_data = convert_to_card_format(applications)
        
        # Move to correct location
        material['operational']['industry_applications'] = card_data
        
        # Remove top-level field
        del material['applications']
        
        materials_updated += 1
        
        if not dry_run:
            print(f"✅ {key}: Moved {len(applications)} applications → operational.industry_applications (card format)")
        else:
            print(f"🔍 {key}: Would move {len(applications)} applications → operational.industry_applications")
    
    # Save if not dry run
    if not dry_run and materials_updated > 0:
        with open(materials_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"\n✅ Updated {materials_updated} materials in Materials.yaml")
    else:
        print(f"\n🔍 DRY RUN: Would update {materials_updated} materials")
        print("Run with --execute to apply changes")


if __name__ == '__main__':
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("Add --execute flag to apply changes\n")
    else:
        print("⚠️  EXECUTE MODE - Changes will be written to Materials.yaml\n")
    
    normalize_materials(dry_run=dry_run)
