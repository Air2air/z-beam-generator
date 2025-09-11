#!/usr/bin/env python3
"""
CRITICAL FIX: Nested YAML Property Generation Bug

This script fixes the nested YAML property generation bug that's blocking TypeScript builds.
Converts nested properties like:
  name:
    name: "value"
To flat properties like:
  name: "value"
"""

import yaml
import re
from pathlib import Path

def fix_nested_yaml_properties(content: str) -> str:
    """
    Fix nested YAML properties in frontmatter content.
    
    Args:
        content: Raw frontmatter content with potential nested properties
        
    Returns:
        Fixed frontmatter content with flat properties
    """
    try:
        # Extract YAML content
        if not content.startswith("---"):
            return content
            
        parts = content.split("---", 2)
        if len(parts) < 2:
            return content
            
        yaml_content = parts[1].strip()
        remaining_content = "---".join(parts[2:]) if len(parts) > 2 else ""
        
        # Parse YAML
        data = yaml.safe_load(yaml_content)
        if not data:
            return content
            
        # Fix nested properties
        fixed_data = fix_nested_dict(data)
        
        # Convert back to YAML
        fixed_yaml = yaml.dump(fixed_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Reconstruct content
        result = f"---\n{fixed_yaml.strip()}\n---"
        if remaining_content:
            result += remaining_content
            
        return result
        
    except Exception as e:
        print(f"Error fixing YAML: {e}")
        return content

def fix_nested_dict(data):
    """
    Recursively fix nested dictionary properties.
    
    Converts patterns like:
    {
        "name": {"name": "value"},
        "title": {"title": "value"}
    }
    To:
    {
        "name": "value",
        "title": "value"
    }
    """
    if not isinstance(data, dict):
        return data
        
    fixed_data = {}
    for key, value in data.items():
        if isinstance(value, dict) and len(value) == 1 and key in value:
            # This is the nested pattern: key: {key: actual_value}
            actual_value = value[key]
            print(f"  Fixed nested property: {key}: {{{key}: {actual_value}}} -> {key}: {actual_value}")
            fixed_data[key] = actual_value
        elif isinstance(value, dict):
            # Recursively fix nested dictionaries
            fixed_data[key] = fix_nested_dict(value)
        elif isinstance(value, list):
            # Fix nested patterns in lists
            fixed_data[key] = [fix_nested_dict(item) if isinstance(item, dict) else item for item in value]
        else:
            # Keep as is
            fixed_data[key] = value
            
    return fixed_data

def main():
    """Fix nested YAML properties in problematic files."""
    
    # List of files with known nested property issues
    problematic_files = [
        "content/components/frontmatter/phenolic-resin-composites-laser-cleaning.md",
        "content/components/frontmatter/thermoplastic-elastomer-laser-cleaning.md"
    ]
    
    print("🔧 CRITICAL FIX: Nested YAML Property Generation Bug")
    print("=" * 60)
    
    fixed_count = 0
    
    for file_path in problematic_files:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n📁 Processing: {file_path}")
        
        # Read original content
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # Fix nested properties
        fixed_content = fix_nested_yaml_properties(original_content)
        
        # Check if changes were made
        if fixed_content != original_content:
            # Backup original
            backup_path = path.with_suffix(path.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"  💾 Backup created: {backup_path}")
            
            # Write fixed content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed nested properties in: {file_path}")
            fixed_count += 1
        else:
            print(f"  ℹ️  No nested properties found in: {file_path}")
    
    print(f"\n🎯 Fixed {fixed_count} files with nested property issues")
    print("TypeScript builds should now work correctly.")

if __name__ == "__main__":
    main()
