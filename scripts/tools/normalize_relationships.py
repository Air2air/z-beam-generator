#!/usr/bin/env python3
"""
Normalize all relationships in frontmatter files to match FRONTMATTER_GENERATION_GUIDE.md spec.

Transformations:
1. STRING values → dict with presentation: list, items: [value], _section: {...}
2. ARRAY values → dict with presentation: card, items: array, _section: {...}
3. DICT without structure → add presentation:, items:, _section:
4. DICT with structure but missing _section → add _section:

All relationships must have:
- presentation: card|table|list
- items: [array of items]
- _section:
    title: Display Title
    description: Clear description
    icon: icon-name
    order: N
    variant: default|success|warning|danger
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Complete metadata for all 37 relationship types
RELATIONSHIP_METADATA = {
    'materials': {
        'contaminated_by': {
            'title': 'Common Contaminants',
            'description': 'Types of contamination typically found on this material that require laser cleaning',
            'icon': 'droplet',
            'order': 1,
            'variant': 'default',
            'presentation': 'card'
        },
        'regulatory': {
            'title': 'Regulatory Standards',
            'description': 'Safety and compliance standards applicable to laser cleaning of this material',
            'icon': 'file-text',
            'order': 2,
            'variant': 'default',
            'presentation': 'card'
        }
    },
    'contaminants': {
        'chemical_formula': {
            'title': 'Chemical Formula',
            'description': 'Molecular structure and composition of this contamination',
            'icon': 'microscope',
            'order': 1,
            'variant': 'default',
            'presentation': 'list'
        },
        'scientific_name': {
            'title': 'Scientific Name',
            'description': 'Formal scientific nomenclature and classification',
            'icon': 'file-text',
            'order': 2,
            'variant': 'default',
            'presentation': 'list'
        },
        'context_notes': {
            'title': 'Context Notes',
            'description': 'Additional context and important considerations for this contamination type',
            'icon': 'file-text',
            'order': 3,
            'variant': 'default',
            'presentation': 'list'
        },
        'formation_conditions': {
            'title': 'Formation Conditions',
            'description': 'Environmental and process conditions that create this contamination',
            'icon': 'wind',
            'order': 4,
            'variant': 'default',
            'presentation': 'card'
        },
        'required_elements': {
            'title': 'Required Elements',
            'description': 'Chemical elements necessary for this contamination to form',
            'icon': 'microscope',
            'order': 5,
            'variant': 'default',
            'presentation': 'card'
        },
        'invalid_materials': {
            'title': 'Materials Requiring Caution',
            'description': 'Materials that need special consideration for laser removal of this contamination',
            'icon': 'alert-triangle',
            'order': 6,
            'variant': 'warning',
            'presentation': 'card'
        },
        'prohibited_materials': {
            'title': 'Prohibited Materials',
            'description': 'Materials where laser removal of this contamination is not recommended',
            'icon': 'alert-triangle',
            'order': 7,
            'variant': 'danger',
            'presentation': 'card'
        },
        'eeat': {
            'title': 'Evidence & Expertise',
            'description': 'Supporting evidence, citations, and expert analysis for this contamination',
            'icon': 'file-text',
            'order': 8,
            'variant': 'default',
            'presentation': 'list'
        },
        'laser_properties': {
            'title': 'Laser Parameters',
            'description': 'Optimal laser settings and technical parameters for removal',
            'icon': 'zap',
            'order': 9,
            'variant': 'default',
            'presentation': 'list'
        },
        'visual_characteristics': {
            'title': 'Visual Characteristics',
            'description': 'Physical appearance and identification features of this contamination',
            'icon': 'eye',
            'order': 10,
            'variant': 'default',
            'presentation': 'list'
        },
        'realism_notes': {
            'title': 'Realism Notes',
            'description': 'Important considerations for accurate representation and understanding',
            'icon': 'file-text',
            'order': 11,
            'variant': 'default',
            'presentation': 'list'
        },
        'materials': {
            'title': 'Affected Materials',
            'description': 'Materials where this contamination is commonly found',
            'icon': 'users',
            'order': 12,
            'variant': 'default',
            'presentation': 'card'
        },
        'found_on_materials': {
            'title': 'Found on Materials',
            'description': 'Materials commonly affected by this type of contamination',
            'icon': 'users',
            'order': 13,
            'variant': 'default',
            'presentation': 'card'
        },
        'valid_materials': {
            'title': 'Compatible Materials',
            'description': 'Materials where this contamination can be safely removed with laser cleaning',
            'icon': 'shield-check',
            'order': 14,
            'variant': 'default',
            'presentation': 'card'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Safety standards and regulations for handling this contamination',
            'icon': 'file-text',
            'order': 15,
            'variant': 'default',
            'presentation': 'card'
        },
        'produces_compounds': {
            'title': 'Hazardous Compounds Generated',
            'description': 'Chemical compounds released during laser removal of this contamination',
            'icon': 'flame',
            'order': 16,
            'variant': 'danger',
            'presentation': 'card'
        }
    },
    'compounds': {
        'chemical_properties': {
            'title': 'Chemical Properties',
            'description': 'Fundamental chemical characteristics and behavior',
            'icon': 'microscope',
            'order': 1,
            'variant': 'default',
            'presentation': 'list'
        },
        'physical_properties': {
            'title': 'Physical Properties',
            'description': 'Physical characteristics and state information',
            'icon': 'gauge',
            'order': 2,
            'variant': 'default',
            'presentation': 'list'
        },
        'health_effects': {
            'title': 'Health Effects',
            'description': 'Potential health impacts and medical considerations',
            'icon': 'alert-triangle',
            'order': 3,
            'variant': 'danger',
            'presentation': 'card'
        },
        'exposure_limits': {
            'title': 'Exposure Limits',
            'description': 'Regulatory exposure thresholds and safe concentration levels',
            'icon': 'gauge',
            'order': 4,
            'variant': 'warning',
            'presentation': 'card'
        },
        'ppe_requirements': {
            'title': 'PPE Requirements',
            'description': 'Personal protective equipment needed for safe handling',
            'icon': 'shield',
            'order': 5,
            'variant': 'warning',
            'presentation': 'card'
        },
        'detection_monitoring': {
            'title': 'Detection & Monitoring',
            'description': 'Methods and equipment for detecting and monitoring this compound',
            'icon': 'gauge',
            'order': 6,
            'variant': 'default',
            'presentation': 'card'
        },
        'emergency_response': {
            'title': 'Emergency Response',
            'description': 'First aid and emergency procedures for exposure incidents',
            'icon': 'alert-triangle',
            'order': 7,
            'variant': 'danger',
            'presentation': 'card'
        },
        'environmental_impact': {
            'title': 'Environmental Impact',
            'description': 'Environmental effects and ecological considerations',
            'icon': 'wind',
            'order': 8,
            'variant': 'warning',
            'presentation': 'card'
        },
        'produced_from_contaminants': {
            'title': 'Produced From Contaminants',
            'description': 'Contaminants that generate this compound during laser cleaning',
            'icon': 'droplet',
            'order': 9,
            'variant': 'default',
            'presentation': 'card'
        },
        'produced_from_materials': {
            'title': 'Produced From Materials',
            'description': 'Materials that may release this compound during laser cleaning',
            'icon': 'users',
            'order': 10,
            'variant': 'default',
            'presentation': 'card'
        },
        'reactivity': {
            'title': 'Reactivity',
            'description': 'Chemical reactivity and compatibility with other substances',
            'icon': 'flame',
            'order': 11,
            'variant': 'warning',
            'presentation': 'list'
        },
        'regulatory_classification': {
            'title': 'Regulatory Classification',
            'description': 'Hazard classifications and regulatory designations',
            'icon': 'file-text',
            'order': 12,
            'variant': 'default',
            'presentation': 'card'
        },
        'storage_requirements': {
            'title': 'Storage Requirements',
            'description': 'Proper storage conditions and handling precautions',
            'icon': 'alert-triangle',
            'order': 13,
            'variant': 'warning',
            'presentation': 'list'
        },
        'synonyms_identifiers': {
            'title': 'Synonyms & Identifiers',
            'description': 'Alternative names and chemical identifiers (CAS numbers)',
            'icon': 'file-text',
            'order': 14,
            'variant': 'default',
            'presentation': 'card'
        },
        'workplace_exposure': {
            'title': 'Workplace Exposure Limits',
            'description': 'Occupational exposure limits and workplace safety thresholds',
            'icon': 'gauge',
            'order': 15,
            'variant': 'danger',
            'presentation': 'card'
        }
    },
    'settings': {
        'challenges': {
            'title': 'Common Challenges',
            'description': 'Typical difficulties and considerations when using this setting',
            'icon': 'alert-triangle',
            'order': 1,
            'variant': 'warning',
            'presentation': 'card'
        },
        'optimized_for_materials': {
            'title': 'Optimized Materials',
            'description': 'Materials that work best with this laser cleaning setting',
            'icon': 'users',
            'order': 2,
            'variant': 'success',
            'presentation': 'card'
        },
        'removes_contaminants': {
            'title': 'Removes Contaminants',
            'description': 'Types of contamination effectively removed by this setting',
            'icon': 'droplet',
            'order': 3,
            'variant': 'default',
            'presentation': 'card'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Safety and compliance standards applicable to this laser setting',
            'icon': 'file-text',
            'order': 4,
            'variant': 'default',
            'presentation': 'card'
        }
    }
}


def normalize_relationship(
    rel_name: str,
    rel_value: Any,
    domain: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Normalize a relationship to the standard format.
    
    Returns a dict with:
    - presentation: card|table|list
    - items: [array]
    - _section: {metadata}
    """
    
    # Get metadata for this relationship type
    if rel_name not in metadata:
        print(f"⚠️  Warning: No metadata for '{rel_name}' in {domain} domain")
        # Use generic metadata
        rel_metadata = {
            'title': rel_name.replace('_', ' ').title(),
            'description': f'Information about {rel_name.replace("_", " ")}',
            'icon': 'file-text',
            'order': 99,
            'variant': 'default',
            'presentation': 'list'
        }
    else:
        rel_metadata = metadata[rel_name]
    
    # Determine current type and normalize
    if isinstance(rel_value, str):
        # STRING → dict with items: [value]
        normalized = {
            'presentation': rel_metadata.get('presentation', 'list'),
            'items': [rel_value] if rel_value else [],
            '_section': {
                'title': rel_metadata['title'],
                'description': rel_metadata['description'],
                'icon': rel_metadata['icon'],
                'order': rel_metadata['order'],
                'variant': rel_metadata['variant']
            }
        }
        return normalized
    
    elif isinstance(rel_value, list):
        # ARRAY → dict with items: array
        normalized = {
            'presentation': rel_metadata.get('presentation', 'card'),
            'items': rel_value,
            '_section': {
                'title': rel_metadata['title'],
                'description': rel_metadata['description'],
                'icon': rel_metadata['icon'],
                'order': rel_metadata['order'],
                'variant': rel_metadata['variant']
            }
        }
        return normalized
    
    elif isinstance(rel_value, dict):
        # DICT → ensure proper structure
        normalized = dict(rel_value)  # Copy existing dict
        
        # Add presentation if missing
        if 'presentation' not in normalized:
            normalized['presentation'] = rel_metadata.get('presentation', 'card')
        
        # Handle items key
        if 'items' not in normalized:
            # Check if this dict has nested data that should become items
            # For dicts like visual_characteristics: {appearance: {...}, texture: {...}}
            # Or laser_properties: {wavelength: X, power: Y}
            # These should stay as-is but get items: [] added
            
            # Special handling for dicts that are data containers
            data_keys = [k for k in normalized.keys() if k not in ['presentation', '_section', 'items']]
            if data_keys and all(isinstance(normalized[k], (dict, list, str, int, float)) for k in data_keys):
                # This is a data container dict - keep structure, add empty items
                normalized['items'] = []
            else:
                normalized['items'] = []
        
        # Add or update _section
        if '_section' not in normalized:
            # Use section_description (new standard) instead of description
            normalized['_section'] = {
                'title': rel_metadata['title'],
                'section_description': rel_metadata['description'],
                'icon': rel_metadata['icon'],
                'order': rel_metadata['order'],
                'variant': rel_metadata['variant']
            }
        else:
            # Ensure all required fields exist in _section
            section = normalized['_section']
            if 'title' not in section:
                section['title'] = rel_metadata['title']
            if 'section_description' not in section and 'description' not in section:
                # Use section_description (new standard)
                section['section_description'] = rel_metadata['description']
            if 'icon' not in section:
                section['icon'] = rel_metadata['icon']
            if 'order' not in section:
                section['order'] = rel_metadata['order']
            if 'variant' not in section:
                section['variant'] = rel_metadata['variant']
        
        return normalized
    
    else:
        # Unknown type - wrap in dict
        print(f"⚠️  Warning: Unknown type {type(rel_value)} for {rel_name}")
        return {
            'presentation': 'list',
            'items': [str(rel_value)],
            '_section': {
                'title': rel_metadata['title'],
                'description': rel_metadata['description'],
                'icon': rel_metadata['icon'],
                'order': rel_metadata['order'],
                'variant': rel_metadata['variant']
            }
        }


def normalize_file(filepath: Path, domain: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Normalize all relationships in a frontmatter file.
    
    Returns dict with counts:
    - transformed: Number of relationships normalized
    - already_compliant: Number already in correct format
    """
    
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return {'transformed': 0, 'already_compliant': 0}
    
    if 'relationships' not in data or not data['relationships']:
        return {'transformed': 0, 'already_compliant': 0}
    
    relationships = data['relationships']
    metadata = RELATIONSHIP_METADATA.get(domain, {})
    
    transformed = 0
    already_compliant = 0
    
    # Normalize each relationship
    for rel_name, rel_value in list(relationships.items()):
        # Check if already compliant
        if isinstance(rel_value, dict) and \
           'presentation' in rel_value and \
           'items' in rel_value and \
           '_section' in rel_value and \
           len(rel_value.get('_section', {})) >= 5:  # All 5 fields
            already_compliant += 1
            continue
        
        # Normalize
        normalized = normalize_relationship(rel_name, rel_value, domain, metadata)
        relationships[rel_name] = normalized
        transformed += 1
        
        if not dry_run:
            print(f"  ✅ Normalized: {rel_name}")
    
    # Write back
    if transformed > 0 and not dry_run:
        try:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"✅ Updated: {filepath.name} ({transformed} relationships normalized)")
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return {'transformed': 0, 'already_compliant': already_compliant}
    elif transformed > 0:
        print(f"[DRY RUN] Would update: {filepath.name} ({transformed} relationships)")
    
    return {'transformed': transformed, 'already_compliant': already_compliant}


def main():
    parser = argparse.ArgumentParser(
        description='Normalize all relationships to FRONTMATTER_GENERATION_GUIDE.md spec'
    )
    parser.add_argument(
        '--domain',
        choices=['materials', 'contaminants', 'compounds', 'settings', 'all'],
        required=True,
        help='Domain to process'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Process single file (requires --domain)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    # Base directory
    base_dir = Path(__file__).parent.parent.parent.parent / 'z-beam' / 'frontmatter'
    
    if not base_dir.exists():
        print(f"❌ Frontmatter directory not found: {base_dir}")
        return 1
    
    # Determine domains to process
    if args.domain == 'all':
        domains = ['materials', 'contaminants', 'compounds', 'settings']
    else:
        domains = [args.domain]
    
    total_transformed = 0
    total_compliant = 0
    total_files = 0
    
    for domain in domains:
        domain_dir = base_dir / domain
        
        if not domain_dir.exists():
            print(f"⚠️  Domain directory not found: {domain_dir}")
            continue
        
        print(f"\n{'='*60}")
        print(f"🔄 NORMALIZING: {domain}")
        print(f"{'='*60}\n")
        
        # Process files
        if args.file:
            # Single file mode
            files = [domain_dir / args.file.name]
        else:
            # All files in domain
            files = sorted(domain_dir.glob('*.yaml'))
        
        for filepath in files:
            if not filepath.exists():
                print(f"⚠️  File not found: {filepath}")
                continue
            
            print(f"\n📄 Processing: {filepath.name}")
            result = normalize_file(filepath, domain, args.dry_run)
            
            total_transformed += result['transformed']
            total_compliant += result['already_compliant']
            total_files += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 NORMALIZATION SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {total_files}")
    print(f"Relationships transformed: {total_transformed}")
    print(f"Already compliant: {total_compliant}")
    print(f"Total relationships: {total_transformed + total_compliant}")
    if total_transformed + total_compliant > 0:
        compliance_pct = (total_compliant / (total_transformed + total_compliant)) * 100
        print(f"Compliance rate: {compliance_pct:.1f}%")
    print(f"{'='*60}\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
