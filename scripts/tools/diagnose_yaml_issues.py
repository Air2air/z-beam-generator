#!/usr/bin/env python3
"""
Diagnose specific YAML issues in frontmatter files.
"""

import yaml
import os
import sys

def diagnose_file(file_path):
    """Diagnose YAML issues in a specific file."""
    print(f"\n🔍 Diagnosing: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse with different loaders
        try:
            data = yaml.safe_load(content)
            print("✅ File parses correctly with safe_load")
            return True
        except yaml.YAMLError as e:
            print(f"❌ YAML Error: {e}")
            
            # Show problematic lines
            lines = content.split('\n')
            if hasattr(e, 'problem_mark'):
                line_num = e.problem_mark.line
                print(f"Problem at line {line_num + 1}:")
                start = max(0, line_num - 2)
                end = min(len(lines), line_num + 3)
                for i in range(start, end):
                    marker = ">>> " if i == line_num else "    "
                    print(f"{marker}{i+1:3}: {lines[i]}")
            
            return False
            
    except Exception as e:
        print(f"❌ File read error: {e}")
        return False

def main():
    # List of problematic files from the repair script output
    problematic_files = [
        "birch", "bluestone", "brick", "calcite", "cement", "gallium", 
        "hafnium", "iron", "marble", "mdf", "metal-matrix-composites-mmcs",
        "mortar", "nickel", "porphyry", "pyrex", "rosewood", "sandstone",
        "serpentine", "shale", "silicon-carbide", "silver", "stoneware",
        "tantalum", "tempered-glass", "terracotta", "tungsten", "walnut"
    ]
    
    frontmatter_dir = "/Users/todddunning/Desktop/Z-Beam/z-beam-generator/frontmatter/materials"
    
    for material in problematic_files[:5]:  # Just check first 5 to start
        file_path = os.path.join(frontmatter_dir, f"{material}.yaml")
        if os.path.exists(file_path):
            diagnose_file(file_path)
        else:
            print(f"❌ File not found: {file_path}")

if __name__ == "__main__":
    main()
