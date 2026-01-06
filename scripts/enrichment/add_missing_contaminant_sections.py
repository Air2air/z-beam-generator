#!/usr/bin/env python3
"""
Add missing safety sections to contaminants source data.

Fixes Core Principle 0.6 violation where enrichers were creating these sections
at export time. Now they will exist in source data with complete _section metadata.

Sections to add:
1. fire_explosion_risk
2. fumes_generated
3. particulate_generation
4. ppe_requirements
5. toxic_gas_risk
6. ventilation_requirements
7. visibility_hazard
8. substrate_compatibility_warnings (if missing)
"""

import yaml
from pathlib import Path
from typing import Dict, Any

# Section definitions with complete _section metadata
MISSING_SECTIONS = {
    'fire_explosion_risk': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],  # Will be populated by enrichers during initial data generation
        '_section': {
            'sectionTitle': 'Fire & Explosion Risk',
            'sectionDescription': 'Fire and explosion hazards during laser cleaning',
            'icon': 'flame',
            'order': 21,
            'variant': 'warning'
        }
    },
    'fumes_generated': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],
        '_section': {
            'sectionTitle': 'Fumes Generated',
            'sectionDescription': 'Hazardous fumes produced during laser removal',
            'icon': 'cloud',
            'order': 22,
            'variant': 'warning'
        }
    },
    'particulate_generation': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],
        '_section': {
            'sectionTitle': 'Particulate Generation',
            'sectionDescription': 'Airborne particles and dust created during cleaning',
            'icon': 'wind',
            'order': 23,
            'variant': 'warning'
        }
    },
    'ppe_requirements': {
        'category': 'safety',
        'presentation': 'card',
        'items': [],
        '_section': {
            'sectionTitle': 'PPE Requirements',
            'sectionDescription': 'Required personal protective equipment',
            'icon': 'shield',
            'order': 24,
            'variant': 'default'
        }
    },
    'toxic_gas_risk': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],
        '_section': {
            'sectionTitle': 'Toxic Gas Risk',
            'sectionDescription': 'Toxic gases that may be released during removal',
            'icon': 'alert-triangle',
            'order': 25,
            'variant': 'danger'
        }
    },
    'ventilation_requirements': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],
        '_section': {
            'sectionTitle': 'Ventilation Requirements',
            'sectionDescription': 'Required ventilation and air filtration systems',
            'icon': 'wind',
            'order': 26,
            'variant': 'default'
        }
    },
    'visibility_hazard': {
        'category': 'safety',
        'presentation': 'descriptive',
        'items': [],
        '_section': {
            'sectionTitle': 'Visibility Hazard',
            'sectionDescription': 'Smoke and debris affecting operator visibility',
            'icon': 'eye-off',
            'order': 27,
            'variant': 'warning'
        }
    },
    'substrate_compatibility_warnings': {
        'category': 'safety',
        'presentation': 'card',
        'items': [],
        '_section': {
            'sectionTitle': 'Substrate Compatibility',
            'sectionDescription': 'Material compatibility warnings and precautions',
            'icon': 'alert-circle',
            'order': 28,
            'variant': 'warning'
        }
    }
}


def add_missing_sections(contaminant_data: Dict[str, Any]) -> int:
    """Add missing sections to contaminant relationships."""
    
    if 'relationships' not in contaminant_data:
        contaminant_data['relationships'] = {}
    
    added = 0
    
    for section_key, section_config in MISSING_SECTIONS.items():
        category = section_config['category']
        
        # Ensure category exists
        if category not in contaminant_data['relationships']:
            contaminant_data['relationships'][category] = {}
        
        # Skip if section already exists
        if section_key in contaminant_data['relationships'][category]:
            continue
        
        # Add section with metadata
        contaminant_data['relationships'][category][section_key] = {
            'presentation': section_config['presentation'],
            'items': section_config['items'],
            '_section': section_config['_section']
        }
        added += 1
    
    return added


def main():
    """Add missing sections to all contaminants."""
    
    contaminants_file = Path('data/contaminants/Contaminants.yaml')
    
    if not contaminants_file.exists():
        print(f"❌ File not found: {contaminants_file}")
        return 1
    
    print("📖 Loading contaminants source data...")
    with open(contaminants_file) as f:
        data = yaml.safe_load(f)
    
    total_added = 0
    total_contaminants = len(data['contaminants'])
    
    print(f"🔧 Processing {total_contaminants} contaminants...\n")
    
    # Process each contaminant
    for contaminant_key, contaminant_data in data['contaminants'].items():
        added = add_missing_sections(contaminant_data)
        if added > 0:
            print(f"  ✅ {contaminant_key}: Added {added} sections")
            total_added += added
    
    if total_added == 0:
        print("✅ All sections already exist in source data")
        return 0
    
    # Create backup
    backup_file = contaminants_file.with_suffix('.yaml.backup2')
    print(f"\n💾 Creating backup: {backup_file}")
    import shutil
    shutil.copy2(contaminants_file, backup_file)
    
    # Write updated data
    print(f"💾 Writing updated source data...")
    with open(contaminants_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=float('inf'))
    
    print(f"\n✅ COMPLETE")
    print(f"   Total sections added: {total_added}")
    print(f"   Sections per contaminant: {total_added // total_contaminants}")
    print(f"   Backup created: {backup_file}")
    
    print(f"\n📋 Verification:")
    print(f"   Each contaminant should now have 12-13 sections with _section metadata")
    print(f"\n📋 Next steps:")
    print(f"   1. Re-export contaminants: python3 run.py --export --domain contaminants")
    print(f"   2. Verify no sections added at export time (should preserve all from source)")
    print(f"   3. Check compliance: 100% sections should have _section metadata")
    
    return 0


if __name__ == '__main__':
    exit(main())
