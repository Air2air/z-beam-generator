#!/usr/bin/env python3

import os
import yaml
import glob
from pathlib import Path

def check_yaml_accuracy(file_path):
    """Check YAML front matter accuracy in JSON-LD files."""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has front matter
        if not content.startswith('---'):
            issues.append("Missing YAML front matter delimiter at start")
            return issues
        
        # Extract YAML front matter
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append("Missing closing YAML front matter delimiter")
            return issues
        
        yaml_content = parts[1].strip()
        
        # Try to parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            issues.append(f"YAML parsing error: {e}")
            return issues
        
        # Check required fields
        required_fields = [
            'headline', 'description', 'keywords', 'articleBody', 
            'image', 'datePublished', 'dateModified', 'author', 'subjectSlug'
        ]
        
        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")
        
        # Check field types
        if 'keywords' in data and not isinstance(data['keywords'], list):
            issues.append("'keywords' should be a list")
        
        if 'image' in data and not isinstance(data['image'], list):
            issues.append("'image' should be a list")
        
        # Check for empty values
        for key, value in data.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append(f"Empty value for field: {key}")
            elif isinstance(value, list) and not value:
                issues.append(f"Empty list for field: {key}")
        
        # Check date format
        date_fields = ['datePublished', 'dateModified']
        for date_field in date_fields:
            if date_field in data:
                date_value = str(data[date_field])
                # Simple date format check (YYYY-MM-DD)
                if len(date_value) != 10 or date_value.count('-') != 2:
                    try:
                        year, month, day = date_value.split('-')
                        if len(year) != 4 or len(month) != 2 or len(day) != 2:
                            issues.append(f"Invalid date format for {date_field}: {date_value}")
                    except ValueError:
                        issues.append(f"Invalid date format for {date_field}: {date_value}")
        
        # Check for consistent author format
        if 'author' in data:
            author = data['author']
            if not isinstance(author, str) or not author.strip():
                issues.append("Author should be a non-empty string")
        
        # Check chemical formula formatting
        if 'chemicalFormula' in data:
            formula = data['chemicalFormula']
            # Check if it contains proper subscripts
            # Valid subscript characters: ₀₁₂₃₄₅₆₇₈₉
            subscript_chars = '₀₁₂₃₄₅₆₇₈₉'
            if any(char.isdigit() for char in formula) and not any(char in subscript_chars for char in formula):
                issues.append("Chemical formula may need proper subscript formatting")
        
    except Exception as e:
        issues.append(f"File reading error: {e}")
    
    return issues

def main():
    jsonld_dir = "content/components/jsonld"
    if not os.path.exists(jsonld_dir):
        print(f"Directory {jsonld_dir} not found!")
        return
    
    pattern = os.path.join(jsonld_dir, "*.md")
    files = glob.glob(pattern)
    
    if not files:
        print("No JSON-LD files found!")
        return
    
    print(f"Checking {len(files)} JSON-LD files for YAML accuracy...")
    print("=" * 70)
    
    total_issues = 0
    files_with_issues = 0
    
    for file_path in sorted(files):
        filename = os.path.basename(file_path)
        issues = check_yaml_accuracy(file_path)
        
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"\n❌ {filename}:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"✅ {filename}: No issues found")
    
    print("\n" + "=" * 70)
    print(f"Summary: {files_with_issues}/{len(files)} files have issues")
    print(f"Total issues found: {total_issues}")
    
    if files_with_issues == 0:
        print("🎉 All JSON-LD files have valid YAML formatting!")

if __name__ == "__main__":
    main()
