#!/usr/bin/env python3
"""
Migrate challenges from data-based to ID-based references.

Converts Settings.yaml challenges from raw data objects to ID references
pointing to ChallengePatterns.yaml library.

Before:
  relationships:
    challenges:
      items:
        - thermal_management:
            - challenge: "High thermal conductivity..."
              severity: medium
              solutions: [...]

After:
  relationships:
    challenges:
      items:
        - thermal_management:
            - id: high-thermal-conductivity
              type: challenge
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Challenge text → library ID mapping
CHALLENGE_MAPPING = {
    # Thermal management challenges
    "High thermal conductivity and heat spread": "high-thermal-conductivity",
    "Low thermal diffusivity and heat accumulation": "low-thermal-diffusivity",
    "Anisotropic thermal properties": "anisotropic-thermal",
    "Moisture-induced spalling and explosive failure": "moisture-spalling",
    "Charring and carbonization": "charring-carbonization",
    "Melting and heat-affected zone formation": "melting-haz",
    "Matrix degradation and delamination": "matrix-degradation",
    "Slow thermal diffusivity": "slow-thermal-diffusivity",
    
    # Contamination challenges
    "Rust and oxide layer removal": "rust-oxide-removal",
    "Oil and grease removal": "oil-grease-removal",
    "Paint and coating removal": "paint-coating-removal",
    "Adhesive and paint removal": "adhesive-paint-removal",
    "Biological growth and deep staining": "biological-growth",
    "Coating and residue removal": "coating-residue-removal",
    "Varnish and coating removal": "varnish-coating-removal",
    "Resin-based contaminant removal": "resin-contaminant-removal",
}

def find_challenge_id(challenge_text: str) -> str:
    """Match challenge text to library ID."""
    # Exact match
    if challenge_text in CHALLENGE_MAPPING:
        return CHALLENGE_MAPPING[challenge_text]
    
    # Fuzzy match (starts with)
    for known_challenge, challenge_id in CHALLENGE_MAPPING.items():
        if challenge_text.startswith(known_challenge[:30]):
            return challenge_id
    
    # Unknown challenge - return None to keep as data
    return None

def migrate_challenges_for_setting(setting_data: Dict[str, Any]) -> tuple[int, int]:
    """
    Migrate challenges in a single setting.
    
    Returns:
        (migrated_count, kept_as_data_count)
    """
    migrated = 0
    kept_as_data = 0
    
    if 'relationships' not in setting_data:
        return migrated, kept_as_data
    
    if 'challenges' not in setting_data['relationships']:
        return migrated, kept_as_data
    
    challenges_rel = setting_data['relationships']['challenges']
    if 'items' not in challenges_rel:
        return migrated, kept_as_data
    
    new_items = []
    
    for item in challenges_rel['items']:
        if not isinstance(item, dict):
            new_items.append(item)
            continue
        
        new_item = {}
        
        # Process thermal_management challenges
        if 'thermal_management' in item:
            thermal_list = item['thermal_management']
            if isinstance(thermal_list, list):
                new_thermal = []
                for challenge_obj in thermal_list:
                    if isinstance(challenge_obj, dict) and 'challenge' in challenge_obj:
                        challenge_id = find_challenge_id(challenge_obj['challenge'])
                        if challenge_id:
                            # Convert to ID reference
                            new_thermal.append({
                                'id': challenge_id,
                                'type': 'challenge'
                            })
                            migrated += 1
                        else:
                            # Keep as data (unknown pattern)
                            new_thermal.append(challenge_obj)
                            kept_as_data += 1
                    else:
                        new_thermal.append(challenge_obj)
                new_item['thermal_management'] = new_thermal
        
        # Process contamination_challenges
        if 'contamination_challenges' in item:
            contam_list = item['contamination_challenges']
            if isinstance(contam_list, list):
                new_contam = []
                for challenge_obj in contam_list:
                    if isinstance(challenge_obj, dict) and 'challenge' in challenge_obj:
                        challenge_id = find_challenge_id(challenge_obj['challenge'])
                        if challenge_id:
                            # Convert to ID reference
                            new_contam.append({
                                'id': challenge_id,
                                'type': 'challenge'
                            })
                            migrated += 1
                        else:
                            # Keep as data (unknown pattern)
                            new_contam.append(challenge_obj)
                            kept_as_data += 1
                    else:
                        new_contam.append(challenge_obj)
                new_item['contamination_challenges'] = new_contam
        
        new_items.append(new_item)
    
    challenges_rel['items'] = new_items
    return migrated, kept_as_data

def migrate_settings_file(dry_run: bool = False) -> Dict[str, int]:
    """
    Migrate all settings in Settings.yaml.
    
    Returns:
        Statistics dict
    """
    settings_path = Path('data/settings/Settings.yaml')
    
    # Load data
    with open(settings_path, 'r') as f:
        data = yaml.safe_load(f)
    
    stats = {
        'total_settings': 0,
        'settings_with_challenges': 0,
        'challenges_migrated': 0,
        'challenges_kept_as_data': 0
    }
    
    # Process each setting
    for setting_id, setting_data in data.get('settings', {}).items():
        stats['total_settings'] += 1
        
        migrated, kept = migrate_challenges_for_setting(setting_data)
        
        if migrated > 0 or kept > 0:
            stats['settings_with_challenges'] += 1
            stats['challenges_migrated'] += migrated
            stats['challenges_kept_as_data'] += kept
    
    # Save if not dry run
    if not dry_run:
        # Backup
        backup_path = settings_path.with_suffix(
            f'.yaml.backup_challenges_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        with open(backup_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✅ Backup created: {backup_path}")
        
        # Save migrated data
        with open(settings_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"✅ Settings.yaml updated")
    
    return stats

def main():
    dry_run = '--dry-run' in sys.argv
    
    print("=" * 70)
    print("CHALLENGE MIGRATION TO LIBRARY REFERENCES")
    print("=" * 70)
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified\n")
    
    stats = migrate_settings_file(dry_run=dry_run)
    
    print("\n📊 MIGRATION STATISTICS")
    print(f"Total settings: {stats['total_settings']}")
    print(f"Settings with challenges: {stats['settings_with_challenges']}")
    print(f"Challenges migrated to ID references: {stats['challenges_migrated']}")
    print(f"Challenges kept as data (unknown patterns): {stats['challenges_kept_as_data']}")
    
    if dry_run:
        print("\n⚠️  This was a dry run. Use without --dry-run to apply changes.")
    else:
        print(f"\n✅ Migration complete!")
        print(f"   {stats['challenges_migrated']} data objects → ID references")
        print(f"   {stats['challenges_kept_as_data']} unknown patterns kept as data")
        print(f"\n📚 Challenge library: data/challenges/ChallengePatterns.yaml")
        print(f"📝 Source data: data/settings/Settings.yaml")

if __name__ == '__main__':
    main()
