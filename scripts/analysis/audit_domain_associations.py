#!/usr/bin/env python3
"""
Phase 1: Association Auditor
Analyzes current DomainAssociations.yaml and identifies gaps.
"""

import sys
import yaml
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_yaml(file_path):
    """Load YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}

def main():
    print("=" * 80)
    print("PHASE 1: DOMAIN ASSOCIATIONS AUDIT")
    print("=" * 80)
    print()
    
    # Load all data files
    print("📁 Loading data files...")
    materials = load_yaml(project_root / "data/materials/Materials.yaml")
    contaminants_data = load_yaml(project_root / "data/contaminants/Contaminants.yaml")
    compounds = load_yaml(project_root / "data/compounds/Compounds.yaml")
    settings = load_yaml(project_root / "data/settings/Settings.yaml")
    associations = load_yaml(project_root / "data/associations/DomainAssociations.yaml")
    
    # Extract correct keys
    contaminants = contaminants_data.get('contamination_patterns', {})
    
    print(f"   Materials: {len(materials.get('materials', {}))} items")
    print(f"   Contaminants: {len(contaminants)} items")
    print(f"   Compounds: {len(compounds.get('compounds', {}))} items")
    print(f"   Settings: {len(settings.get('settings', {}))} items")
    print()
    
    # Extract relationship types
    print("📊 Current Association Coverage:")
    print("-" * 80)
    
    relationship_types = {
        'material_to_contaminant': 0,
        'material_to_compound': 0,
        'material_to_setting': 0,
        'contaminant_to_material': 0,
        'compound_to_material': 0,
        'setting_to_material': 0
    }
    
    # Count existing relationships
    for rel_type in relationship_types.keys():
        if rel_type in associations:
            for source, targets in associations[rel_type].items():
                if isinstance(targets, list):
                    relationship_types[rel_type] += len(targets)
                else:
                    relationship_types[rel_type] += 1
    
    total_current = sum(relationship_types.values())
    
    for rel_type, count in relationship_types.items():
        print(f"   {rel_type}: {count} relationships")
    
    print(f"\n   TOTAL CURRENT RELATIONSHIPS: {total_current}")
    print()
    
    # Calculate expected relationships
    print("🎯 Expected Relationships (Full Population):")
    print("-" * 80)
    
    num_materials = len(materials.get('materials', {}))
    num_contaminants = len(contaminants)
    num_compounds = len(compounds.get('compounds', {}))
    num_settings = len(settings.get('settings', {}))
    
    # Estimates based on analysis
    expected = {
        'material_to_contaminant': num_materials * 8,  # avg 8 contaminants per material
        'material_to_compound': num_materials * 3,     # avg 3 compounds per material
        'material_to_setting': num_materials * 1,      # 1:1 mapping
        'contaminant_to_material': num_contaminants * 12,  # avg 12 materials per contaminant
        'compound_to_material': num_compounds * 12,    # avg 12 materials per compound
        'setting_to_material': num_settings * 1        # 1:1 mapping
    }
    
    total_expected = sum(expected.values())
    
    for rel_type, count in expected.items():
        current = relationship_types[rel_type]
        coverage = (current / count * 100) if count > 0 else 0
        print(f"   {rel_type}: {count} expected, {current} current ({coverage:.1f}% coverage)")
    
    print(f"\n   TOTAL EXPECTED RELATIONSHIPS: {total_expected}")
    print(f"   CURRENT COVERAGE: {total_current}/{total_expected} ({total_current/total_expected*100:.1f}%)")
    print(f"   GAP: {total_expected - total_current} relationships missing")
    print()
    
    # Identify orphaned items
    print("🔍 Orphaned Items Analysis:")
    print("-" * 80)
    
    # Materials with no relationships
    material_links = defaultdict(int)
    for rel_type in ['material_to_contaminant', 'material_to_compound', 'material_to_setting']:
        if rel_type in associations:
            for material in associations[rel_type].keys():
                material_links[material] += 1
    
    orphaned_materials = [m for m in materials.get('materials', {}).keys() if m not in material_links]
    orphan_pct = (len(orphaned_materials)/num_materials*100) if num_materials > 0 else 0
    print(f"   Orphaned Materials: {len(orphaned_materials)}/{num_materials} ({orphan_pct:.1f}%)")
    
    # Contaminants with no relationships
    contaminant_links = defaultdict(int)
    if 'contaminant_to_material' in associations:
        for contaminant in associations['contaminant_to_material'].keys():
            contaminant_links[contaminant] += 1
    
    orphaned_contaminants = [c for c in contaminants.keys() if c not in contaminant_links]
    orphan_pct = (len(orphaned_contaminants)/num_contaminants*100) if num_contaminants > 0 else 0
    print(f"   Orphaned Contaminants: {len(orphaned_contaminants)}/{num_contaminants} ({orphan_pct:.1f}%)")
    
    # Compounds with no relationships
    compound_links = defaultdict(int)
    if 'compound_to_material' in associations:
        for compound in associations['compound_to_material'].keys():
            compound_links[compound] += 1
    
    orphaned_compounds = [c for c in compounds.get('compounds', {}).keys() if c not in compound_links]
    orphan_pct = (len(orphaned_compounds)/num_compounds*100) if num_compounds > 0 else 0
    print(f"   Orphaned Compounds: {len(orphaned_compounds)}/{num_compounds} ({orphan_pct:.1f}%)")
    
    # Settings orphans (should be 0 since 1:1 mapping)
    setting_links = defaultdict(int)
    if 'setting_to_material' in associations:
        for setting in associations['setting_to_material'].keys():
            setting_links[setting] += 1
    
    orphaned_settings = [s for s in settings.get('settings', {}).keys() if s not in setting_links]
    orphan_pct = (len(orphaned_settings)/num_settings*100) if num_settings > 0 else 0
    print(f"   Orphaned Settings: {len(orphaned_settings)}/{num_settings} ({orphan_pct:.1f}%)")
    
    total_orphaned = len(orphaned_materials) + len(orphaned_contaminants) + len(orphaned_compounds) + len(orphaned_settings)
    total_items = num_materials + num_contaminants + num_compounds + num_settings
    
    print(f"\n   TOTAL ORPHANED ITEMS: {total_orphaned}/{total_items} ({total_orphaned/total_items*100:.1f}%)")
    print()
    
    # Save missing relationships report
    print("💾 Saving detailed gap report...")
    
    gap_report = {
        'timestamp': '2025-12-20',
        'summary': {
            'total_current_relationships': total_current,
            'total_expected_relationships': total_expected,
            'gap': total_expected - total_current,
            'coverage_percent': round(total_current/total_expected*100, 1)
        },
        'by_relationship_type': {},
        'orphaned_items': {
            'materials': orphaned_materials,
            'contaminants': orphaned_contaminants,
            'compounds': orphaned_compounds,
            'settings': orphaned_settings
        }
    }
    
    for rel_type in relationship_types.keys():
        gap_report['by_relationship_type'][rel_type] = {
            'current': relationship_types[rel_type],
            'expected': expected[rel_type],
            'gap': expected[rel_type] - relationship_types[rel_type],
            'coverage_percent': round((relationship_types[rel_type] / expected[rel_type] * 100) if expected[rel_type] > 0 else 0, 1)
        }
    
    output_file = project_root / "ASSOCIATION_AUDIT_REPORT_DEC20_2025.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(gap_report, f, default_flow_style=False, sort_keys=False)
    
    print(f"   Saved: {output_file}")
    print()
    
    print("=" * 80)
    print("✅ PHASE 1 COMPLETE")
    print("=" * 80)
    print(f"\n📊 KEY FINDINGS:")
    print(f"   • Current relationships: {total_current}")
    print(f"   • Expected relationships: {total_expected}")
    print(f"   • Coverage: {total_current/total_expected*100:.1f}%")
    print(f"   • Orphaned items: {total_orphaned} ({total_orphaned/total_items*100:.1f}%)")
    print(f"\n📁 Next: Phase 2 will auto-populate {total_expected - total_current} missing relationships")
    print()

if __name__ == '__main__':
    main()
