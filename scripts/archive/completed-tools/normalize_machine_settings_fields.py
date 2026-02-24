#!/usr/bin/env python3
"""
Normalize machine settings field names in Settings.yaml.

Changes:
1. powerRange → laserPower (primary power field)
2. power → laserPowerAlternative (backup, for reference)
3. repetitionRate → frequency
4. Ensure machineSettings (camelCase) is used consistently

Usage:
    python3 scripts/tools/normalize_machine_settings_fields.py --dry-run
    python3 scripts/tools/normalize_machine_settings_fields.py --execute
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

SETTINGS_FILE = Path('data/settings/Settings.yaml')

def normalize_settings(data: Dict[str, Any], dry_run: bool = True) -> Tuple[Dict[str, Any], List[str]]:
    """
    Normalize machine settings field names.
    
    Args:
        data: Settings.yaml data dictionary
        dry_run: If True, don't modify data, just report changes
    
    Returns:
        Tuple of (normalized_data, list_of_changes)
    """
    changes = []
    settings_updated = 0
    
    for setting_key, setting_data in data['settings'].items():
        machine_settings = setting_data.get('machineSettings', {})
        setting_changes = 0
        
        # Change 1: powerRange → laserPower (primary field)
        if 'powerRange' in machine_settings:
            machine_settings['laserPower'] = machine_settings.pop('powerRange')
            changes.append(f"{setting_key}: Renamed powerRange → laserPower")
            setting_changes += 1
        
        # Change 2: power → laserPowerAlternative (secondary field, keep for reference)
        if 'power' in machine_settings:
            # Keep as secondary field with clear name
            machine_settings['laserPowerAlternative'] = machine_settings.pop('power')
            changes.append(f"{setting_key}: Renamed power → laserPowerAlternative")
            setting_changes += 1
        
        # Change 3: repetitionRate → frequency
        if 'repetitionRate' in machine_settings:
            machine_settings['frequency'] = machine_settings.pop('repetitionRate')
            changes.append(f"{setting_key}: Renamed repetitionRate → frequency")
            setting_changes += 1
        
        if setting_changes > 0:
            settings_updated += 1
    
    if dry_run:
        print(f"\n{'='*80}")
        print(f"DRY RUN: Machine Settings Field Normalization")
        print(f"{'='*80}\n")
        print(f"📊 Summary:")
        print(f"   Total settings: {len(data['settings'])}")
        print(f"   Settings to update: {settings_updated}")
        print(f"   Total field changes: {len(changes)}")
        print(f"\n📋 Changes by type:")
        power_changes = len([c for c in changes if 'powerRange' in c])
        alt_power_changes = len([c for c in changes if 'power →' in c and 'Alternative' in c])
        freq_changes = len([c for c in changes if 'repetitionRate' in c])
        print(f"   powerRange → laserPower: {power_changes}")
        print(f"   power → laserPowerAlternative: {alt_power_changes}")
        print(f"   repetitionRate → frequency: {freq_changes}")
        
        print(f"\n🔍 Sample changes (first 5):")
        for change in changes[:5]:
            print(f"   • {change}")
        if len(changes) > 5:
            print(f"   ... and {len(changes) - 5} more")
        
        print(f"\n💡 Run with --execute to apply changes")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print(f"EXECUTING: Machine Settings Field Normalization")
        print(f"{'='*80}\n")
        print(f"✅ Applied {len(changes)} changes to {settings_updated} settings")
        print(f"   powerRange → laserPower: {len([c for c in changes if 'powerRange' in c])}")
        print(f"   power → laserPowerAlternative: {len([c for c in changes if 'Alternative' in c])}")
        print(f"   repetitionRate → frequency: {len([c for c in changes if 'repetitionRate' in c])}")
    
    return data, changes

def verify_required_fields(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Verify all settings have required machine parameter fields.
    
    Required fields for Tier 1 validation:
    - laserPower, wavelength, spotSize, frequency
    - pulseWidth, scanSpeed, passCount, overlapRatio
    
    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    required = ['laserPower', 'wavelength', 'spotSize', 'frequency', 
                'pulseWidth', 'scanSpeed', 'passCount', 'overlapRatio']
    
    errors = []
    valid_count = 0
    
    for setting_key, setting_data in data['settings'].items():
        machine_settings = setting_data.get('machineSettings', {})
        missing_fields = [f for f in required if f not in machine_settings]
        
        if missing_fields:
            errors.append(f"{setting_key}: Missing {missing_fields}")
        else:
            valid_count += 1
    
    all_valid = len(errors) == 0
    
    if all_valid:
        print(f"\n✅ VALIDATION PASSED: All {valid_count} settings have required fields")
    else:
        print(f"\n❌ VALIDATION FAILED: {len(errors)} settings missing required fields:")
        for error in errors[:10]:
            print(f"   • {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    
    return all_valid, errors

def main():
    """Main execution function."""
    dry_run = '--execute' not in sys.argv
    
    print(f"\n{'='*80}")
    print(f"Machine Settings Field Normalization Tool")
    print(f"{'='*80}\n")
    print(f"📁 Target: {SETTINGS_FILE}")
    print(f"🔧 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    
    # Load Settings.yaml
    print(f"\n📖 Loading {SETTINGS_FILE}...")
    try:
        with open(SETTINGS_FILE) as f:
            data = yaml.safe_load(f)
        print(f"✅ Loaded successfully ({len(data.get('settings', {}))} settings)")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return 1
    
    # Normalize
    normalized, changes = normalize_settings(data, dry_run)
    
    # Save if not dry run
    if not dry_run:
        print(f"\n💾 Saving changes to {SETTINGS_FILE}...")
        try:
            with open(SETTINGS_FILE, 'w') as f:
                yaml.dump(normalized, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"✅ Saved successfully")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return 1
        
        # Verify after changes
        print(f"\n🔍 Verifying required fields...")
        valid, errors = verify_required_fields(normalized)
        
        if valid:
            print(f"\n{'='*80}")
            print(f"✅ NORMALIZATION COMPLETE")
            print(f"{'='*80}")
            print(f"\n📊 Final Status:")
            print(f"   • {len(changes)} fields renamed")
            print(f"   • {len(data['settings'])} settings validated")
            print(f"   • 0 errors")
            print(f"\n🚀 Next step: Test dataset generation")
            print(f"   python3 scripts/export/generate_datasets.py --domain materials --dry-run")
            print(f"\n{'='*80}\n")
            return 0
        else:
            print(f"\n❌ Validation failed after normalization")
            return 1
    else:
        # Verify what would happen
        print(f"\n🔍 Previewing validation after changes...")
        valid, errors = verify_required_fields(normalized)
        return 0

if __name__ == '__main__':
    sys.exit(main())
