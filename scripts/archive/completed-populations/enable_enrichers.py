#!/usr/bin/env python3
"""
Phase 3: Enable Enrichers
Updates export config files to enable all relationship enrichers.
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_yaml(file_path):
    """Load YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}

def save_yaml(data, file_path):
    """Save YAML file"""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def main():
    print("=" * 80)
    print("PHASE 3: ENABLE ENRICHERS")
    print("=" * 80)
    print()
    
    configs_updated = 0
    
    # Materials enricher config
    print("📝 Updating export/config/materials.yaml...")
    materials_config = load_yaml(project_root / "export/config/materials.yaml")
    
    # Ensure enrichers section exists
    if 'enrichers' not in materials_config:
        materials_config['enrichers'] = []
    
    # Find or add DomainLinkagesEnricher
    linkage_enricher = None
    for enricher in materials_config['enrichers']:
        if enricher.get('name') == 'DomainLinkagesEnricher':
            linkage_enricher = enricher
            break
    
    if not linkage_enricher:
        linkage_enricher = {'name': 'DomainLinkagesEnricher', 'enabled': True, 'config': {}}
        materials_config['enrichers'].append(linkage_enricher)
    
    linkage_enricher['enabled'] = True
    if 'config' not in linkage_enricher:
        linkage_enricher['config'] = {}
    
    linkage_enricher['config']['relationship_types'] = [
        'related_settings',
        'removes_contaminants',
        'produces_compounds'
    ]
    
    save_yaml(materials_config, project_root / "export/config/materials.yaml")
    configs_updated += 1
    print("   ✅ Enabled: related_settings, removes_contaminants, produces_compounds")
    print()
    
    # Contaminants enricher config
    print("📝 Updating export/config/contaminants.yaml...")
    contaminants_config = load_yaml(project_root / "export/config/contaminants.yaml")
    
    if 'enrichers' not in contaminants_config:
        contaminants_config['enrichers'] = []
    
    linkage_enricher = None
    for enricher in contaminants_config['enrichers']:
        if enricher.get('name') == 'DomainLinkagesEnricher':
            linkage_enricher = enricher
            break
    
    if not linkage_enricher:
        linkage_enricher = {'name': 'DomainLinkagesEnricher', 'enabled': True, 'config': {}}
        contaminants_config['enrichers'].append(linkage_enricher)
    
    linkage_enricher['enabled'] = True
    if 'config' not in linkage_enricher:
        linkage_enricher['config'] = {}
    
    linkage_enricher['config']['relationship_types'] = [
        'affects_materials',
        'found_on_materials'
    ]
    
    save_yaml(contaminants_config, project_root / "export/config/contaminants.yaml")
    configs_updated += 1
    print("   ✅ Enabled: affects_materials, found_on_materials")
    print()
    
    # Compounds enricher config
    print("📝 Updating export/config/compounds.yaml...")
    compounds_config = load_yaml(project_root / "export/config/compounds.yaml")
    
    if 'enrichers' not in compounds_config:
        compounds_config['enrichers'] = []
    
    linkage_enricher = None
    for enricher in compounds_config['enrichers']:
        if enricher.get('name') == 'DomainLinkagesEnricher':
            linkage_enricher = enricher
            break
    
    if not linkage_enricher:
        linkage_enricher = {'name': 'DomainLinkagesEnricher', 'enabled': True, 'config': {}}
        compounds_config['enrichers'].append(linkage_enricher)
    
    linkage_enricher['enabled'] = True
    if 'config' not in linkage_enricher:
        linkage_enricher['config'] = {}
    
    linkage_enricher['config']['relationship_types'] = [
        'produced_by_materials'
    ]
    
    save_yaml(compounds_config, project_root / "export/config/compounds.yaml")
    configs_updated += 1
    print("   ✅ Enabled: produced_by_materials")
    print()
    
    # Settings enricher config
    print("📝 Updating export/config/settings.yaml...")
    settings_config = load_yaml(project_root / "export/config/settings.yaml")
    
    if 'enrichers' not in settings_config:
        settings_config['enrichers'] = []
    
    linkage_enricher = None
    for enricher in settings_config['enrichers']:
        if enricher.get('name') == 'DomainLinkagesEnricher':
            linkage_enricher = enricher
            break
    
    if not linkage_enricher:
        linkage_enricher = {'name': 'DomainLinkagesEnricher', 'enabled': True, 'config': {}}
        settings_config['enrichers'].append(linkage_enricher)
    
    linkage_enricher['enabled'] = True
    if 'config' not in linkage_enricher:
        linkage_enricher['config'] = {}
    
    linkage_enricher['config']['relationship_types'] = [
        'applies_to_materials',
        'effective_against_contaminants'
    ]
    
    save_yaml(settings_config, project_root / "export/config/settings.yaml")
    configs_updated += 1
    print("   ✅ Enabled: applies_to_materials, effective_against_contaminants")
    print()
    
    print("=" * 80)
    print("✅ PHASE 3 COMPLETE")
    print("=" * 80)
    print(f"\n📊 CONFIGS UPDATED: {configs_updated}")
    print(f"   • Materials: 3 relationship types enabled")
    print(f"   • Contaminants: 2 relationship types enabled")
    print(f"   • Compounds: 1 relationship type enabled")
    print(f"   • Settings: 2 relationship types enabled")
    print(f"\n📁 Next: Phase 4 will create comprehensive link validator")
    print()

if __name__ == '__main__':
    main()
