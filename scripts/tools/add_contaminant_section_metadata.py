#!/usr/bin/env python3
"""
Add _section metadata to contaminants source data.

This fixes the architectural violation where section metadata was being added
at export/build time. Per Rule 0.6: No Build-Time Data Enhancement, all metadata
must exist in source data files, not be created during export.

This script adds complete _section blocks to all relationship sections in
data/contaminants/Contaminants.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Section metadata definitions (from export/config/contaminants.yaml)
SECTION_METADATA = {
    'regulatory_standards': {
        'sectionTitle': 'Regulatory Standards',
        'sectionDescription': 'Safety regulations and compliance standards for this contaminant',
        'icon': 'shield-check',
        'order': 20,
        'variant': 'default'
    },
    'exposure_limits': {
        'sectionTitle': 'Exposure Limits',
        'sectionDescription': 'Permissible exposure limits and safety thresholds',
        'icon': 'alert-triangle',
        'order': 21,
        'variant': 'warning'
    },
    'ppe_requirements': {
        'sectionTitle': 'PPE Requirements',
        'sectionDescription': 'Required personal protective equipment',
        'icon': 'shield',
        'order': 22,
        'variant': 'default'
    },
    'health_effects': {
        'sectionTitle': 'Health Effects',
        'sectionDescription': 'Known health impacts and medical considerations',
        'icon': 'heart-pulse',
        'order': 23,
        'variant': 'warning'
    },
    'first_aid': {
        'sectionTitle': 'First Aid Measures',
        'sectionDescription': 'Emergency response and first aid procedures',
        'icon': 'cross',
        'order': 24,
        'variant': 'info'
    },
    'storage_handling': {
        'sectionTitle': 'Storage & Handling',
        'sectionDescription': 'Safe storage and handling procedures',
        'icon': 'package',
        'order': 25,
        'variant': 'default'
    },
    'disposal': {
        'sectionTitle': 'Disposal Methods',
        'sectionDescription': 'Proper disposal and waste management procedures',
        'icon': 'trash-2',
        'order': 26,
        'variant': 'default'
    },
    'emergency_procedures': {
        'sectionTitle': 'Emergency Procedures',
        'sectionDescription': 'Emergency response protocols and spill procedures',
        'icon': 'siren',
        'order': 27,
        'variant': 'warning'
    },
    'fire_explosion_risk': {
        'sectionTitle': 'Fire & Explosion Risk',
        'sectionDescription': 'Fire hazards and explosion risks',
        'icon': 'flame',
        'order': 28,
        'variant': 'warning'
    },
    'produces_compounds': {
        'sectionTitle': 'Produced Compounds',
        'sectionDescription': 'Hazardous compounds produced during laser cleaning',
        'icon': 'flask-conical',
        'order': 10,
        'variant': 'warning'
    },
    'affects_materials': {
        'sectionTitle': 'Affected Materials',
        'sectionDescription': 'Materials where this contaminant commonly appears',
        'icon': 'layers',
        'order': 11,
        'variant': 'default'
    },
    'appearance_on_categories': {
        'sectionTitle': 'Visual Appearance',
        'sectionDescription': 'How this contaminant appears on different material categories',
        'icon': 'eye',
        'order': 50,
        'variant': 'default'
    },
    'laser_properties': {
        'sectionTitle': 'Laser Removal Properties',
        'sectionDescription': 'Laser parameters and removal characteristics',
        'icon': 'zap',
        'order': 40,
        'variant': 'default'
    }
}


def add_section_metadata(contaminant_data: Dict[str, Any]) -> int:
    """
    Add _section metadata to all relationship sections.
    
    Returns:
        Number of sections updated
    """
    updated = 0
    
    if 'relationships' not in contaminant_data:
        return 0
    
    for category, sections in contaminant_data['relationships'].items():
        if not isinstance(sections, dict):
            continue
            
        for section_key, section_data in sections.items():
            if not isinstance(section_data, dict):
                continue
            
            # Skip if already has _section
            if '_section' in section_data:
                continue
            
            # Get metadata for this section
            if section_key not in SECTION_METADATA:
                print(f"  ⚠️  No metadata defined for section: {category}.{section_key}")
                continue
            
            # Add _section block
            section_data['_section'] = SECTION_METADATA[section_key].copy()
            updated += 1
    
    return updated


def main():
    """Add section metadata to contaminants source data."""
    
    contaminants_file = Path('data/contaminants/Contaminants.yaml')
    
    if not contaminants_file.exists():
        print(f"❌ File not found: {contaminants_file}")
        return 1
    
    # Load source data
    print("📖 Loading contaminants source data...")
    with open(contaminants_file) as f:
        data = yaml.safe_load(f)
    
    total_updated = 0
    total_contaminants = len(data['contaminants'])
    
    print(f"🔧 Processing {total_contaminants} contaminants...\n")
    
    # Process each contaminant
    for contaminant_key, contaminant_data in data['contaminants'].items():
        updated = add_section_metadata(contaminant_data)
        if updated > 0:
            print(f"  ✅ {contaminant_key}: Added {updated} _section blocks")
            total_updated += updated
    
    # Create backup
    backup_file = contaminants_file.with_suffix('.yaml.backup')
    print(f"\n💾 Creating backup: {backup_file}")
    with open(backup_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Write updated data
    print(f"💾 Writing updated source data...")
    with open(contaminants_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n✅ COMPLETE")
    print(f"   Total sections updated: {total_updated}")
    print(f"   Backup created: {backup_file}")
    print(f"\n📋 Next steps:")
    print(f"   1. Remove section_metadata task from export/config/contaminants.yaml")
    print(f"   2. Re-export contaminants: python3 run.py --export --domain contaminants")
    print(f"   3. Verify frontmatter preserves _section metadata from source")
    
    return 0


if __name__ == '__main__':
    exit(main())
