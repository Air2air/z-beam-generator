#!/usr/bin/env python3
"""
Post-generation frontmatter normalization script.
Fixes quote formatting inconsistencies and YAML truncation issues.
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime

class FrontmatterNormalizer:
    def __init__(self):
        # Fields that should ALWAYS be quoted
        self.always_quote = {
            'name', 'description', 'author', 'title', 'headline',
            'powerRange', 'pulseDuration', 'wavelength', 'spotSize', 
            'repetitionRate', 'fluenceRange', 'safetyClass', 'detail',
            'formula', 'symbol', 'materialType', 'laserType'
        }
        
        # Fields that should NEVER be quoted
        self.never_quote = {
            'id', 'densityPercentile', 'meltingPercentile', 'thermalPercentile',
            'tensilePercentile', 'hardnessPercentile', 'modulusPercentile'
        }

    def should_quote_value(self, key, value):
        """Determine if a value should be quoted."""
        if key in self.always_quote:
            return True
        if key in self.never_quote:
            return False
        if isinstance(value, (int, float, bool)):
            return False
        if isinstance(value, str):
            # Quote if contains special characters or looks like a technical spec
            if any(c in value for c in ':-[]{}()') or 'nm' in value or 'W' in value:
                return True
        return False

    def normalize_yaml_structure(self, data):
        """Recursively normalize YAML structure with proper quoting."""
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    normalized[key] = self.normalize_yaml_structure(value)
                elif isinstance(value, list):
                    normalized[key] = [self.normalize_yaml_structure(item) for item in value]
                else:
                    if self.should_quote_value(key, value):
                        normalized[key] = str(value)  # Ensure it's a string for quoting
                    else:
                        normalized[key] = value
            return normalized
        elif isinstance(data, list):
            return [self.normalize_yaml_structure(item) for item in data]
        else:
            return data

    def fix_truncated_yaml(self, content):
        """Fix known truncation issues in YAML content."""
        fixes = [
            # Fix truncated image URLs
            (r'url: "/images/(\w+)$', r'url: "/images/\1-laser-cleaning-hero.jpg"'),
            (r'url: "/images/(\w+)-(\w+)$', r'url: "/images/\1-\2-laser-cleaning-hero.jpg"'),
            
            # Fix truncated alt text
            (r'alt: "Microscopic$', r'alt: "Microscopic view showing preserved microstructure"'),
            (r'alt: "([^"]*) showing preserved$', r'alt: "\1 showing preserved microstructure"'),
            
            # Fix truncated headlines
            (r'headline: "([^"]*) guide for$', r'headline: "\1 guide for laser cleaning applications"'),
            (r'headline: "([^"]*) guide f$', r'headline: "\1 guide for laser cleaning applications"'),
            
            # Fix incomplete quoted strings
            (r'(\w+): "([^"]*)\n', r'\1: "\2"\n'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content

    def extract_and_normalize_yaml(self, content):
        """Extract YAML frontmatter and normalize it."""
        if not content.startswith('---'):
            return None, content
        
        yaml_end = content.find('---', 3)
        if yaml_end <= 0:
            return None, content
        
        yaml_content = content[4:yaml_end]
        remaining_content = content[yaml_end + 3:]
        
        # Fix truncation issues first
        yaml_content = self.fix_truncated_yaml(yaml_content)
        
        try:
            # Parse YAML
            data = yaml.safe_load(yaml_content)
            if not isinstance(data, dict):
                return None, content
            
            # Normalize structure
            normalized_data = self.normalize_yaml_structure(data)
            
            # Generate clean YAML with selective quoting
            clean_yaml = yaml.dump(
                normalized_data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=1000,
                indent=2,
                default_style=None  # Let YAML decide quoting
            )
            
            # Apply consistent quoting rules
            lines = clean_yaml.split('\n')
            corrected_lines = []
            
            for line in lines:
                # Don't quote keys themselves
                if ':' in line and not line.strip().startswith('-'):
                    key_part, value_part = line.split(':', 1)
                    key = key_part.strip()
                    value = value_part.strip()
                    
                    # Remove existing quotes from key
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                    
                    # Apply value quoting rules
                    if value and key in self.always_quote:
                        if not (value.startswith('"') and value.endswith('"')):
                            value = f'"{value}"'
                    elif value and key in self.never_quote:
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                    
                    corrected_lines.append(f"{' ' * (len(key_part) - len(key))}{key}: {value}")
                else:
                    corrected_lines.append(line)
            
            clean_yaml = '\n'.join(corrected_lines)
            
            return f"---\n{clean_yaml}---", remaining_content
            
        except Exception as e:
            print(f"⚠️ YAML parsing error: {e}")
            return None, content

    def normalize_file(self, file_path):
        """Normalize a single frontmatter file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract and normalize YAML
            normalized_yaml, remaining = self.extract_and_normalize_yaml(content)
            
            if normalized_yaml is None:
                return False, "Failed to parse YAML"
            
            # Reconstruct file
            new_content = normalized_yaml + remaining
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, None
            
        except Exception as e:
            return False, str(e)

def main():
    """Normalize all frontmatter files for consistent formatting."""
    print("🔧 FRONTMATTER QUOTE NORMALIZATION")
    print("=" * 50)
    
    normalizer = FrontmatterNormalizer()
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
        success, error = normalizer.normalize_file(file_path)
        
        if success:
            print(f"✅ {file_path.name}")
            success_count += 1
        else:
            print(f"❌ {file_path.name}: {error}")
            errors.append(f"{file_path.name}: {error}")
            error_count += 1
    
    print()
    print("📊 NORMALIZATION RESULTS:")
    print(f"   ✅ Successfully normalized: {success_count} files")
    print(f"   ❌ Errors encountered: {error_count} files")
    
    if errors:
        print("\n❌ ERROR DETAILS:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")
    
    if error_count == 0:
        print("\n🎉 ALL FILES NORMALIZED FOR CONSISTENT FORMATTING!")
        print("✅ All files now have standardized quote usage")
        print("✅ Technical specifications consistently formatted")
        print("✅ YAML syntax validated and repaired")
    else:
        print(f"\n⚠️  {error_count} files need manual attention")

if __name__ == "__main__":
    main()
