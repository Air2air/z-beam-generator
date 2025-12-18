#!/usr/bin/env python3
"""
Create CategoryTaxonomy.yaml from Categories.yaml by removing duplicated content.
Extracts only the essential category taxonomy and ranges, removing sections
that have been moved to PropertyDefinitions.yaml and ParameterDefinitions.yaml.
"""

import yaml
from pathlib import Path


def create_category_taxonomy():
    """Extract category taxonomy from Categories.yaml and create slim version."""
    
    data_dir = Path(__file__).parent.parent.parent / "data" / "materials"
    input_file = data_dir / "Categories.yaml"
    output_file = data_dir / "CategoryTaxonomy.yaml"
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Create slimmed-down structure
    taxonomy = {
        '_metadata': {
            'version': '1.0.0',
            'description': 'Category taxonomy and material classification',
            'created_date': '2025-11-13',
            'source': 'Extracted from Categories.yaml v3.0.0',
            'purpose': 'Material categorization, ranges, and industry standards',
            'normalized_architecture': True,
            'property_definitions_ref': 'PropertyDefinitions.yaml',
            'parameter_definitions_ref': 'ParameterDefinitions.yaml',
            'total_categories': data.get('recommendationmetadata', {}).get('total_categories', 10),
        },
        
        # Keep universal regulatory standards
        'universal_regulatory_standards': data.get('universal_regulatory_standards', []),
        
        # Keep categories with their ranges and challenges
        'categories': data.get('categories', {}),
    }
    
    # Remove duplicated sections from _metadata that now live elsewhere
    if 'recommendationmetadata' in data:
        rec_meta = data['recommendationmetadata']
        # Keep only essential metadata
        taxonomy['_metadata'].update({
            'source_materials_yaml_hash': rec_meta.get('source_materials_yaml_hash'),
            'last_updated': rec_meta.get('last_updated'),
        })
    
    print(f"\nCreating slimmed-down CategoryTaxonomy.yaml...")
    print(f"  - Categories: {len(taxonomy['categories'])}")
    print(f"  - Regulatory standards: {len(taxonomy['universal_regulatory_standards'])}")
    
    # Sections removed (now in other files):
    removed_sections = []
    if 'machine_settingsRanges' in data:
        removed_sections.append(f"machine_settingsRanges ({len(data['machine_settingsRanges'])} parameters) → ParameterDefinitions.yaml")
    if 'propertyCategories' in data:
        removed_sections.append(f"propertyCategories → PropertyDefinitions.yaml")
    if 'machine_settingsDescriptions' in data:
        removed_sections.append(f"machine_settingsDescriptions → ParameterDefinitions.yaml")
    if 'materialPropertyDescriptions' in data:
        removed_sections.append(f"materialPropertyDescriptions → PropertyDefinitions.yaml")
    if 'environmentalImpactTemplates' in data:
        removed_sections.append(f"environmentalImpactTemplates → IndustryApplications.yaml")
    if 'applicationTypeDefinitions' in data:
        removed_sections.append(f"applicationTypeDefinitions → IndustryApplications.yaml")
    
    if removed_sections:
        print(f"\n  Removed duplicated sections:")
        for section in removed_sections:
            print(f"    - {section}")
    
    # Calculate size reduction
    original_size = len(yaml.dump(data))
    new_size = len(yaml.dump(taxonomy))
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"\n  Original size: ~{original_size // 1024}KB")
    print(f"  New size: ~{new_size // 1024}KB")
    print(f"  Reduction: {reduction:.1f}%")
    
    # Write the new file
    print(f"\nWriting {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Category Taxonomy - Material Classification and Ranges\n")
        f.write("# This file contains ONLY category definitions and material classifications\n")
        f.write("# Property definitions → PropertyDefinitions.yaml\n")
        f.write("# Parameter definitions → ParameterDefinitions.yaml\n")
        f.write("# Industry applications → IndustryApplications.yaml\n")
        f.write("# Version: 1.0.0 (Normalized Architecture)\n")
        f.write("# Created: 2025-11-13\n\n")
        yaml.dump(taxonomy, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ CategoryTaxonomy.yaml created successfully!")
    print(f"   {len(taxonomy['categories'])} categories with ranges and challenges")
    
    return taxonomy


if __name__ == '__main__':
    create_category_taxonomy()
