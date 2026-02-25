#!/usr/bin/env python3
"""
Phase 1 + 2: Fix camelCase keys AND remove redundant prefixes
Comprehensive replacement across all files in codebase.
"""

import os
import re
from pathlib import Path

# Replacement mappings (order matters - do specific replacements first)
REPLACEMENTS = [
    ('characteristics', 'characteristics'),
    ('properties', 'properties'),
    ('metadata', 'metadata'),
    ('description', 'description'),
    ('regulatory_standards', 'regulatory_standards'),
    ('machine_settings', 'machine_settings'),
    ('challenges', 'challenges'),
]

# File patterns to process
FILE_PATTERNS = ['*.py', '*.yaml', '*.yml', '*.md', '*.json']

# Directories to skip
SKIP_DIRS = {'.git', '__pycache__', 'venv', 'node_modules', '.pytest_cache'}

def should_process_file(file_path):
    """Check if file should be processed."""
    # Skip if in excluded directory
    for part in file_path.parts:
        if part in SKIP_DIRS:
            return False
    
    # Only process files matching our patterns
    for pattern in FILE_PATTERNS:
        if file_path.match(pattern):
            return True
    
    return False

def process_file(file_path):
    """Apply replacements to a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacements_made = []
        
        # Apply each replacement
        for old_key, new_key in REPLACEMENTS:
            if old_key in content:
                content = content.replace(old_key, new_key)
                count = original_content.count(old_key)
                replacements_made.append((old_key, new_key, count))
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_made
        
    except Exception as e:
        print(f"⚠️  Error processing {file_path}: {e}")
    
    return []

def main():
    print("🔄 Phase 1 + 2: Renaming keys for consistency and clarity...")
    print("")
    print("📝 Changes to apply:")
    for old_key, new_key in REPLACEMENTS:
        print(f"   {old_key} → {new_key}")
    print("")
    
    # Process z-beam-generator directory
    root_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam-generator')
    files_processed = 0
    total_replacements = {old: 0 for old, _ in REPLACEMENTS}
    
    print("📂 Processing z-beam-generator...")
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            replacements = process_file(file_path)
            if replacements:
                files_processed += 1
                for old_key, new_key, count in replacements:
                    total_replacements[old_key] += count
    
    # Process production frontmatter directory
    frontmatter_dir = Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter')
    if frontmatter_dir.exists():
        print("📂 Processing production frontmatter...")
        for file_path in frontmatter_dir.rglob('*.yaml'):
            if file_path.is_file():
                replacements = process_file(file_path)
                if replacements:
                    files_processed += 1
                    for old_key, new_key, count in replacements:
                        total_replacements[old_key] += count
    
    print("")
    print("✅ Phase 1 + 2 complete!")
    print("")
    print(f"📊 Files modified: {files_processed}")
    print("")
    print("📈 Replacements made:")
    for old_key, new_key in REPLACEMENTS:
        count = total_replacements[old_key]
        if count > 0:
            print(f"   {old_key} → {new_key}: {count} occurrences")
    print("")
    
    print("🔍 Verifying changes...")
    # Quick verification
    all_clear = True
    for old_key, _ in REPLACEMENTS:
        remaining = 0
        for file_path in root_dir.rglob('*'):
            if file_path.is_file() and should_process_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if old_key in f.read():
                            remaining += 1
                except:
                    pass
        
        if remaining > 0:
            print(f"   ⚠️  '{old_key}' still found in {remaining} files")
            all_clear = False
    
    if all_clear:
        print("   ✅ All old keys successfully replaced!")
    print("")

if __name__ == '__main__':
    main()
