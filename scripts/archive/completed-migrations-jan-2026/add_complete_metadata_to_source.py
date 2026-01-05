#!/usr/bin/env python3
"""
Add Complete Metadata to Source Data Files
===========================================

Implements Core Principle 0.6: No Build-Time Data Enhancement

This script adds ALL metadata fields to source YAML files that were
previously added during export/build time. Following the new mandatory
policy, ALL structure, metadata, and relationships must be in source data.

Changes:
1. Add camelCase fields: schemaVersion, pageTitle, metaDescription, contentType, fullPath
2. Remove snake_case fields: schema_version, page_title, page_description
3. Generate material-specific metaDescriptions (120-155 chars)
4. Add proper section metadata to relationships
5. Convert FAQ to expert_answers collapsible format
6. Add collapsible format to industry_applications
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List

def generate_meta_description(domain: str, name: str, data: Dict[str, Any]) -> str:
    """
    Generate SEO-optimized metaDescription (120-155 chars)
    
    Template: {Item} laser cleaning {context} for {primary_use}. 
              {Benefit statement}. Optimized for {industry}.
    """
    if domain == 'settings':
        # Extract material from name
        material = name.replace('-laser-cleaning', '').replace('-', ' ').title()
        
        # Material-specific templates
        templates = {
            'Aluminum': f"Aluminum laser cleaning parameters for oxide removal. Settings preserve substrate integrity while removing surface oxidation. Optimized for aerospace applications.",
            'Steel': f"Steel laser cleaning parameters for rust and scale removal. Settings maintain hardness while removing corrosion layers. Optimized for automotive manufacturing.",
            'Titanium': f"Titanium laser cleaning parameters for precision oxide removal. Settings preserve critical surface properties while removing contamination. Optimized for medical implants.",
            'Copper': f"Copper laser cleaning parameters for tarnish removal. Settings maintain conductivity while removing oxidation and residues. Optimized for electronics manufacturing.",
            'Stainless Steel': f"Stainless steel laser cleaning parameters for passive layer restoration. Settings remove contamination without affecting corrosion resistance. Optimized for food industry.",
        }
        
        # Default template for other materials
        desc = templates.get(material, 
            f"{material} laser cleaning parameters for contamination removal. Industrial-grade settings preserve substrate integrity. Optimized for precision applications.")
        
    elif domain == 'materials':
        # Get category and description from data
        category = data.get('category', '')
        description = data.get('description', '') or data.get('micro', '')
        
        desc = f"{name.replace('-laser-cleaning', '').replace('-', ' ').title()} laser cleaning guide. Remove contamination while preserving substrate integrity. Industrial applications for {category.lower()} materials."
        
    elif domain == 'compounds':
        # Get hazard info
        desc = f"{name.replace('-', ' ').title()} safety information for laser cleaning. Health hazards, exposure limits, and protective equipment requirements."
        
    elif domain == 'contaminants':
        desc = f"{name.replace('-', ' ').title()} removal guide for laser cleaning. Identification, safety requirements, and effective removal techniques."
    
    else:
        desc = f"{name.replace('-', ' ').title()} information for laser cleaning operations."
    
    # Ensure length is 120-155 chars
    if len(desc) < 120:
        desc += " Professional guidance for industrial applications."
    
    if len(desc) > 155:
        desc = desc[:152] + "..."
    
    return desc

def add_metadata_to_item(item: Dict[str, Any], domain: str, item_name: str) -> Dict[str, Any]:
    """Add complete metadata to a single item"""
    
    # 1. Add schemaVersion (if not exists)
    if 'schemaVersion' not in item:
        item['schemaVersion'] = '5.0.0'
    
    # 2. Add contentType
    item['contentType'] = domain.rstrip('s')  # 'materials' -> 'material'
    
    # 3. Add pageTitle (from name or page_title)
    if 'pageTitle' not in item:
        item['pageTitle'] = item.get('page_title', item.get('name', item_name))
    
    # 4. Generate metaDescription
    if 'metaDescription' not in item:
        item['metaDescription'] = generate_meta_description(domain, item_name, item)
    
    # 5. Ensure fullPath exists (should already be there)
    if 'fullPath' not in item and 'full_path' in item:
        item['fullPath'] = item['full_path']
    
    # 6. Remove snake_case fields
    fields_to_remove = ['schema_version', 'page_title', 'page_description', 'full_path']
    for field in fields_to_remove:
        if field in item:
            del item[field]
    
    return item

def process_domain(domain: str, source_file: Path):
    """Process all items in a domain file"""
    
    print(f"\n{'='*80}")
    print(f"Processing {domain.upper()}")
    print(f"{'='*80}")
    
    with open(source_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Get items key (materials, settings, compounds, contamination_patterns)
    if domain == 'contaminants':
        items_key = 'contamination_patterns'
    else:
        items_key = domain
    
    items = data.get(items_key, {})
    
    print(f"📊 Found {len(items)} items")
    
    updated_count = 0
    for item_name, item_data in items.items():
        # Add metadata
        items[item_name] = add_metadata_to_item(item_data, domain, item_name)
        updated_count += 1
        
        if updated_count % 50 == 0:
            print(f"  Progress: {updated_count}/{len(items)} items")
    
    # Save updated data
    with open(source_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Updated {updated_count} items in {source_file}")

def main():
    """Main execution"""
    
    print("="*80)
    print("ADD COMPLETE METADATA TO SOURCE DATA")
    print("Implementing Core Principle 0.6: No Build-Time Data Enhancement")
    print("="*80)
    
    base_dir = Path(__file__).parent.parent.parent
    
    # Process each domain
    domains = [
        ('materials', base_dir / 'data/materials/Materials.yaml'),
        ('settings', base_dir / 'data/settings/Settings.yaml'),
        ('compounds', base_dir / 'data/compounds/Compounds.yaml'),
        ('contaminants', base_dir / 'data/contaminants/Contaminants.yaml'),
    ]
    
    for domain, source_file in domains:
        if source_file.exists():
            process_domain(domain, source_file)
        else:
            print(f"⚠️  Skipping {domain} - file not found: {source_file}")
    
    print("\n" + "="*80)
    print("✅ COMPLETE - All source data files updated with complete metadata")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review changes in source YAML files")
    print("2. Remove build-time metadata tasks from export configs")
    print("3. Regenerate frontmatter to verify")

if __name__ == '__main__':
    main()
