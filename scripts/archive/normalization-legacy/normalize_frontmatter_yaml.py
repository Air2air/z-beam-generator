#!/usr/bin/env python3
"""
Normalize frontmatter YAML formatting across all material files.
Fixes quote delimiters, YAML structure, and formatting consistency.
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime

def extract_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    # Handle various frontmatter formats
    patterns = [
        r'^---\n(.*?)\n---',  # Standard YAML frontmatter
        r'^```yaml\n(.*?)\n```',  # Code block format
        r'^````markdown\n```yaml\n(.*?)\n```',  # Nested format
    ]
    
    for pattern in patterns:
        match = re.match(pattern, content, re.DOTALL)
        if match:
            return match.group(1), content[match.end():]
    
    return None, content

def normalize_yaml_content(yaml_content):
    """Normalize YAML content structure and formatting."""
    try:
        # Try to parse existing YAML
        data = yaml.safe_load(yaml_content)
        if not isinstance(data, dict):
            return None
        
        # Fix common structural issues
        normalized_data = {}
        
        for key, value in data.items():
            # Fix nested key-value pairs (like name: {name: "value"})
            if isinstance(value, dict) and len(value) == 1 and key in value:
                normalized_data[key] = value[key]
            else:
                normalized_data[key] = value
        
        return normalized_data
        
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
        return None

def format_yaml_with_quotes(data):
    """Format YAML with proper quote usage."""
    # Fields that should always be quoted
    always_quote = {
        'name', 'description', 'author', 'title', 'headline',
        'powerRange', 'pulseDuration', 'wavelength', 'spotSize', 
        'repetitionRate', 'fluenceRange', 'safetyClass'
    }
    
    # Fields that should never be quoted (numbers, booleans)
    never_quote = {
        'id', 'densityPercentile', 'meltingPercentile', 'thermalPercentile',
        'tensilePercentile', 'hardnessPercentile', 'modulusPercentile'
    }
    
    def should_quote_value(key, value):
        if key in always_quote:
            return True
        if key in never_quote:
            return False
        if isinstance(value, (int, float, bool)):
            return False
        if isinstance(value, str):
            # Quote if contains special characters or starts with number
            if re.match(r'^[0-9]', value) or any(c in value for c in ':-[]{}'):
                return True
        return False
    
    def format_value(key, value):
        if isinstance(value, dict):
            return {k: format_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [format_value(key, item) for item in value]
        elif should_quote_value(key, value):
            return f'"{str(value)}"'
        else:
            return value
    
    return {key: format_value(key, value) for key, value in data.items()}

def generate_normalized_frontmatter(data):
    """Generate properly formatted YAML frontmatter."""
    normalized_data = format_yaml_with_quotes(data)
    
    # Custom YAML dumper for better formatting
    yaml_content = yaml.dump(
        normalized_data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,  # Prevent line wrapping
        indent=2
    )
    
    # Clean up formatting issues
    yaml_content = re.sub(r"'([^']*)'", r'"\1"', yaml_content)  # Convert single quotes to double
    
    return f"---\n{yaml_content}---"

def normalize_frontmatter_file(file_path):
    """Normalize a single frontmatter file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        yaml_content, remaining_content = extract_yaml_frontmatter(content)
        
        if yaml_content is None:
            print(f"❌ No valid frontmatter found in {file_path.name}")
            return False
        
        # Normalize YAML structure
        data = normalize_yaml_content(yaml_content)
        
        if data is None:
            print(f"❌ Failed to parse YAML in {file_path.name}")
            return False
        
        # Generate normalized frontmatter
        normalized_frontmatter = generate_normalized_frontmatter(data)
        
        # Create version log
        version_log = f"""
# Version Information
# Generated: {datetime.now().isoformat()}
# Material: {data.get('name', 'Unknown')}
# Component: frontmatter
# Generator: Z-Beam v2.1.0
# Author: AI Assistant
# Normalization: YAML formatting optimized
# File: {file_path.name}
"""
        
        # Combine normalized content
        new_content = normalized_frontmatter + "\\n" + version_log
        
        # Write normalized file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Normalized {file_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main normalization process."""
    print("🔧 FRONTMATTER YAML NORMALIZATION")
    print("=" * 50)
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    # Get all markdown files
    md_files = list(frontmatter_dir.glob('*.md'))
    
    print(f"📁 Found {len(md_files)} frontmatter files")
    
    # Create backup
    backup_dir = frontmatter_dir.parent / 'frontmatter_backup'
    backup_dir.mkdir(exist_ok=True)
    
    print(f"💾 Creating backup in {backup_dir}")
    
    success_count = 0
    error_count = 0
    
    for file_path in md_files:
        # Create backup
        backup_path = backup_dir / file_path.name
        try:
            with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        except Exception as e:
            print(f"⚠️ Backup failed for {file_path.name}: {e}")
        
        # Normalize file
        if normalize_frontmatter_file(file_path):
            success_count += 1
        else:
            error_count += 1
    
    print()
    print("📊 NORMALIZATION RESULTS:")
    print(f"   ✅ Successfully normalized: {success_count} files")
    print(f"   ❌ Errors encountered: {error_count} files")
    print(f"   💾 Backups created in: {backup_dir}")
    
    if success_count > 0:
        print()
        print("🎯 NORMALIZATION IMPROVEMENTS:")
        print("   ✅ Proper YAML delimiters (---)")
        print("   ✅ Consistent quote usage")
        print("   ✅ Fixed nested key-value pairs")
        print("   ✅ Standardized version logs")
        print("   ✅ Optimized field formatting")

if __name__ == "__main__":
    main()
