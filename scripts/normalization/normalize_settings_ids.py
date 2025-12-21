#!/usr/bin/env python3
"""
Normalize Settings.yaml IDs to match cross-domain conventions

CHANGES:
- Title Case with spaces -> lowercase-with-hyphens
- Add 'name' field with original Title Case value
- Preserve all other data

EXAMPLES:
- "Aluminum" -> "aluminum" (name: "Aluminum")
- "Borosilicate Glass" -> "borosilicate-glass" (name: "Borosilicate Glass")
- "Acrylic (PMMA)" -> "acrylic-pmma" (name: "Acrylic (PMMA)")
"""

import yaml
from pathlib import Path


def normalize_id(title_case_id: str) -> str:
    """Convert Title Case ID to lowercase-with-hyphens"""
    # Remove parentheses content but keep it for name
    normalized = title_case_id.lower()
    
    # Replace spaces with hyphens
    normalized = normalized.replace(' ', '-')
    
    # Remove parentheses but keep content
    normalized = normalized.replace('(', '').replace(')', '')
    
    # Clean up multiple hyphens
    while '--' in normalized:
        normalized = normalized.replace('--', '-')
    
    return normalized


def main():
    settings_file = Path('data/settings/Settings.yaml')
    
    print("Loading Settings.yaml...")
    with open(settings_file, 'r') as f:
        data = yaml.safe_load(f)
    
    old_settings = data.get('settings', {})
    new_settings = {}
    
    print(f"\nNormalizing {len(old_settings)} setting IDs...")
    
    changes = []
    
    for old_id, setting_data in old_settings.items():
        # Generate new ID
        new_id = normalize_id(old_id)
        
        # Add name field if not present
        if 'name' not in setting_data or not setting_data['name']:
            setting_data['name'] = old_id
        
        # Store with new ID
        new_settings[new_id] = setting_data
        
        if old_id != new_id:
            changes.append((old_id, new_id))
    
    # Update data
    data['settings'] = new_settings
    
    # Write back
    print(f"\nWriting normalized Settings.yaml...")
    with open(settings_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ COMPLETE: {len(changes)} IDs normalized")
    print(f"\nFirst 10 changes:")
    for old_id, new_id in changes[:10]:
        print(f"  '{old_id}' -> '{new_id}'")
    
    if len(changes) > 10:
        print(f"  ... and {len(changes) - 10} more")
    
    return len(changes)


if __name__ == '__main__':
    count = main()
    print(f"\n{'='*80}")
    print(f"NORMALIZATION COMPLETE: {count} settings updated")
    print(f"{'='*80}")
