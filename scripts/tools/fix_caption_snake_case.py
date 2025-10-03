#!/usr/bin/env python3
"""
Fix Caption Snake Case to CamelCase

Migrates all frontmatter YAML files from snake_case caption keys to camelCase.
Converts: before_text → beforeText, after_text → afterText, etc.

Usage:
    python3 scripts/tools/fix_caption_snake_case.py --dry-run  # Preview changes
    python3 scripts/tools/fix_caption_snake_case.py --execute  # Apply changes
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


def convert_caption_to_camelcase(caption: Dict) -> Tuple[Dict, List[str]]:
    """
    Convert caption dictionary from snake_case to camelCase.
    
    Returns:
        Tuple of (converted_caption, list_of_changes)
    """
    converted = caption.copy()
    changes = []
    
    # Map of snake_case → camelCase conversions
    key_mappings = {
        'before_text': 'beforeText',
        'after_text': 'afterText',
        'technical_analysis': 'technicalAnalysis',
        'material_properties': 'materialProperties',
        'image_url': 'imageUrl',
        'technical_focus': 'technicalFocus',
        'unique_characteristics': 'uniqueCharacteristics',
        'contamination_profile': 'contaminationProfile',
        'microscopy_parameters': 'microscopyParameters',
        'quality_metrics': 'qualityMetrics'
    }
    
    # Convert top-level keys
    for snake_key, camel_key in key_mappings.items():
        if snake_key in converted:
            converted[camel_key] = converted.pop(snake_key)
            changes.append(f"  {snake_key} → {camel_key}")
    
    # Convert nested keys in technicalAnalysis
    if 'technicalAnalysis' in converted and isinstance(converted['technicalAnalysis'], dict):
        tech_analysis = converted['technicalAnalysis']
        nested_mappings = {
            'technical_focus': 'focus',
            'unique_characteristics': 'uniqueCharacteristics',
            'contamination_profile': 'contaminationProfile'
        }
        for snake_key, camel_key in nested_mappings.items():
            if snake_key in tech_analysis:
                tech_analysis[camel_key] = tech_analysis.pop(snake_key)
                changes.append(f"  technicalAnalysis.{snake_key} → {camel_key}")
    
    # Convert nested keys in microscopy
    if 'microscopy' in converted and isinstance(converted['microscopy'], dict):
        microscopy = converted['microscopy']
        nested_mappings = {
            'microscopy_parameters': 'parameters',
            'quality_metrics': 'qualityMetrics'
        }
        for snake_key, camel_key in nested_mappings.items():
            if snake_key in microscopy:
                microscopy[camel_key] = microscopy.pop(snake_key)
                changes.append(f"  microscopy.{snake_key} → {camel_key}")
    
    return converted, changes


def process_file(file_path: Path, execute: bool = False) -> Tuple[bool, List[str]]:
    """
    Process a single frontmatter YAML file.
    
    Returns:
        Tuple of (has_changes, list_of_changes)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict) or 'caption' not in data:
            return False, []
        
        caption = data['caption']
        if not isinstance(caption, dict):
            return False, []
        
        # Check if any snake_case keys exist
        snake_case_keys = ['before_text', 'after_text', 'technical_analysis', 
                           'material_properties', 'image_url']
        has_snake_case = any(key in caption for key in snake_case_keys)
        
        if not has_snake_case:
            return False, []
        
        # Convert caption keys
        converted_caption, changes = convert_caption_to_camelcase(caption)
        
        if execute and changes:
            # Update data and write back
            data['caption'] = converted_caption
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                         sort_keys=False, indent=2)
        
        return bool(changes), changes
        
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False, []


def main():
    """Main migration script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix caption snake_case to camelCase')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without applying them')
    parser.add_argument('--execute', action='store_true',
                       help='Apply changes to files')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Must specify either --dry-run or --execute")
        print("Usage:")
        print("  python3 scripts/tools/fix_caption_snake_case.py --dry-run")
        print("  python3 scripts/tools/fix_caption_snake_case.py --execute")
        sys.exit(1)
    
    mode = "DRY RUN" if args.dry_run else "EXECUTE"
    print(f"\n{'='*60}")
    print(f"Caption Snake Case to CamelCase Migration - {mode}")
    print(f"{'='*60}\n")
    
    # Find all frontmatter YAML files
    frontmatter_dir = project_root / "content" / "components" / "frontmatter"
    yaml_files = sorted(frontmatter_dir.glob("*-laser-cleaning.yaml"))
    
    print(f"Found {len(yaml_files)} frontmatter files to check\n")
    
    files_with_changes = []
    total_changes = 0
    
    for file_path in yaml_files:
        has_changes, changes = process_file(file_path, execute=args.execute)
        
        if has_changes:
            files_with_changes.append(file_path.name)
            total_changes += len(changes)
            
            status = "✅ FIXED" if args.execute else "⚠️  NEEDS FIX"
            print(f"{status}: {file_path.name}")
            for change in changes:
                print(f"  {change}")
            print()
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files checked: {len(yaml_files)}")
    print(f"Files with snake_case: {len(files_with_changes)}")
    print(f"Total conversions: {total_changes}")
    
    if args.dry_run and files_with_changes:
        print(f"\n⚠️  Run with --execute to apply these changes")
    elif args.execute and files_with_changes:
        print(f"\n✅ All caption keys converted to camelCase")
    elif not files_with_changes:
        print(f"\n✅ All files already use camelCase")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
