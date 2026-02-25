#!/usr/bin/env python3
"""
Restore Challenges Data from Backup

This script merges the 'challenges' field from Settings_backup_20251221_131702.yaml
back into the current Settings.yaml file.

The backup has keys like 'alabaster' with challenges data.
The current has keys like 'alabaster-settings' without challenges.

This script:
1. Loads both files
2. Maps backup keys to current keys (alabaster -> alabaster-settings)
3. Copies 'challenges' field from backup to current
4. Preserves all other current data
5. Creates backup before modifying
"""

import yaml
from pathlib import Path
from datetime import datetime
import sys

def map_backup_key_to_current(backup_key: str) -> str:
    """
    Map backup key format to current key format.
    
    Example: 'alabaster' -> 'alabaster-settings'
    """
    if backup_key.endswith('-settings'):
        return backup_key
    return f"{backup_key}-settings"

def restore_challenges():
    """Main restoration function."""
    
    current_file = Path('data/settings/Settings.yaml')
    backup_file = Path('data/settings/Settings_backup_20251221_131702.yaml')
    
    if not current_file.exists():
        print(f"❌ Current file not found: {current_file}")
        sys.exit(1)
        
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_file}")
        sys.exit(1)
    
    print("📂 Loading files...")
    
    # Load current
    with open(current_file, 'r') as f:
        current = yaml.safe_load(f)
    
    # Load backup
    with open(backup_file, 'r') as f:
        backup = yaml.safe_load(f)
    
    print(f"✅ Loaded {len(current['settings'])} current settings")
    print(f"✅ Loaded {len(backup['settings'])} backup settings")
    
    # Create backup of current file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = current_file.parent / f"Settings.yaml.backup_{timestamp}"
    
    print(f"\n💾 Creating backup: {backup_path.name}")
    with open(backup_path, 'w') as f:
        yaml.dump(current, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Restore challenges
    restored_count = 0
    missing_count = 0
    
    print("\n🔄 Restoring challenges field...")
    
    for backup_key, backup_data in backup['settings'].items():
        if 'challenges' not in backup_data:
            continue
            
        # Map to current key format
        current_key = map_backup_key_to_current(backup_key)
        
        if current_key not in current['settings']:
            print(f"⚠️  Warning: Current key not found: {current_key} (from {backup_key})")
            missing_count += 1
            continue
        
        # Copy challenges field
        current['settings'][current_key]['challenges'] = backup_data['challenges']
        restored_count += 1
    
    print(f"\n✅ Restored challenges to {restored_count} settings")
    
    if missing_count > 0:
        print(f"⚠️  {missing_count} backup entries not found in current file")
    
    # Verify restoration
    verification_count = sum(1 for s in current['settings'].values() if 'challenges' in s)
    print(f"\n🔍 Verification: {verification_count} settings now have challenges field")
    
    # Save updated file
    print(f"\n💾 Saving updated Settings.yaml...")
    with open(current_file, 'w') as f:
        yaml.dump(current, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n✅ COMPLETE - Challenges restored!")
    print(f"   - Backup created: {backup_path.name}")
    print(f"   - Settings with challenges: {verification_count}")
    print(f"   - Challenge categories: thermal_management, surface_characteristics, contamination_challenges")
    
    return verification_count

if __name__ == '__main__':
    try:
        count = restore_challenges()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
