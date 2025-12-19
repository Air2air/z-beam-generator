#!/usr/bin/env python3
"""
Phase 1: Frontmatter Key Audit
Analyzes all 424 frontmatter files to identify scattered keys and modularization opportunities.
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any
import json

# Path to frontmatter directory
FRONTMATTER_DIR = Path("/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter")

def get_all_keys_recursive(data: Any, prefix: str = "") -> Set[str]:
    """Recursively extract all keys from nested dict/list structures"""
    keys = set()
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            keys.update(get_all_keys_recursive(value, full_key))
    elif isinstance(data, list) and data:
        # Sample first item to understand list structure
        keys.update(get_all_keys_recursive(data[0], prefix + "[]"))
    
    return keys

def analyze_file(filepath: Path) -> Dict:
    """Analyze single frontmatter file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return {'error': 'Empty file', 'keys': set()}
        
        # Get all keys
        all_keys = get_all_keys_recursive(data)
        
        # Top-level keys
        top_level = set(data.keys())
        
        # Relationship keys
        relationship_keys = set()
        if 'relationships' in data and isinstance(data['relationships'], dict):
            relationship_keys = set(data['relationships'].keys())
        
        return {
            'filename': filepath.name,
            'domain': filepath.parent.name,
            'all_keys': all_keys,
            'top_level_keys': top_level,
            'relationship_keys': relationship_keys,
            'has_relationships': 'relationships' in data,
            'data': data  # Keep for value analysis
        }
    except Exception as e:
        return {'error': str(e), 'filename': filepath.name, 'keys': set()}

def find_duplicate_values(files_data: List[Dict]) -> Dict:
    """Find values that appear in multiple files (candidates for modularization)"""
    value_tracker = defaultdict(list)
    
    for file_info in files_data:
        if 'data' not in file_info:
            continue
        
        data = file_info['data']
        filename = file_info['filename']
        
        # Track specific high-value data patterns
        if 'ppe_requirements' in data:
            ppe_str = json.dumps(data['ppe_requirements'], sort_keys=True)
            value_tracker[f"ppe_requirements:{ppe_str}"].append(filename)
        
        if 'regulatory_standards' in data:
            # Check each standard
            for std in data.get('regulatory_standards', []):
                if isinstance(std, dict):
                    std_str = json.dumps(std, sort_keys=True)
                    value_tracker[f"regulatory_standard:{std_str}"].append(filename)
        
        if 'emergency_response' in data:
            er_str = json.dumps(data['emergency_response'], sort_keys=True)
            value_tracker[f"emergency_response:{er_str}"].append(filename)
    
    # Filter to duplicates (appears in 2+ files)
    duplicates = {k: v for k, v in value_tracker.items() if len(v) >= 2}
    return duplicates

def main():
    print("="*80)
    print("PHASE 1: FRONTMATTER KEY AUDIT")
    print("="*80)
    print()
    
    # Collect all YAML files
    all_files = []
    for domain in ['materials', 'contaminants', 'compounds', 'settings']:
        domain_path = FRONTMATTER_DIR / domain
        if domain_path.exists():
            all_files.extend(domain_path.glob("*.yaml"))
    
    print(f"📊 Analyzing {len(all_files)} frontmatter files...")
    print()
    
    # Analyze each file
    files_data = []
    for filepath in sorted(all_files):
        result = analyze_file(filepath)
        if 'error' not in result:
            files_data.append(result)
        else:
            print(f"⚠️  Error in {filepath.name}: {result['error']}")
    
    print(f"✅ Successfully analyzed {len(files_data)} files")
    print()
    
    # Aggregate statistics
    all_keys_counter = Counter()
    top_level_keys_counter = Counter()
    relationship_keys_counter = Counter()
    keys_by_domain = defaultdict(lambda: defaultdict(set))
    
    for file_info in files_data:
        domain = file_info['domain']
        
        # Count key occurrences
        for key in file_info['all_keys']:
            all_keys_counter[key] += 1
            keys_by_domain[domain]['all'].add(key)
        
        for key in file_info['top_level_keys']:
            top_level_keys_counter[key] += 1
            keys_by_domain[domain]['top_level'].add(key)
        
        for key in file_info['relationship_keys']:
            relationship_keys_counter[key] += 1
            keys_by_domain[domain]['relationships'].add(key)
    
    # Print results
    print("="*80)
    print("1. TOP-LEVEL KEYS (Should mostly be page-specific)")
    print("="*80)
    
    # Page-specific keys (should stay at top-level)
    page_specific = {
        'id', 'name', 'slug', 'title', 'display_name', 'category', 'subcategory',
        'content_type', 'schema_version', 'datePublished', 'dateModified',
        'description', 'micro', 'faq', 'author', 'images', 'breadcrumb',
        'breadcrumb_text', 'seo_description', 'excerpt'
    }
    
    print("\n✅ PAGE-SPECIFIC KEYS (correct at top-level):")
    for key in sorted(page_specific):
        if key in top_level_keys_counter:
            count = top_level_keys_counter[key]
            print(f"   {key:30} {count:4} files")
    
    print("\n⚠️  SCATTERED KEYS (should move to relationships):")
    scattered = set(top_level_keys_counter.keys()) - page_specific
    for key in sorted(scattered):
        count = top_level_keys_counter[key]
        # Show which domains have this key
        domains_with_key = [d for d in keys_by_domain if key in keys_by_domain[d]['top_level']]
        print(f"   {key:40} {count:4} files  [{', '.join(domains_with_key)}]")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total top-level keys: {len(top_level_keys_counter)}")
    print(f"   Page-specific (correct): {len(page_specific & set(top_level_keys_counter.keys()))}")
    print(f"   Scattered (need migration): {len(scattered)}")
    
    # Relationship keys analysis
    print("\n" + "="*80)
    print("2. RELATIONSHIP KEYS (current usage)")
    print("="*80)
    
    for key in sorted(relationship_keys_counter.keys()):
        count = relationship_keys_counter[key]
        domains_with_key = [d for d in keys_by_domain if key in keys_by_domain[d]['relationships']]
        print(f"   {key:40} {count:4} files  [{', '.join(domains_with_key)}]")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total relationship types: {len(relationship_keys_counter)}")
    print(f"   Files with relationships key: {sum(1 for f in files_data if f['has_relationships'])}/{len(files_data)}")
    
    # Domain-specific analysis
    print("\n" + "="*80)
    print("3. KEYS BY DOMAIN")
    print("="*80)
    
    for domain in sorted(keys_by_domain.keys()):
        print(f"\n{domain.upper()}:")
        top_keys = keys_by_domain[domain]['top_level']
        rel_keys = keys_by_domain[domain]['relationships']
        
        print(f"   Top-level keys: {len(top_keys)}")
        print(f"   Relationship keys: {len(rel_keys)}")
        
        # Show unique keys not in other domains
        other_domains = [d for d in keys_by_domain.keys() if d != domain]
        unique_top = top_keys - set().union(*[keys_by_domain[d]['top_level'] for d in other_domains])
        if unique_top:
            print(f"   Unique top-level keys: {sorted(unique_top)}")
    
    # Modularization opportunities
    print("\n" + "="*80)
    print("4. MODULARIZATION OPPORTUNITIES")
    print("="*80)
    
    duplicates = find_duplicate_values(files_data)
    
    print(f"\n📦 Found {len(duplicates)} duplicate value patterns:")
    
    # Group by type
    ppe_dups = {k: v for k, v in duplicates.items() if k.startswith('ppe_requirements:')}
    reg_dups = {k: v for k, v in duplicates.items() if k.startswith('regulatory_standard:')}
    er_dups = {k: v for k, v in duplicates.items() if k.startswith('emergency_response:')}
    
    if ppe_dups:
        print(f"\n⚠️  PPE Requirements: {len(ppe_dups)} duplicate patterns")
        for pattern, files in list(ppe_dups.items())[:3]:
            print(f"   Used in {len(files)} files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
    
    if reg_dups:
        print(f"\n⚠️  Regulatory Standards: {len(reg_dups)} duplicate patterns")
        for pattern, files in list(reg_dups.items())[:3]:
            print(f"   Used in {len(files)} files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
    
    if er_dups:
        print(f"\n⚠️  Emergency Response: {len(er_dups)} duplicate patterns")
        for pattern, files in list(er_dups.items())[:3]:
            print(f"   Used in {len(files)} files: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
    
    # Recommendations
    print("\n" + "="*80)
    print("5. RECOMMENDATIONS")
    print("="*80)
    
    print("\n📋 IMMEDIATE ACTIONS:")
    print()
    print("1. MOVE TO RELATIONSHIPS:")
    for key in sorted(list(scattered)[:10]):  # Show top 10
        count = top_level_keys_counter[key]
        print(f"   • {key} ({count} files)")
    if len(scattered) > 10:
        print(f"   ... and {len(scattered) - 10} more keys")
    
    print("\n2. CREATE MODULAR DATA FILES:")
    if len(ppe_dups) > 0:
        print(f"   • PPE Requirements Library ({len(ppe_dups)} patterns)")
    if len(reg_dups) > 0:
        print(f"   • Regulatory Standards Library ({len(reg_dups)} patterns)")
    if len(er_dups) > 0:
        print(f"   • Emergency Response Templates ({len(er_dups)} patterns)")
    
    print("\n3. STANDARDIZE STRUCTURES:")
    print("   • All relationship entries use unified schema")
    print("   • Reference external libraries by ID")
    print("   • Validate against TypeScript interfaces")
    
    print("\n" + "="*80)
    print("✅ AUDIT COMPLETE")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Review scattered keys list above")
    print("2. Decide which keys move to relationships")
    print("3. Design modular data files for common patterns")
    print("4. Create TypeScript interfaces for validation")
    print()

if __name__ == "__main__":
    main()
