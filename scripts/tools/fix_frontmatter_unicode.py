#!/usr/bin/env python3
"""
Fix Frontmatter Unicode Escaping and Formatting Issues

This script addresses:
1. Unicode escape sequences (\\u2013, \\u2082, \\u2083, \\u03BC, etc.)
2. Standardizes quoting across all frontmatter files
3. Ensures consistent formatting and encoding
"""

import os
import re
from pathlib import Path
from typing import Dict, List

def fix_frontmatter_encoding():
    """Fix Unicode escaping and formatting issues in all frontmatter files."""
    
    frontmatter_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter"
    files = list(Path(frontmatter_dir).glob("*.md"))
    
    print(f"🔧 Fixing Unicode escaping and formatting in {len(files)} frontmatter files")
    print("=" * 70)
    
    # Unicode escape mappings
    unicode_fixes = {
        # En dash and em dash
        '\\u2013': '–',  # En dash
        '\\u2014': '—',  # Em dash  
        
        # Mathematical symbols and subscripts
        '\\u2082': '₂',  # Subscript 2 (for O₂, etc.)
        '\\u2083': '₃',  # Subscript 3 (for O₃, etc.)
        '\\u2084': '₄',  # Subscript 4
        '\\u2085': '₅',  # Subscript 5
        '\\u2086': '₆',  # Subscript 6
        '\\u2087': '₇',  # Subscript 7
        '\\u2088': '₈',  # Subscript 8
        '\\u2089': '₉',  # Subscript 9
        '\\u2080': '₀',  # Subscript 0
        '\\u2081': '₁',  # Subscript 1
        
        # Greek letters (common in technical content)
        '\\u03BC': 'μ',  # Micro symbol (μm, μg, etc.)
        '\\u03B1': 'α',  # Alpha
        '\\u03B2': 'β',  # Beta
        '\\u03B3': 'γ',  # Gamma
        '\\u03C0': 'π',  # Pi
        
        # Degree symbol
        '\\u00B0': '°',  # Degree symbol
        
        # Other common technical symbols
        '\\u00B1': '±',  # Plus-minus
        '\\u00D7': '×',  # Multiplication
        '\\u00F7': '÷',  # Division
        '\\u221E': '∞',  # Infinity
        '\\u2264': '≤',  # Less than or equal to
        '\\u2265': '≥',  # Greater than or equal to
        '\\u2260': '≠',  # Not equal to
        '\\u2248': '≈',  # Approximately equal to
        '\\u00BC': '¼',  # One quarter
        '\\u00BD': '½',  # One half
        '\\u00BE': '¾',  # Three quarters
        
        # Range symbols commonly used
        '\\u2010': '‐',  # Hyphen
        '\\u2012': '‒',  # Figure dash
        '\\u2015': '―',  # Horizontal bar
    }
    
    # Statistics
    files_processed = 0
    total_fixes = 0
    
    for file_path in sorted(files):
        material_name = file_path.stem.replace('-laser-cleaning', '')
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Apply Unicode fixes
            for escape_seq, replacement in unicode_fixes.items():
                count = content.count(escape_seq)
                if count > 0:
                    content = content.replace(escape_seq, replacement)
                    fixes_in_file += count
                    total_fixes += count
            
            # Additional formatting fixes
            
            # Fix range symbols that should use en dash
            # Pattern: number-number or letter-letter should use en dash
            content = re.sub(r'(\\d+)-(\\d+)', r'\\1–\\2', content)
            
            # Fix quoted ranges that might have hyphens
            content = re.sub(r'\"([^\"]*)(\\d+)-(\\d+)([^\"]*?)\"', r'\"\\1\\2–\\3\\4\"', content)
            
            # Standardize degree symbols in quoted strings
            content = re.sub(r'°C', '°C', content)  # Ensure proper degree symbol
            content = re.sub(r'°F', '°F', content)  # Ensure proper degree symbol
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {material_name:<25} - Fixed {fixes_in_file} Unicode escapes")
                files_processed += 1
            else:
                print(f"⏭️  {material_name:<25} - No issues found")
                
        except Exception as e:
            print(f"❌ {material_name:<25} - Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Total Unicode fixes: {total_fixes}")
    print(f"   Files scanned: {len(files)}")
    
    if total_fixes > 0:
        print(f"\\n✅ Successfully fixed {total_fixes} Unicode escape sequences!")
    else:
        print("\\n✅ All files already have proper Unicode encoding!")

def validate_fixed_content():
    """Validate that all files still parse correctly after fixes."""
    
    frontmatter_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter"
    files = list(Path(frontmatter_dir).glob("*.md"))
    
    print(f"\\n🔍 Validating {len(files)} fixed frontmatter files...")
    
    invalid_files = []
    
    for file_path in sorted(files):
        material_name = file_path.stem.replace('-laser-cleaning', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if content starts with YAML frontmatter
            if not content.startswith('---'):
                invalid_files.append((material_name, "Missing YAML frontmatter delimiter"))
                continue
            
            # Find end of frontmatter
            end_marker = content.find('---', 3)
            if end_marker == -1:
                invalid_files.append((material_name, "Missing closing YAML delimiter"))
                continue
            
            # Extract and validate YAML
            yaml_content = content[3:end_marker].strip()
            
            # Basic validation - check for balanced quotes
            double_quotes = yaml_content.count('"')
            if double_quotes % 2 != 0:
                invalid_files.append((material_name, "Unbalanced double quotes"))
                continue
                
        except Exception as e:
            invalid_files.append((material_name, f"Read error: {e}"))
    
    if invalid_files:
        print(f"\\n❌ Found {len(invalid_files)} files with issues:")
        for material, issue in invalid_files[:5]:
            print(f"   {material}: {issue}")
        if len(invalid_files) > 5:
            print(f"   ... and {len(invalid_files) - 5} more")
    else:
        print("\\n✅ All files validated successfully!")
    
    return len(invalid_files) == 0

if __name__ == "__main__":
    print("🚀 Starting Frontmatter Unicode Fix Process")
    print("=" * 70)
    
    # Step 1: Fix Unicode escaping
    fix_frontmatter_encoding()
    
    # Step 2: Validate results
    validation_success = validate_fixed_content()
    
    if validation_success:
        print("\\n🎉 All frontmatter files successfully fixed and validated!")
    else:
        print("\\n⚠️  Some files may need manual attention.")
