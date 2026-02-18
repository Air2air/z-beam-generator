#!/usr/bin/env python3
"""
Phase 4: Comprehensive Link Validator
Validates all internal links in frontmatter files.
"""

import sys
import yaml
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_yaml(file_path):
    """Load YAML file"""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {}

def main():
    print("=" * 80)
    print("PHASE 4: COMPREHENSIVE LINK VALIDATION")
    print("=" * 80)
    print()
    
    # Locate frontmatter directory
    frontmatter_dir = project_root.parent / "z-beam/frontmatter"
    
    if not frontmatter_dir.exists():
        print(f"❌ ERROR: Frontmatter directory not found: {frontmatter_dir}")
        return
    
    print(f"📁 Scanning frontmatter directory: {frontmatter_dir}")
    print()
    
    # Build index of all frontmatter files
    print("🔍 Building frontmatter index...")
    file_index = {}
    for domain in ['materials', 'contaminants', 'compounds', 'settings', 'applications']:
        domain_dir = frontmatter_dir / domain
        if domain_dir.exists():
            for yaml_file in domain_dir.glob('*.yaml'):
                slug = yaml_file.stem
                file_index[slug] = {
                    'path': yaml_file,
                    'domain': domain
                }
    
    print(f"   Indexed {len(file_index)} files")
    print()
    
    # Validation results
    validation_results = {
        'files_scanned': 0,
        'total_links': 0,
        'structural_errors': [],
        'broken_links': [],
        'format_errors': [],
        'bidirectional_mismatches': [],
        'orphaned_items': [],
        'stats': defaultdict(int)
    }
    
    print("🔎 Validating links...")
    print("-" * 80)
    
    # URL patterns for each domain
    url_patterns = {
        'materials': r'^/materials/[\w-]+/[\w-]+/[\w-]+$',
        'settings': r'^/settings/[\w-]+/[\w-]+/[\w-]+-settings$',
        'contaminants': r'^/contaminants/[\w-]+/[\w-]+/[\w-]+$',
        'compounds': r'^/compounds/[\w-]+/[\w-]+/[\w-]+-compound$',
        'applications': r'^/applications/[\w-]+$'
    }
    
    # Relationship tracking for bidirectional check
    all_relationships = defaultdict(lambda: defaultdict(list))
    
    # Scan all files
    for slug, file_info in file_index.items():
        validation_results['files_scanned'] += 1
        file_path = file_info['path']
        domain = file_info['domain']
        
        data = load_yaml(file_path)
        if not data:
            continue
        
        # Check for relationships section
        if 'relationships' not in data:
            validation_results['orphaned_items'].append({
                'slug': slug,
                'domain': domain,
                'path': str(file_path)
            })
            continue
        
        relationships = data['relationships']
        if not relationships:
            validation_results['orphaned_items'].append({
                'slug': slug,
                'domain': domain,
                'path': str(file_path)
            })
            continue
        
        # Validate each relationship section
        for rel_type, links in relationships.items():
            if not links or not isinstance(links, list):
                continue
            
            for link in links:
                validation_results['total_links'] += 1
                validation_results['stats'][f"{domain}_links"] += 1
                
                # Structural validation
                if not isinstance(link, dict):
                    validation_results['structural_errors'].append({
                        'file': str(file_path),
                        'error': 'Link is not a dictionary',
                        'link': str(link)
                    })
                    continue
                
                required_fields = ['name', 'slug', 'full_path']
                missing_fields = [f for f in required_fields if f not in link]
                if missing_fields:
                    validation_results['structural_errors'].append({
                        'file': str(file_path),
                        'error': f"Missing fields: {', '.join(missing_fields)}",
                        'link': link
                    })
                    continue
                
                # Target existence validation
                target_slug = link.get('slug', '')
                if target_slug not in file_index:
                    validation_results['broken_links'].append({
                        'source': str(file_path),
                        'target_slug': target_slug,
                        'link': link
                    })
                    continue
                
                # Full path format validation
                target_domain = file_index[target_slug]['domain']
                full_path = link.get('full_path', '')
                pattern = url_patterns.get(target_domain)
                
                if pattern and not re.match(pattern, full_path):
                    validation_results['format_errors'].append({
                        'file': str(file_path),
                        'full_path': full_path,
                        'expected_pattern': pattern,
                        'target_domain': target_domain
                    })
                
                # Track for bidirectional check
                all_relationships[slug][target_slug].append(rel_type)
    
    # Bidirectional consistency check
    print("\n🔄 Checking bidirectional consistency...")
    for source_slug, targets in all_relationships.items():
        for target_slug in targets.keys():
            # Check if reverse relationship exists
            if target_slug in all_relationships:
                if source_slug not in all_relationships[target_slug]:
                    validation_results['bidirectional_mismatches'].append({
                        'source': source_slug,
                        'target': target_slug,
                        'note': f"{source_slug}→{target_slug} exists, but {target_slug}→{source_slug} missing"
                    })
    
    # Print results
    print()
    print("=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    print()
    
    print(f"📊 FILES SCANNED: {validation_results['files_scanned']}")
    print(f"🔗 TOTAL LINKS: {validation_results['total_links']}")
    print()
    
    # Structural validation
    print(f"✅ STRUCTURAL VALIDATION:")
    if validation_results['structural_errors']:
        print(f"   ❌ Errors: {len(validation_results['structural_errors'])}")
        for error in validation_results['structural_errors'][:5]:
            print(f"      • {error['file']}: {error['error']}")
        if len(validation_results['structural_errors']) > 5:
            print(f"      ... and {len(validation_results['structural_errors']) - 5} more")
    else:
        print(f"   ✅ Valid: {validation_results['total_links']}/{validation_results['total_links']} (100%)")
    print()
    
    # Target existence
    print(f"✅ TARGET EXISTENCE:")
    if validation_results['broken_links']:
        print(f"   ❌ Broken links: {len(validation_results['broken_links'])}")
        for error in validation_results['broken_links'][:5]:
            print(f"      • {error['target_slug']} not found (from {Path(error['source']).name})")
        if len(validation_results['broken_links']) > 5:
            print(f"      ... and {len(validation_results['broken_links']) - 5} more")
    else:
        print(f"   ✅ Valid: {validation_results['total_links']}/{validation_results['total_links']} (100%)")
    print()
    
    # Full path format
    print(f"✅ FULL PATH FORMAT:")
    if validation_results['format_errors']:
        print(f"   ❌ Format errors: {len(validation_results['format_errors'])}")
        for error in validation_results['format_errors'][:5]:
            print(f"      • {error['full_path']} (expected: {error['expected_pattern']})")
        if len(validation_results['format_errors']) > 5:
            print(f"      ... and {len(validation_results['format_errors']) - 5} more")
    else:
        print(f"   ✅ Valid: {validation_results['total_links']}/{validation_results['total_links']} (100%)")
    print()
    
    # Bidirectional consistency
    print(f"✅ BIDIRECTIONAL CONSISTENCY:")
    if validation_results['bidirectional_mismatches']:
        print(f"   ⚠️  Unidirectional: {len(validation_results['bidirectional_mismatches'])}")
        for mismatch in validation_results['bidirectional_mismatches'][:5]:
            print(f"      • {mismatch['note']}")
        if len(validation_results['bidirectional_mismatches']) > 5:
            print(f"      ... and {len(validation_results['bidirectional_mismatches']) - 5} more")
    else:
        print(f"   ✅ All relationships are bidirectional")
    print()
    
    # Orphaned items
    print(f"🎯 ORPHANED ITEMS: {len(validation_results['orphaned_items'])} ({len(validation_results['orphaned_items'])/validation_results['files_scanned']*100:.1f}%)")
    
    orphan_by_domain = defaultdict(int)
    for orphan in validation_results['orphaned_items']:
        orphan_by_domain[orphan['domain']] += 1
    
    for domain, count in orphan_by_domain.items():
        print(f"   • {domain}: {count}")
    print()
    
    # Stats
    print(f"📊 CROSS-DOMAIN STATISTICS:")
    for key, value in sorted(validation_results['stats'].items()):
        print(f"   • {key}: {value}")
    print()
    
    # Overall status
    print("=" * 80)
    total_errors = (len(validation_results['structural_errors']) + 
                    len(validation_results['broken_links']) + 
                    len(validation_results['format_errors']))
    
    if total_errors == 0:
        print("✅ VALIDATION PASSED")
        print("=" * 80)
        print()
        return 0
    else:
        print(f"⚠️  VALIDATION ISSUES FOUND: {total_errors} errors")
        print("=" * 80)
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
