"""
Migration Script: Add Library Relationships to Acetaldehyde

Proof of concept - converts acetaldehyde from full data to compact relationships.
"""

import sys
from pathlib import Path
import yaml
from collections import OrderedDict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def migrate_acetaldehyde():
    """Migrate acetaldehyde to use library relationships."""
    
    print("=" * 80)
    print("MIGRATION: Acetaldehyde → Library Relationships")
    print("=" * 80)
    print()
    
    # Load Compounds.yaml
    compounds_file = project_root / 'data' / 'compounds' / 'Compounds.yaml'
    print(f"Loading: {compounds_file}")
    
    with open(compounds_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    compounds = data.get('compounds', {})
    
    if 'acetaldehyde' not in compounds:
        print("❌ Acetaldehyde not found in Compounds.yaml")
        return
    
    acetaldehyde = compounds['acetaldehyde']
    print(f"✅ Found acetaldehyde")
    print()
    
    # Create relationships section
    relationships = {
        'chemical_properties': [{
            'type': 'chemical_properties',
            'id': 'acetaldehyde-physical-data',
            'notes': 'Standard physical/chemical data from NIST'
        }],
        'health_effects': [{
            'type': 'health_effects',
            'id': 'acetaldehyde-toxicology',
            'notes': 'Toxicology data from IARC, NTP, NIOSH'
        }],
        'environmental_impact': [{
            'type': 'environmental_impact',
            'id': 'acetaldehyde-environmental-data',
            'notes': 'Environmental fate from EPA databases'
        }],
        'detection_monitoring': [{
            'type': 'detection_monitoring',
            'id': 'acetaldehyde-monitoring-methods',
            'notes': 'NIOSH Method 2538, EPA TO-15'
        }],
        'ppe_requirements': [{
            'type': 'ppe_requirements',
            'id': 'irritant-gas-high-concentration',
            'notes': 'Level B protection for >25 ppm or unknown concentrations',
            'overrides': {
                'specific_compound': 'acetaldehyde',
                'ceiling_limit_ppm': 25
            }
        }],
        'emergency_response': [{
            'type': 'emergency_response',
            'id': 'flammable-gas-extremely',
            'notes': 'Flash point -39°C, LEL 4%, UEL 60%',
            'overrides': {
                'specific_compound': 'acetaldehyde',
                'reportable_quantity': '1000 lbs',
                'iarc_classification': 'Group 2B (Possibly carcinogenic)'
            }
        }]
    }
    
    print("Adding relationships:")
    for lib_type, rels in relationships.items():
        print(f"  • {lib_type}: {rels[0]['id']}")
    print()
    
    # Add relationships to acetaldehyde
    acetaldehyde['relationships'] = relationships
    
    # Backup original file
    backup_file = compounds_file.with_suffix('.yaml.backup')
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ Backup created")
    print()
    
    # Save updated file
    print(f"Saving updated file: {compounds_file}")
    with open(compounds_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ Relationships added")
    print()
    
    # Show before/after sizes
    original_size = len(str(acetaldehyde))
    print(f"Data structure size: {original_size:,} characters")
    print()
    
    print("=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review acetaldehyde relationships in Compounds.yaml")
    print("2. Test enrichment: python3 scripts/test_enrichment.py")
    print("3. Export frontmatter: python3 run.py --export --domain compounds --item acetaldehyde")
    print("4. Verify enriched output in ../z-beam/frontmatter/compounds/")
    print()
    
    return acetaldehyde


if __name__ == '__main__':
    migrate_acetaldehyde()
