"""
Batch Migration: Convert All Compounds to Library Relationships

Migrates all 20 compounds from full duplicated data to compact library references.
"""

import sys
from pathlib import Path
import yaml
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Mapping of hazard characteristics to PPE library IDs
PPE_MAPPING = {
    ('irritant_gas', 'low'): 'irritant-gas-low-concentration',
    ('irritant_gas', 'high'): 'irritant-gas-high-concentration',
    ('particulate', 'carcinogen'): 'particulate-carcinogen',
    ('corrosive_liquid', 'moderate'): 'corrosive-liquid-moderate',
    ('flammable_vapor', 'high'): 'flammable-vapor-high',
}

# Mapping of hazard types to emergency response library IDs
EMERGENCY_MAPPING = {
    'flammable_gas_extreme': 'flammable-gas-extremely',
    'corrosive_liquid_strong': 'corrosive-liquid-strong',
    'toxic_gas_extreme': 'toxic-gas-extreme',
}


def determine_ppe_template(compound: Dict[str, Any]) -> str:
    """Determine appropriate PPE template based on compound characteristics."""
    category = compound.get('category', '')
    hazard_class = compound.get('hazard_class', '')
    
    # Map based on category and hazard
    if 'toxic_gas' in category or 'irritant_gas' in category:
        # Check concentration thresholds in exposure limits
        exposure = compound.get('exposure_limits', {})
        pel_ppm = exposure.get('osha_pel_ppm', 0)
        
        if pel_ppm and pel_ppm < 25:
            return 'irritant-gas-high-concentration'
        else:
            return 'irritant-gas-low-concentration'
    
    elif 'particulate' in category or 'carcinogen' in hazard_class:
        return 'particulate-carcinogen'
    
    elif 'corrosive' in category or 'corrosive' in hazard_class:
        return 'corrosive-liquid-moderate'
    
    elif 'flammable' in category or hazard_class == 'flammable':
        return 'flammable-vapor-high'
    
    # Default
    return 'irritant-gas-low-concentration'


def determine_emergency_template(compound: Dict[str, Any]) -> str:
    """Determine appropriate emergency response template."""
    physical_props = compound.get('physical_properties', {})
    flash_point_str = physical_props.get('flash_point', '')
    
    category = compound.get('category', '')
    hazard_class = compound.get('hazard_class', '')
    
    # Check flash point for flammable classification
    if 'gas' in category and ('flammable' in hazard_class or 'flammable' in category):
        return 'flammable-gas-extremely'
    
    # Check for corrosive
    if 'corrosive' in category or 'corrosive' in hazard_class:
        return 'corrosive-liquid-strong'
    
    # Check for toxic gas with low IDLH
    if 'toxic' in category and 'gas' in category:
        return 'toxic-gas-extreme'
    
    # Default to flammable (most common in laser fumes)
    return 'flammable-gas-extremely'


def add_relationships_to_compound(compound_id: str, compound: Dict[str, Any]) -> Dict[str, Any]:
    """Add library relationships to a compound entry."""
    
    # Determine appropriate library templates
    ppe_id = determine_ppe_template(compound)
    emergency_id = determine_emergency_template(compound)
    
    # Create relationships structure
    relationships = {
        'chemical_properties': [{
            'type': 'chemical_properties',
            'id': f'{compound_id}-physical-data',
        }],
        'health_effects': [{
            'type': 'health_effects',
            'id': f'{compound_id}-toxicology',
        }],
        'environmental_impact': [{
            'type': 'environmental_impact',
            'id': f'{compound_id}-environmental-data',
        }],
        'detection_monitoring': [{
            'type': 'detection_monitoring',
            'id': f'{compound_id}-monitoring-methods',
        }],
        'ppe_requirements': [{
            'type': 'ppe_requirements',
            'id': ppe_id,
            'overrides': {
                'specific_compound': compound.get('name', compound_id),
            }
        }],
        'emergency_response': [{
            'type': 'emergency_response',
            'id': emergency_id,
            'overrides': {
                'specific_compound': compound.get('name', compound_id),
            }
        }]
    }
    
    # Add overrides from exposure limits if available
    if 'exposure_limits' in compound:
        exposure = compound['exposure_limits']
        if 'osha_pel_ppm' in exposure:
            relationships['ppe_requirements'][0]['overrides']['pel_ppm'] = exposure['osha_pel_ppm']
    
    return relationships


def migrate_all_compounds():
    """Migrate all compounds to library relationships."""
    
    print("=" * 80)
    print("BATCH MIGRATION: All Compounds → Library Relationships")
    print("=" * 80)
    print()
    
    # Load Compounds.yaml
    compounds_file = project_root / 'data' / 'compounds' / 'Compounds.yaml'
    print(f"Loading: {compounds_file}")
    
    with open(compounds_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    compounds = data.get('compounds', {})
    total = len(compounds)
    print(f"✅ Found {total} compounds")
    print()
    
    # Backup original file
    backup_file = compounds_file.with_suffix('.yaml.pre-migration-backup')
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ Backup created")
    print()
    
    # Migrate each compound
    print("Migrating compounds:")
    migrated = 0
    skipped = 0
    
    for compound_id, compound in compounds.items():
        # Skip if already has library relationships
        rels = compound.get('relationships', {})
        has_library_rels = any(k in rels for k in ['chemical_properties', 'health_effects', 'environmental_impact',
                                                     'detection_monitoring', 'ppe_requirements', 'emergency_response'])
        if has_library_rels:
            print(f"  ⏭️  {compound_id} (already has library relationships)")
            skipped += 1
            continue
        
        # Add relationships
        relationships = add_relationships_to_compound(compound_id, compound)
        
        # Merge with existing relationships (preserve old linkages)
        if 'relationships' not in compound:
            compound['relationships'] = {}
        compound['relationships'].update(relationships)
        
        # Show PPE and emergency templates assigned
        ppe_id = relationships['ppe_requirements'][0]['id']
        emerg_id = relationships['emergency_response'][0]['id']
        print(f"  ✅ {compound_id}")
        print(f"      PPE: {ppe_id}")
        print(f"      Emergency: {emerg_id}")
        
        migrated += 1
    
    print()
    print(f"Migrated: {migrated}/{total}")
    print(f"Skipped: {skipped}/{total}")
    print()
    
    # Save updated file
    print(f"Saving updated file: {compounds_file}")
    with open(compounds_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ File saved")
    print()
    
    print("=" * 80)
    print("✅ BATCH MIGRATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print(f"1. Review relationships in {compounds_file}")
    print("2. Test enrichment: python3 scripts/test_enrichment.py")
    print("3. Export all: python3 run.py --export --domain compounds --all")
    print("4. Verify enriched output in ../z-beam/frontmatter/compounds/")
    print()
    print("To restore original:")
    print(f"  cp {backup_file} {compounds_file}")
    print()


if __name__ == '__main__':
    migrate_all_compounds()
