#!/usr/bin/env python3
"""
Challenge Query Tool
Query materials by challenge_id for cross-material analysis.

Usage:
    python3 scripts/tools/query_challenges.py high_reflectivity
    python3 scripts/tools/query_challenges.py thermal_shock_and_microcracking
    python3 scripts/tools/query_challenges.py --list-challenges
    python3 scripts/tools/query_challenges.py --stats
"""

import yaml
from pathlib import Path
from collections import defaultdict
import sys

def load_all_challenges():
    """Load challenges from all settings files."""
    materials_with_challenges = {}
    
    for yaml_file in Path('frontmatter/settings').glob('*.yaml'):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        
        if data and 'material_challenges' in data:
            material_id = data.get('id', yaml_file.stem)
            material_name = data.get('name', material_id)
            materials_with_challenges[material_id] = {
                'name': material_name,
                'challenges': data['material_challenges']
            }
    
    return materials_with_challenges

def find_materials_with_challenge(challenge_id: str):
    """Find all materials with a specific challenge_id."""
    materials_data = load_all_challenges()
    results = []
    
    for material_id, data in materials_data.items():
        challenges = data['challenges']
        
        for category in ['thermal_management', 'surface_characteristics', 'contamination_challenges']:
            if category in challenges and isinstance(challenges[category], list):
                for challenge in challenges[category]:
                    if challenge.get('challenge_id') == challenge_id:
                        results.append({
                            'material_id': material_id,
                            'material_name': data['name'],
                            'category': category,
                            'challenge': challenge.get('challenge'),
                            'severity': challenge.get('severity'),
                            'impact': challenge.get('impact', '')[:80] + '...' if challenge.get('impact') else 'N/A'
                        })
    
    return results

def list_all_challenge_ids():
    """List all unique challenge IDs."""
    materials_data = load_all_challenges()
    challenge_ids = defaultdict(int)
    
    for material_id, data in materials_data.items():
        challenges = data['challenges']
        
        for category in ['thermal_management', 'surface_characteristics', 'contamination_challenges']:
            if category in challenges and isinstance(challenges[category], list):
                for challenge in challenges[category]:
                    cid = challenge.get('challenge_id')
                    if cid:
                        challenge_ids[cid] += 1
    
    return dict(sorted(challenge_ids.items(), key=lambda x: x[1], reverse=True))

def print_stats():
    """Print challenge statistics."""
    materials_data = load_all_challenges()
    challenge_ids = list_all_challenge_ids()
    
    total_materials = len(materials_data)
    total_challenges = sum(challenge_ids.values())
    unique_challenges = len(challenge_ids)
    
    print(f"📊 Challenge Statistics")
    print(f"=" * 60)
    print(f"Materials with challenges: {total_materials}")
    print(f"Total challenge instances: {total_challenges}")
    print(f"Unique challenge types: {unique_challenges}")
    print(f"\n🔝 Top 10 Most Common Challenges:")
    print(f"-" * 60)
    
    for i, (cid, count) in enumerate(list(challenge_ids.items())[:10], 1):
        print(f"{i:2d}. {cid:45s} ({count:3d} materials)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == '--list-challenges':
        challenge_ids = list_all_challenge_ids()
        print(f"📋 All Challenge IDs ({len(challenge_ids)} unique)")
        print("=" * 60)
        for cid, count in challenge_ids.items():
            print(f"{cid:50s} ({count:3d} materials)")
    
    elif arg == '--stats':
        print_stats()
    
    else:
        # Query specific challenge
        challenge_id = arg
        results = find_materials_with_challenge(challenge_id)
        
        if not results:
            print(f"❌ No materials found with challenge_id: {challenge_id}")
            print(f"\nUse --list-challenges to see all available IDs")
        else:
            print(f"🔍 Materials with challenge: {challenge_id}")
            print(f"=" * 80)
            print(f"Found {len(results)} materials\n")
            
            for r in results:
                print(f"📌 {r['material_name']} ({r['material_id']})")
                print(f"   Category: {r['category']}")
                print(f"   Challenge: {r['challenge']}")
                print(f"   Severity: {r['severity']}")
                print(f"   Impact: {r['impact']}")
                print()

if __name__ == '__main__':
    main()
