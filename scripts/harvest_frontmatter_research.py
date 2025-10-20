#!/usr/bin/env python3
"""
Harvest AI-researched properties from existing frontmatter files and write back to Materials.yaml.

This script extracts properties with source='ai_research' from generated frontmatter files
and persists them back to the Materials.yaml database to avoid re-researching.

Author: October 20, 2025
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def harvest_frontmatter_research():
    """Extract AI-researched properties from frontmatter and update Materials.yaml."""
    
    materials_file = Path("data/Materials.yaml")
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not materials_file.exists():
        print("❌ Materials.yaml not found")
        return False
    
    if not frontmatter_dir.exists():
        print("❌ Frontmatter directory not found")
        return False
    
    # Create backup
    backup_file = materials_file.with_suffix(
        f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    )
    shutil.copy2(materials_file, backup_file)
    print(f"📦 Backup created: {backup_file.name}")
    
    # Load Materials.yaml
    print("📂 Loading Materials.yaml...")
    with open(materials_file) as f:
        materials_data = yaml.safe_load(f)
    
    # Create name mapping from frontmatter abbreviations to Materials.yaml full names
    name_mapping = {
        'CFRP': 'Carbon Fiber Reinforced Polymer',
        'GFRP': 'Glass Fiber Reinforced Polymers GFRP',
        'FRPU': 'Fiber Reinforced Polyurethane FRPU',
        'MMCs': 'Metal Matrix Composites MMCs',
        'CMCs': 'Ceramic Matrix Composites CMCs',
        'PTFE': 'Polytetrafluoroethylene',
        'PVC': 'Polyvinyl Chloride'
    }
    
    # Statistics
    stats = {
        'files_processed': 0,
        'materials_updated': 0,
        'properties_added': 0,
        'properties_upgraded': 0,
        'properties_skipped': 0
    }
    
    # Process each frontmatter file
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.yaml"))
    print(f"\n🔍 Found {len(frontmatter_files)} frontmatter files")
    
    for fm_file in sorted(frontmatter_files):
        try:
            with open(fm_file) as f:
                frontmatter = yaml.safe_load(f)
            
            material_name = frontmatter.get('name')
            if not material_name:
                continue
            
            # Map abbreviated names to full Materials.yaml names
            lookup_name = name_mapping.get(material_name, material_name)
            
            # Check if material exists in Materials.yaml
            if lookup_name not in materials_data.get('materials', {}):
                print(f"⚠️  {material_name} (looked up as '{lookup_name}') not found in Materials.yaml, skipping...")
                continue
            
            material_entry = materials_data['materials'][lookup_name]
            
            
            # Ensure properties dict exists
            if 'properties' not in material_entry:
                material_entry['properties'] = {}
            
            # Extract AI-researched properties from frontmatter
            researched_props = {}
            material_props = frontmatter.get('materialProperties', {})
            
            for category_key, category_data in material_props.items():
                if not isinstance(category_data, dict):
                    continue
                    
                properties = category_data.get('properties', {})
                for prop_name, prop_data in properties.items():
                    if not isinstance(prop_data, dict):
                        continue
                    
                    # Check if this is AI-researched
                    source = prop_data.get('source', '')
                    if source == 'ai_research':
                        researched_props[prop_name] = {
                            'value': prop_data['value'],
                            'unit': prop_data['unit'],
                            'confidence': prop_data.get('confidence', 0.9),
                            'source': 'ai_research',
                            'research_date': prop_data.get('research_date', datetime.now().isoformat()),
                            'research_basis': prop_data.get('research_basis', 'ai_research_comprehensive')
                        }
            
            if not researched_props:
                continue
            
            # Update Materials.yaml with researched properties
            updates_count = 0
            upgrades_count = 0
            skipped_count = 0
            
            for prop_name, prop_data in researched_props.items():
                existing = material_entry['properties'].get(prop_name)
                
                if existing is None:
                    # New property - add it
                    material_entry['properties'][prop_name] = prop_data
                    updates_count += 1
                elif existing.get('source') != 'ai_research':
                    # Existing property but not from AI - upgrade it
                    material_entry['properties'][prop_name] = prop_data
                    upgrades_count += 1
                else:
                    # Already has AI research
                    skipped_count += 1
            
            if updates_count > 0 or upgrades_count > 0:
                print(f"✅ {material_name}: +{updates_count} new, ↑{upgrades_count} upgraded, ⏭️ {skipped_count} skipped")
                stats['materials_updated'] += 1
                stats['properties_added'] += updates_count
                stats['properties_upgraded'] += upgrades_count
            
            stats['properties_skipped'] += skipped_count
            stats['files_processed'] += 1
            
        except Exception as e:
            print(f"❌ Error processing {fm_file.name}: {e}")
            continue
    
    # Write updated Materials.yaml
    if stats['properties_added'] > 0 or stats['properties_upgraded'] > 0:
        print(f"\n💾 Writing updated Materials.yaml...")
        with open(materials_file, 'w') as f:
            yaml.dump(materials_data, f, default_flow_style=False, indent=2, sort_keys=False)
        print("✅ Materials.yaml updated successfully")
    else:
        print("\n⏭️  No updates needed - all properties already in Materials.yaml")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 HARVEST SUMMARY")
    print("="*70)
    print(f"Frontmatter files processed: {stats['files_processed']}")
    print(f"Materials updated: {stats['materials_updated']}")
    print(f"Properties added: {stats['properties_added']}")
    print(f"Properties upgraded: {stats['properties_upgraded']}")
    print(f"Properties skipped: {stats['properties_skipped']}")
    print(f"Backup saved: {backup_file.name}")
    print("="*70)
    
    return True


if __name__ == '__main__':
    harvest_frontmatter_research()
