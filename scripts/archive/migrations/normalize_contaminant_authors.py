#!/usr/bin/env python3
"""
Normalize author objects in Contaminants.yaml
Replaces full 15-field author objects with simple id references

BEFORE:
    author:
      affiliation: {...}
      email: info@z-beam.com
      [13 more fields]

AFTER:
    author:
      id: 3
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.authors.registry import AUTHOR_REGISTRY

# Map author names to IDs
AUTHOR_NAME_TO_ID = {
    "Ikmanda Roswati": 3,      # Indonesia
    "Marco Lombardi": 2,        # Italy  
    "Alessandro Moretti": 2,    # Italy (alias)
    "Jin-Wei Chen": 1,          # Taiwan
    "Yi-Chun Lin": 1,           # Taiwan (alias for Jin-Wei Chen)
    "Todd Dunning": 4           # USA
}

def normalize_contaminants_yaml(input_path: str, output_path: str = None):
    """
    Normalize author objects in Contaminants.yaml
    
    Args:
        input_path: Path to Contaminants.yaml
        output_path: Optional output path (defaults to input_path)
    """
    if output_path is None:
        output_path = input_path
    
    print("🔧 Loading Contaminants.yaml...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    patterns = data.get('contamination_patterns', {})
    total = len(patterns)
    normalized = 0
    skipped = 0
    errors = []
    
    print(f"📊 Found {total} contamination patterns")
    print(f"🔍 Scanning for author objects to normalize...\n")
    
    for pattern_id, pattern_data in patterns.items():
        if 'author' not in pattern_data:
            continue
            
        author = pattern_data['author']
        
        # Remove empty author objects
        if not author or (isinstance(author, dict) and len(author) == 0):
            print(f"🗑️  {pattern_id}: Removing empty author object")
            del pattern_data['author']
            normalized += 1
            continue
        
        # Check if already normalized (just has 'id' field)
        if isinstance(author, dict) and 'id' in author and len(author) == 1:
            skipped += 1
            continue
        
        # Extract author name
        if isinstance(author, dict) and 'name' in author:
            author_name = author['name']
            
            # Look up ID
            if author_name in AUTHOR_NAME_TO_ID:
                author_id = AUTHOR_NAME_TO_ID[author_name]
                
                # Replace with simple id reference
                pattern_data['author'] = {'id': author_id}
                normalized += 1
                
                print(f"✅ {pattern_id}: {author_name} → id: {author_id}")
            else:
                errors.append(f"❌ {pattern_id}: Unknown author '{author_name}'")
        else:
            errors.append(f"⚠️  {pattern_id}: Invalid author format")
    
    # Report results
    print(f"\n{'='*60}")
    print(f"📊 NORMALIZATION RESULTS")
    print(f"{'='*60}")
    print(f"✅ Normalized: {normalized}")
    print(f"⏭️  Skipped (already normalized): {skipped}")
    print(f"❌ Errors: {len(errors)}")
    print(f"{'='*60}\n")
    
    if errors:
        print("⚠️  ERRORS ENCOUNTERED:")
        for error in errors:
            print(f"   {error}")
        print()
    
    if normalized > 0:
        print(f"💾 Writing normalized data to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✅ Successfully normalized {normalized} author objects")
    else:
        print("ℹ️  No changes needed - all authors already normalized")
    
    return {
        'normalized': normalized,
        'skipped': skipped,
        'errors': len(errors),
        'total': total
    }

def verify_normalization(yaml_path: str):
    """Verify all author objects are properly normalized"""
    print("\n🔍 VERIFICATION PHASE")
    print("="*60)
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    patterns = data.get('contamination_patterns', {})
    valid = 0
    invalid = []
    
    for pattern_id, pattern_data in patterns.items():
        if 'author' not in pattern_data:
            continue
        
        author = pattern_data['author']
        
        # Check format: should be {id: N} where N is 1-4
        if isinstance(author, dict) and 'id' in author and len(author) == 1:
            author_id = author['id']
            if 1 <= author_id <= 4:
                valid += 1
            else:
                invalid.append(f"{pattern_id}: Invalid author ID {author_id} (must be 1-4)")
        else:
            invalid.append(f"{pattern_id}: Not normalized (has {len(author) if isinstance(author, dict) else 0} fields)")
    
    print(f"✅ Valid normalized authors: {valid}")
    print(f"❌ Invalid/non-normalized: {len(invalid)}")
    
    if invalid:
        print("\n⚠️  INVALID ENTRIES:")
        for entry in invalid[:10]:  # Show first 10
            print(f"   {entry}")
        if len(invalid) > 10:
            print(f"   ... and {len(invalid) - 10} more")
    else:
        print("\n🎉 ALL AUTHOR OBJECTS PROPERLY NORMALIZED!")
    
    print("="*60)
    
    return len(invalid) == 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Normalize author objects in Contaminants.yaml")
    parser.add_argument('--input', default='data/contaminants/Contaminants.yaml',
                        help='Input YAML file path')
    parser.add_argument('--output', default=None,
                        help='Output YAML file path (defaults to input)')
    parser.add_argument('--verify-only', action='store_true',
                        help='Only verify normalization, do not modify')
    
    args = parser.parse_args()
    
    if args.verify_only:
        success = verify_normalization(args.input)
        sys.exit(0 if success else 1)
    else:
        results = normalize_contaminants_yaml(args.input, args.output)
        
        # Verify after normalization
        if results['normalized'] > 0:
            print()
            verify_normalization(args.output or args.input)
        
        sys.exit(0 if results['errors'] == 0 else 1)
