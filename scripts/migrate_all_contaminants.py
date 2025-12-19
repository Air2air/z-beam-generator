#!/usr/bin/env python3
"""
Migrate All Contaminants to Library Enrichment System

Adds library relationship references to all contaminants in Contaminants.yaml.
Similar to migrate_all_materials.py but for contaminants domain.

Usage:
    python3 scripts/migrate_all_contaminants.py

Author: AI Assistant
Date: December 18, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def migrate_contaminants():
    """Add library relationships to all contaminants"""
    
    # Load contaminants data
    contaminants_path = Path('data/contaminants/Contaminants.yaml')
    print(f'📖 Loading {contaminants_path}...')
    
    with open(contaminants_path) as f:
        data = yaml.safe_load(f)
    
    contaminants = data['contamination_patterns']
    print(f'   Found {len(contaminants)} contaminants')
    
    # Track changes
    updated_count = 0
    
    # Add regulatory_standards to all contaminants
    for contaminant_id, contaminant_data in contaminants.items():
        # Initialize relationships dict if not exists
        if 'relationships' not in contaminant_data:
            contaminant_data['relationships'] = {}
        
        relationships = contaminant_data['relationships']
        
        # Add regulatory_standards if not exists
        if 'regulatory_standards' not in relationships:
            # All laser cleaning operations require these 2 core standards
            relationships['regulatory_standards'] = [
                {'type': 'regulatory_standards', 'id': 'osha-ppe-requirements'},
                {'type': 'regulatory_standards', 'id': 'ansi-z136-1-laser-safety'}
            ]
            updated_count += 1
        
        # Preserve existing related_contaminants, produces_compounds, etc.
        # The relationships dict now has BOTH old linkages AND new library relationships
    
    print(f'\n✅ Updated {updated_count} contaminants with regulatory_standards')
    
    # Save back to file
    print(f'\n💾 Saving to {contaminants_path}...')
    with open(contaminants_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print('✅ Migration complete!')
    print(f'\nNext steps:')
    print(f'1. Update export/config/contaminants.yaml with library_enrichments section')
    print(f'2. Verify regulatory enricher is configured for dict-based library')
    print(f'3. Export contaminants and verify regulatory_standards_detail appears')


if __name__ == '__main__':
    migrate_contaminants()
