#!/usr/bin/env python3
"""
Add _section metadata to source data files (Materials.yaml, Contaminants.yaml, etc.)

Core Principle 0.6 Compliance (Jan 5, 2026):
- ALL metadata must be in source data BEFORE export
- Export tasks only transform/format, NOT add data
- This script enriches source files with _section metadata from export configs
"""

import yaml
from pathlib import Path
from typing import Dict, Any

def load_section_metadata_from_config(config_path: str) -> Dict[str, Any]:
    """Load section_metadata definitions from export config"""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config.get('section_metadata', {})

def enrich_relationships_with_section_metadata(
    relationships: Dict[str, Any],
    section_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Add _section metadata to all relationship sections"""
    
    for category, sections in relationships.items():
        if not isinstance(sections, dict):
            continue
        
        for section_key, section_data in sections.items():
            if not isinstance(section_data, dict):
                continue
            
            # Skip if _section already exists
            if '_section' in section_data:
                continue
            
            # Try to get metadata from config (category.section_key format)
            metadata_key = f"{category}.{section_key}"
            metadata = section_metadata.get(metadata_key) or section_metadata.get(section_key)
            
            if metadata:
                # Add _section with camelCase naming per backend requirements
                section_data['_section'] = {
                    'sectionTitle': metadata.get('section_title'),
                    'sectionDescription': metadata.get('section_description'),
                    'icon': metadata.get('icon', 'circle-info'),
                    'order': metadata.get('order', 100),
                    'variant': metadata.get('variant', 'default')
                }
                
                # Add sectionMetadata if present (internal developer notes)
                if 'section_metadata' in metadata:
                    section_data['_section']['sectionMetadata'] = metadata['section_metadata']
    
    return relationships

def enrich_domain(domain: str, config_path: str, data_path: str):
    """Enrich source data file for a domain"""
    
    print(f"\n{'='*80}")
    print(f"Enriching {domain} source data with _section metadata")
    print(f"{'='*80}")
    
    # Load section metadata from export config
    section_metadata = load_section_metadata_from_config(config_path)
    print(f"Loaded {len(section_metadata)} section_metadata definitions from config")
    
    # Load source data
    with open(data_path) as f:
        data = yaml.safe_load(f)
    
    # Get the main data key (materials, contaminants, compounds, settings)
    if domain == 'setting':
        main_key = 'settings'
    else:
        main_key = f"{domain}s"
    
    if main_key not in data:
        main_key = domain
    
    items = data.get(main_key, {})
    if not isinstance(items, dict):
        print(f"❌ No items found in {main_key}")
        return
    
    # Track changes
    enriched_count = 0
    section_count = 0
    
    # Enrich each item
    for item_id, item_data in items.items():
        if 'relationships' in item_data and isinstance(item_data['relationships'], dict):
            before = sum(
                1 for category in item_data['relationships'].values()
                if isinstance(category, dict)
                for section in category.values()
                if isinstance(section, dict) and '_section' in section
            )
            
            item_data['relationships'] = enrich_relationships_with_section_metadata(
                item_data['relationships'],
                section_metadata
            )
            
            after = sum(
                1 for category in item_data['relationships'].values()
                if isinstance(category, dict)
                for section in category.values()
                if isinstance(section, dict) and '_section' in section
            )
            
            added = after - before
            if added > 0:
                enriched_count += 1
                section_count += added
    
    # Save enriched data
    with open(data_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Enriched {enriched_count} items with {section_count} _section metadata blocks")
    print(f"✅ Saved to {data_path}")

def main():
    """Enrich all domain source data files"""
    
    domains = [
        ('material', 'export/config/materials.yaml', 'data/materials/Materials.yaml'),
        ('contaminant', 'export/config/contaminants.yaml', 'data/contaminants/Contaminants.yaml'),
        ('compound', 'export/config/compounds.yaml', 'data/compounds/Compounds.yaml'),
        ('setting', 'export/config/settings.yaml', 'data/settings/Settings.yaml'),
    ]
    
    for domain, config_path, data_path in domains:
        if Path(config_path).exists() and Path(data_path).exists():
            enrich_domain(domain, config_path, data_path)
        else:
            print(f"⚠️  Skipping {domain}: config or data file not found")
    
    print(f"\n{'='*80}")
    print("✅ Source data enrichment complete!")
    print("   Next step: Re-export frontmatter to reflect enriched source data")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
