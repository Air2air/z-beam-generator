#!/usr/bin/env python3
"""
Add Missing _section Metadata to Frontmatter Relationships

Automatically adds _section blocks to relationship definitions that are missing them.
Follows FRONTMATTER_GENERATION_GUIDE.md specifications.

Usage:
    python3 scripts/tools/add_missing_section_metadata.py --domain materials
    python3 scripts/tools/add_missing_section_metadata.py --domain all --dry-run
    python3 scripts/tools/add_missing_section_metadata.py --file path/to/file.yaml
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Domain-specific relationship metadata per FRONTMATTER_GENERATION_GUIDE.md
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
            'description': 'Safety and compliance standards applicable to laser cleaning of this material',
            'icon': 'file-text',
            'order': 2,
            'variant': 'default'
        },
        'related_settings': {
            'title': 'Recommended Settings',
            'description': 'Laser parameters optimized for cleaning this material',
            'icon': 'settings',
            'order': 3,
            'variant': 'default'
        },
        'produces_compounds': {
            'title': 'Generated Compounds',
            'description': 'Chemical compounds produced during laser cleaning of this material',
            'icon': 'flame',
            'order': 4,
            'variant': 'warning'
        }
    },
    'contaminants': {
        'produces_compounds': {
            'title': 'Hazardous Compounds Generated',
            'description': 'Chemical compounds released during laser removal of this contamination',
            'icon': 'flame',
            'order': 1,
            'variant': 'danger'
        },
        'found_on_materials': {
            'title': 'Found on Materials',
            'description': 'Materials commonly affected by this type of contamination',
            'icon': 'users',
            'order': 2,
            'variant': 'default'
        },
        'visual_characteristics': {
            'title': 'Visual Characteristics',
            'description': 'Detailed appearance and identification characteristics across different material categories',
            'icon': 'microscope',
            'order': 3,
            'variant': 'default'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Safety standards and regulations for handling this contamination',
            'icon': 'file-text',
            'order': 4,
            'variant': 'default'
        },
        'removal_methods': {
            'title': 'Removal Methods',
            'description': 'Laser cleaning approaches for removing this contamination',
            'icon': 'zap',
            'order': 5,
            'variant': 'default'
        }
    },
    'compounds': {
        'produced_from_contaminants': {
            'title': 'Source Contaminants',
            'description': 'Contaminants that produce this compound when removed with laser cleaning',
            'icon': 'droplet',
            'order': 1,
            'variant': 'default'
        },
        'produced_from_materials': {
            'title': 'Source Materials',
            'description': 'Materials that can release this compound during laser cleaning processes',
            'icon': 'users',
            'order': 2,
            'variant': 'default'
        },
        'ppe_requirements': {
            'title': 'PPE Requirements',
            'description': 'Required personal protective equipment for handling this compound',
            'icon': 'shield',
            'order': 3,
            'variant': 'warning'
        },
        'storage_requirements': {
            'title': 'Storage Requirements',
            'description': 'Proper storage conditions and incompatibilities',
            'icon': 'alert-triangle',
            'order': 4,
            'variant': 'warning'
        },
        'workplace_exposure': {
            'title': 'Workplace Exposure Limits',
            'description': 'Occupational exposure limits and monitoring requirements',
            'icon': 'gauge',
            'order': 5,
            'variant': 'danger'
        },
        'exposure_limits': {
            'title': 'Exposure Limits',
            'description': 'OSHA, NIOSH, and ACGIH exposure thresholds',
            'icon': 'gauge',
            'order': 5,
            'variant': 'danger'
        },
        'regulatory_classification': {
            'title': 'Regulatory Classification',
            'description': 'Regulatory classifications and hazard categories',
            'icon': 'file-text',
            'order': 6,
            'variant': 'default'
        },
        'detection_monitoring': {
            'title': 'Detection and Monitoring',
            'description': 'Methods for detecting and monitoring compound presence',
            'icon': 'eye',
            'order': 7,
            'variant': 'default'
        },
        'health_effects': {
            'title': 'Health Effects',
            'description': 'Potential health impacts and medical considerations',
            'icon': 'alert-triangle',
            'order': 8,
            'variant': 'danger'
        },
        'environmental_impact': {
            'title': 'Environmental Impact',
            'description': 'Environmental concerns and disposal requirements',
            'icon': 'wind',
            'order': 9,
            'variant': 'warning'
        },
        'emergency_response': {
            'title': 'Emergency Response',
            'description': 'Emergency procedures for exposure or spills',
            'icon': 'alert-triangle',
            'order': 10,
            'variant': 'danger'
        },
        'chemical_properties': {
            'title': 'Chemical Properties',
            'description': 'Key chemical and physical properties',
            'icon': 'microscope',
            'order': 11,
            'variant': 'default'
        },
        'contamination_context': {
            'title': 'Contamination Context',
            'description': 'Common scenarios where this compound is encountered',
            'icon': 'droplet',
            'order': 12,
            'variant': 'default'
        }
    },
    'settings': {
        'optimized_for_materials': {
            'title': 'Optimized for Materials',
            'description': 'Materials these settings are specifically optimized for',
            'icon': 'users',
            'order': 1,
            'variant': 'default'
        },
        'removes_contaminants': {
            'title': 'Removes Contaminants',
            'description': 'Contaminants effectively removed by these settings',
            'icon': 'droplet',
            'order': 2,
            'variant': 'default'
        },
        'challenges': {
            'title': 'Common Challenges',
            'description': 'Challenges encountered with these settings and mitigation strategies',
            'icon': 'alert-triangle',
            'order': 3,
            'variant': 'warning'
        },
        'regulatory_standards': {
            'title': 'Regulatory Standards',
            'description': 'Safety standards applicable to these laser parameters',
            'icon': 'file-text',
            'order': 4,
            'variant': 'default'
        }
    }
}


def get_section_metadata(domain: str, relationship_name: str) -> Optional[Dict]:
    """Get _section metadata for a relationship type."""
    return RELATIONSHIP_METADATA.get(domain, {}).get(relationship_name)


def find_relationships_without_section(content: str) -> List[tuple]:
    """
    Find all relationship blocks missing complete _section metadata.
    Returns list of (relationship_name, start_line, has_partial_section, section_line) tuples.
    """
    lines = content.split('\n')
    missing = []
    in_relationships = False
    current_relationship = None
    relationship_start_line = -1
    section_line = -1
    has_complete_section = False
    section_fields = set()
    
    for i, line in enumerate(lines):
        # Check if we're entering relationships block
        if line.strip() == 'relationships:':
            in_relationships = True
            continue
        
        if not in_relationships:
            continue
        
        # Check for relationship start (2-space indent + name + colon)
        if re.match(r'^  [a-z_]+:', line):
            # Save previous relationship if missing complete _section
            if current_relationship and not has_complete_section:
                missing.append((current_relationship, relationship_start_line, 
                              bool(section_fields), section_line))
            
            # Start new relationship
            current_relationship = line.strip().rstrip(':')
            relationship_start_line = i
            section_line = -1
            has_complete_section = False
            section_fields = set()
            continue
        
        # Check for _section and its fields
        if current_relationship:
            if line.strip().startswith('_section:'):
                section_line = i
                section_fields = set()
                continue
            
            # Check for required _section fields
            if section_line > 0:
                stripped = line.strip()
                for field in ['title:', 'description:', 'icon:', 'order:', 'variant:']:
                    if stripped.startswith(field):
                        section_fields.add(field.rstrip(':'))
                
                # Check if we have all 5 required fields
                if len(section_fields) >= 5:
                    has_complete_section = True
        
        # Check if we've exited relationships (top-level key)
        if in_relationships and line and not line[0].isspace():
            # Save last relationship if missing complete _section
            if current_relationship and not has_complete_section:
                missing.append((current_relationship, relationship_start_line,
                              bool(section_fields), section_line))
            break
    
    # Handle case where relationships is the last block
    if current_relationship and not has_complete_section:
        missing.append((current_relationship, relationship_start_line,
                      bool(section_fields), section_line))
    
    return missing


def add_section_metadata(content: str, domain: str, dry_run: bool = False) -> tuple:
    """
    Add or complete _section metadata for relationships missing it.
    Returns (modified_content, count_added).
    """
    missing = find_relationships_without_section(content)
    if not missing:
        return content, 0
    
    lines = content.split('\n')
    additions_made = 0
    
    # Process in reverse order to maintain line numbers
    for relationship_name, start_line, has_partial, section_line in reversed(missing):
        metadata = get_section_metadata(domain, relationship_name)
        if not metadata:
            if not dry_run:
                print(f"  ⚠️  No metadata defined for relationship: {relationship_name}")
            continue
        
        # If there's a partial _section, complete it
        if has_partial and section_line > 0:
            # Find existing fields
            existing_fields = set()
            i = section_line + 1
            while i < len(lines) and lines[i].startswith('      '):
                field = lines[i].strip().split(':')[0]
                existing_fields.add(field)
                i += 1
            
            # Add missing fields
            insert_pos = i
            for field in ['variant', 'order', 'icon', 'description', 'title']:
                if field not in existing_fields:
                    value = metadata[field]
                    lines.insert(insert_pos, f'      {field}: {value}')
            
            additions_made += 1
            if not dry_run:
                print(f"  ✅ Completed _section for: {relationship_name}")
        else:
            # Add complete _section block
            # Find where to insert (after items block)
            insert_line = start_line + 1
            while insert_line < len(lines):
                line = lines[insert_line]
                
                # Stop at next relationship or end of relationships block
                if (line and not line[0].isspace()) or re.match(r'^  [a-z_]+:', line):
                    break
                
                insert_line += 1
            
            # Build _section block
            section_lines = [
                '    _section:',
                f'      title: {metadata["title"]}',
                f'      description: {metadata["description"]}',
                f'      icon: {metadata["icon"]}',
                f'      order: {metadata["order"]}',
                f'      variant: {metadata["variant"]}'
            ]
            
            # Insert _section before the next relationship or end
            for section_line in reversed(section_lines):
                lines.insert(insert_line, section_line)
            
            additions_made += 1
            if not dry_run:
                print(f"  ✅ Added _section to: {relationship_name}")
    
    return '\n'.join(lines), additions_made


def process_file(file_path: Path, domain: str, dry_run: bool = False) -> int:
    """Process a single frontmatter file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        modified_content, count = add_section_metadata(content, domain, dry_run)
        
        if count > 0:
            if dry_run:
                print(f"  🔍 {file_path.name}: Would add {count} _section blocks")
            else:
                file_path.write_text(modified_content, encoding='utf-8')
                print(f"  ✅ {file_path.name}: Added {count} _section blocks")
        
        return count
    except Exception as e:
        print(f"  ❌ Error processing {file_path.name}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description='Add missing _section metadata to frontmatter relationships')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'all'], 
                       help='Domain to process')
    parser.add_argument('--file', type=Path, help='Process single file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    
    args = parser.parse_args()
    
    if not args.domain and not args.file:
        parser.error('Must specify either --domain or --file')
    
    # Find frontmatter directory
    script_dir = Path(__file__).parent.parent.parent
    frontmatter_dir = script_dir.parent / 'z-beam' / 'frontmatter'
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        sys.exit(1)
    
    total_added = 0
    
    if args.file:
        # Process single file
        if not args.file.exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        
        # Determine domain from path
        domain = args.file.parent.name
        print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}Processing {args.file.name} ({domain} domain)...")
        total_added = process_file(args.file, domain, args.dry_run)
    else:
        # Process domain(s)
        domains = ['materials', 'contaminants', 'compounds', 'settings'] if args.domain == 'all' else [args.domain]
        
        for domain in domains:
            domain_dir = frontmatter_dir / domain
            if not domain_dir.exists():
                print(f"⚠️  Domain directory not found: {domain_dir}")
                continue
            
            print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}Processing {domain} domain...")
            files = sorted(domain_dir.glob('*.yaml'))
            
            for file_path in files:
                count = process_file(file_path, domain, args.dry_run)
                total_added += count
    
    # Summary
    print(f"\n{'═' * 80}")
    if args.dry_run:
        print(f"🔍 DRY RUN COMPLETE - Would add {total_added} _section blocks")
    else:
        print(f"✅ COMPLETE - Added {total_added} _section blocks")
    print(f"{'═' * 80}\n")


if __name__ == '__main__':
    main()
