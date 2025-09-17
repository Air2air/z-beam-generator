#!/usr/bin/env python3
"""
Simple and reliable frontmatter YAML normalization script.
Focuses on critical fixes without complex processing.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def fix_yaml_delimiters(content):
    """Fix malformed YAML delimiters."""
    # Replace malformed markdown code blocks with proper YAML delimiters
    patterns_to_fix = [
        (r'^````markdown\n```yaml\n', '---\n'),
        (r'^```yaml\n', '---\n'),
        (r'\n```\n````$', '\n---'),
        (r'\n```$', '\n---'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content

def fix_truncated_content(content):
    """Fix known truncated content issues."""
    fixes = [
        # Fix truncated image alt text
        (r'showing preserved$', 'showing preserved microstructure'),
        (r'showing preserved\n', 'showing preserved microstructure\n'),
        # Fix truncated headlines
        (r'headline: "Comprehensive technical guide for$', 
         'headline: "Comprehensive technical guide for laser cleaning applications"'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    return content

def add_version_info(content, filename):
    """Add standardized version information."""
    # Remove existing version logs
    content = re.sub(r'\n---\nVersion Log.*?---\n````', '', content, flags=re.DOTALL)
    content = re.sub(r'\n# Version Information.*?$', '', content, flags=re.DOTALL)
    
    # Extract material name from content
    name_match = re.search(r'name: ["\']?([^"\']+)["\']?', content)
    material_name = name_match.group(1) if name_match else 'Unknown'
    
    # Add clean version information
    version_info = f"""
# Version Information
# Generated: {datetime.now().isoformat()}
# Material: {material_name}
# Component: frontmatter
# Generator: Z-Beam v2.1.0
# Author: AI Assistant
# Normalization: YAML formatting optimized
# File: {filename}
"""
    
    # Ensure content ends with proper YAML delimiter
    if not content.strip().endswith('---'):
        content = content.rstrip() + '\n---'
    
    return content + version_info

def normalize_single_file(file_path):
    """Normalize a single frontmatter file with minimal processing."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        content = fix_yaml_delimiters(content)
        content = fix_truncated_content(content)
        content = add_version_info(content, file_path.name)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def main():
    """Simple normalization with minimal risk."""
    print("🔧 SIMPLE FRONTMATTER NORMALIZATION")
    print("=" * 50)
    
    frontmatter_dir = Path('content/components/frontmatter')
    
    if not frontmatter_dir.exists():
        print(f"❌ Directory not found: {frontmatter_dir}")
        return
    
    # Get all markdown files
    md_files = list(frontmatter_dir.glob('*.md'))
    print(f"📁 Found {len(md_files)} frontmatter files")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for file_path in md_files:
        success, error = normalize_single_file(file_path)
        
        if success:
            print(f"✅ {file_path.name}")
            success_count += 1
        else:
            print(f"❌ {file_path.name}: {error}")
            errors.append(f"{file_path.name}: {error}")
            error_count += 1
    
    print()
    print("📊 NORMALIZATION RESULTS:")
    print(f"   ✅ Successfully processed: {success_count} files")
    print(f"   ❌ Errors encountered: {error_count} files")
    
    if errors:
        print("\n❌ ERROR DETAILS:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
    
    if error_count == 0:
        print("\n🎉 ALL FILES NORMALIZED SUCCESSFULLY!")
        print("✅ Ready for YAML validation testing")
    else:
        print(f"\n⚠️  {error_count} files need manual attention")

if __name__ == "__main__":
    main()
