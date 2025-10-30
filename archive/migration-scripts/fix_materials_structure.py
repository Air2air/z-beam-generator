#!/usr/bin/env python3
"""
Fix Materials.yaml data structure to match example.yaml format:
1. Convert regulatoryStandards from strings to objects
2. Add missing micro images for all materials
"""

import yaml
import re
from datetime import datetime
from pathlib import Path

# Regulatory standards mapping: name -> (url, logo)
REGULATORY_MAPPING = {
    'FDA': {
        'pattern': r'FDA\s+21\s+CFR\s+1040\.10',
        'url': 'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10',
        'image': '/images/logo/logo-org-fda.png'
    },
    'ANSI': {
        'pattern': r'ANSI\s+Z136\.\d+',
        'url': 'https://webstore.ansi.org/standards/lia/ansiz1362022',
        'image': '/images/logo/logo-org-ansi.png'
    },
    'IEC': {
        'pattern': r'IEC\s+60825',
        'url': 'https://webstore.iec.ch/publication/3587',
        'image': '/images/logo/logo-org-iec.png'
    },
    'OSHA': {
        'pattern': r'OSHA',
        'url': 'https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.102',
        'image': '/images/logo/logo-org-osha.png'
    },
    'ISO': {
        'pattern': r'ISO\s+\d+',
        'url': 'https://www.iso.org/standard/60426.html',
        'image': '/images/logo/logo-org-iso.png'
    },
    'EN': {
        'pattern': r'EN\s+\d+',
        'url': 'https://www.en-standard.eu/',
        'image': '/images/logo/logo-org-en.png'
    },
    'CDRH': {
        'pattern': r'CDRH',
        'url': 'https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/laser-products-and-instruments',
        'image': '/images/logo/logo-org-fda.png'
    }
}

def parse_regulatory_string(reg_string: str) -> dict:
    """Convert regulatory string to object format."""
    
    # Try to match against known patterns
    for name, info in REGULATORY_MAPPING.items():
        if re.search(info['pattern'], reg_string, re.IGNORECASE):
            return {
                'name': name,
                'description': reg_string.strip(),
                'url': info['url'],
                'image': info['image']
            }
    
    # If no match, create generic object
    return {
        'name': 'Unknown',
        'description': reg_string.strip(),
        'url': '',
        'image': '/images/logo/logo-org-generic.png'
    }

def generate_micro_image(material_name: str, hero_alt: str) -> dict:
    """Generate micro image structure from material name and hero alt."""
    
    # Convert material name to URL-friendly format
    url_name = material_name.lower().replace(' ', '-').replace('_', '-')
    
    # Create alt text from hero alt (modify to be microscopic view)
    if 'surface' in hero_alt.lower():
        micro_alt = hero_alt.replace('surface undergoing', 'microscopic view of')
        micro_alt = micro_alt.replace('showing', 'showing detailed')
    else:
        micro_alt = f"Microscopic view of {material_name.lower()} surface showing laser cleaning effects"
    
    return {
        'alt': micro_alt,
        'url': f'/images/material/{url_name}-laser-cleaning-micro.jpg'
    }

def fix_materials_structure():
    """Fix Materials.yaml structure to match example.yaml."""
    
    # Load Materials.yaml
    materials_path = Path('data/Materials.yaml')
    
    print("Loading Materials.yaml...")
    with open(materials_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Create backup
    backup_path = materials_path.parent / f'Materials.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
    print(f"Creating backup: {backup_path}")
    with open(backup_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Track changes
    stats = {
        'regulatory_fixed': 0,
        'micro_added': 0,
        'total_materials': 0
    }
    
    # Fix each material
    for material_name, material_data in data['materials'].items():
        stats['total_materials'] += 1
        
        # Fix regulatoryStandards (if exists and is string array)
        if 'regulatoryStandards' in material_data:
            reg_standards = material_data['regulatoryStandards']
            
            if isinstance(reg_standards, list) and len(reg_standards) > 0:
                if isinstance(reg_standards[0], str):
                    # Convert strings to objects
                    new_standards = []
                    for reg_string in reg_standards:
                        new_standards.append(parse_regulatory_string(reg_string))
                    
                    material_data['regulatoryStandards'] = new_standards
                    stats['regulatory_fixed'] += 1
                    print(f"✓ {material_name}: Fixed {len(new_standards)} regulatory standards")
        
        # Add missing micro images
        if 'images' in material_data:
            images = material_data['images']
            
            # Check if micro is missing
            if 'micro' not in images and 'hero' in images:
                hero_alt = images['hero'].get('alt', '')
                images['micro'] = generate_micro_image(material_name, hero_alt)
                stats['micro_added'] += 1
                print(f"✓ {material_name}: Added micro image")
    
    # Write updated data
    print("\nWriting updated Materials.yaml...")
    with open(materials_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Print summary
    print("\n" + "=" * 80)
    print("STRUCTURE FIX SUMMARY")
    print("=" * 80)
    print(f"Total Materials: {stats['total_materials']}")
    print(f"Regulatory Standards Fixed: {stats['regulatory_fixed']}")
    print(f"Micro Images Added: {stats['micro_added']}")
    print(f"\nBackup saved to: {backup_path}")
    print("=" * 80)
    
    return stats

if __name__ == '__main__':
    fix_materials_structure()
