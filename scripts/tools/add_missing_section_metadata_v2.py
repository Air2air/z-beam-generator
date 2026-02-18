#!/usr/bin/env python3
"""
Add Missing _section Metadata to Frontmatter Relationships - v2 COMPLETE

Automatically adds _section blocks to ALL relationship definitions.
Includes metadata for all 37 relationship types discovered in exported frontmatter.

Usage:
    python3 scripts/tools/add_missing_section_metadata_v2.py --domain materials
    python3 scripts/tools/add_missing_section_metadata_v2.py --domain all
    python3 scripts/tools/add_missing_section_metadata_v2.py --file path/to/file.yaml --dry-run
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Complete metadata for ALL 37 relationship types across all domains
RELATIONSHIP_METADATA = {
    'materials': {
        'contaminated_by': {
            'title': 'Common Contaminants',
            'description': 'Types of contamination typically found on this material that require laser cleaning',
            'icon': 'droplet',
            'order': 1,
            'variant': 'default'
        },
        'regulatory': {
            'title': 'Regulatory Standards',
            'description': 'Industry standards and regulations governing laser cleaning of this material',
            'icon': 'file-text',
            'order': 2,
            'variant': 'default'
        }
    },
    'contaminants': {
        'chemical_formula': {
            'title': 'Chemical Formula',
            'description': 'Molecular structure and chemical composition',
            'icon': 'microscope',
            'order': 1,
            'variant': 'default'
        },
        'context_notes': {
            'title': 'Context Notes',
            'description': 'Additional information and usage context',
            'icon': 'file-text',
            'order': 2,
            'variant': 'default'
        },
        'eeat': {
            'title': 'Expertise & Trust',
            'description': 'Expert evaluation and trust indicators',
            'icon': 'shield',
            'order': 3,
            'variant': 'default'
        },
        'formation_conditions': {
            'title': 'Formation Conditions',
            'description': 'Environmental and process conditions that create this contamination',
            'icon': 'wind',
            'order': 4,
            'variant': 'default'
        },
        'found_on_materials': {
            'title': 'Found on Materials',
            'description': 'Materials where this contamination is commonly encountered',
            'icon': 'users',
            'order': 5,
            'variant': 'default'
        },
        'invalid_materials': {
            'title': 'Invalid Materials',
            'description': 'Materials where this contamination does not occur',
            'icon': 'alert-triangle',
            'order': 6,
            'variant': 'warning'
        },
        'laser_properties': {
            'title': 'Laser Interaction',
            'description': 'How this contaminant responds to laser cleaning',
            'icon': 'zap',
            'order': 7,
            'variant': 'default'
        },
        'materials': {
            'title': 'Related Materials',
            'description': 'Materials associated with this contamination',
            'icon': 'users',
            'order': 8,
            'variant': 'default'
        },
        'produces_compounds': {
            'title': 'Hazardous Compounds Generated',
            'description': 'Chemical compounds produced when this contaminant is removed with laser cleaning',
            'icon': 'flame',
            'order': 9,
            'variant': 'danger'
        },
        'prohibited_materials': {
            'title': 'Prohibited Materials',
            'description': 'Materials where this contamination must not be present',
            'icon': 'alert-triangle',
            'order': 10,
            'variant': 'danger'
        },
        'realism_notes': {
            'title': 'Realism Notes',
            'description': 'Practical considerations and real-world behavior',
            'icon': 'eye',
            'order': 11,
            'variant': 'default'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Industry standards and regulations related to this contamination',
            'icon': 'file-text',
            'order': 12,
            'variant': 'default'
        },
        'required_elements': {
            'title': 'Required Elements',
            'description': 'Chemical elements that must be present',
            'icon': 'microscope',
            'order': 13,
            'variant': 'default'
        },
        'scientific_name': {
            'title': 'Scientific Name',
            'description': 'Technical and scientific nomenclature',
            'icon': 'file-text',
            'order': 14,
            'variant': 'default'
        },
        'valid_materials': {
            'title': 'Valid Materials',
            'description': 'Materials where this contamination commonly occurs',
            'icon': 'users',
            'order': 15,
            'variant': 'default'
        },
        'visual_characteristics': {
            'title': 'Visual Characteristics',
            'description': 'Physical appearance and visual properties of this contamination',
            'icon': 'microscope',
            'order': 16,
            'variant': 'default'
        }
    },
    'compounds': {
        'chemical_properties': {
            'title': 'Chemical Properties',
            'description': 'Molecular characteristics and chemical behavior',
            'icon': 'microscope',
            'order': 1,
            'variant': 'default'
        },
        'detection_monitoring': {
            'title': 'Detection and Monitoring',
            'description': 'Methods for detecting and monitoring this compound in the workplace',
            'icon': 'eye',
            'order': 2,
            'variant': 'default'
        },
        'emergency_response': {
            'title': 'Emergency Response',
            'description': 'Emergency procedures for exposure or spills',
            'icon': 'alert-triangle',
            'order': 3,
            'variant': 'danger'
        },
        'environmental_impact': {
            'title': 'Environmental Impact',
            'description': 'Effects on environment and ecosystems',
            'icon': 'wind',
            'order': 4,
            'variant': 'warning'
        },
        'exposure_limits': {
            'title': 'Exposure Limits',
            'description': 'Maximum safe exposure levels and time-weighted averages',
            'icon': 'gauge',
            'order': 5,
            'variant': 'danger'
        },
        'health_effects': {
            'title': 'Health Effects',
            'description': 'Potential health impacts and symptoms of exposure',
            'icon': 'alert-triangle',
            'order': 6,
            'variant': 'danger'
        },
        'physical_properties': {
            'title': 'Physical Properties',
            'description': 'Physical characteristics including melting point, boiling point, and appearance',
            'icon': 'microscope',
            'order': 7,
            'variant': 'default'
        },
        'ppe_requirements': {
            'title': 'PPE Requirements',
            'description': 'Required personal protective equipment when handling this compound',
            'icon': 'shield',
            'order': 8,
            'variant': 'warning'
        },
        'produced_from_contaminants': {
            'title': 'Source Contaminants',
            'description': 'Contaminants that produce this compound when removed with laser cleaning',
            'icon': 'droplet',
            'order': 9,
            'variant': 'default'
        },
        'produced_from_materials': {
            'title': 'Source Materials',
            'description': 'Materials that can release this compound during laser cleaning processes',
            'icon': 'users',
            'order': 10,
            'variant': 'default'
        },
        'reactivity': {
            'title': 'Reactivity',
            'description': 'Chemical reactivity and compatibility with other substances',
            'icon': 'flame',
            'order': 11,
            'variant': 'warning'
        },
        'regulatory_classification': {
            'title': 'Regulatory Classification',
            'description': 'Hazard classifications and regulatory designations',
            'icon': 'file-text',
            'order': 12,
            'variant': 'default'
        },
        'storage_requirements': {
            'title': 'Storage Requirements',
            'description': 'Proper storage conditions and handling precautions',
            'icon': 'alert-triangle',
            'order': 13,
            'variant': 'warning'
        },
        'synonyms_identifiers': {
            'title': 'Synonyms & Identifiers',
            'description': 'Alternative names and chemical identifiers (CAS numbers)',
            'icon': 'file-text',
            'order': 14,
            'variant': 'default'
        },
        'workplace_exposure': {
            'title': 'Workplace Exposure Limits',
            'description': 'Occupational exposure limits and workplace safety thresholds',
            'icon': 'gauge',
            'order': 15,
            'variant': 'danger'
        }
    },
    'settings': {
        'challenges': {
            'title': 'Common Challenges',
            'description': 'Technical challenges and considerations when using these laser settings',
            'icon': 'alert-triangle',
            'order': 1,
            'variant': 'warning'
        },
        'optimized_for_materials': {
            'title': 'Optimized for Materials',
            'description': 'Materials that perform best with these laser settings',
            'icon': 'users',
            'order': 2,
            'variant': 'default'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Industry standards and safety regulations for these laser parameters',
            'icon': 'file-text',
            'order': 3,
            'variant': 'default'
        },
        'removes_contaminants': {
            'title': 'Removes Contaminants',
            'description': 'Types of contamination effectively removed by these settings',
            'icon': 'droplet',
            'order': 4,
            'variant': 'default'
        }
    }
}

def find_relationships_without_section(lines: List[str]) -> List[Tuple[str, int, bool, Optional[int]]]:
    """
    Find relationships missing _section or with incomplete _section blocks.
    
    Returns list of tuples: (relationship_name, start_line, has_partial_section, section_line)
    """
    relationships = []
    in_relationships = False
    current_rel = None
    current_rel_line = 0
    has_section = False
    section_line = None
    section_fields = set()
    required_fields = {'title', 'description', 'icon', 'order', 'variant'}
    
    for i, line in enumerate(lines):
        # Detect relationships block
        if line.strip() == 'relationships:':
            in_relationships = True
            continue
        
        # Exit relationships block
        if in_relationships and line and not line.startswith(' '):
            in_relationships = False
            # Save previous relationship if incomplete
            if current_rel and (not has_section or section_fields != required_fields):
                relationships.append((current_rel, current_rel_line, has_section, section_line))
            current_rel = None
            continue
        
        # Detect relationship name (2-space indent, ends with colon)
        if in_relationships and re.match(r'^  [a-z_]+:$', line):
            # Save previous relationship if incomplete
            if current_rel and (not has_section or section_fields != required_fields):
                relationships.append((current_rel, current_rel_line, has_section, section_line))
            
            # Start new relationship
            current_rel = line.strip()[:-1]  # Remove colon
            current_rel_line = i
            has_section = False
            section_line = None
            section_fields = set()
        
        # Detect _section block (4-space indent)
        if in_relationships and current_rel and line.strip() == '_section:':
            has_section = True
            section_line = i
        
        # Detect _section fields (6-space indent)
        if in_relationships and has_section and re.match(r'^      (title|description|icon|order|variant):', line):
            field_name = line.strip().split(':')[0]
            section_fields.add(field_name)
    
    # Don't forget last relationship
    if current_rel and (not has_section or section_fields != required_fields):
        relationships.append((current_rel, current_rel_line, has_section, section_line))
    
    return relationships

def add_section_metadata(
    lines: List[str],
    relationship_name: str,
    start_line: int,
    metadata: Dict[str, any],
    has_partial_section: bool = False,
    section_line: Optional[int] = None
) -> List[str]:
    """Add or complete _section metadata to a relationship."""
    
    if has_partial_section and section_line is not None:
        # Add missing fields to existing _section
        # Find where _section block ends
        insert_line = section_line + 1
        while insert_line < len(lines) and (lines[insert_line].startswith('      ') or not lines[insert_line].strip()):
            insert_line += 1
        
        # Collect existing fields
        existing_fields = set()
        for i in range(section_line + 1, insert_line):
            if re.match(r'^      [a-z_]+:', lines[i]):
                field_name = lines[i].strip().split(':')[0]
                existing_fields.add(field_name)
        
        # Add missing fields before the next block
        new_lines = []
        for field_name in ['title', 'description', 'icon', 'order', 'variant']:
            if field_name not in existing_fields:
                value = metadata[field_name]
                if isinstance(value, str):
                    new_lines.append(f"      {field_name}: {value}\n")
                else:
                    new_lines.append(f"      {field_name}: {value}\n")
        
        # Insert new fields
        for i, new_line in enumerate(new_lines):
            lines.insert(insert_line + i, new_line)
        
        return lines
    
    else:
        # Add complete _section block
        # Find insertion point - right after the relationship declaration
        insert_line = start_line + 1
        
        # Skip past any existing content to find where to insert _section
        # We want to insert after presentation: and items: if they exist
        indent_level = 4  # _section should be at 4-space indent
        max_search = start_line + 50  # Don't search too far
        
        while insert_line < len(lines) and insert_line < max_search:
            line = lines[insert_line]
            
            # Stop if we hit next relationship (2-space indent ending with colon)
            if re.match(r'^  [a-z_]+:$', line):
                break
            
            # Stop if we exit relationships block entirely
            if line and not line.startswith(' '):
                break
            
            # Check if _section already exists at this relationship
            if line.strip() == '_section:' and line.startswith('    '):
                # _section already exists for this relationship, don't add another
                return lines
            
            insert_line += 1
        
        # Back up to insert before the next relationship or block
        insert_line = insert_line
        
        # Create _section block
        section_block = [
            "    _section:\n",
            f"      title: {metadata['title']}\n",
            f"      description: {metadata['description']}\n",
            f"      icon: {metadata['icon']}\n",
            f"      order: {metadata['order']}\n",
            f"      variant: {metadata['variant']}\n"
        ]
        
        # Insert block at the determined position
        for new_line in reversed(section_block):
            lines.insert(insert_line, new_line)
        
        return lines

def process_file(filepath: Path, domain: str, dry_run: bool = False) -> int:
    """Process a single frontmatter file. Returns count of sections added."""
    
    # Read file
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return 0
    
    # Find missing sections
    missing = find_relationships_without_section(lines)
    
    if not missing:
        return 0
    
    # Get domain metadata
    domain_metadata = RELATIONSHIP_METADATA.get(domain, {})
    
    # Process in reverse to maintain line numbers
    count = 0
    for rel_name, start_line, has_partial, section_line in reversed(missing):
        if rel_name not in domain_metadata:
            print(f"⚠️  Warning: No metadata defined for relationship '{rel_name}' in {domain} domain")
            continue
        
        metadata = domain_metadata[rel_name]
        lines = add_section_metadata(lines, rel_name, start_line, metadata, has_partial, section_line)
        count += 1
        
        if not dry_run:
            print(f"  ✅ Added _section to: {rel_name}")
    
    # Write back
    if count > 0 and not dry_run:
        try:
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print(f"✅ Updated: {filepath.name} ({count} sections added)")
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return 0
    elif count > 0:
        print(f"[DRY RUN] Would update: {filepath.name} ({count} sections)")
    
    return count

def main():
    parser = argparse.ArgumentParser(description='Add missing _section metadata to frontmatter relationships')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'applications', 'all'],
                       help='Domain to process')
    parser.add_argument('--file', type=Path, help='Process single file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    if not args.domain and not args.file:
        parser.error('Must specify --domain or --file')
    
    # Determine frontmatter directory
    frontmatter_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        sys.exit(1)
    
    total_added = 0
    
    if args.file:
        # Process single file
        domain = args.file.parent.name
        total_added = process_file(args.file, domain, args.dry_run)
    else:
        # Process domain(s)
        domains = ['materials', 'contaminants', 'compounds', 'settings', 'applications'] if args.domain == 'all' else [args.domain]
        
        for domain in domains:
            print(f"\n{'='*70}")
            print(f"🔍 Processing {domain} domain...")
            print('='*70)
            
            domain_dir = frontmatter_dir / domain
            if not domain_dir.exists():
                print(f"⚠️  Domain directory not found: {domain_dir}")
                continue
            
            yaml_files = list(domain_dir.glob('*.yaml'))
            print(f"Found {len(yaml_files)} YAML files\n")
            
            domain_count = 0
            for filepath in sorted(yaml_files):
                count = process_file(filepath, domain, args.dry_run)
                domain_count += count
            
            print(f"\n{'='*70}")
            print(f"✅ {domain}: Added {domain_count} _section blocks")
            print('='*70)
            
            total_added += domain_count
    
    print(f"\n{'='*70}")
    print(f"✅ COMPLETE - Added {total_added} _section blocks")
    print('='*70)

if __name__ == '__main__':
    main()
