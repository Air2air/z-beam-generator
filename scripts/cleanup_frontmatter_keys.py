#!/usr/bin/env python3
"""
Script to remove specified keys from all frontmatter YAML files.
"""

import yaml
from pathlib import Path

def cleanup_frontmatter_file(file_path):
    """Remove specified keys from a frontmatter YAML file."""
    keys_to_remove = [
        'prompt_chain_verification',
        'properties',
        'generation_mode', 
        'data_source',
        'ai_generated_fields',
        'generated_at',
        'generated_by'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print(f"Warning: Empty or invalid YAML in {file_path}")
            return False
            
        # Remove the specified keys
        removed_keys = []
        for key in keys_to_remove:
            if key in data:
                del data[key]
                removed_keys.append(key)
        
        if removed_keys:
            # Write back the cleaned data
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"✅ Cleaned {file_path}: removed {len(removed_keys)} keys")
            return True
        else:
            print(f"ℹ️  No cleanup needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Clean up all frontmatter files."""
    
    # Find all frontmatter YAML files
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        return
    
    yaml_files = list(frontmatter_dir.glob("*.yaml"))
    
    if not yaml_files:
        print(f"❌ No YAML files found in {frontmatter_dir}")
        return
    
    print(f"🔍 Found {len(yaml_files)} frontmatter files to process")
    
    cleaned_count = 0
    error_count = 0
    
    for yaml_file in sorted(yaml_files):
        if cleanup_frontmatter_file(yaml_file):
            cleaned_count += 1
        else:
            # Check if it was an error or just no cleanup needed
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if any(key in data for key in ['prompt_chain_verification', 'properties', 'generation_mode', 'data_source', 'ai_generated_fields', 'generated_at', 'generated_by']):
                    error_count += 1
            except Exception:
                error_count += 1
    
    print("\n📊 Cleanup Summary:")
    print(f"   Files processed: {len(yaml_files)}")
    print(f"   Files cleaned: {cleaned_count}")
    print(f"   Errors: {error_count}")
    print(f"   No cleanup needed: {len(yaml_files) - cleaned_count - error_count}")

if __name__ == "__main__":
    main()