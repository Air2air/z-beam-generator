#!/usr/bin/env python3
"""
Analyze frontmatter files for quoting inconsistencies and formatting issues.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_frontmatter_quotes():
    """Analyze all frontmatter files for quoting issues."""
    
    frontmatter_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/content/components/frontmatter"
    files = list(Path(frontmatter_dir).glob("*.md"))
    
    print(f"🔍 Analyzing {len(files)} frontmatter files for quoting issues")
    print("=" * 60)
    
    issues = {
        'mixed_quotes_in_values': [],
        'unnecessary_quotes_on_numbers': [],
        'missing_quotes_on_strings': [],
        'backslash_issues': [],
        'yaml_parse_errors': []
    }
    
    for file_path in sorted(files):
        material_name = file_path.stem.replace('-laser-cleaning', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML frontmatter
            if content.startswith('---'):
                end_marker = content.find('---', 3)
                if end_marker != -1:
                    yaml_content = content[3:end_marker].strip()
                    
                    # Check for various issues
                    check_quoting_issues(material_name, yaml_content, issues)
                    
                    # Try to parse YAML
                    try:
                        yaml.safe_load(yaml_content)
                    except yaml.YAMLError as e:
                        issues['yaml_parse_errors'].append((material_name, str(e)))
                        
        except Exception as e:
            print(f"❌ Error reading {material_name}: {e}")
    
    # Report findings
    print_analysis_results(issues)
    
    return issues

def check_quoting_issues(material_name: str, yaml_content: str, issues: Dict):
    """Check for specific quoting issues in YAML content."""
    
    lines = yaml_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith('#') or not line or ':' not in line:
            continue
            
        # Split key: value
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Check for mixed quotes
            if ('"' in value and "'" in value) and not (value.startswith('"') and value.endswith('"')):
                issues['mixed_quotes_in_values'].append((material_name, line_num, line))
            
            # Check for unnecessary quotes on numbers
            if value.startswith('"') and value.endswith('"'):
                inner_value = value[1:-1]
                if re.match(r'^[\d.]+$', inner_value):  # Pure number
                    issues['unnecessary_quotes_on_numbers'].append((material_name, line_num, line))
            
            # Check for backslash issues
            if '\\' in value and not (value.startswith('"') or value.startswith("'")):
                issues['backslash_issues'].append((material_name, line_num, line))

def print_analysis_results(issues: Dict):
    """Print the analysis results."""
    
    print("\n📊 QUOTING ANALYSIS RESULTS")
    print("=" * 60)
    
    for issue_type, items in issues.items():
        if items:
            print(f"\n🔸 {issue_type.replace('_', ' ').title()}: {len(items)} issues")
            
            # Show first few examples
            for i, item in enumerate(items[:3]):
                if issue_type == 'yaml_parse_errors':
                    material, error = item
                    print(f"   {material}: {error}")
                else:
                    material, line_num, line = item
                    print(f"   {material}:{line_num} -> {line}")
            
            if len(items) > 3:
                print(f"   ... and {len(items) - 3} more")
        else:
            print(f"\n✅ {issue_type.replace('_', ' ').title()}: No issues found")
    
    print(f"\n📋 Summary:")
    total_issues = sum(len(items) for items in issues.values())
    print(f"   Total issues found: {total_issues}")
    
    if total_issues > 0:
        print("   Recommended action: Create quote standardization script")
    else:
        print("   ✅ All frontmatter files have consistent quoting!")

if __name__ == "__main__":
    analyze_frontmatter_quotes()
