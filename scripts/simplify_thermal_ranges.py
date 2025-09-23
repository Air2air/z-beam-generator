#!/usr/bin/env python3
"""
Range Value Simplification Script

Converts all ranged numeric property values (e.g., "250-350°C", "7.8-8.2 g/cm³", "150-200 GPa") 
to single representative values (e.g., "300°C", "8.0 g/cm³", "175 GPa") in frontmatter files. 
This simplifies the data model while maintaining meaningful numeric information.

Usage: python3 scripts/simplify_thermal_ranges.py [--dry-run] [--method mean|min|max]

Note: "mean" and "average" are mathematically identical - this script uses "mean" terminology.
"""

import re
import argparse
from pathlib import Path
from typing import Tuple, Optional

def extract_range_values(value_str: str) -> Tuple[Optional[float], Optional[float], str]:
    """
    Extract min, max values and unit from a range string.
    
    Returns:
        Tuple of (min_value, max_value, unit)
    """
    # Match patterns like "250-350°C", "1.2-2.8 g/cm³", etc.
    range_pattern = r'(\d+(?:\.\d+)?)[-–](\d+(?:\.\d+)?)\s*([^\d\s]+)'
    match = re.search(range_pattern, value_str)
    
    if match:
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        unit = match.group(3)
        return min_val, max_val, unit
    
    return None, None, ""

def simplify_range_value(value_str: str, method: str = "mean") -> str:
    """
    Simplify a range value to a single value.
    
    Args:
        value_str: Range value like "250-350°C", "7.8-8.2 g/cm³", "150-200 GPa"
        method: "mean", "min", or "max"
    
    Returns:
        Simplified value like "300°C", "8.0 g/cm³", "175 GPa"
    """
    min_val, max_val, unit = extract_range_values(value_str)
    
    if min_val is None or max_val is None:
        # Not a range, return as-is
        return value_str
    
    if method == "mean":
        result_val = (min_val + max_val) / 2
    elif method == "min":
        result_val = min_val
    elif method == "max":
        result_val = max_val
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Format to appropriate precision
    if result_val == int(result_val):
        return f"{int(result_val)}{unit}"
    else:
        return f"{result_val:.1f}{unit}"

def process_frontmatter_file(file_path: Path, method: str = "mean", dry_run: bool = False) -> bool:
    """
    Process a single frontmatter file to simplify all numeric range values.
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Define all numeric properties that might have ranges
        numeric_properties = [
            'thermalDestructionPoint',
            'density',
            'hardness',
            'tensileStrength',
            'yieldStrength',
            'elasticModulus',
            'thermalConductivity',
            'electricalResistivity',
            'magneticPermeability',
            'meltingPoint',
            'decompositionPoint',
            'boilingPoint',
            'specificHeat',
            'thermalExpansion'
        ]
        
        # Process each property type
        for prop in numeric_properties:
            pattern = rf'(\s+{prop}:\s*)([^\n]+)'
            
            def replace_property_value(match):
                prefix = match.group(1)
                value = match.group(2).strip()
                simplified = simplify_range_value(value, method)
                
                # Track changes for reporting
                if value != simplified:
                    changes_made.append((prop, value, simplified))
                
                return f"{prefix}{simplified}"
            
            # Replace property values
            content = re.sub(pattern, replace_property_value, content)
        
        # Check if any changes were made
        if content != original_content:
            if dry_run:
                # Show what would change
                print(f"🔄 {file_path.name}:")
                for prop, original, simplified in changes_made:
                    print(f"   {prop}: {original} → {simplified}")
            else:
                # Write changes
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Simplified {len(changes_made)} properties in: {file_path.name}")
                for prop, original, simplified in changes_made:
                    print(f"   {prop}: {original} → {simplified}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simplify all numeric range values in frontmatter files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--method', choices=['mean', 'min', 'max'], default='mean',
                        help='Method for simplifying ranges (default: mean)')
    args = parser.parse_args()
    
    # Find all frontmatter files
    frontmatter_dir = Path(__file__).parent.parent / "content" / "components" / "frontmatter"
    frontmatter_files = list(frontmatter_dir.glob("*-laser-cleaning.md"))
    
    print(f"🔍 Found {len(frontmatter_files)} frontmatter files")
    print(f"📊 Using method: {args.method} (arithmetic mean of range)")
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No files will be modified")
    
    # Process each file
    processed_count = 0
    for file_path in frontmatter_files:
        if process_frontmatter_file(file_path, args.method, args.dry_run):
            processed_count += 1
    
    # Summary
    print("\n📈 Simplification Summary:")
    print(f"   Total files: {len(frontmatter_files)}")
    print(f"   {'Would simplify' if args.dry_run else 'Simplified'}: {processed_count}")
    print(f"   Already single values: {len(frontmatter_files) - processed_count}")
    
    if args.dry_run and processed_count > 0:
        print("\n💡 Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()
